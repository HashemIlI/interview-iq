"""
tests/test_pipeline.py — Phase 9 pipeline.evaluate_answer() smoke tests.

Zero network, zero real models: ASR is a mocked transcribe_fn, decomposition
is a mocked decompose_fn, and NLI uses the tiny offline DebertaV2 pattern
from tests/test_run_scoring.py / tests/test_gold_eval.py (injected
nli_model/nli_tokenizer -- build_pretrained_model_and_tokenizer is never
called). Reference chunks/key_points come from tests/fixtures/refdocs_mini.json,
same fixture test_run_scoring.py already uses.

Run with:  pytest tests/test_pipeline.py -v
"""

from __future__ import annotations

from pathlib import Path

import pytest
from tokenizers import Tokenizer
from tokenizers.models import WordLevel
from tokenizers.pre_tokenizers import Whitespace
from tokenizers.processors import TemplateProcessing
from transformers import DebertaV2Config, DebertaV2ForSequenceClassification, PreTrainedTokenizerFast

from interview_iq.asr.engine import ASRError
from interview_iq.config import Config
from interview_iq.decomposition.types import DecompositionResult
from interview_iq.decomposition_llm.client import LLMDecompositionError
from interview_iq.pipeline import evaluate_answer
from interview_iq.refdocs.loader import load_reference_docs

FIXTURES_DIR = Path(__file__).parent / "fixtures"
REFDOCS_MINI = FIXTURES_DIR / "refdocs_mini.json"
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


FAKE_CLAIMS = ["fixture claim one about Recursion", "fixture claim two about Iteration Loop"]


def _fake_transcribe_ok(audio_path, config, device_override=None, compute_type_override=None, question_id=None):
    return {
        "question_id": question_id,
        "status": "ok",
        "raw_transcript": "raw fixture transcript",
        "normalized_transcript": "normalized fixture transcript",
        "normalization_log": [],
        "word_timestamps": [],
        "vad_features": {"segments": [{"start_ms": 100.0, "end_ms": 900.0}], "total_speech_duration_ms": 800.0, "threshold": 0.5},
        "avg_logprob": -0.15,
        "pre_answer_latency_sec": 0.1,
    }


def _fake_transcribe_no_speech(audio_path, config, device_override=None, compute_type_override=None, question_id=None):
    return {
        "question_id": question_id,
        "status": "no_speech",
        "raw_transcript": "",
        "normalized_transcript": "",
        "normalization_log": [],
        "word_timestamps": [],
        "vad_features": {"segments": [], "total_speech_duration_ms": 0.0, "threshold": 0.5},
        "avg_logprob": None,
        "pre_answer_latency_sec": None,
    }


def _fake_transcribe_too_short(audio_path, config, device_override=None, compute_type_override=None, question_id=None):
    return {
        "question_id": question_id,
        "status": "too_short",
        "raw_transcript": "",
        "normalized_transcript": "",
        "normalization_log": [],
        "word_timestamps": [],
        "vad_features": {"segments": [{"start_ms": 0.0, "end_ms": 100.0}], "total_speech_duration_ms": 100.0, "threshold": 0.5},
        "avg_logprob": None,
        "pre_answer_latency_sec": 0.0,
    }


def _fake_transcribe_raises(*args, **kwargs):
    raise ASRError("simulated ASR failure for smoke test")


def _fake_decompose_ok(asr_text: str) -> DecompositionResult:
    return DecompositionResult(source_text=asr_text, claims=list(FAKE_CLAIMS))


def _fake_decompose_raises(asr_text: str) -> DecompositionResult:
    raise LLMDecompositionError("simulated Groq failure for smoke test")


def _exploding_decompose(asr_text: str) -> DecompositionResult:
    raise AssertionError("decompose_fn must not be called when ASR did not reach status='ok'")


@pytest.fixture()
def cfg() -> Config:
    return Config(configs_dir=CONFIGS_DIR)


@pytest.fixture()
def document():
    refdocs = load_reference_docs(REFDOCS_MINI)
    return refdocs.get_document("ZZ-001")


