"""
tests/test_scoring.py — Phase 6 scoring-engine unit tests.

Every test here is hand-computed pure Python: NO model, NO downloads, NO
matrix objects from nli/engine.py. scoring/aggregation.py and
scoring/metrics.py take plain floats in and plain floats/dataclasses out,
which is exactly what makes them unit-testable without a tokenizer or a
model in the loop.

Run with:  pytest tests/test_scoring.py -v
"""

from __future__ import annotations

import pytest

from interview_iq.refdocs.loader import Chunk, ReferenceDocument
from interview_iq.scoring.aggregation import Verdict, score_claim
from interview_iq.scoring.metrics import (
    DanglingKeyPointError,
    compute_scoring_result,
    coverage_channel,
    harmonic_f,
    precision_channel,
    resolve_key_point_chunks,
)

TAU = 0.5
TAU_E = 0.9
ALPHA = 0.0


# ═══════════════════════════════════════════════════════════════════════════
# (a) VERIFIED case: max_E >= tau_e even with a high max_C present -> C ignored
# ═══════════════════════════════════════════════════════════════════════════


def test_verified_ignores_high_contradiction() -> None:
    verdict = score_claim(max_e=0.95, max_c=0.99, tau=TAU, tau_e=TAU_E, alpha=ALPHA)
    assert verdict.verdict is Verdict.VERIFIED
    assert verdict.score == pytest.approx(1.0)


def test_verified_at_exact_threshold() -> None:
    # max_E == tau_e must still verify ("if max_E >= tau_e", not strictly >).
    verdict = score_claim(max_e=TAU_E, max_c=0.99, tau=TAU, tau_e=TAU_E, alpha=ALPHA)
    assert verdict.verdict is Verdict.VERIFIED


# ═══════════════════════════════════════════════════════════════════════════
# (b) Contradiction penalty: max_C > tau -> score = -max_C
# ═══════════════════════════════════════════════════════════════════════════


def test_contradiction_penalty_equals_negative_max_c() -> None:
    verdict = score_claim(max_e=0.1, max_c=0.7, tau=TAU, tau_e=TAU_E, alpha=ALPHA)
    assert verdict.verdict is Verdict.CONTRADICTED
    assert verdict.score == pytest.approx(-0.7)


# ═══════════════════════════════════════════════════════════════════════════
# (c) Neutral handling with alpha = 0 (and alpha != 0, to prove it is used)
# ═══════════════════════════════════════════════════════════════════════════


def test_neutral_with_alpha_zero() -> None:
    verdict = score_claim(max_e=0.1, max_c=0.2, tau=TAU, tau_e=TAU_E, alpha=0.0)
    assert verdict.verdict is Verdict.NEUTRAL
    assert verdict.score == pytest.approx(0.0)


def test_neutral_uses_configured_alpha_not_a_hardcoded_zero() -> None:
    verdict = score_claim(max_e=0.1, max_c=0.2, tau=TAU, tau_e=TAU_E, alpha=0.3)
    assert verdict.verdict is Verdict.NEUTRAL
    assert verdict.score == pytest.approx(0.3)


# ═══════════════════════════════════════════════════════════════════════════
# (d) Ordering invariant: correct > silent > wrong (STRICT)
# ═══════════════════════════════════════════════════════════════════════════


def _score_answer(max_e_claims: list[float], max_c_claims: list[float], max_e_keypoints: list[float]) -> float:
    precision, _ = precision_channel(max_e_claims, max_c_claims, tau=TAU, tau_e=TAU_E, alpha=ALPHA)
    coverage = coverage_channel(max_e_keypoints)
    return harmonic_f(precision, coverage)


def test_ordering_invariant_correct_silent_wrong() -> None:
    # correct: one claim confidently entailed, and it covers the key point too.
    score_correct = _score_answer(max_e_claims=[0.95], max_c_claims=[0.1], max_e_keypoints=[0.9])
    # silent: one claim, neither confirms nor denies anything, weak coverage.
    score_silent = _score_answer(max_e_claims=[0.2], max_c_claims=[0.1], max_e_keypoints=[0.1])
    # wrong: one claim confidently contradicts the reference.
    score_wrong = _score_answer(max_e_claims=[0.05], max_c_claims=[0.8], max_e_keypoints=[0.9])

    assert score_correct == pytest.approx(2 * 1.0 * 0.9 / (1.0 + 0.9))
    assert score_silent == pytest.approx(0.0)
    assert score_wrong == pytest.approx(-0.8)

    assert score_correct > score_silent > score_wrong


