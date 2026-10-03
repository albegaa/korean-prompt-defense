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
