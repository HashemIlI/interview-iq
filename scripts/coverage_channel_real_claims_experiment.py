"""
D82 pre-registered experiment: first measurement of the Coverage channel on
real decomposition claims (decisions.md D82, two-arm addendum).

For each of the 25 O9 questions (results/o9_decomposition_exercises.md, D51):
  1. Parse question_id + raw answer text.
  2. Call decompose_via_llm ONCE per answer (same production call path,
     D74/D77-D80) -- NOT re-decomposed per NLI arm.
  3. Look up the question's official key_points via
     scoring.metrics.resolve_key_point_chunks (chunk_id strings resolved to
     Chunk objects, per refdocs/loader.py's schema).
  4. Run the Coverage channel (nli.engine.build_coverage_matrix +
     CoverageMatrix.max_entailment_for_keypoint + scoring.metrics.
     coverage_channel) TWICE on the SAME claims -- once against the
     zero-shot base NLI model, once against the fine-tuned adapter
     (iq-checkpoints-nli-v1) -- per the D82 two-arm addendum, matching the
     D40/D46/D49 convention of comparing both arms rather than only one.

This is a read-only diagnostic: it does not modify O9, key_points,
reference_docs, or any file under src/interview_iq/. It reuses the real
Coverage-channel functions verified in d82_interface_inspection.md; it does
not reimplement any of that math.

n=25 -> directional judgment, not statistical (D82 pre-registered
constraint). Decomposition quality itself is still unmeasured in isolation
(D74/D75); NLI thresholds remain PRE-CALIBRATION DEFAULT (G4 not yet run).
Per D82's RISK-ACCEPTED note, a weak number here cannot be confidently
attributed to one component in isolation.

Usage (Kaggle T4 thin-runner is the standing execution environment per D82;
see module-level defaults below for local paths):
    python scripts/coverage_channel_real_claims_experiment.py \\
        --adapter-path /path/to/iq-checkpoints-nli-v1

Output:
    results/coverage_channel_real_claims/run_<UTC timestamp>/
        raw_results.json   -- full machine-readable output per question
        report.csv          -- human review sheet (UTF-8-sig)
        report.md            -- same, human-readable

Reference: D42 (Coverage-channel fragility hypotheses this experiment
targets), D44 (defers real-claims measurement until a decomposition module
exists and passes its sanity gate), D46/D49 (claim-free reversed-direction
probe -- this experiment is the first WITH real claims), D82 (this
experiment's pre-registration + two-arm addendum).
"""

from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

_REPO_ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_O9_PATH = _REPO_ROOT / "results" / "o9_decomposition_exercises.md"
_DEFAULT_REFERENCE_DOCS_PATH = _REPO_ROOT / "data" / "refdocs" / "reference_docs_250_FINAL_v1.json"
_DEFAULT_OUTPUT_ROOT = _REPO_ROOT / "results" / "coverage_channel_real_claims"

sys.path.insert(0, str(_REPO_ROOT / "src"))

from interview_iq.config import Config  # noqa: E402
from interview_iq.decomposition_llm.client import (  # noqa: E402
    GROQ_MODEL,
    LLMDecompositionError,
    decompose_via_llm,
)
from interview_iq.evaluation.gold_eval import build_pretrained_model_and_tokenizer, load_adapter  # noqa: E402
from interview_iq.nli.engine import build_coverage_matrix  # noqa: E402
from interview_iq.refdocs.loader import Chunk, ReferenceDocs, load_reference_docs  # noqa: E402
from interview_iq.scoring.metrics import (  # noqa: E402
    DanglingKeyPointError,
    coverage_channel,
    resolve_key_point_chunks,
)

