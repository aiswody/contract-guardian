"""파인튜닝된 KLUE-RoBERTa 로컬 평가 (CPU).

- 위험도 모델: val 기준 Macro-F1 / danger Recall / 혼동행렬 (eval_utils 공통 기준)
- 카테고리 모델: val 기준 Macro-F1
- confidence(softmax 최댓값) 분포도 함께 출력 — threshold(`확인 필요`) 튜닝 재료

사용법: python ml/scripts/eval_roberta.py [--split val]
"""
import argparse
from pathlib import Path

import torch
import torch.nn.functional as F
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from eval_utils import ROOT, load_split, report

MODELS = ROOT / "model-server" / "models"
CATEGORIES = ["deposit_return", "repair_defect", "restoration",
              "termination_renewal", "lien_rights", "fees_utilities", "etc"]


@torch.no_grad()
def predict(model_dir: Path, texts, batch_size=32):
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForSequenceClassification.from_pretrained(model_dir)
    model.eval()
    preds, confs = [], []
    for i in range(0, len(texts), batch_size):
        batch = tokenizer(texts[i:i + batch_size], truncation=True, max_length=128,
                          padding=True, return_tensors="pt")
        probs = F.softmax(model(**batch).logits, dim=-1)
        conf, idx = probs.max(dim=-1)
        preds += [model.config.id2label[int(j)] for j in idx]
        confs += conf.tolist()
    return preds, confs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="val")
    args = ap.parse_args()

    texts, risk_true, rows = load_split(args.split)

    risk_pred, risk_conf = predict(MODELS / "risk_model" / "best", texts)
    report(f"KLUE-RoBERTa 위험도 — {args.split}", risk_true, risk_pred)
    wrong_high = sum(1 for t, p, c in zip(risk_true, risk_pred, risk_conf) if t != p and c >= 0.9)
    print(f"confidence: 평균 {sum(risk_conf) / len(risk_conf):.3f}, "
          f"0.7 미만 {sum(c < 0.7 for c in risk_conf)}건, 오답인데 0.9 이상 {wrong_high}건")
    print("\n[오분류 상세]")
    for t, p, c, r in zip(risk_true, risk_pred, risk_conf, rows):
        if t != p:
            print(f"  정답 {t} / 예측 {p} (conf {c:.2f}) — {r['text'][:50]}")

    cat_true = [r["category"] for r in rows]
    cat_pred, _ = predict(MODELS / "category_model" / "best", texts)
    report(f"KLUE-RoBERTa 카테고리 — {args.split}", cat_true, cat_pred, labels=CATEGORIES)


if __name__ == "__main__":
    main()
