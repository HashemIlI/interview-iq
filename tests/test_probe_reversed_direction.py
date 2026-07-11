"""
tests/test_probe_reversed_direction.py — D46 probe CPU smoke test.

Same injected-tiny-offline-model pattern as test_nli_engine.py /
test_gold_eval.py — a randomly initialized DebertaV2ForSequenceClassification
(architecturally faithful to mDeBERTa-v3) plus a from-scratch WordLevel
tokenizer; no network access, no real checkpoint needed.

Uses refdocs_mini.json as a stand-in for the real reference docs:
  ZZ-001 (3 chunks, 2 key_points) → plays the role of DS-014 (probe_doc)
  ZZ-002 (2 chunks, 1 key_point)  → plays the role of SE-001 (distant_doc)

Expected pair counts per test:
  A  n = len(probe_doc.chunks) = 3                (diagonal self-pairs)
  B  n = len(probe_doc.chunks) * len(distant key_points) = 3 * 1 = 3
  C  n = 3 * 2 - 2 = 4  (3 chunks × 2 key_points minus 2 self-pairs)

Run with:  pytest tests/test_probe_reversed_direction.py -v
"""

from __future__ import annotations

import math
from pathlib import Path

from tokenizers import Tokenizer
from tokenizers.models import WordLevel
from tokenizers.pre_tokenizers import Whitespace
from tokenizers.processors import TemplateProcessing
from transformers import DebertaV2Config, DebertaV2ForSequenceClassification, PreTrainedTokenizerFast

from interview_iq.nli.probe import run_probe
from interview_iq.nli.probe_verdict import (
    TEST_A_THRESHOLD,
    TEST_B_THRESHOLD,
    TEST_C_SIGNAL_THRESHOLD,
    evaluate_verdict,
)
from interview_iq.refdocs.loader import load_reference_docs

FIXTURES_DIR = Path(__file__).parent / "fixtures"
REFDOCS_MINI = FIXTURES_DIR / "refdocs_mini.json"

ID2LABEL = {0: "entailment", 1: "neutral", 2: "contradiction"}
LABEL2ID = {v: k for k, v in ID2LABEL.items()}


def _build_tiny_tokenizer(texts: list[str]) -> PreTrainedTokenizerFast:
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
        tokenizer_object=backend, unk_token="[UNK]", pad_token="[PAD]", cls_token="[CLS]", sep_token="[SEP]"
    )
    tokenizer.model_max_length = 160
    return tokenizer


def _build_tiny_model_and_tokenizer(all_texts: list[str]):
    tokenizer = _build_tiny_tokenizer(all_texts)
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
        id2label=ID2LABEL,
        label2id=LABEL2ID,
    )
    model = DebertaV2ForSequenceClassification(config)
    return model, tokenizer


def test_probe_smoke_shape_and_valid_probs() -> None:
    """run_probe runs end-to-end on CPU fixtures and returns well-formed output."""
    refdocs = load_reference_docs(REFDOCS_MINI)
    probe_doc = refdocs.get_document("ZZ-001")
    distant_doc = refdocs.get_document("ZZ-002")
    assert probe_doc is not None and distant_doc is not None

    all_texts = [c.text for c in probe_doc.chunks] + [c.text for c in distant_doc.chunks]
    model, tokenizer = _build_tiny_model_and_tokenizer(all_texts)

    result = run_probe(model, tokenizer, probe_doc, distant_doc)

    assert result["probe_doc_id"] == "ZZ-001"
    assert result["distant_doc_id"] == "ZZ-002"

    # Test A: one diagonal pair per chunk
    assert result["test_A"]["n_pairs"] == len(probe_doc.chunks)  # 3
    for pair in result["test_A"]["pairs"]:
        assert pair["premise_id"] == pair["hypothesis_id"]

    # Test B: all (probe_chunk, distant_kp) combinations — no exclusions
    assert result["test_B"]["n_pairs"] == len(probe_doc.chunks) * len(distant_doc.key_points)  # 3

    # Test C: (probe_chunk × probe_kp) minus self-pairs
    # ZZ-001: 3 chunks, key_points=[ZZ001-C01, ZZ001-C02] → 3*2 - 2 = 4
    probe_kp_set = set(probe_doc.key_points)
    expected_c = sum(
        1
        for c in probe_doc.chunks
        for kp in probe_doc.key_points
        if c.chunk_id != kp
    )
    assert result["test_C"]["n_pairs"] == expected_c  # 4
    for pair in result["test_C"]["pairs"]:
        assert pair["premise_id"] != pair["hypothesis_id"]
        assert pair["hypothesis_id"] in probe_kp_set

    # All median_p_e values are finite floats in [0, 1]
    for test_key in ("test_A", "test_B", "test_C"):
        median = result[test_key]["median_p_e"]
        assert isinstance(median, float) and not math.isnan(median)
        assert 0.0 <= median <= 1.0

    # All per-pair probs are valid softmax distributions
    for test_key in ("test_A", "test_B", "test_C"):
        for pair in result[test_key]["pairs"]:
            assert 0.0 <= pair["p_e"] <= 1.0
            probs = pair["probs"]
            assert set(probs.keys()) == {"entailment", "neutral", "contradiction"}
            assert abs(sum(probs.values()) - 1.0) < 1e-4
            # p_e must agree with the probs dict
            assert abs(pair["p_e"] - probs["entailment"]) < 1e-9


