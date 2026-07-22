"""
tests/test_coverage_channel_real_claims_experiment.py — D82 smoke test.

Exercises scripts/coverage_channel_real_claims_experiment.py's actual wiring
(O9 markdown parsing -> mocked decomposition -> both NLI arms' Coverage
computation) against tests/fixtures/o9_mini.md and
tests/fixtures/refdocs_mini.json, with an injected tiny offline DebertaV2
model for BOTH arms (same pattern as test_run_scoring.py) and a mocked
decompose_via_llm (no HTTP layer involved -- OpenRouter's HTTP behavior is
already covered by the sanity-gate tests, not this script's job to re-test).

Never calls main() (which would build the real ~550MB base model, load a
real LoRA adapter, and make a real OpenRouter API call) -- model/tokenizer/
decompose_fn injection is exactly how run_one_question() is designed to be
tested. Zero real API or network calls anywhere in this file.

Run with:  pytest tests/test_coverage_channel_real_claims_experiment.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from tokenizers import Tokenizer
from tokenizers.models import WordLevel
from tokenizers.pre_tokenizers import Whitespace
from tokenizers.processors import TemplateProcessing
from transformers import DebertaV2Config, DebertaV2ForSequenceClassification, PreTrainedTokenizerFast

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

from coverage_channel_real_claims_experiment import (  # noqa: E402
    O9Question,
    parse_o9_markdown,
    run_one_question,
)
from interview_iq.decomposition.types import DecompositionResult  # noqa: E402
from interview_iq.decomposition_llm.client import LLMDecompositionError  # noqa: E402
from interview_iq.refdocs.loader import load_reference_docs  # noqa: E402

FIXTURES_DIR = Path(__file__).parent / "fixtures"
O9_MINI = FIXTURES_DIR / "o9_mini.md"
REFDOCS_MINI = FIXTURES_DIR / "refdocs_mini.json"

ID2LABEL = {0: "entailment", 1: "neutral", 2: "contradiction"}
LABEL2ID = {v: k for k, v in ID2LABEL.items()}


def _build_tiny_tokenizer(texts: list[str]) -> PreTrainedTokenizerFast:
    """Same pattern as tests/test_run_scoring.py's helper -- duplicated here
    rather than imported, matching this project's existing convention of
    self-contained per-test-file tiny-model fixtures (see also
    test_finetune_smoke.py)."""
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


def _build_tiny_model_and_tokenizer(vocab_texts: list[str]):
    tokenizer = _build_tiny_tokenizer(vocab_texts)
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


# ── Pure parsing tests (no models, no mocks needed) ──────────────────────────


def test_parse_o9_markdown_skips_preamble_and_finds_both_questions() -> None:
    text = O9_MINI.read_text(encoding="utf-8")
    questions = parse_o9_markdown(text)
    assert len(questions) == 2
    assert [q.question_id for q in questions] == ["ZZ-001", "ZZ-002"]


def test_parse_o9_markdown_handles_no_colon_warning_header() -> None:
    """ZZ-002's header ('### ZZ-002 ⚠️ (...)') has no ':' and no question
    text -- mirrors the real DA-029/DS-030 edge case found in
    results/o9_decomposition_exercises.md. Must not be mis-parsed or dropped."""
    text = O9_MINI.read_text(encoding="utf-8")
    questions = parse_o9_markdown(text)
    zz002 = next(q for q in questions if q.question_id == "ZZ-002")
    assert zz002.raw_answer_text  # non-empty
    assert "LIFO" in zz002.raw_answer_text


def test_parse_o9_markdown_handles_both_answer_label_variants() -> None:
    """ZZ-001 uses '**إجابة (لهجة مصرية):**', ZZ-002 uses plain
    '**إجابة:**' -- both must resolve to non-empty raw answer text."""
    text = O9_MINI.read_text(encoding="utf-8")
    questions = parse_o9_markdown(text)
    zz001 = next(q for q in questions if q.question_id == "ZZ-001")
    assert zz001.raw_answer_text
    assert "Recursion" in zz001.raw_answer_text


def test_parse_o9_markdown_raises_on_missing_claims_boundary() -> None:
    broken_text = "### ZZ-999: broken fixture\n\n**إجابة:**\nsome answer text with no Claims section at all\n"
    with pytest.raises(ValueError, match="ZZ-999"):
        parse_o9_markdown(broken_text)


# ── End-to-end wiring test: mocked decomposition + two injected tiny NLI arms ─


def test_run_one_question_end_to_end_success_both_arms() -> None:
    refdocs = load_reference_docs(REFDOCS_MINI)
    question = O9Question(question_id="ZZ-001", raw_answer_text="fixture raw answer text")

    document = refdocs.get_document("ZZ-001")
    assert document is not None

    fake_claims = ["fixture claim one about Recursion", "fixture claim two about Iteration Loop"]
    vocab_texts = fake_claims + [c.text for c in document.chunks]

    zero_shot_model, tokenizer = _build_tiny_model_and_tokenizer(vocab_texts)
    adapter_model, _ = _build_tiny_model_and_tokenizer(vocab_texts)  # independent instance, not shared state

    def _mock_decompose(asr_text: str) -> DecompositionResult:
        return DecompositionResult(source_text=asr_text, claims=fake_claims)

    record = run_one_question(
        question,
        refdocs,
        zero_shot_model,
        tokenizer,
        adapter_model,
        tokenizer,
        decompose_fn=_mock_decompose,
    )

    assert record["decomposition_status"] == "SUCCESS"
    assert record["claims"] == fake_claims
    assert record["track"] == "ZZ"
    assert record["key_point_count"] == 2  # ZZ-001 has 2 key_points in refdocs_mini.json

    for arm_name in ("zero_shot", "adapter"):
        arm = record[arm_name]
        assert arm["status"] == "SUCCESS", arm["error"]
        assert arm["error"] is None
        assert len(arm["max_e_per_keypoint"]) == 2
        for p in arm["max_e_per_keypoint"]:
            assert 0.0 <= p <= 1.0
        assert 0.0 <= arm["coverage_score"] <= 1.0


def test_run_one_question_decomposition_failure_skips_both_arms_without_crashing() -> None:
    refdocs = load_reference_docs(REFDOCS_MINI)
    question = O9Question(question_id="ZZ-001", raw_answer_text="fixture raw answer text")
    document = refdocs.get_document("ZZ-001")
    assert document is not None

    zero_shot_model, tokenizer = _build_tiny_model_and_tokenizer([c.text for c in document.chunks])
    adapter_model = zero_shot_model  # arms are never reached on this path -- reuse is fine here

    def _mock_decompose_raises(asr_text: str) -> DecompositionResult:
        raise LLMDecompositionError("simulated Groq failure for smoke test")

    record = run_one_question(
        question,
        refdocs,
        zero_shot_model,
        tokenizer,
        adapter_model,
        tokenizer,
        decompose_fn=_mock_decompose_raises,
    )

    assert record["decomposition_status"] == "ERROR"
    assert record["claims"] is None
    assert record["zero_shot"]["status"] == "SKIPPED_NO_CLAIMS"
    assert record["adapter"]["status"] == "SKIPPED_NO_CLAIMS"
    assert record["zero_shot"]["coverage_score"] is None
    assert record["adapter"]["coverage_score"] is None


def test_run_one_question_empty_claims_still_scores_coverage_as_zero() -> None:
    """NO_EXTRACTABLE_CLAIMS (claims == []) is a genuine decomposition
    result, not a script error -- Coverage must still run and naturally
    yield 0.0 (coverage_channel's own empty-sequence default), not be
    treated as a skip."""
    refdocs = load_reference_docs(REFDOCS_MINI)
    question = O9Question(question_id="ZZ-001", raw_answer_text="fixture raw answer text")
    document = refdocs.get_document("ZZ-001")
    assert document is not None

    zero_shot_model, tokenizer = _build_tiny_model_and_tokenizer([c.text for c in document.chunks])
    adapter_model, _ = _build_tiny_model_and_tokenizer([c.text for c in document.chunks])

    def _mock_decompose_empty(asr_text: str) -> DecompositionResult:
        return DecompositionResult(source_text=asr_text, claims=[])

    record = run_one_question(
        question,
        refdocs,
        zero_shot_model,
        tokenizer,
        adapter_model,
        tokenizer,
        decompose_fn=_mock_decompose_empty,
    )

    assert record["decomposition_status"] == "SUCCESS"
    assert record["claims"] == []
    for arm_name in ("zero_shot", "adapter"):
        arm = record[arm_name]
        assert arm["status"] == "SUCCESS"
        assert arm["coverage_score"] == 0.0
        assert arm["max_e_per_keypoint"] == [0.0, 0.0]


def test_run_one_question_unknown_question_id_skips_both_arms() -> None:
    refdocs = load_reference_docs(REFDOCS_MINI)
    question = O9Question(question_id="ZZ-404", raw_answer_text="fixture raw answer text")

    def _mock_decompose(asr_text: str) -> DecompositionResult:
        return DecompositionResult(source_text=asr_text, claims=["irrelevant claim"])

    # Decomposition still runs even when the document lookup fails (it does not
    # depend on refdocs), but the coverage arms never reach a model call on this
    # path -- passing None for all four model/tokenizer args asserts that.
    record = run_one_question(
        question,
        refdocs,
        None,
        None,
        None,
        None,
        decompose_fn=_mock_decompose,
    )

    assert record["track"] is None
    assert record["zero_shot"]["status"] == "SKIPPED"
    assert record["adapter"]["status"] == "SKIPPED"
    assert "ZZ-404" in record["zero_shot"]["error"]
