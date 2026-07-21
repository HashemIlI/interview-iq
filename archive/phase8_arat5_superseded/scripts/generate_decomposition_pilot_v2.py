"""CLI for the DRAFT_UNREVIEWED decomposition corpus v2 pilot."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from interview_iq.decomposition.pilot_v2 import PilotGenerationError, build_pilot  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=("local", "gemini"), default="local")
    parser.add_argument("--model", default=None)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=Path, default=REPO_ROOT / "results" / "decomposition_corpus_v2_pilot")
    parser.add_argument("--no-resume", action="store_true")
    args = parser.parse_args()
    try:
        audit = build_pilot(REPO_ROOT, args.output_dir, args.provider, args.model, args.seed, not args.no_resume)
    except (PilotGenerationError, ValueError, OSError) as exc:
        print(f"DATASET GENERATION PIPELINE FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(audit, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())