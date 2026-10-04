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
- [x] KoELECTRA Augmented training
- [ ] KoELECTRA Original obfuscated test
- [ ] KoELECTRA Augmented clean test
- [ ] KoELECTRA Augmented obfuscated test
- [ ] KoreanGuardrail supplementary evaluation

Augmented training data and 17-technique obfuscated evaluation data were delivered on 2026-10-04 and passed the Step 1 data validator.

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

---

## 2026-10-04 — KoELECTRA Augmented

### 1. Training configuration

- Model: `monologg/koelectra-base-v3-discriminator`
- Training: Augmented
- Original train: `data/step1/train.jsonl`
- Augmented input: `data/step1/augmented_train.jsonl`
- Validation: `data/step1/valid.jsonl`
- Final train rows: 14,377
- Original rows: 4,809
- Variant rows: 9,568
- Benign: 7,200
- Attack: 7,177
- Augmentation cells:
  - `yamin_swap`, intensity 0.7: 4,759 rows
  - `symbol_insert`, intensity 0.3: 4,809 rows
- Epochs: 3
- Batch size: 16
- Learning rate: 2e-5
- Weight decay: 0.01
- Max length: 128
- Seed: 42
- FP16: enabled
- Best-model selection: validation F1

The delivered `augmented_train.jsonl` already contains the original 4,809 training rows.
`prepare_augmented_train.py` detected the input as `combined` mode and used 14,377 rows without duplicating the original rows.

### 2. Validation result

Best epoch: 1

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
| Validation loss | 0.0363 |

Saved model:

`results/step1/koelectra/augmented/best_model`

Training outputs:

- `results/step1/koelectra/augmented/validation_results.csv`
- `results/step1/koelectra/augmented/metrics.json`
- `results/step1/koelectra/augmented/training_history.csv`
- `results/step1/koelectra/augmented/best_model`

### 3. Training history

| Epoch | Train loss | Accuracy | Precision | Attack Recall | F1 | Benign FPR | FNR | Validation loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.1012 | 0.9917 | 0.9868 | 0.9967 | 0.9917 | 0.0132 | 0.0033 | 0.0363 |
| 2 | 0.0216 | 0.9801 | 0.9645 | 0.9967 | 0.9803 | 0.0362 | 0.0033 | 0.0816 |
| 3 | 0.0115 | 0.9851 | 0.9866 | 0.9833 | 0.9850 | 0.0132 | 0.0167 | 0.0558 |

### 4. Comparison with Original-only validation

| Training | Best epoch | Accuracy | Attack Recall | F1 | Benign FPR |
| --- | ---: | ---: | ---: | ---: | ---: |
| Original-only | 3 | 0.9868 | 0.9933 | 0.9868 | 0.0197 |
| Augmented | 1 | 0.9917 | 0.9967 | 0.9917 | 0.0132 |

On the clean validation set, the Augmented model showed slightly higher F1 and lower benign FPR than the Original-only model.

This validation result alone does not establish robustness to obfuscation.
The main comparison requires evaluation on the clean and 17-technique obfuscated test sets.

### 5. Next evaluation

- [ ] KoELECTRA Original obfuscated test
- [ ] KoELECTRA Augmented clean test
- [ ] KoELECTRA Augmented obfuscated test
- [ ] KoELECTRA Original/Augmented KoreanGuardrail evaluation
- [ ] Original vs Augmented paired/statistical comparison

