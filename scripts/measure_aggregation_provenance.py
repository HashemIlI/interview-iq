"""
scripts/measure_aggregation_provenance.py — D110 measurement instrument
(decisions.md D110, pending registration).

Purpose: quantify the effect of taking max_c from the SAME chunk that
produced max_e (argmax-entailment), instead of independently maximizing
entailment and contradiction over the whole chunk set, on the claims
already recorded in existing pipeline_demo artifacts. D88 registered that
"max_E/max_C are over one chunk" on the Gold Set but "aggregate over a
Claims x Chunks matrix" in the real path (decisions.md D43) without ever
specifying same-vs-different-chunk provenance for either quantity; D94/D104
are the real-audio pipeline_demo runs this script measures; D108 is the
Coverage-channel baseline re-derivation that reuses the same production
aggregation functions this script also reuses unmodified. This script
measures the same-chunk-vs-independent gap directly rather than assuming it
is small.

Read-only against src/interview_iq/: no production file is modified. Every
number in this script's output comes from unmodified production functions —
build_claims_chunks_matrix, build_coverage_matrix (nli/engine.py),
score_claim (scoring/aggregation.py), and compute_scoring_result
(scoring/metrics.py) — called twice per question: once with the
independently-computed max_c (current production behaviour) and once with
max_c substituted for the contradiction probability at the SAME chunk that
produced max_e. Nothing here reimplements any of that math. Retrieval
capping uses select_top_k_chunks exactly as pipeline.py does (never the
full chunk set directly), so this measurement runs on the production code
path.

Local-CPU note: an attempt at this exact measurement on local CPU (pre-
registration discussion, 2026-07-30) measured roughly 5 minutes per single-
claim forward pass and was abandoned as unusable. This script is the
corresponding Kaggle T4 thin-runner instrument
(kaggle/runners/run-aggregation-provenance.ipynb) — per the standing
Kaggle-T4-for-GPU-work environment decision (D19), it is not intended to be
run locally.

scripts/diag_precision_two_arms.py is NOT reused and NOT modified by this
script: its claims are hardcoded module-level constants frozen from the v1
(pre-glossary) decomposition run, and it scores against the full document
chunk set directly rather than through select_top_k_chunks. It remains D88
evidence, unchanged.

Usage:
    python scripts/measure_aggregation_provenance.py \\
        --results-json results/pipeline_demo/SE-028_v3.json \\
        --results-json results/pipeline_demo/GN-040_v3.json

Output:
    results/aggregation_provenance/run_<UTC timestamp>/
        raw_results.json   -- full machine-readable output per question/claim
        report.md            -- human-readable per-claim comparison tables

Reference: D19 (Kaggle-as-GPU-engine standing environment decision), D43
(registers that max_E/max_C "aggregate over a Claims x Chunks matrix" in the
real path, without specifying chunk provenance), D88 (two-arm Precision
diagnostic whose functions this script reuses), D89/D109 (zero-shot is the
closed runtime arm — this script's default), D94/D104 (the real-audio
pipeline_demo artifacts this measures), D108 (Coverage baseline
re-derivation, same production functions), D110 (this measurement's own
pending pre-registration).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_REFERENCE_DOCS_PATH = _REPO_ROOT / "data" / "refdocs" / "reference_docs_250_FINAL_v1.json"
_DEFAULT_OUTPUT_ROOT = _REPO_ROOT / "results" / "aggregation_provenance"

sys.path.insert(0, str(_REPO_ROOT / "src"))

from interview_iq.config import Config  # noqa: E402
from interview_iq.evaluation.gold_eval import build_pretrained_model_and_tokenizer, load_adapter  # noqa: E402
from interview_iq.nli.engine import build_claims_chunks_matrix, build_coverage_matrix  # noqa: E402
from interview_iq.refdocs.loader import ReferenceDocs, load_reference_docs  # noqa: E402
from interview_iq.retrieval.chunk_cap import select_top_k_chunks  # noqa: E402
from interview_iq.scoring.aggregation import score_claim  # noqa: E402
from interview_iq.scoring.metrics import compute_scoring_result, resolve_key_point_chunks  # noqa: E402


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


def _load_question_id_and_claims(results_json_path: Path) -> tuple[str, list[str]]:
    """Reads question_id and the post-glossary "claims" array from a
    pipeline_demo results JSON. Fails loudly -- no fallback to claims_raw --
    if either key is absent, per this script's explicit registration."""
    data = json.loads(results_json_path.read_text(encoding="utf-8"))
    if "question_id" not in data:
        raise ValueError(f"{results_json_path}: missing required key 'question_id'")
    if "claims" not in data:
        raise ValueError(
            f"{results_json_path}: missing required key 'claims' (post-glossary). "
            "This script does NOT fall back to 'claims_raw' -- if this artifact only "
            "has claims_raw, that is a different (pre-glossary) measurement and must "
            "be requested explicitly against a different artifact, not silently "
            "substituted here."
        )
    return data["question_id"], data["claims"]


