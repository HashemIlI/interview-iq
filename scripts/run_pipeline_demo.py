"""
scripts/run_pipeline_demo.py — Thin CLI: real end-to-end pipeline.evaluate_answer()
run for the pilot recording (D85's ASR module + orchestrator), against real
audio, real faster-whisper, real Groq decomposition, and real NLI
models (zero-shot base + LoRA adapter).

Usage:
    python scripts/run_pipeline_demo.py \\
        --audio-path recordings/SE-028.wav \\
        --question-id SE-028 \\
        --adapter-path /path/to/iq-checkpoints-nli-v1 \\
        --output-path results/pipeline_demo/SE-028.json

This is a thin CLI only — it resolves one question's data from the
reference-docs JSON (reusing refdocs.loader.load_reference_docs /
ReferenceDocs.get_document, never reimplementing that parsing) and calls
pipeline.evaluate_answer() with no injected mocks: the real production path
(build_pretrained_model_and_tokenizer + load_adapter, transcribe_audio,
decompose_via_llm) runs exactly as evaluate_answer's own docstring
describes when its injection points are left at their defaults. All real
logic lives in the package; this script just wires it, matching the
project's thin-runner convention (see cli/run_scoring.py,
scripts/coverage_channel_real_claims_experiment.py).

GROQ_API_KEY is read from `.env` only, via decomposition_llm.client's
existing contract — this script never touches it directly.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_REFERENCE_DOCS_PATH = _REPO_ROOT / "data" / "refdocs" / "reference_docs_250_FINAL_v1.json"

sys.path.insert(0, str(_REPO_ROOT / "src"))

from interview_iq.config import Config  # noqa: E402
from interview_iq.pipeline import evaluate_answer  # noqa: E402
from interview_iq.refdocs.loader import load_reference_docs  # noqa: E402


def _print_summary(result: dict) -> None:
    print(f"\n[run_pipeline_demo] status: {result['status']}")
    if result.get("error"):
        print(f"[run_pipeline_demo] error: {result['error']}")

    asr = result.get("asr")
    if asr is not None:
        print(f"\n[run_pipeline_demo] ASR status: {asr['status']}")
        print(f"[run_pipeline_demo] raw_transcript: {asr['raw_transcript']}")
        print(f"[run_pipeline_demo] normalized_transcript: {asr['normalized_transcript']}")

    claims = result.get("claims")
    if claims is not None:
        print(f"\n[run_pipeline_demo] claims ({len(claims)}):")
        for i, claim in enumerate(claims, 1):
            print(f"  {i}. {claim}")

    if result.get("precision") is not None:
        print(f"\n[run_pipeline_demo] precision:  {result['precision']:.4f}")
        print(f"[run_pipeline_demo] coverage:   {result['coverage']:.4f}")
        print(f"[run_pipeline_demo] harmonic_f: {result['harmonic_f']:.4f}")
        print(f"[run_pipeline_demo] score:      {result['score']:.2f}")

    print(f"\n[run_pipeline_demo] models_used: {json.dumps(result['models_used'], ensure_ascii=False, indent=2)}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Thin CLI: real end-to-end evaluate_answer() run for the pilot recording (D85)."
    )
    parser.add_argument("--audio-path", type=Path, required=True)
    parser.add_argument("--question-id", type=str, required=True, help="e.g. SE-028 or GN-040.")
    parser.add_argument("--reference-docs-path", type=Path, default=_DEFAULT_REFERENCE_DOCS_PATH)
    parser.add_argument("--adapter-path", type=Path, required=True, help="LoRA adapter checkpoint directory.")
    parser.add_argument("--device", type=str, default=None, help="Override configs/asr.yaml's device for this call only.")
    parser.add_argument("--compute-type", type=str, default=None, help="Override configs/asr.yaml's compute_type for this call only.")
    parser.add_argument("--output-path", type=Path, required=True, help="Where to write the full evaluate_answer() result JSON.")
    args = parser.parse_args(argv)

    refdocs = load_reference_docs(args.reference_docs_path)
    document = refdocs.get_document(args.question_id)
    if document is None:
        parser.error(f"question_id {args.question_id!r} not found in {args.reference_docs_path}")
        return 2  # unreachable; parser.error exits, this satisfies type-checkers

    cfg = Config()

    print(f"[run_pipeline_demo] question_id={args.question_id} track={document.track}")
    print(f"[run_pipeline_demo] audio_path={args.audio_path}")
    print(f"[run_pipeline_demo] adapter_path={args.adapter_path}")

    result = evaluate_answer(
        audio_path=str(args.audio_path),
        question=document.question,
        reference_chunks=document.chunks,
        key_points=document.key_points,
        config=cfg,
        device_override=args.device,
        compute_type_override=args.compute_type,
        question_id=args.question_id,
        adapter_path=args.adapter_path,
    )

    _print_summary(result)

    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    with args.output_path.open("w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=2)
    print(f"\n[run_pipeline_demo] Wrote full result to: {args.output_path}")

    return 0 if result["status"] == "SUCCESS" else 1


if __name__ == "__main__":
    sys.exit(main())
