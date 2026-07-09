# FILE_PLACEMENT.md — Manual File Placement Checklist for Ahmed

All files below are placed **manually by Ahmed** before Phase 3 begins.
`validate_data` (Phase 3) is the gate that verifies their presence and correctness.
Do **not** commit these files to Git — they are listed in `.gitignore`.

---

## Checklist

- [ ] **`PROJECT_EXECUTION_PLAN.md`** → repo root (`P:/Interview IQ/PROJECT_EXECUTION_PLAN.md`)
  - Already present if you are reading this file.

- [ ] **`decisions.md`** → repo root (`P:/Interview IQ/decisions.md`)
  - The unified decision log (D## entries). Create or copy from your notes before Phase 2.

- [ ] **`data/questions/questions_250.json`**
  - 250 questions across DA / DS / CS / SE / GN tracks (50 each).
  - Placed manually before Phase 3. Never generated or modified by Claude.

- [ ] **`data/refdocs/reference_docs_250_FINAL_v1.json`**
  - Reference documents for all 250 questions, chunked (one fact per line,
    Modern Standard Arabic, technical terms in Latin script).
  - Note (Q2 in plan): internal metadata still marked DRAFT / "AI-generated,
    pending expert review". Ahmed is responsible for defending the review status
    before academic submission.
  - Placed manually before Phase 3.

- [ ] **`data/nli/gold_set_48.json`**
  - DS-014 Gold Set — 48 NLI pairs, **evaluation only**.
  - **HARD RULE (D-DS014 / Plan §5 Rule 7):** This file must NEVER appear in
    any training premise pool. `validate_data` enforces this automatically.
  - Placed manually before Phase 3.

- [ ] **`data/nli/pairs_pilot_150_v2/pairs_DA001_pilot_v1.json`**
  - DA001 pilot NLI pairs (Stage 1–3 complete; Stage-4 human review pending — RISK ACCEPTED per decisions.md).
  - Placed manually before Phase 3.

- [ ] **`data/nli/pairs_pilot_150_v2/pairs_pilot_remaining9_v2.json`**
  - Remaining 9-question pilot NLI pairs.
  - Together with `pairs_DA001_pilot_v1.json` these constitute the full 150-pair
    pilot set (target distribution: E=50 / C=60 / N=40).
  - Placed manually before Phase 3.

---

## Notes

- `validate_data` (Phase 3 deliverable) is the **automated gate** for all files above.
  It will hard-fail (non-zero exit) if any file is missing, malformed, or violates
  schema / uniqueness / DS-014 exclusion / HARD_POS twin integrity / label distribution.
- Do not move on to Phase 4 until `validate_data` exits 0.
- Open question Q9 (GitHub repo URL) must be resolved before filling in the
  Kaggle Runner notebooks in Phase 4–7.
