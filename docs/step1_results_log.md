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


---

## 2026-10-05 — KoELECTRA Seeds 43/44 Repeated Runs

### 1. Purpose

To check whether the Step 1 result depends on a single random seed,
KoELECTRA Original and Augmented training were repeated with seeds 43 and 44.

The training configuration was identical to seed 42 except for the random seed.

- Model: `monologg/koelectra-base-v3-discriminator`
- Original train rows: 4,809
- Augmented train rows: 14,377
- Validation rows: 604
- Epochs: 3
- Batch size: 16
- Learning rate: 2e-5
- Weight decay: 0.01
- Max length: 128
- FP16: enabled
- Best-model selection: validation F1

Seed-specific outputs are stored under:

- `results/step1_seeds/koelectra/seed43/`
- `results/step1_seeds/koelectra/seed44/`

### 2. Validation summary

| Seed | Training | Best epoch | Validation F1 |
| ---: | --- | ---: | ---: |
| 43 | Original | 2 | 0.9866 |
| 43 | Augmented | 3 | 0.9900 |
| 44 | Original | 1 | 0.9900 |
| 44 | Augmented | 3 | 0.9884 |

All four runs achieved approximately 0.99 validation F1.
Therefore, clean validation performance alone is not sufficient to evaluate robustness to obfuscation.

### 3. Seed 43 evaluation

For obfuscated evaluations, the main result uses only rows with `changed=true`.

| Evaluation | Training | Accuracy | Attack Recall | F1 | Benign FPR |
| --- | --- | ---: | ---: | ---: | ---: |
| clean | Original | 0.9818 | 0.9767 | 0.9816 | 0.0132 |
| clean | Augmented | 0.9868 | 0.9867 | 0.9867 | 0.0132 |
| kg_clean | Original | 0.7674 | 0.6481 | 0.7778 | 0.0312 |
| kg_clean | Augmented | 0.7733 | 0.6944 | 0.7937 | 0.0938 |
| obfuscated | Original | 0.8565 | 0.7179 | 0.8326 | 0.0065 |
| obfuscated | Augmented | 0.9444 | 0.9005 | 0.9416 | 0.0121 |
| kg_obfuscated | Original | 0.5988 | 0.3853 | 0.5483 | 0.0348 |
| kg_obfuscated | Augmented | 0.6671 | 0.5196 | 0.6636 | 0.0795 |

Main obfuscated-test Recall improved from 71.79% to 90.05% (+18.26 percentage points).

### 4. Seed 44 evaluation

| Evaluation | Training | Accuracy | Attack Recall | F1 | Benign FPR |
| --- | --- | ---: | ---: | ---: | ---: |
| clean | Original | 0.9851 | 0.9967 | 0.9852 | 0.0263 |
| clean | Augmented | 0.9934 | 0.9933 | 0.9933 | 0.0066 |
| kg_clean | Original | 0.9070 | 0.9167 | 0.9252 | 0.1094 |
| kg_clean | Augmented | 0.7674 | 0.6759 | 0.7849 | 0.0781 |
| obfuscated | Original | 0.8606 | 0.7330 | 0.8394 | 0.0133 |
| obfuscated | Augmented | 0.9380 | 0.8830 | 0.9341 | 0.0076 |
| kg_obfuscated | Original | 0.6678 | 0.5190 | 0.6638 | 0.0767 |
| kg_obfuscated | Augmented | 0.6454 | 0.4791 | 0.6306 | 0.0690 |

Main obfuscated-test Recall improved from 73.30% to 88.30% (+15.00 percentage points).

### 5. Interim interpretation

The general obfuscated test showed the same direction of improvement for both repeated seeds:

- Seed 43: 71.79% -> 90.05% (+18.26 pp)
- Seed 44: 73.30% -> 88.30% (+15.00 pp)

This provides preliminary evidence that training augmentation with
`yamin_swap` 0.7 and `symbol_insert` 0.3 improves KoELECTRA attack Recall
on the general obfuscated evaluation set.

