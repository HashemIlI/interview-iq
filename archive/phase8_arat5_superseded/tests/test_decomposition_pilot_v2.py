from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import pytest

from interview_iq.decomposition import pilot_v2

REPO_ROOT = Path(__file__).parents[1]
PILOT_DIR = REPO_ROOT / "results" / "decomposition_corpus_v2_pilot"
CORPUS_PATH = PILOT_DIR / "pilot_corpus_v2_DRAFT_UNREVIEWED.jsonl"
EXPECTED_IDS = [
    "DA-004", "DA-010", "DA-020", "DA-045",
    "DS-007", "DS-012", "DS-018", "DS-019",
    "CS-006", "CS-037", "CS-041", "CS-049",
    "SE-002", "SE-003", "SE-006", "SE-031",
    "GN-016", "GN-017", "GN-035", "GN-041",
]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def records() -> list[dict]:
    return pilot_v2.load_pilot_jsonl(CORPUS_PATH)


def test_final_counts_balance_and_unique_case_ids(records: list[dict]) -> None:
    assert len(records) == 100
    assert len({r["question_id"] for r in records}) == 20
    assert len({r["answer_case_id"] for r in records}) == 100
    assert Counter(r["track"] for r in records) == {track: 20 for track in pilot_v2.TRACKS}
    assert Counter(r["case_type"] for r in records) == {case_type: 20 for case_type in pilot_v2.CASE_TYPES}
    grouped = defaultdict(list)
    for record in records:
        grouped[record["question_id"]].append(record)
    assert all(len(cases) == 5 for cases in grouped.values())
    assert all(len({case["answer_original"] for case in cases}) == 5 for cases in grouped.values())


def test_exclusions_status_and_json_claim_lists(records: list[dict]) -> None:
    o9_ids = pilot_v2.parse_o9_question_ids(REPO_ROOT)
    qids = {r["question_id"] for r in records}
    assert "GN-050" not in qids
    assert qids.isdisjoint(o9_ids)
    assert all(r["review_status"] == "DRAFT_UNREVIEWED" for r in records)
    assert all(isinstance(r["claims"], list) and r["claims"] for r in records)
    assert all(all(isinstance(claim, str) for claim in r["claims"]) for r in records)
    assert all("rendered_target" not in r for r in records)


def test_latin_terms_and_paired_asr_share_one_claim_list(records: list[dict]) -> None:
    for record in records:
        answer_terms = pilot_v2.extract_latin_terms(record["answer_original"])
        assert answer_terms == record["latin_terms_in_answer"]
        assert all(term in record["answer_asr_simulated"] for term in answer_terms)
        assert all(term in "\n".join(record["claims"]) for term in answer_terms)
        assert "claims_original" not in record
        assert "claims_asr_simulated" not in record
    manifest = json.loads((PILOT_DIR / "pilot_corpus_v2_manifest.json").read_text(encoding="utf-8"))
    assert manifest["asr_variant_policy"].startswith("paired fields in one canonical case")
    assert manifest["automatic_splits_created"] is False


def test_selection_is_deterministic_at_seed_42() -> None:
    questions, _ = pilot_v2.load_project_inputs(REPO_ROOT)
    o9_ids = pilot_v2.parse_o9_question_ids(REPO_ROOT)
    first = pilot_v2.select_question_ids(questions, o9_ids, 42)
    second = pilot_v2.select_question_ids(questions, o9_ids, 42)
    assert first == second == EXPECTED_IDS


def test_audit_reports_required_guards() -> None:
    audit = json.loads((PILOT_DIR / "pilot_corpus_v2_audit.json").read_text(encoding="utf-8"))
    assert audit["verdict"] == "DATASET GENERATION PIPELINE PASS"
    assert audit["record_count"] == 100
    assert audit["term_corruption_count"] == 0
    assert audit["exact_duplicate_answer_count"] == 0
    assert audit["secret_scan_hits"] == []
    assert audit["automatic_splits_created"] is False
    assert audit["existing_results_unchanged"] is True


def test_missing_gemini_key_fails_safely(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(pilot_v2.PilotGenerationError, match="GEMINI_API_KEY"):
        pilot_v2.GeminiProvider()


def test_provider_error_stops_without_final_dataset(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    class FailingProvider:
        name = "failing"
        model = "test"
        def generate_answers(self, document, terms):
            raise RuntimeError("simulated API outage")
    monkeypatch.setattr(pilot_v2, "_provider_from_name", lambda name, model=None: FailingProvider())
    output = tmp_path / "failed"
    with pytest.raises(pilot_v2.PilotGenerationError, match="PASS 1 failed safely"):
        pilot_v2.build_pilot(REPO_ROOT, output)
    assert not (output / "pilot_corpus_v2_DRAFT_UNREVIEWED.jsonl").exists()


def test_resume_does_not_duplicate_completed_responses(tmp_path: Path) -> None:
    output = tmp_path / "resume"
    pilot_v2.build_pilot(REPO_ROOT, output, resume=True)
    raw_paths = sorted((output / "raw_responses").glob("*.jsonl"))
    before = {path.name: (_sha(path), len(path.read_text(encoding="utf-8").splitlines())) for path in raw_paths}
    corpus_before = _sha(output / "pilot_corpus_v2_DRAFT_UNREVIEWED.jsonl")
    pilot_v2.build_pilot(REPO_ROOT, output, resume=True)
    after = {path.name: (_sha(path), len(path.read_text(encoding="utf-8").splitlines())) for path in raw_paths}
    assert before == after
    assert {name: lines for name, (_, lines) in after.items()} == {
        "pass1_answers.jsonl": 20,
        "pass2_claims.jsonl": 100,
        "pass3_audits.jsonl": 100,
    }
    assert _sha(output / "pilot_corpus_v2_DRAFT_UNREVIEWED.jsonl") == corpus_before


def test_build_does_not_modify_existing_dataset(tmp_path: Path) -> None:
    protected = REPO_ROOT / "results" / "pilot_llm_assisted_batch1_DRAFT_UNREVIEWED.md"
    before = _sha(protected)
    pilot_v2.build_pilot(REPO_ROOT, tmp_path / "isolated")
    assert _sha(protected) == before

def test_three_raw_passes_are_separate_and_draft() -> None:
    raw_dir = PILOT_DIR / "raw_responses"
    pass1 = [json.loads(line) for line in (raw_dir / "pass1_answers.jsonl").read_text(encoding="utf-8").splitlines()]
    pass2 = [json.loads(line) for line in (raw_dir / "pass2_claims.jsonl").read_text(encoding="utf-8").splitlines()]
    pass3 = [json.loads(line) for line in (raw_dir / "pass3_audits.jsonl").read_text(encoding="utf-8").splitlines()]
    assert (len(pass1), len(pass2), len(pass3)) == (20, 100, 100)
    assert all(row["status"] == "DRAFT_UNREVIEWED" for row in [*pass1, *pass2, *pass3])
    assert all("claims" not in case for row in pass1 for case in row["payload"]["cases"])
    assert all(isinstance(row["claims"], list) for row in pass2)
    assert all("findings" in row for row in pass3)


def test_case_semantics_and_human_review_defaults(records: list[dict]) -> None:
    for record in records:
        is_error_case = record["case_type"] in {"mixed_correctness", "plausible_misconception"}
        assert bool(record["intended_errors"]) is is_error_case
        assert all(value is None for value in record["human_review"].values())
        if record["case_type"] == "natural_egyptian_spoken":
            assert "قصدي" in record["answer_original"]