"""test set 최종 평가 — 단 1회 실행 (2026-07-12 개봉).

봉인 원칙: 이 스크립트 실행 이후 모델·threshold를 수정하면 여기서 얻은 수치는 무효.
세 모델(규칙 / TF-IDF+LR / KLUE-RoBERTa v2)을 동일 test 34문장으로 비교한다.

사용법: python ml/scripts/final_test_eval.py
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

from baseline1_rules import classify
from eval_roberta import CATEGORIES, MODELS, predict
from eval_utils import load_split, report


def main():
    train_x, train_y, _ = load_split("train")
    texts, y_true, rows = load_split("test")

    # Baseline 1 — 규칙
    report("test | Baseline 1 (규칙)", y_true, [classify(t) for t in texts])

    # Baseline 2 — TF-IDF + LR (train으로 학습)
    b2 = make_pipeline(
        TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), min_df=2),
        LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42))
    b2.fit(train_x, train_y)
    report("test | Baseline 2 (TF-IDF+LR)", y_true, b2.predict(texts))

    # Main — KLUE-RoBERTa v2 (위험도) + v1 (카테고리)
    risk_pred, risk_conf = predict(MODELS / "risk_model_v2" / "best", texts)
    report("test | KLUE-RoBERTa v2 위험도", y_true, risk_pred)
    uncertain = sum(c < 0.7 for c in risk_conf)
    missed = sum(1 for t, p, c in zip(y_true, risk_pred, risk_conf)
                 if t == "danger" and p != "danger" and c >= 0.7)
    n_danger = sum(1 for t in y_true if t == "danger")
    print(f"threshold 0.7 적용 시: uncertain {uncertain}건, "
          f"유효 danger 놓침 {missed}/{n_danger}")

    cat_true = [r["category"] for r in rows]
    cat_pred, _ = predict(MODELS / "category_model" / "best", texts)
    report("test | KLUE-RoBERTa 카테고리", cat_true, cat_pred, labels=CATEGORIES)


if __name__ == "__main__":
    main()
