"""
scripts/compute_probe_verdict.py — D46 verdict CLI.

Reads the two raw per-arm JSON files written by scripts/probe_reversed_direction.py
(one --zero-shot run, one --adapter-path run) and applies D46's pre-registered
A/B/C thresholds via interview_iq.nli.probe_verdict.evaluate_verdict(), writing
the resulting verdict dict to disk and printing a human-readable summary.

This script does not run any model and does not recompute probabilities — it
only reads the two already-written result files and applies the decision rule.

Usage:
    python scripts/compute_probe_verdict.py \
        --zero-shot-json results/probe_reversed/probe_zero_shot.json \
        --adapter-json results/probe_reversed/probe_adapter.json

Output default: results/probe_reversed/verdict.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from interview_iq.nli.probe_verdict import evaluate_verdict  # noqa: E402

DEFAULT_OUTPUT = REPO_ROOT / "results" / "probe_reversed" / "verdict.json"


def _print_summary(verdict: dict) -> None:
    print("\n[compute_probe_verdict] D46 verdict summary")
    for arm in ("zero_shot", "adapter"):
        arm_verdict = verdict[arm]
        a = arm_verdict["test_A"]
        b = arm_verdict["test_B"]
        print(f"\n  arm={arm}")
        print(f"    test_A  median_p_e={a['median_p_e']:.6f}  threshold>={a['threshold']}  "
              f"{'PASS' if a['pass'] else 'FAIL'}")
        print(f"    test_B  median_p_e={b['median_p_e']:.6f}  threshold<={b['threshold']}  "
              f"{'PASS' if b['pass'] else 'FAIL'}")

    signal = verdict["test_C_signal"]
    print("\n  test_C_signal")
    print(f"    zero_shot median_p_e={signal['zero_shot_median_p_e']:.6f}")
    print(f"    adapter   median_p_e={signal['adapter_median_p_e']:.6f}")
    print(f"    diff (zero_shot - adapter)={signal['diff']:.6f}  threshold>={signal['signal_threshold']}")
    print(f"    direction_matches_prediction={signal['direction_matches_prediction']}")
    print(f"    signal_detected={signal['signal_detected']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="D46 verdict CLI — applies pre-registered thresholds to two probe result JSONs."
    )
    parser.add_argument(
        "--zero-shot-json",
        type=Path,
        required=True,
        help="Path to the raw zero-shot arm result JSON (probe_reversed_direction.py --zero-shot output).",
    )
    parser.add_argument(
        "--adapter-json",
        type=Path,
        required=True,
        help="Path to the raw adapter arm result JSON (probe_reversed_direction.py --adapter-path output).",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Where to write the verdict JSON. Default: {DEFAULT_OUTPUT}",
    )
    args = parser.parse_args(argv)

    with args.zero_shot_json.open("r", encoding="utf-8") as fh:
        zero_shot_result = json.load(fh)
    with args.adapter_json.open("r", encoding="utf-8") as fh:
        adapter_result = json.load(fh)

    verdict = evaluate_verdict(zero_shot_result, adapter_result)

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    with args.output_json.open("w", encoding="utf-8") as fh:
        json.dump(verdict, fh, ensure_ascii=False, indent=2)

    _print_summary(verdict)
    print(f"\n[compute_probe_verdict] Wrote: {args.output_json}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
