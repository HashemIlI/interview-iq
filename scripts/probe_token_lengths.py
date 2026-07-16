"""
scripts/probe_token_lengths.py — §5.13 empirical probe (pre-D57).

Measures actual AraT5-base tokenizer output on the real Phase 8 corpus
(train: build_kd_dataset, val/gold: build_gold_validation_set) so that
max_source_length / max_target_length in D57 are set from measured
data, not inferred from the D53 pilot addendum text.

Read-only: does not write, train, or modify anything.
"""

from __future__ import annotations

import statistics
import sys
from pathlib import Path

from transformers import AutoTokenizer

from interview_iq.decomposition.dataset_builder import (
    build_gold_validation_set,
    build_kd_dataset,
)
from interview_iq.decomposition.prompts import build_training_pair
from interview_iq.decomposition.types import AnnotationRules

MODEL_NAME = "UBC-NLP/AraT5-base"
CANDIDATE_MAX_LENGTHS = [128, 192, 256, 320, 384, 448, 512]


def token_length(tokenizer, text: str) -> int:
    return len(tokenizer(text, add_special_tokens=True)["input_ids"])


def compute_stats(lengths: list[int]) -> dict:
    s = sorted(lengths)
    n = len(s)
    p95_idx = min(n - 1, int(round(0.95 * (n - 1))))
    return {
        "n": n,
        "min": s[0],
        "max": s[-1],
        "mean": round(statistics.mean(s), 1),
        "median": statistics.median(s),
        "p95": s[p95_idx],
    }


def print_stats(label: str, lengths: list[int]) -> None:
    stats = compute_stats(lengths)
    print(f"\n[{label}] n={stats['n']}")
    print(f"  min={stats['min']}  max={stats['max']}  "
          f"mean={stats['mean']}  median={stats['median']}  p95={stats['p95']}")
    for max_len in CANDIDATE_MAX_LENGTHS:
        truncated = sum(1 for l in lengths if l > max_len)
        pct = round(100 * truncated / stats["n"], 1) if stats["n"] else 0.0
        print(f"  max_length={max_len:>4}: {truncated:>3} truncated ({pct}%)")


def main() -> None:
    corpus_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("results")

    print(f"[probe] loading tokenizer: {MODEL_NAME}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    rules = AnnotationRules(
        preserve_hedging=True,
        generalise_personal_framing=True,
        no_unverifiable_causal_bridge=True,
        enforce_self_containment=True,
    )

    print(f"[probe] loading gold/val set from: {corpus_path}")
    val_examples = build_gold_validation_set(corpus_path)
    print(f"[probe] loading training corpus from: {corpus_path}")
    train_examples = build_kd_dataset(corpus_path, rules)

    print(f"\n[probe] loaded: {len(train_examples)} train, {len(val_examples)} val")

    train_input_lens, train_target_lens = [], []
    for ex in train_examples:
        inp, tgt = build_training_pair(ex)
        train_input_lens.append(token_length(tokenizer, inp))
        train_target_lens.append(token_length(tokenizer, tgt))

    val_input_lens, val_target_lens = [], []
    for ex in val_examples:
        inp, tgt = build_training_pair(ex)
        val_input_lens.append(token_length(tokenizer, inp))
        val_target_lens.append(token_length(tokenizer, tgt))

    print("\n" + "=" * 60)
    print("RAW TOKEN LENGTH STATS (AraT5-base tokenizer)")
    print("=" * 60)
    print_stats("train / input", train_input_lens)
    print_stats("train / target", train_target_lens)
    print_stats("val (O9) / input", val_input_lens)
    print_stats("val (O9) / target", val_target_lens)

    all_input = train_input_lens + val_input_lens
    all_target = train_target_lens + val_target_lens
    print_stats("ALL / input (train+val combined)", all_input)
    print_stats("ALL / target (train+val combined)", all_target)


if __name__ == "__main__":
    main()