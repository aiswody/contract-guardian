# 3주차 모델 결과 리포트

> 모든 수치는 `ml/scripts/eval_utils.py` 기준 (Macro-F1 + danger Recall).
> **개발 중 평가는 val(34문장)만 사용.** test(34문장)는 3주차 말 최종 비교에서 1회만 개봉.
> val이 작아(클래스당 9~14건) 수치의 신뢰구간이 넓다는 점을 감안할 것 (2주차 기록 참조).

## 위험도 3-class — val 결과

| 모델 | Macro-F1 | danger Recall | 비고 |
|---|---|---|---|
| Baseline 1 — 키워드 규칙 | 0.537 | 0.455 | danger precision 1.000 (규칙에 걸리면 확실하나 절반을 놓침) |
| Baseline 2 — TF-IDF + LR | 0.530 | 0.545 | train 0.992 → val 0.530, 심한 과적합 |
| KLUE-RoBERTa-base | (학습 예정) | (학습 예정) | Colab 노트북 `train_klue_roberta.ipynb` |

### 해석

- 규칙 기반(B1)은 danger precision 1.0 — 유형표의 대표 패턴이 정확하다는 방증.
  그러나 표현이 조금만 변형돼도 놓친다 (Recall 0.455). "패턴 사전으로는 재현율을
  못 채운다"가 파인튜닝의 존재 이유.
- TF-IDF(B2)는 train을 통째로 외웠지만 val(증강 없는 시드 원본)에서 무너짐 —
  표면 n-gram이 아니라 의미 이해가 필요하다는 근거.
- val 34문장 기준 오차가 크므로, baseline 간 우열(0.537 vs 0.530)은 유의미한
  차이로 해석하지 않는다.

## 카테고리 7-class

파인튜닝 모델(A')에서만 학습·평가 예정. baseline은 위험도만 다룬다 (스펙 §5.3 표).

## test set 개봉 기록

- (아직 개봉하지 않음)
