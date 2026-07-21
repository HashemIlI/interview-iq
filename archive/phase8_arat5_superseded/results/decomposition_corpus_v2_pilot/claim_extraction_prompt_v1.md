# Claim Extraction Prompt v1

Status: DRAFT_UNREVIEWED data preparation.

PASS 2 ONLY. You receive one candidate answer and no reference document. Return a JSON
list of atomic, self-contained claims in simplified MSA. Extract every proposition from
the answer only. Do not add, correct, or omit information. Preserve errors, negation,
hedging, uncertainty, and every Latin technical term byte-for-byte where possible.
Do not return a rendered numbered target.