The KoreanGuardrail supplementary evaluations were not consistent across seeds.
Therefore, conclusions for `kg_clean` and `kg_obfuscated` are deferred until
seed 42 and the three-seed statistics, including AUROC, are available.

### 6. Remaining work

- [x] Seed 43 Original/Augmented training
- [x] Seed 43 four evaluation sets
- [x] Seed 44 Original/Augmented training
- [x] Seed 44 four evaluation sets
- [ ] Seed 42 remaining seven evaluations
- [ ] Three-seed mean and standard deviation
- [ ] AUROC aggregation
- [ ] Final three-seed technique/group-level comparison
- [ ] Final Step 1 comparison table

Raw data, model checkpoints, and prediction-level outputs are not committed to the repository.

### 7. Technique-group interim analysis (seeds 43/44)

To check whether the augmentation effect is limited to the training cells,
the `obfuscated_test` rows with `changed=true` were divided into three groups:

- trained technique, same intensity:
  - `yamin_swap 0.7`
  - `symbol_insert 0.3`
- same technique, different intensity:
  - `yamin_swap 0.3`
  - `symbol_insert 0.7`
- unseen techniques:
  - the remaining 15 techniques

| Seed | Group | Original Recall | Augmented Recall | ΔRecall | Original FPR | Augmented FPR | ΔFPR |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 43 | trained / same intensity | 86.29% | 97.66% | +11.37 pp | 0.50% | 1.32% | +0.83 pp |
| 43 | same technique / other intensity | 57.80% | 93.73% | +35.93 pp | 0.67% | 2.68% | +2.01 pp |
| 43 | unseen 15 techniques | 71.75% | 89.29% | +17.54 pp | 0.66% | 1.11% | +0.45 pp |
| 44 | trained / same intensity | 92.31% | 97.49% | +5.18 pp | 1.82% | 0.99% | -0.83 pp |
| 44 | same technique / other intensity | 56.95% | 94.92% | +37.97 pp | 1.17% | 1.17% | +0.00 pp |
| 44 | unseen 15 techniques | 73.11% | 87.24% | +14.13 pp | 1.31% | 0.72% | -0.59 pp |

Recall increased after augmentation in all three groups for both repeated seeds.

In particular, the unseen 15-technique group improved in both seeds:

- seed 43: 71.75% -> 89.29% (+17.54 pp)
- seed 44: 73.11% -> 87.24% (+14.13 pp)

The same-technique/different-intensity group also showed large gains:

- seed 43: 57.80% -> 93.73% (+35.93 pp)
- seed 44: 56.95% -> 94.92% (+37.97 pp)

These are interim results from seeds 43 and 44 only.
They are therefore interpreted as a consistent direction of improvement across the two repeated seeds,
not yet as a final three-seed generalization result.

Seed 42 will be added using the same grouping rule before the final paper table is produced.

---

## 2026-10-06 — KoELECTRA Final Three-Seed Analysis

### 1. Completion of seed 42 evaluation

The remaining seed 42 evaluations were completed using the shared
KoELECTRA Original and Augmented best-model checkpoints.

The Original clean evaluation was independently reproduced and exactly matched
the previous result:

- TP: 299
- TN: 300
- FP: 4
- FN: 1
- F1: 0.9917

Results are therefore available for seeds 42, 43, and 44 under the same
four evaluation conditions.

For obfuscated evaluations, only rows with `changed=true` are used as the
main analysis set.

### 2. Three-seed summary

Values in parentheses are sample standard deviations across seeds 42, 43, and 44.

