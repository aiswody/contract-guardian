"""추론 파이프라인 — 위험도(v2) + 카테고리 모델 로드, threshold 정책 적용.

설계 원칙 (스펙 §2·§9):
- 판별은 학습 모델만 한다. LLM은 여기 관여하지 않는다.
- confidence < THRESHOLD 인 위험도 판정은 `uncertain`으로 강등 — 모르는 것을
  아는 척하지 않는다. 원 판정과 확신도는 함께 반환해 UI가 맥락을 보여줄 수 있게 한다.
"""
import os
from pathlib import Path

import torch
import torch.nn.functional as F
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from .patterns import find_signals

MODEL_DIR = Path(os.environ.get("MODEL_DIR", Path(__file__).resolve().parents[1] / "models"))
RISK_MODEL = MODEL_DIR / "risk_model_v2" / "best"
CATEGORY_MODEL = MODEL_DIR / "category_model" / "best"
THRESHOLD = float(os.environ.get("RISK_THRESHOLD", "0.7"))  # 3주차 튜닝 결과
MODEL_VERSION = "risk_v2+cat_v1 (2026-07-12, dataset v1)"


class _Classifier:
    def __init__(self, model_dir: Path):
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_dir)
        self.model.eval()

    @torch.no_grad()
    def predict(self, texts: list[str], batch_size: int = 16):
        results = []
        for i in range(0, len(texts), batch_size):
            enc = self.tokenizer(texts[i:i + batch_size], truncation=True, max_length=128,
                                 padding=True, return_tensors="pt")
            probs = F.softmax(self.model(**enc).logits, dim=-1)
            conf, idx = probs.max(dim=-1)
            results += [(self.model.config.id2label[int(j)], float(c))
                        for j, c in zip(idx, conf)]
        return results


class Pipeline:
    def __init__(self):
        self.risk = _Classifier(RISK_MODEL)
        self.category = _Classifier(CATEGORY_MODEL)

    def analyze_clauses(self, clauses: list[str]) -> list[dict]:
        risk_preds = self.risk.predict(clauses)
        cat_preds = self.category.predict(clauses)
        out = []
        for i, (text, (risk, conf), (cat, _)) in enumerate(zip(clauses, risk_preds, cat_preds)):
            uncertain = conf < THRESHOLD
            signals = find_signals(text)
            out.append({
                "order_index": i,
                "text": text,
                "category": cat,
                "risk_level": "uncertain" if uncertain else risk,
                "model_risk": risk,           # threshold 적용 전 원 판정
                "confidence": round(conf, 3),
                "reason": " / ".join(signals) if signals else None,
            })
        return out
