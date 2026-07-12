"""자기 일치도 검증용 파일럿 시트 생성.

seed_clauses.csv에서 50문장을 무작위 추출해 라벨을 가린 시트 2장을 만든다.
- pilot_round1.csv / pilot_round2.csv : 라벨러가 각각 1회차, 2회차(3일+ 시차)에 작성
- pilot_mapping.csv : pilot_no -> seed_id 매핑 (검증 전에는 열어보지 않는다)

고정 시드(42)로 추출하므로 재실행해도 같은 표본이 나온다.
사용법: python ml/scripts/make_pilot.py
"""
import csv
import random
from pathlib import Path

SEED = 42
SAMPLE_SIZE = 50
ROOT = Path(__file__).resolve().parents[2]
SEED_CSV = ROOT / "ml" / "data" / "seed" / "seed_clauses.csv"
PILOT_DIR = ROOT / "ml" / "data" / "pilot"


def main():
    with open(SEED_CSV, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if len(rows) < SAMPLE_SIZE:
        raise SystemExit(f"시드가 {len(rows)}문장뿐이라 {SAMPLE_SIZE}문장을 추출할 수 없습니다.")

    rng = random.Random(SEED)
    sample = rng.sample(rows, SAMPLE_SIZE)
    rng.shuffle(sample)  # 출처·카테고리 순서가 힌트가 되지 않도록 섞는다

    PILOT_DIR.mkdir(parents=True, exist_ok=True)

    for round_name in ("pilot_round1.csv", "pilot_round2.csv"):
        with open(PILOT_DIR / round_name, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["pilot_no", "text", "category", "risk_level", "memo"])
            for i, row in enumerate(sample, 1):
                w.writerow([i, row["text"], "", "", ""])

    with open(PILOT_DIR / "pilot_mapping.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pilot_no", "seed_id"])
        for i, row in enumerate(sample, 1):
            w.writerow([i, row["id"]])

    print(f"{SAMPLE_SIZE}문장 추출 완료 -> {PILOT_DIR}")
    print("1회차: pilot_round1.csv를 지금 작성")
    print("2회차: 최소 3일 후 pilot_round2.csv를 1회차를 보지 않고 작성")
    print("비교:  python ml/scripts/pilot_agreement.py")


if __name__ == "__main__":
    main()
