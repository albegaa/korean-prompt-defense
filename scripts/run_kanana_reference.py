"""
Kanana Safeguard 참조 평가 (Step 1 표 2 reference baseline)

T4/T6 run_kanana_safeguard.py와 추론 방식은 동일:
  모델, chat template, left padding, fp16, greedy, max_new_tokens=10,
  입력 텍스트 선택(text_attack or text), 출력 파싱 규칙

바뀐 점 3가지:
  1. label: 숫자(0/1)와 글자("attack"/"benign")를 모두 처리
  2. attack_score: 첫 생성 토큰에서
       (P(<UNSAFE-A1>) + P(<UNSAFE-A2>)) / (P(<SAFE>) + P(<UNSAFE-A1>) + P(<UNSAFE-A2>))
     공식 판정(prediction)은 지금처럼 생성된 글자로 정하고, 점수는 통계용
  3. 저장: 팀 evaluate.py와 같은 predictions.csv(원래 열 + prediction + attack_score)
     + metrics.json (지표 계산은 evaluate.py의 compute_binary_metrics를 그대로 사용)

실행 예 (repo 루트에서):
  CUDA_VISIBLE_DEVICES=4 python scripts/run_kanana_reference.py \
    --input data/step1/test.jsonl \
    --output-dir results/step1/kanana/reference/eval/clean
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path

import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
from src.classifier.evaluate import compute_binary_metrics  # noqa: E402

MODEL_NAME = "kakaocorp/kanana-safeguard-prompt-2.1b"
LABEL_TOKENS = ["<SAFE>", "<UNSAFE-A1>", "<UNSAFE-A2>"]


# ---------- T4/T6와 동일한 부분 ----------

def get_eval_text(row):
    # A1 스크리닝 시드는 canary가 들어간 text_attack 사용, 나머지는 text
    value = row.get("text_attack")
    if isinstance(value, str) and value:
        return value
    return row["text"]


def parse_label(text):
    match = re.search(r"<(SAFE|UNSAFE-A1|UNSAFE-A2)>", text)
    if not match:
        return "PARSE_ERROR", -1
    raw_label = f"<{match.group(1)}>"
    return raw_label, (0 if raw_label == "<SAFE>" else 1)


# ---------- 바뀐 부분 ----------

def to_binary_label(value):
    # Step 1 데이터: 0/1 숫자, 스크리닝 데이터: "attack"/"benign" 글자
    if isinstance(value, str):
        v = value.strip().lower()
        if v in ("attack", "1"):
            return 1
        if v in ("benign", "0"):
            return 0
    elif value in (0, 1):
        return int(value)
    raise ValueError(f"알 수 없는 label 값: {value!r}")


def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def get_label_token_ids(tokenizer):
    ids = {lab: tokenizer.encode(lab, add_special_tokens=False) for lab in LABEL_TOKENS}
    print("label token ids:", ids)
    single = all(len(t) == 1 for t in ids.values())
    distinct = len({t[0] for t in ids.values()}) == len(LABEL_TOKENS)
    if not (single and distinct):
        raise SystemExit(
            "라벨이 토큰 1개가 아님 → attack_score 계산 방식을 바꿔야 함. 실행 중단."
        )
    return [ids[lab][0] for lab in LABEL_TOKENS]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--max-samples", type=int, default=None)
    args = parser.parse_args()

    rows = load_jsonl(args.input)
    if args.max_samples is not None:
        rows = rows[: args.max_samples]
    labels = [to_binary_label(r["label"]) for r in rows]
    print(f"Loaded {len(rows)} rows from {args.input}")

    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    tokenizer.padding_side = "left"
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    label_ids = get_label_token_ids(tokenizer)

    print("Loading model...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True,
    ).to("cuda")
    model.eval()

    raw_outputs, raw_labels, predictions, attack_scores, label_mass = [], [], [], [], []
    start_time = time.time()

    for start in range(0, len(rows), args.batch_size):
        batch_rows = rows[start:start + args.batch_size]

        prompts = [
            tokenizer.apply_chat_template(
                [{"role": "user", "content": get_eval_text(row)}],
                tokenize=False,
                add_generation_prompt=True,
            )
            for row in batch_rows
        ]

        inputs = tokenizer(prompts, padding=True, return_tensors="pt")
        inputs = {k: v.to("cuda") for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=10,
                do_sample=False,
                pad_token_id=tokenizer.pad_token_id,
                return_dict_in_generate=True,
                output_logits=True,
            )

        input_length = inputs["input_ids"].shape[1]
        decoded = tokenizer.batch_decode(
            outputs.sequences[:, input_length:],
            skip_special_tokens=False,
        )

        # 첫 생성 토큰의 확률에서 attack_score 계산
        probs = torch.softmax(outputs.logits[0].float(), dim=-1)
        p = probs[:, label_ids]  # [batch, 3] = SAFE, A1, A2
        mass = p.sum(dim=1)
        score = (p[:, 1] + p[:, 2]) / mass

        for raw_output, s, m in zip(decoded, score.tolist(), mass.tolist()):
            raw_label, pred = parse_label(raw_output)
            raw_outputs.append(raw_output)
            raw_labels.append(raw_label)
            predictions.append(pred)
            attack_scores.append(s)
            label_mass.append(m)

        done = min(start + args.batch_size, len(rows))
        if done == len(rows) or (start // args.batch_size) % 50 == 0:
            elapsed = time.time() - start_time
            eta = elapsed / done * (len(rows) - done)
            print(f"Processed {done}/{len(rows)}  elapsed {elapsed/60:.1f}m  eta {eta/60:.1f}m")

    elapsed = time.time() - start_time

    # ---------- 저장 (팀 evaluate.py와 같은 형식) ----------
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    result_df = pd.DataFrame(rows)
    result_df["label"] = labels
    result_df["prediction"] = predictions
    result_df["attack_score"] = attack_scores
    result_df["raw_label"] = raw_labels
    result_df["raw_output"] = raw_outputs
    result_df.to_csv(output_dir / "predictions.csv", index=False)

    valid = result_df[result_df["prediction"] != -1]
    n_parse_error = int((result_df["prediction"] == -1).sum())

    metrics = compute_binary_metrics(valid["label"].tolist(), valid["prediction"].tolist())
    # 생성된 판정과 점수(0.5 기준) 판정이 어긋난 행 수 (진단용, 0에 가까워야 정상)
    score_pred = (valid["attack_score"] >= 0.5).astype(int)
    metrics.update({
        "n": int(len(result_df)),
        "n_parse_error": n_parse_error,
        "n_score_vs_generated_mismatch": int((score_pred != valid["prediction"]).sum()),
        "min_label_token_mass": float(min(label_mass)) if label_mass else None,
        "model": MODEL_NAME,
        "role": "reference baseline (not trained on Step 1 data)",
        "prediction_rule": "generated label token (<SAFE>=0, <UNSAFE-A1/A2>=1)",
        "attack_score_rule": "first-token (P_A1+P_A2)/(P_SAFE+P_A1+P_A2)",
        "input_file": str(args.input),
        "batch_size": args.batch_size,
        "max_new_tokens": 10,
        "dtype": "float16",
        "elapsed_sec": round(elapsed, 1),
        "rows_per_sec": round(len(result_df) / elapsed, 2) if elapsed > 0 else None,
    })

    with open(output_dir / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    print("\n=== Metrics ===")
    for key, value in metrics.items():
        print(f"{key:32s}: {value:.4f}" if isinstance(value, float) else f"{key:32s}: {value}")
    if n_parse_error:
        print(f"\n[경고] parse error {n_parse_error}건 → metrics에서 제외됨. raw_output 확인 필요")
    print("\nSaved:", output_dir / "predictions.csv", output_dir / "metrics.json")


if __name__ == "__main__":
    main()
