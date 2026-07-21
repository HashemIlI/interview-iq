# Answer Generation Prompt v1

Status: DRAFT_UNREVIEWED data preparation. This prompt does not create human answers.

PASS 1 ONLY. Given question_id, track, question text, authorized reference chunks,
and the Latin technical terms found in those inputs, return JSON containing exactly
five Egyptian-Arabic candidate answers: complete_correct, short_partial,
mixed_correctness, plausible_misconception, and natural_egyptian_spoken.

The five cases must differ semantically, not merely lexically. Preserve Latin technical
terms. Do not copy the reference verbatim. Preserve deliberately expressed factual
errors, negation, hedging, and uncertainty. Do not emit claims in this pass. Do not
include the case label inside answer text. These are synthetic candidate-answer cases,
not real human responses.
