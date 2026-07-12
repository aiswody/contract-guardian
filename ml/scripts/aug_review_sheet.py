"""증강 검수용 대조 뷰 생성 — 원문(시드)과 변형문을 나란히 표시.

aug_clauses.csv의 미검수(provisional) 행만 골라 원문과 짝지은
Markdown 파일을 만든다. 검수 자체는 aug_clauses.csv에서 한다
(이 파일은 읽기용 파생물 — git에 커밋하지 않음).

사용법: python ml/scripts/aug_review_sheet.py
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUG_CSV = ROOT / "ml" / "data" / "augmented" / "aug_clauses.csv"
SEED_CSV = ROOT / "ml" / "data" / "seed" / "seed_clauses.csv"
OUT = ROOT / "ml" / "data" / "augmented" / "review_view.md"


def main():
    with open(SEED_CSV, encoding="utf-8") as f:
        seed = {r["id"]: r for r in csv.DictReader(f)}
    with open(AUG_CSV, encoding="utf-8") as f:
        augs = [a for a in csv.DictReader(f) if a["review_status"] == "provisional"]

    lines = [
        "# 증강 검수 대조 뷰 (자동 생성 — 검수는 aug_clauses.csv에서)",
        "",
        f"미검수 {len(augs)}건. 확인 포인트: ① 의미 보존 ② 위험도 보존(금액·기한·범위 변화 없음) ③ 자연스러움",
        "",
    ]
    for a in augs:
        s = seed[a["seed_id"]]
        lines += [
            f"## {a['aug_id']} (seed {a['seed_id']} · {a['category']} · {a['risk_level']} · {a['method']})",
            f"- 원문: {s['text']}",
            f"- 변형: {a['text']}",
            "",
        ]

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"{len(augs)}건 -> {OUT}")


if __name__ == "__main__":
    main()