# ── full wiring / SUCCESS shape ──────────────────────────────────────────────


def test_evaluate_answer_success_full_dict_shape(cfg: Config, document) -> None:
    vocab_texts = FAKE_CLAIMS + [c.text for c in document.chunks]
    model, tokenizer = _build_tiny_model_and_tokenizer(vocab_texts)

    result = evaluate_answer(
        audio_path="fixture_audio.wav",
        question=document.question,
        reference_chunks=document.chunks,
        key_points=document.key_points,
        config=cfg,
        question_id="ZZ-001",
        nli_model=model,
        nli_tokenizer=tokenizer,
        transcribe_fn=_fake_transcribe_ok,
        decompose_fn=_fake_decompose_ok,
    )

    assert result["status"] == "SUCCESS"
    assert result["error"] is None
    assert result["question_id"] == "ZZ-001"
    assert result["asr"]["status"] == "ok"
    assert result["asr"]["raw_transcript"] == "raw fixture transcript"
    assert result["claims"] == FAKE_CLAIMS

    models_used = result["models_used"]
    assert models_used["asr_checkpoint"] == cfg.asr_model
    assert models_used["decomposition_model"] is not None or models_used["decomposition_model"] is None  # env-dependent, just present
    assert "decomposition_model" in models_used
    assert models_used["nli_base_model"] == cfg.nli_model
    assert models_used["nli_adapter_path"] is None

    assert len(result["claim_scores"]) == 2
    for cs in result["claim_scores"]:
        assert cs["best_chunk_id"] in {c.chunk_id for c in document.chunks}
        assert 0.0 <= cs["max_e"] <= 1.0
        assert 0.0 <= cs["max_c"] <= 1.0
        assert cs["verdict"] in {"VERIFIED", "CONTRADICTED", "NEUTRAL"}

    assert result["key_point_chunk_ids"] == list(document.key_points)
    assert len(result["max_e_per_keypoint"]) == len(document.key_points)
    assert isinstance(result["precision"], float)
    assert isinstance(result["coverage"], float)
    assert isinstance(result["harmonic_f"], float)
    assert isinstance(result["score"], float)
    assert result["score"] == result["harmonic_f"] * cfg.scoring["combination"]["score_scale"]


def test_evaluate_answer_empty_claims_still_scores(cfg: Config, document) -> None:
    """NO_EXTRACTABLE_CLAIMS (claims == []) must flow through to SUCCESS with
    precision=coverage=0.0, not be treated as a pipeline failure."""
    model, tokenizer = _build_tiny_model_and_tokenizer([c.text for c in document.chunks])

    def _fake_decompose_empty(asr_text: str) -> DecompositionResult:
        return DecompositionResult(source_text=asr_text, claims=[])

    result = evaluate_answer(
        audio_path="fixture_audio.wav",
        question=document.question,
        reference_chunks=document.chunks,
        key_points=document.key_points,
        config=cfg,
        nli_model=model,
        nli_tokenizer=tokenizer,
        transcribe_fn=_fake_transcribe_ok,
        decompose_fn=_fake_decompose_empty,
    )

    assert result["status"] == "SUCCESS"
    assert result["claims"] == []
    assert result["claim_scores"] == []
    assert result["precision"] == 0.0


# ── ASR failure modes ────────────────────────────────────────────────────────


def test_evaluate_answer_asr_failed(cfg: Config, document) -> None:
    result = evaluate_answer(
        audio_path="fixture_audio.wav",
        question=document.question,
        reference_chunks=document.chunks,
        key_points=document.key_points,
        config=cfg,
        transcribe_fn=_fake_transcribe_raises,
        decompose_fn=_exploding_decompose,
    )
    assert result["status"] == "ASR_FAILED"
    assert "ASRError" in result["error"]
    assert result["claims"] is None
    assert result["precision"] is None


