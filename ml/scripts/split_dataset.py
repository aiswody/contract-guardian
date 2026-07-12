"""시드 train/val/test 분할 — 층화(카테고리 x 위험도 21칸) 70/15/15.

증강(Step 3)보다 분할을 먼저 수행한다: val/test 시드의 패러프레이즈가
train에 섞이는 평가 오염을 원천 차단하기 위함 (스펙 §5.2의 "증강은 train에만,
val/test는 시드 원본만" 원칙의 안전한 구현 순서).

- 고정 시드(42)로 재현 가능. 칸별로 largest remainder 방식으로 val/test 수를
  배분해 전체 비율을 15%에 정확히 맞춘다.
- 출력: ml/data/processed/{train,val,test}_seed.csv (시드 스키마 + split 컬럼 없음)

사용법: python ml/scripts/split_dataset.py
"""
import csv
import random
from collections import defaultdict
from pathlib import Path

SEED = 42
VAL_RATIO = TEST_RATIO = 0.15
ROOT = Path(__file__).resolve().parents[2]
SEED_CSV = ROOT / "ml" / "data" / "seed" / "seed_clauses.csv"
OUT_DIR = ROOT / "ml" / "data" / "processed"


def allocate(cells, total_rows, ratio):
    """칸별 배분 수를 largest remainder 방식으로 계산."""
    target = round(total_rows * ratio)
    quotas = {k: len(v) * ratio for k, v in cells.items()}
    alloc = {k: int(q) for k, q in quotas.items()}
    remainder_order = sorted(cells, key=lambda k: quotas[k] - alloc[k], reverse=True)
    i = 0
    while sum(alloc.values()) < target:
        alloc[remainder_order[i % len(remainder_order)]] += 1
        i += 1
    return alloc


def main():
    with open(SEED_CSV, encoding="utf-8") as f:
        fieldnames = csv.DictReader(f).fieldnames
    with open(SEED_CSV, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    not_confirmed = [r["id"] for r in rows if r["label_status"] != "confirmed"]
    if not_confirmed:
        print(f"[경고] confirmed 아닌 행 포함: id {', '.join(not_confirmed)}")

    cells = defaultdict(list)
    for r in rows:
        cells[(r["category"], r["risk_level"])].append(r)

    rng = random.Random(SEED)
    for v in cells.values():
        rng.shuffle(v)

    val_alloc = allocate(cells, len(rows), VAL_RATIO)
    test_alloc = allocate(cells, len(rows), TEST_RATIO)

    splits = {"train": [], "val": [], "test": []}
    for key, members in cells.items():
        n_test, n_val = test_alloc[key], val_alloc[key]
        splits["test"] += members[:n_test]
        splits["val"] += members[n_test:n_test + n_val]
        splits["train"] += members[n_test + n_val:]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, members in splits.items():
        members.sort(key=lambda r: int(r["id"]))
        with open(OUT_DIR / f"{name}_seed.csv", "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(members)
        print(f"{name}: {len(members)}문장 ({len(members) / len(rows):.1%})")

    print(f"총 {len(rows)}문장 분할 완료 -> {OUT_DIR}")


if __name__ == "__main__":
    main()