def measure_claim(
    claim_index: int,
    claim_text: str,
    document: Any,
    model: Any,
    tokenizer: Any,
    cfg: Config,
) -> dict[str, Any]:
    """One claim's full per-chunk matrix plus both aggregation variants.
    Retrieval cap applied exactly as pipeline.py does (select_top_k_chunks
    per claim, never the full chunk set directly)."""
    cap = select_top_k_chunks(claim_text, document.chunks, k=cfg.k, embedder=None)
    row_matrix = build_claims_chunks_matrix(model, tokenizer, claims=[claim_text], chunks=cap.chunks)

    chunks_out = []
    for chunk_idx, chunk in enumerate(cap.chunks):
        probs = row_matrix.matrix[0][chunk_idx]
        chunks_out.append(
            {
                "chunk_id": chunk.chunk_id,
                "entailment": probs["entailment"],
                "neutral": probs["neutral"],
                "contradiction": probs["contradiction"],
            }
        )

    max_e = row_matrix.max_entailment(0)
    max_c_independent = row_matrix.max_contradiction(0)
    argmax_e_idx = max(range(len(cap.chunks)), key=lambda j: row_matrix.matrix[0][j]["entailment"])
    argmax_c_idx = max(range(len(cap.chunks)), key=lambda j: row_matrix.matrix[0][j]["contradiction"])
    max_e_chunk_id = cap.chunks[argmax_e_idx].chunk_id
    max_c_independent_chunk_id = cap.chunks[argmax_c_idx].chunk_id
    c_at_argmax_e = row_matrix.matrix[0][argmax_e_idx]["contradiction"]
    same_chunk = argmax_e_idx == argmax_c_idx

    verdict_current = score_claim(max_e, max_c_independent, tau=cfg.tau, tau_e=cfg.tau_e, alpha=cfg.alpha)
    verdict_if_same_chunk = score_claim(max_e, c_at_argmax_e, tau=cfg.tau, tau_e=cfg.tau_e, alpha=cfg.alpha)

    return {
        "claim_index": claim_index,
        "claim_text": claim_text,
        "capped": cap.capped,
        "chunks": chunks_out,
        "max_e": max_e,
        "max_e_chunk_id": max_e_chunk_id,
        "max_c_independent": max_c_independent,
        "max_c_independent_chunk_id": max_c_independent_chunk_id,
        "c_at_argmax_e": c_at_argmax_e,
        "same_chunk": same_chunk,
        "best_chunk_id": row_matrix.best_chunk_id(0),
        "verdict_current": {"verdict": verdict_current.verdict.value, "score": verdict_current.score},
        "verdict_if_same_chunk": {
            "verdict": verdict_if_same_chunk.verdict.value,
            "score": verdict_if_same_chunk.score,
        },
    }


