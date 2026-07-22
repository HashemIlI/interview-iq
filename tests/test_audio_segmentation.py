"""
tests/test_audio_segmentation.py — Phase 7 audio/segmentation.py smoke tests.

extract_audio: ffmpeg's subprocess.run call is monkeypatched — no real
ffmpeg binary is ever invoked. run_vad: a fake VadBackend is injected — no
torch.hub download or real Silero VAD model is ever touched.

Run with:  pytest tests/test_audio_segmentation.py -v
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from interview_iq.audio.segmentation import (
    AudioSegmentationError,
    VadResult,
    extract_audio,
    run_vad,
)
from interview_iq.config import Config

CONFIGS_DIR = Path(__file__).parent.parent / "configs"


@pytest.fixture(scope="module")
def cfg() -> Config:
    return Config(configs_dir=CONFIGS_DIR)


# ── extract_audio ────────────────────────────────────────────────────────────


class _FakeCompletedProcess:
    def __init__(self, returncode: int, stderr: str = "") -> None:
        self.returncode = returncode
        self.stderr = stderr


def test_extract_audio_raises_if_video_missing(tmp_path: Path) -> None:
    with pytest.raises(AudioSegmentationError, match="not found"):
        extract_audio(tmp_path / "missing.mp4", tmp_path / "out.wav")


def test_extract_audio_builds_expected_ffmpeg_argv(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    video_path = tmp_path / "input.mp4"
    video_path.write_bytes(b"fake video bytes")
    output_path = tmp_path / "out.wav"

    captured_cmd: list[str] = []

    def _fake_run(cmd, capture_output, text, check):  # noqa: ANN001 - test double
        captured_cmd.extend(cmd)
        output_path.write_bytes(b"fake wav bytes")  # simulate ffmpeg producing output
        return _FakeCompletedProcess(returncode=0)

    monkeypatch.setattr(subprocess, "run", _fake_run)

    result = extract_audio(video_path, output_path)

    assert result == output_path
    assert captured_cmd[0] == "ffmpeg"
    assert "-i" in captured_cmd and str(video_path) in captured_cmd
    assert "-ac" in captured_cmd and "1" in captured_cmd  # mono
    assert "-ar" in captured_cmd and "16000" in captured_cmd  # 16kHz
    assert str(output_path) in captured_cmd
    assert "shell" not in captured_cmd  # no shell=True anywhere in the design


def test_extract_audio_raises_on_nonzero_exit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    video_path = tmp_path / "input.mp4"
    video_path.write_bytes(b"fake video bytes")
    output_path = tmp_path / "out.wav"

    def _fake_run(cmd, capture_output, text, check):  # noqa: ANN001 - test double
        return _FakeCompletedProcess(returncode=1, stderr="ffmpeg: invalid data")

    monkeypatch.setattr(subprocess, "run", _fake_run)

    with pytest.raises(AudioSegmentationError, match="ffmpeg extraction failed"):
        extract_audio(video_path, output_path)


def test_extract_audio_raises_if_ffmpeg_not_found(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    video_path = tmp_path / "input.mp4"
    video_path.write_bytes(b"fake video bytes")
    output_path = tmp_path / "out.wav"

    def _fake_run(*args, **kwargs):  # noqa: ANN002, ANN003 - test double
        raise FileNotFoundError("ffmpeg")

    monkeypatch.setattr(subprocess, "run", _fake_run)

    with pytest.raises(AudioSegmentationError, match="ffmpeg executable not found"):
        extract_audio(video_path, output_path)


# ── run_vad ──────────────────────────────────────────────────────────────────


class _FakeVadBackend:
    """Returns whatever fixed timestamp list it was constructed with —
    never touches torch.hub or a real model."""

    def __init__(self, timestamps: list[dict[str, int]]) -> None:
        self._timestamps = timestamps

    def get_speech_timestamps(self, audio_path, sampling_rate, threshold, max_speech_duration_s):  # noqa: ANN001
        return self._timestamps


def test_run_vad_ok_status(cfg: Config, tmp_path: Path) -> None:
    audio_path = tmp_path / "audio.wav"
    audio_path.write_bytes(b"fake wav")
    # 500ms segment starting at 200ms -- above min_speech_duration_ms (500) exactly at boundary,
    # use a duration comfortably above threshold to avoid boundary flakiness.
    timestamps = [{"start": 3200, "end": 24000}]  # 16kHz samples -> 200ms to 1500ms (1300ms speech)
    backend = _FakeVadBackend(timestamps)

    result = run_vad(audio_path, config=cfg, backend=backend)

    assert isinstance(result, VadResult)
    assert result.status == "ok"
    assert result.vad_features["segments"] == [{"start_ms": 200.0, "end_ms": 1500.0}]
    assert result.vad_features["total_speech_duration_ms"] == 1300.0


def test_run_vad_no_speech_status(cfg: Config, tmp_path: Path) -> None:
    audio_path = tmp_path / "audio.wav"
    audio_path.write_bytes(b"fake wav")
    backend = _FakeVadBackend([])

    result = run_vad(audio_path, config=cfg, backend=backend)

    assert result.status == "no_speech"
    assert result.vad_features["segments"] == []
    assert result.vad_features["total_speech_duration_ms"] == 0.0


def test_run_vad_too_short_status(cfg: Config, tmp_path: Path) -> None:
    audio_path = tmp_path / "audio.wav"
    audio_path.write_bytes(b"fake wav")
    # 100ms of speech total -- below configs/asr.yaml's min_speech_duration_ms (500).
    timestamps = [{"start": 0, "end": 1600}]  # 16kHz samples -> 0 to 100ms
    backend = _FakeVadBackend(timestamps)

    result = run_vad(audio_path, config=cfg, backend=backend)

    assert result.status == "too_short"
    assert result.vad_features["total_speech_duration_ms"] == 100.0
