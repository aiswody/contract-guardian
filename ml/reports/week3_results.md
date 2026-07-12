# 3주차 모델 결과 리포트

> 모든 수치는 `ml/scripts/eval_utils.py` 기준 (Macro-F1 + danger Recall).
> **개발 중 평가는 val(34문장)만 사용.** test(34문장)는 3주차 말 최종 비교에서 1회만 개봉.
> val이 작아(클래스당 9~14건) 수치의 신뢰구간이 넓다는 점을 감안할 것 (2주차 기록 참조).

## 위험도 3-class — val 결과

| 모델 | Macro-F1 | danger Recall | 비고 |
|---|---|---|---|
| Baseline 1 — 키워드 규칙 | 0.537 | 0.455 | danger precision 1.000 (규칙에 걸리면 확실하나 절반을 놓침) |
| Baseline 2 — TF-IDF + LR | 0.530 | 0.545 | train 0.992 → val 0.530, 심한 과적합 |
| KLUE-RoBERTa-base **1차 (실패)** | 0.635 | **0.273** | 과소학습 — 아래 진단 참조 |
| KLUE-RoBERTa-base 2차 (재학습) | (진행 중) | (진행 중) | `train_local.py` — 에폭 8, 결합 선택 기준, danger 가중 손실 |

### 1차 학습 실패 진단 (기록)

- 증상: danger Recall 0.273으로 baseline보다 낮음. train 데이터에서조차 Macro-F1 0.796,
  confidence 평균 0.69 — 자기 학습 데이터도 못 맞히는 과소학습 상태.
- 대조군: 동일 스크립트의 카테고리 모델은 train 1.000 / val 0.840으로 정상 학습됨.
- 원인: `load_best_model_at_end`가 **34문장 val의 macro-F1 단독**으로 best를 선택 —
  위험도 과제는 val 수치 요동이 커서 덜 배운 초기 에폭 체크포인트가 우연히 선택됨.
- 조치 (`train_local.py`): ① 에폭 5→8, ② best 선택 기준을 (Macro-F1 + danger Recall)/2
  결합 점수로 변경 — FN 최소화 원칙의 학습 단계 적용, ③ danger 가중 손실(1.5배).
- 교훈: 작은 val로 체크포인트를 고를 때는 선택 지표가 서비스의 비용 구조(danger FN)를
  반영해야 한다.

### 해석

- 규칙 기반(B1)은 danger precision 1.0 — 유형표의 대표 패턴이 정확하다는 방증.
  그러나 표현이 조금만 변형돼도 놓친다 (Recall 0.455). "패턴 사전으로는 재현율을
  못 채운다"가 파인튜닝의 존재 이유.
- TF-IDF(B2)는 train을 통째로 외웠지만 val(증강 없는 시드 원본)에서 무너짐 —
  표면 n-gram이 아니라 의미 이해가 필요하다는 근거.
- val 34문장 기준 오차가 크므로, baseline 간 우열(0.537 vs 0.530)은 유의미한
  차이로 해석하지 않는다.

## 카테고리 7-class — val 결과

| 모델 | Macro-F1 | 비고 |
|---|---|---|
| KLUE-RoBERTa-base (1차 학습) | **0.840** | deposit_return·lien_rights 100%. 혼동은 fees↔repair(비용 배분 vs 수리 책임 — 라벨링에서도 어려웠던 경계) |

baseline은 위험도만 다룬다 (스펙 §5.3 표). 카테고리 모델은 1차 학습으로 충분해 재학습 대상 아님.

## test set 개봉 기록

- (아직 개봉하지 않음)
