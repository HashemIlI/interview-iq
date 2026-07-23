"""
D97 Step 4 (revised) -- deterministic safety filters over the authored
transliteration glossary (data/glossary/transliteration_glossary.json).

Applies, in order, over the authored entries:
    R-A (collision):  two distinct terms whose forms RAW-normalize (diacritics
                       stripped, alef variants unified -- NO proclitic
                       stripping) to the same Arabic string -- BOTH terms are
                       removed entirely. Proclitic stripping is deliberately
                       excluded here: the first implementation used it for
                       collision detection and produced eight false-positive
                       removals (Bash/Cache, Code/Pod, FIFO/LIFO, Queue/View/
                       Vue, catch/Batch/Patch) because a term's own initial
                       root consonant coincided with one of the six proclitic
                       letters and got stripped as if it were a clitic,
                       collapsing unrelated words onto the same "core".
                       Proclitic stripping remains correct and necessary for
                       RUNTIME matching (transliteration.py), where it
                       handles a real attached prefix on an already-known
                       word; it is the wrong tool for deciding whether two
                       DIFFERENT English terms sound alike in Arabic.
    R-B (lexical):    a surviving form whose raw-normalized string occurs as
                       a standalone token anywhere in the Arabic prose
                       (question text + chunk text) of the 250 reference
                       documents -- removed (it is a real Arabic word, at
                       least in this domain's technical prose).
    R-D (lexicon):    a surviving form whose raw-normalized string occurs in
                       the general Arabic wordlist (data/glossary/
                       arabic_wordlist.txt, MIT-licensed, ~3.49M entries --
                       see decisions.md D97 revision note) -- removed, same
                       reasoning as R-B but against general vocabulary
                       rather than just this project's technical prose.
    R-C (length):     a surviving form whose RAW authored length is <= 4
                       characters is removed. Raised from the original "<= 2"
                       threshold: the wordlist (R-D) is predominantly Modern
                       Standard Arabic and will not catch Egyptian colloquial
                       homographs of short technical loanwords -- the length
                       rule is the deterministic backstop for that gap. The
                       threshold is 4, not 5, specifically so that
                       article-carrying forms (5 characters, e.g. the
                       definite-article spellings of "test" and "code")
                       survive while their bare 2-3 character stems do not
                       silently pass as "long enough" on their own.

Filter order: R-A, then R-B, then R-D, then R-C -- each applied over the
forms still surviving after the previous rule. A term with zero surviving
forms after all four is dropped from the glossary entirely. Terms authored
with an empty forms list from the start are not candidates and are silently
omitted from both "entries" and "ambiguous" -- they were never proposed, so
they are not "removed".

Normalization used by R-A/R-B/R-D (normalize_arabic): strip Arabic
diacritics, unify alef variants (hamza-on-alif / hamza-under-alif / madda ->
plain alif). No proclitic stripping -- see the R-A section above for why.
R-C measures the raw authored form length, not the normalized string.

Usage:
    python scripts/filter_glossary.py

Output (overwritten in place):
    data/glossary/transliteration_glossary.json  -- "entries" replaced with
        survivors, "ambiguous" populated.
    results/glossary/filter_report_v2.txt        -- full human-readable report.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_GLOSSARY_PATH = _REPO_ROOT / "data" / "glossary" / "transliteration_glossary.json"
_REFDOCS_PATH = _REPO_ROOT / "data" / "refdocs" / "reference_docs_250_FINAL_v1.json"
_WORDLIST_PATH = _REPO_ROOT / "data" / "glossary" / "arabic_wordlist.txt"
_REPORT_PATH = _REPO_ROOT / "results" / "glossary" / "filter_report_v2.txt"

_DIACRITICS_RE = re.compile(
    "[ؐ-ًؚ-ٰٟۖ-ۜ۟-۪ۨ-ۭـ]"
)
_ALEF_TRANSLATION = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا"})
_PROCLITICS = ("ال", "و", "ب", "ك", "ل", "ف")  # al, wa, bi, ka, li, fa -- "al" checked first (2 chars)
_R_C_MAX_LEN = 4

_TOKEN_RE = re.compile(r"[^\s.,!?؛،:؟()\[\]{}\"'«»…\-–—]+")


def normalize_arabic(text: str) -> str:
    """Diacritics stripped + alef variants unified. No proclitic stripping.
    This is the ONLY normalization used for collision detection (R-A, R-B,
    R-D). Proclitic stripping is a separate, runtime-only concern -- see
    strip_proclitic below and the module docstring's R-A section."""
    text = _DIACRITICS_RE.sub("", text)
    text = text.translate(_ALEF_TRANSLATION)
    return text.strip()


