"""Baseline 2 — TF-IDF(문자 n-gram) + Logistic Regression 위험도 분류기.

- 문자 2~4그램: 형태소 분석기 없이 한국어 어미 변형에 견디게 하는 표준 선택
- class_weight=balanced: danger Recall 우선 목표에 맞춰 소수 클래스 가중
- 학습은 train, 평가는 val (test는 3주차 말 최종 비교에서 1회만 사용)

사용법: python ml/scripts/baseline2_tfidf.py
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

from eval_utils import load_split, report


def main():
    train_x, train_y, _ = load_split("train")
    val_x, val_y, _ = load_split("val")

    model = make_pipeline(
        TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), min_df=2),
        LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42),
    )
    model.fit(train_x, train_y)

    report("Baseline 2 (TF-IDF+LR) — train", train_y, model.predict(train_x))
    report("Baseline 2 (TF-IDF+LR) — val", val_y, model.predict(val_x))


if __name__ == "__main__":
    main()
