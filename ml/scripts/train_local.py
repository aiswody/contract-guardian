"""위험도 3-class 로컬 재학습 (CPU 가능).

1차 Colab 학습의 문제(34문장 val 기준 macro-F1 단독으로 best 선택 → 과소학습
체크포인트 채택)를 보완한 설정:
- 에폭 8 (기존 5)
- best 선택: danger Recall과 Macro-F1의 평균 점수 — FN 최소화 원칙의 학습 단계 적용
- danger 가중 손실 (safe/caution 1.0, danger 1.5) — 위험을 놓치는 비용을 손실에 반영

출력: model-server/models/risk_model_v2/best
사용법: python ml/scripts/train_local.py
"""
import numpy as np
import torch
from sklearn.metrics import f1_score, recall_score
from transformers import (AutoModelForSequenceClassification, AutoTokenizer,
                          Trainer, TrainingArguments)
from datasets import Dataset

from eval_utils import ROOT, load_split

MODEL_NAME = "klue/roberta-base"
LABELS = ["safe", "caution", "danger"]
LABEL2ID = {l: i for i, l in enumerate(LABELS)}
OUT = ROOT / "model-server" / "models" / "risk_model_v2"
CLASS_WEIGHTS = torch.tensor([1.0, 1.0, 1.5])  # danger FN 비용 반영


class WeightedTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        loss = torch.nn.functional.cross_entropy(
            outputs.logits, labels, weight=CLASS_WEIGHTS.to(outputs.logits.device))
        return (loss, outputs) if return_outputs else loss


def make_dataset(split, tokenizer):
    texts, labels, _ = load_split(split)
    ds = Dataset.from_dict({"text": texts, "labels": [LABEL2ID[l] for l in labels]})
    return ds.map(lambda x: tokenizer(x["text"], truncation=True, max_length=128))


def compute_metrics(eval_pred):
    logits, y = eval_pred
    pred = logits.argmax(-1)
    macro = f1_score(y, pred, average="macro", zero_division=0)
    d = LABEL2ID["danger"]
    danger_rec = recall_score(np.array(y) == d, pred == d, zero_division=0)
    return {"macro_f1": macro, "danger_recall": danger_rec,
            "score": (macro + danger_rec) / 2}


def main():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    train_ds = make_dataset("train", tokenizer)
    val_ds = make_dataset("val", tokenizer)

    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME, num_labels=3,
        label2id=LABEL2ID, id2label={i: l for l, i in LABEL2ID.items()})

    args = TrainingArguments(
        output_dir=str(OUT), seed=42,
        num_train_epochs=8, learning_rate=2e-5,
        per_device_train_batch_size=16, per_device_eval_batch_size=64,
        warmup_ratio=0.1, weight_decay=0.01,
        eval_strategy="epoch", save_strategy="epoch", save_total_limit=2,
        load_best_model_at_end=True, metric_for_best_model="score",
        logging_steps=20, report_to="none")

    trainer = WeightedTrainer(model=model, args=args, train_dataset=train_ds,
                              eval_dataset=val_ds, compute_metrics=compute_metrics,
                              processing_class=tokenizer)
    trainer.train()
    trainer.save_model(str(OUT / "best"))
    tokenizer.save_pretrained(str(OUT / "best"))
    print("저장 완료:", OUT / "best")
    print("val 최종:", trainer.evaluate())


if __name__ == "__main__":
    main()