# ── O9 markdown parsing ──────────────────────────────────────────────────────
#
# Two edge cases confirmed empirically against the real file (see
# d82_interface_inspection.md), not assumed:
#   - 23/25 headers are "### {qid}: {question text}"; DA-029 and DS-030 are
#     "### {qid} <warning annotation>" with no colon/text at all. question_id
#     is therefore extracted via a leading [A-Z]{2}-\d{3} token, never by
#     splitting the header line on ':'.
#   - the answer label has two variants ("**إجابة:**" and
#     "**إجابة (لهجة مصرية):**"), matched via a wildcard between "إجابة"
#     and the closing "**", not two separate hardcoded patterns.

_QID_HEADER_RE = re.compile(r"^###\s*([A-Z]{2}-\d{3})")
_ANSWER_BLOCK_RE = re.compile(r"\*\*إجابة[^*]*\*\*\s*\n(.*?)\n\s*\*\*الـ Claims", re.DOTALL)


@dataclass(frozen=True)
class O9Question:
    question_id: str
    raw_answer_text: str


def parse_o9_markdown(text: str) -> list[O9Question]:
    """Split O9 markdown into per-question blocks and extract question_id +
    raw answer text. Does not use the O9 manual reference claims at all
    (D44/D82: official key_points from reference_docs is the ground truth
    here, not O9's own claims, to avoid measuring data consistency with
    itself)."""
    blocks = re.split(r"(?=^###\s)", text, flags=re.MULTILINE)
    questions: list[O9Question] = []
    for block in blocks:
        header_match = _QID_HEADER_RE.match(block.strip())
        if not header_match:
            continue  # preamble before the first ### header
        question_id = header_match.group(1)
        answer_match = _ANSWER_BLOCK_RE.search(block)
        if not answer_match:
            raise ValueError(
                f"{question_id}: could not locate a '**إجابة...:**' ... '**الـ Claims' block"
            )
        raw_answer_text = answer_match.group(1).strip()
        questions.append(O9Question(question_id=question_id, raw_answer_text=raw_answer_text))
    return questions


# ── Coverage channel (real functions, not reimplemented) ────────────────────


def compute_coverage_for_arm(
    claims: list[str],
    key_point_chunks: list[Chunk],
    model: Any,
    tokenizer: Any,
) -> tuple[list[float], float]:
    """One NLI arm's Coverage result for one question's claims -- mirrors
    cli/run_scoring.py's own Coverage-only lines, factored out so it can run
    twice (zero-shot, adapter) against the same claims."""
    matrix = build_coverage_matrix(model, tokenizer, claims=claims, key_point_chunks=key_point_chunks)
    max_e_per_keypoint = [matrix.max_entailment_for_keypoint(i) for i in range(len(key_point_chunks))]
    coverage_score = coverage_channel(max_e_per_keypoint)
    return max_e_per_keypoint, coverage_score


def _empty_arm_result() -> dict[str, Any]:
    return {"status": None, "max_e_per_keypoint": None, "coverage_score": None, "error": None}


