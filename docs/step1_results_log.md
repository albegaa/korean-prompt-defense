# Step 1 Experiment Results Log

## 2026-10-03 — KoELECTRA Original-only

### 1. Training configuration

- Model: `monologg/koelectra-base-v3-discriminator`
- Training: Original-only
- Train: `data/step1/train.jsonl`
- Validation: `data/step1/valid.jsonl`
- Train rows: 4,809
- Validation rows: 604
- Epochs: 3
- Batch size: 16
- Learning rate: 2e-5
- Weight decay: 0.01
- Max length: 128
- Seed: 42
- FP16: enabled
- Best-model selection: validation F1

### 2. Validation result

Best epoch: 3

| Metric | Result |
| --- | ---: |
| Accuracy | 0.9868 |
| Precision | 0.9803 |
| Attack Recall | 0.9933 |
| F1 | 0.9868 |
| Benign FPR | 0.0197 |
| FNR | 0.0067 |
| TP | 298 |
| TN | 298 |
| FP | 6 |
| FN | 2 |
| Validation loss | 0.0494 |

Saved model:

`results/step1/koelectra/original/best_model`

### 3. Clean test result

Input:

`data/step1/test.jsonl`

- Rows: 604
- Benign: 304
- Attack: 300
- Evaluation batch size: 8
- Max length: 128
- FP16: enabled

| Metric | Result |
| --- | ---: |
| Accuracy | 0.9917 |
| Precision | 0.9868 |
| Attack Recall | 0.9967 |
| F1 | 0.9917 |
| Benign FPR | 0.0132 |
| FNR | 0.0033 |
| TP | 299 |
| TN | 300 |
| FP | 4 |
| FN | 1 |
| Loss | 0.0474 |

Outputs:

- `results/step1/koelectra/original/eval/clean/predictions.csv`
- `results/step1/koelectra/original/eval/clean/metrics.json`

### 4. Current status

- [x] KoELECTRA Original-only training
- [x] KoELECTRA Original clean test
- [ ] KoELECTRA Augmented training
- [ ] KoELECTRA Original obfuscated test
- [ ] KoELECTRA Augmented clean test
- [ ] KoELECTRA Augmented obfuscated test
- [ ] KoreanGuardrail supplementary evaluation

Augmented training data and 17-technique obfuscated evaluation data are pending delivery.

### 5. xTRam1 length-bin analysis

KoELECTRA Original clean-test predictions에서 `source == "xtram1"`인 행만 사용하여
문자 길이 기준 4개 구간으로 나누어 Attack Recall과 Benign FPR을 확인하였다.

| Length bin | N | Attack N | Benign N | Attack Recall | Benign FPR |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0~40 | 84 | 36 | 48 | 1.0000 | 0.0208 |
| 40~55 | 125 | 84 | 41 | 1.0000 | 0.0000 |
| 55~70 | 86 | 39 | 47 | 1.0000 | 0.0000 |
| 70+ | 112 | 44 | 68 | 0.9773 | 0.0000 |

KoELECTRA Original clean test에서는 길이 구간에 따른 큰 성능 차이는 관찰되지 않았다.
가장 긴 70+ 구간에서 공격 44건 중 1건을 놓쳤고,
가장 짧은 0~40 구간에서 정상 48건 중 1건을 오탐하였다.

최종 비교에서는 KoELECTRA Augmented와 mDeBERTa 결과에도 동일 분석을 적용한다.
