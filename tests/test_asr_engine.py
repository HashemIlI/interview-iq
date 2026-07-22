"""
tests/test_asr_engine.py — Phase 7 asr/engine.py smoke tests.

faster-whisper's WhisperModel is never constructed or imported here — a fake
WhisperBackend is injected. Silero VAD is never touched — a fake VadBackend
is injected. Zero network, zero real models.

Run with:  pytest tests/test_asr_engine.py -v
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pytest

from interview_iq.asr.engine import ASRError, transcribe_audio
from interview_iq.config import Config

CONFIGS_DIR = Path(__file__).parent.parent / "configs"


@pytest.fixture(scope="module")
def cfg() -> Config:
    return Config(configs_dir=CONFIGS_DIR)


@pytest.fixture()
def audio_path(tmp_path: Path) -> Path:
    p = tmp_path / "answer.wav"
    p.write_bytes(b"fake wav bytes")
    return p


# ── fakes ────────────────────────────────────────────────────────────────────


@dataclass
class _FakeWord:
    word: str
    start: float
    end: float


@dataclass
class _FakeSegment:
    text: str
    avg_logprob: float
    words: list[_FakeWord] = field(default_factory=list)


class _FakeWhisperBackend:
    def __init__(self, segments: list[_FakeSegment]) -> None:
        self._segments = segments
        self.called = False

    def transcribe(self, audio_path: str, language: str):  # noqa: ANN001
        self.called = True
        return iter(self._segments), object()


class _ExplodingWhisperBackend:
    """Fails the test loudly if transcribe_audio ever calls it on a
    non-'ok' VAD status -- proves the VAD-before-ASR gate actually skips
    the expensive Whisper call, per configs/asr.yaml's own documented
    pipeline order."""

    def transcribe(self, audio_path: str, language: str):  # noqa: ANN001
        raise AssertionError("Whisper backend must not be called when VAD status != 'ok'")


class _FakeVadBackend:
    def __init__(self, timestamps: list[dict[str, int]]) -> None:
        self._timestamps = timestamps

    def get_speech_timestamps(self, audio_path, sampling_rate, threshold, max_speech_duration_s):  # noqa: ANN001
        return self._timestamps


_OK_VAD_TIMESTAMPS = [{"start": 3200, "end": 24000}]  # 200ms -> 1500ms at 16kHz


# ── Format Spec v1.1 field order ─────────────────────────────────────────────


def test_transcribe_audio_returns_fields_in_config_canonical_order(cfg: Config, audio_path: Path) -> None:
    segments = [_FakeSegment(text="hello ", avg_logprob=-0.1, words=[_FakeWord("hello", 0.0, 0.5)])]
    record = transcribe_audio(
        audio_path,
        config=cfg,
        question_id="DA-001",
        whisper_backend=_FakeWhisperBackend(segments),
        vad_backend=_FakeVadBackend(_OK_VAD_TIMESTAMPS),
    )
    assert list(record.keys()) == list(cfg.asr["output"]["fields"])


def test_transcribe_audio_fields_match_config_exactly(cfg: Config, audio_path: Path) -> None:
    expected_fields = [
        "question_id", "status", "raw_transcript", "normalized_transcript",
        "normalization_log", "word_timestamps", "vad_features", "avg_logprob",
        "pre_answer_latency_sec",
    ]
    assert cfg.asr["output"]["fields"] == expected_fields
    segments = [_FakeSegment(text="hello", avg_logprob=-0.1)]
    record = transcribe_audio(
        audio_path, config=cfg, whisper_backend=_FakeWhisperBackend(segments), vad_backend=_FakeVadBackend(_OK_VAD_TIMESTAMPS)
    )
    assert list(record.keys()) == expected_fields


# ── status handling ──────────────────────────────────────────────────────────


def test_status_ok_runs_whisper_and_fills_transcript(cfg: Config, audio_path: Path) -> None:
    segments = [
        _FakeSegment(text="hello ", avg_logprob=-0.2, words=[_FakeWord("hello", 0.2, 0.5)]),
        _FakeSegment(text="world", avg_logprob=-0.4, words=[_FakeWord("world", 0.6, 0.9)]),
    ]
    backend = _FakeWhisperBackend(segments)
    record = transcribe_audio(
        audio_path, config=cfg, question_id="DA-001", whisper_backend=backend, vad_backend=_FakeVadBackend(_OK_VAD_TIMESTAMPS)
    )

    assert backend.called is True
    assert record["status"] == "ok"
    assert record["question_id"] == "DA-001"
    assert record["raw_transcript"] == "hello world"
    # No normalization rule is implemented yet -- normalized == raw, log empty (honest placeholder).
    assert record["normalized_transcript"] == record["raw_transcript"]
    assert record["normalization_log"] == []
    assert record["avg_logprob"] == pytest.approx((-0.2 + -0.4) / 2)
    assert len(record["word_timestamps"]) == 2
    assert record["word_timestamps"][0] == {"word": "hello", "start": 0.2, "end": 0.5}
    assert record["vad_features"]["segments"] == [{"start_ms": 200.0, "end_ms": 1500.0}]
    # pre_answer_latency_sec = first VAD speech segment's start, in seconds.
    assert record["pre_answer_latency_sec"] == 0.2


def test_status_no_speech_skips_whisper_entirely(cfg: Config, audio_path: Path) -> None:
    record = transcribe_audio(
        audio_path, config=cfg, whisper_backend=_ExplodingWhisperBackend(), vad_backend=_FakeVadBackend([])
    )
    assert record["status"] == "no_speech"
    assert record["raw_transcript"] == ""
    assert record["normalized_transcript"] == ""
    assert record["normalization_log"] == []
    assert record["word_timestamps"] == []
    assert record["avg_logprob"] is None
    assert record["pre_answer_latency_sec"] is None


def test_status_too_short_skips_whisper_entirely(cfg: Config, audio_path: Path) -> None:
    # 100ms total speech -- below configs/asr.yaml's min_speech_duration_ms (500).
    short_timestamps = [{"start": 0, "end": 1600}]
    record = transcribe_audio(
        audio_path, config=cfg, whisper_backend=_ExplodingWhisperBackend(), vad_backend=_FakeVadBackend(short_timestamps)
    )
    assert record["status"] == "too_short"
    assert record["raw_transcript"] == ""
    assert record["avg_logprob"] is None
    # too_short still has a first detected segment, unlike no_speech.
    assert record["pre_answer_latency_sec"] == 0.0


def test_missing_audio_file_raises_asr_error(cfg: Config, tmp_path: Path) -> None:
    missing = tmp_path / "does_not_exist.wav"
    with pytest.raises(ASRError, match="not found"):
        transcribe_audio(missing, config=cfg, vad_backend=_FakeVadBackend(_OK_VAD_TIMESTAMPS))


def test_whisper_backend_crash_raises_asr_error(cfg: Config, audio_path: Path) -> None:
    class _CrashingBackend:
        def transcribe(self, audio_path, language):  # noqa: ANN001
            raise RuntimeError("simulated faster-whisper crash")

    with pytest.raises(ASRError, match="transcription failed"):
        transcribe_audio(
            audio_path, config=cfg, whisper_backend=_CrashingBackend(), vad_backend=_FakeVadBackend(_OK_VAD_TIMESTAMPS)
        )


# ── device/compute_type override does not mutate config ─────────────────────


def test_device_override_does_not_mutate_config(cfg: Config, audio_path: Path) -> None:
    original_device = cfg.asr["model"]["device"]
    original_compute_type = cfg.asr["model"]["compute_type"]
    assert original_device == "cpu"
    assert original_compute_type == "int8"

    segments = [_FakeSegment(text="hello", avg_logprob=-0.1)]
    transcribe_audio(
        audio_path,
        config=cfg,
        device_override="cuda",
        compute_type_override="float16",
        whisper_backend=_FakeWhisperBackend(segments),
        vad_backend=_FakeVadBackend(_OK_VAD_TIMESTAMPS),
    )

    assert cfg.asr["model"]["device"] == original_device == "cpu"
    assert cfg.asr["model"]["compute_type"] == original_compute_type == "int8"


def test_no_override_uses_config_baseline(cfg: Config, audio_path: Path) -> None:
    """Without an override, the config's own CPU/int8 baseline must be what
    would be passed to FasterWhisperBackend (verified indirectly: a fresh
    Config still reports the registered baseline after a call with no
    override, and no exception was raised needing device/compute_type)."""
    segments = [_FakeSegment(text="hello", avg_logprob=-0.1)]
    transcribe_audio(
        audio_path, config=cfg, whisper_backend=_FakeWhisperBackend(segments), vad_backend=_FakeVadBackend(_OK_VAD_TIMESTAMPS)
    )
    assert cfg.asr["model"]["device"] == "cpu"
    assert cfg.asr["model"]["compute_type"] == "int8"