def strip_proclitic(word: str) -> str:
    """Runtime-matching helper only (used by transliteration.py). Must NOT
    be used for collision detection -- see module docstring."""
    for prefix in _PROCLITICS:
        if word.startswith(prefix) and len(word) - len(prefix) >= 2:
            return word[len(prefix):]
    return word


def build_corpus_token_cores(refdocs_path: Path) -> set[str]:
    with refdocs_path.open("r", encoding="utf-8") as fh:
        raw = json.load(fh)

    cores: set[str] = set()
    for doc in raw["documents"]:
        text_fields = [doc["question"]] + [chunk["text"] for chunk in doc["chunks"]]
        for text in text_fields:
            for token in _TOKEN_RE.findall(text):
                cores.add(normalize_arabic(token))
    return cores


def load_wordlist_cores(wordlist_path: Path) -> set[str]:
    cores: set[str] = set()
    with wordlist_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            word = line.strip()
            if word:
                cores.add(normalize_arabic(word))
    return cores


def apply_filters(
    authored_entries: list[dict],
    corpus_token_cores: set[str],
    wordlist_cores: set[str],
) -> tuple[list[dict], list[dict]]:
    # Only terms proposed with at least one form are candidates.
    candidates = [e for e in authored_entries if e["forms"]]

    # ---- R-A: cross-term collision on RAW normalized form (no proclitic stripping) ----
    core_to_terms: dict[str, set[str]] = defaultdict(set)
    for entry in candidates:
        for form in entry["forms"]:
            core_to_terms[normalize_arabic(form)].add(entry["term"])

    colliding_terms: dict[str, set[str]] = defaultdict(set)  # term -> set of terms it collides with
    for core, terms in core_to_terms.items():
        if len(terms) > 1:
            for t in terms:
                colliding_terms[t] |= terms - {t}

    ambiguous: list[dict] = []
    surviving: dict[str, list[str]] = {}

    for entry in candidates:
        term = entry["term"]
        if term in colliding_terms:
            for form in entry["forms"]:
                ambiguous.append(
                    {
                        "term": term,
                        "form": form,
                        "rule": "R-A",
                        "colliding_term": ", ".join(sorted(colliding_terms[term])),
                    }
                )
            continue
        surviving[term] = list(entry["forms"])

    # ---- R-B: lexical collision with real corpus Arabic words -------------
    after_rb: dict[str, list[str]] = {}
    for term, forms in surviving.items():
        keep: list[str] = []
        for form in forms:
            if normalize_arabic(form) in corpus_token_cores:
                ambiguous.append({"term": term, "form": form, "rule": "R-B"})
            else:
                keep.append(form)
        if keep:
            after_rb[term] = keep

    # ---- R-D: lexical collision with the general Arabic wordlist ----------
    after_rd: dict[str, list[str]] = {}
    for term, forms in after_rb.items():
        keep = []
        for form in forms:
            if normalize_arabic(form) in wordlist_cores:
                ambiguous.append({"term": term, "form": form, "rule": "R-D"})
            else:
                keep.append(form)
        if keep:
            after_rd[term] = keep

    # ---- R-C: raw form length <= 4 ------------------------------------------
    after_rc: dict[str, list[str]] = {}
    for term, forms in after_rd.items():
        keep = []
        for form in forms:
            if len(form) <= _R_C_MAX_LEN:
                ambiguous.append({"term": term, "form": form, "rule": "R-C"})
            else:
                keep.append(form)
        if keep:
            after_rc[term] = keep

    surviving_entries = [{"term": term, "forms": forms} for term, forms in after_rc.items()]
    return surviving_entries, ambiguous


