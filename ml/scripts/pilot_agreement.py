"""파일럿 1·2회차 라벨의 자기 일치도 계산.

위험도·카테고리 각각의 일치율을 출력하고, 불일치 문장을 나열한다.
잠정 라벨(seed_clauses.csv)과의 비교도 함께 출력한다 — 수집 시점 판단과
가이드라인 기반 판단이 어긋난 지점을 찾기 위함.

합격선(가이드라인 §6): 위험도 일치율 90% 이상.
사용법: python ml/scripts/pilot_agreement.py
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PILOT_DIR = ROOT / "ml" / "data" / "pilot"
SEED_CSV = ROOT / "ml" / "data" / "seed" / "seed_clauses.csv"


def load(path, key="pilot_no"):
    with open(path, encoding="utf-8") as f:
        return {row[key]: row for row in csv.DictReader(f)}


def agreement(r1, r2, field):
    keys = [k for k in r1 if r1[k][field].strip() and r2[k][field].strip()]
    if not keys:
        return None, []
    diffs = [k for k in keys if r1[k][field].strip() != r2[k][field].strip()]
    return 1 - len(diffs) / len(keys), diffs


def main():
    r1 = load(PILOT_DIR / "pilot_round1.csv")
    r2 = load(PILOT_DIR / "pilot_round2.csv")
    mapping = load(PILOT_DIR / "pilot_mapping.csv")
    seed = load(SEED_CSV, key="id")

    for field, label in (("risk_level", "위험도"), ("category", "카테고리")):
        rate, diffs = agreement(r1, r2, field)
        if rate is None:
            print(f"[{label}] 두 회차 모두 채워진 문장이 없습니다 — 시트를 먼저 작성하세요.")
            continue
        n = sum(1 for k in r1 if r1[k][field].strip() and r2[k][field].strip())
        print(f"\n[{label}] 자기 일치율: {rate:.1%} ({n - len(diffs)}/{n})")
        if field == "risk_level":
            print("  ->", "합격 (90% 이상)" if rate >= 0.9 else "불합격 — 불일치 문장을 가이드라인 §5에 수록하고 기준 보완 후 재검증")
        for k in diffs:
            sid = mapping[k]["seed_id"]
            prov = seed[sid][field]
            print(f"  - pilot {k} (seed {sid}): 1회차={r1[k][field]} / 2회차={r2[k][field]} / 잠정={prov}")
            print(f"    {r1[k]['text'][:60]}...")

    # 잠정 라벨과의 비교 (1회차 기준)
    filled = [k for k in r1 if r1[k]["risk_level"].strip()]
    if filled:
        diffs_prov = [
            k for k in filled
            if r1[k]["risk_level"].strip() != seed[mapping[k]["seed_id"]]["risk_level"]
        ]
        rate = 1 - len(diffs_prov) / len(filled)
        print(f"\n[참고] 1회차 vs 수집 시점 잠정 라벨 (위험도): {rate:.1%}")
        for k in diffs_prov:
            sid = mapping[k]["seed_id"]
            print(f"  - pilot {k} (seed {sid}): 1회차={r1[k]['risk_level']} / 잠정={seed[sid]['risk_level']}")


if __name__ == "__main__":
    main()
