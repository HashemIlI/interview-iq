"""
decomposition/dataset_builder.py — KD dataset builder.

Q6 resolved (decisions.md D54): AraT5-base. D55: training corpus built
via LLM-assisted offline generation (batch1-5, 223/225 questions) with
mandatory human review, sourced from Markdown files under `results/`.
O9 (results/o9_decomposition_exercises.md) is the Gold/Validation set
(D55) and must never appear in the training corpus -- see
`check_o9_not_in_training` below, modeled on the DS-014 guard in
`interview_iq.nli.dataset.check_ds014_exclusion` (D28).

Parsing note (§5.13): this regex-based parser has NOT been run
end-to-end against the full results/ directory as of writing. Run this
module's __main__ smoke test and manually compare the printed counts
against the known per-batch claim totals (batch1: 90, batch2: 461,
batch3: 434, batch4: 400, batch5: 462) before trusting the output for
actual training.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from interview_iq.decomposition.types import AnnotationRules, KDExample

# --- File layout (results/) ------------------------------------------

GOLD_FILENAME = "o9_decomposition_exercises.md"

TRAIN_FILENAMES = [
    "pilot_llm_assisted_batch1_DRAFT_UNREVIEWED.md",
    "pilot_llm_assisted_batch2_DRAFT_UNREVIEWED.md",
    "pilot_llm_assisted_batch3_DRAFT_UNREVIEWED.md",
    "pilot_llm_assisted_batch4_DRAFT_UNREVIEWED.md",
    "pilot_llm_assisted_batch5_DRAFT_UNREVIEWED.md",
]

# Marker within a question block that flags it as excluded from
# training (e.g. GN-050 in batch4 -- behavioural question, no real
# NLI-checkable reference).
EXCLUSION_MARKER = "مستبعد من corpus التدريب"

_QUESTION_HEADER_RE = re.compile(r"^###\s+([A-Z]{2}-\d{3})(?:\s*\[[^\]]*\])?[:\s].*$", re.MULTILINE)
_CLAIMS_SECTION_RE = re.compile(r"\*\*(?:الـ )?Claims:?\*\*", re.IGNORECASE)
_ANSWER_SECTION_RE = re.compile(r"\*\*(?:الـ )?(?:إجابة|الإجابة)(?:\s*\([^)]*\))?:?\*\*")
_CLAIM_LINE_RE = re.compile(r"^\s*(\d+)\.\s*(⚠️\s*)?(.+?)\s*$", re.MULTILINE)


@dataclass(frozen=True)
class ParsedQuestion:
    """Intermediate parse result for one question block, kept separate
    from KDExample so exclusion/metadata decisions stay visible and
    testable independently."""

    question_id: str
    source_text: str
    claims: list[str]
    excluded: bool
    source_file: str


def _split_question_blocks(text: str) -> list[str]:
    matches = list(_QUESTION_HEADER_RE.finditer(text))
    blocks = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        blocks.append(text[start:end])
    return blocks


def _extract_answer(block: str) -> str:
    ans_match = _ANSWER_SECTION_RE.search(block)
    claims_match = _CLAIMS_SECTION_RE.search(block)
    if not ans_match or not claims_match or ans_match.start() >= claims_match.start():
        raise ValueError("could not locate answer section between إجابة/Claims markers")
    return block[ans_match.end():claims_match.start()].strip()


def _clean_claim_text(raw_claim: str) -> str:
    """Strip a trailing R1 editorial annotation, e.g. '(خطأ عضوي — R1: ...)'.
    Heuristic (§5.13 -- verify manually on a sample): only strips a
    trailing '(...)' if it contains 'R1' or 'عضوي'; otherwise assumes
    it's part of the claim itself (e.g. an abbreviation like '(SOC)')."""
    text = raw_claim.strip()
    paren_match = re.search(r"\s*\(([^()]*)\)\s*$", text)
    if paren_match and ("R1" in paren_match.group(1) or "عضوي" in paren_match.group(1)):
        text = text[: paren_match.start()].strip()
    return text


def _extract_claims(block: str) -> list[str]:
    claims_match = _CLAIMS_SECTION_RE.search(block)
    if not claims_match:
        raise ValueError("no '**الـ Claims:**' section found in block")
    tail = block[claims_match.end():]
    end = tail.find("\n---")
    if end != -1:
        tail = tail[:end]
    claims = []
    for m in _CLAIM_LINE_RE.finditer(tail):
        _, _warn_flag, text = m.groups()
        cleaned = _clean_claim_text(text)
        if cleaned:
            claims.append(cleaned)
    return claims