def run_one_question(
    question: O9Question,
    refdocs: ReferenceDocs,
    zero_shot_model: Any,
    zero_shot_tokenizer: Any,
    adapter_model: Any,
    adapter_tokenizer: Any,
    decompose_fn: Callable[[str], Any] = decompose_via_llm,
) -> dict[str, Any]:
    """Runs the full D82 procedure for one O9 question: one decomposition
    call, then Coverage computed on both NLI arms against the same claims.
    model/tokenizer/decompose_fn are always injected by the caller (never
    constructed here) -- same pattern as nli/engine.py and cli/run_scoring.py
    -- so this function is directly testable with tiny offline models and a
    mocked decompose_fn, with zero real API/network calls."""
    record: dict[str, Any] = {
        "question_id": question.question_id,
        "track": None,
        "raw_answer_text": question.raw_answer_text,
        "model_used": GROQ_MODEL,
        "decomposition_status": None,
        "decomposition_error": None,
        "claims": None,
        "key_point_count": None,
        "key_point_chunk_ids": None,
        "zero_shot": _empty_arm_result(),
        "adapter": _empty_arm_result(),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": None,
    }
    start = time.monotonic()

    document = refdocs.get_document(question.question_id)
    if document is not None:
        record["track"] = document.track

    try:
        result = decompose_fn(question.raw_answer_text)
        record["decomposition_status"] = "SUCCESS"
        record["claims"] = result.claims
    except LLMDecompositionError as exc:
        record["decomposition_status"] = "ERROR"
        record["decomposition_error"] = str(exc)
    except Exception as exc:  # noqa: BLE001 -- one bad question must not kill the whole run
        record["decomposition_status"] = "UNEXPECTED_ERROR"
        record["decomposition_error"] = f"{type(exc).__name__}: {exc}"

    if document is None:
        msg = f"question_id {question.question_id!r} not found in reference_docs"
        record["zero_shot"]["status"] = "SKIPPED"
        record["zero_shot"]["error"] = msg
        record["adapter"]["status"] = "SKIPPED"
        record["adapter"]["error"] = msg
        record["elapsed_seconds"] = round(time.monotonic() - start, 3)
        return record

    try:
        key_point_chunks = resolve_key_point_chunks(document)
        record["key_point_count"] = len(key_point_chunks)
        record["key_point_chunk_ids"] = [c.chunk_id for c in key_point_chunks]
    except DanglingKeyPointError as exc:
        msg = f"key_points resolution failed: {exc}"
        record["zero_shot"]["status"] = "SKIPPED"
        record["zero_shot"]["error"] = msg
        record["adapter"]["status"] = "SKIPPED"
        record["adapter"]["error"] = msg
        record["elapsed_seconds"] = round(time.monotonic() - start, 3)
        return record

    if record["claims"] is None:
        # Decomposition itself failed -- no claims exist to score on either arm.
        # (An empty claims list, e.g. NO_EXTRACTABLE_CLAIMS, is NOT this case --
        # that is a genuine result and flows through to coverage_channel below,
        # which returns 0.0 for an empty claim set rather than erroring.)
        msg = f"no claims available (decomposition {record['decomposition_status']}): {record['decomposition_error']}"
        record["zero_shot"]["status"] = "SKIPPED_NO_CLAIMS"
        record["zero_shot"]["error"] = msg
        record["adapter"]["status"] = "SKIPPED_NO_CLAIMS"
        record["adapter"]["error"] = msg
        record["elapsed_seconds"] = round(time.monotonic() - start, 3)
        return record

    claims = record["claims"]
    arms = (
        ("zero_shot", zero_shot_model, zero_shot_tokenizer),
        ("adapter", adapter_model, adapter_tokenizer),
    )
    for arm_name, model, tokenizer in arms:
        try:
            max_e_per_keypoint, coverage_score = compute_coverage_for_arm(
                claims, key_point_chunks, model, tokenizer
            )
            record[arm_name]["status"] = "SUCCESS"
            record[arm_name]["max_e_per_keypoint"] = max_e_per_keypoint
            record[arm_name]["coverage_score"] = coverage_score
        except Exception as exc:  # noqa: BLE001 -- one arm's failure must not block the other
            record[arm_name]["status"] = "ERROR"
            record[arm_name]["error"] = f"{type(exc).__name__}: {exc}"

    record["elapsed_seconds"] = round(time.monotonic() - start, 3)
    return record


# ── Reporting (same conventions as scripts/llm_decomposition_sanity_gate.py) ─


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


