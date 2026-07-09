"""
tests/test_finetune_smoke.py — Phase 4 CPU smoke test.

Exercises the full nli/finetune.py training loop (LoRA wrapping, tokenization,
Trainer.train/evaluate, checkpoint save) end-to-end in seconds by injecting a
tiny, fully offline, randomly-initialized DebertaV2 model that is
architecturally faithful to mDeBERTa-v3 (same query_proj/value_proj module
names the locked LoRA config targets) instead of downloading the real
~550MB base model. No network access is required.

Run with:  pytest tests/test_finetune_smoke.py -v
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from tokenizers import Tokenizer
from tokenizers.models import WordLevel
from tokenizers.pre_tokenizers import Whitespace
from tokenizers.processors import TemplateProcessing
from transformers import DebertaV2Config, DebertaV2ForSequenceClassification, PreTrainedTokenizerFast

from interview_iq.config import Config
from interview_iq.nli.dataset import load_pilot_pairs
from interview_iq.nli.finetune import (
    D28ContaminationError,
    TwinSplitError,
    assert_twins_not_split,
    run_finetune,
    split_train_val,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"
REFDOCS_MINI = FIXTURES_DIR / "refdocs_mini.json"
PAIRS_FLAT = FIXTURES_DIR / "pairs_mini_flat.json"  # question ZZ-001, includes HARD_POS twin HP1
PAIRS_NESTED = FIXTURES_DIR / "pairs_mini_nested.json"  # question ZZ-002
CONFIGS_DIR = Path(__file__).parent.parent / "configs"

FAST_TRAINING_OVERRIDES = {
    "max_steps": 1,
    "per_device_train_batch_size": 2,
    "per_device_eval_batch_size": 2,
    "evaluation_strategy": "no",
    "save_strategy": "no",
    "load_best_model_at_end": False,
    "logging_strategy": "no",
    "warmup_ratio": 0.0,
}


def _build_tiny_tokenizer(texts: list[str]) -> PreTrainedTokenizerFast:
    """A minimal fully offline WordLevel tokenizer built from the fixture
    vocabulary — no download, no real sentencepiece model."""
    vocab = {"[UNK]": 0, "[PAD]": 1, "[CLS]": 2, "[SEP]": 3}
    for text in texts:
        for tok in text.split():
            if tok not in vocab:
                vocab[tok] = len(vocab)

    backend = Tokenizer(WordLevel(vocab=vocab, unk_token="[UNK]"))
    backend.pre_tokenizer = Whitespace()
    backend.post_processor = TemplateProcessing(
        single="[CLS] $A [SEP]",
        pair="[CLS] $A [SEP] $B [SEP]",
        special_tokens=[("[CLS]", vocab["[CLS]"]), ("[SEP]", vocab["[SEP]"])],
    )
    tokenizer = PreTrainedTokenizerFast(
        tokenizer_object=backend,
        unk_token="[UNK]",
        pad_token="[PAD]",
        cls_token="[CLS]",
        sep_token="[SEP]",
    )
    tokenizer.model_max_length = 160
    return tokenizer


def _fixture_texts() -> list[str]:
    texts: list[str] = []
    refdocs_data = json.loads(REFDOCS_MINI.read_text(encoding="utf-8"))
    for doc in refdocs_data["documents"]:
        for chunk in doc["chunks"]:
            texts.append(chunk["text"])
    flat_data = json.loads(PAIRS_FLAT.read_text(encoding="utf-8"))
    texts.extend(p["hypothesis"] for p in flat_data["pairs"])
    nested_data = json.loads(PAIRS_NESTED.read_text(encoding="utf-8"))
    for doc in nested_data["documents"]:
        texts.extend(p["hypothesis"] for p in doc["pairs"])
    return texts


def _build_tiny_model_and_tokenizer() -> tuple[DebertaV2ForSequenceClassification, PreTrainedTokenizerFast]:
    tokenizer = _build_tiny_tokenizer(_fixture_texts())
    config = DebertaV2Config(
        vocab_size=tokenizer.vocab_size,
        hidden_size=16,
        num_hidden_layers=2,
        num_attention_heads=2,
        intermediate_size=32,
        max_position_embeddings=160,
        type_vocab_size=1,
        relative_attention=True,
        position_buckets=32,
        pad_token_id=tokenizer.pad_token_id,
        num_labels=3,
    )
    model = DebertaV2ForSequenceClassification(config)
    return model, tokenizer


@pytest.fixture(scope="module")
def cfg() -> Config:
    """Loads the real, locked configs/nli_finetune.yaml — r=16, alpha=32,
    query_proj/value_proj, lr in [2e-4, 3e-4] all come from here, not from
    this test, so the smoke test exercises the actual locked hyperparameters."""
    return Config(configs_dir=CONFIGS_DIR)


# ═══════════════════════════════════════════════════════════════════════════
# split / twin-integrity helpers (no model involved — fast, no fixture needed)
# ═══════════════════════════════════════════════════════════════════════════


def test_split_train_val_holds_out_question() -> None:
    pairs = load_pilot_pairs([PAIRS_FLAT, PAIRS_NESTED])
    train, val = split_train_val(pairs, {"ZZ-002"})
    assert {p.question_id for p in train} == {"ZZ-001"}
    assert {p.question_id for p in val} == {"ZZ-002"}
    assert len(train) == 6
    assert len(val) == 3
    assert_twins_not_split(train, val)  # must not raise


def test_split_train_val_rejects_unknown_question() -> None:
    pairs = load_pilot_pairs([PAIRS_FLAT, PAIRS_NESTED])
    with pytest.raises(ValueError):
        split_train_val(pairs, {"NOPE-999"})


def test_assert_twins_not_split_detects_violation() -> None:
    pairs = load_pilot_pairs([PAIRS_FLAT, PAIRS_NESTED])
    twin_a = next(p for p in pairs if p.pair_id == "ZZ001-P02a")
    twin_b = next(p for p in pairs if p.pair_id == "ZZ001-P02b")
    with pytest.raises(TwinSplitError):
        assert_twins_not_split([twin_a], [twin_b])


# ═══════════════════════════════════════════════════════════════════════════
# full training-loop smoke tests (tiny synthetic model, one optimizer step)
# ═══════════════════════════════════════════════════════════════════════════


def test_one_training_step_on_fixtures(cfg: Config, tmp_path: Path) -> None:
    model, tokenizer = _build_tiny_model_and_tokenizer()

    result = run_finetune(
        cfg=cfg,
        refdocs_path=REFDOCS_MINI,
        pilot_pair_paths=[PAIRS_FLAT, PAIRS_NESTED],
        output_dir=tmp_path / "checkpoint",
        model=model,
        tokenizer=tokenizer,
        val_question_ids={"ZZ-002"},
        excluded_question_ids={"DS-014"},  # config default; matches nothing in fixtures
        training_arg_overrides=FAST_TRAINING_OVERRIDES,
    )

    assert result.n_train_pairs == 6  # ZZ-001
    assert result.n_val_pairs == 3  # ZZ-002
    assert result.train_result.global_step == 1
    assert "eval_f1_macro" in result.eval_metrics
    assert (tmp_path / "checkpoint").exists()


def test_lora_adapter_is_actually_applied(cfg: Config, tmp_path: Path) -> None:
    model, tokenizer = _build_tiny_model_and_tokenizer()
    run_finetune(
        cfg=cfg,
        refdocs_path=REFDOCS_MINI,
        pilot_pair_paths=[PAIRS_FLAT, PAIRS_NESTED],
        output_dir=tmp_path / "checkpoint",
        model=model,
        tokenizer=tokenizer,
        val_question_ids={"ZZ-002"},
        training_arg_overrides=FAST_TRAINING_OVERRIDES,
    )
    # A LoRA (PEFT) checkpoint saves an adapter_config.json + adapter weights,
    # not a full model state dict -- this is the on-disk proof LoRA was used.
    assert (tmp_path / "checkpoint" / "adapter_config.json").exists()
    adapter_cfg = json.loads((tmp_path / "checkpoint" / "adapter_config.json").read_text(encoding="utf-8"))
    assert adapter_cfg["r"] == 16
    assert adapter_cfg["lora_alpha"] == 32
    assert sorted(adapter_cfg["target_modules"]) == ["query_proj", "value_proj"]


def test_run_finetune_aborts_on_ds014_contamination(cfg: Config, tmp_path: Path) -> None:
    model, tokenizer = _build_tiny_model_and_tokenizer()
    with pytest.raises(D28ContaminationError):
        run_finetune(
            cfg=cfg,
            refdocs_path=REFDOCS_MINI,
            pilot_pair_paths=[PAIRS_FLAT, PAIRS_NESTED],
            output_dir=tmp_path / "checkpoint",
            model=model,
            tokenizer=tokenizer,
            val_question_ids={"ZZ-002"},
            excluded_question_ids={"ZZ-001"},  # simulate contamination
            training_arg_overrides=FAST_TRAINING_OVERRIDES,
        )
