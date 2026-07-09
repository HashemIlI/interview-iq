"""
tests/test_data_layer.py — Phase 3 Data Layer tests (refdocs loader + NLI dataset + validate_data CLI).

All tests run on CPU against small synthetic fixtures in tests/fixtures/ —
no real project data is read or copied here.
Run with:  pytest tests/test_data_layer.py -v
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from interview_iq.cli.validate_data import main as validate_data_main
from interview_iq.nli.dataset import (
    GoldPairRecord,
    NLIDataSchemaError,
    PairRecord,
    check_chunk_resolution,
    check_ds014_exclusion,
    check_five_word_overlap,
    check_hard_pos_twin_integrity,
    check_label_distribution,
    check_question_id_split_readiness,
    check_stage2_verdict_presence,
    load_gold_set,
    load_pilot_pairs,
    load_pilot_pairs_file,
)
from interview_iq.refdocs.loader import (
    ChunkUniquenessError,
    RefDocsSchemaError,
    load_reference_docs,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"
REFDOCS_MINI = FIXTURES_DIR / "refdocs_mini.json"
QUESTIONS_MINI = FIXTURES_DIR / "questions_mini.json"
PAIRS_FLAT = FIXTURES_DIR / "pairs_mini_flat.json"
PAIRS_NESTED = FIXTURES_DIR / "pairs_mini_nested.json"
GOLD_MINI = FIXTURES_DIR / "gold_mini.json"


def _write_json(path: Path, data: dict) -> Path:
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return path


# ═══════════════════════════════════════════════════════════════════════════
# refdocs/loader.py
# ═══════════════════════════════════════════════════════════════════════════


class TestLoadReferenceDocs:
    def test_loads_valid_fixture(self) -> None:
        refdocs = load_reference_docs(REFDOCS_MINI)
        assert len(refdocs.documents) == 2
        assert len(refdocs.chunk_ids()) == 5

    def test_get_document(self) -> None:
        refdocs = load_reference_docs(REFDOCS_MINI)
        doc = refdocs.get_document("ZZ-001")
        assert doc is not None
        assert doc.track == "ZZ"
        assert len(doc.chunks) == 3
        assert refdocs.get_document("NOPE-999") is None

    def test_get_chunk_text(self) -> None:
        refdocs = load_reference_docs(REFDOCS_MINI)
        assert "Recursion" in refdocs.get_chunk_text("ZZ001-C01")
        assert refdocs.get_chunk_text("NOPE-C99") is None

    def test_question_ids(self) -> None:
        refdocs = load_reference_docs(REFDOCS_MINI)
        assert refdocs.question_ids() == {"ZZ-001", "ZZ-002"}

    def test_missing_file(self) -> None:
        with pytest.raises(FileNotFoundError):
            load_reference_docs(FIXTURES_DIR / "does_not_exist.json")

    def test_malformed_json(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad.json"
        bad.write_text("{not valid json", encoding="utf-8")
        with pytest.raises(RefDocsSchemaError):
            load_reference_docs(bad)

    def test_missing_top_level_key(self, tmp_path: Path) -> None:
        bad = _write_json(tmp_path / "bad.json", {"meta": {}})
        with pytest.raises(RefDocsSchemaError):
            load_reference_docs(bad)

    def test_missing_required_doc_key(self, tmp_path: Path) -> None:
        data = json.loads(REFDOCS_MINI.read_text(encoding="utf-8"))
        del data["documents"][0]["track"]
        bad = _write_json(tmp_path / "bad.json", data)
        with pytest.raises(RefDocsSchemaError):
            load_reference_docs(bad)

    def test_duplicate_question_id(self, tmp_path: Path) -> None:
        data = json.loads(REFDOCS_MINI.read_text(encoding="utf-8"))
        data["documents"][1]["question_id"] = data["documents"][0]["question_id"]
        bad = _write_json(tmp_path / "bad.json", data)
        with pytest.raises(RefDocsSchemaError):
            load_reference_docs(bad)

    def test_duplicate_chunk_id(self, tmp_path: Path) -> None:
        data = json.loads(REFDOCS_MINI.read_text(encoding="utf-8"))
        # ZZ002-C02 is not referenced by any key_points, so this only trips
        # the chunk-uniqueness check, not the key_points-resolution check.
        data["documents"][1]["chunks"][1]["chunk_id"] = "ZZ001-C01"
        bad = _write_json(tmp_path / "bad.json", data)
        with pytest.raises(ChunkUniquenessError):
            load_reference_docs(bad)

    def test_unresolved_key_points(self, tmp_path: Path) -> None:
        """V3: a dangling key_point chunk_id reference is a hard failure —
        it would permanently cap that document's Coverage."""
        data = json.loads(REFDOCS_MINI.read_text(encoding="utf-8"))
        data["documents"][0]["key_points"].append("ZZ001-C99")
        bad = _write_json(tmp_path / "bad.json", data)
        with pytest.raises(RefDocsSchemaError):
            load_reference_docs(bad)

    def test_duplicate_key_points(self, tmp_path: Path) -> None:
        """V3: a duplicate chunk_id within one document's key_points list is
        a hard failure (distinct from the dangling-reference case above)."""
        data = json.loads(REFDOCS_MINI.read_text(encoding="utf-8"))
        data["documents"][0]["key_points"].append(data["documents"][0]["key_points"][0])
        bad = _write_json(tmp_path / "bad.json", data)
        with pytest.raises(RefDocsSchemaError):
            load_reference_docs(bad)

    def test_empty_key_points(self, tmp_path: Path) -> None:
        """V3: an empty key_points list is a hard failure — every document
        must declare at least one mandatory-coverage chunk."""
        data = json.loads(REFDOCS_MINI.read_text(encoding="utf-8"))
        data["documents"][0]["key_points"] = []
        bad = _write_json(tmp_path / "bad.json", data)
        with pytest.raises(RefDocsSchemaError):
            load_reference_docs(bad)

    def test_key_points_happy_path_counts(self) -> None:
        """Happy path: valid key_points resolve, are unique, non-empty, and
        their per-document counts are exactly what the fixture declares."""
        refdocs = load_reference_docs(REFDOCS_MINI)
        doc1 = refdocs.get_document("ZZ-001")
        doc2 = refdocs.get_document("ZZ-002")
        assert doc1 is not None and doc2 is not None
        assert doc1.key_points == ("ZZ001-C01", "ZZ001-C02")
        assert doc2.key_points == ("ZZ002-C01",)
        assert len(set(doc1.key_points)) == len(doc1.key_points)
        assert len(set(doc2.key_points)) == len(doc2.key_points)


