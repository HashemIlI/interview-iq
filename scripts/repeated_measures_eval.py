"""
scripts/repeated_measures_eval.py — D112 measurement instrument
(decisions.md D112, pending registration).

Purpose: measure run-to-run variability of the end-to-end score on the same
audio, holding ASR fixed. Trigger: two consecutive end-to-end runs on
identical SE-028 audio (same commit family, same model, same thresholds,
same glossary state) produced Precision 0.6672/score 56.1487 versus
Precision 0.4006/score 42.8495 -- a 24 percent difference attributable to
decomposition variability alone (a merged-claim atomicity violation on the
second run). This script re-runs the full production pipeline n times per
question on a SINGLE cached transcript, so any variation in the output is
attributable to decomposition and scoring, never to ASR.

Reuse, not reimplementation: pipeline.evaluate_answer has no dedicated
"pass a pre-computed transcript" parameter, but it already accepts an
injectable `transcribe_fn` callable (pipeline.py's own module docstring:
"Injection points for tests ... and for callers who already hold a loaded
model/tokenizer across many calls"). This script uses exactly that
mechanism instead of calling asr.engine.transcribe_audio,
decomposition_llm.client.decompose_via_llm, apply_glossary,
retrieval.chunk_cap.select_top_k_chunks, nli.engine.build_claims_chunks_matrix
/build_coverage_matrix or scoring.metrics.compute_scoring_result directly:
    1. Run 0 for a question calls evaluate_answer with its DEFAULT
       transcribe_fn (the real asr.engine.transcribe_audio) -- this is the
       one and only real transcription per question.
    2. That call's result["asr"] (the full Format Spec v1.1 record) is
       captured and wrapped in a trivial closure that ignores its arguments
       and returns that SAME cached dict.
    3. Runs 1..n-1 call evaluate_answer with transcribe_fn set to that
       closure -- every pipeline stage after ASR (decomposition, glossary,
       chunk cap, NLI, scoring) still runs for real and unmodified; only the
       transcription step is skipped in favour of the cached result.
No production function is reimplemented anywhere in this file. decompose_fn
is left at its default (decompose_via_llm) on every run, since real
decomposition variability across repeated calls is exactly what is being
measured.

Aggregation (mean/min/max/range across n runs) is plain arithmetic over
already-computed production outputs -- not a reimplementation of
precision_channel/coverage_channel/harmonic_f/compute_scoring_result, all of
which are called once per run, inside evaluate_answer, unmodified.

Usage:
    python scripts/repeated_measures_eval.py \\
        --audio-path data/pilot_audio/SE-028.wav --question-id SE-028 \\
        --audio-path data/pilot_audio/GN-040.wav --question-id GN-040 \\
        --n-runs 5

Output:
    results/repeated_measures/run_<UTC timestamp>/
        raw_results.json   -- full machine-readable output per question/run
        report.md            -- human-readable per-run table + aggregates

Reference: D106 (openai/gpt-oss-120b free-tier pacing constraint motivating
--inter-call-delay and the checkpoint), D110 (same-chunk contradiction rule,
already the production default this script measures against), D111
(glossary state as of the بيت reclassification), D112 (this measurement's
own pending pre-registration; outcome registered separately as D113).
"""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_REFERENCE_DOCS_PATH = _REPO_ROOT / "data" / "refdocs" / "reference_docs_250_FINAL_v1.json"
_DEFAULT_OUTPUT_ROOT = _REPO_ROOT / "results" / "repeated_measures"

sys.path.insert(0, str(_REPO_ROOT / "src"))

from interview_iq.config import Config  # noqa: E402
from interview_iq.decomposition_llm.client import GROQ_MODEL  # noqa: E402
from interview_iq.evaluation.gold_eval import build_pretrained_model_and_tokenizer, load_adapter  # noqa: E402
from interview_iq.pipeline import evaluate_answer  # noqa: E402
from interview_iq.refdocs.loader import load_reference_docs  # noqa: E402

