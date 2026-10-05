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

증강 학습 데이터와 17개 난독화 기법 × 2개 강도(0.3, 0.7)로 구성된 평가 데이터는 2026-10-04에 전달받았으며, Step 1 데이터 검증 스크립트를 통과하였다.

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

---

## 2026-10-05 — KoELECTRA Seed 43/44 반복 실험

### 1. 목적

기본 실험 seed 42의 결과가 특정 초기화에 의존하는지 확인하고,
mDeBERTa와 동일한 3-seed 기준(seed 42, 43, 44)으로 비교하기 위해
KoELECTRA Original/Augmented 모델을 seed 43, 44에서 추가 학습하였다.

학습 설정은 seed를 제외하고 기존 seed 42 실험과 동일하다.

- 모델: `monologg/koelectra-base-v3-discriminator`
- Epoch 수: 3
- Batch size: 16
- Learning rate: 2e-5
- Weight decay: 0.01
- Max length: 128
- FP16: 사용
- 최적 모델 선정 기준: validation F1
- Original train: 4,809건
- Augmented train: 14,377건
- Validation: 604건

seed 43, 44 결과는 다음 경로에 저장하였다.

- `results/step1_seeds/koelectra/seed43/`
- `results/step1_seeds/koelectra/seed44/`

### 2. 학습 및 검증 결과

| Seed | 학습 방식 | Best epoch | Accuracy | Attack Recall | F1 | Benign FPR |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 43 | Original | 2 | 0.9868 | 0.9833 | 0.9866 | 0.0099 |
| 43 | Augmented | 3 | 0.9901 | 0.9900 | 0.9900 | 0.0099 |
| 44 | Original | 1 | 0.9901 | 0.9933 | 0.9900 | 0.0132 |
| 44 | Augmented | 3 | 0.9884 | 0.9933 | 0.9884 | 0.0164 |

validation F1은 네 모델 모두 약 0.99 수준으로 높아,
validation 성능만으로 난독화 강건성 차이를 판단하기는 어렵다.

### 3. Seed 43 평가 결과

난독화 평가는 팀 기준에 따라 `changed=true` 행만 주 결과로 사용하였다.

| 평가 | 학습 방식 | Accuracy | Attack Recall | F1 | Benign FPR |
| --- | --- | ---: | ---: | ---: | ---: |
| clean | Original | 0.9818 | 0.9767 | 0.9816 | 0.0132 |
| clean | Augmented | 0.9868 | 0.9867 | 0.9867 | 0.0132 |
| kg_clean | Original | 0.7674 | 0.6481 | 0.7778 | 0.0312 |
| kg_clean | Augmented | 0.7733 | 0.6944 | 0.7937 | 0.0938 |
| obfuscated | Original | 0.8565 | 0.7179 | 0.8326 | 0.0065 |
| obfuscated | Augmented | 0.9444 | 0.9005 | 0.9416 | 0.0121 |
| kg_obfuscated | Original | 0.5988 | 0.3853 | 0.5483 | 0.0348 |
| kg_obfuscated | Augmented | 0.6671 | 0.5196 | 0.6636 | 0.0795 |

주요 변화:

- clean Recall: 97.67% → 98.67% (+1.00%p)
- kg_clean Recall: 64.81% → 69.44% (+4.63%p)
- obfuscated Recall: 71.79% → 90.05% (**+18.26%p**)
- kg_obfuscated Recall: 38.53% → 51.96% (+13.43%p)

seed 43에서는 증강 후 일반 난독화 평가의 Recall이 크게 상승하였다.
다만 kg 계열에서는 Recall 상승과 함께 FPR도 증가하였다.

### 4. Seed 44 평가 결과

| 평가 | 학습 방식 | Accuracy | Attack Recall | F1 | Benign FPR |
| --- | --- | ---: | ---: | ---: | ---: |
| clean | Original | 0.9851 | 0.9967 | 0.9852 | 0.0263 |
| clean | Augmented | 0.9934 | 0.9933 | 0.9933 | 0.0066 |
| kg_clean | Original | 0.9070 | 0.9167 | 0.9252 | 0.1094 |
| kg_clean | Augmented | 0.7674 | 0.6759 | 0.7849 | 0.0781 |
| obfuscated | Original | 0.8606 | 0.7330 | 0.8394 | 0.0133 |
| obfuscated | Augmented | 0.9380 | 0.8830 | 0.9341 | 0.0076 |
| kg_obfuscated | Original | 0.6678 | 0.5190 | 0.6638 | 0.0767 |
| kg_obfuscated | Augmented | 0.6454 | 0.4791 | 0.6306 | 0.0690 |

주요 변화:

- clean Recall: 99.67% → 99.33% (-0.34%p)
- kg_clean Recall: 91.67% → 67.59% (-24.08%p)
- obfuscated Recall: 73.30% → 88.30% (**+15.00%p**)
- kg_obfuscated Recall: 51.90% → 47.91% (-3.99%p)

seed 44에서도 일반 난독화 평가의 Recall은 증강 후 크게 상승하였다.
반면 kg 계열은 seed 43과 증감 방향이 일치하지 않았다.

### 5. 현재까지의 관찰

seed 43과 44 모두 `obfuscated_test`에서는 증강 학습 후 Recall이 같은 방향으로 상승하였다.

- seed 43: 71.79% → 90.05% (+18.26%p)
- seed 44: 73.30% → 88.30% (+15.00%p)

따라서 현재까지는 `yamin_swap 0.7`과 `symbol_insert 0.3`을 이용한
증강 학습이 일반 난독화 평가에서 KoELECTRA의 공격 탐지 Recall을 높이는 경향이 관찰된다.

반면 `kg_clean`과 `kg_obfuscated`는 seed에 따라 증강 효과의 방향이 달라졌다.
따라서 KoreanGuardrail 기반 보조 평가에 대해서는 단일 seed 결과로 결론을 내리지 않고,
seed 42까지 포함한 3-seed 결과와 AUROC를 함께 확인한 뒤 최종 해석한다.

### 6. 현재 진행 상태

- [x] KoELECTRA seed 43 Original 학습
- [x] KoELECTRA seed 43 Augmented 학습
- [x] KoELECTRA seed 43 평가 4종
- [x] KoELECTRA seed 44 Original 학습
- [x] KoELECTRA seed 44 Augmented 학습
- [x] KoELECTRA seed 44 평가 4종
- [ ] KoELECTRA seed 42 나머지 7개 평가
- [ ] seed 42/43/44 3-seed 평균 및 표준편차
- [ ] AUROC 계산
- [ ] 기법 그룹별 비교
- [ ] mDeBERTa와 동일 형식의 표 2 최종 정리

seed 42의 Original/Augmented `best_model`은 후속 평가를 위해 팀원에게 공유하였다.

### 7. 결과 파일

seed 43, 44의 평가 결과는 각각 아래에 저장되어 있다.

`results/step1_seeds/koelectra/seed{43,44}/{original,augmented}/eval/`

각 평가 폴더에는:

- `metrics.json`
- `predictions.csv`

가 저장되어 있으며, 난독화 평가에는 추가로:

- `analysis/obfuscated_overall.csv`
- `analysis/obfuscated_by_technique.csv`
- `analysis/obfuscated_by_cell.csv`

가 생성되었다.

데이터, 모델, prediction 결과는 저장소에 커밋하지 않고 로컬/서버에서만 관리한다.