| Evaluation | Training | Recall | FPR | F1 | AUROC |
| --- | --- | ---: | ---: | ---: | ---: |
| clean | Original | 99.00 (1.15) | 1.75 (0.76) | 98.62 (0.51) | 0.9986 (0.0009) |
| clean | Augmented | 98.67 (0.67) | 0.88 (0.38) | 98.89 (0.39) | 0.9970 (0.0017) |
| obfuscated | Original | 72.06 (1.13) | 0.88 (0.40) | 83.33 (0.58) | 0.9768 (0.0022) |
| obfuscated | Augmented | **87.71 (2.68)** | 0.87 (0.31) | **93.01 (1.40)** | **0.9919 (0.0010)** |
| kg_clean | Original | 78.09 (13.43) | 7.81 (4.13) | 85.05 (7.37) | 0.9428 (0.0036) |
| kg_clean | Augmented | 67.59 (1.85) | 8.33 (0.90) | 78.34 (1.10) | 0.9144 (0.0082) |
| kg_obfuscated | Original | 44.66 (6.75) | 5.38 (2.12) | 60.23 (5.82) | 0.8704 (0.0154) |
| kg_obfuscated | Augmented | 48.34 (3.42) | 7.05 (0.84) | 63.37 (2.85) | 0.8635 (0.0064) |

On the general obfuscated evaluation, Recall increased from 72.06% to 87.71%,
an average improvement of 15.65 percentage points.

The per-seed Recall changes were:

- seed 42: 71.09% -> 84.79% (+13.70 pp)
- seed 43: 71.79% -> 90.05% (+18.26 pp)
- seed 44: 73.30% -> 88.30% (+15.00 pp)

All three seeds showed the same direction of improvement.

At the same time, mean obfuscated FPR did not increase
(0.88% -> 0.87%).

The clean Recall decrease observed in seed 42 was not consistent across seeds.
The three-seed mean changed only from 99.00% to 98.67%.

### 3. Final technique-group analysis

The 34 technique-by-intensity cells in `obfuscated_test` were divided into:

- trained technique / same intensity: 2 cells
- same technique / different intensity: 2 cells
- unseen techniques: 30 cells (15 techniques × 2 intensities)

Recall and FPR were first calculated for each cell and then averaged within
each group.

| Group | Training | Recall (mean ± SD) | FPR (mean ± SD) |
| --- | --- | ---: | ---: |
| trained / same intensity | Original | 89.82 ± 3.13 | 1.21 ± 0.67 |
| trained / same intensity | Augmented | **96.83 ± 1.30** | 0.88 ± 0.50 |
| same technique / other intensity | Original | 59.35 ± 2.29 | 1.01 ± 0.29 |
| same technique / other intensity | Augmented | **92.09 ± 4.04** | 1.49 ± 1.03 |
| unseen 30 cells | Original | 72.27 ± 1.33 | 0.85 ± 0.41 |
| unseen 30 cells | Augmented | **87.04 ± 2.68** | 0.82 ± 0.24 |

For the 30 cells belonging to techniques that were not used for augmentation,
Recall increased from 72.27% to 87.04% (+14.77 pp).

The improvement therefore was not limited to the two augmentation cells:
the same direction was also observed for different intensities of the trained
techniques and for unseen techniques.

### 4. Comparison with mDeBERTa

mDeBERTa showed the same overall direction:
its three-seed mean obfuscated Recall increased from 78.1% to 91.3%.

KoELECTRA increased from 72.06% to 87.71%.

Thus, augmentation improved general obfuscated-input detection in both
classifier architectures.

In contrast, `kg_clean` and `kg_obfuscated` showed substantial seed variation
and inconsistent Original-to-Augmented changes. No firm augmentation effect is
therefore claimed for the supplementary KoreanGuardrail evaluation sets.

### 5. Final status

- [x] KoELECTRA seeds 42/43/44 Original training
- [x] KoELECTRA seeds 42/43/44 Augmented training
- [x] Four evaluation sets for all three seeds
- [x] Three-seed mean and standard deviation
- [x] AUROC analysis
- [x] Final technique-group comparison
- [x] Comparison under the same framework as mDeBERTa
- [ ] Final KSC Table 2 formatting
- [ ] Final KSC Section 4.3 text

Raw data, model checkpoints, and prediction-level outputs containing source text
are not committed to the public repository.
