"""Pure deterministic Gold v1 extraction helpers for D68.

This module contains no semantic pass, classification, rationale,
independent-test answer, or source-support judgment. It parses only the five
frozen Gold v1 files and exposes exact evidence to separately authored passes.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from interview_iq.decomposition.dataset_builder import TRAIN_FILENAMES, _parse_file  # noqa: E402

EXPECTED_HEAD = "2e29c065222b72633250c2402604f7aed545ec7d"
EXPECTED_DECISIONS_SHA256 = "8f810336a744279e62bc15faf6e3af5f51377d88dd5b763237db119e7b4f6686"
EXPECTED_EXAMPLES = 222
EXPECTED_CLAIMS = 1836

GOLD_FILES = [
    "results/pilot_llm_assisted_batch1_DRAFT_UNREVIEWED.md",
    "results/pilot_llm_assisted_batch2_DRAFT_UNREVIEWED.md",
    "results/pilot_llm_assisted_batch3_DRAFT_UNREVIEWED.md",
    "results/pilot_llm_assisted_batch4_DRAFT_UNREVIEWED.md",
    "results/pilot_llm_assisted_batch5_DRAFT_UNREVIEWED.md",
]

EXPECTED_GOLD_SHA256 = {
    GOLD_FILES[0]: "2ae700cbeacd6ec9b04efa686a4caae02a240363fe845a6f9760e45850ef172c",
    GOLD_FILES[1]: "b0da2c26ec1456ba656045813e3373041b793d9561b9b7862ffc49c5af24f274",
    GOLD_FILES[2]: "5e201144828e1d70b28e2780d10e93dc05d42792160458ea5fd9358f973591cc",
    GOLD_FILES[3]: "5a2226e9ffdacb969027d5635cc3f31b6eeb4a233e5ab66aead4b3bb75695761",
    GOLD_FILES[4]: "fea0be20aabfae9004b249cbc968aa7f11aeecc1b4423f1aabc0458cf6523163",
}

FROZEN_KEYS = [
    "SE-049:6", "DS-003:3", "CS-003:1", "SE-003:5", "SE-033:1",
    "GN-006:5", "GN-028:2", "GN-046:1", "DA-038:4", "DA-038:5",
    "DA-049:5", "CS-010:1", "CS-049:4", "SE-035:1", "GN-002:1",
    "GN-002:3", "GN-038:3", "DA-017:6", "DS-038:1", "CS-001:4",
    "CS-032:2", "SE-030:5", "SE-047:3", "GN-009:4", "DA-037:5",
    "DA-041:7", "SE-022:4", "SE-029:5", "SE-032:2", "SE-032:3",
    "SE-032:8", "GN-015:3", "GN-037:2", "GN-048:4",
]

NON_ATOMIC = "NON_ATOMIC_REPAIR_REQUIRED"
INTEGRATED = "INTEGRATED_SINGLE_CLAIM_FALSE_POSITIVE"
ALLOWED_CLASSIFICATIONS = {NON_ATOMIC, INTEGRATED}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def write_json(path: Path, payload: object) -> None:
    write_text(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def fail(message: str) -> None:
    raise RuntimeError(message)


def linguistic_flags(claim: str) -> dict[str, bool]:
    padded = f" {claim} "
    return {
        "uncertainty_present": any(marker in padded for marker in ("قد ", "غالبًا", "شبه")),
        "negation_present": any(marker in padded for marker in (" لا ", "لم ", "لن ", "ليس", "دون ", "عدم ", "غير ", "يمنع", "تمنع")),
        "approximation_present": any(marker in padded for marker in ("غالبًا", "شبه", "تقريب")),
    }


def extract_candidates() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Extract exact source/claim evidence without making semantic judgments."""
    if list(TRAIN_FILENAMES) != [Path(name).name for name in GOLD_FILES]:
        fail("The repository parser's training filenames differ from frozen Gold v1")
    if sha256(REPO_ROOT / "decisions.md") != EXPECTED_DECISIONS_SHA256:
        fail("decisions.md changed")

    questions: dict[str, object] = {}
    gold_verification: list[dict[str, object]] = []
    example_count = 0
    claim_count = 0
    accessed_paths: list[str] = []

    for relative_path in GOLD_FILES:
        path = REPO_ROOT / relative_path
        actual_hash = sha256(path)
        if actual_hash != EXPECTED_GOLD_SHA256[relative_path]:
            fail(f"Gold v1 file changed: {relative_path}: {actual_hash}")
        parsed = _parse_file(path)
        included = [question for question in parsed if not question.excluded]
        accessed_paths.append(relative_path)
        gold_verification.append({
            "relative_path": relative_path,
            "size_bytes": path.stat().st_size,
            "sha256": actual_hash,
            "parsed_questions": len(parsed),
            "included_questions": len(included),
            "included_claims": sum(len(question.claims) for question in included),
            "unchanged": True,
        })
        for question in included:
            if question.question_id in questions:
                fail(f"Duplicate included question ID: {question.question_id}")
            questions[question.question_id] = question
            example_count += 1
            claim_count += len(question.claims)

    if accessed_paths != GOLD_FILES:
        fail("Unexpected extraction path access")
    if (example_count, claim_count) != (EXPECTED_EXAMPLES, EXPECTED_CLAIMS):
        fail(f"Unexpected corpus counts: {example_count} examples, {claim_count} claims")

    candidates: list[dict[str, object]] = []
    seen: set[str] = set()
    for key in FROZEN_KEYS:
        question_id, raw_index = key.split(":", 1)
        claim_index = int(raw_index)
        question = questions.get(question_id)
        if question is None:
            fail(f"Unresolved frozen candidate: {key}")
        if claim_index < 1 or claim_index > len(question.claims):
            fail(f"Invalid frozen claim index: {key}")
        if key in seen:
            fail(f"Duplicate frozen key: {key}")
        seen.add(key)
        exact_claim = question.claims[claim_index - 1]
        candidates.append({
            "candidate_key": key,
            "question_id": question_id,
            "track": question_id.split("-", 1)[0],
            "claim_index": claim_index,
            "source_file": f"results/{question.source_file}",
            "source_file_sha256": EXPECTED_GOLD_SHA256[f"results/{question.source_file}"],
            "exact_source_answer": question.source_text,
            "exact_claim_text": exact_claim,
            "previous_claim": question.claims[claim_index - 2] if claim_index > 1 else None,
            "next_claim": question.claims[claim_index] if claim_index < len(question.claims) else None,
            **linguistic_flags(exact_claim),
        })

    if [item["candidate_key"] for item in candidates] != FROZEN_KEYS:
        fail("Candidate order differs from the frozen order")
    return candidates, gold_verification
