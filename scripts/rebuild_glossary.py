"""
D98 glossary rebuild -- applies the H-1 human adjudication and V-1 survivor
verification results to data/glossary/transliteration_glossary.json.

Reads:
    data/glossary/transliteration_glossary.json     (pre-adjudication glossary)
    results/glossary/adjudication_H1_v1.tsv         (362 R-B/R-D records, human verdict)
    results/glossary/verification_V1_v1.tsv         (164 survivor records, human verdict)

Construction rules (decisions.md D98 + its R-C amendment):
    KEEP set  = (surviving forms MINUS forms marked AMBIGUOUS in V-1)
                UNION (forms marked KEEP in H-1)
    AMBIGUOUS = all R-A records (16) + the R-C record (1)
                + H-1 AMBIGUOUS (4) + V-1 AMBIGUOUS (1)

R-B and R-D are deleted rules (D98): their old ambiguous records are
entirely superseded by the H-1 verdicts on the same 362-record set. No
completion step is run -- no form is generated that was not authored.
R-C no longer vetoes a form carrying a human verdict; the single surviving
R-C record (Scrum / سكرم) is carried forward unchanged because it was never
placed before an adjudicator.

Writes data/glossary/transliteration_glossary.json in place, preserving the
existing schema: top-level meta / entries / ambiguous; each entry
{"term", "forms"}; each ambiguous record {"term", "form", "rule"[,
"colliding_term"]}.

All construction counts are asserted against the values pre-registered in
decisions.md D98 and its amendment BEFORE the file is written. A mismatch
aborts with no write.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_GLOSSARY_PATH = _REPO_ROOT / "data" / "glossary" / "transliteration_glossary.json"
_H1_PATH = _REPO_ROOT / "results" / "glossary" / "adjudication_H1_v1.tsv"
_V1_PATH = _REPO_ROOT / "results" / "glossary" / "verification_V1_v1.tsv"

sys.path.insert(0, str(_REPO_ROOT / "src"))
from interview_iq.decomposition_llm.transliteration import normalize_arabic  # noqa: E402


def _read_tsv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def build_glossary() -> dict:
    with _GLOSSARY_PATH.open("r", encoding="utf-8") as fh:
        old = json.load(fh)

    h1_rows = _read_tsv(_H1_PATH)
    v1_rows = _read_tsv(_V1_PATH)
    assert len(h1_rows) == 362, f"expected 362 H-1 rows, got {len(h1_rows)}"
    assert len(v1_rows) == 164, f"expected 164 V-1 rows, got {len(v1_rows)}"

    # term -> ordered list of raw forms, seeded from the pre-adjudication survivors.
    term_forms: dict[str, list[str]] = {
        entry["term"]: list(entry["forms"]) for entry in old["entries"]
    }

    new_ambiguous: list[dict] = []

    # Carry forward R-A (permanent, not adjudicable) and R-C (backstop, no
    # human verdict on this record) ambiguous records unchanged.
    for item in old["ambiguous"]:
        if item["rule"] in ("R-A", "R-C"):
            new_ambiguous.append(dict(item))

    # V-1: remove forms verified AMBIGUOUS from the survivor set.
    v1_ambiguous_count = 0
    for row in v1_rows:
        if row["verdict"] == "AMBIGUOUS":
            v1_ambiguous_count += 1
            term, form = row["term"], row["form"]
            forms = term_forms.get(term, [])
            assert form in forms, f"V-1 AMBIGUOUS form not found in survivors: {term}/{form}"
            forms.remove(form)
            new_ambiguous.append({"term": term, "form": form, "rule": "V-1"})

    # H-1: KEEP restores a form; AMBIGUOUS records the form as ambiguous.
    h1_keep_count = 0
    h1_ambiguous_count = 0
    for row in h1_rows:
        term, form = row["term"], row["form"]
        if row["verdict"] == "KEEP":
            h1_keep_count += 1
            forms = term_forms.setdefault(term, [])
            assert form not in forms, f"H-1 KEEP form already present: {term}/{form}"
            forms.append(form)
        elif row["verdict"] == "AMBIGUOUS":
            h1_ambiguous_count += 1
            new_ambiguous.append({"term": term, "form": form, "rule": "H-1"})
        else:
            raise AssertionError(f"unexpected H-1 verdict {row['verdict']!r} for {term}/{form}")

    # Drop any term left with zero KEEP forms (e.g. List, both forms AMBIGUOUS).
    final_term_forms = {t: fs for t, fs in term_forms.items() if fs}

    new_entries = [
        {"term": term, "forms": final_term_forms[term]}
        for term in sorted(final_term_forms)
    ]

    new_meta = dict(old["meta"])
    new_meta["version"] = 2
    new_meta["authored_by"] = (
        "forms authored by a build-time LLM (Claude Code); adjudicated by a "
        "human (Ahmed) under D98 H-1 (adjudication) and V-1 (verification)"
    )

    return {
        "meta": new_meta,
        "entries": new_entries,
        "ambiguous": new_ambiguous,
        "_diagnostics": {
            "h1_keep_count": h1_keep_count,
            "h1_ambiguous_count": h1_ambiguous_count,
            "v1_ambiguous_count": v1_ambiguous_count,
        },
    }


def _rule_counts(ambiguous: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in ambiguous:
        counts[item["rule"]] = counts.get(item["rule"], 0) + 1
    return counts


def run_assertions(glossary: dict) -> None:
    entries = glossary["entries"]
    ambiguous = glossary["ambiguous"]

    keep_form_records = sum(len(e["forms"]) for e in entries)
    keep_terms = len(entries)
    ambiguous_records = len(ambiguous)
    rule_counts = _rule_counts(ambiguous)

    raw_form_to_terms: dict[str, set[str]] = {}
    for e in entries:
        for form in e["forms"]:
            raw_form_to_terms.setdefault(form, set()).add(e["term"])
    shared_raw_forms = sum(1 for terms in raw_form_to_terms.values() if len(terms) > 1)

    normalized_to_terms: dict[str, set[str]] = {}
    for e in entries:
        for form in e["forms"]:
            key = normalize_arabic(form)
            normalized_to_terms.setdefault(key, set()).add(e["term"])
    distinct_normalized_keys = len(normalized_to_terms)
    normalized_keys_multi_term = sum(
        1 for terms in normalized_to_terms.values() if len(terms) > 1
    )

    checks = [
        ("KEEP form-records", keep_form_records, 1791),
        ("KEEP terms", keep_terms, 892),
        ("AMBIGUOUS records", ambiguous_records, 22),
        ("AMBIGUOUS R-A", rule_counts.get("R-A", 0), 16),
        ("AMBIGUOUS R-C", rule_counts.get("R-C", 0), 1),
        ("AMBIGUOUS H-1", rule_counts.get("H-1", 0), 4),
        ("AMBIGUOUS V-1", rule_counts.get("V-1", 0), 1),
        ("raw forms shared by >1 term", shared_raw_forms, 0),
        ("distinct normalised KEEP keys", distinct_normalized_keys, 1791),
        ("normalised keys mapping to >1 term", normalized_keys_multi_term, 0),
    ]

    failures = [
        f"  {name}: expected {expected}, got {actual}"
        for name, actual, expected in checks
        if actual != expected
    ]

    print("Rebuild assertion checks:")
    for name, actual, expected in checks:
        status = "OK" if actual == expected else "FAIL"
        print(f"  [{status}] {name}: {actual} (expected {expected})")

    if failures:
        raise AssertionError("Rebuild assertions failed:\n" + "\n".join(failures))


def main() -> None:
    glossary = build_glossary()
    run_assertions(glossary)

    # Diagnostics block is informational only -- not part of the on-disk schema.
    glossary.pop("_diagnostics")

    with _GLOSSARY_PATH.open("w", encoding="utf-8") as fh:
        json.dump(glossary, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    print(f"\nWrote {_GLOSSARY_PATH}")


if __name__ == "__main__":
    main()
