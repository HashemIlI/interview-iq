"""
tests/test_run_pipeline_demo.py — smoke test for scripts/run_pipeline_demo.py.

evaluate_answer is entirely mocked (monkeypatched on the script module) —
no real audio, no real models, no network, no real OpenRouter call. This
verifies only the CLI's own job: resolving question/chunks/key_points from
a reference-docs file and calling evaluate_answer with the right arguments,
plus writing the output JSON and choosing the right exit code.

Never runs against real audio (that is explicitly deferred, per D85/the
pilot-recording task).

Run with:  pytest tests/test_run_pipeline_demo.py -v
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

import run_pipeline_demo  # noqa: E402

FIXTURES_DIR = Path(__file__).parent / "fixtures"
REFDOCS_MINI = FIXTURES_DIR / "refdocs_mini.json"


def _fake_success_result() -> dict:
    return {
        "status": "SUCCESS",
        "error": None,
        "asr": {"status": "ok", "raw_transcript": "raw fixture transcript", "normalized_transcript": "normalized fixture transcript"},
        "claims": ["fixture claim one", "fixture claim two"],
        "precision": 0.5,
        "coverage": 0.75,
        "harmonic_f": 0.6,
        "score": 60.0,
        "models_used": {"asr_checkpoint": "large-v3", "nli_adapter_path": "/fake/adapter"},
    }


def test_main_resolves_question_and_calls_evaluate_answer(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict = {}

    def _fake_evaluate_answer(**kwargs):
        captured.update(kwargs)
        return _fake_success_result()

    monkeypatch.setattr(run_pipeline_demo, "evaluate_answer", _fake_evaluate_answer)

    audio_path = tmp_path / "audio.wav"
    audio_path.write_bytes(b"fake wav bytes")
    output_path = tmp_path / "out.json"
    adapter_path = tmp_path / "adapter"

    exit_code = run_pipeline_demo.main([
        "--audio-path", str(audio_path),
        "--question-id", "ZZ-001",
        "--reference-docs-path", str(REFDOCS_MINI),
        "--adapter-path", str(adapter_path),
        "--output-path", str(output_path),
    ])

    assert exit_code == 0

    # evaluate_answer must have been called with the resolved fixture data.
    assert captured["audio_path"] == str(audio_path)
    assert captured["question_id"] == "ZZ-001"
    assert captured["question"] == "Fixture question one — what is the difference between Recursion and Iteration?"
    assert [c.chunk_id for c in captured["reference_chunks"]] == ["ZZ001-C01", "ZZ001-C02", "ZZ001-C03"]
    assert list(captured["key_points"]) == ["ZZ001-C01", "ZZ001-C02"]
    assert captured["adapter_path"] == adapter_path
    assert captured["device_override"] is None
    assert captured["compute_type_override"] is None

    written = json.loads(output_path.read_text(encoding="utf-8"))
    assert written["status"] == "SUCCESS"
    assert written["claims"] == ["fixture claim one", "fixture claim two"]


def test_main_passes_device_and_compute_type_overrides(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict = {}

    def _fake_evaluate_answer(**kwargs):
        captured.update(kwargs)
        return _fake_success_result()

    monkeypatch.setattr(run_pipeline_demo, "evaluate_answer", _fake_evaluate_answer)

    audio_path = tmp_path / "audio.wav"
    audio_path.write_bytes(b"fake wav bytes")

    run_pipeline_demo.main([
        "--audio-path", str(audio_path),
        "--question-id", "ZZ-002",
        "--reference-docs-path", str(REFDOCS_MINI),
        "--adapter-path", str(tmp_path / "adapter"),
        "--output-path", str(tmp_path / "out.json"),
        "--device", "cuda",
        "--compute-type", "float16",
    ])

    assert captured["device_override"] == "cuda"
    assert captured["compute_type_override"] == "float16"
    assert list(captured["key_points"]) == ["ZZ002-C01"]


def test_main_errors_on_unknown_question_id(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def _exploding_evaluate_answer(**kwargs):
        raise AssertionError("evaluate_answer must not be called for an unknown question_id")

    monkeypatch.setattr(run_pipeline_demo, "evaluate_answer", _exploding_evaluate_answer)

    audio_path = tmp_path / "audio.wav"
    audio_path.write_bytes(b"fake wav bytes")

    with pytest.raises(SystemExit) as exc_info:
        run_pipeline_demo.main([
            "--audio-path", str(audio_path),
            "--question-id", "ZZ-404",
            "--reference-docs-path", str(REFDOCS_MINI),
            "--adapter-path", str(tmp_path / "adapter"),
            "--output-path", str(tmp_path / "out.json"),
        ])
    assert exc_info.value.code == 2


def test_main_returns_nonzero_on_non_success_status(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def _fake_evaluate_answer(**kwargs):
        return {
            "status": "ASR_FAILED",
            "error": "ASRError: simulated failure for smoke test",
            "asr": None,
            "claims": None,
            "precision": None,
            "coverage": None,
            "harmonic_f": None,
            "score": None,
            "models_used": {"asr_checkpoint": "large-v3"},
        }

    monkeypatch.setattr(run_pipeline_demo, "evaluate_answer", _fake_evaluate_answer)

    audio_path = tmp_path / "audio.wav"
    audio_path.write_bytes(b"fake wav bytes")
    output_path = tmp_path / "out.json"

    exit_code = run_pipeline_demo.main([
        "--audio-path", str(audio_path),
        "--question-id", "ZZ-001",
        "--reference-docs-path", str(REFDOCS_MINI),
        "--adapter-path", str(tmp_path / "adapter"),
        "--output-path", str(output_path),
    ])

    assert exit_code == 1
    written = json.loads(output_path.read_text(encoding="utf-8"))
    assert written["status"] == "ASR_FAILED"
