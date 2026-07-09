"""
evaluation/gold_eval.py — Gold Set evaluation for the Interview IQ NLI model.

Phase 5 (see PROJECT_EXECUTION_PLAN.md). Runs inference over the 48-pair
DS-014 Gold Set (evaluation-only, per D28 — see FILE_PLACEMENT.md and
nli/dataset.load_gold_set, reused here unmodified) and computes the
pre-registered metrics:

  - per-class precision / recall / F1 (entailment, neutral, contradiction)
  - the full 3x3 confusion matrix (raw counts)
  - the E->C and C->E cells explicitly (the Subject Blindness signature)
  - macro-F1

This module supports both arms of the comparison from the same code path:
zero-shot (base model only) and adapter (base model + LoRA checkpoint).
It does not pick or tune any threshold, and it does not render a verdict —
it reports the numbers; judging whether Subject Blindness is fixed is a
human call made by comparing the two reports side by side.

⚠️ RISK ACCEPTED (D33): Gate G1 (Stage-4 per-pair human review of the 150
pilot pairs) is closed by Ahmed's explicit accepted-risk decision, not by
completed review. Every result from this module is tagged RISK ACCEPTED.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

import torch
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    PreTrainedModel,
    PreTrainedTokenizerBase,
)
from peft import PeftModel

from interview_iq.config import Config
from interview_iq.nli.dataset import load_gold_set

logger = logging.getLogger(__name__)

LABEL_ORDER: tuple[str, ...] = ("entailment", "neutral", "contradiction")


# ── pure metric computation (no model involved — fully unit-testable) ───────


@dataclass(frozen=True)
class PredictionRecord:
    pair_id: str
    question_id: str
    gold_label: str
    predicted_label: str
    correct: bool


@dataclass
class GoldEvalReport:
    mode: str  # "zero-shot" or "adapter:<path>"
    n_pairs: int
    label_order: tuple[str, ...]
    confusion_matrix: dict[str, dict[str, int]]  # confusion_matrix[gold][predicted]
    per_class: dict[str, dict[str, float]]  # per_class[label] = {precision, recall, f1, support}
    macro_f1: float
    e_to_c_count: int
    e_to_c_rate: float  # e_to_c_count / support(entailment) — Subject Blindness signature
    c_to_e_count: int
    c_to_e_rate: float  # c_to_e_count / support(contradiction) — Subject Blindness signature
    predictions: list[PredictionRecord] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "n_pairs": self.n_pairs,
            "label_order": list(self.label_order),
            "confusion_matrix": self.confusion_matrix,
            "per_class": self.per_class,
            "macro_f1": self.macro_f1,
            "e_to_c_count": self.e_to_c_count,
            "e_to_c_rate": self.e_to_c_rate,
            "c_to_e_count": self.c_to_e_count,
            "c_to_e_rate": self.c_to_e_rate,
            "predictions": [
                {
                    "pair_id": p.pair_id,
                    "question_id": p.question_id,
                    "gold_label": p.gold_label,
                    "predicted_label": p.predicted_label,
                    "correct": p.correct,
                }
                for p in self.predictions
            ],
        }


def compute_confusion_matrix(
    gold_labels: Sequence[str], predicted_labels: Sequence[str], label_order: Sequence[str] = LABEL_ORDER
) -> dict[str, dict[str, int]]:
    cm = {g: {p: 0 for p in label_order} for g in label_order}
    for gold, pred in zip(gold_labels, predicted_labels):
        cm[gold][pred] += 1
    return cm


def compute_per_class_metrics(
    cm: dict[str, dict[str, int]], label_order: Sequence[str] = LABEL_ORDER
) -> dict[str, dict[str, float]]:
    result: dict[str, dict[str, float]] = {}
    for c in label_order:
        tp = cm[c][c]
        fp = sum(cm[r][c] for r in label_order if r != c)
        fn = sum(cm[c][r] for r in label_order if r != c)
        support = sum(cm[c].values())
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        result[c] = {"precision": precision, "recall": recall, "f1": f1, "support": float(support)}
    return result


def build_gold_report(
    pair_ids: Sequence[str],
    question_ids: Sequence[str],
    gold_labels: Sequence[str],
    predicted_labels: Sequence[str],
    mode: str,
    label_order: Sequence[str] = LABEL_ORDER,
) -> GoldEvalReport:
    cm = compute_confusion_matrix(gold_labels, predicted_labels, label_order)
    per_class = compute_per_class_metrics(cm, label_order)
    macro_f1 = sum(m["f1"] for m in per_class.values()) / len(label_order)

    e_to_c = cm["entailment"]["contradiction"]
    c_to_e = cm["contradiction"]["entailment"]
    e_support = per_class["entailment"]["support"]
    c_support = per_class["contradiction"]["support"]

    predictions = [
        PredictionRecord(pair_id=pid, question_id=qid, gold_label=g, predicted_label=p, correct=(g == p))
        for pid, qid, g, p in zip(pair_ids, question_ids, gold_labels, predicted_labels)
    ]

    return GoldEvalReport(
        mode=mode,
        n_pairs=len(gold_labels),
        label_order=tuple(label_order),
        confusion_matrix=cm,
        per_class=per_class,
        macro_f1=macro_f1,
        e_to_c_count=e_to_c,
        e_to_c_rate=(e_to_c / e_support if e_support else 0.0),
        c_to_e_count=c_to_e,
        c_to_e_rate=(c_to_e / c_support if c_support else 0.0),
        predictions=predictions,
    )


# ── model construction / inference ───────────────────────────────────────────


EXPECTED_ID2LABEL: dict[int, str] = {0: "entailment", 1: "neutral", 2: "contradiction"}


def _assert_id2label(model: PreTrainedModel) -> None:
    """Verification pass hardening: print the model's actual id2label and
    raise immediately if it doesn't match the canonical mapping this whole
    pipeline assumes (configs/nli_finetune.yaml's labels: section) — a
    mismatch here would silently corrupt every downstream prediction."""
    print(f"[gold_eval] model.config.id2label = {model.config.id2label}")
    actual = {int(k): str(v).strip().lower() for k, v in model.config.id2label.items()}
    if actual != EXPECTED_ID2LABEL:
        raise ValueError(f"model.config.id2label mismatch: expected {EXPECTED_ID2LABEL}, got {model.config.id2label}")


def build_pretrained_model_and_tokenizer(model_name: str) -> tuple[PreTrainedModel, PreTrainedTokenizerBase]:
    """Production path: downloads the real base model + tokenizer from the
    Hugging Face Hub. Never called by tests (which inject a tiny synthetic
    model instead) — network access is a Kaggle-runner concern."""
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    _assert_id2label(model)
    return model, tokenizer


def load_adapter(model: PreTrainedModel, adapter_path: Path) -> PreTrainedModel:
    """Loads the LoRA adapter and fails loud if it did not actually attach:
    asserts model.peft_config is non-empty, and logs the resolved path plus
    the adapter_config.json contents so a silently-inert adapter is visible
    in the run log, not just in the (separate) prediction-identity guard."""
    peft_model = PeftModel.from_pretrained(model, str(adapter_path))

    peft_config = getattr(peft_model, "peft_config", None)
    if not peft_config:
        raise RuntimeError(
            f"Adapter loaded from {adapter_path} but the resulting model's peft_config "
            f"is empty — the LoRA adapter did not attach to the base model."
        )

    adapter_config_path = Path(adapter_path) / "adapter_config.json"
    adapter_config_contents: dict[str, Any] | None = None
    if adapter_config_path.exists():
        adapter_config_contents = json.loads(adapter_config_path.read_text(encoding="utf-8"))

    logger.info("Loaded LoRA adapter from: %s", adapter_path)
    logger.info("peft_config: %s", {name: str(cfg) for name, cfg in peft_config.items()})
    logger.info("adapter_config.json contents: %s", adapter_config_contents)
    print(f"[gold_eval] Loaded LoRA adapter from: {adapter_path}")
    print(f"[gold_eval] adapter_config.json: {adapter_config_contents}")

    return peft_model


def _normalize_label(raw: str) -> str:
    label = str(raw).strip().lower()
    if label not in LABEL_ORDER:
        raise ValueError(f"Unrecognized model label {raw!r}; expected one of {LABEL_ORDER}")
    return label


@torch.no_grad()
def predict_labels(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizerBase,
    premises: Sequence[str],
    hypotheses: Sequence[str],
    max_length: int = 256,
    batch_size: int = 8,
) -> list[str]:
    model.eval()
    id2label = {int(k): v for k, v in model.config.id2label.items()}
    predictions: list[str] = []
    for start in range(0, len(premises), batch_size):
        batch_premises = list(premises[start : start + batch_size])
        batch_hyps = list(hypotheses[start : start + batch_size])
        inputs = tokenizer(
            batch_premises, batch_hyps, truncation=True, padding=True, max_length=max_length, return_tensors="pt"
        )
        logits = model(**inputs).logits
        pred_ids = logits.argmax(dim=-1).tolist()
        predictions.extend(_normalize_label(id2label[i]) for i in pred_ids)
    return predictions


# ── orchestration ─────────────────────────────────────────────────────────────


def run_gold_eval(
    cfg: Config,
    gold_set_path: Path,
    model: PreTrainedModel | None = None,
    tokenizer: PreTrainedTokenizerBase | None = None,
    adapter_path: Path | None = None,
    zero_shot: bool = False,
    batch_size: int = 8,
    max_length: int = 256,
) -> GoldEvalReport:
    """Evaluate the base model (zero_shot=True, or adapter_path=None) or the
    base model + LoRA adapter (zero_shot=False and adapter_path given) on the
    DS-014 Gold Set, reusing `nli.dataset.load_gold_set` unmodified.

    If `model`/`tokenizer` are omitted, the real base model from config is
    downloaded (production path). Tests inject a tiny synthetic model/tokenizer
    instead so inference can be smoke-tested offline in seconds.
    """
    gold_pairs = load_gold_set(gold_set_path)

    if model is None or tokenizer is None:
        model, tokenizer = build_pretrained_model_and_tokenizer(cfg.nli_model)

    mode = "zero-shot"
    if not zero_shot and adapter_path is not None:
        model = load_adapter(model, adapter_path)
        mode = f"adapter:{adapter_path}"

    premises = [p.premise for p in gold_pairs]
    hypotheses = [p.hypothesis for p in gold_pairs]
    gold_labels = [p.label for p in gold_pairs]

    predicted_labels = predict_labels(model, tokenizer, premises, hypotheses, max_length=max_length, batch_size=batch_size)

    return build_gold_report(
        pair_ids=[p.pair_id for p in gold_pairs],
        question_ids=[p.question_id for p in gold_pairs],
        gold_labels=gold_labels,
        predicted_labels=predicted_labels,
        mode=mode,
    )
