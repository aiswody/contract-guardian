"""dataset v1 병합 — train 시드 + 검수 확정 증강문을 학습용 데이터셋으로 만든다.

- train = processed/train_seed.csv (confirmed만) + augmented/aug_clauses.csv (confirmed만)
- val / test = 시드 원본만 그대로 복사 (증강 미포함 — 평가 오염 방지, 스펙 §5.2)
- 출력: ml/data/processed/dataset_v1/{train,val,test}.csv
  컬럼: uid, text, category, risk_level, source_type(seed|augmented), origin_id

사용법: python ml/scripts/build_dataset.py
"""
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROC = ROOT / "ml" / "data" / "processed"
AUG_CSV = ROOT / "ml" / "data" / "augmented" / "aug_clauses.csv"
OUT = PROC / "dataset_v1"

FIELDS = ["uid", "text", "category", "risk_level", "source_type", "origin_id"]
RISKS = ["safe", "caution", "danger"]


def load(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def to_row(uid, r, source_type, origin_id):
    return {"uid": uid, "text": r["text"], "category": r["category"],
            "risk_level": r["risk_level"], "source_type": source_type, "origin_id": origin_id}


def write(name, rows):
    with open(OUT / name, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    dist = Counter(r["risk_level"] for r in rows)
    print(f"{name[:-4]:>5}: {len(rows):>4}문장  " +
          " / ".join(f"{k} {dist[k]}" for k in RISKS))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    uid = 0
    splits = {}

    for split in ("train", "val", "test"):
        rows = []
        excluded = []
        for r in load(PROC / f"{split}_seed.csv"):
            if r["label_status"] != "confirmed":
                excluded.append(r["id"])
                continue
            uid += 1
            rows.append(to_row(uid, r, "seed", r["id"]))
        if excluded:
            print(f"[제외] {split} 시드 미확정 {len(excluded)}건: id {', '.join(excluded)} — 확정 후 재빌드 시 포함")
        splits[split] = rows

    aug_excluded = 0
    for a in load(AUG_CSV):
        if a["review_status"] != "confirmed":
            aug_excluded += 1
            continue
        uid += 1
        splits["train"].append(to_row(uid, a, "augmented", a["aug_id"]))
    if aug_excluded:
        print(f"[제외] 증강 미확정 {aug_excluded}건")

    for split in ("train", "val", "test"):
        write(f"{split}.csv", splits[split])

    total = sum(len(v) for v in splits.values())
    print(f"dataset v1 완성: 총 {total}문장 -> {OUT}")


if __name__ == "__main__":
    main()
