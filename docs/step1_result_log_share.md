# Step 1 실험 결과 기록

## 2026-10-03 — KoELECTRA 원본 데이터 학습 (Original-only)

### 1. 학습 설정

- 모델: `monologg/koelectra-base-v3-discriminator`
- 학습 방식: 원본 데이터만 사용 (Original-only)
- 학습 데이터: `data/step1/train.jsonl`
- 검증 데이터: `data/step1/valid.jsonl`
- 학습 데이터 수: 4,809
- 검증 데이터 수: 604
- Epoch 수: 3
- 배치 크기: 16
- 학습률: 2e-5
- Weight decay: 0.01
- 최대 입력 길이: 128
- Seed: 42
- FP16: 사용
- 최적 모델 선정 기준: 검증 F1

### 2. 검증 결과

최적 Epoch: 3

| 지표 | 결과 |
| --- | ---: |
| 정확도 (Accuracy) | 0.9868 |
| 정밀도 (Precision) | 0.9803 |
| 공격 재현율 (Attack Recall) | 0.9933 |
| F1 | 0.9868 |
| 정상 오탐률 (Benign FPR) | 0.0197 |
| 공격 미탐률 (FNR) | 0.0067 |
| TP | 298 |
| TN | 298 |
| FP | 6 |
| FN | 2 |
| 검증 손실 (Validation loss) | 0.0494 |

저장된 모델:

`results/step1/koelectra/original/best_model`

### 3. Clean 테스트 결과

입력 데이터:

`data/step1/test.jsonl`

- 전체 데이터 수: 604
- 정상 데이터: 304
- 공격 데이터: 300
- 평가 배치 크기: 8
- 최대 입력 길이: 128
- FP16: 사용

| 지표 | 결과 |
| --- | ---: |
| 정확도 (Accuracy) | 0.9917 |
| 정밀도 (Precision) | 0.9868 |
| 공격 재현율 (Attack Recall) | 0.9967 |
| F1 | 0.9917 |
| 정상 오탐률 (Benign FPR) | 0.0132 |
| 공격 미탐률 (FNR) | 0.0033 |
| TP | 299 |
| TN | 300 |
| FP | 4 |
| FN | 1 |
| 손실 (Loss) | 0.0474 |

출력 파일:

- `results/step1/koelectra/original/eval/clean/predictions.csv`
- `results/step1/koelectra/original/eval/clean/metrics.json`

### 4. 현재 진행 상태

- [x] KoELECTRA 원본 데이터 학습
- [x] KoELECTRA 원본 모델 Clean 테스트
- [x] KoELECTRA 증강 데이터 학습
- [ ] KoELECTRA 원본 모델 난독화 테스트
- [ ] KoELECTRA 증강 모델 Clean 테스트
- [ ] KoELECTRA 증강 모델 난독화 테스트
- [ ] KoreanGuardrail 보조 평가

증강 학습 데이터와 17종 난독화 평가 데이터는 2026-10-04에 전달받았으며,
Step 1 데이터 검증 스크립트를 통과하였다.

### 5. xTRam1 길이 구간별 분석

KoELECTRA 원본 모델의 Clean 테스트 예측 결과 중
`source == "xtram1"`인 행만 사용하여 문자 길이를 기준으로 4개 구간으로 나누고,
공격 재현율과 정상 오탐률을 확인하였다.

| 길이 구간 | 전체 수 | 공격 수 | 정상 수 | 공격 재현율 | 정상 오탐률 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0~40 | 84 | 36 | 48 | 1.0000 | 0.0208 |
| 40~55 | 125 | 84 | 41 | 1.0000 | 0.0000 |
| 55~70 | 86 | 39 | 47 | 1.0000 | 0.0000 |
| 70+ | 112 | 44 | 68 | 0.9773 | 0.0000 |

KoELECTRA 원본 모델의 Clean 테스트에서는
길이 구간에 따른 큰 성능 차이는 관찰되지 않았다.

가장 긴 70+ 구간에서는 공격 44건 중 1건을 놓쳤으며,
가장 짧은 0~40 구간에서는 정상 48건 중 1건을 공격으로 오탐하였다.

최종 비교에서는 KoELECTRA 증강 모델과 mDeBERTa 결과에도
동일한 길이 구간 분석을 적용한다.

---

