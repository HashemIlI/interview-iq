"""
scripts/recount_overlap.py — Phase 5 hardening, Task B (blocking).

Independently recomputes the D35 5-consecutive-word overlap check over the
real 150 pilot pairs, using a DIFFERENT algorithm than
interview_iq.nli.dataset.check_five_word_overlap (which uses a dynamic-
programming longest-common-substring scan) — this script uses 5-gram set
intersection instead. Both are correct ways to answer ">=5 consecutive
tokens shared between hypothesis and premise"; agreement between the two is
a cross-check, not a re-run of the same code.

Reuses the real data loaders (refdocs.loader, nli.dataset) to read the
actual pair/chunk text — only the overlap-detection algorithm is
reimplemented here, not the data-loading logic.

Prints numbers only. Does NOT edit decisions.md. CPU-only, no network calls.

Also supports --gold-set: recomputes the same check over the 48-pair DS-014
Gold Set (data/nli/gold_set_48.json). The Gold Set's "premise" field is
embedded directly on each pair (see nli.dataset.GoldPairRecord) — no refdocs
chunk-resolution step is needed there.

Usage:
    python scripts/recount_overlap.py
    python scripts/recount_overlap.py --gold-set
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from interview_iq.nli.dataset import PairRecord, load_gold_set, load_pilot_pairs  # noqa: E402
from interview_iq.refdocs.loader import load_reference_docs  # noqa: E402

N = 5  # "5-consecutive-word overlap"

NEUTRAL_LABELS = {"neutral", "paired_neutral", "standard_neutral"}


def _canonical_label(label: str) -> str:
    if label in NEUTRAL_LABELS:
        return "neutral"
    return label


def tokenize(text: str) -> list[str]:
    """Tokenization/normalization applied (stated explicitly, not assumed):
      1. Unicode NFC normalization.
      2. Strip all Unicode combining marks (category 'Mn') — removes Arabic
         diacritics (tashkeel/harakat) so 'مسبقًا' and 'مسبقا' tokenize the same.
      3. Lowercase (affects Latin-script technical terms only; Arabic has no case).
      4. Extract maximal runs of Unicode word characters via regex \\w+
         (re.UNICODE) — punctuation, quotes, and whitespace are all token
         boundaries; nothing else is stripped or stemmed.
    """
    text = unicodedata.normalize("NFC", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = text.lower()
    return re.findall(r"\w+", text, flags=re.UNICODE)


def ngrams(tokens: list[str], n: int) -> set[tuple[str, ...]]:
    if len(tokens) < n:
        return set()
    return {tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)}


def has_ngram_overlap(premise_tokens: list[str], hypothesis_tokens: list[str], n: int = N) -> bool:
    premise_ngrams = ngrams(premise_tokens, n)
    if not premise_ngrams:
        return False
    hyp_ngrams = ngrams(hypothesis_tokens, n)
    return bool(premise_ngrams & hyp_ngrams)


def _print_header(source_label: str) -> None:
    print("=" * 78)
    print(f"5-consecutive-word overlap recount (Phase 5, Task B) -- source: {source_label}")
    print("=" * 78)
    print("\nAlgorithm: 5-gram set intersection (premise 5-grams ∩ hypothesis 5-grams).")
    print("Tokenization/normalization applied:")
    print("  1. Unicode NFC normalization")
    print("  2. Strip Unicode combining marks (category 'Mn') -- removes Arabic tashkeel")
    print("  3. Lowercase")
    print("  4. re.findall(r'\\w+', text, re.UNICODE) -- maximal word-character runs")
    print(f"N = {N} (>= {N} consecutive shared tokens counts as a violation)")


def _print_report(pairs: list[tuple[str, str, str, str]], total_loaded: int, unresolved: list[str]) -> None:
    """pairs: list of (pair_id, canonical_label, premise, hypothesis) already
    filtered to those with a resolvable premise."""
    print(f"\nTotal pairs loaded: {total_loaded}")
    if unresolved:
        print(f"\nWARNING: {len(unresolved)} pair(s) have unresolved premise/chunk -- skipped: {unresolved}")

    violations: list[tuple[str, str]] = []  # (pair_id, canonical_label)
    for pair_id, label, premise, hypothesis in pairs:
        if has_ngram_overlap(tokenize(premise), tokenize(hypothesis), N):
            violations.append((pair_id, label))

    label_counts = Counter(label for _, label in violations)
    total_scored = len(pairs)

    print(f"\nViolations: {len(violations)} / {total_scored}")
    print("Breakdown by gold label (paired_neutral + standard_neutral merged into 'neutral'):")
    for label in ("entailment", "contradiction", "neutral"):
        count = label_counts.get(label, 0)
        pct_of_violations = (count / len(violations) * 100) if violations else 0.0
        print(f"  {label:<14} {count:>3}  ({pct_of_violations:.1f}% of violations)")

    print(f"\nRaw pair_id list of violators: {sorted(pid for pid, _ in violations)}")


def run_pilot() -> None:
    refdocs_path = REPO_ROOT / "data" / "refdocs" / "reference_docs_250_FINAL_v1.json"
    da001_path = REPO_ROOT / "data" / "nli" / "pairs_pilot_150_v2" / "pairs_DA001_pilot_v1.json"
    remaining9_path = REPO_ROOT / "data" / "nli" / "pairs_pilot_150_v2" / "pairs_pilot_remaining9_v2.json"

    refdocs = load_reference_docs(refdocs_path)
    raw_pairs: list[PairRecord] = load_pilot_pairs([da001_path, remaining9_path])

    _print_header("150 pilot pairs (data/nli/pairs_pilot_150_v2/*.json); premise resolved via refdocs chunk_id")

    unresolved = [p.pair_id for p in raw_pairs if refdocs.get_chunk_text(p.chunk_id) is None]
    resolved = [
        (p.pair_id, _canonical_label(p.label), refdocs.get_chunk_text(p.chunk_id), p.hypothesis)
        for p in raw_pairs
        if refdocs.get_chunk_text(p.chunk_id) is not None
    ]
    _print_report(resolved, len(raw_pairs), unresolved)


def run_gold_set() -> None:
    gold_path = REPO_ROOT / "data" / "nli" / "gold_set_48.json"
    gold_pairs = load_gold_set(gold_path)

    _print_header("48-pair DS-014 Gold Set (data/nli/gold_set_48.json); premise embedded directly on each pair")

    resolved = [(p.pair_id, p.label, p.premise, p.hypothesis) for p in gold_pairs]
    _print_report(resolved, len(gold_pairs), unresolved=[])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Phase 5 Task B: independent 5-word overlap recount.")
    parser.add_argument(
        "--gold-set", action="store_true", help="Run against data/nli/gold_set_48.json instead of the 150 pilot pairs."
    )
    args = parser.parse_args(argv)

    if args.gold_set:
        run_gold_set()
    else:
        run_pilot()

    return 0


if __name__ == "__main__":
    sys.exit(main())
