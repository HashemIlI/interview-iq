"""
scripts/probe_reversed_direction.py — D46 pre-registered diagnostic probe CLI.

Runs the reversed-direction NLI probe (nli/probe.py) on DS-014, which is the
only document the fine-tuned model has never seen as a premise (D28). Three
tests per arm (see nli/probe.py for full specification):

  A  self-entailment  (median P(E) >= 0.90 criterion)
  B  no-relation ceiling vs SE-001  (median P(E) <= 0.10 criterion)
  C  cross-entity within DS-014  (pre-registered: adapter < zero-shot by >= 0.10)

Run once per arm:
    python scripts/probe_reversed_direction.py --zero-shot \
        --refdocs-path data/refdocs/reference_docs_250_FINAL_v1.json
    python scripts/probe_reversed_direction.py \
        --adapter-path /kaggle/working/iq-checkpoints-nli-v1/checkpoint-27 \
        --refdocs-path data/refdocs/reference_docs_250_FINAL_v1.json

Output files: results/probe_reversed/probe_zero_shot.json  (--zero-shot arm)
              results/probe_reversed/probe_adapter.json     (--adapter-path arm)

DO NOT run locally against the real model. Runs on Kaggle. D46's pre-registered
criteria decide the verdict — no verdict logic lives in this script.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from interview_iq.evaluation.gold_eval import build_pretrained_model_and_tokenizer, load_adapter  # noqa: E402
from interview_iq.nli.probe import run_probe  # noqa: E402
from interview_iq.refdocs.loader import load_reference_docs  # noqa: E402

PROBE_DOC_ID = "DS-014"
DISTANT_DOC_ID = "SE-001"

OUTPUT_DIR = REPO_ROOT / "results" / "probe_reversed"


def _print_result(arm: str, result: dict) -> None:
    print(f"\n[probe_reversed_direction] arm={arm}  probe={result['probe_doc_id']}  distant={result['distant_doc_id']}")
    for test_key in ("test_A", "test_B", "test_C"):
        t = result[test_key]
        print(f"\n  {test_key} ({t['label']})  n_pairs={t['n_pairs']}  median_P(E)={t['median_p_e']:.6f}")
        print(f"  {'premise_id':<16}{'hypothesis_id':<16}{'P(E)':>10}")
        for pair in t["pairs"]:
            print(f"  {pair['premise_id']:<16}{pair['hypothesis_id']:<16}{pair['p_e']:>10.6f}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="D46 reversed-direction probe — runs on Kaggle, not locally."
    )
    parser.add_argument(
        "--refdocs-path",
        type=Path,
        default=REPO_ROOT / "data" / "refdocs" / "reference_docs_250_FINAL_v1.json",
        help="Path to reference_docs_250_FINAL_v1.json.",
    )
    parser.add_argument(
        "--zero-shot",
        action="store_true",
        help="Run the zero-shot arm (base model, no adapter).",
    )
    parser.add_argument(
        "--adapter-path",
        type=Path,
        default=None,
        help="Path to a LoRA adapter checkpoint. Omit for zero-shot.",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=None,
        help="Override output path. Default: results/probe_reversed/probe_{arm}.json.",
    )
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--max-length", type=int, default=256)
    args = parser.parse_args(argv)

    if not args.zero_shot and args.adapter_path is None:
        parser.error("Specify --zero-shot OR --adapter-path (exactly one arm per run).")

    refdocs = load_reference_docs(args.refdocs_path)
    probe_doc = refdocs.get_document(PROBE_DOC_ID)
    distant_doc = refdocs.get_document(DISTANT_DOC_ID)
    if probe_doc is None:
        parser.error(f"{PROBE_DOC_ID} not found in {args.refdocs_path}")
    if distant_doc is None:
        parser.error(f"{DISTANT_DOC_ID} not found in {args.refdocs_path}")

    from interview_iq.config import Config  # noqa: PLC0415

    cfg = Config()
    print(f"[probe_reversed_direction] Base model: {cfg.nli_model}")
    model, tokenizer = build_pretrained_model_and_tokenizer(cfg.nli_model)

    if args.zero_shot:
        arm = "zero_shot"
        print("[probe_reversed_direction] Arm: zero-shot (no adapter)")
    else:
        arm = "adapter"
        model = load_adapter(model, args.adapter_path)
        print(f"[probe_reversed_direction] Arm: adapter  path={args.adapter_path}")

    result = run_probe(
        model, tokenizer, probe_doc, distant_doc,
        batch_size=args.batch_size, max_length=args.max_length,
    )
    result["arm"] = arm

    _print_result(arm, result)

    output_path = args.output_json or (OUTPUT_DIR / f"probe_{arm}.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=2)
    print(f"\n[probe_reversed_direction] Wrote: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
