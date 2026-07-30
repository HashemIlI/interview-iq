"""
tests/test_nli_engine.py — Phase 6 NLI-matrix-engine CPU smoke tests.

Same injected-tiny-offline-model pattern as test_gold_eval.py / test_finetune_smoke.py
— a randomly initialized DebertaV2ForSequenceClassification (architecturally
faithful to mDeBERTa-v3) plus a from-scratch WordLevel tokenizer, no network
access. Verifies the full Claims x Chunks matrix (Precision direction) and
the reversed Coverage-direction matrix actually run end-to-end on CPU and
produce well-formed raw softmax probabilities (never argmax internally).

Run with:  pytest tests/test_nli_engine.py -v
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

from interview_iq.nli.engine import (
    LABEL_ORDER,
    ClaimsChunksMatrix,
    build_claims_chunks_matrix,
    build_coverage_matrix,
    run_nli_matrix,
)
from interview_iq.refdocs.loader import load_reference_docs
from interview_iq.scoring.aggregation import Verdict, score_claim

FIXTURES_DIR = Path(__file__).parent / "fixtures"
REFDOCS_MINI = FIXTURES_DIR / "refdocs_mini.json"
CLAIMS_MINI = FIXTURES_DIR / "claims_mini.json"

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


def _load_fixture_texts() -> tuple[list[str], list, list[str]]:
    """Returns (claim_texts, chunks, all_texts_for_vocab)."""
    refdocs = load_reference_docs(REFDOCS_MINI)
    document = refdocs.get_document("ZZ-001")
    assert document is not None

    claims_data = json.loads(CLAIMS_MINI.read_text(encoding="utf-8"))
    claim_texts = [c["text"] for c in claims_data["claims"]]

    all_texts = claim_texts + [c.text for c in document.chunks]
    return claim_texts, list(document.chunks), all_texts


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


def _assert_valid_probs(probs: dict[str, float]) -> None:
    assert set(probs.keys()) == set(LABEL_ORDER)
    assert abs(sum(probs.values()) - 1.0) < 1e-4
    for v in probs.values():
        assert 0.0 <= v <= 1.0


def test_run_nli_matrix_shape_and_valid_probs() -> None:
    claim_texts, chunks, vocab_texts = _load_fixture_texts()
    model, tokenizer = _build_tiny_model_and_tokenizer(vocab_texts)

    matrix = run_nli_matrix(model, tokenizer, premises=[c.text for c in chunks], hypotheses=claim_texts)
    assert len(matrix) == len(chunks)
    for row in matrix:
        assert len(row) == len(claim_texts)
        for cell in row:
            _assert_valid_probs(cell)


def test_build_claims_chunks_matrix_is_claim_major_and_valid() -> None:
    claim_texts, chunks, vocab_texts = _load_fixture_texts()
    model, tokenizer = _build_tiny_model_and_tokenizer(vocab_texts)

    matrix = build_claims_chunks_matrix(model, tokenizer, claims=claim_texts, chunks=chunks)
    assert matrix.claims == tuple(claim_texts)
    assert matrix.chunk_ids == tuple(c.chunk_id for c in chunks)
    assert len(matrix.matrix) == len(claim_texts)
    for claim_idx in range(len(claim_texts)):
        assert len(matrix.matrix[claim_idx]) == len(chunks)
        e = matrix.max_entailment(claim_idx)
        c = matrix.max_contradiction(claim_idx)
        assert 0.0 <= e <= 1.0
        assert 0.0 <= c <= 1.0
        best = matrix.best_chunk_id(claim_idx)
        assert best in matrix.chunk_ids
        # D110: best_evidence's chunk/entailment must agree with the
        # existing best_chunk_id/max_entailment (both are argmax-entailment
        # by definition); its contradiction is read from that same chunk,
        # not independently maximised, so it need not equal max_contradiction.
        best_evidence_chunk, best_evidence_e, best_evidence_c = matrix.best_evidence(claim_idx)
        assert best_evidence_chunk == best
        assert best_evidence_e == e
        assert 0.0 <= best_evidence_c <= 1.0


def test_build_coverage_matrix_is_keypoint_major_and_valid() -> None:
    claim_texts, chunks, vocab_texts = _load_fixture_texts()
    model, tokenizer = _build_tiny_model_and_tokenizer(vocab_texts)

    # ZZ-001's key_points are a 2-chunk subset (see refdocs_mini.json).
    key_point_chunks = [c for c in chunks if c.chunk_id in ("ZZ001-C01", "ZZ001-C02")]
    matrix = build_coverage_matrix(model, tokenizer, claims=claim_texts, key_point_chunks=key_point_chunks)

    assert matrix.key_point_chunk_ids == tuple(c.chunk_id for c in key_point_chunks)
    assert len(matrix.matrix) == len(key_point_chunks)
    for kp_idx in range(len(key_point_chunks)):
        assert len(matrix.matrix[kp_idx]) == len(claim_texts)
        e = matrix.max_entailment_for_keypoint(kp_idx)
        assert 0.0 <= e <= 1.0


def test_id2label_mismatch_raises() -> None:
    claim_texts, chunks, vocab_texts = _load_fixture_texts()
    tokenizer = _build_tiny_tokenizer(vocab_texts)
    bad_config = DebertaV2Config(
        vocab_size=tokenizer.vocab_size,
        hidden_size=16,
        num_hidden_layers=1,
        num_attention_heads=2,
        intermediate_size=32,
        max_position_embeddings=160,
        type_vocab_size=1,
        relative_attention=True,
        position_buckets=32,
        pad_token_id=tokenizer.pad_token_id,
        num_labels=3,
        id2label={0: "contradiction", 1: "neutral", 2: "entailment"},  # wrong order
        label2id={"contradiction": 0, "neutral": 1, "entailment": 2},
    )
    bad_model = DebertaV2ForSequenceClassification(bad_config)

    import pytest

    with pytest.raises(ValueError, match="id2label mismatch"):
        run_nli_matrix(bad_model, tokenizer, premises=[chunks[0].text], hypotheses=[claim_texts[0]])


def test_best_evidence_avoids_false_contradiction_from_unrelated_chunk() -> None:
    """D110: hand-built matrix encoding the real SE-028 claim 4 case
    ("تحسن وتنضف Code دون تغيير سلوكه", a factually correct claim). The
    argmax-entailment chunk (SE028-C04, the Refactor-stage chunk this claim
    is actually about) has low contradiction; a different, unrelated chunk
    (SE028-C03, the Red-stage chunk) happens to have very high contradiction
    against this claim's text. Before D110, max_contradiction() picked up
    that unrelated chunk's 0.999570 independently of which chunk entailed
    the claim, yielding CONTRADICTED at the maximum penalty for a correct
    claim. best_evidence() reads contradiction off the SAME chunk that
    produced max_e, so the verdict is NEUTRAL instead (max_e=0.882708 is
    just below tau_e=0.9, and that chunk's own contradiction, 0.093219, is
    below tau=0.5)."""
    matrix = ClaimsChunksMatrix(
        claims=("تحسن وتنضف Code دون تغيير سلوكه.",),
        chunk_ids=("SE028-C04", "SE028-C03"),
        matrix=(
            (
                {"entailment": 0.882708, "neutral": 0.024073, "contradiction": 0.093219},  # argmax entailment
                {"entailment": 0.000089, "neutral": 0.000341, "contradiction": 0.999570},  # argmax contradiction, different chunk
            ),
        ),
    )

    best_chunk, max_e, max_c = matrix.best_evidence(0)
    assert best_chunk == "SE028-C04"
    assert max_e == pytest.approx(0.882708)
    assert max_c == pytest.approx(0.093219)

    verdict = score_claim(max_e, max_c, tau=0.5, tau_e=0.9, alpha=0.0)
    assert verdict.verdict is Verdict.NEUTRAL

    # Contrast with the pre-D110 independent aggregation, retained on the
    # class for the D110 provenance measurement: it would have produced the
    # false CONTRADICTED verdict this fix removes.
    old_max_c = matrix.max_contradiction(0)
    assert old_max_c == pytest.approx(0.999570)
    old_verdict = score_claim(max_e, old_max_c, tau=0.5, tau_e=0.9, alpha=0.0)
    assert old_verdict.verdict is Verdict.CONTRADICTED