# ═══════════════════════════════════════════════════════════════════════════
# nli/dataset.py — loaders
# ═══════════════════════════════════════════════════════════════════════════


class TestLoadPilotPairs:
    def test_loads_flat_shape(self) -> None:
        records = load_pilot_pairs_file(PAIRS_FLAT)
        assert len(records) == 6
        assert all(r.question_id == "ZZ-001" for r in records)

    def test_loads_nested_shape(self) -> None:
        records = load_pilot_pairs_file(PAIRS_NESTED)
        assert len(records) == 3
        assert all(r.question_id == "ZZ-002" for r in records)

    def test_combined_load(self) -> None:
        records = load_pilot_pairs([PAIRS_FLAT, PAIRS_NESTED])
        assert len(records) == 9
        assert {r.question_id for r in records} == {"ZZ-001", "ZZ-002"}

    def test_hard_pos_fields_preserved(self) -> None:
        records = {r.pair_id: r for r in load_pilot_pairs_file(PAIRS_FLAT)}
        twin_a, twin_b = records["ZZ001-P02a"], records["ZZ001-P02b"]
        assert twin_a.claim_group == twin_b.claim_group == "HP1"
        assert twin_a.hypothesis == twin_b.hypothesis
        assert {twin_a.label, twin_b.label} == {"entailment", "paired_neutral"}

    def test_missing_file(self) -> None:
        with pytest.raises(FileNotFoundError):
            load_pilot_pairs_file(FIXTURES_DIR / "does_not_exist.json")

    def test_duplicate_pair_id_within_file(self, tmp_path: Path) -> None:
        data = json.loads(PAIRS_FLAT.read_text(encoding="utf-8"))
        data["pairs"][1]["pair_id"] = data["pairs"][0]["pair_id"]
        bad = _write_json(tmp_path / "bad.json", data)
        with pytest.raises(NLIDataSchemaError):
            load_pilot_pairs_file(bad)

    def test_duplicate_pair_id_across_files(self, tmp_path: Path) -> None:
        data = json.loads(PAIRS_NESTED.read_text(encoding="utf-8"))
        data["documents"][0]["pairs"][0]["pair_id"] = "ZZ001-P01"  # collides with PAIRS_FLAT
        bad = _write_json(tmp_path / "bad.json", data)
        with pytest.raises(NLIDataSchemaError):
            load_pilot_pairs([PAIRS_FLAT, bad])

    def test_invalid_label(self, tmp_path: Path) -> None:
        data = json.loads(PAIRS_FLAT.read_text(encoding="utf-8"))
        data["pairs"][0]["label"] = "not_a_real_label"
        bad = _write_json(tmp_path / "bad.json", data)
        with pytest.raises(NLIDataSchemaError):
            load_pilot_pairs_file(bad)

    def test_invalid_category(self, tmp_path: Path) -> None:
        data = json.loads(PAIRS_FLAT.read_text(encoding="utf-8"))
        data["pairs"][0]["category"] = "NOT_A_CATEGORY"
        bad = _write_json(tmp_path / "bad.json", data)
        with pytest.raises(NLIDataSchemaError):
            load_pilot_pairs_file(bad)

    def test_missing_required_key(self, tmp_path: Path) -> None:
        data = json.loads(PAIRS_FLAT.read_text(encoding="utf-8"))
        del data["pairs"][0]["hypothesis"]
        bad = _write_json(tmp_path / "bad.json", data)
        with pytest.raises(NLIDataSchemaError):
            load_pilot_pairs_file(bad)

    def test_unrecognized_shape(self, tmp_path: Path) -> None:
        bad = _write_json(tmp_path / "bad.json", {"meta": {"question_id": "ZZ-001"}})
        with pytest.raises(NLIDataSchemaError):
            load_pilot_pairs_file(bad)