def measure_question(
    results_json_path: Path,
    refdocs: ReferenceDocs,
    model: Any,
    tokenizer: Any,
    cfg: Config,
) -> dict[str, Any]:
    question_id, claims = _load_question_id_and_claims(results_json_path)
    document = refdocs.get_document(question_id)
    if document is None:
        raise ValueError(f"question_id {question_id!r} (from {results_json_path}) not found in reference_docs")

    claim_records = [
        measure_claim(i, claim_text, document, model, tokenizer, cfg) for i, claim_text in enumerate(claims)
    ]

    key_point_chunks = resolve_key_point_chunks(document)
    coverage_matrix = build_coverage_matrix(model, tokenizer, claims=claims, key_point_chunks=key_point_chunks)
    max_e_per_keypoint = [coverage_matrix.max_entailment_for_keypoint(i) for i in range(len(key_point_chunks))]

    max_e_per_claim = [r["max_e"] for r in claim_records]
    max_c_independent_per_claim = [r["max_c_independent"] for r in claim_records]
    c_at_argmax_e_per_claim = [r["c_at_argmax_e"] for r in claim_records]
    best_chunk_per_claim = [r["best_chunk_id"] for r in claim_records]
    score_scale = float(cfg.scoring["combination"]["score_scale"])

    # Coverage does not depend on max_c at all, so it is identical under both
    # aggregations -- computed via the same unmodified compute_scoring_result
    # call both times rather than special-cased, per "reimplement nothing".
    result_current = compute_scoring_result(
        claim_texts=claims,
        max_e_per_claim=max_e_per_claim,
        max_c_per_claim=max_c_independent_per_claim,
        best_chunk_per_claim=best_chunk_per_claim,
        max_e_per_keypoint=max_e_per_keypoint,
        tau=cfg.tau, tau_e=cfg.tau_e, alpha=cfg.alpha, score_scale=score_scale,
    )
    result_same_chunk = compute_scoring_result(
        claim_texts=claims,
        max_e_per_claim=max_e_per_claim,
        max_c_per_claim=c_at_argmax_e_per_claim,
        best_chunk_per_claim=best_chunk_per_claim,
        max_e_per_keypoint=max_e_per_keypoint,
        tau=cfg.tau, tau_e=cfg.tau_e, alpha=cfg.alpha, score_scale=score_scale,
    )

    return {
        "results_json_path": str(results_json_path),
        "question_id": question_id,
        "key_point_chunk_ids": [c.chunk_id for c in key_point_chunks],
        "max_e_per_keypoint": max_e_per_keypoint,
        "claims": claim_records,
        "current": {
            "precision": result_current.precision,
            "coverage": result_current.coverage,
            "harmonic_f": result_current.harmonic_f,
            "score": result_current.score,
        },
        "same_chunk_substitution": {
            "precision": result_same_chunk.precision,
            "coverage": result_same_chunk.coverage,
            "harmonic_f": result_same_chunk.harmonic_f,
            "score": result_same_chunk.score,
        },
    }


