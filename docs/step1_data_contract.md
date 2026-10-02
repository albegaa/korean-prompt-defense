# Step 1 Data Contract

## 1. 기본 파일

Step 1에서 사용하는 기본 원본 파일은 다음과 같다.

- `train.jsonl`
- `valid.jsonl`
- `test.jsonl`
- `kg_test.jsonl`

목표 규모:

- Attack 약 3,000건
- Benign 약 3,000건
- Attack : Benign = 1 : 1

---

## 2. 기본 필드

| Field | 의미 |
| --- | --- |
| `id` | 각 행의 고유 ID |
| `text` | 모델 입력 한국어 문장 |
| `label` | 0 = Benign, 1 = Attack |
| `source` | 원본 데이터 출처 |

예:

```json
{
  "id": "xtram1_00123",
  "text": "사용자 입력",
  "label": 1,
  "source": "xtram1"
}
```

---

## 3. 원본 데이터 구성

### Attack

- Lakera `gandalf_ignore_instructions`
- xTRam1 attack 행

### Benign

- xTRam1 benign 행
- KoAlpaca-RealQA
- hh-rlhf helpful-base
- prompts.chat

초기 후보였던 `deepset/prompt-injections`는
다른 데이터와 label 기준이 충돌하여 제외한다.

xTRam1 benign도 정상 후보에 포함하여
Attack과 Benign의 source가 완전히 분리되는 것을 줄인다.

---

## 4. 원본 데이터 정리

원본 데이터셋이 제공하는 split은 그대로 사용하지 않는다.

처리 흐름:

```text
원본 데이터 통합
    ↓
conflicting label 제거
    ↓
내부 및 출처 간 duplicate 제거
    ↓
길이 조건 적용
    ↓
Benign length matching
    ↓
자체 train / valid / test split
```

분할 비율:

```text
8 : 1 : 1
```

원칙:

- split별 Attack : Benign 비율 유지
- fixed random seed 사용
- augmentation 전에 원문 단위로 split
- 동일 원문이 train / valid / test에 동시에 포함되지 않음

---

## 5. 길이 정책

본 연구는

```text
영어 원문 기준 300자 이하의
단일 짧은 프롬프트
```

를 대상으로 한다.

300자 기준은 번역 전 영어 원문을 선택하기 위한 기준이다.

번역된 최종 한국어 `text`에 다시 300자 제한을 적용한다는 의미는 아니다.

Step 1 classifier는

```text
max_length = 128
```

을 사용한다.

KoELECTRA와 mDeBERTa tokenizer 모두
`truncation_side=right`임을 확인하였다.

따라서 128 token을 초과하면 입력의 뒤쪽이 잘린다.

최종 데이터 수신 후 실제 tokenizer 기준으로
128 token 초과 비율을 별도로 측정한다.

확인 대상:

- train
- valid
- test
- kg_test
- augmented train
- obfuscated test
- obfuscated KG test

---

## 6. Benign sampling

Benign 데이터는 후보 전체에서 단순 random sampling하지 않는다.

Attack의 길이 분포를 기준으로 길이 구간별로 대응되도록 추출하고,
최종적으로 Attack과 Benign을 1 : 1로 구성한다.

목적은 모델이 입력 길이를 label shortcut으로 학습하는 가능성을 줄이기 위함이다.

---

## 7. 번역 관련 기록

최종 데이터 카드에는
train / valid / test 각각의 번역 여부 분포를 기록한다.

최소 확인 항목:

- split별 translated / non-translated 비율
- label별 translated / non-translated 비율

예:

```text
train Attack translated %
train Benign translated %

valid Attack translated %
valid Benign translated %

test Attack translated %
test Benign translated %
```

이는 classifier가 공격 특성 대신 번역 문체를
shortcut으로 학습했는지 해석할 때 사용한다.

KoreanGuardrail은 "한국어 원본"이라고 표현하지 않고

```text
번역이 아닌 방식으로 만든 한국어 평가셋
```

으로 구분한다.

---

## 8. KoreanGuardrail 보조 평가

`kg_test.jsonl`은 메인 test와 섞지 않고 별도로 평가한다.

현재 구성:

- 전체 시드 249건
- screening에 사용한 70건 제외
- 최종 179건
- A1 / A2 → label 1
- Benign → label 0

KoreanGuardrail은 Claude 생성 후 검수된 데이터이므로
자연발생 한국어 원본 데이터로 표현하지 않는다.

---

## 9. Variant metadata

난독화 평가 및 증강 데이터에는
기본 필드 외에 다음 metadata가 추가된다.

| Field | 의미 |
| --- | --- |
| `seed_id` | variant가 파생된 원문의 `id` |
| `technique` | 난독화 기법 |
| `intensity` | 난독화 강도 |
| `changed` | 변형 결과가 원문과 실제로 다른지 |
| `n_changed` | 실제 변경 위치 수 |

관계:

```text
original.id == variant.seed_id
```

각 variant 자체의 `id`는 새로 부여한다.

---

## 10. changed 처리

### Evaluation

`changed=false` 행도 평가 파일에는 유지한다.

용도:

- application rate 확인
- transformation 적용 여부 검산
- raw artifact 보존

난독화 robustness의 주 성능은

```text
changed=true
```

행을 기준으로 계산한다.

### Augmented training

`changed=false` variant는
원문과 동일한 no-op duplicate이므로
증강 학습 데이터에서 제외한다.

---

## 11. 증강 조건

Step 1 증강 후보:

- `yamin_swap`, intensity `0.7`
- `symbol_insert`, intensity `0.3`

두 조건은 screening에서 pass한 기법이 아니라
ambiguous fallback 조건이다.

증강은 train split에만 적용한다.

---

## 12. Leakage 기준

원본 행의 group ID:

```text
id
```

variant 행의 group ID:

```text
seed_id
```

허용:

- train ↔ train에서 생성된 augmented variant
- test ↔ test에서 생성된 obfuscated variant
- kg_test ↔ kg_test에서 생성된 obfuscated variant

금지:

- train group ↔ valid group
- train group ↔ test group
- train group ↔ KG evaluation group

또한 split 전에 exact duplicate를 제거한다.

---

## 13. 데이터 공개 주의

라이선스 또는 재배포 제한이 있는 원본 데이터는 Git에 commit하지 않는다.

특히 xTRam1 원본 데이터는 공용 저장소에 직접 업로드하지 않는다.

실제 데이터 공개 여부는 각 원본 데이터의 라이선스 및 사용 조건을 별도로 확인한다.