def _parse_file(path: Path) -> list[ParsedQuestion]:
    text = path.read_text(encoding="utf-8")
    results = []
    for block in _split_question_blocks(text):
        header = _QUESTION_HEADER_RE.match(block)
        if not header:
            continue
        qid = header.group(1)
        try:
            answer = _extract_answer(block)
            claims = _extract_claims(block)
        except ValueError as e:
            raise ValueError(f"{path.name}: failed to parse {qid}: {e}") from e
        results.append(
            ParsedQuestion(
                question_id=qid,
                source_text=answer,
                claims=claims,
                excluded=EXCLUSION_MARKER in block,
                source_file=path.name,
            )
        )
    return results


# --- Public API --------------------------------------------------------


def build_gold_validation_set(corpus_path: Path) -> list[KDExample]:
    """Load O9 as the Gold/Validation set (D55). Never used for
    training -- see check_o9_not_in_training."""
    parsed = _parse_file(corpus_path / GOLD_FILENAME)
    return [
        KDExample(question_id=p.question_id, source_text=p.source_text, claims=p.claims)
        for p in parsed
    ]


def build_kd_dataset(
    corpus_path: Path,
    annotation_rules: AnnotationRules,
) -> list[KDExample]:
    """Build the Knowledge-Distillation training corpus from the five
    LLM-assisted, human-reviewed batch files (D55), excluding any
    question explicitly flagged as excluded (e.g. GN-050).

    `annotation_rules` enforcement here is a LIGHTWEIGHT SANITY CHECK,
    not a re-derivation of R1-R6 -- the actual rules were applied during
    human review of each batch file. Only enforce_self_containment is
    currently checked (weak heuristic: claim length + no bare pronoun
    opener). Other flags are accepted but not independently re-verified.
    """
    examples: list[KDExample] = []
    excluded_log: list[str] = []

    for filename in TRAIN_FILENAMES:
        for p in _parse_file(corpus_path / filename):
            if p.excluded:
                excluded_log.append(f"{p.question_id} ({filename})")
                continue
            if annotation_rules.enforce_self_containment:
                for c in p.claims:
                    if len(c) < 8 or c.split()[0] in {"هو", "هي", "ذلك", "هذا", "هذه"}:
                        raise ValueError(
                            f"{p.question_id}: claim fails weak self-containment "
                            f"heuristic: {c!r}"
                        )
            examples.append(
                KDExample(question_id=p.question_id, source_text=p.source_text, claims=p.claims)
            )

    check_o9_not_in_training(corpus_path, examples)

    if excluded_log:
        print(f"[dataset_builder] excluded {len(excluded_log)} flagged question(s): "
              f"{', '.join(excluded_log)}")

    return examples


def check_o9_not_in_training(corpus_path: Path, examples: list[KDExample]) -> None:
    """Guard against O9 (Gold/Validation set, D55) leaking into the
    training corpus -- same pattern as
    interview_iq.nli.dataset.check_ds014_exclusion (D28)."""
    gold_ids = {e.question_id for e in build_gold_validation_set(corpus_path)}
    train_ids = {e.question_id for e in examples}
    overlap = gold_ids & train_ids
    if overlap:
        raise ValueError(f"Gold/Validation set (O9) leaked into training corpus: {sorted(overlap)}")


if __name__ == "__main__":
    import sys

    corpus_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("results")
    rules = AnnotationRules(
        preserve_hedging=True,
        generalise_personal_framing=True,
        no_unverifiable_causal_bridge=True,
        enforce_self_containment=True,
    )

    gold = build_gold_validation_set(corpus_path)
    train = build_kd_dataset(corpus_path, rules)

    print(f"Gold/Validation set (O9): {len(gold)} questions, {sum(len(e.claims) for e in gold)} claims")
    print(f"Training corpus: {len(train)} questions, {sum(len(e.claims) for e in train)} claims")
    print()
    print("Sample training example:")
    sample = train[0]
    print(f"  {sample.question_id}: {sample.source_text[:80]}...")
    for c in sample.claims[:3]:
        print(f"    - {c}")