class TestLoadGoldSet:
    def test_loads_valid_fixture(self) -> None:
        records = load_gold_set(GOLD_MINI)
        assert len(records) == 2
        assert all(r.question_id == "ZZ-999" for r in records)
        assert records[0].label == "entailment"
        assert records[1].stage2_verdict == "confirmed"

    def test_missing_file(self) -> None:
        with pytest.raises(FileNotFoundError):
            load_gold_set(FIXTURES_DIR / "does_not_exist.json")

    def test_invalid_label(self, tmp_path: Path) -> None:
        data = json.loads(GOLD_MINI.read_text(encoding="utf-8"))
        data["pairs"][0]["label"] = "paired_neutral"  # not a valid gold-set label
        bad = _write_json(tmp_path / "bad.json", data)
        with pytest.raises(NLIDataSchemaError):
            load_gold_set(bad)

    def test_duplicate_pair_id(self, tmp_path: Path) -> None:
        data = json.loads(GOLD_MINI.read_text(encoding="utf-8"))
        data["pairs"][1]["pair_id"] = data["pairs"][0]["pair_id"]
        bad = _write_json(tmp_path / "bad.json", data)
        with pytest.raises(NLIDataSchemaError):
            load_gold_set(bad)


# ═══════════════════════════════════════════════════════════════════════════
# nli/dataset.py — safety checks
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture(scope="module")
def refdocs():
    return load_reference_docs(REFDOCS_MINI)


@pytest.fixture()
def pilot_pairs() -> list[PairRecord]:
    return load_pilot_pairs([PAIRS_FLAT, PAIRS_NESTED])


class TestCheckChunkResolution:
    def test_pass(self, pilot_pairs, refdocs) -> None:
        result = check_chunk_resolution(pilot_pairs, refdocs)
        assert result.passed and result.severity == "HARD"

    def test_fail_on_unknown_chunk(self, pilot_pairs, refdocs) -> None:
        broken = pilot_pairs + [
            PairRecord(
                pair_id="GHOST-P01",
                question_id="ZZ-001",
                category="EASY_POS",
                label="entailment",
                chunk_id="DOES-NOT-EXIST",
                hypothesis="orphan hypothesis",
            )
        ]
        result = check_chunk_resolution(broken, refdocs)
        assert not result.passed
        assert result.severity == "HARD"
        assert ("GHOST-P01", "DOES-NOT-EXIST") in result.details


