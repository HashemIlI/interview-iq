"""
D74 mandatory sanity gate for the LLM-based Claim Decomposition module.

Runs the fixed set of intentionally-flawed test cases in
tests/fixtures/llm_decomposition_sanity_gate/sg_cases.json through the
SAME production call path as real usage
(interview_iq.decomposition_llm.client.decompose_via_llm) and produces a
report for HUMAN review.

This script does NOT decide PASS/FAIL on its own. Per D77 (decisions.md),
judging whether an error was preserved, whether unauthorized information
was added, or whether claims are atomic is a human call -- an automated
judgment here would reintroduce exactly the kind of circularity (LLM-based
verification of LLM output) this gate exists to avoid. What this script
DOES automate is execution, deterministic logging, and preparing a
side-by-side report so that human review is fast and complete.

KNOWN LIMITATION (documented per §5.13, not silently worked around):
decompose_via_llm() is the only public entry point in client.py. It does
not expose per-request retry counts or raw HTTP response bodies -- those
live inside the private _call_groq() helper. Reaching into a
private function to extract them would mean this gate no longer runs the
exact same call path as production. So this script logs what the public
interface actually returns (success/failure, claims, timing) and leaves
retry-count instrumentation as a gap, rather than faking it or patching
internals. If retry visibility becomes necessary later, that requires a
deliberate change to client.py's public interface, registered as its own
decision -- not a workaround bolted onto this gate.

Usage:
    python scripts/llm_decomposition_sanity_gate.py

Output:
    results/llm_decomposition_sanity_gate/run_<UTC timestamp>/
        raw_results.json   -- full machine-readable output per case
        report.csv          -- human review sheet (verdict columns empty)
        report.md            -- same, human-readable

Reference: D74 (original mandatory-gate requirement), D75 (atomicity
spot-check extension), D76 (first end-to-end call, fallback-model
finding), D77 (this gate's design pre-registration).
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_FIXTURES_PATH = _REPO_ROOT / "tests" / "fixtures" / "llm_decomposition_sanity_gate" / "sg_cases.json"
_OUTPUT_ROOT = _REPO_ROOT / "results" / "llm_decomposition_sanity_gate"

sys.path.insert(0, str(_REPO_ROOT / "src"))

from interview_iq.decomposition_llm.client import (  # noqa: E402
    GROQ_MODEL,
    LLMDecompositionError,
    decompose_via_llm,
)


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
    except Exception as exc:  # noqa: BLE001 -- diagnostic logging only, must not crash the gate
        return f"UNAVAILABLE ({exc})"


def _load_fixtures() -> list[dict]:
    if not _FIXTURES_PATH.exists():
        raise FileNotFoundError(
            f"Fixtures file not found at {_FIXTURES_PATH}. "
            "This gate must not run without the pre-registered D77 test cases."
        )
    with open(_FIXTURES_PATH, encoding="utf-8") as f:
        data = json.load(f)
    cases = data.get("cases", [])
    if not cases:
        raise ValueError(f"Fixtures file at {_FIXTURES_PATH} contains zero cases.")
    return cases


def _run_case(case: dict) -> dict:
    case_id = case["case_id"]
    answer_text = case["answer_text"]

    record = {
        "case_id": case_id,
        "track": case.get("track"),
        "injected_error_type": case.get("injected_error_type"),
        "injected_error_anchor": case.get("injected_error_anchor"),
        "latin_terms_expected": case.get("latin_terms_expected", []),
        "input_answer_text": answer_text,
        "model_used": GROQ_MODEL,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "execution_status": None,
        "claims": None,
        "error_message": None,
        "elapsed_seconds": None,
        # Empty verdict columns -- filled in by human reviewer, not by this script.
        "error_preserved": "",
        "no_unauthorized_addition": "",
        "atomicity_verdict": "",
        "reviewer_notes": "",
    }

    start = time.monotonic()
    try:
        result = decompose_via_llm(answer_text)
        record["execution_status"] = "SUCCESS"
        record["claims"] = result.claims
    except LLMDecompositionError as exc:
        record["execution_status"] = "ERROR"
        record["error_message"] = str(exc)
    except Exception as exc:  # noqa: BLE001 -- must not let one bad case kill the whole run
        record["execution_status"] = "UNEXPECTED_ERROR"
        record["error_message"] = f"{type(exc).__name__}: {exc}"
    finally:
        record["elapsed_seconds"] = round(time.monotonic() - start, 3)

    return record


def _write_report_md(records: list[dict], run_dir: Path, meta: dict) -> None:
    lines = [
        "# D74 LLM Decomposition Sanity Gate — Review Report",
        "",
        f"- Run timestamp (UTC): {meta['run_timestamp_utc']}",
        f"- Model used (single model for entire run, per D77): `{meta['model_used']}`",
        f"- Git commit at run time: `{meta['git_commit']}`",
        f"- Cases: {meta['n_cases']} ({meta['n_success']} executed successfully, {meta['n_error']} failed execution)",
        "",
        "**Gate pass rule (D77):** PASS only if every case has `error_preserved=YES` "
        "AND `no_unauthorized_addition=YES`. Any single NO on either column fails the "
        "whole gate. `atomicity_verdict=NON_ATOMIC` is logged and tracked separately "
        "(non-blocking, per Q8-style handling) -- it does NOT fail the gate.",
        "",
        "**Instructions for reviewer:** for each case, compare `input_answer_text` "
        "against `claims`, using `injected_error_anchor` as the reference for what the "
        "deliberate flaw was. Fill in the three verdict columns below in "
        "`report.csv` (or directly in `raw_results.json`), then record the final "
        "PASS/FAIL result as a D77 update or new D## in decisions.md.",
        "",
    ]

    for r in records:
        lines.append(f"## {r['case_id']} — {r['track']} / {r['injected_error_type']}")
        lines.append("")
        lines.append(f"- **Execution status:** {r['execution_status']}")
        if r["error_message"]:
            lines.append(f"- **Error:** `{r['error_message']}`")
        lines.append(f"- **Input (ASR-style):** {r['input_answer_text']}")
        lines.append(f"- **Injected error anchor:** {r['injected_error_anchor']}")
        lines.append(f"- **Latin terms expected:** {', '.join(r['latin_terms_expected']) or '(none)'}")
        lines.append("- **Claims produced:**")
        if r["claims"]:
            for i, claim in enumerate(r["claims"], 1):
                lines.append(f"  {i}. {claim}")
        else:
            lines.append("  (none -- execution failed or NO_EXTRACTABLE_CLAIMS)")
        lines.append("")
        lines.append(
            "- **Verdict (fill in):** error_preserved = `___` | "
            "no_unauthorized_addition = `___` | atomicity_verdict = `___`"
        )
        lines.append("")

    (run_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")


def _write_report_csv(records: list[dict], run_dir: Path) -> None:
    fieldnames = [
        "case_id",
        "track",
        "injected_error_type",
        "execution_status",
        "model_used",
        "timestamp_utc",
        "elapsed_seconds",
        "input_answer_text",
        "injected_error_anchor",
        "latin_terms_expected",
        "claims",
        "error_message",
        "error_preserved",
        "no_unauthorized_addition",
        "atomicity_verdict",
        "reviewer_notes",
    ]
    with open(run_dir / "report.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            row = dict(r)
            row["latin_terms_expected"] = "; ".join(r["latin_terms_expected"])
            row["claims"] = " | ".join(r["claims"]) if r["claims"] else ""
            writer.writerow(row)


def main() -> int:
    cases = _load_fixtures()
    git_commit = _get_git_commit()
    run_timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = _OUTPUT_ROOT / f"run_{run_timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    if not GROQ_MODEL:
        print(
            "ERROR: GROQ_MODEL is not set in .env. Per client.py, this must be "
            "verified manually against https://console.groq.com/docs/models before running.",
            file=sys.stderr,
        )
        return 1

    print(f"Running D74 sanity gate: {len(cases)} cases, model={GROQ_MODEL!r}, "
          f"git commit={git_commit}")

    records = []
    for case in cases:
        print(f"  -> {case['case_id']} ({case.get('track')}, {case.get('injected_error_type')})...", end=" ")
        record = _run_case(case)
        print(record["execution_status"])
        records.append(record)

    n_success = sum(1 for r in records if r["execution_status"] == "SUCCESS")
    n_error = len(records) - n_success

    meta = {
        "run_timestamp_utc": run_timestamp,
        "model_used": GROQ_MODEL,
        "git_commit": git_commit,
        "n_cases": len(records),
        "n_success": n_success,
        "n_error": n_error,
    }

    with open(run_dir / "raw_results.json", "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "records": records}, f, ensure_ascii=False, indent=2)

    _write_report_md(records, run_dir, meta)
    _write_report_csv(records, run_dir)

    print()
    print(f"Execution complete: {n_success}/{len(records)} cases executed successfully.")
    if n_error:
        print(f"WARNING: {n_error} case(s) failed execution -- see raw_results.json for error_message.")
    print(f"Output written to: {run_dir}")
    print()
    print("NEXT STEP (human, not automated): review report.md or report.csv, fill in "
          "error_preserved / no_unauthorized_addition / atomicity_verdict for each "
          "case, then record the PASS/FAIL result in decisions.md per D77.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