## 2026-10-04 — KoELECTRA 증강 데이터 학습 (Augmented)

### 1. 학습 설정

- 모델: `monologg/koelectra-base-v3-discriminator`
- 학습 방식: 증강 데이터 사용 (Augmented)
- 원본 학습 데이터: `data/step1/train.jsonl`
- 증강 학습 데이터: `data/step1/augmented_train.jsonl`
- 검증 데이터: `data/step1/valid.jsonl`
- 최종 학습 데이터 수: 14,377
- 원본 데이터 수: 4,809
- 변형 데이터 수: 9,568
- 정상 데이터: 7,200
- 공격 데이터: 7,177
- 학습에 사용한 증강 조건:
  - `yamin_swap`, intensity 0.7: 4,759건
  - `symbol_insert`, intensity 0.3: 4,809건
- Epoch 수: 3
- 배치 크기: 16
- 학습률: 2e-5
- Weight decay: 0.01
- 최대 입력 길이: 128
- Seed: 42
- FP16: 사용
- 최적 모델 선정 기준: 검증 F1

전달받은 `augmented_train.jsonl`에는
원본 학습 데이터 4,809건이 이미 포함되어 있다.

`prepare_augmented_train.py`는 해당 파일을 `combined` 모드로 인식하였으며,
원본 데이터를 중복으로 추가하지 않고 총 14,377건을 그대로 학습에 사용하였다.

### 2. 검증 결과

최적 Epoch: 1

| 지표 | 결과 |
| --- | ---: |
| 정확도 (Accuracy) | 0.9917 |
| 정밀도 (Precision) | 0.9868 |
| 공격 재현율 (Attack Recall) | 0.9967 |
| F1 | 0.9917 |
| 정상 오탐률 (Benign FPR) | 0.0132 |
| 공격 미탐률 (FNR) | 0.0033 |
| TP | 299 |
| TN | 300 |
| FP | 4 |
| FN | 1 |
| 검증 손실 (Validation loss) | 0.0363 |

저장된 모델:

`results/step1/koelectra/augmented/best_model`

학습 결과 파일:

- `results/step1/koelectra/augmented/validation_results.csv`
- `results/step1/koelectra/augmented/metrics.json`
- `results/step1/koelectra/augmented/training_history.csv`
- `results/step1/koelectra/augmented/best_model`

### 3. Epoch별 학습 및 검증 결과

| Epoch | 학습 손실 | 검증 정확도 | 검증 정밀도 | 검증 공격 재현율 | 검증 F1 | 검증 정상 오탐률 | 검증 FNR | 검증 손실 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.1012 | 0.9917 | 0.9868 | 0.9967 | 0.9917 | 0.0132 | 0.0033 | 0.0363 |
| 2 | 0.0216 | 0.9801 | 0.9645 | 0.9967 | 0.9803 | 0.0362 | 0.0033 | 0.0816 |
| 3 | 0.0115 | 0.9851 | 0.9866 | 0.9833 | 0.9850 | 0.0132 | 0.0167 | 0.0558 |

### 4. 원본 학습 모델과 증강 학습 모델의 검증 성능 비교

| 학습 방식 | 최적 Epoch | 정확도 | 공격 재현율 | F1 | 정상 오탐률 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 원본 데이터 학습 | 3 | 0.9868 | 0.9933 | 0.9868 | 0.0197 |
| 증강 데이터 학습 | 1 | 0.9917 | 0.9967 | 0.9917 | 0.0132 |

Clean 검증 데이터에서는 증강 학습 모델이 원본 학습 모델보다
F1이 소폭 높고 정상 오탐률은 낮게 나타났다.

다만 이 검증 결과만으로 난독화 공격에 대한 강건성이 향상되었다고 판단할 수는 없다.

최종적인 증강 효과 평가는
Clean 테스트셋과 17종 난독화 테스트셋에서
원본 학습 모델과 증강 학습 모델을 동일한 조건으로 비교한 뒤 판단한다.

### 5. 후속 평가 항목

- [ ] KoELECTRA 원본 모델 난독화 테스트
- [ ] KoELECTRA 증강 모델 Clean 테스트
- [ ] KoELECTRA 증강 모델 난독화 테스트
- [ ] KoELECTRA 원본/증강 모델 KoreanGuardrail 평가
- [ ] 원본 모델과 증강 모델의 paired/statistical 비교