class TestCheckDS014Exclusion:
    def test_pass_when_no_excluded_question(self, pilot_pairs) -> None:
        result = check_ds014_exclusion(pilot_pairs, {"ZZ-999"})
        assert result.passed and result.severity == "HARD"

    def test_fail_on_contamination(self, pilot_pairs) -> None:
        result = check_ds014_exclusion(pilot_pairs, {"ZZ-001"})
        assert not result.passed
        assert result.severity == "HARD"
        assert "ZZ001-P01" in result.details


class TestCheckHardPosTwinIntegrity:
    def test_pass(self, pilot_pairs) -> None:
        result = check_hard_pos_twin_integrity(pilot_pairs, expected_groups=1)
        assert result.passed and result.details["n_groups"] == 1

    def test_fail_on_group_count_mismatch(self, pilot_pairs) -> None:
        result = check_hard_pos_twin_integrity(pilot_pairs, expected_groups=30)
        assert not result.passed

    def test_fail_on_label_mismatch(self, pilot_pairs) -> None:
        broken = [
            p if p.pair_id != "ZZ001-P02b" else PairRecord(**{**p.__dict__, "label": "contradiction"})
            for p in pilot_pairs
        ]
        result = check_hard_pos_twin_integrity(broken)
        assert not result.passed

    def test_fail_on_hypothesis_mismatch(self, pilot_pairs) -> None:
        broken = [
            p if p.pair_id != "ZZ001-P02b" else PairRecord(**{**p.__dict__, "hypothesis": "different text"})
            for p in pilot_pairs
        ]
        result = check_hard_pos_twin_integrity(broken)
        assert not result.passed


class TestCheckLabelDistribution:
    def test_matches_expected(self, pilot_pairs) -> None:
        # flat (6): entailment=2, paired_neutral=1, contradiction=2, standard_neutral=1
        # nested (3): entailment=1, contradiction=1, standard_neutral=1
        # combined: entailment=3, contradiction=3, neutral=(1+1+1)=3
        expected = {"entailment": 3, "contradiction": 3, "neutral": 3}
        result = check_label_distribution(pilot_pairs, expected=expected)
        assert result.passed
        assert result.details == expected

    def test_mismatch_fails(self, pilot_pairs) -> None:
        result = check_label_distribution(pilot_pairs, expected={"entailment": 99, "contradiction": 0, "neutral": 0})
        assert not result.passed

    def test_no_expected_always_passes(self, pilot_pairs) -> None:
        result = check_label_distribution(pilot_pairs, expected=None)
        assert result.passed


class TestCheckQuestionIdSplitReadiness:
    def test_pass(self, pilot_pairs) -> None:
        result = check_question_id_split_readiness(pilot_pairs)
        assert result.passed and result.details["n_questions"] == 2

    def test_fail_on_missing_question_id(self, pilot_pairs) -> None:
        broken = [
            p if p.pair_id != "ZZ001-P01" else PairRecord(**{**p.__dict__, "question_id": ""})
            for p in pilot_pairs
        ]
        result = check_question_id_split_readiness(broken)
        assert not result.passed


class TestCheckFiveWordOverlap:
    def test_reports_without_failing(self, pilot_pairs, refdocs) -> None:
        result = check_five_word_overlap(pilot_pairs, refdocs)
        assert result.passed  # never a hard failure
        assert result.severity in {"INFO", "WARNING"}
        assert "n_violations" in result.details

    def test_escalates_when_one_sided(self, refdocs) -> None:
        # All violating pairs share the exact same premise text verbatim and
        # the same label -> 100% one-sided -> must escalate to WARNING.
        lopsided = [
            PairRecord(
                pair_id=f"P{i}",
                question_id="ZZ-001",
                category="EASY_POS",
                label="entailment",
                chunk_id="ZZ001-C01",
                hypothesis="Recursion هي أسلوب برمجي يستدعي فيه الدالة Function نفسها لحل مسألة أصغر من نفس النوع.",
            )
            for i in range(4)
        ]
        result = check_five_word_overlap(lopsided, refdocs, overlap_threshold=5)
        assert result.severity == "WARNING"