# ── D46 verdict logic: threshold comparisons on synthetic medians ──────────
# No model, no inference — these test evaluate_verdict() against hand-built
# result dicts carrying only the median_p_e values D46's criteria compare.


def _arm_result(median_a: float, median_b: float, median_c: float) -> dict:
    return {
        "test_A": {"median_p_e": median_a},
        "test_B": {"median_p_e": median_b},
        "test_C": {"median_p_e": median_c},
    }


def test_verdict_test_a_pass_at_exact_threshold() -> None:
    zero_shot = _arm_result(median_a=TEST_A_THRESHOLD, median_b=0.0, median_c=0.5)
    adapter = _arm_result(median_a=TEST_A_THRESHOLD, median_b=0.0, median_c=0.5)
    verdict = evaluate_verdict(zero_shot, adapter)
    assert verdict["zero_shot"]["test_A"]["pass"] is True
    assert verdict["adapter"]["test_A"]["pass"] is True


def test_verdict_test_a_fails_just_below_threshold() -> None:
    zero_shot = _arm_result(median_a=TEST_A_THRESHOLD - 0.001, median_b=0.0, median_c=0.5)
    adapter = _arm_result(median_a=0.95, median_b=0.0, median_c=0.5)
    verdict = evaluate_verdict(zero_shot, adapter)
    assert verdict["zero_shot"]["test_A"]["pass"] is False
    assert verdict["adapter"]["test_A"]["pass"] is True


def test_verdict_test_b_pass_at_exact_threshold() -> None:
    zero_shot = _arm_result(median_a=0.95, median_b=TEST_B_THRESHOLD, median_c=0.5)
    adapter = _arm_result(median_a=0.95, median_b=TEST_B_THRESHOLD, median_c=0.5)
    verdict = evaluate_verdict(zero_shot, adapter)
    assert verdict["zero_shot"]["test_B"]["pass"] is True
    assert verdict["adapter"]["test_B"]["pass"] is True


def test_verdict_test_b_fails_just_above_threshold() -> None:
    zero_shot = _arm_result(median_a=0.95, median_b=TEST_B_THRESHOLD + 0.001, median_c=0.5)
    adapter = _arm_result(median_a=0.95, median_b=0.05, median_c=0.5)
    verdict = evaluate_verdict(zero_shot, adapter)
    assert verdict["zero_shot"]["test_B"]["pass"] is False
    assert verdict["adapter"]["test_B"]["pass"] is True


def test_verdict_signal_detected_when_diff_clears_threshold_and_direction_correct() -> None:
    # adapter median comfortably more than TEST_C_SIGNAL_THRESHOLD below zero-shot.
    zero_shot = _arm_result(median_a=0.95, median_b=0.05, median_c=0.60)
    adapter = _arm_result(median_a=0.95, median_b=0.05, median_c=0.40)
    verdict = evaluate_verdict(zero_shot, adapter)
    signal = verdict["test_C_signal"]
    assert signal["direction_matches_prediction"] is True
    assert signal["diff"] > TEST_C_SIGNAL_THRESHOLD
    assert signal["signal_detected"] is True


def test_verdict_no_signal_when_diff_below_threshold_despite_correct_direction() -> None:
    zero_shot = _arm_result(median_a=0.95, median_b=0.05, median_c=0.60)
    adapter = _arm_result(median_a=0.95, median_b=0.05, median_c=0.55)  # diff = 0.05 < 0.10
    verdict = evaluate_verdict(zero_shot, adapter)
    signal = verdict["test_C_signal"]
    assert signal["direction_matches_prediction"] is True
    assert signal["signal_detected"] is False


def test_verdict_no_signal_when_direction_contradicts_prediction() -> None:
    # adapter median HIGHER than zero-shot by >= 0.10 in magnitude: D46 predicted
    # the opposite direction, so this must not count as a detected signal even
    # though the raw magnitude clears the threshold.
    zero_shot = _arm_result(median_a=0.95, median_b=0.05, median_c=0.50)
    adapter = _arm_result(median_a=0.95, median_b=0.05, median_c=0.65)
    verdict = evaluate_verdict(zero_shot, adapter)
    signal = verdict["test_C_signal"]
    assert signal["direction_matches_prediction"] is False
    assert signal["signal_detected"] is False


def test_verdict_reports_correct_medians_and_diff() -> None:
    zero_shot = _arm_result(median_a=0.92, median_b=0.03, median_c=0.42)
    adapter = _arm_result(median_a=0.91, median_b=0.04, median_c=0.20)
    verdict = evaluate_verdict(zero_shot, adapter)
    signal = verdict["test_C_signal"]
    assert signal["zero_shot_median_p_e"] == 0.42
    assert signal["adapter_median_p_e"] == 0.20
    assert abs(signal["diff"] - 0.22) < 1e-9
