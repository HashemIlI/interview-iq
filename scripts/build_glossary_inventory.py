"""
D97 Step 0 — deterministic glossary term inventory.

Extracts every Latin-script token from the content-bearing text fields of
the reference-docs corpus (data/refdocs/reference_docs_250_FINAL_v1.json,
schema per src/interview_iq/refdocs/loader.py) with NO semantic filtering.
This is a pure frequency inventory, not a curated glossary -- filtering
(stopwords, "is this a real term") is deliberately deferred to a later,
separate, human-reviewed step so that step can be audited against the full
unfiltered list. See decisions.md D96/D97.

Fields extracted from (content-bearing text only):
    - documents[i].question
    - documents[i].chunks[j].text
Fields explicitly excluded (structural/metadata, not candidate content):
    - meta.*
    - documents[i].question_id, documents[i].track
    - documents[i].chunks[j].chunk_id
    - documents[i].key_points

Trailing "." "_" "-" characters are stripped from every extracted token
before counting (sentence-final punctuation is not part of the term).
"+" and "#" are never stripped (C++, C# must survive intact).

In addition to single tokens, multi-token Latin sequences (two to four
consecutive Latin tokens separated by exactly one space, e.g. "Machine
Learning") are extracted as phrase candidates, since single-token
extraction destroys them.

Usage:
    python scripts/build_glossary_inventory.py

Output:
    results/glossary/term_inventory_v1.json
    results/glossary/term_inventory_v1.tsv
    results/glossary/phrase_inventory_v1.tsv
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_REFDOCS_PATH = _REPO_ROOT / "data" / "refdocs" / "reference_docs_250_FINAL_v1.json"
_OUTPUT_DIR = _REPO_ROOT / "results" / "glossary"

_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9+#._-]*")
_RUN_RE = re.compile(r"[A-Za-z][A-Za-z0-9+#._-]*(?: [A-Za-z][A-Za-z0-9+#._-]*)*")
_TRAILING_STRIP_CHARS = "._-"
_MIN_TOKEN_LEN = 2
_MAX_PHRASE_LEN = 4


def _strip_trailing_punct(token: str) -> str:
    while token and token[-1] in _TRAILING_STRIP_CHARS:
        token = token[:-1]
    return token


def _extract_tokens(text: str) -> list[str]:
    tokens = []
    for raw in _TOKEN_RE.findall(text):
        cleaned = _strip_trailing_punct(raw)
        if len(cleaned) < _MIN_TOKEN_LEN:
            continue
        tokens.append(cleaned)
    return tokens


def _extract_phrases(text: str) -> list[str]:
    """Two-to-four-token Latin sequences separated by exactly one space."""
    phrases: list[str] = []
    for match in _RUN_RE.finditer(text):
        raw_words = match.group(0).split(" ")

        # Clean each word; a word that collapses below the minimum length
        # breaks the run at that point (it is not a valid token).
        subruns: list[list[str]] = [[]]
        for raw_word in raw_words:
            cleaned = _strip_trailing_punct(raw_word)
            if len(cleaned) < _MIN_TOKEN_LEN:
                subruns.append([])
                continue
            subruns[-1].append(cleaned)

        for subrun in subruns:
            n = len(subrun)
            if n < 2:
                continue
            max_len = min(_MAX_PHRASE_LEN, n)
            for window in range(2, max_len + 1):
                for i in range(0, n - window + 1):
                    phrases.append(" ".join(subrun[i : i + window]))

    return phrases


def _load_documents(refdocs_path: Path) -> list[dict]:
    if not refdocs_path.is_file():
        raise FileNotFoundError(f"Reference docs file not found: {refdocs_path}")

    with refdocs_path.open("r", encoding="utf-8") as fh:
        raw = json.load(fh)

    return raw["documents"]


def _text_fields(doc: dict) -> list[str]:
    fields = [doc["question"]]
    for chunk in doc["chunks"]:
        fields.append(chunk["text"])
    return fields


def build_inventory(documents: list[dict]) -> list[dict]:
    total_occurrences: Counter[str] = Counter()
    doc_sets: dict[str, set[str]] = defaultdict(set)
    casing_counts: dict[str, Counter[str]] = defaultdict(Counter)

    for doc in documents:
        question_id = doc["question_id"]

        for text in _text_fields(doc):
            for token in _extract_tokens(text):
                key = token.lower()
                total_occurrences[key] += 1
                doc_sets[key].add(question_id)
                casing_counts[key][token] += 1

    inventory = []
    for key, count in total_occurrences.items():
        display_form = casing_counts[key].most_common(1)[0][0]
        inventory.append(
            {
                "term": display_form,
                "total_occurrences": count,
                "n_documents": len(doc_sets[key]),
            }
        )

    return inventory


def build_phrase_inventory(documents: list[dict]) -> list[dict]:
    total_occurrences: Counter[str] = Counter()
    doc_sets: dict[str, set[str]] = defaultdict(set)
    casing_counts: dict[str, Counter[str]] = defaultdict(Counter)

    for doc in documents:
        question_id = doc["question_id"]

        for text in _text_fields(doc):
            for phrase in _extract_phrases(text):
                key = phrase.lower()
                total_occurrences[key] += 1
                doc_sets[key].add(question_id)
                casing_counts[key][phrase] += 1

    inventory = []
    for key, count in total_occurrences.items():
        display_form = casing_counts[key].most_common(1)[0][0]
        inventory.append(
            {
                "term": display_form,
                "total_occurrences": count,
                "n_documents": len(doc_sets[key]),
            }
        )

    return inventory


def write_json(inventory: list[dict], out_path: Path) -> None:
    out_path.write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def write_tsv(inventory: list[dict], out_path: Path) -> None:
    rows = sorted(inventory, key=lambda r: (-r["total_occurrences"], r["term"]))
    lines = ["term\ttotal_occurrences\tn_documents"]
    for r in rows:
        lines.append(f"{r['term']}\t{r['total_occurrences']}\t{r['n_documents']}")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    documents = _load_documents(_REFDOCS_PATH)

    inventory = build_inventory(documents)
    phrase_inventory = build_phrase_inventory(documents)

    _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(inventory, _OUTPUT_DIR / "term_inventory_v1.json")
    write_tsv(inventory, _OUTPUT_DIR / "term_inventory_v1.tsv")
    write_tsv(phrase_inventory, _OUTPUT_DIR / "phrase_inventory_v1.tsv")

    total_unique = len(inventory)
    n_ge_2 = sum(1 for r in inventory if r["n_documents"] >= 2)
    n_ge_5 = sum(1 for r in inventory if r["n_documents"] >= 5)
    n_ge_10 = sum(1 for r in inventory if r["n_documents"] >= 10)

    print("Single-token inventory (after trailing-punctuation-strip fix):")
    print(f"  Total unique terms: {total_unique}")
    print(f"  Terms with n_documents >= 2: {n_ge_2}")
    print(f"  Terms with n_documents >= 5: {n_ge_5}")
    print(f"  Terms with n_documents >= 10: {n_ge_10}")

    total_phrases = len(phrase_inventory)
    p_ge_2 = sum(1 for r in phrase_inventory if r["n_documents"] >= 2)
    p_ge_5 = sum(1 for r in phrase_inventory if r["n_documents"] >= 5)

    print("Phrase inventory (2-4 token Latin sequences, single-space separated):")
    print(f"  Total unique phrases: {total_phrases}")
    print(f"  Phrases with n_documents >= 2: {p_ge_2}")
    print(f"  Phrases with n_documents >= 5: {p_ge_5}")

    print(f"Output written to: {_OUTPUT_DIR}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
