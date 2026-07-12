"""하이브리드 평가 — 규칙(danger 한정) 백스톱 + 파인튜닝 모델.

동기: v2 모델이 놓친 danger는 train에 유사 패턴이 없는 문장들로, confidence가
높아 threshold로 구제 불가. 반면 규칙 baseline의 danger 판정 precision은 1.0
(train·val 공통) — 규칙에 걸리면 확실히 위험하다.

정책: Baseline1의 DANGER 패턴에 걸리면 danger로 상향(override), 아니면 모델 판정.
danger 방향으로만 개입하므로 FN은 줄고 FP만 소폭 늘 수 있음 — FN 최소화 원칙에 부합.

사용법: python ml/scripts/hybrid_eval.py [--risk-dir risk_model_v2] [--split val]
"""
import argparse
import re

from baseline1_rules import DANGER
from eval_roberta import MODELS, predict
from eval_utils import load_split, report


def rule_danger(text):
    return any(re.search(p, text) for p in DANGER)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--risk-dir", default="risk_model_v2")
    ap.add_argument("--split", default="val")
    args = ap.parse_args()

    texts, y_true, _ = load_split(args.split)
    model_pred, _ = predict(MODELS / args.risk_dir / "best", texts)

    hybrid_pred = ["danger" if rule_danger(t) else p for t, p in zip(texts, model_pred)]
    overridden = sum(1 for m, h in zip(model_pred, hybrid_pred) if m != h)

    report(f"모델 단독 — {args.split}", y_true, model_pred)
    report(f"하이브리드 (규칙 danger 백스톱) — {args.split}", y_true, hybrid_pred)
    print(f"\n규칙 개입(비danger→danger 상향): {overridden}건")


if __name__ == "__main__":
    main()
