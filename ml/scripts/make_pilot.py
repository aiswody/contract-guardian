"""자기 일치도 검증용 파일럿 시트 생성.

seed_clauses.csv에서 50문장을 무작위 추출해 라벨을 가린 시트 2장을 만든다.
- {prefix}_round1.csv / {prefix}_round2.csv : 라벨러가 1회차, 2회차에 작성
  (2회차 시트는 순서를 다르게 셔플 — 당일 재검증 시 위치 기억 효과 완화)
- {prefix}_mapping.csv : pilot_no -> seed_id 매핑 (검증 전에는 열어보지 않는다)

고정 시드로 추출하므로 같은 인자로 재실행하면 같은 표본이 나온다.

사용법:
  python ml/scripts/make_pilot.py                          # 1차 파일럿 (prefix=pilot, seed=42)
  python ml/scripts/make_pilot.py --prefix pilot2 --seed 43 \
      --exclude ml/data/pilot/pilot_mapping.csv            # 2차: 1차 표본 제외
"""
import argparse
import csv
import random
from pathlib import Path

SAMPLE_SIZE = 50
ROOT = Path(__file__).resolve().parents[2]
SEED_CSV = ROOT / "ml" / "data" / "seed" / "seed_clauses.csv"
PILOT_DIR = ROOT / "ml" / "data" / "pilot"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", default="pilot")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--exclude", action="append", default=[],
                    help="제외할 이전 파일럿의 mapping.csv 경로 (복수 지정 가능)")
    args = ap.parse_args()

    with open(SEED_CSV, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    excluded = set()
    for path in args.exclude:
        with open(ROOT / path, encoding="utf-8") as f:
            excluded |= {r["seed_id"] for r in csv.DictReader(f)}

    pool = [r for r in rows if r["id"] not in excluded]
    if len(pool) < SAMPLE_SIZE:
        raise SystemExit(f"제외 후 남은 시드가 {len(pool)}문장이라 {SAMPLE_SIZE}문장을 추출할 수 없습니다.")

    rng = random.Random(args.seed)
    sample = rng.sample(pool, SAMPLE_SIZE)
    rng.shuffle(sample)

    PILOT_DIR.mkdir(parents=True, exist_ok=True)
    numbered = list(enumerate(sample, 1))

    round2_order = numbered[:]
    rng.shuffle(round2_order)  # 2회차는 다른 순서

    for name, order in ((f"{args.prefix}_round1.csv", numbered),
                        (f"{args.prefix}_round2.csv", round2_order)):
        with open(PILOT_DIR / name, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["pilot_no", "text", "category", "risk_level", "memo"])
            for i, row in order:
                w.writerow([i, row["text"], "", "", ""])

    with open(PILOT_DIR / f"{args.prefix}_mapping.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pilot_no", "seed_id"])
        for i, row in numbered:
            w.writerow([i, row["id"]])

    print(f"{SAMPLE_SIZE} sentences -> {PILOT_DIR} (prefix={args.prefix}, excluded={len(excluded)})")


if __name__ == "__main__":
    main()