def test_evaluate_answer_asr_no_speech_stops_pipeline(cfg: Config, document) -> None:
    result = evaluate_answer(
        audio_path="fixture_audio.wav",
        question=document.question,
        reference_chunks=document.chunks,
        key_points=document.key_points,
        config=cfg,
        transcribe_fn=_fake_transcribe_no_speech,
        decompose_fn=_exploding_decompose,
    )
    assert result["status"] == "ASR_NO_SPEECH"
    assert result["asr"]["status"] == "no_speech"
    assert result["claims"] is None


def test_evaluate_answer_asr_too_short_stops_pipeline(cfg: Config, document) -> None:
    result = evaluate_answer(
        audio_path="fixture_audio.wav",
        question=document.question,
        reference_chunks=document.chunks,
        key_points=document.key_points,
        config=cfg,
        transcribe_fn=_fake_transcribe_too_short,
        decompose_fn=_exploding_decompose,
    )
    assert result["status"] == "ASR_TOO_SHORT"
    assert result["asr"]["status"] == "too_short"
    assert result["claims"] is None


# ── decomposition failure ────────────────────────────────────────────────────


def test_evaluate_answer_decomposition_failed(cfg: Config, document) -> None:
    result = evaluate_answer(
        audio_path="fixture_audio.wav",
        question=document.question,
        reference_chunks=document.chunks,
        key_points=document.key_points,
        config=cfg,
        transcribe_fn=_fake_transcribe_ok,
        decompose_fn=_fake_decompose_raises,
    )
    assert result["status"] == "DECOMPOSITION_FAILED"
    assert "simulated Groq failure" in result["decomposition_error"]
    assert "LLMDecompositionError" in result["error"]
    assert result["claims"] is None
    assert result["precision"] is None


# ── NLI failure ───────────────────────────────────────────────────────────────


def test_evaluate_answer_nli_failed_on_dangling_key_point(cfg: Config, document) -> None:
    """An invalid key_point chunk_id (not present in reference_chunks) must
    surface as NLI_FAILED, not crash the caller -- scoring.metrics.resolve_key_point_chunks
    raises DanglingKeyPointError for exactly this case."""
    model, tokenizer = _build_tiny_model_and_tokenizer([c.text for c in document.chunks] + FAKE_CLAIMS)

    result = evaluate_answer(
        audio_path="fixture_audio.wav",
        question=document.question,
        reference_chunks=document.chunks,
        key_points=["NONEXISTENT-CHUNK-ID"],
        config=cfg,
        nli_model=model,
        nli_tokenizer=tokenizer,
        transcribe_fn=_fake_transcribe_ok,
        decompose_fn=_fake_decompose_ok,
    )
    assert result["status"] == "NLI_FAILED"
    assert "DanglingKeyPointError" in result["error"]
    assert result["claims"] == FAKE_CLAIMS  # decomposition itself succeeded


# ── device_override plumbed through to transcribe_fn ────────────────────────


def test_evaluate_answer_passes_device_override_to_transcribe_fn(cfg: Config, document) -> None:
    captured = {}

    def _capturing_transcribe(audio_path, config, device_override=None, compute_type_override=None, question_id=None):
        captured["device_override"] = device_override
        captured["compute_type_override"] = compute_type_override
        return _fake_transcribe_ok(audio_path, config, device_override, compute_type_override, question_id)

    model, tokenizer = _build_tiny_model_and_tokenizer([c.text for c in document.chunks] + FAKE_CLAIMS)

    evaluate_answer(
        audio_path="fixture_audio.wav",
        question=document.question,
        reference_chunks=document.chunks,
        key_points=document.key_points,
        config=cfg,
        device_override="cuda",
        compute_type_override="float16",
        nli_model=model,
        nli_tokenizer=tokenizer,
        transcribe_fn=_capturing_transcribe,
        decompose_fn=_fake_decompose_ok,
    )

    assert captured["device_override"] == "cuda"
    assert captured["compute_type_override"] == "float16"
    # Original config baseline must remain untouched.
    assert cfg.asr["model"]["device"] == "cpu"
    assert cfg.asr["model"]["compute_type"] == "int8"
