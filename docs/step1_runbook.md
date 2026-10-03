# Step 1 Runbook

이 문서는 최종 Step 1 데이터 수신 후 KoELECTRA와 mDeBERTa 경량 classifier를 동일한 조건으로 학습하고, Clean / Obfuscated / KoreanGuardrail 평가를 수행하기 위한 실제 실행 절차를 정리한다.

---

## 0. 최초 1회 설정

처음 서버에서 작업하는 경우에만 진행한다.

### 저장소 clone

```bash
cd /root/project
git clone https://github.com/albegaa/korean-prompt-defense.git
cd korean-prompt-defense
```

이미 clone되어 있으면 생략한다.

### Python 환경

```bash
python -m venv /root/project/.venv
source /root/project/.venv/bin/activate
pip install -r requirements-server.txt
```

이후 새 터미널에서는 다음만 설정하면 된다.

```bash
cd /root/project/korean-prompt-defense
export PYTHON=/root/project/.venv/bin/python
```

---

## 1. 실험 전 확인

저장소 이동:

```bash
cd /root/project/korean-prompt-defense
export PYTHON=/root/project/.venv/bin/python
```

GPU 확인:

```bash
nvidia-smi
```

데이터 예시:

```text
data/step1/
├── train.jsonl
├── valid.jsonl
├── test.jsonl
├── kg_test.jsonl
├── augmented_train.jsonl
├── obfuscated_test.jsonl
└── obfuscated_kg_test.jsonl
```

경로 설정:

```bash
export TRAIN_FILE=data/step1/train.jsonl
export VALID_FILE=data/step1/valid.jsonl
export TEST_FILE=data/step1/test.jsonl
export KG_TEST_FILE=data/step1/kg_test.jsonl
export AUGMENTED_INPUT=data/step1/augmented_train.jsonl
export OBFUSCATED_TEST_FILE=data/step1/obfuscated_test.jsonl
export OBFUSCATED_KG_FILE=data/step1/obfuscated_kg_test.jsonl
```

---

## 2. 데이터 검증

본학습 전에 한 번 실행한다.

```bash
"$PYTHON" scripts/validate_step1_data.py \
  --train "$TRAIN_FILE" \
  --valid "$VALID_FILE" \
  --test "$TEST_FILE" \
  --kg-test "$KG_TEST_FILE" \
  --augmented-train "$AUGMENTED_INPUT" \
  --obfuscated-test "$OBFUSCATED_TEST_FILE" \
  --obfuscated-kg-test "$OBFUSCATED_KG_FILE"
```

validator가 실패하면 학습 전에 데이터를 먼저 수정한다.

추가로 최종 데이터 수신 후에는 다음을 확인한다.

- label / source 분포
- 번역 / 비번역 비율
- KoELECTRA, mDeBERTa 기준 128 token 초과 비율

세부 데이터 기준은 `docs/step1_data_contract.md`를 따른다.

---

## 3. 학습 설정

기본값:

```text
learning rate = 2e-5
weight decay  = 0.01
max length    = 128
seed          = 42
batch size    = 16
epochs        = 3
FP16          = enabled
```

필요하면 실행 전에 설정한다.

```bash
export BATCH_SIZE=16
export MAX_LENGTH=128
```

---

## 4. Original 학습

### KoELECTRA

```bash
bash scripts/run_original_train.sh \
  koelectra \
  "$TRAIN_FILE" \
  "$VALID_FILE" \
  0 \
  3
```

### mDeBERTa

```bash
bash scripts/run_original_train.sh \
  mdeberta \
  "$TRAIN_FILE" \
  "$VALID_FILE" \
  0 \
  3
```

결과:

```text
results/step1/koelectra/original/
results/step1/mdeberta/original/
```

---

## 5. Augmented 학습

`run_augmented_train.sh`가 내부에서
증강 데이터 준비와 validation을 처리한다.

### KoELECTRA

