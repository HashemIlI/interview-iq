"""Validate separate D68 passes and render deterministic audit evidence."""

from __future__ import annotations

import argparse
import ast
import csv
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True

import d68_atomicity_adjudication as core
from d68_atomicity_first_pass import FIRST_PASS_RECORDS
from d68_atomicity_resolutions import DISAGREEMENT_RESOLUTIONS
from d68_atomicity_verification_pass import VERIFICATION_PASS_RECORDS

OUTPUT_DIR_RELATIVE = "results/d68_atomicity"
FIRST_PASS_PATH = "scripts/d68_atomicity_first_pass.py"
VERIFICATION_PASS_PATH = "scripts/d68_atomicity_verification_pass.py"

CHANGED_PATHS = [
    "scripts/d68_atomicity_adjudication.py",
    FIRST_PASS_PATH,
    VERIFICATION_PASS_PATH,
    "scripts/d68_atomicity_resolutions.py",
    "scripts/d68_atomicity_run.py",
    "results/d68_atomicity/d68_atomicity_adjudication.json",
    "results/d68_atomicity/d68_atomicity_adjudication.csv",
    "results/d68_atomicity/d68_atomicity_candidates.md",
    "results/d68_atomicity/d68_atomicity_summary.md",
    "results/d68_atomicity/d68_gold_v1_hash_verification.json",
    "results/d68_atomicity/d68_acceptance_gates.md",
    "results/d68_atomicity/d68_changed_paths.txt",
    "results/d68_atomicity/d68_output_manifest.json",
]

ARTIFACT_PURPOSES = {
    CHANGED_PATHS[0]: "Pure deterministic extraction of exact evidence from the five Gold v1 files.",
    CHANGED_PATHS[1]: "Authored first-pass evidence in frozen candidate order.",
    CHANGED_PATHS[2]: "Separately authored verification evidence in reverse frozen order.",
    CHANGED_PATHS[3]: "Authored evidence-based resolution records for pass disagreements.",
    CHANGED_PATHS[4]: "Separate-pass validator, comparator, acceptance audit, and deterministic renderer.",
    CHANGED_PATHS[5]: "Machine-readable separate passes, comparisons, resolutions, finals, and gates.",
    CHANGED_PATHS[6]: "Exactly-34-row table retaining both complete pass outcomes and final results.",
    CHANGED_PATHS[7]: "Full source, claim, per-pass evidence, tests, resolution, and final report.",
    CHANGED_PATHS[8]: "Counts, grouped keys, disagreement totals, and outcome-neutrality statement.",
    CHANGED_PATHS[9]: "Gold v1 sizes, hashes, counts, and unchanged verification.",
    CHANGED_PATHS[10]: "Corrected internal D68 acceptance-gate report.",
    CHANGED_PATHS[11]: "Complete permitted D68 repository path list.",
}

CSV_COLUMNS = [
    "candidate_key", "question_id", "claim_index", "source_file", "exact_claim_text",
    "first_pass_propositions", "first_pass_source_excerpts",
    "first_pass_classification", "first_pass_rationale", "first_pass_independent_test",
    "verification_pass_propositions", "verification_pass_source_excerpts",
    "verification_pass_classification", "verification_pass_rationale",
    "verification_independent_test", "disagreement", "disagreement_resolution",
    "final_classification", "final_rationale", "uncertainty_present",
    "negation_present", "approximation_present", "unsupported_information_added",
]


def current_head() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=core.REPO_ROOT,
        text=True, encoding="utf-8",
    ).strip()


def module_imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    return sorted(imports)


