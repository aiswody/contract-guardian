"""시드 커버리지 집계 — risk-pattern-matrix.md 트래커의 자동화 버전.

카테고리 x 위험도 매트릭스, 위험도 비율, 라벨 상태별 건수를 출력한다.
사용법: python ml/scripts/coverage.py
"""
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEED_CSV = ROOT / "ml" / "data" / "seed" / "seed_clauses.csv"

CATEGORIES = ["deposit_return", "repair_defect", "restoration",
              "termination_renewal", "lien_rights", "fees_utilities", "etc"]
RISKS = ["safe", "caution", "danger"]
MIN_PER_CELL = 10


def main():
    with open(SEED_CSV, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    cell = Counter((r["category"], r["risk_level"]) for r in rows)
    status = Counter(r["label_status"] for r in rows)

    bad = [r["id"] for r in rows
           if r["category"] not in CATEGORIES or r["risk_level"] not in RISKS]
    if bad:
        print(f"[경고] 유효하지 않은 카테고리/위험도: id {', '.join(bad)}")

    header = f"{'카테고리':<22}" + "".join(f"{r:>9}" for r in RISKS) + f"{'소계':>7}"
    print(header)
    print("-" * len(header))
    under = []
    for c in CATEGORIES:
        counts = [cell[(c, r)] for r in RISKS]
        print(f"{c:<22}" + "".join(f"{n:>9}" for n in counts) + f"{sum(counts):>7}")
        under += [f"{c}×{r}({n})" for r, n in zip(RISKS, counts) if n < MIN_PER_CELL]

    totals = [sum(cell[(c, r)] for c in CATEGORIES) for r in RISKS]
    total = sum(totals)
    print("-" * len(header))
    print(f"{'합계':<22}" + "".join(f"{n:>9}" for n in totals) + f"{total:>7}")
    print(f"\n위험도 비율: " + " / ".join(f"{r} {n / total:.0%}" for r, n in zip(RISKS, totals)))
    print(f"라벨 상태: " + ", ".join(f"{k} {v}" for k, v in sorted(status.items())))
    print(f"\n칸별 최소 {MIN_PER_CELL} 미달: {', '.join(under) if under else '없음 — 전 칸 달성'}")


if __name__ == "__main__":
    main()