```bash
bash scripts/run_augmented_train.sh \
  koelectra \
  "$TRAIN_FILE" \
  "$AUGMENTED_INPUT" \
  "$VALID_FILE" \
  0 \
  3
```

### mDeBERTa

```bash
bash scripts/run_augmented_train.sh \
  mdeberta \
  "$TRAIN_FILE" \
  "$AUGMENTED_INPUT" \
  "$VALID_FILE" \
  0 \
  3
```

결과:

```text
results/step1/koelectra/augmented/
results/step1/mdeberta/augmented/
```

---

## 6. 평가

형식:

```bash
bash scripts/run_step1_eval.sh \
  <model_key> \
  <training_type> \
  <eval_name> \
  <input_file> \
  [gpu] \
  [batch_size]
```

가능한 값:

```text
model_key      : koelectra | mdeberta
training_type  : original | augmented
eval_name      : clean | obfuscated | kg_clean | kg_obfuscated
```

예: KoELECTRA Original Clean

```bash
bash scripts/run_step1_eval.sh \
  koelectra original clean "$TEST_FILE" 0 32
```

예: KoELECTRA Original Obfuscated

```bash
bash scripts/run_step1_eval.sh \
  koelectra original obfuscated "$OBFUSCATED_TEST_FILE" 0 32
```

예: KoELECTRA Original KG Clean

```bash
bash scripts/run_step1_eval.sh \
  koelectra original kg_clean "$KG_TEST_FILE" 0 32
```

예: KoELECTRA Original KG Obfuscated

```bash
bash scripts/run_step1_eval.sh \
  koelectra original kg_obfuscated "$OBFUSCATED_KG_FILE" 0 32
```

같은 방식으로 아래 4개 학습 조건을 모두 평가한다.

```text
KoELECTRA Original
KoELECTRA Augmented
mDeBERTa Original
mDeBERTa Augmented
```

`obfuscated`, `kg_obfuscated` 평가에서는
`analyze_obfuscated_eval.py`가 자동 실행된다.

난독화 주 결과는 `changed=true` 기준이다.

---

## 7. 결과표 생성

Main 결과표:

```bash
"$PYTHON" scripts/make_step1_table.py
```

KoreanGuardrail summary:

```bash
"$PYTHON" scripts/make_step1_kg_summary.py
```

결과 루트:

```text
results/step1/
```

---

## 8. 길이 구간별 성능 확인

최종 test에서는 `source == "xtram1"`인 행을 대상으로
text 길이에 따른 성능 차이도 확인한다.

구간:

- 0~40자
- 40~55자
- 55~70자
- 70자 이상

각 구간에서 다음을 계산한다.

- Attack Recall
- Benign FPR

valid / test의 xTRam1 공격·정상 길이 분포 차이가 일부 남아 있으므로,
구간별 성능 차이가 큰 경우 모델이 입력 길이에 의존하는지 함께 해석한다.

---

## 9. 추가 통계 분석

추가 통계는 각 평가의 `predictions.csv`를 사용한다.

기본 원칙:

- Original vs Augmented는 동일 `id` 기준 비교
- 난독화 variant는 `seed_id` 기준으로 묶어서 처리
- 실제 증강 조건:
  - `yamin_swap`, intensity `0.7`
  - `symbol_insert`, intensity `0.3`

통계 script가 merge되면 실제 실행 명령을 여기에 추가!

---

## 10. 실험 완료 체크

- [ ] 데이터 validator 통과
- [ ] 데이터 분포 / token 길이 확인
- [ ] xTRam1 길이 구간별 Recall / FPR 확인
- [ ] KoELECTRA Original 학습
- [ ] mDeBERTa Original 학습
- [ ] KoELECTRA Augmented 학습
- [ ] mDeBERTa Augmented 학습
- [ ] Clean 평가
- [ ] Obfuscated 평가
- [ ] KG Clean 평가
- [ ] KG Obfuscated 평가
- [ ] Main 결과표 생성
- [ ] KG summary 생성
- [ ] 통계 분석 및 결과 검산
