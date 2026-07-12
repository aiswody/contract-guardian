# ml/data — 데이터셋 디렉토리

## 구조

```
ml/data/
├── raw/          # 스크랩 원문·스크린샷 등 원본 (git 미포함 — .gitignore 참조)
├── seed/         # 정제된 시드 문장 CSV (git 포함 — 버전 관리 대상)
│   └── seed_clauses.csv
└── processed/    # 2주차 이후: 증강·분할 결과 (train/val/test)
```

**git 포함 경계**: 저작권·개인정보 우려가 있는 원본(raw)은 제외하고,
개인정보를 제거·정제한 시드 CSV는 포함해 라벨 이력을 추적한다.

## seed_clauses.csv 스키마

| 컬럼 | 타입 | 설명 |
|---|---|---|
| `id` | int | 문장 고유 번호 (1부터 증가, 재사용 금지) |
| `text` | str | 조항 문장 원문 (개인정보 제거 완료 상태) |
| `category` | str | `deposit_return` \| `repair_defect` \| `restoration` \| `termination_renewal` \| `lien_rights` \| `fees_utilities` \| `etc` |
| `risk_level` | str | `safe` \| `caution` \| `danger` (잠정 라벨 — 2주차 본 라벨링에서 확정) |
| `source` | str | `standard_contract`(표준계약서) \| `guide_column`(예방 가이드·칼럼) \| `community`(커뮤니티) \| `authored`(직접 작성) |
| `source_note` | str | 출처 상세 (URL, 문서명 등. 커뮤니티는 게시판명 수준까지만) |
| `collected_at` | date | 수집일 (YYYY-MM-DD) |
| `label_status` | str | `provisional`(잠정) \| `confirmed`(2주차 확정) \| `flagged`(경계 사례 — 가이드라인 논의 필요) |

- 인코딩: UTF-8 (BOM 없음), 구분자: 콤마, 줄바꿈 포함 문장은 큰따옴표로 감싼다.
- 카테고리·위험도 코드의 정의와 판단 기준은 `docs/risk-pattern-matrix.md` 및 `docs/labeling-guideline.md` 참조.
- `uncertain`은 모델 출력 상태이지 라벨이 아니므로 이 파일에 등장하지 않는다.