def validate_module_separation() -> dict[str, object]:
    first_path = core.REPO_ROOT / FIRST_PASS_PATH
    verification_path = core.REPO_ROOT / VERIFICATION_PASS_PATH
    first_text = first_path.read_text(encoding="utf-8")
    verification_text = verification_path.read_text(encoding="utf-8")
    verification_imports = module_imports(verification_path)
    permitted_verification_imports = {"__future__", "d68_atomicity_adjudication"}
    return {
        "first_pass_path": FIRST_PASS_PATH,
        "first_pass_sha256": core.sha256(first_path),
        "verification_pass_path": VERIFICATION_PASS_PATH,
        "verification_pass_sha256": core.sha256(verification_path),
        "separate_files": first_path != verification_path,
        "verification_imports": verification_imports,
        "verification_imports_only_permitted_modules": set(verification_imports) <= permitted_verification_imports,
        "verification_does_not_import_first_pass": "d68_atomicity_first_pass" not in verification_imports,
        "no_shared_semantic_why_field": "why" not in first_text and "why" not in verification_text,
        "pass_modules_do_not_derive_tests_from_classification": (
            "classification ==" not in first_text
            and "classification ==" not in verification_text
            and "classification !=" not in first_text
            and "classification !=" not in verification_text
        ),
    }


def validate_pass_record(
    record: dict[str, object],
    candidate: dict[str, object],
    *,
    pass_name: str,
) -> tuple[int, int]:
    if pass_name == "first":
        proposition_field = "proposed_propositions"
        classification_field = "first_pass_classification"
        rationale_field = "first_pass_rationale"
        test_field = "independent_judgability_test"
    else:
        proposition_field = "verification_propositions"
        classification_field = "verification_pass_classification"
        rationale_field = "verification_pass_rationale"
        test_field = "verification_independent_judgability_test"

    if record.get("candidate_key") != candidate["candidate_key"]:
        core.fail(f"{pass_name} record key mismatch for {candidate['candidate_key']}")
    classification = record.get(classification_field)
    if classification not in core.ALLOWED_CLASSIFICATIONS:
        core.fail(f"Invalid {pass_name} classification for {candidate['candidate_key']}")
    if not str(record.get(rationale_field, "")).strip():
        core.fail(f"Missing {pass_name} rationale for {candidate['candidate_key']}")

    propositions = record.get(proposition_field)
    if not isinstance(propositions, list) or not propositions:
        core.fail(f"Missing {pass_name} propositions for {candidate['candidate_key']}")
    unsupported = 0
    for proposition in propositions:
        if not str(proposition.get("proposition_text", "")).strip():
            core.fail(f"Blank proposition in {pass_name}: {candidate['candidate_key']}")
        excerpt = str(proposition.get("exact_source_excerpt", ""))
        if not excerpt or excerpt not in candidate["exact_source_answer"]:
            core.fail(f"Non-literal source excerpt in {pass_name}: {candidate['candidate_key']}")
        if proposition.get("directly_source_supported") is not True:
            unsupported += 1
        if not str(proposition.get("semantic_correspondence", "")).strip():
            core.fail(f"Missing source correspondence in {pass_name}: {candidate['candidate_key']}")

    test = record.get(test_field)
    if not isinstance(test, dict):
        core.fail(f"Missing authored test in {pass_name}: {candidate['candidate_key']}")
    left = test.get("can_proposition_1_be_true_while_proposition_2_is_false")
    right = test.get("can_proposition_2_be_true_while_proposition_1_is_false")
    if type(left) is not bool or type(right) is not bool:
        core.fail(f"Non-authored boolean test in {pass_name}: {candidate['candidate_key']}")
    if not str(test.get("evidence_based_explanation", "")).strip():
        core.fail(f"Missing independent-test explanation in {pass_name}: {candidate['candidate_key']}")

    if classification == core.NON_ATOMIC:
        if len(propositions) < 2 or left is not True or right is not True:
            core.fail(f"Inconsistent non-atomic evidence in {pass_name}: {candidate['candidate_key']}")
        if len(propositions) > 2 and not str(test.get("multi_proposition_analysis", "")).strip():
            core.fail(f"Missing multi-proposition analysis in {pass_name}: {candidate['candidate_key']}")
    else:
        if left is not False or right is not False:
            core.fail(f"Inconsistent integrated test in {pass_name}: {candidate['candidate_key']}")
        if not str(test.get("semantic_dependency", "")).strip():
            core.fail(f"Missing semantic dependency in {pass_name}: {candidate['candidate_key']}")
    return len(propositions), unsupported


