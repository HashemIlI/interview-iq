# Field Run Constraint Checklist (post prompt-v2, D95)

**Purpose:** D94 found that real field-run violations (O-a transliteration inconsistency, O-b invented naming) were logged as non-gating "additional observations" rather than checked against a fixed list — there was no standing checklist tying field-run review to every constraint in `src/interview_iq/decomposition_llm/system_prompt.md`. This checklist closes that gap. Run it against every future field run's claim output (SE/GN/DA/... audio, not just synthetic sanity-gate fixtures), in addition to — not instead of — the sanity gate.

**How to use:** for each claim decomposition output in a field run, check every row below PASS/FAIL against the actual `answer_text` input and produced claims. Any FAIL is a logged field violation regardless of whether it affects the run's C1/C2/C3-style scoring criteria. Record results per case (e.g. `SE-028: C1=PASS, C3=FAIL(...)`) alongside the run's other evidence.

| # | Constraint (system_prompt.md ref) | Check |
|---|---|---|
| C1 | HARD CONSTRAINT 1 — no correction/completion of wrong or incomplete content | Every wrong/incomplete fact in the input appears unchanged in the claims. No claim reads as "corrected". |
| C2 | HARD CONSTRAINT 1 — no numeric substitution | Every numeric value the candidate stated appears unchanged, even when factually wrong and even mid-sentence. |
| C3 | HARD CONSTRAINT 1 (prompt-v2 addition, P1) — no meta-commentary / editorialized correction | No claim contains a comparison to the "true" value or commentary about the transcript (e.g. "X, not Y as stated", "but the original said Y"). |
| C4 | HARD CONSTRAINT 2 — no added facts/examples/details | Nothing appears in the claims that is not explicitly present in the input. |
| C5 | HARD CONSTRAINT 2 (prompt-v2 addition, P5) — no invented labels | If the speaker does not name something (or trails off before naming it), no claim assigns it a name. |
| C6 | HARD CONSTRAINT 3 — mandatory transliteration | Every English/technical term written in Arabic letters in the input appears in Latin script in the claims, for every occurrence (not just some). |
| C7 | HARD CONSTRAINT 3 (prompt-v2 addition, P3) — spelled-out acronyms | Letter-by-letter spelled acronyms (e.g. تي دي دي) are converted to the acronym in Latin script (TDD), never left as separate letters, never dropped. |
| C8 | HARD CONSTRAINT 3 (prompt-v2 addition, P4) — near-homograph disambiguation | Ambiguous surface forms (e.g. بيت→bit/byte) are transliterated per local context, without altering, hedging on, or commenting on any asserted quantity. |
| C9 | HARD CONSTRAINT 4 — atomicity | Each claim contains exactly one proposition; multi-fact sentences are split, not merged. (Non-blocking per D77 — log AMBIGUOUS/NON_ATOMIC but do not fail the run on this alone.) |
| C10 | HARD CONSTRAINT 5 — self-containment | No claim relies on a bare pronoun resolved only in another claim; the explicit subject is repeated. |
| C11 | HARD CONSTRAINT 6 — no evaluation/judgment | No claim evaluates, judges, or comments on correctness; no headers/explanations/preambles outside the numbered list. |
| C12 | HARD CONSTRAINT 7 — empty/unintelligible input handling | If applicable, output is exactly `NO_EXTRACTABLE_CLAIMS`, not a guess. |
| C13 | HARD CONSTRAINT 8 — Arabic prose surrounding Latin terms | Claim sentences (subject, verb, connectors, explanation) are simplified-MSA Arabic; only individual technical terms stay in Latin script, regardless of how English-heavy the input is. |

**Non-constraint field observations** (e.g. `asr_device` resolution, timing/latency, infra config) are still logged separately as observations, not against this checklist — this checklist is scoped to `system_prompt.md`'s constraints only.

**Reference:** D94 (decisions.md — gap this closes), D95 (decisions.md — prompt v2 + gate fixtures v2 that this checklist's C3/C5/C6-C8 rows correspond to), D77 (decisions.md — atomicity non-blocking precedent).