def _write_report_md(records: list[dict[str, Any]], run_dir: Path, meta: dict[str, Any]) -> None:
    lines = [
        "# D82 Coverage Channel Real-Claims Experiment — Report",
        "",
        f"- Run timestamp (UTC): {meta['run_timestamp_utc']}",
        f"- Git commit at run time: `{meta['git_commit']}`",
        f"- Decomposition model (single model for entire run, per D77 convention): `{meta['model_used']}`",
        f"- NLI base model: `{meta['nli_base_model']}`",
        f"- Adapter checkpoint: `{meta['adapter_path']}`",
        f"- Questions: {meta['n_questions']} "
        f"({meta['n_decomposition_success']} decomposed successfully, "
        f"{meta['n_decomposition_failed']} decomposition failures)",
        f"- Coverage arms: zero-shot {meta['n_zero_shot_success']}/{meta['n_questions']} scored, "
        f"adapter {meta['n_adapter_success']}/{meta['n_questions']} scored",
        "",
        "**Read this as a directional first reading (n=25), not a statistical result "
        "(D82 pre-registered constraint).** Per the D82 two-arm addendum, this is the "
        "first test of D42-b/D46-C's prediction (learned-neutral shift from HARD_POS "
        "twins may make the adapter's Coverage worse than zero-shot's) on real claims.",
        "",
    ]

    for r in records:
        lines.append(f"## {r['question_id']} ({r['track'] or 'unknown track'})")
        lines.append("")
        lines.append(f"- **Decomposition status:** {r['decomposition_status']}")
        if r["decomposition_error"]:
            lines.append(f"- **Decomposition error:** `{r['decomposition_error']}`")
        lines.append(f"- **Raw answer:** {r['raw_answer_text']}")
        lines.append("- **Claims produced:**")
        if r["claims"]:
            for i, claim in enumerate(r["claims"], 1):
                lines.append(f"  {i}. {claim}")
        else:
            lines.append("  (none -- decomposition failed or NO_EXTRACTABLE_CLAIMS)")
        lines.append(f"- **Key points:** {r['key_point_count']} ({', '.join(r['key_point_chunk_ids'] or [])})")
        for arm_name in ("zero_shot", "adapter"):
            arm = r[arm_name]
            lines.append(f"- **{arm_name} arm:** status={arm['status']}, coverage_score={arm['coverage_score']}")
            if arm["max_e_per_keypoint"] is not None:
                lines.append(f"  - per-key-point max P(entailment): {arm['max_e_per_keypoint']}")
            if arm["error"]:
                lines.append(f"  - error: `{arm['error']}`")
        lines.append("")

    (run_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")


def _write_report_csv(records: list[dict[str, Any]], run_dir: Path) -> None:
    fieldnames = [
        "question_id",
        "track",
        "decomposition_status",
        "model_used",
        "timestamp_utc",
        "elapsed_seconds",
        "key_point_count",
        "key_point_chunk_ids",
        "zero_shot_status",
        "zero_shot_coverage_score",
        "zero_shot_max_e_per_keypoint",
        "zero_shot_error",
        "adapter_status",
        "adapter_coverage_score",
        "adapter_max_e_per_keypoint",
        "adapter_error",
        "raw_answer_text",
        "claims",
        "decomposition_error",
    ]
    with open(run_dir / "report.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            row = {
                "question_id": r["question_id"],
                "track": r["track"],
                "decomposition_status": r["decomposition_status"],
                "model_used": r["model_used"],
                "timestamp_utc": r["timestamp_utc"],
                "elapsed_seconds": r["elapsed_seconds"],
                "key_point_count": r["key_point_count"],
                "key_point_chunk_ids": "; ".join(r["key_point_chunk_ids"] or []),
                "zero_shot_status": r["zero_shot"]["status"],
                "zero_shot_coverage_score": r["zero_shot"]["coverage_score"],
                "zero_shot_max_e_per_keypoint": "; ".join(
                    str(v) for v in (r["zero_shot"]["max_e_per_keypoint"] or [])
                ),
                "zero_shot_error": r["zero_shot"]["error"],
                "adapter_status": r["adapter"]["status"],
                "adapter_coverage_score": r["adapter"]["coverage_score"],
                "adapter_max_e_per_keypoint": "; ".join(
                    str(v) for v in (r["adapter"]["max_e_per_keypoint"] or [])
                ),
                "adapter_error": r["adapter"]["error"],
                "raw_answer_text": r["raw_answer_text"],
                "claims": " | ".join(r["claims"]) if r["claims"] else "",
                "decomposition_error": r["decomposition_error"],
            }
            writer.writerow(row)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "D82: Coverage channel measurement on real decomposition claims "
            "(25 O9 questions, two NLI arms per the D82 addendum)."
        )
    )
    parser.add_argument("--o9-path", type=Path, default=_DEFAULT_O9_PATH)
    parser.add_argument("--reference-docs-path", type=Path, default=_DEFAULT_REFERENCE_DOCS_PATH)
    parser.add_argument(
        "--adapter-path",
        type=Path,
        required=True,
        help=(
            "LoRA adapter checkpoint directory (iq-checkpoints-nli-v1). Required, not "
            "optional -- per the D82 two-arm addendum, both the zero-shot and adapter "
            "arms always run; the adapter is never silently skipped."
        ),
    )
    parser.add_argument("--output-dir", type=Path, default=_DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args(argv)

    if not GROQ_MODEL:
        print(
            "ERROR: GROQ_MODEL is not set in .env. Verify manually against "
            "https://console.groq.com/docs/models before running (client.py).",
            file=sys.stderr,
        )
        return 1

    git_commit = _get_git_commit()
    run_timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = args.output_dir / f"run_{run_timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"[D82] Parsing O9 markdown: {args.o9_path}")
    o9_text = args.o9_path.read_text(encoding="utf-8")
    questions = parse_o9_markdown(o9_text)
    print(f"[D82] Parsed {len(questions)} O9 questions.")

    print(f"[D82] Loading reference docs: {args.reference_docs_path}")
    refdocs = load_reference_docs(args.reference_docs_path)

    cfg = Config()
    print(f"[D82] NLI base model: {cfg.nli_model}")
    print("[D82] Building zero-shot arm model (no adapter)...")
    zero_shot_model, tokenizer = build_pretrained_model_and_tokenizer(cfg.nli_model)
    print("[D82] Building adapter arm base model...")
    adapter_base_model, _ = build_pretrained_model_and_tokenizer(cfg.nli_model)
    adapter_model = load_adapter(adapter_base_model, args.adapter_path)
    print(f"[D82] Loaded adapter: {args.adapter_path}")

    records: list[dict[str, Any]] = []
    for q in questions:
        print(f"  -> {q.question_id} ...", end=" ")
        record = run_one_question(
            q, refdocs, zero_shot_model, tokenizer, adapter_model, tokenizer
        )
        print(
            f"decomposition={record['decomposition_status']} "
            f"zero_shot={record['zero_shot']['status']} adapter={record['adapter']['status']}"
        )
        records.append(record)

    n_decomposition_success = sum(1 for r in records if r["decomposition_status"] == "SUCCESS")
    n_zero_shot_success = sum(1 for r in records if r["zero_shot"]["status"] == "SUCCESS")
    n_adapter_success = sum(1 for r in records if r["adapter"]["status"] == "SUCCESS")

    meta = {
        "run_timestamp_utc": run_timestamp,
        "git_commit": git_commit,
        "model_used": GROQ_MODEL,
        "nli_base_model": cfg.nli_model,
        "adapter_path": str(args.adapter_path),
        "o9_path": str(args.o9_path),
        "reference_docs_path": str(args.reference_docs_path),
        "n_questions": len(records),
        "n_decomposition_success": n_decomposition_success,
        "n_decomposition_failed": len(records) - n_decomposition_success,
        "n_zero_shot_success": n_zero_shot_success,
        "n_adapter_success": n_adapter_success,
    }

    import json

    with open(run_dir / "raw_results.json", "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "records": records}, f, ensure_ascii=False, indent=2)

    _write_report_md(records, run_dir, meta)
    _write_report_csv(records, run_dir)

    print()
    print(
        f"Execution complete: {n_decomposition_success}/{len(records)} decomposed, "
        f"{n_zero_shot_success}/{len(records)} zero-shot Coverage scored, "
        f"{n_adapter_success}/{len(records)} adapter Coverage scored."
    )
    print(f"Output written to: {run_dir}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