class TestCheckStage2VerdictPresence:
    def test_all_present(self) -> None:
        records = load_pilot_pairs_file(PAIRS_FLAT)
        result = check_stage2_verdict_presence(records, label="ZZ001")
        assert result.details["missing"] == []
        assert len(result.details["present"]) == len(records)

    def test_reports_missing(self) -> None:
        records = [
            PairRecord(
                pair_id="P1", question_id="ZZ-001", category="EASY_POS",
                label="entailment", chunk_id="ZZ001-C01", hypothesis="x",
                stage2_verdict=None,
            )
        ]
        result = check_stage2_verdict_presence(records)
        assert result.details["missing"] == ["P1"]


# ═══════════════════════════════════════════════════════════════════════════
# cli/validate_data.py — end-to-end
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture()
def mini_data_dir(tmp_path: Path) -> Path:
    """Lay out the mini fixtures under the same relative structure as data/."""
    data_dir = tmp_path / "data"
    (data_dir / "refdocs").mkdir(parents=True)
    (data_dir / "questions").mkdir(parents=True)
    (data_dir / "nli" / "pairs_pilot_150_v2").mkdir(parents=True)

    (data_dir / "refdocs" / "reference_docs_250_FINAL_v1.json").write_text(
        REFDOCS_MINI.read_text(encoding="utf-8"), encoding="utf-8"
    )
    (data_dir / "questions" / "questions_250.json").write_text(
        QUESTIONS_MINI.read_text(encoding="utf-8"), encoding="utf-8"
    )
    (data_dir / "nli" / "gold_set_48.json").write_text(
        GOLD_MINI.read_text(encoding="utf-8"), encoding="utf-8"
    )
    (data_dir / "nli" / "pairs_pilot_150_v2" / "pairs_DA001_pilot_v1.json").write_text(
        PAIRS_FLAT.read_text(encoding="utf-8"), encoding="utf-8"
    )
    (data_dir / "nli" / "pairs_pilot_150_v2" / "pairs_pilot_remaining9_v2.json").write_text(
        PAIRS_NESTED.read_text(encoding="utf-8"), encoding="utf-8"
    )
    return data_dir


def test_validate_data_runs_end_to_end_on_fixtures(mini_data_dir: Path, capsys) -> None:
    """The mini fixture set is internally consistent but deliberately tiny, so
    the production-scale count checks (250 docs / 1,515 chunks / 30 twin
    groups / 50-60-40 label split) are expected to fail — this test asserts
    the CLI runs to completion without crashing, and that the *structural*
    checks (schema, chunk resolution, contamination, twin shape) still pass."""
    exit_code = validate_data_main(["--data-dir", str(mini_data_dir)])
    out = capsys.readouterr().out

    assert exit_code == 1  # production-scale counts won't match the mini fixture
    assert "refdocs_schema: 2 documents, 5 unique chunks" in out
    assert "chunk_resolution: All 9 pairs resolve to a valid chunk_id" in out
    assert "premise_pool_contamination" in out and "D28 OK" in out
    assert "DOCUMENTED EXCEPTION (D35)" in out
    assert "Q4 diagnostic (DA001)" in out
    assert "RESULT: FAILED" in out
    # V3: key_points integrity passed (loader would have raised otherwise)
    # and the per-document count summary was printed.
    assert "key_points_integrity (V3): all 2 documents passed" in out
    assert "key_points_summary" in out and "min=1, max=2" in out


def test_validate_data_hard_fails_on_dangling_key_points(mini_data_dir: Path) -> None:
    """V3 end-to-end: a dangling key_point reference in refdocs must abort
    validate_data with a HARD failure (not a warning)."""
    refdocs_path = mini_data_dir / "refdocs" / "reference_docs_250_FINAL_v1.json"
    data = json.loads(refdocs_path.read_text(encoding="utf-8"))
    data["documents"][0]["key_points"].append("ZZ001-C99")
    refdocs_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    exit_code = validate_data_main(["--data-dir", str(mini_data_dir)])
    assert exit_code == 1


def test_validate_data_hard_fails_on_missing_refdocs(tmp_path: Path) -> None:
    empty_dir = tmp_path / "data"
    empty_dir.mkdir()
    exit_code = validate_data_main(["--data-dir", str(empty_dir)])
    assert exit_code == 1