_METRICS = ("claim_count", "precision", "coverage", "harmonic_f", "score")


def _get_git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=_REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        )
        return result.stdout.strip()
    except Exception as exc:  # noqa: BLE001 -- diagnostic logging only, must not crash the run
        return f"UNAVAILABLE ({exc})"


def _fixed_transcript_fn(asr_record: dict[str, Any]):
    """Returns a transcribe_fn-compatible closure that ignores every
    argument evaluate_answer passes it and returns the SAME cached ASR
    record every time -- see module docstring."""

    def _inner(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
        return asr_record

    return _inner


def run_repeated_measures_for_question(
    audio_path: Path,
    question_id: str,
    document: Any,
    cfg: Config,
    nli_model: Any,
    nli_tokenizer: Any,
    adapter_path: Path | None,
    n_runs: int,
    inter_call_delay: float,
    checkpoint: dict[str, Any],
    checkpoint_path: Path,
) -> dict[str, Any]:
    """Runs n_runs of evaluate_answer for one question, ASR executed only
    once (run 0, or recovered from checkpoint), and writes the checkpoint
    after every single run."""
    q_checkpoint = checkpoint.setdefault(question_id, {})

    asr_record: dict[str, Any] | None = None
    if "0" in q_checkpoint:
        asr_record = q_checkpoint["0"]["asr"]

    run_records: list[dict[str, Any]] = []
    for run_index in range(n_runs):
        key = str(run_index)
        if key in q_checkpoint:
            print(f"    run {run_index}: RESUMED from checkpoint")
            record = q_checkpoint[key]
        else:
            if run_index == 0:
                # The one and only real transcription for this question.
                result = evaluate_answer(
                    audio_path=str(audio_path),
                    question=document.question,
                    reference_chunks=document.chunks,
                    key_points=document.key_points,
                    config=cfg,
                    question_id=question_id,
                    nli_model=nli_model,
                    nli_tokenizer=nli_tokenizer,
                    adapter_path=adapter_path,
                )
                asr_record = result["asr"]
            else:
                if asr_record is None:
                    raise RuntimeError(
                        f"{question_id}: run {run_index} requested before run 0's transcript "
                        "was established -- run 0 must complete (or be present in the "
                        "checkpoint) first."
                    )
                result = evaluate_answer(
                    audio_path=str(audio_path),
                    question=document.question,
                    reference_chunks=document.chunks,
                    key_points=document.key_points,
                    config=cfg,
                    question_id=question_id,
                    nli_model=nli_model,
                    nli_tokenizer=nli_tokenizer,
                    adapter_path=adapter_path,
                    transcribe_fn=_fixed_transcript_fn(asr_record),
                )
            record = {
                "run_index": run_index,
                "status": result["status"],
                "error": result["error"],
                "claims_raw": result["claims_raw"],
                "claims": result["claims"],
                "transliteration_audit": result["transliteration_audit"],
                "claim_scores": result["claim_scores"],
                "precision": result["precision"],
                "coverage": result["coverage"],
                "harmonic_f": result["harmonic_f"],
                "score": result["score"],
                "asr": result["asr"],
            }
            print(
                f"    run {run_index}: status={record['status']} "
                f"n_claims={len(record['claims']) if record['claims'] is not None else None} "
                f"score={record['score']}"
            )
            q_checkpoint[key] = record
            checkpoint_path.write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2), encoding="utf-8")
            if run_index < n_runs - 1:
                time.sleep(inter_call_delay)
        run_records.append(record)

    successful = [r for r in run_records if r["status"] == "SUCCESS"]
    aggregates: dict[str, dict[str, float | None]] = {}
    for metric in _METRICS:
        if metric == "claim_count":
            values = [len(r["claims"]) for r in successful if r["claims"] is not None]
        else:
            values = [r[metric] for r in successful if r[metric] is not None]
        if values:
            aggregates[metric] = {
                "mean": statistics.mean(values),
                "min": min(values),
                "max": max(values),
                "range": max(values) - min(values),
                "stdev": statistics.stdev(values) if len(values) > 1 else 0.0,
                "n": len(values),
            }
        else:
            aggregates[metric] = {"mean": None, "min": None, "max": None, "range": None, "stdev": None, "n": 0}

    return {
        "question_id": question_id,
        "audio_path": str(audio_path),
        "transcript": asr_record["normalized_transcript"] if asr_record else None,
        "asr_status": asr_record["status"] if asr_record else None,
        "runs": run_records,
        "aggregates": aggregates,
    }