def _write_report_md(question_results: list[dict[str, Any]], report_path: Path, meta: dict[str, Any]) -> None:
    lines = [
        "# D110 Aggregation Provenance Measurement — Report",
        "",
        f"- Run timestamp (UTC): {meta['run_timestamp_utc']}",
        f"- Git commit at run time: `{meta['git_commit']}`",
        f"- NLI base model: `{meta['nli_base_model']}`",
        (
            f"- Adapter path: `{meta['adapter_path']}`"
            if meta["adapter_path"]
            else "- Adapter path: none (zero-shot only, D89/D109)"
        ),
        f"- Thresholds: tau={meta['thresholds']['tau']}, tau_e={meta['thresholds']['tau_e']}, "
        f"alpha={meta['thresholds']['alpha']}, k={meta['thresholds']['k']}",
        "",
        "Per claim: `verdict_current` = `score_claim(max_e, max_c_independent, ...)` versus "
        "`verdict_if_same_chunk` = `score_claim(max_e, c_at_argmax_e, ...)` — same production "
        "`score_claim` function (scoring/aggregation.py) both times; only which chunk's "
        "contradiction probability is passed in differs.",
        "",
    ]

    for q in question_results:
        lines.append(f"## {q['question_id']} ({q['results_json_path']})")
        lines.append("")
        lines.append(
            "| claim_index | max_e | max_c_independent | c_at_argmax_e | same_chunk "
            "| verdict_current | verdict_if_same_chunk |"
        )
        lines.append("|---|---|---|---|---|---|---|")
        for c in q["claims"]:
            lines.append(
                f"| {c['claim_index']} | {c['max_e']:.6f} | {c['max_c_independent']:.6f} | "
                f"{c['c_at_argmax_e']:.6f} | {c['same_chunk']} | "
                f"{c['verdict_current']['verdict']} (score={c['verdict_current']['score']:.4f}) | "
                f"{c['verdict_if_same_chunk']['verdict']} (score={c['verdict_if_same_chunk']['score']:.4f}) |"
            )
        lines.append("")
        lines.append(f"max_e_per_keypoint: {q['max_e_per_keypoint']}")
        lines.append("")
        lines.append("| metric | current (independent max_c) | same-chunk substitution |")
        lines.append("|---|---|---|")
        for metric in ("precision", "coverage", "harmonic_f", "score"):
            lines.append(f"| {metric} | {q['current'][metric]:.6f} | {q['same_chunk_substitution'][metric]:.6f} |")
        lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "D110: measure the effect of same-chunk vs independent max_c aggregation "
            "on claims already recorded in pipeline_demo results JSONs."
        )
    )
    parser.add_argument(
        "--results-json",
        type=Path,
        action="append",
        required=True,
        help=(
            "Path to a pipeline_demo results JSON (repeatable, at least one required). "
            "Must contain 'question_id' and post-glossary 'claims' -- no fallback to "
            "'claims_raw'."
        ),
    )
    parser.add_argument(
        "--adapter-path",
        type=Path,
        default=None,
        help=(
            "LoRA adapter checkpoint directory. Optional -- default None runs zero-shot "
            "only, per D89/D109 (zero-shot is the closed runtime arm; this script does "
            "not force an adapter arm the way diag_precision_two_arms.py's two-arm "
            "design does)."
        ),
    )
    parser.add_argument("--reference-docs-path", type=Path, default=_DEFAULT_REFERENCE_DOCS_PATH)
    parser.add_argument(
        "--output-path",
        type=Path,
        default=None,
        help="Defaults to results/aggregation_provenance/run_<UTC timestamp>/raw_results.json.",
    )
    args = parser.parse_args(argv)

    run_timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = args.output_path or (_DEFAULT_OUTPUT_ROOT / f"run_{run_timestamp}" / "raw_results.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cfg = Config()
    print(f"[D110] NLI base model: {cfg.nli_model}")
    print(f"[D110] Loading reference docs: {args.reference_docs_path}")
    refdocs = load_reference_docs(args.reference_docs_path)

    print("[D110] Building model (zero-shot base)...")
    model, tokenizer = build_pretrained_model_and_tokenizer(cfg.nli_model)
    if args.adapter_path is not None:
        print(f"[D110] Loading adapter: {args.adapter_path}")
        model = load_adapter(model, args.adapter_path)
    else:
        print("[D110] No --adapter-path given: zero-shot only (D89/D109).")

    question_results = []
    for results_json_path in args.results_json:
        print(f"[D110] Measuring {results_json_path} ...")
        q_result = measure_question(results_json_path, refdocs, model, tokenizer, cfg)
        question_results.append(q_result)
        print(f"[D110]   done: {q_result['question_id']} ({len(q_result['claims'])} claims)")

    meta = {
        "run_timestamp_utc": run_timestamp,
        "git_commit": _get_git_commit(),
        "nli_base_model": cfg.nli_model,
        "adapter_path": str(args.adapter_path) if args.adapter_path is not None else None,
        "thresholds": {"tau": cfg.tau, "tau_e": cfg.tau_e, "alpha": cfg.alpha, "k": cfg.k},
        "reference_docs_path": str(args.reference_docs_path),
        "results_json_paths": [str(p) for p in args.results_json],
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "questions": question_results}, f, ensure_ascii=False, indent=2)
    print(f"[D110] raw_results.json written to: {output_path}")

    report_path = output_path.parent / "report.md"
    _write_report_md(question_results, report_path, meta)
    print(f"[D110] report.md written to: {report_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
