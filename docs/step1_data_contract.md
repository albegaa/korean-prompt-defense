# Step 1 Data Contract

## 1. 기본 파일

Step 1에서 사용하는 기본 파일은 다음과 같다.

- `train.jsonl`
- `valid.jsonl`
- `test.jsonl`
- `kg_test.jsonl`
- `kg_test_meta.jsonl`

최종 전달 규모:

- `train.jsonl`: 4,809건 (Attack 2,401 / Benign 2,408)
- `valid.jsonl`: 604건 (Attack 300 / Benign 304)
- `test.jsonl`: 604건 (Attack 300 / Benign 304)
- `kg_test.jsonl`: 172건 (Attack 108 / Benign 64)

train에는 xTRam1 길이 보정을 위한 `_dup1` 복제 행 373건이 포함된다.
이 행들은 오류가 아니라 train 내부 길이 분포 보정을 위해 의도적으로 추가된 데이터이다.

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

`deepset/prompt-injections`는 다른 데이터와 label 기준이 충돌하여 제외한다.

xTRam1 benign도 정상 데이터에 포함하여
Attack과 Benign의 source가 완전히 분리되는 것을 줄인다.

---

## 4. 원본 데이터 정리 및 분할

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

분할 원칙:

- 공격 문장은 영어 원문 단어 Jaccard 유사도 0.6 이상이면 같은 group으로 묶는다.
- 같은 공격 group은 train / valid / test 중 한 split에만 들어간다.
- 30건 이상인 큰 공격 group은 train에 고정한다.
- `(label, source)` 조합별로 train : valid : test = 8 : 1 : 1이 되도록 층화한다.
- augmentation 전에 split한다.
- fixed random seed를 사용한다.
- test 공격은 train에서 유사한 표현을 본 적 없는 공격으로 구성된다.

train의 xTRam1 정상 데이터에는 길이 분포 보정을 위한 `_dup1` 복제 행 373건이 포함된다.

valid / test에는 이 길이 보정을 적용하지 않는다.

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

KoELECTRA와 mDeBERTa tokenizer 모두 `truncation_side=right`임을 확인하였다.

따라서 128 token을 초과하면 입력 뒤쪽이 잘린다.

실제 전달된 train / valid / test 6,017건의 token 길이를 확인한 결과:

- KoELECTRA: 128 token 초과 0 / 6,017건
  - train 0 / 4,809
  - valid 0 / 604
  - test 0 / 604
- mDeBERTa: 128 token 초과 5 / 6,017건 (0.0831%)
  - train 4 / 4,809
  - valid 1 / 604
  - test 0 / 604
- `kg_test` 172건: 두 tokenizer 모두 128 token 초과 0건

mDeBERTa의 5건도 잘리는 부분은 문장 끝 일부이며,
공격 지시는 앞쪽에 남아 있는 것으로 확인되었다.

따라서 Step 1의 `max_length=128` 설정은 유지한다.

추후 증강 및 난독화 데이터가 전달되면 다음 파일도 동일하게 token 길이를 확인한다.

- augmented train
- obfuscated test
- obfuscated KG test

---

## 6. Benign sampling

Benign 데이터는 후보 전체에서 단순 random sampling하지 않는다.

Attack의 길이 분포를 기준으로 길이 구간별로 대응되도록 추출하고,
최종적으로 Attack과 Benign을 약 1 : 1로 구성한다.

목적은 모델이 입력 길이를 label shortcut으로 학습하는 가능성을 줄이기 위함이다.

---

## 7. 번역 관련 기록

최종 데이터의 번역 구성은 다음과 같다.

Attack:

- train / valid / test의 공격 문장은 모두 영어 원문을 한국어로 번역한 문장

Benign:

| Split | 번역 | KoAlpaca 한국어 원본 |
| --- | ---: | ---: |
| train | 2,157 (89.1%) | 265 (10.9%) |
| valid | 271 (89.1%) | 33 (10.9%) |
| test | 271 (89.1%) | 33 (10.9%) |

공격은 모두 번역문이므로 classifier가 공격 특성 대신 번역투를 shortcut으로 사용할 가능성이 남아 있다.

이를 보조적으로 확인하기 위해 KoreanGuardrail 평가를 별도로 수행한다.

KoreanGuardrail은 "한국어 원본"이라고 표현하지 않고

```text
번역이 아닌 방식으로 만든 한국어 평가셋
```

으로 구분한다.

---

## 8. KoreanGuardrail 보조 평가

`kg_test.jsonl`은 메인 test와 섞지 않고 별도로 평가한다.

최종 구성:

- `kg_test.jsonl`: 172건
- Attack: 108건
- Benign: 64건
- 전체 KG 후보 249건에서 screening 시드 70건과 외국어 공격 E2 7건 제외
- A1 / A2 등 공격 → label 1
- Benign → label 0

채점에는 반드시 `kg_test.jsonl`의 `label`을 사용한다.

`kg_test_meta.jsonl`은 KG 원본 category / subtype 등 참고용 metadata이며,
그 안의 `kg_label`은 Step 1 classifier 채점에 사용하지 않는다.

KoreanGuardrail은 Claude 생성 후 검수된 데이터이므로
자연발생 한국어 원본 데이터로 표현하지 않는다.

---

## 9. Variant metadata

난독화 평가 및 증강 데이터에는 기본 필드 외에 다음 metadata가 추가된다.

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

난독화 robustness의 주 성능은 `changed=true` 행을 기준으로 계산한다.

### Augmented training

`changed=false` variant는 원문과 동일한 no-op duplicate이므로
증강 학습 데이터에서 제외한다.

---

## 11. 증강 조건

Step 1 증강 후보:

- `yamin_swap`, intensity `0.7`
- `symbol_insert`, intensity `0.3`

두 조건은 screening에서 pass한 기법이 아니라 ambiguous fallback 조건이다.

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

train의 `_dup1` 행은 길이 보정을 위해 의도적으로 만든 train-only 복제이므로
일반 duplicate 오류와 구분한다.

---

## 13. 추가 평가 시 주의

valid / test의 xTRam1 공격-정상 길이 분포 차이가 일부 남아 있다.

따라서 최종 test 결과에서는 `source == "xtram1"`인 행을 text 길이 기준으로 나누어
구간별 Attack Recall과 Benign FPR도 확인한다.

권장 구간:

- 0~40자
- 40~55자
- 55~70자
- 70자 이상

---

## 14. 데이터 공개 주의

xTRam1은 라이선스가 명시되지 않아 팀 내부 실험용으로만 사용하고 외부 배포하지 않는다.

따라서 xTRam1이 포함된 원본 데이터 및 최종 Step 1 데이터 파일은
공용 Git 저장소에 직접 commit하지 않는다.

실제 데이터 공개 여부는 각 원본 데이터의 라이선스 및 사용 조건을 별도로 확인한다.
