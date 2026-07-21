"""
decomposition/trainer.py — Phase 8 fine-tuning trainer for AraT5-base.

Fine-tunes UBC-NLP/AraT5-base (configs/decomposition.yaml model.selected,
Q6/D54) as a full seq2seq model -- no LoRA here; the LoRA setup (r=16,
alpha=32) is specific to the NLI classifier (D38) and does not apply to
this generation task. Trains on the Knowledge Distillation corpus
(dataset_builder.build_kd_dataset, D55) using the prompt/target format
from prompts.py (D56).

All hyperparameters come from configs/decomposition.yaml via
interview_iq.config.Config -- nothing is hardcoded here (same convention
as interview_iq.nli.finetune). Actual values registered in decisions.md
D57, measured empirically via scripts/probe_token_lengths.py.

O9 (Gold/Validation set, D55) is never touched by this module -- only
build_kd_dataset's paired variant corpus is split for train/val here. O9
is reserved exclusively for the final gold evaluation in inference.py.

Intended to run on Kaggle T4 (fp16 requires GPU); not a local-CPU-viable
training loop given AraT5-base's size and the epoch/patience budget in
D57.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from datasets import Dataset
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    DataCollatorForSeq2Seq,
    EarlyStoppingCallback,
    PreTrainedModel,
    PreTrainedTokenizerBase,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
)

from interview_iq.config import Config
from interview_iq.decomposition.dataset_builder import build_kd_dataset
from interview_iq.decomposition.prompts import build_training_pair
from interview_iq.decomposition.types import AnnotationRules, KDExample


# ── question-ID-level split ────────────────────────────────────────────────


def split_by_question_ids(
    examples: list[KDExample], val_ratio: float, seed: int
) -> tuple[list[KDExample], list[KDExample]]:
    """Question-ID-level split (same principle as
    interview_iq.nli.finetune.split_train_val, D26). Each KDExample here
    may contain multiple variants per question_id, so the seeded shuffle and
    ratio cut operate on unique question IDs. All variants of a question are
    then selected together, preventing cross-split leakage.

    Must only be called on build_kd_dataset's output. Never pass O9
    (Gold/Validation set, D55) in here -- it is not part of this split.
    """
    if not 0.0 < val_ratio < 1.0:
        raise ValueError(f"val_ratio must be in (0, 1), got {val_ratio!r}")

    example_ids = [e.example_id for e in examples]
    if len(example_ids) != len(set(example_ids)):
        raise ValueError("split_by_question_ids requires unique example_id values")

    qids = sorted({e.question_id for e in examples})

    rng = random.Random(seed)
    shuffled = qids[:]
    rng.shuffle(shuffled)

    n_val = max(1, round(len(shuffled) * val_ratio))
    val_ids = set(shuffled[:n_val])

    train = [e for e in examples if e.question_id not in val_ids]
    val = [e for e in examples if e.question_id in val_ids]

    if not train:
        raise ValueError("Train split is empty after applying val_ratio")
    if not val:
        raise ValueError("Val split is empty after applying val_ratio")

    return train, val


# ── tokenization ─────────────────────────────────────────────────────────────


def examples_to_dataset(
    examples: list[KDExample],
    tokenizer: PreTrainedTokenizerBase,
    max_source_length: int,
    max_target_length: int,
) -> Dataset:
    pairs = [build_training_pair(e) for e in examples]
    inputs = [p[0] for p in pairs]
    targets = [p[1] for p in pairs]

    ds = Dataset.from_dict(
        {
            "question_id": [e.question_id for e in examples],
            "example_id": [e.example_id for e in examples],
            "variant": [e.variant for e in examples],
            "source_file": [e.source_file for e in examples],
            "input_text": inputs,
            "target_text": targets,
        }
    )

    def _tokenize(batch: dict[str, list[Any]]) -> dict[str, Any]:
        model_inputs = tokenizer(
            batch["input_text"], truncation=True, max_length=max_source_length
        )
        labels = tokenizer(
            text_target=batch["target_text"], truncation=True, max_length=max_target_length
        )
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    ds = ds.map(_tokenize, batched=True)
    ds = ds.remove_columns(["input_text", "target_text"])
    return ds


# ── model construction ─────────────────────────────────────────────────────


def build_pretrained_model_and_tokenizer(
    model_name: str,
) -> tuple[PreTrainedModel, PreTrainedTokenizerBase]:
    """Production path: downloads the real AraT5-base model + tokenizer
    from the Hugging Face Hub. Mirrors
    interview_iq.nli.finetune.build_pretrained_model_and_tokenizer -- tests
    should inject a tiny synthetic model/tokenizer instead (network access
    is a Kaggle-runner concern, same convention as the NLI trainer)."""
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return model, tokenizer


# ── orchestration ──────────────────────────────────────────────────────────


@dataclass
class TrainerResult:
    n_train: int
    n_val: int
    train_result: Any
    eval_metrics: dict[str, float]
    output_dir: Path


def run_training(
    cfg: Config,
    corpus_path: Path,
    output_dir: Path,
    model: PreTrainedModel | None = None,
    tokenizer: PreTrainedTokenizerBase | None = None,
    annotation_rules: AnnotationRules | None = None,
    training_arg_overrides: dict[str, Any] | None = None,
) -> TrainerResult:
    """Run one AraT5-base fine-tuning job end to end (D57 hyperparameters).

    If `model`/`tokenizer` are omitted, the real base model from
    configs/decomposition.yaml (`model.selected`) is downloaded via
    `build_pretrained_model_and_tokenizer` (production path). Tests should
    inject a tiny synthetic model/tokenizer instead so the loop can be
    smoke-tested offline in seconds -- same convention as
    interview_iq.nli.finetune.run_finetune.
    """
    decomp_cfg = cfg.decomposition
    split_cfg = decomp_cfg["split"]
    tok_cfg = decomp_cfg["tokenizer"]
    train_cfg = decomp_cfg["training"]
    model_name = decomp_cfg["model"]["selected"]

    if annotation_rules is None:
        rules_cfg = decomp_cfg["annotation_rules"]
        annotation_rules = AnnotationRules(
            preserve_hedging=bool(rules_cfg["preserve_hedging"]),
            generalise_personal_framing=bool(rules_cfg["generalise_personal_framing"]),
            no_unverifiable_causal_bridge=bool(rules_cfg["no_unverifiable_causal_bridge"]),
            enforce_self_containment=bool(rules_cfg["enforce_self_containment"]),
        )

    # build_kd_dataset already excludes flagged questions (e.g. GN-050) and
    # asserts O9 is not leaked in (dataset_builder.check_o9_not_in_training).
    all_examples = build_kd_dataset(corpus_path, annotation_rules)

    train_examples, val_examples = split_by_question_ids(
        all_examples,
        val_ratio=float(split_cfg["val_ratio"]),
        seed=int(split_cfg["seed"]),
    )

    if model is None or tokenizer is None:
        model, tokenizer = build_pretrained_model_and_tokenizer(model_name)

    max_source_length = int(tok_cfg["max_source_length"])
    max_target_length = int(tok_cfg["max_target_length"])

    train_ds = examples_to_dataset(train_examples, tokenizer, max_source_length, max_target_length)
    val_ds = examples_to_dataset(val_examples, tokenizer, max_source_length, max_target_length)

    args_kwargs: dict[str, Any] = dict(
        output_dir=str(output_dir),
        learning_rate=float(train_cfg["learning_rate"]),
        lr_scheduler_type=train_cfg["lr_scheduler_type"],
        warmup_ratio=float(train_cfg["warmup_ratio"]),
        per_device_train_batch_size=int(train_cfg["per_device_train_batch_size"]),
        per_device_eval_batch_size=int(train_cfg["per_device_eval_batch_size"]),
        gradient_accumulation_steps=int(train_cfg["gradient_accumulation_steps"]),
        weight_decay=float(train_cfg["weight_decay"]),
        num_train_epochs=float(train_cfg["num_train_epochs"]),
        evaluation_strategy=train_cfg["evaluation_strategy"],
        save_strategy=train_cfg["save_strategy"],
        save_total_limit=int(train_cfg["save_total_limit"]),
        load_best_model_at_end=bool(train_cfg["load_best_model_at_end"]),
        metric_for_best_model=train_cfg["metric_for_best_model"],
        greater_is_better=bool(train_cfg["greater_is_better"]),
        fp16=bool(train_cfg["fp16"]),
        predict_with_generate=True,
        seed=int(train_cfg["seed"]),
        report_to=[],
    )
    if training_arg_overrides:
        args_kwargs.update(training_arg_overrides)
    training_args = Seq2SeqTrainingArguments(**args_kwargs)

    data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model)
    early_stopping_patience = int(train_cfg["early_stopping_patience"])

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        data_collator=data_collator,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=early_stopping_patience)],
    )

    train_result = trainer.train()
    eval_metrics = trainer.evaluate() if len(val_ds) > 0 else {}
    trainer.save_model(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))

    return TrainerResult(
        n_train=len(train_examples),
        n_val=len(val_examples),
        train_result=train_result,
        eval_metrics=eval_metrics,
        output_dir=output_dir,
    )


if __name__ == "__main__":
    import sys

    corpus_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("results")
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("checkpoints/decomposition_arat5")

    cfg = Config()
    result = run_training(cfg, corpus_path, output_dir)

    print(f"train examples: {result.n_train}")
    print(f"val examples:   {result.n_val}")
    print(f"eval metrics:   {result.eval_metrics}")
    print(f"saved to:       {result.output_dir}")
