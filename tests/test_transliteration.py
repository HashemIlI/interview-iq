"""
tests/test_transliteration.py — D97 (a) deterministic transliteration layer.

Covers: a term substituted with the definite article; a term substituted
without it; an AMBIGUOUS form left untouched (R-A collision); a claim with
no glossary terms returned unchanged; idempotence; plus, added after the
STEP 4 filter revision (R-A raw-normalization fix, R-D general-lexicon
filter, R-C threshold raised to 4): a form removed by R-C left untouched,
a term wrongly removed by the old buggy R-A now substituting correctly,
and a spaced multi-word form substituting correctly. Updated for the D98
rebuild (2026-07-27, R-B/R-D deleted, H-1/V-1 human adjudication): a form
adjudicated AMBIGUOUS under H-1 left untouched.
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
    # Fixture changed from Cache/الكاش to Batch/الباتش (D98 rebuild, 2026-07-27):
    # Cache was adjudicated KEEP at H-1 idx 42/43 and no longer collides with
    # anything, so الكاش now substitutes and can no longer serve as an
    # AMBIGUOUS fixture. الباتش/Batch collides with Patch under R-A, which is
    # permanent and not adjudicable (decisions.md D98), so this fixture
    # cannot be invalidated by any future H-1/V-1 verdict.
    claims = ["الباتش ده بيصلح المشكلة بسرعة"]
    out, audit = apply_glossary(claims)
    assert "الباتش" in out[0]
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


def test_form_adjudicated_ambiguous_under_h1_left_untouched() -> None:
    # D98 rebuild (2026-07-27): R-D is deleted, so a fixture asserting an
    # R-D-removed form stays untouched no longer describes the current
    # design (the term's forms now carry an H-1/V-1 verdict instead).
    # Replacement: Node / نود, H-1 idx 203 -- adjudicated AMBIGUOUS by
    # post-hoc edit (decisions.md D98, "One post-hoc edit recorded").
    # Node's other form (النود, idx 202) was adjudicated KEEP, so this also
    # exercises a term with a genuinely mixed H-1 verdict: the bare form
    # نود must stay untouched even though its sibling substitutes.
    # Confirmed against the rebuilt glossary before writing this test:
    # {"term": "Node", "form": "نود", "rule": "H-1"} is present in the
    # "ambiguous" list of data/glossary/transliteration_glossary.json.
    claims = ["نود ده بتاع الشبكة الموزعة"]
    out, audit = apply_glossary(claims)
    assert "نود" in out[0]
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


def test_r1_alef_variant_form_abstraction_substitutes() -> None:
    # D98 Finding G / Required repair R-1. normalize_arabic() rewrites the
    # alef-hamza variant أ to ا, but only on the input-claim side; the
    # compiled glossary pattern is built from the raw authored form
    # "الأبستراكشن" (with أ), so before the repair this can never match a
    # normalized claim and this test must FAIL. After the repair (glossary
    # forms normalized identically at load time) it must substitute.
    claims = ["بستخدم مبدأ الأبستراكشن في التصميم"]
    out, audit = apply_glossary(claims)
    assert "Abstraction" in out[0]
    assert any(s["replacement_term"] == "Abstraction" for s in audit["substitutions"])


def test_r1_diacritic_bearing_form_full_stack_substitutes() -> None:
    # D98 Finding G / Required repair R-1. Diacritic-bearing form chosen:
    # "فُل ستاك" (term "Full Stack") -- one of the 14 surviving forms in
    # transliteration_glossary.json carrying a diacritic (damma on ف).
    # Chosen deliberately because it contains no alef-hamza variant, so it
    # isolates the diacritic-stripping half of Finding G from the
    # alef-unification half tested above. Before the repair,
    # normalize_arabic() strips the damma from the input claim only, so
    # the raw diacritic-bearing compiled pattern can never match and this
    # test must FAIL. After the repair it must substitute.
    claims = ["هو مبرمج فُل ستاك قوي جدا"]
    out, audit = apply_glossary(claims)
    assert "Full Stack" in out[0]
    assert any(s["replacement_term"] == "Full Stack" for s in audit["substitutions"])


def test_h1_restored_terms_substitute() -> None:
    # D98 rebuild (2026-07-27). Test/Code/Queue/RAM were removed entirely
    # by R-B or R-D (rules deleted in D98) and had zero surviving forms in
    # the pre-D98 glossary -- the absence that caused the D96
    # transliteration failure. All four are restored via H-1 KEEP verdicts
    # (adjudication_H1_v1.tsv idx 324/325 Test, 55/56 Code, 241/242 Queue,
    # 243/244 RAM). This test must FAIL against the pre-D98 glossary (none
    # of these terms have a surviving form to match) and PASS against the
    # rebuilt one -- demonstrated by execution, not asserted.
    claims = [
        "التست ده بيغطي كل الحالات",
        "الكود ده بيتفذ بسرعة",
        "الكيو ده بيتعامل مع الرسايل",
        "الرام ده بيتاكد من الاداء",
    ]
    out, audit = apply_glossary(claims)
    assert "Test" in out[0]
    assert "Code" in out[1]
    assert "Queue" in out[2]
    assert "RAM" in out[3]
    replaced_terms = {s["replacement_term"] for s in audit["substitutions"]}
    assert {"Test", "Code", "Queue", "RAM"} <= replaced_terms
