"""
tests/test_gold_eval.py — Phase 5 CPU smoke + metric-correctness tests.

Metric computation (compute_confusion_matrix / compute_per_class_metrics /
build_gold_report) is pure Python and tested directly against a hand-built
confusion case. Model inference is smoke-tested with the same
injected-tiny-offline-model pattern as test_finetune_smoke.py — a randomly
initialized DebertaV2ForSequenceClassification (architecturally faithful to
mDeBERTa-v3) plus a from-scratch WordLevel tokenizer, no network access.

Run with:  pytest tests/test_gold_eval.py -v
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
from interview_iq.evaluation.gold_eval import (
    LABEL_ORDER,
    build_gold_report,
    compute_confusion_matrix,
    compute_per_class_metrics,
    predict_labels,
    run_gold_eval,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"
GOLD_MINI = FIXTURES_DIR / "gold_mini.json"
CONFIGS_DIR = Path(__file__).parent.parent / "configs"

ID2LABEL = {0: "entailment", 1: "neutral", 2: "contradiction"}
LABEL2ID = {v: k for k, v in ID2LABEL.items()}


# ═══════════════════════════════════════════════════════════════════════════
# pure metric math — hand-built confusion case
# ═══════════════════════════════════════════════════════════════════════════

# gold:      E  E  C  C  C  N
# predicted: E  N  C  E  C  N
GOLD = ["entailment", "entailment", "contradiction", "contradiction", "contradiction", "neutral"]
PRED = ["entailment", "neutral", "contradiction", "entailment", "contradiction", "neutral"]


def test_confusion_matrix_hand_built() -> None:
    cm = compute_confusion_matrix(GOLD, PRED)
    assert cm == {
        "entailment": {"entailment": 1, "neutral": 1, "contradiction": 0},
        "neutral": {"entailment": 0, "neutral": 1, "contradiction": 0},
        "contradiction": {"entailment": 1, "neutral": 0, "contradiction": 2},
    }


def test_per_class_metrics_hand_built() -> None:
    cm = compute_confusion_matrix(GOLD, PRED)
    per_class = compute_per_class_metrics(cm)

    assert per_class["entailment"]["precision"] == pytest.approx(0.5)
    assert per_class["entailment"]["recall"] == pytest.approx(0.5)
    assert per_class["entailment"]["f1"] == pytest.approx(0.5)
    assert per_class["entailment"]["support"] == 2

    assert per_class["neutral"]["precision"] == pytest.approx(0.5)
    assert per_class["neutral"]["recall"] == pytest.approx(1.0)
    assert per_class["neutral"]["f1"] == pytest.approx(2 / 3)
    assert per_class["neutral"]["support"] == 1

    assert per_class["contradiction"]["precision"] == pytest.approx(1.0)
    assert per_class["contradiction"]["recall"] == pytest.approx(2 / 3)
    assert per_class["contradiction"]["f1"] == pytest.approx(0.8)
    assert per_class["contradiction"]["support"] == 3


def test_macro_f1_and_e_c_cells() -> None:
    report = build_gold_report(
        pair_ids=[f"P{i}" for i in range(len(GOLD))],
        question_ids=["ZZ-999"] * len(GOLD),
        gold_labels=GOLD,
        predicted_labels=PRED,
        mode="unit-test",
    )
    expected_macro_f1 = (0.5 + 2 / 3 + 0.8) / 3
    assert report.macro_f1 == pytest.approx(expected_macro_f1)

    # E->C: gold=entailment, predicted=contradiction -> 0 occurrences above
    assert report.e_to_c_count == 0
    assert report.e_to_c_rate == pytest.approx(0.0)
    # C->E: gold=contradiction, predicted=entailment -> 1 occurrence (index 3)
    assert report.c_to_e_count == 1
    assert report.c_to_e_rate == pytest.approx(1 / 3)

    assert report.n_pairs == 6
    assert len(report.predictions) == 6
    assert report.predictions[3].gold_label == "contradiction"
    assert report.predictions[3].predicted_label == "entailment"
    assert report.predictions[3].correct is False
    assert report.predictions[0].correct is True


def test_to_dict_round_trips_through_json() -> None:
    report = build_gold_report(
        pair_ids=["P1"], question_ids=["ZZ-999"], gold_labels=["entailment"], predicted_labels=["entailment"], mode="unit-test"
    )
    payload = json.dumps(report.to_dict(), ensure_ascii=False)
    reloaded = json.loads(payload)
    assert reloaded["mode"] == "unit-test"
    assert reloaded["n_pairs"] == 1
    assert reloaded["predictions"][0]["gold_label"] == "entailment"


def test_signature_rates_are_zero_with_no_support() -> None:
    # No entailment/contradiction gold examples at all -> rates must not
    # divide by zero, and must report 0.0 rather than raising.
    report = build_gold_report(
        pair_ids=["P1"], question_ids=["ZZ-999"], gold_labels=["neutral"], predicted_labels=["neutral"], mode="unit-test"
    )
    assert report.e_to_c_rate == 0.0
    assert report.c_to_e_rate == 0.0


# ═══════════════════════════════════════════════════════════════════════════
# model injection — offline tiny DebertaV2, no network access
# ═══════════════════════════════════════════════════════════════════════════


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


def _build_tiny_model_and_tokenizer():
    gold_data = json.loads(GOLD_MINI.read_text(encoding="utf-8"))
    texts = []
    for pair in gold_data["pairs"]:
        texts.append(pair["premise"])
        texts.append(pair["hypothesis"])
    tokenizer = _build_tiny_tokenizer(texts)

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


@pytest.fixture(scope="module")
def cfg() -> Config:
    return Config(configs_dir=CONFIGS_DIR)


def test_zero_shot_inference_runs_end_to_end(cfg: Config) -> None:
    model, tokenizer = _build_tiny_model_and_tokenizer()
    report = run_gold_eval(
        cfg=cfg,
        gold_set_path=GOLD_MINI,
        model=model,
        tokenizer=tokenizer,
        zero_shot=True,
    )
    assert report.mode == "zero-shot"
    assert report.n_pairs == 2
    assert all(p.predicted_label in LABEL_ORDER for p in report.predictions)


def test_zero_shot_flag_skips_adapter_loading_even_if_path_given(cfg: Config) -> None:
    model, tokenizer = _build_tiny_model_and_tokenizer()
    # A nonexistent adapter path would raise if load_adapter were ever called.
    bogus_adapter_path = Path("/does/not/exist/adapter")
    report = run_gold_eval(
        cfg=cfg,
        gold_set_path=GOLD_MINI,
        model=model,
        tokenizer=tokenizer,
        adapter_path=bogus_adapter_path,
        zero_shot=True,  # must take priority and skip adapter loading entirely
    )
    assert report.mode == "zero-shot"


def test_omitting_adapter_path_is_also_zero_shot(cfg: Config) -> None:
    model, tokenizer = _build_tiny_model_and_tokenizer()
    report = run_gold_eval(
        cfg=cfg,
        gold_set_path=GOLD_MINI,
        model=model,
        tokenizer=tokenizer,
        adapter_path=None,
        zero_shot=False,
    )
    assert report.mode == "zero-shot"


# ═══════════════════════════════════════════════════════════════════════════
# V2 — raw probabilities (decisions.md D41/D42)
# ═══════════════════════════════════════════════════════════════════════════


def test_predict_labels_returns_probs_alongside_labels() -> None:
    model, tokenizer = _build_tiny_model_and_tokenizer()
    gold_data = json.loads(GOLD_MINI.read_text(encoding="utf-8"))
    premises = [p["premise"] for p in gold_data["pairs"]]
    hypotheses = [p["hypothesis"] for p in gold_data["pairs"]]

    labels, probs = predict_labels(model, tokenizer, premises, hypotheses)

    assert len(labels) == len(probs) == len(premises)
    for label, prob_dict in zip(labels, probs):
        assert set(prob_dict.keys()) == set(LABEL_ORDER)
        # argmax of the reported probs must agree with the reported label --
        # proves the probs are not just decorative, they describe the same event.
        assert max(prob_dict, key=prob_dict.get) == label
        assert abs(sum(prob_dict.values()) - 1.0) < 1e-4  # softmax sums to 1
        for v in prob_dict.values():
            assert 0.0 <= v <= 1.0
            assert v == round(v, 6)  # rounded to 6 decimals, not more


def test_run_gold_eval_predictions_carry_probs(cfg: Config) -> None:
    model, tokenizer = _build_tiny_model_and_tokenizer()
    report = run_gold_eval(cfg=cfg, gold_set_path=GOLD_MINI, model=model, tokenizer=tokenizer, zero_shot=True)

    assert len(report.predictions) == 2
    for p in report.predictions:
        assert p.probs is not None
        assert set(p.probs.keys()) == set(LABEL_ORDER)
        assert max(p.probs, key=p.probs.get) == p.predicted_label

    payload = json.dumps(report.to_dict(), ensure_ascii=False)
    reloaded = json.loads(payload)
    assert "probs" in reloaded["predictions"][0]
    assert set(reloaded["predictions"][0]["probs"].keys()) == set(LABEL_ORDER)


def test_build_gold_report_probs_default_to_none_when_omitted() -> None:
    """Backward compatibility: callers that only have label lists (e.g. hand-built
    confusion-matrix tests) must not be forced to supply probs."""
    report = build_gold_report(
        pair_ids=["P1"], question_ids=["ZZ-999"], gold_labels=["entailment"], predicted_labels=["entailment"], mode="unit-test"
    )
    assert report.predictions[0].probs is None
    assert report.to_dict()["predictions"][0]["probs"] is None


def test_build_gold_report_accepts_explicit_probs() -> None:
    probs = [{"entailment": 0.7, "neutral": 0.2, "contradiction": 0.1}]
    report = build_gold_report(
        pair_ids=["P1"],
        question_ids=["ZZ-999"],
        gold_labels=["entailment"],
        predicted_labels=["entailment"],
        mode="unit-test",
        probs=probs,
    )
    assert report.predictions[0].probs == probs[0]