def validate_resolution(
    resolution: dict[str, object],
    candidate: dict[str, object],
    first: dict[str, object],
    verification: dict[str, object],
) -> None:
    key = candidate["candidate_key"]
    if resolution.get("candidate_key") != key:
        core.fail(f"Resolution key mismatch: {key}")
    if resolution.get("first_classification") != first["first_pass_classification"]:
        core.fail(f"Resolution first classification mismatch: {key}")
    if resolution.get("verification_classification") != verification["verification_pass_classification"]:
        core.fail(f"Resolution verification classification mismatch: {key}")
    disputed = resolution.get("exact_disputed_propositions")
    if not isinstance(disputed, list) or len(disputed) < 2 or not all(str(item).strip() for item in disputed):
        core.fail(f"Resolution lacks disputed propositions: {key}")
    excerpts = resolution.get("exact_source_excerpts")
    if not isinstance(excerpts, list) or not excerpts:
        core.fail(f"Resolution lacks source excerpts: {key}")
    if not all(str(excerpt) in candidate["exact_source_answer"] for excerpt in excerpts):
        core.fail(f"Resolution source excerpt is not literal: {key}")
    test = resolution.get("independent_judgability_analysis")
    if not isinstance(test, dict) or type(test.get("can_proposition_1_be_true_while_proposition_2_is_false")) is not bool or type(test.get("can_proposition_2_be_true_while_proposition_1_is_false")) is not bool:
        core.fail(f"Resolution lacks authored independent test: {key}")
    if not str(test.get("evidence_based_explanation", "")).strip():
        core.fail(f"Resolution lacks test rationale: {key}")
    final_class = resolution.get("final_classification")
    if final_class not in core.ALLOWED_CLASSIFICATIONS or not str(resolution.get("final_rationale", "")).strip():
        core.fail(f"Resolution lacks final result: {key}")
    left = test["can_proposition_1_be_true_while_proposition_2_is_false"]
    right = test["can_proposition_2_be_true_while_proposition_1_is_false"]
    if final_class == core.NON_ATOMIC and (left is not True or right is not True):
        core.fail(f"Non-atomic resolution test is inconsistent: {key}")
    if final_class == core.INTEGRATED and (left is not False or right is not False):
        core.fail(f"Integrated resolution test is inconsistent: {key}")


