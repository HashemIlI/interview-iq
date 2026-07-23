"""
tests/test_transliteration.py — D97 (a) deterministic transliteration layer.

Covers: a term substituted with the definite article; a term substituted
without it; an AMBIGUOUS form left untouched; a claim with no glossary
terms returned unchanged; idempotence; plus, added after the STEP 4
filter revision (R-A raw-normalization fix, R-D general-lexicon filter,
R-C threshold raised to 4): a form removed by R-D left untouched, a form
removed by R-C left untouched, a term wrongly removed by the old buggy
R-A now substituting correctly, and a spaced multi-word form substituting
correctly.
"""

from __future__ import annotations

from interview_iq.decomposition_llm.transliteration import apply_glossary


def test_substitution_with_definite_article() -> None:
    # "Server" (السيرفر/سيرفر) is used as the illustrative example throughout
    # D97, but the STEP 4 revision's R-D filter removes it entirely: both
    # forms occur in the general Arabic wordlist. "Function" (الفانكشن/
    # فانكشن) survives R-A/R-B/R-D/R-C with both forms intact and is used
    # here instead -- see the STEP 4 revision report for the full list of
    # terms this affected.
    claims = ["الفانكشن دي بترجع نتيجة غلط"]
    out, audit = apply_glossary(claims)
    assert "Function" in out[0]
    assert "الفانكشن" not in out[0]
    assert any(s["replacement_term"] == "Function" for s in audit["substitutions"])


def test_substitution_without_definite_article() -> None:
    claims = ["فيه فانكشن واحدة بس اللي بتفشل"]
    out, audit = apply_glossary(claims)
    assert "Function" in out[0]
    assert any(s["replacement_term"] == "Function" for s in audit["substitutions"])


def test_ambiguous_form_left_untouched() -> None:
    # "Bash" and "Cache" no longer collide under R-A (that was the bug fixed
    # in the STEP 4 revision): both are individually removed to AMBIGUOUS by
    # R-D instead, because الكاش/الباش occur in the general Arabic wordlist
    # (data/glossary/arabic_wordlist.txt). Their Arabic forms must NOT be
    # substituted, and must be counted in residual_ambiguous_count.
    claims = ["الكاش بيسرع النظام"]
    out, audit = apply_glossary(claims)
    assert "الكاش" in out[0]
    assert audit["residual_ambiguous_count"] >= 1
    assert audit["substitutions"] == []


def test_claim_with_no_glossary_terms_unchanged() -> None:
    claims = ["مفيش حاجة تقنية في الجملة دي خالص"]
    out, audit = apply_glossary(claims)
    assert out[0] == claims[0]
    assert audit["substitutions"] == []
    assert audit["residual_ambiguous_count"] == 0


def test_idempotence() -> None:
    claims = ["السيرفر بيستخدم الكاش عشان يسرع الاستجابة"]
    once, _ = apply_glossary(claims)
    twice, _ = apply_glossary(once)
    assert once == twice


def test_form_removed_by_r_d_left_untouched() -> None:
    # "bit" was re-authored with three candidate forms (البت, بت, بيت) in
    # the STEP 3b revision; all three collide with real, common entries in
    # the general Arabic wordlist (data/glossary/arabic_wordlist.txt) and
    # are removed to AMBIGUOUS by R-D. The claim must be left untouched.
    claims = ["البت ده جزء من البايت"]
    out, audit = apply_glossary(claims)
    assert "البت" in out[0]
    assert audit["residual_ambiguous_count"] >= 1
    assert audit["substitutions"] == []


def test_form_removed_by_r_c_left_untouched() -> None:
    # "Scrum" -> السكرم/سكرم: the bare form سكرم is exactly 4 characters and
    # is removed by R-C (raw length <= 4); السكرم is separately removed by
    # R-D. Deliberately avoids the words "ماستر" here, since "Scrum Master"
    # is itself a separate, surviving phrase entry that would otherwise
    # shadow this single-word case via longest-match-first.
    claims = ["احنا بنعمل سكرم كل يوم الصبح"]
    out, audit = apply_glossary(claims)
    assert "سكرم" in out[0]
    assert audit["residual_ambiguous_count"] >= 1
    assert audit["substitutions"] == []


def test_step3a_restored_term_substitutes_correctly() -> None:
    # "catch" was one of the eight terms wrongly removed entirely by the
    # original buggy R-A (proclitic-stripping collapsed كاتش down to the
    # same core as باتش/الباتش). After the fix it survives with الكاتش and
    # must substitute correctly.
    claims = ["لازم تعمل الكاتش للإكسبشن ده"]
    out, audit = apply_glossary(claims)
    assert "catch" in out[0]
    assert "الكاتش" not in out[0]
    assert any(s["replacement_term"] == "catch" for s in audit["substitutions"])


def test_spaced_multiword_form_substitutes_correctly() -> None:
    # STEP 3d added a spaced variant (داتا بيز) alongside the joined form
    # for "Database". The joined form (الداتابيز/داتابيز) was removed by
    # R-D, but the spaced two-word form survives and must substitute.
    claims = ["الداتا بيز بتاعتنا كبيرة جدا"]
    out, audit = apply_glossary(claims)
    assert "Database" in out[0]
    assert any(s["replacement_term"] == "Database" for s in audit["substitutions"])
