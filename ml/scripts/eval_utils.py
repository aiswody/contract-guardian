"""공용 평가 유틸 — 모든 모델(규칙/TF-IDF/RoBERTa)이 동일 기준으로 비교되도록 한다.

핵심 지표 우선순위 (스펙 §5.3):
1. danger Recall — 위험 조항을 놓치는 False Negative가 최악의 오류
2. Macro-F1 — 클래스 불균형 하의 전반 성능
"""
import csv
from pathlib import Path

from sklearn.metrics import classification_report, confusion_matrix, f1_score, recall_score

ROOT = Path(__file__).resolve().parents[2]
DATASET = ROOT / "ml" / "data" / "processed" / "dataset_v1"
RISKS = ["safe", "caution", "danger"]


def load_split(name):
    """dataset_v1의 한 split을 (texts, risk_labels, rows)로 로드."""
    with open(DATASET / f"{name}.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return [r["text"] for r in rows], [r["risk_level"] for r in rows], rows


def report(name, y_true, y_pred, labels=RISKS):
    """지표 출력 + (macro_f1, danger_recall) 반환."""
    macro = f1_score(y_true, y_pred, labels=labels, average="macro", zero_division=0)
    danger_rec = recall_score(y_true, y_pred, labels=["danger"], average="macro", zero_division=0)
    print(f"\n===== {name} =====")
    print(f"Macro-F1: {macro:.3f} | danger Recall: {danger_rec:.3f}")
    print(classification_report(y_true, y_pred, labels=labels, digits=3, zero_division=0))
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    print("혼동행렬 (행=정답, 열=예측) [" + ", ".join(labels) + "]")
    for lab, row in zip(labels, cm):
        print(f"  {lab:>8}: {row}")
    fn = cm[labels.index("danger")][: labels.index("danger")].sum() if "danger" in labels else 0
    if fn:
        print(f"  ** danger -> 비danger 오분류(FN) {fn}건 — 최우선 감소 대상")
    return macro, danger_rec