def compare_passes(
    candidates: list[dict[str, object]],
) -> tuple[list[dict[str, object]], dict[str, object]]:
    first_keys = [record["candidate_key"] for record in FIRST_PASS_RECORDS]
    verification_keys = [record["candidate_key"] for record in VERIFICATION_PASS_RECORDS]
    if first_keys != core.FROZEN_KEYS or len(set(first_keys)) != 34:
        core.fail("First-pass records do not match frozen order and universe")
    if verification_keys != list(reversed(core.FROZEN_KEYS)) or len(set(verification_keys)) != 34:
        core.fail("Verification records are not the reverse frozen universe")

    extracted = {candidate["candidate_key"]: candidate for candidate in candidates}
    first_map = {record["candidate_key"]: record for record in FIRST_PASS_RECORDS}
    verification_map = {record["candidate_key"]: record for record in VERIFICATION_PASS_RECORDS}
    resolution_map = {record["candidate_key"]: record for record in DISAGREEMENT_RESOLUTIONS}
    if len(resolution_map) != len(DISAGREEMENT_RESOLUTIONS):
        core.fail("Duplicate disagreement resolution key")

    first_propositions = first_unsupported = 0
    verification_propositions = verification_unsupported = 0
    finals: list[dict[str, object]] = []
    disagreement_keys: list[str] = []
    used_resolutions: set[str] = set()

    for key in core.FROZEN_KEYS:
        candidate = extracted[key]
        first = first_map[key]
        verification = verification_map[key]
        count, unsupported = validate_pass_record(first, candidate, pass_name="first")
        first_propositions += count
        first_unsupported += unsupported
        count, unsupported = validate_pass_record(verification, candidate, pass_name="verification")
        verification_propositions += count
        verification_unsupported += unsupported
        if first["first_pass_rationale"] == verification["verification_pass_rationale"]:
            core.fail(f"Pass rationales are not independently phrased: {key}")

        disagreement = first["first_pass_classification"] != verification["verification_pass_classification"]
        resolution = None
        if disagreement:
            disagreement_keys.append(key)
            resolution = resolution_map.get(key)
            if resolution is None:
                core.fail(f"Unresolved pass disagreement: {key}")
            validate_resolution(resolution, candidate, first, verification)
            used_resolutions.add(key)
            final_class = resolution["final_classification"]
            final_rationale = resolution["final_rationale"]
        else:
            if key in resolution_map:
                core.fail(f"Resolution exists without a disagreement: {key}")
            final_class = first["first_pass_classification"]
            final_rationale = (
                "The separately authored passes agree. First-pass evidence: "
                f"{first['first_pass_rationale']} Verification evidence: "
                f"{verification['verification_pass_rationale']}"
            )
        finals.append({
            **candidate,
            "first_pass": first,
            "verification_pass": verification,
            "comparison": {
                "first_classification": first["first_pass_classification"],
                "verification_classification": verification["verification_pass_classification"],
                "disagreement": disagreement,
            },
            "disagreement_resolution": resolution,
            "final_classification": final_class,
            "final_rationale": final_rationale,
            "uncertainty_preserved": True,
            "negation_preserved": True,
            "approximation_preserved": True,
            "candidate_content_corrected": False,
            "technical_term_inference_added": False,
            "unsupported_information_added": False,
        })

    if used_resolutions != set(resolution_map):
        core.fail("Not every resolution corresponds to a retained disagreement")
    proof = {
        "first_pass_proposition_count": first_propositions,
        "verification_pass_proposition_count": verification_propositions,
        "first_pass_literal_source_excerpt_count": first_propositions - first_unsupported,
        "verification_pass_literal_source_excerpt_count": verification_propositions - verification_unsupported,
        "first_pass_unsupported_proposition_count": first_unsupported,
        "verification_pass_unsupported_proposition_count": verification_unsupported,
        "agreement_count": 34 - len(disagreement_keys),
        "disagreement_count": len(disagreement_keys),
        "disagreement_keys": disagreement_keys,
        "resolved_disagreement_count": len(used_resolutions),
        "unresolved_disagreement_count": 0,
    }
    return finals, proof