def _write_report_md(question_results: list[dict[str, Any]], report_path: Path, meta: dict[str, Any]) -> None:
    lines = [
        "# D112 Repeated-Measures Evaluation — Report",
        "",
        f"- Run timestamp (UTC): {meta['run_timestamp_utc']}",
        f"- Git commit at run time: `{meta['git_commit']}`",
        f"- Decomposition model: `{meta['decomposition_model']}`",
        f"- NLI base model: `{meta['nli_base_model']}`",
        f"- Adapter path: `{meta['adapter_path']}`" if meta["adapter_path"] else "- Adapter path: none (zero-shot)",
        f"- Thresholds: tau={meta['thresholds']['tau']}, tau_e={meta['thresholds']['tau_e']}, "
        f"alpha={meta['thresholds']['alpha']}, k={meta['thresholds']['k']}",
        f"- n_runs: {meta['n_runs']}, inter_call_delay: {meta['inter_call_delay']}s",
        "",
    ]

    for q in question_results:
        lines.append(f"## {q['question_id']} ({q['audio_path']})")
        lines.append("")
        lines.append(f"Transcript (ASR run once, status={q['asr_status']}):")
        lines.append(f"> {q['transcript']}")
        lines.append("")
        lines.append("| run_index | claim_count | precision | coverage | harmonic_f | score |")
        lines.append("|---|---|---|---|---|---|")
        for r in q["runs"]:
            n_claims = len(r["claims"]) if r["claims"] is not None else None
            lines.append(
                f"| {r['run_index']} | {n_claims} | {r['precision']} | {r['coverage']} | "
                f"{r['harmonic_f']} | {r['score']} |"
            )
        lines.append("")
        lines.append("| metric | mean | min | max | range | stdev (descriptive only, n=5) |")
        lines.append("|---|---|---|---|---|---|")
        for metric in _METRICS:
            agg = q["aggregates"][metric]
            lines.append(
                f"| {metric} | {agg['mean']} | {agg['min']} | {agg['max']} | {agg['range']} | {agg['stdev']} |"
            )
        lines.append("")
        lines.append("Claims per run (atomicity inspection):")
        for r in q["runs"]:
            lines.append(f"- run {r['run_index']} ({r['status']}):")
            if r["claims"]:
                for i, claim in enumerate(r["claims"], 1):
                    lines.append(f"  {i}. {claim}")
            else:
                lines.append("  (none)")
        lines.append("")

    if len(question_results) == 2:
        a, b = question_results
        a_scores = a["aggregates"]["score"]
        b_scores = b["aggregates"]["score"]
        lines.append("## Separation criterion (D112)")
        lines.append("")
        lines.append(f"- {a['question_id']} score: mean={a_scores['mean']}, range=[{a_scores['min']}, {a_scores['max']}]")
        lines.append(f"- {b['question_id']} score: mean={b_scores['mean']}, range=[{b_scores['min']}, {b_scores['max']}]")
        if a_scores["mean"] is not None and b_scores["mean"] is not None:
            higher = a if a_scores["mean"] >= b_scores["mean"] else b
            ranges_overlap = not (a_scores["max"] < b_scores["min"] or b_scores["max"] < a_scores["min"])
            lines.append(f"- Higher mean score: {higher['question_id']}")
            lines.append(f"- Ranges overlap: {ranges_overlap}")
        lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "D112: repeated-measures evaluation of run-to-run variability in the "
            "end-to-end score, ASR held fixed per question."
        )
    )
    parser.add_argument(
        "--audio-path",
        type=Path,
        action="append",
        required=True,
        help="Path to an answer-segment audio file (repeatable, paired positionally with --question-id).",
    )
    parser.add_argument(
        "--question-id",
        type=str,
        action="append",
        required=True,
        help="Question ID for the corresponding --audio-path (repeatable, same order/count as --audio-path).",
    )
    parser.add_argument("--n-runs", type=int, default=5)
    parser.add_argument("--inter-call-delay", type=float, default=20.0)
    parser.add_argument("--reference-docs-path", type=Path, default=_DEFAULT_REFERENCE_DOCS_PATH)
    parser.add_argument("--adapter-path", type=Path, default=None)
    parser.add_argument("--checkpoint-path", type=Path, default=None)
    parser.add_argument("--output-path", type=Path, default=None)
    args = parser.parse_args(argv)

    if len(args.audio_path) != len(args.question_id):
        raise ValueError(
            f"--audio-path was given {len(args.audio_path)} time(s) but --question-id "
            f"{len(args.question_id)} time(s) -- they are paired positionally and must match."
        )

    run_timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = args.output_path or (_DEFAULT_OUTPUT_ROOT / f"run_{run_timestamp}" / "raw_results.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_path = args.checkpoint_path or (_DEFAULT_OUTPUT_ROOT / "checkpoint.json")

    cfg = Config()
    print(f"[D112] NLI base model: {cfg.nli_model}")
    print(f"[D112] Loading reference docs: {args.reference_docs_path}")
    refdocs = load_reference_docs(args.reference_docs_path)

    print("[D112] Building NLI model (zero-shot base)...")
    nli_model, nli_tokenizer = build_pretrained_model_and_tokenizer(cfg.nli_model)
    if args.adapter_path is not None:
        print(f"[D112] Loading adapter: {args.adapter_path}")
        nli_model = load_adapter(nli_model, args.adapter_path)
    else:
        print("[D112] No --adapter-path given: zero-shot only (D89/D109).")

    checkpoint: dict[str, Any] = {}
    if checkpoint_path.exists():
        checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        print(f"[D112] Loaded checkpoint from {checkpoint_path} ({len(checkpoint)} question(s) present)")

    question_results = []
    for audio_path, question_id in zip(args.audio_path, args.question_id):
        document = refdocs.get_document(question_id)
        if document is None:
            raise ValueError(f"question_id {question_id!r} not found in {args.reference_docs_path}")
        print(f"[D112] {question_id}: {args.n_runs} run(s) on {audio_path}")
        q_result = run_repeated_measures_for_question(
            audio_path=audio_path,
            question_id=question_id,
            document=document,
            cfg=cfg,
            nli_model=nli_model,
            nli_tokenizer=nli_tokenizer,
            adapter_path=args.adapter_path,
            n_runs=args.n_runs,
            inter_call_delay=args.inter_call_delay,
            checkpoint=checkpoint,
            checkpoint_path=checkpoint_path,
        )
        question_results.append(q_result)

    meta = {
        "run_timestamp_utc": run_timestamp,
        "git_commit": _get_git_commit(),
        "decomposition_model": GROQ_MODEL,
        "nli_base_model": cfg.nli_model,
        "adapter_path": str(args.adapter_path) if args.adapter_path is not None else None,
        "thresholds": {"tau": cfg.tau, "tau_e": cfg.tau_e, "alpha": cfg.alpha, "k": cfg.k},
        "n_runs": args.n_runs,
        "inter_call_delay": args.inter_call_delay,
        "reference_docs_path": str(args.reference_docs_path),
        "checkpoint_path": str(checkpoint_path),
        "question_ids": args.question_id,
        "audio_paths": [str(p) for p in args.audio_path],
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "questions": question_results}, f, ensure_ascii=False, indent=2)
    print(f"[D112] raw_results.json written to: {output_path}")

    report_path = output_path.parent / "report.md"
    _write_report_md(question_results, report_path, meta)
    print(f"[D112] report.md written to: {report_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
