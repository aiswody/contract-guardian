# 파일럿 — 자기 일치도 검증 (가이드라인 §6)

시드 102문장 중 무작위 50문장으로 라벨링 기준의 안정성을 검증한다.
`make_pilot.py`(고정 시드 42)로 생성 — 재실행해도 같은 표본.

## 진행 방법

1. **1회차 (지금)**: `pilot_round1.csv`의 `category`, `risk_level`을
   `docs/labeling-guideline.md` 기준으로 작성한다.
   - `risk_level`: `safe` / `caution` / `danger`
   - `category`: `deposit_return` / `repair_defect` / `restoration` / `termination_renewal` / `lien_rights` / `fees_utilities` / `etc`
   - 판단이 어려웠던 문장은 `memo`에 이유를 남긴다 (경계 사례집 후보)
2. **2회차 (최소 3일 후)**: `pilot_round2.csv`를 **1회차 결과를 보지 않고** 작성한다.
3. **비교**: `python ml/scripts/pilot_agreement.py`
   - 위험도 일치율 90% 이상 → 합격, 2주차 본 라벨링 진행
   - 90% 미만 → 불일치 문장을 가이드라인 §5(경계 사례집)에 수록하고 기준 보완 후 재검증

## 주의

- `pilot_mapping.csv`(pilot_no → seed_id 매핑)는 비교 단계 전에 열어보지 않는다.
  시드 CSV의 잠정 라벨이 답안지 역할을 하므로, 미리 보면 검증이 무의미해진다.
- 라벨링 중 가이드라인의 허점을 발견하면 그 자리에서 가이드라인을 고치지 말고
  memo에 기록만 한다. (1·2회차가 같은 기준 위에서 이루어져야 일치율이 의미를 가짐)
