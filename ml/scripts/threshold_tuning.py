"""confidence threshold 튜닝 — `확인 필요(uncertain)` 판정선 결정.

스펙 §4.3·§9: confidence가 임계값 미만이면 판정을 단정하지 않고 `확인 필요`로 표시.
핵심 트레이드오프:
- threshold ↑ → uncertain 비율 ↑ (사용자가 직접 확인할 항목 증가, UX 비용)
- threshold ↑ → **유효 danger 놓침** ↓ (위험인데 확신 있게 비danger로 판정하는 최악 사례 감소)

유효 danger 놓침 = 정답 danger를 threshold 이상의 확신으로 safe/caution 판정한 비율.
(uncertain으로 빠진 danger는 사용자에게 "확인 필요"로 노출되므로 놓침이 아님)

사용법: python ml/scripts/threshold_tuning.py [--risk-dir risk_model_v2]
"""
import argparse

from eval_roberta import MODELS, predict
from eval_utils import load_split


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--risk-dir", default="risk_model_v2")
    ap.add_argument("--split", default="val")
    args = ap.parse_args()

    texts, y_true, _ = load_split(args.split)
    y_pred, conf = predict(MODELS / args.risk_dir / "best", texts)

    n = len(y_true)
    n_danger = sum(1 for t in y_true if t == "danger")
    print(f"{args.split} {n}문장 (danger {n_danger}건) — threshold별 트레이드오프\n")
    print(f"{'threshold':>9} | {'uncertain':>9} | {'커버리지':>7} | {'유효 danger 놓침':>14}")
    for t in [0.0, 0.5, 0.6, 0.7, 0.8, 0.9]:
        uncertain = sum(1 for c in conf if c < t)
        missed = sum(1 for yt, yp, c in zip(y_true, y_pred, conf)
                     if yt == "danger" and yp != "danger" and c >= t)
        print(f"{t:>9.2f} | {uncertain:>6}건 | {1 - uncertain / n:>6.0%} | "
              f"{missed}건 / {n_danger} ({missed / n_danger:.0%})")


if __name__ == "__main__":
    main()
