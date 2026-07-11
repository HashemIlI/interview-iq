"""
tests/test_compute_probe_verdict.py — scripts/compute_probe_verdict.py CLI test.

Writes two synthetic JSON fixtures to a tmp_path, matching the real schema
scripts/probe_reversed_direction.py writes (probe_doc_id, distant_doc_id,
test_A/test_B/test_C each with label/n_pairs/median_p_e/pairs, arm) — not the
trimmed shape used in probe_verdict.py's own unit tests — so this test
exercises the CLI against realistic input, not a shape convenient for the
verdict logic alone.

Invokes the script as a subprocess (exactly how it's actually run), and
checks the written verdict JSON matches interview_iq.nli.probe_verdict.
evaluate_verdict() called directly on the same two fixtures.

No real model, no real DS-014 data.

Run with:  pytest tests/test_compute_probe_verdict.py -v
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from interview_iq.nli.probe_verdict import evaluate_verdict

REPO_ROOT = Path(__file__).parent.parent
SCRIPT = REPO_ROOT / "scripts" / "compute_probe_verdict.py"


def _make_arm_result(doc_id: str, distant_id: str, arm: str, median_a: float, median_b: float, median_c: float) -> dict:
    """Mirrors the real schema written by probe_reversed_direction.py / run_probe()."""
    return {
        "probe_doc_id": doc_id,
        "distant_doc_id": distant_id,
        "test_A": {"label": "self_entailment", "n_pairs": 6, "median_p_e": median_a, "pairs": []},
        "test_B": {"label": "no_relation_ceiling", "n_pairs": 18, "median_p_e": median_b, "pairs": []},
        "test_C": {"label": "cross_entity_within_doc", "n_pairs": 15, "median_p_e": median_c, "pairs": []},
        "arm": arm,
    }


def test_cli_writes_verdict_matching_direct_evaluate_verdict_call(tmp_path: Path) -> None:
    zero_shot_result = _make_arm_result("DS-014", "SE-001", "zero_shot", median_a=0.95, median_b=0.04, median_c=0.55)
    adapter_result = _make_arm_result("DS-014", "SE-001", "adapter", median_a=0.93, median_b=0.06, median_c=0.30)

    zero_shot_path = tmp_path / "probe_zero_shot.json"
    adapter_path = tmp_path / "probe_adapter.json"
    output_path = tmp_path / "verdict.json"

    zero_shot_path.write_text(json.dumps(zero_shot_result), encoding="utf-8")
    adapter_path.write_text(json.dumps(adapter_result), encoding="utf-8")

    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--zero-shot-json", str(zero_shot_path),
            "--adapter-json", str(adapter_path),
            "--output-json", str(output_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 0, proc.stderr

    assert output_path.exists()
    with output_path.open(encoding="utf-8") as fh:
        written_verdict = json.load(fh)

    expected_verdict = evaluate_verdict(zero_shot_result, adapter_result)
    assert written_verdict == expected_verdict

    # Human-readable summary printed to stdout, per requirement 4.
    assert "PASS" in proc.stdout
    assert "signal_detected" in proc.stdout


def test_cli_reports_fail_and_no_signal_correctly_in_summary(tmp_path: Path) -> None:
    # test_A below 0.90, test_B above 0.10, and C direction wrong (adapter higher).
    zero_shot_result = _make_arm_result("DS-014", "SE-001", "zero_shot", median_a=0.80, median_b=0.20, median_c=0.40)
    adapter_result = _make_arm_result("DS-014", "SE-001", "adapter", median_a=0.70, median_b=0.30, median_c=0.60)

    zero_shot_path = tmp_path / "probe_zero_shot.json"
    adapter_path = tmp_path / "probe_adapter.json"
    output_path = tmp_path / "verdict.json"

    zero_shot_path.write_text(json.dumps(zero_shot_result), encoding="utf-8")
    adapter_path.write_text(json.dumps(adapter_result), encoding="utf-8")

    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--zero-shot-json", str(zero_shot_path),
            "--adapter-json", str(adapter_path),
            "--output-json", str(output_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 0, proc.stderr

    with output_path.open(encoding="utf-8") as fh:
        written_verdict = json.load(fh)

    assert written_verdict["zero_shot"]["test_A"]["pass"] is False
    assert written_verdict["zero_shot"]["test_B"]["pass"] is False
    assert written_verdict["test_C_signal"]["direction_matches_prediction"] is False
    assert written_verdict["test_C_signal"]["signal_detected"] is False

    assert "FAIL" in proc.stdout
