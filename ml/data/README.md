# ml/data — 데이터셋 디렉토리

## 구조

```
ml/data/
├── raw/          # 스크랩 원문·스크린샷 등 원본 (git 미포함 — .gitignore 참조)
├── seed/         # 정제된 시드 문장 CSV (git 포함 — 버전 관리 대상)
│   └── seed_clauses.csv
├── pilot/        # 자기 일치도 검증 시트 (1주차 산출물)
├── processed/    # train/val/test 분할 결과 (scripts/split_dataset.py 출력)
│   ├── train_seed.csv   # 161문장 — 증강 대상
│   ├── val_seed.csv     # 34문장 — 시드 원본만
│   └── test_seed.csv    # 34문장 — 시드 원본만, 학습 전 과정에서 참조 금지
└── augmented/    # LLM 증강 문장 (train 시드의 패러프레이즈만)
    └── aug_clauses.csv
```

**git 포함 경계**: 저작권·개인정보 우려가 있는 원본(raw)은 제외하고,
개인정보를 제거·정제한 시드 CSV는 포함해 라벨 이력을 추적한다.

## seed_clauses.csv 스키마

| 컬럼 | 타입 | 설명 |
|---|---|---|
| `id` | int | 문장 고유 번호 (1부터 증가, 재사용 금지) |
| `text` | str | 조항 문장 원문 (개인정보 제거 완료 상태) |
| `category` | str | `deposit_return` \| `repair_defect` \| `restoration` \| `termination_renewal` \| `lien_rights` \| `fees_utilities` \| `etc` |
| `risk_level` | str | `safe` \| `caution` \| `danger` |
| `source` | str | `standard_contract`(표준계약서) \| `guide_column`(예방 가이드·칼럼) \| `community`(커뮤니티) \| `authored`(직접 작성) |
| `source_note` | str | 출처 상세 또는 판정 근거 |
| `collected_at` | date | 수집일 (YYYY-MM-DD) |
| `label_status` | str | `provisional`(잠정) \| `confirmed`(검수 확정) \| `flagged`(경계 사례 — 판정 대기) |

- 인코딩: UTF-8 (BOM 없음), 구분자: 콤마, 줄바꿈 포함 문장은 큰따옴표로 감싼다.
- 카테고리·위험도 판단 기준은 `docs/labeling-guideline.md`(v0.6, 사례집 35건) 참조.

## 분할 원칙 (2주차)

- **분할을 증강보다 먼저 한다.** 스펙 §5.2는 증강(Step 3)→분할(Step 4) 순이지만,
  val/test 시드의 패러프레이즈가 train에 들어가는 평가 오염을 막으려면
  시드를 먼저 나누고 **train 시드만 증강**해야 한다.
- 층화 기준: 카테고리 × 위험도 21칸, 비율 70/15/15, 고정 시드 42 (재현 가능).
- test는 모델 학습·튜닝 전 과정에서 참조하지 않는다 (스펙 §5.2 Step 4).

## aug_clauses.csv 스키마 (증강)

| 컬럼 | 설명 |
|---|---|
| `aug_id` | `a001` 형식 증강 고유 번호 |
| `seed_id` | 원본 시드 id — **train_seed.csv에 있는 id만 허용** |
| `text` | 패러프레이즈 문장 |
| `category`, `risk_level` | 원본 시드에서 상속 (변경 금지) |
| `method` | `reorder`(어순) \| `word_variation`(용어 치환) \| `register`(문체 변환) \| `condense`(축약) \| `expand`(부연) \| `colloquial`(구어체) |
| `created_at`, `review_status` | 생성일 / `provisional` → 검수 후 `confirmed` |

### 증강 규칙 (스펙 §5.2 Step 3)

1. **의미·위험도 보존이 최우선.** 라벨을 바꿀 수 있는 변형 금지:
   금액·기한·범위의 추가/삭제/변경, 긍정↔부정 반전, 의무 주체 변경.
2. 허용 변형: 어순 재배열, 용어 치환(임대인↔집주인·갑, 임차인↔세입자·을,
   보증금↔임차보증금), 문체 변환(한다/하기로 한다/~함/구어체), 축약·부연.
3. 증강 배율 목표: train 시드의 3~4배 (약 500~650문장).
4. **전수 검수 후에만 train에 편입** (`review_status=confirmed`).
   val/test에는 절대 포함하지 않는다.
5. 생성 주체: Claude (LLM 보조) — 시드 라벨링과 동일하게 사람이 최종 검수.