def write_report(
    report_path: Path,
    n_authored: int,
    n_empty: int,
    n_candidates: int,
    surviving_entries: list[dict],
    ambiguous: list[dict],
) -> None:
    n_ra = sum(1 for a in ambiguous if a["rule"] == "R-A")
    n_rb = sum(1 for a in ambiguous if a["rule"] == "R-B")
    n_rd = sum(1 for a in ambiguous if a["rule"] == "R-D")
    n_rc = sum(1 for a in ambiguous if a["rule"] == "R-C")

    surviving_by_term = {e["term"]: e["forms"] for e in surviving_entries}
    ambiguous_by_term: dict[str, list[dict]] = defaultdict(list)
    for a in ambiguous:
        ambiguous_by_term[a["term"]].append(a)

    def term_status(term: str) -> str:
        if term in surviving_by_term:
            return f"SURVIVES with forms {surviving_by_term[term]!r}"
        if term in ambiguous_by_term:
            rules = sorted({a["rule"] for a in ambiguous_by_term[term]})
            details = "; ".join(f"{a['form']!r} removed by {a['rule']}" for a in ambiguous_by_term[term])
            return f"REMOVED entirely (rule(s) {rules}) -- {details}"
        return "NOT A CANDIDATE (authored with empty forms, or term not present)"

    lines = []
    lines.append("D97 Step 4 (revised) -- Glossary filter report (R-A / R-B / R-D / R-C)")
    lines.append("=" * 72)
    lines.append(f"Terms authored (total entries in inventory): {n_authored}")
    lines.append(f"Terms with empty forms (not candidates):     {n_empty}")
    lines.append(f"Terms proposed with >=1 form (candidates):   {n_candidates}")
    lines.append(f"Terms surviving all filters:                 {len(surviving_entries)}")
    lines.append(f"Forms removed by R-A (cross-term collision, raw-normalized): {n_ra}")
    lines.append(f"Forms removed by R-B (real corpus word):                     {n_rb}")
    lines.append(f"Forms removed by R-D (general Arabic wordlist):              {n_rd}")
    lines.append(f"Forms removed by R-C (length <= {_R_C_MAX_LEN}):                            {n_rc}")
    lines.append(f"Total ambiguous form-records:                                {len(ambiguous)}")
    lines.append("")
    lines.append("-" * 72)
    lines.append("Full list of R-A collisions (term <-> colliding term(s), form)")
    lines.append("-" * 72)
    ra_items = [a for a in ambiguous if a["rule"] == "R-A"]
    if not ra_items:
        lines.append("(none)")
    else:
        for item in sorted(ra_items, key=lambda a: (a["term"], a["form"])):
            lines.append(f"  {item['term']!r} <-> {item['colliding_term']!r}  (form: {item['form']!r})")

    lines.append("")
    lines.append("-" * 72)
    lines.append("Final status of specific terms of interest")
    lines.append("-" * 72)
    for term in ["bit", "Byte", "Test", "Code", "Database", "Stack", "Queue", "FIFO", "LIFO", "Worm", "Scan", "RAM"]:
        lines.append(f"  {term}: {term_status(term)}")

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    with _GLOSSARY_PATH.open("r", encoding="utf-8") as fh:
        glossary = json.load(fh)

    authored_entries = glossary["entries"]
    n_authored = len(authored_entries)
    n_empty = sum(1 for e in authored_entries if not e["forms"])
    n_candidates = n_authored - n_empty

    corpus_token_cores = build_corpus_token_cores(_REFDOCS_PATH)
    wordlist_cores = load_wordlist_cores(_WORDLIST_PATH)
    surviving_entries, ambiguous = apply_filters(authored_entries, corpus_token_cores, wordlist_cores)

    glossary["entries"] = sorted(surviving_entries, key=lambda e: e["term"])
    glossary["ambiguous"] = sorted(ambiguous, key=lambda a: (a["rule"], a["term"], a["form"]))

    with _GLOSSARY_PATH.open("w", encoding="utf-8") as fh:
        json.dump(glossary, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    write_report(_REPORT_PATH, n_authored, n_empty, n_candidates, surviving_entries, ambiguous)

    print(f"Terms authored: {n_authored}")
    print(f"Terms with empty forms: {n_empty}")
    print(f"Terms proposed with >=1 form: {n_candidates}")
    print(f"Terms surviving all filters: {len(surviving_entries)}")
    n_ra = sum(1 for a in ambiguous if a["rule"] == "R-A")
    n_rb = sum(1 for a in ambiguous if a["rule"] == "R-B")
    n_rd = sum(1 for a in ambiguous if a["rule"] == "R-D")
    n_rc = sum(1 for a in ambiguous if a["rule"] == "R-C")
    print(f"Removed by R-A: {n_ra}")
    print(f"Removed by R-B: {n_rb}")
    print(f"Removed by R-D: {n_rd}")
    print(f"Removed by R-C: {n_rc}")
    print(f"Report written to: {_REPORT_PATH}")
    print(f"Glossary rewritten at: {_GLOSSARY_PATH}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
