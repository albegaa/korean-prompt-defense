# Step 1 Lightweight Classifier

## 1. 목적

Step 1의 목적은 한국어 프롬프트 공격을 탐지하는
경량 binary classifier를 학습하고,
한국어 난독화 데이터를 학습에 추가했을 때
난독화 robustness가 어떻게 달라지는지 평가하는 것이다.

Label:

- `0` = Benign
- `1` = Attack

classifier의 class 1 softmax 출력은

    attack_score

로 저장한다.

`attack_score`는 Attack class의 softmax score이며
calibrated probability로 해석하지 않는다.

---

## 2. 비교 모델

### KoELECTRA

    monologg/koelectra-base-v3-discriminator

한국어 전용 encoder 모델이다.

### mDeBERTa

    microsoft/mdeberta-v3-base

다국어 baseline으로 사용한다.

mDeBERTa는 tokenizer 차이를 줄이기 위해
slow tokenizer를 사용한다.

---

## 3. 학습 조건

각 모델에서 두 조건을 비교한다.

### Original-only

원문 train과 original validation만 사용한다.

### Augmented

원문 train과 선정된 난독화 variant를 함께 사용한다.

Original-only와 Augmented는
동일한 validation set을 사용한다.

---

## 4. 실험 행렬

총 4개의 fine-tuned classifier를 평가한다.

| Model | Training |
| --- | --- |
| KoELECTRA | Original |
| KoELECTRA | Augmented |
| mDeBERTa | Original |
| mDeBERTa | Augmented |

---

## 5. 평가 데이터

각 모델은 다음 네 평가셋에서 평가할 수 있다.

### Main

- Clean test
- Obfuscated test

### Supplementary

- KoreanGuardrail clean
- KoreanGuardrail obfuscated

난독화 평가의 주 결과는
실제로 문자열이 변경된

    changed=true

행을 기준으로 본다.

`changed=false` 행은
application rate와 raw artifact 확인을 위해 보존한다.

---

## 6. 증강 조건

사전 screening에서 pass 조건을 만족한 기법은 없었다.

Ambiguous fallback 조건으로 다음 두 cell을
Step 1 증강 후보로 사용한다.

- `yamin_swap`, intensity `0.7`
- `symbol_insert`, intensity `0.3`

이 두 조건은
효과가 입증된 pass 기법이 아니라
ambiguous boundary case이다.

따라서 결과에서도
"유효성이 입증된 공격 기법"으로 표현하지 않는다.

---

## 7. 주요 평가 지표

저장 지표:

- Accuracy
- Precision
- Recall
- F1
- FPR
- FNR
- TP
- TN
- FP
- FN

주요 비교:

- Clean Recall
- Clean F1
- Clean FPR
- Obfuscated Recall
- Obfuscated F1
- Obfuscated FPR

추가로 다음 차이를 확인한다.

    F1 difference
    = Clean F1 - Obfuscated F1

    Recall difference
    = Clean Recall - Obfuscated Recall

Obfuscated 주 결과는 `changed=true` variant 집합을 사용하므로
이 차이는 동일 sample의 paired 전후 감소량으로 해석하지 않는다.

논문에서는

    Clean 대비 changed-only 난독화 평가셋에서
    관찰된 성능 차이

로 해석한다.

---

## 8. 통계 분석

기본 평가 결과 외에
`predictions.csv`를 이용한 통계 분석을 추가할 수 있다.

예정 분석:

- 지표별 95% confidence interval
- 동일 평가 행 기준 Original vs Augmented paired 비교
- 동일 원문에서 파생된 variant를 `seed_id`로 묶은 분석
- 실제 증강에 사용한 selected cell과 나머지 조건 비교

기존 학습 및 평가 코드는 변경하지 않고
후처리 script 형태로 추가하는 것을 원칙으로 한다.

---

## 9. 현재 공통 학습 설정

기본값:

- learning rate = `2e-5`
- weight decay = `0.01`
- max length = `128`
- seed = `42`
- FP16
- best model = validation F1 기준

본실험 전 실제 데이터와 GPU 상황을 확인하여
다음을 최종 확정한다.

- epochs
- batch size

KoELECTRA와 mDeBERTa는
가능한 한 동일한 조건을 사용한다.

---

## 10. 연구 범위

현재 데이터 구성은

    영어 원문 기준 300자 이하의
    단일 짧은 프롬프트

를 대상으로 한다.

Step 1 모델의 `max_length=128`은 유지한다.

KoELECTRA와 mDeBERTa tokenizer 모두
`truncation_side=right`임을 확인하였으므로
128 token을 넘는 경우 입력 뒤쪽이 잘린다.

최종 번역 데이터 수신 후에는
실제 tokenizer 기준으로
128 token 초과 비율을 별도로 확인한다.

장문의 DAN류 jailbreak,
긴 문서 내부의 indirect injection 등은
현재 Step 1의 직접적인 범위에서 제외한다.
