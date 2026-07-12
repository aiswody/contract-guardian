"""증강 데이터 무결성 검증.

- 모든 aug 행의 seed_id가 train_seed.csv에 존재하는가 (val/test 오염 차단)
- category / risk_level이 원본 시드와 일치하는가 (라벨 상속 검증)
- aug_id 중복 여부, 검수 상태 집계

사용법: python ml/scripts/validate_aug.py
"""
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUG_CSV = ROOT / "ml" / "data" / "augmented" / "aug_clauses.csv"
TRAIN_CSV = ROOT / "ml" / "data" / "processed" / "train_seed.csv"


def main():
    with open(TRAIN_CSV, encoding="utf-8") as f:
        train = {r["id"]: r for r in csv.DictReader(f)}
    with open(AUG_CSV, encoding="utf-8") as f:
        augs = list(csv.DictReader(f))

    errors = []
    dup = [k for k, v in Counter(a["aug_id"] for a in augs).items() if v > 1]
    if dup:
        errors.append(f"aug_id 중복: {', '.join(dup)}")

    for a in augs:
        sid = a["seed_id"]
        if sid not in train:
            errors.append(f"{a['aug_id']}: seed {sid}가 train에 없음 — 평가 오염 위험!")
            continue
        for field in ("category", "risk_level"):
            if a[field] != train[sid][field]:
                errors.append(f"{a['aug_id']}: {field} 불일치 (aug={a[field]}, seed={train[sid][field]})")

    status = Counter(a["review_status"] for a in augs)
    per_seed = Counter(a["seed_id"] for a in augs)
    print(f"증강 {len(augs)}문장 / 원본 시드 {len(per_seed)}종 / train 대비 배율 {len(augs) / len(train):.2f}x")
    print(f"검수 상태: {dict(status)}")
    if errors:
        print(f"\n[오류 {len(errors)}건]")
        for e in errors:
            print(" -", e)
        raise SystemExit(1)
    print("무결성 검증 통과 — train 외 시드 참조 없음, 라벨 상속 일치")


if __name__ == "__main__":
    main()