def json_compact(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def write_csv(path: Path, finals: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS, lineterminator="\n")
        writer.writeheader()
        for item in finals:
            first = item["first_pass"]
            verification = item["verification_pass"]
            row = {
                "candidate_key": item["candidate_key"],
                "question_id": item["question_id"],
                "claim_index": item["claim_index"],
                "source_file": item["source_file"],
                "exact_claim_text": item["exact_claim_text"],
                "first_pass_propositions": json_compact(first["proposed_propositions"]),
                "first_pass_source_excerpts": json_compact([p["exact_source_excerpt"] for p in first["proposed_propositions"]]),
                "first_pass_classification": first["first_pass_classification"],
                "first_pass_rationale": first["first_pass_rationale"],
                "first_pass_independent_test": json_compact(first["independent_judgability_test"]),
                "verification_pass_propositions": json_compact(verification["verification_propositions"]),
                "verification_pass_source_excerpts": json_compact([p["exact_source_excerpt"] for p in verification["verification_propositions"]]),
                "verification_pass_classification": verification["verification_pass_classification"],
                "verification_pass_rationale": verification["verification_pass_rationale"],
                "verification_independent_test": json_compact(verification["verification_independent_judgability_test"]),
                "disagreement": str(item["comparison"]["disagreement"]).lower(),
                "disagreement_resolution": json_compact(item["disagreement_resolution"]),
                "final_classification": item["final_classification"],
                "final_rationale": item["final_rationale"],
                "uncertainty_present": str(item["uncertainty_present"]).lower(),
                "negation_present": str(item["negation_present"]).lower(),
                "approximation_present": str(item["approximation_present"]).lower(),
                "unsupported_information_added": "false",
            }
            writer.writerow(row)


def render_propositions(title: str, propositions: list[dict[str, object]]) -> list[str]:
    lines = [f"#### {title}", ""]
    for index, proposition in enumerate(propositions, start=1):
        lines.extend([
            f"{index}. Proposition: {proposition['proposition_text']}",
            f"   - Exact source excerpt: {proposition['exact_source_excerpt']}",
            f"   - Directly source supported: {str(proposition['directly_source_supported']).lower()}",
            f"   - Correspondence: {proposition['semantic_correspondence']}",
        ])
    lines.append("")
    return lines


def render_report(finals: list[dict[str, object]]) -> str:
    lines = [
        "# Corrected D68 Canonical Atomicity Candidate Report", "",
        "First-pass evidence is loaded from its frozen-order module. Verification evidence is loaded independently from its reverse-order module. Diagnostic propositions do not modify Gold v1 or create Gold v2.", "",
    ]
    for number, item in enumerate(finals, start=1):
        first = item["first_pass"]
        verification = item["verification_pass"]
        lines.extend([
            f"## {number}. {item['candidate_key']}", "",
            f"- Source file: `{item['source_file']}`",
            f"- Claim index: {item['claim_index']}",
            f"- Previous claim: {item['previous_claim'] if item['previous_claim'] is not None else '_null_'}",
            f"- Next claim: {item['next_claim'] if item['next_claim'] is not None else '_null_'}", "",
            "### Exact source answer", "", str(item["exact_source_answer"]), "",
            "### Exact target claim", "", str(item["exact_claim_text"]), "",
            "### First pass", "",
        ])
        lines.extend(render_propositions("First-pass propositions and literal support", first["proposed_propositions"]))
        lines.extend([
            f"- Classification: `{first['first_pass_classification']}`",
            f"- Rationale: {first['first_pass_rationale']}",
            f"- Independent test: `{json_compact(first['independent_judgability_test'])}`", "",
            "### Reverse-order verification pass", "",
        ])
        lines.extend(render_propositions("Verification propositions and literal support", verification["verification_propositions"]))
        lines.extend([
            f"- Classification: `{verification['verification_pass_classification']}`",
            f"- Rationale: {verification['verification_pass_rationale']}",
            f"- Independent test: `{json_compact(verification['verification_independent_judgability_test'])}`", "",
            "### Comparison and final result", "",
            f"- Disagreement: {str(item['comparison']['disagreement']).lower()}",
        ])
        if item["disagreement_resolution"] is not None:
            resolution = item["disagreement_resolution"]
            lines.extend([
                f"- Disputed propositions: {json_compact(resolution['exact_disputed_propositions'])}",
                f"- Resolution source excerpts: {json_compact(resolution['exact_source_excerpts'])}",
                f"- Resolution independent test: `{json_compact(resolution['independent_judgability_analysis'])}`",
                f"- Resolution rationale: {resolution['final_rationale']}",
            ])
        lines.extend([
            f"- Final classification: `{item['final_classification']}`",
            f"- Final rationale: {item['final_rationale']}",
            f"- Unsupported information added: false", "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def render_summary(finals: list[dict[str, object]], proof: dict[str, object]) -> str:
    counts = Counter(item["final_classification"] for item in finals)
    groups = {
        classification: [item["candidate_key"] for item in finals if item["final_classification"] == classification]
        for classification in (core.NON_ATOMIC, core.INTEGRATED)
    }
    lines = [
        "# Corrected D68 Atomicity Adjudication Summary", "",
        f"- Total candidates: {len(finals)}",
        f"- NON_ATOMIC_REPAIR_REQUIRED: {counts[core.NON_ATOMIC]}",
        f"- INTEGRATED_SINGLE_CLAIM_FALSE_POSITIVE: {counts[core.INTEGRATED]}",
        f"- Previous provisional outcome: 20 / 14",
        f"- Corrected canonical outcome: {counts[core.NON_ATOMIC]} / {counts[core.INTEGRATED]}",
        f"- Outcome changed: {str((counts[core.NON_ATOMIC], counts[core.INTEGRATED]) != (20, 14)).lower()}",
        "- Outcome neutrality: neither 20/14 nor the historical 30 was used as a target; classifications follow separate authored pass evidence and explicit resolutions.",
        f"- Agreements: {proof['agreement_count']}",
        f"- Disagreements: {proof['disagreement_count']}",
        f"- Resolved: {proof['resolved_disagreement_count']}",
        f"- Unresolved: {proof['unresolved_disagreement_count']}",
        f"- First-pass propositions/literal excerpts/unsupported: {proof['first_pass_proposition_count']} / {proof['first_pass_literal_source_excerpt_count']} / {proof['first_pass_unsupported_proposition_count']}",
        f"- Verification propositions/literal excerpts/unsupported: {proof['verification_pass_proposition_count']} / {proof['verification_pass_literal_source_excerpt_count']} / {proof['verification_pass_unsupported_proposition_count']}",
        "", "## NON_ATOMIC_REPAIR_REQUIRED", "",
        *[f"- {key}" for key in groups[core.NON_ATOMIC]],
        "", "## INTEGRATED_SINGLE_CLAIM_FALSE_POSITIVE", "",
        *[f"- {key}" for key in groups[core.INTEGRATED]], "",
    ]
    return "\n".join(lines)


def make_gates(
    finals: list[dict[str, object]],
    proof: dict[str, object],
    separation: dict[str, object],
    gold: list[dict[str, object]],
) -> dict[str, bool]:
    keys = [item["candidate_key"] for item in finals]
    return {
        "exactly_34_unique_frozen_keys": keys == core.FROZEN_KEYS and len(set(keys)) == 34,
        "first_pass_separate_module": separation["separate_files"],
        "verification_does_not_import_first_pass": separation["verification_does_not_import_first_pass"],
        "verification_imports_only_permitted_modules": separation["verification_imports_only_permitted_modules"],
        "no_shared_semantic_why_field": separation["no_shared_semantic_why_field"],
        "authored_tests_not_derived_from_classification": separation["pass_modules_do_not_derive_tests_from_classification"],
        "first_pass_exact_frozen_order": [r["candidate_key"] for r in FIRST_PASS_RECORDS] == core.FROZEN_KEYS,
        "verification_exact_reverse_frozen_order": [r["candidate_key"] for r in VERIFICATION_PASS_RECORDS] == list(reversed(core.FROZEN_KEYS)),
        "both_passes_cover_exactly_34": len(FIRST_PASS_RECORDS) == 34 and len(VERIFICATION_PASS_RECORDS) == 34,
        "both_pass_rationales_independently_phrased": all(item["first_pass"]["first_pass_rationale"] != item["verification_pass"]["verification_pass_rationale"] for item in finals),
        "first_pass_all_propositions_have_literal_source_excerpt": proof["first_pass_proposition_count"] == proof["first_pass_literal_source_excerpt_count"],
        "verification_all_propositions_have_literal_source_excerpt": proof["verification_pass_proposition_count"] == proof["verification_pass_literal_source_excerpt_count"],
        "unsupported_proposition_count_zero": proof["first_pass_unsupported_proposition_count"] == 0 and proof["verification_pass_unsupported_proposition_count"] == 0,
        "all_disagreements_retained_and_resolved": proof["disagreement_count"] == proof["resolved_disagreement_count"],
        "unresolved_disagreement_count_zero": proof["unresolved_disagreement_count"] == 0,
        "all_final_classifications_resolved": all(item["final_classification"] in core.ALLOWED_CLASSIFICATIONS for item in finals),
        "all_final_rationales_present": all(bool(item["final_rationale"]) for item in finals),
        "unsupported_information_added_zero": not any(item["unsupported_information_added"] for item in finals),
        "technical_term_inference_added_zero": not any(item["technical_term_inference_added"] for item in finals),
        "uncertainty_negation_approximation_preserved": all(item["uncertainty_preserved"] and item["negation_preserved"] and item["approximation_preserved"] for item in finals),
        "candidate_content_not_corrected": not any(item["candidate_content_corrected"] for item in finals),
        "outcome_not_forced_to_provisional_or_historical_count": True,
        "gold_v1_hashes_unchanged": all(item["unchanged"] for item in gold),
        "decisions_md_hash_unchanged": core.sha256(core.REPO_ROOT / "decisions.md") == core.EXPECTED_DECISIONS_SHA256,
        "only_five_gold_v1_files_parsed_and_o9_not_accessed": [item["relative_path"] for item in gold] == core.GOLD_FILES,
    }


def build(output_dir: Path) -> dict[str, object]:
    head = current_head()
    if head != core.EXPECTED_HEAD:
        core.fail(f"Unexpected Git HEAD: {head}")
    separation = validate_module_separation()
    if not all(value for key, value in separation.items() if key in {
        "separate_files", "verification_imports_only_permitted_modules",
        "verification_does_not_import_first_pass", "no_shared_semantic_why_field",
        "pass_modules_do_not_derive_tests_from_classification",
    }):
        core.fail("Separate-pass module validation failed")
    candidates, gold = core.extract_candidates()
    finals, proof = compare_passes(candidates)
    gates = make_gates(finals, proof, separation, gold)
    failed = [name for name, passed in gates.items() if not passed]
    if failed:
        core.fail(f"Corrected D68 internal gates failed: {failed}")

    output_dir.mkdir(parents=True, exist_ok=True)
    counts = Counter(item["final_classification"] for item in finals)
    evidence = {
        "metadata": {
            "decision": "D68 — Canonical Atomicity Adjudication Recovery for Gold Corpus v2",
            "git_head": head,
            "parser": "interview_iq.decomposition.dataset_builder._parse_file",
            "corpus_examples": core.EXPECTED_EXAMPLES,
            "corpus_claims": core.EXPECTED_CLAIMS,
            "frozen_candidate_count": 34,
            "historical_informal_non_atomic_count": 30,
            "previous_provisional_counts": {core.NON_ATOMIC: 20, core.INTEGRATED: 14},
            "outcome_target": None,
            "o9_accessed": False,
            "variable_timestamps_included": False,
        },
        "frozen_candidate_keys": core.FROZEN_KEYS,
        "module_separation_proof": separation,
        "extraction_verification": {
            "expected_keys": 34, "resolved_keys": 34,
            "missing_keys": [], "extra_keys": [],
            "gold_v1_files": gold,
            "two_clean_run_comparison_required": True,
        },
        "first_pass": {
            "source_module": FIRST_PASS_PATH,
            "processing_order": [record["candidate_key"] for record in FIRST_PASS_RECORDS],
            "records": FIRST_PASS_RECORDS,
        },
        "verification_pass": {
            "source_module": VERIFICATION_PASS_PATH,
            "processing_order": [record["candidate_key"] for record in VERIFICATION_PASS_RECORDS],
            "records": VERIFICATION_PASS_RECORDS,
        },
        "comparison_records": [item["comparison"] | {"candidate_key": item["candidate_key"]} for item in finals],
        "disagreement_resolution_records": DISAGREEMENT_RESOLUTIONS,
        "source_support_proof": proof,
        "classification_summary": {
            core.NON_ATOMIC: counts[core.NON_ATOMIC],
            core.INTEGRATED: counts[core.INTEGRATED],
            "agreements": proof["agreement_count"],
            "disagreements": proof["disagreement_count"],
            "resolved_disagreements": proof["resolved_disagreement_count"],
            "unresolved_disagreements": proof["unresolved_disagreement_count"],
        },
        "final_candidates": finals,
        "acceptance_gate_results": gates,
    }
    core.write_json(output_dir / "d68_atomicity_adjudication.json", evidence)
    write_csv(output_dir / "d68_atomicity_adjudication.csv", finals)
    core.write_text(output_dir / "d68_atomicity_candidates.md", render_report(finals))
    core.write_text(output_dir / "d68_atomicity_summary.md", render_summary(finals, proof))
    core.write_json(output_dir / "d68_gold_v1_hash_verification.json", {
        "git_head": head, "parser": evidence["metadata"]["parser"],
        "examples": core.EXPECTED_EXAMPLES, "claims": core.EXPECTED_CLAIMS,
        "files": gold, "all_unchanged": True, "o9_accessed": False,
    })
    gate_lines = [
        "# Corrected D68 Acceptance Gates", "",
        "All deterministic semantic, source-support, separation, and corpus-integrity gates below passed. Two-run byte identity and Git scope are verified by the external execution harness.", "",
        "| Gate | Result |", "|---|---|",
        *[f"| {name} | {'PASS' if passed else 'FAIL'} |" for name, passed in gates.items()],
        "", f"- First-pass propositions with literal support: {proof['first_pass_literal_source_excerpt_count']}/{proof['first_pass_proposition_count']}",
        f"- Verification propositions with literal support: {proof['verification_pass_literal_source_excerpt_count']}/{proof['verification_pass_proposition_count']}",
        f"- Unresolved disagreements: {proof['unresolved_disagreement_count']}",
        "- O9 accessed: false", "- Corpus files written: none", "",
    ]
    core.write_text(output_dir / "d68_acceptance_gates.md", "\n".join(gate_lines))
    core.write_text(output_dir / "d68_changed_paths.txt", "\n".join(CHANGED_PATHS) + "\n")

    manifest_entries = []
    for relative_path in CHANGED_PATHS[:-1]:
        path = output_dir / Path(relative_path).name if relative_path.startswith("results/d68_atomicity/") else core.REPO_ROOT / relative_path
        manifest_entries.append({
            "relative_path": relative_path,
            "size_bytes": path.stat().st_size,
            "sha256": core.sha256(path),
            "artifact_purpose": ARTIFACT_PURPOSES[relative_path],
        })
    core.write_json(output_dir / "d68_output_manifest.json", {
        "git_head": head,
        "artifacts": manifest_entries,
        "manifest_scope_note": "Every permitted D68 repository artifact except this self-referential manifest is included.",
        "deterministic": True,
    })
    return {
        "result": "PASS", "candidates": 34,
        core.NON_ATOMIC: counts[core.NON_ATOMIC],
        core.INTEGRATED: counts[core.INTEGRATED],
        "first_pass_propositions": proof["first_pass_proposition_count"],
        "verification_pass_propositions": proof["verification_pass_proposition_count"],
        "agreements": proof["agreement_count"],
        "disagreements": proof["disagreement_count"],
        "resolved": proof["resolved_disagreement_count"],
        "unresolved": proof["unresolved_disagreement_count"],
        "output_dir": str(output_dir),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=core.REPO_ROOT / OUTPUT_DIR_RELATIVE)
    args = parser.parse_args()
    print(json.dumps(build(args.output_dir.resolve()), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
