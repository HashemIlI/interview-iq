"""
decomposition/prompts.py — Phase 8 fine-tuning prompt format (D56).

Builds on the original Q6-pilot PROMPT_TEMPLATE
(scripts/q6_pilot_decomposition.py, D53) verbatim, plus an explicit
output-format instruction that pilot never tested (zero-shot only
tested comprehension, not formatting). The pilot script itself is left
untouched -- it remains frozen historical evidence for D53/D54.
"""

from __future__ import annotations

from interview_iq.decomposition.types import KDExample

# Verbatim from scripts/q6_pilot_decomposition.py (D53) -- do not reword
# this part; it is the only empirically-referenced instruction text we
# have (even though the pilot result itself was non-evidentiary, D54).
_BASE_INSTRUCTION = (
    "فكّك الإجابة العامية التالية إلى claims ذرّية بالفصحى المبسّطة، مع إبقاء "
    "المصطلحات التقنية بحروف لاتينية، ومع الحفاظ على التردد والأخطاء كما "
    "وردت دون تصحيح أو حذف:"
)

# New in D56: explicit output-format instruction, never tested in the
# D53 pilot (which only tested comprehension, not formatting).
_FORMAT_INSTRUCTION = (
    "أخرج كل claim في سطر مستقل، مرقّم بالشكل التالي:\n"
    "1. النص\n2. النص\n"
    "بدون أي مقدمة أو خاتمة أو نص إضافي خارج القائمة المرقّمة."
)

PROMPT_TEMPLATE = f"{_BASE_INSTRUCTION}\n\n{_FORMAT_INSTRUCTION}\n\n{{raw_answer}}"

# Matches configs/decomposition.yaml output.claim_separator (locked).
CLAIM_SEPARATOR = "\n"

_ARAT5_UNSUPPORTED_MARKS = str.maketrans(
    {
        "\u064b": None,  # ARABIC FATHATAN
        "\u064d": None,  # ARABIC KASRATAN
    }
)


def normalize_for_arat5(text: str) -> str:
    """Remove only the two D61 candidate marks before tokenization."""
    return text.translate(_ARAT5_UNSUPPORTED_MARKS)


def build_prompt(raw_answer: str) -> str:
    """Fine-tuning input text for one training pair."""
    prompt = PROMPT_TEMPLATE.format(raw_answer=raw_answer)
    return normalize_for_arat5(prompt)


def build_target(claims: list[str]) -> str:
    """Fine-tuning target text: numbered claims, one per line, matching
    the exact convention already used in O9 / batch1-5 source Markdown
    (no reformatting needed when parsing dataset_builder.py output)."""
    target = CLAIM_SEPARATOR.join(
        f"{i}. {claim}"
        for i, claim in enumerate(claims, start=1)
    )
    return normalize_for_arat5(target)


def build_training_pair(example: KDExample) -> tuple[str, str]:
    """(input_text, target_text) for one KDExample, ready for a
    seq2seq tokenizer."""
    return build_prompt(example.source_text), build_target(example.claims)