"""
TEMPORARY demo bridge script (21 Jul 2026 session) -- NOT a production
pipeline component, NOT registered as a D## decision in decisions.md.

Manually stitches LLM Claim Decomposition (D74, client.py) output into
the interim Phase 6 claims-JSON format that scripts/run_scoring.py /
cli/run_scoring.py already consumes, so the two already-working pieces
(LLM decomposition + NLI scoring) can be demoed connected end-to-end.

MUST be run against a TEST FIXTURE refdocs file
(tests/fixtures/refdocs_mini.json), NOT production reference docs
(data/refdocs/reference_docs_250_FINAL_v1.json) -- running real claims
against production data here would collide with D44's Coverage-measurement
gate, which is still closed pending the D74 sanity gate's human verdict.

This script performs NO validation of its own beyond what
decompose_via_llm() already does internally. It does NOT replace or
satisfy the D74 mandatory sanity gate (scripts/llm_decomposition_sanity_gate.py)
-- that review is separate, still pending, and unaffected by this script.

Usage:
    python scripts/demo_llm_to_nli_bridge.py \
        --question-id ZZ-002 \
        --answer-text "..." \
        --output-json out/demo_claims_ZZ-002.json

    (then feed out/demo_claims_ZZ-002.json into run_scoring.py as usual)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src"))

from interview_iq.decomposition_llm.client import (  # noqa: E402
    OPENROUTER_MODEL,
    LLMDecompositionError,
    decompose_via_llm,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="TEMPORARY demo bridge: LLM decomposition output -> interim Phase 6 claims JSON."
    )
    parser.add_argument(
        "--question-id",
        required=True,
        help="Must match a question_id already present in the target refdocs fixture (e.g. ZZ-001, ZZ-002).",
    )
    parser.add_argument("--answer-text", required=True, help="Raw ASR-style candidate answer text.")
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args()

    print(f"[demo bridge] model={OPENROUTER_MODEL!r}")
    print(f"[demo bridge] Calling LLM decomposition for question_id={args.question_id!r}...")

    try:
        result = decompose_via_llm(args.answer_text)
    except LLMDecompositionError as exc:
        print(f"[demo bridge] LLM decomposition FAILED: {exc}", file=sys.stderr)
        return 1

    if not result.claims:
        print("[demo bridge] WARNING: zero claims returned (NO_EXTRACTABLE_CLAIMS or empty).", file=sys.stderr)

    payload = {
        "meta": {
            "status": (
                "TEMPORARY DEMO BRIDGE OUTPUT -- LLM decomposition (D74) manually wired into the "
                "interim Phase 6 claims format for a one-off demo. NOT production pipeline wiring."
            ),
            "model_used": OPENROUTER_MODEL,
            "question_id": args.question_id,
            "source_text": result.source_text,
        },
        "question_id": args.question_id,
        "claims": [
            {"claim_id": f"CL{idx:02d}", "text": claim_text}
            for idx, claim_text in enumerate(result.claims, start=1)
        ],
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    with args.output_json.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)

    print(f"[demo bridge] Wrote {len(result.claims)} claim(s) to {args.output_json}")
    for c in payload["claims"]:
        print(f"  {c['claim_id']}: {c['text']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
