"""
tests/test_run_scoring.py — Phase 6 end-to-end scoring smoke test.

Exercises cli/run_scoring.run_scoring() — retrieval cap + full NLI matrix
(both directions) + Dual-Channel Scoring — against tests/fixtures/ with an
injected tiny offline DebertaV2 model (same pattern as test_gold_eval.py).
No network access, no production data. Never calls main() (which would
construct the real ~550MB base model) — model injection is exactly how this
module is designed to be tested (see run_scoring()'s docstring).

Run with:  pytest tests/test_run_scoring.py -v
"""

from __future__ import annotations

import json
from pathlib import Path

from tokenizers import Tokenizer
from tokenizers.models import WordLevel
from tokenizers.pre_tokenizers import Whitespace
from tokenizers.processors import TemplateProcessing
from transformers import DebertaV2Config, DebertaV2ForSequenceClassification, PreTrainedTokenizerFast

from interview_iq.cli.run_scoring import load_claims, run_scoring
from interview_iq.config import Config
from interview_iq.refdocs.loader import load_reference_docs

FIXTURES_DIR = Path(__file__).parent / "fixtures"
REFDOCS_MINI = FIXTURES_DIR / "refdocs_mini.json"
CLAIMS_MINI = FIXTURES_DIR / "claims_mini.json"
CONFIGS_DIR = Path(__file__).parent.parent / "configs"

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


def test_load_claims_reads_interim_fixture_format() -> None:
    question_id, claims = load_claims(CLAIMS_MINI)
    assert question_id == "ZZ-001"
    assert len(claims) == 2
    assert claims[0].claim_id == "CL01"
    assert claims[0].text  # non-empty


def test_run_scoring_end_to_end_on_fixtures_cpu_only() -> None:
    refdocs = load_reference_docs(REFDOCS_MINI)
    document = refdocs.get_document("ZZ-001")
    assert document is not None

    _, claims = load_claims(CLAIMS_MINI)

    claims_data = json.loads(CLAIMS_MINI.read_text(encoding="utf-8"))
    claim_texts = [c["text"] for c in claims_data["claims"]]
    vocab_texts = claim_texts + [c.text for c in document.chunks]
    model, tokenizer = _build_tiny_model_and_tokenizer(vocab_texts)

    cfg = Config(configs_dir=CONFIGS_DIR)
    # ZZ-001 has 3 chunks, well under any realistic k -> the retrieval cap
    # never binds here; this test's job is to prove the whole pipeline wires
    # together correctly, not to re-test chunk_cap's own ranking behaviour
    # (see test_chunk_cap.py for that).
    result = run_scoring(cfg, document, claims, model, tokenizer)

    assert len(result.claim_scores) == 2
    for cs in result.claim_scores:
        assert cs.best_chunk_id in {c.chunk_id for c in document.chunks}
        assert 0.0 <= cs.max_e <= 1.0
        assert 0.0 <= cs.max_c <= 1.0
    assert 0.0 <= result.coverage <= 1.0
    # score == harmonic_f * configs/scoring.yaml's score_scale (100 by default)
    assert result.score == result.harmonic_f * cfg.scoring["combination"]["score_scale"]