# ═══════════════════════════════════════════════════════════════════════════
# (e) D42 fragility: Coverage = 0 forces F = 0 even at Precision = 1.0
# ═══════════════════════════════════════════════════════════════════════════


def test_coverage_zero_forces_f_zero_even_at_precision_one() -> None:
    assert harmonic_f(precision=1.0, coverage=0.0) == pytest.approx(0.0)


# ═══════════════════════════════════════════════════════════════════════════
# (f) 2-key-point document (63/250 real docs, decisions.md D42): missing
#     exactly one key point caps F at 0.67 when Precision = 1.0.
# ═══════════════════════════════════════════════════════════════════════════


def test_two_keypoint_document_missing_one_caps_f_at_point_67() -> None:
    # One key point fully entailed (max_E=1.0), the other missed entirely (max_E=0.0).
    coverage = coverage_channel([1.0, 0.0])
    assert coverage == pytest.approx(0.5)

    f = harmonic_f(precision=1.0, coverage=coverage)
    assert f == pytest.approx(2 / 3, abs=5e-3)  # decisions.md D42 reports this rounded to 0.67
    assert round(f, 2) == 0.67


# ═══════════════════════════════════════════════════════════════════════════
# (g) metrics.py raises on a dangling key_point chunk_id
# ═══════════════════════════════════════════════════════════════════════════


def test_resolve_key_point_chunks_raises_on_dangling_reference() -> None:
    document = ReferenceDocument(
        question_id="ZZ-100",
        track="ZZ",
        question="Fixture question for the dangling key_point test.",
        chunks=(Chunk(chunk_id="ZZ100-C01", text="Only chunk in this document."),),
        key_points=("ZZ100-C99",),  # does not exist among document.chunks
    )
    with pytest.raises(DanglingKeyPointError, match="ZZ100-C99"):
        resolve_key_point_chunks(document)


def test_resolve_key_point_chunks_succeeds_when_all_references_resolve() -> None:
    document = ReferenceDocument(
        question_id="ZZ-101",
        track="ZZ",
        question="Fixture question for the happy-path resolution test.",
        chunks=(
            Chunk(chunk_id="ZZ101-C01", text="First chunk."),
            Chunk(chunk_id="ZZ101-C02", text="Second chunk."),
        ),
        key_points=("ZZ101-C02",),
    )
    resolved = resolve_key_point_chunks(document)
    assert [c.chunk_id for c in resolved] == ["ZZ101-C02"]


# ═══════════════════════════════════════════════════════════════════════════
# D47 regression guards — seven values empirically measured on 43dae43.
# Assert EXACTLY the measured outputs; no derivation, no re-implementation.
# ═══════════════════════════════════════════════════════════════════════════


def test_harmonic_f_zero_precision_zero_coverage_returns_zero() -> None:
    # Regression guard: this case was NOT covered by the 98-test suite as of 43dae43.
    assert harmonic_f(0.0, 0.0) == pytest.approx(0.0)


def test_harmonic_f_zero_precision_nonzero_coverage_returns_zero() -> None:
    assert harmonic_f(0.0, 1.0) == pytest.approx(0.0)


def test_harmonic_f_negative_precision_with_nonzero_coverage_returns_precision() -> None:
    assert harmonic_f(-1.0, 1.0) == pytest.approx(-1.0)


def test_harmonic_f_negative_precision_zero_coverage_returns_precision() -> None:
    assert harmonic_f(-1.0, 0.0) == pytest.approx(-1.0)


def test_precision_channel_empty_claims_returns_zero_and_empty_verdicts() -> None:
    result, verdicts = precision_channel([], [], tau=0.5, tau_e=0.9, alpha=0.0)
    assert result == pytest.approx(0.0)
    assert verdicts == []


def test_compute_scoring_result_silent_answer_score_is_zero() -> None:
    result = compute_scoring_result([], [], [], [], [0.0], 0.5, 0.9, 0.0)
    assert result.score == pytest.approx(0.0)


def test_compute_scoring_result_single_contradicted_claim_score_is_negative_100() -> None:
    result = compute_scoring_result(["x"], [0.0], [1.0], [None], [0.95], 0.5, 0.9, 0.0)
    assert result.score == pytest.approx(-100.0)
