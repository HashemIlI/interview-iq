# decisions.md — Interview IQ / Unified Decision Log (D1–D81)
**Version:** v3.4 — 28 July 2026 (D103 — outcome of D102: glossary layer measured; four findings recorded, F4-F7)
**Status:** The sole legal project record. This file supersedes and merges the former Arabic `decisions.md` and `DECISIONS_RECONCILIATION_v1.1`. The pre-D81 Arabic original is archived (see D81), not deleted.

**Governing numbering rule:** D1–D25 are fixed as in the master document `InterviewIQ_Pipeline_Docs_v2.0.md`. The pipeline-session decisions were renumbered D26–D34. Every new decision takes the next free number.

**Status legend:** ✅ locked / final · ⛔ open / pending · 🔶 empirical / unverified · 🗑️ cancelled

---

## Snapshot — Current State (21 July 2026)

- **NLI module (mDeBERTa-v3 + LoRA):** complete, validated, locked. Phase 5 Gold Set (DS-014, n=48) PASSED under the pre-registered rule; inference is deterministic (48/48). Open risk: the Coverage channel has still never been measured on real decomposition output (Q8).
- **Claim Decomposition:** pivoted (D74) from AraT5 full fine-tuning to a runtime external LLM API (OpenRouter), supervisor-approved, after AraT5 showed severe generalization failure. Phase 8 (AraT5) is CLOSED — SUPERSEDED.
- **Decomposition model now in use:** `cohere/north-mini-code:free`, adopted after passing the mandatory D77/D74 sanity gate 8/8 (D80). Three earlier candidates were rejected: nemotron (CoT leakage), gemma (rate-limited), llama-3.3-70b (free slug deprecated).
- **Runtime constraint:** "Zero-LLM-at-runtime" now applies to the whole pipeline **except** Claim Decomposition (D74). The correctness judgment itself stays LLM-free (local NLI).
- **Next up:** wire decomposition into the production pipeline; measure the Coverage channel on real claims (Q8, unblocks now that decomposition produces output); threshold calibration (G4); ASR pilot/model selection (Q7/G3); Demo #1 (Q10).

---

## Section 1 — D1–D25 (legal text lives in the master pipeline document)

Full text of these decisions is in `InterviewIQ_Pipeline_Docs_v2.0.md` and is not copied here. Only the items referenced or amended by consolidation are listed.

- **D19 ✅** — Development is local (Claude Code + Git); GitHub is the single source of truth; Kaggle is the GPU engine via thin runners.
  - *Documented, closed deviation (8 Jul):* the staging notebook pulled scripts from a Kaggle Dataset instead of `git clone` because the repo did not yet exist. Resolved once the repo was published.
  - *Q9 closed (9 Jul 2026):* official repo = https://github.com/HashemIlI/interview-iq (private). Runner notebooks pull exclusively via `git clone` + a PAT from Kaggle Secrets (`GH_TOKEN`).
  - *Environment note:* the default Kaggle image ships a newer `peft` + incompatible `torchao==0.10.0` ⇒ `get_peft_model` fails with `ImportError`. The runner explicitly reinstalls `requirements.txt` and removes `torchao`.
- **D20 ✅ / 🗑️** — Linguistic Confidence Module permanently out of scope; everything related to it is cancelled.
- **D21 ✅** — Option B Dual-Channel Scoring (Precision + Coverage → Harmonic F). *(Consolidation note: the old "D21 update" was a different decision — now D26.)*
  - *Structural consequence (D44):* the harmonic merge means `Coverage = 0` zeroes F regardless of Precision ⇒ **an unmeasured Coverage channel leaves half the scoring system unverified.**
  - *Implementation detail (D45):* merge behavior at `Precision < 0` and for the silent answer is ratified in D45.
- **D22 ✅ (amended)** — adds officially: **τ_E = 0.9**, tagged `PRE-CALIBRATION DEFAULT — NOT VALIDATED`.
  - *Calibration input (D43):* on the Gold Set, `τ_E = 0.9` is not strict — 14/17 entailment pairs clear it in the fine-tuned model.
- **D24 ✅** — Baseline Demo for the supervisor. *(Numbering clash with "P09 Edge Case" resolved: the latter became D29.)*
- **D25 ✅ (constrained)** — the three data layers (Easy Pos/Neg/Hard Neg) were designed before the Subject Blindness diagnosis; **the actually-implemented NLI data structure is the six D32 categories, which replace them.** Still in force from D25: the pre-registered zero-shot thresholds (Contradiction F1 < 0.75 **or** E↔C confusion > 5% ⇒ fine-tuning mandatory).
  - **Later audit (D41):** on the Gold Set, zero-shot scored `Contradiction F1 = 0.865` ⇒ **first condition not met**. The actual trigger was the second alone: `E↔C = 8.3% > 5%`. Any claim that zero-shot "failed catastrophically" is **unsupported** at argmax level.
  - **But (D43):** reading raw probabilities against the actual scoring threshold, zero-shot commits **two false verifications** (P12, P34). **This is the strongest quantitative evidence that fine-tuning was necessary.**

---

## Section 2 — NLI Module & Scoring Engine (D26–D49)

### D26 — Hard Positive Pairing Rule (✅ locked) *(formerly "D21 update")*
- Each HARD_POS instance emits **two forced pairs bound to the same claim text**:
  - Pair A: premise = original chunk (entity X), label = entailment.
  - Pair B: premise = chunk about a different entity Y in the same document (distractor), same hypothesis, label = **neutral**.
- The resulting N is named `paired_neutral`, distinct from `standard_neutral`.
- **Operational rule:** twins are never split across the train/val boundary.
- *Automated check:* `validate_data` confirmed **30 intact twin groups** across the 150 pairs.
- **Observed empirical effect (D41):** twins = 60/150 = **40% of the training signal**, explicitly teaching "premise about a different entity ⇒ neutral." This is the **mechanistic explanation** for the fine-tuned model's shift toward `neutral`.
- **Predicted effect on the Coverage channel (D42-b):** in the reversed direction the normal case is premise (claim) about one aspect, hypothesis (key point) about another — **exactly the case the model was explicitly trained to label `neutral`.** Testable prediction — tested in D46-C.

### D27 — Pilot Scope Reduction (🔶 empirical, capacity-driven) *(formerly D22)*
- Reviewing 47 documents before generation was unrealistic within the available review budget.
- Decision: Phase 1 pilot = **10 documents only (2 per track)**, chosen as **contrastive**.
- Approved docs (✅ manually reviewed): DA-001, DA-003, DS-001, DS-003, CS-002, CS-004, SE-001, SE-005, GN-001, GN-008.
- Pool expansion deferred until the pipeline proves out end-to-end and a separate document-review time budget is allocated.

### D28 — Gold Set Leakage Resolution (✅ confirmed) *(formerly D23)*
- The entire 48-pair Gold Set comes from **one question: DS-014 (Overfitting)**.
- Rule: **DS-014 is permanently excluded from the premise pool of any training data**, no exceptions. Reserved exclusively as a held-out evaluation set.
- Enforcement: check in `validate_data` + `D28ContaminationError` in `finetune.py` + a filesystem gate in the Kaggle runner (D37).
- *Verified:* zero contamination in the 150 pairs.
- **Additional use (D46):** as the only document whose chunks the model never saw as a premise, it is the only clean source for the reversed-direction diagnostic.

### D29 — P09 Edge Case Resolution (✅ resolved) *(formerly D24 in the old log)*
- Case: DA001-P09 (subject-swap) — "semi-structured has no organizational form" vs premise C03 "contains organizational tags/keys".
- Decision: **confirmed contradiction.** An absolute negation collides with a partial assertion — a direct logical contradiction, not two non-exclusive alternatives like the reference weak-contradiction case (**P48: two non-conflicting detection methods**).
- **Later note (D41):** the P48 description above — written **before** Phase 5 — is consistent with the fine-tuned model labeling it `neutral`. **The label was not changed.**

### D30 — Pilot Generation Complete (✅ 150/150 pairs, Stages 1–3)
- Overall distribution: E=50 (33.3%) | C=60 (40%) | N=40 (26.7%).
- Subject-swap = 40/60 of C = **66.7%** (below the 73% target; to be corrected at scale).
- *Automated check:* `validate_data` confirmed the distribution exactly.

### D31 — Genuine Stage 2 Pass on 9-Doc Set (✅ completed, findings logged)
- Explicit correction: the prior "Stage 3 done programmatically ✅" claim was an assumption, not an execution.
- **Result:** 132/135 confirmed, **2 genuine near-duplicates** replaced (DS003-P06, CS004-P06), **1 lower-confidence case** (DA003-P10).
- Approved file: `pairs_pilot_remaining9_v2.json` — **supersedes** v1.
- **Logged lesson (general rule — §5.13):** always distinguish "actually executed with a tool" from "assumed/inferred." Conflating them caused:
  1. Missing a real duplicate (this item);
  2. Two false claims about the fine-tuning scope (D38);
  3. The unratified 0.002 figure (D42);
  4. Claiming `validate_data` does not check dangling key_points — the check had existed since Phase 3. A **supervisor** error: absence of the check inferred from absence of a per-chunk field.
  5. **(10 Jul 2026) Claiming `git log` proves a `results/phase5/*.json` change came from commit `da0a825`.** Structurally impossible: a file showing as `modified` in `git status` is an **uncommitted** working-tree change that `git log` cannot attribute to any commit. The conclusion (the change was not from the Phase 6 task) was correct, but the **evidence was fabricated.** Truth: the two files were replaced manually after a Kaggle rerun (D43) and not yet committed.
- **The rule applies to everyone without exception, and is elevated to §5 of `PROJECT_EXECUTION_PLAN.md` (Rule 13). A correct result with fabricated evidence = a full violation.**

### D32 — Per-Document Quota (✅ locked)

| Category | n instances | E | C | N |
|---|---|---|---|---|
| EASY_POS | 2 | 2 | | |
| HARD_POS | 3 | 3 (A) | | 3 (B) |
| EASY_NEG | 1 | | 1 | |
| SUBJECT_SWAP | 4 | | 4 | |
| HN_OTHER | 1 | | 1 | |
| STANDARD_NEUTRAL | 1 | | | 1 |
| **per doc** | **12 instances → 15 pairs** | **5** | **6** | **4** |

- **Replaces the three D25 layers.** Subject-swap share of C = 66.7%. Pilot: 10 × 15 = **150 pairs**.

### D33 — ⚠️ RISK ACCEPTED: Stage 4 not executed — G1 closed by risk acceptance (✅ closed by decision)
- **Per-pair review of the 150 pairs (Stage 4) was not executed** except P09 (D29). A documented deviation from the locked methodology, by Ahmed's explicit decision.
- **Final decision:** Phases 5+ proceed **without** the 20% retroactive spot-check. **G1 is closed by accepting the risk, not by completing the review.**
- **Non-negotiable counter-obligation:** stated explicitly in the write-up and defense:
  > "The 150 pairs did not undergo per-pair human review (Stage 4). They underwent automated and qualitative review (Stages 1–3) and manual review of the 10 reference documents. This is a known limit on label validity, and the fine-tuning results are read in that light."
- **Mitigations:** (a) the Gold Set is fully independent of training; (b) D31 documented discovery of real duplicates; (c) the effect of any corrupt labels shows up in the Gold Set confusion matrix.
- Every fine-tuning result produced under this decision is tagged `RISK ACCEPTED`.

### D34 — Deferral of Coverage-direction pairs (✅)
- Coverage-direction pairs are **excluded from the first fine-tuning batch** to avoid contaminating ablation results.
- **Logged side-effect (D42):** the fine-tuned model **never saw the Coverage direction** ⇒ using it there is **out-of-distribution (OOD).**
- **With Phase 5 done the deferral is lifted for discussion. Measurement on real claims remains deferred to post–Phase 8 (D44). The claim-free diagnostic is allowed and registered in D46.**

### D35 — Accepting the 5-word overlap rule violation (✅ ratified, corrected twice)
- **Approved figures:** 65/150 (43.3%). Distribution: **C = 37 · E = 28 · N = 0**.
- **Source:** `scripts/recount_overlap.py` — two independent algorithms give the same output.
- **Measurement definition:** NFC → strip `Mn`-category marks → lowercase → `re.findall(r'\w+')`, then ≥5 consecutive shared tokens. Does **not** include alif/hamza/ta-marbuta unification ⇒ **65 is a lower bound.**
- **Documentation correction:** a prior version recorded "43/150 with C=25/E=18." That figure is cancelled. **The cause of the discrepancy was not investigated.**
- **Decision: accept with documentation.** Rationale:
  - *On the E↔C axis:* the distribution does not create a "high overlap ⇒ Entailment" heuristic; it runs opposite to it (McCoy et al., 2019 — HANS).
  - *On the N/¬N axis:* perfect correlation in the data (75/75). **The learned-shortcut hypothesis was empirically rejected — D40.**
- **Limit on the measurement tool (D41):** P43 (near-verbatim paraphrase) recorded `overlap=False` ⇒ the metric is a **weak proxy** for semantic overlap in Arabic. It measures **surface match.**
- In `validate_data`: a **documented exception printed in the report**, not a hard failure.

### D36 — Validation Split Strategy (✅ ratified)
- `val_fraction: 0.2` **rejected** (may split twins; violates Question-ID-level splitting).
- Adopted: **document-level holdout on GN-008** (15 pairs), in `configs/nli_finetune.yaml`.
- **Known limit:** val = 15 pairs ⇒ high variance. Its role is checkpoint selection only. **Final judgment is on the Gold Set.**

### D37 — Data Staging on Kaggle (✅)
- Data files are excluded from Git, so `git clone` doesn't fetch them. A staging cell detects the Kaggle Dataset **by content, not by name.**
- **Documented exception to "zero logic in the notebook":** this is **environment logic**, not project logic.
- The Gold Set is a **separate** Kaggle Dataset (`iq-gold-set`) and is never mounted in a training session — an explicit `assert` verifies its absence.
- *Phase 5 extension:* the eval runner mounts the Gold Set, asserts the absence of pilot pairs, detects the adapter by content with a `RuntimeError` on failure, and includes a `SILENT ADAPTER FAILURE SUSPECTED` guard and an `--assert-matches` guard (D43).

### D38 — First Fine-tuning Run Result (✅ logged, RISK ACCEPTED)
- 135 training pairs / 15 val (GN-008 holdout). Kaggle T4 ×2. 5 epochs, 45 steps.
- eval_loss: 0.789 → 0.482 → 0.344 → 0.309 → 0.303 (converged). Best val macro-F1 = 0.927 (epoch 3) — **not cited as model performance.**
- Checkpoint published as `iq-checkpoints-nli-v1`. `load_best_model_at_end` enabled; the adapter matches `checkpoint-27` byte-for-byte.
- **Fine-tuning scope (corrected — empirically verified):** LoRA (r=16, α=32) on `query_proj`/`value_proj`, **plus the classification head**: `peft.get_peft_model(task_type=SEQ_CLS)` auto-injects `modules_to_save = {'classifier','score'}` even with `LoraConfig.modules_to_save = None`. **The head is trained and saved inside the adapter.** Any description otherwise is cancelled.
- **V1 (✅ closed):** `adapter_model.safetensors` = **50 keys** (48 LoRA + `classifier.weight` + `.bias`). Checked as the first cell in `run-nli-eval.ipynb`.
- **Subject Blindness result:** see **D41** (argmax) and **D43** (probabilities at thresholds).

### D39 — Pre-registered decision rule for Phase 5 (✅ — before run, commit `f4fbf27`)
- Gold Set: DS-014, n=48 — E=17 · N=12 · C=19.
- **Subject Blindness signature = the C→E cell.**
- **Success criteria (all three):** `C→E ≤ 2/19` · `Contradiction recall ≥ 16/19` · `E→C ≤ 2/17`.
- **Interpretation constraints (pre-registered):** the pair = 5.3% of C ⇒ thresholds by count not percent; a gap < 3 pairs is within noise · judgment is **directional, not statistical** · baseline = zero-shot on the same 48 via the same code path · single document ⇒ **existence** evidence, not **generalization** · macro-F1 is descriptive, not an acceptance criterion.
- **Acknowledged limit (D41):** it constrained the shift toward `contradiction` but **not the shift toward `neutral`** — which is what happened. **An incomplete acceptance rule.**
- **Second limit (D43):** written at `argmax` level, while the scoring engine works on probabilities at thresholds. **Correct, but not measuring what the system measures.** Any future scoring-stage rule is written at threshold level.

### D40 — Overlap is a data property, not a learned shortcut (✅ materially revised)
- **Descriptive stats:** pilot: 65 pairs (C=37 · E=28 · **N=0**) · gold: 10 pairs (C=5 · E=5 · **N=0**) ⇒ 75/75.
- **Structural cause:** neutral pairs draw the premise from a different chunk than the hypothesis source.
- **Empirical test (Phase 5) — rejects the learned-shortcut hypothesis:**

| Arm (overlap=True, n=10) | → E | → N | → C |
|---|---|---|---|
| zero-shot | 6 | **0** | 4 |
| adapter | 4 | **3** | 3 |

- The **base** model — which never saw training data — predicted `neutral` in **0/10**. It cannot learn an artifact from a file it never saw ⇒ the correlation is a **general property of NLI models trained on MNLI/XNLI**, semantically justified (E and C require topical overlap; N does not).
- The **fine-tuned** model: 3/10 ⇒ **moved away** from the correlation.
- The six errors toward `neutral` split **3 overlap / 3 no-overlap** ⇒ **no signal.**
- **Prior conclusion withdrawn.** *Limits of the negative:* n=10 ⇒ **underpowered** test. Reported as "a test was run and found no signal," not "the shortcut does not exist."

### D41 — Phase 5 Result: Gold Set Evaluation (✅ — RISK ACCEPTED)
- **Verdict against D39 (registered in `f4fbf27` before the run): PASSED — all three.**

| Criterion | zero-shot | adapter | verdict |
|---|---|---|---|
| C→E ≤ 2/19 | 3 | **0** | ✅ |
| Contradiction recall ≥ 16/19 | 16/19 | **16/19** | ✅ |
| E→C ≤ 2/17 | 1 | **0** | ✅ |

- **The E↔C cells were emptied. Subject Blindness — by the pre-registered definition — is broken.**
- **Limits:** C→E gap = exactly 3 pairs, **at the minimum**. E→C gap = one pair ⇒ **within noise**. Directional judgment (n=19). Single document ⇒ **existence**, not **generalization**.
- **What did not improve:** `Contradiction recall = 16/19` in both arms — a **wash**: P12, P34 fixed · P27, P31 broke ⇒ **the model did not detect more contradictions, it redistributed its errors.**
- **Cost at argmax:** macro-F1: 0.880 → 0.850 · neutral precision: 0.917 → 0.647 · errors: 6 → 7.
- **Gain under the scoring rule:** `entailment precision = 1.000` ⇒ zero false verifications at argmax level. ⚠️ *Post-hoc analysis, not an acceptance criterion.* ✅ Conditional warning lifted: D43 measured `P(E)` for C→N pairs and found it ≪ τ_E.
- **Mechanistic explanation of the neutral shift** (based on D26, written before the run): 40% of the training signal teaches "premise about a different entity ⇒ neutral." The observed effect is expected from the design.
- **Named cases:**
  - **P48** — gold=C · zero-shot=E · adapter=**N**. D29 (pre-run) describes it as a weak contradiction; the model's classification is consistent with that. **The label was not changed** — changing it after seeing the result would void pre-registration. Reported as a **limit on Gold Set validity.**
  - **P26** — gold=N · predicted=**C in both arms**. Label is correct, both models wrong. **The only remaining false-penalty generator** (D43).
  - **P43** — gold=E, near-verbatim paraphrase, both arms said `neutral` despite `overlap=False` ⇒ a limit on the overlap metric (D35).
- **Outputs:** `results/phase5/gold_eval_{zero_shot,adapter}.json` — **replaced (10 Jul)** by V2 copies carrying probabilities; the 48 `predicted_label` values are **byte-identical**, verified by `--assert-matches` (D43).

### D42 — Reframing Q8 and withdrawing the 0.002 figure (✅ corrected and expanded)
- **(1) The 0.002 figure is withdrawn — no source.** One appearance in the repo described as a "documented example." **No script, no JSON, no input description.** Non-citable, removed from the plan (§5.13).
- **(2) The "long formal chunks" claim is falsified by measurement.** Chunk length: **mean = 15.5 · median = 15 · p90 = 20** (whitespace tokens). **There is no length asymmetry.** The term is replaced by **"Coverage-channel fragility."**
- **(3) Coverage was never measured** (at time of writing): `scoring/*` and `nli/engine.py` = 0 bytes. **A worry-hypothesis, not an experiment result.** *(Built in Phase 6; still unmeasured on real claims — D44.)*
- **Supervisor-issued correction:** the first version claimed `validate_data` does not check `key_points`. **Wrong** — the check has existed since Phase 3. Its absence was inferred from the absence of an `is_key_point` field — **inference, not verification** (§5.13).
- **The denominator is sound:** `meta.key_points_semantics` defines Coverage over a subset (`key_points`). **V3: 250/250 pass** ⇒ no structural ceiling from corrupt data.
- **Three hypothesized sources of fragility:**
  - **(a) Reversed direction is OOD:** the model never saw it (D34). Tested in D46-A/B.
  - **(b) Learned `neutral` shift:** D26 makes 40% of the training signal teach "different entity ⇒ neutral," which is the normal case in the Coverage direction ⇒ the fine-tuned model is expected to be **worse** than zero-shot. Tested in D46-C.
  - **(c) Composition error:** `max_entailment_per_keypoint` with a single premise claim ⇒ a key point requiring two claims jointly is entailed by no single claim. A flaw in the aggregation rule — only testable with real claims (D44).
- **Measured channel-coarseness figures:** chunks/doc: min=6 · max=12 · mean=6.06 · median=6. key_points/doc: min=2 · max=6 · mean=2.9 · median=3.

| key_points | docs | weight each | one miss ⇒ F (at P=1.0) |
|---|---|---|---|
| **2** | **63 (25.2%)** | **50%** | **0.67** |
| 3 | 154 (61.6%) | 33% | 0.80 |
| 4 | 29 (11.6%) | 25% | 0.86 |
| 5 | 3 | 20% | 0.89 |
| 6 | 1 | 17% | 0.91 |

⇒ **a quarter of questions have only two key points** ⇒ the channel is **nearly binary**; missing both ⇒ **zero regardless of Precision.** Averaging (2.9) hides this.
- **Anomaly — SE-006:** the only doc where `len(key_points) == len(chunks)` (6 = 6). **Likely a generation error. Not changed** — inspected under Q2, with the three docs that have 5 key points.

### D43 — Raw probabilities at scoring thresholds · V2 closed (✅ post-hoc)
- **V2 closed.** `[reproducibility gate] PASSED` on both arms: **48/48 matching predictions** ⇒ (1) the inference path is **deterministic** — despite `use_deterministic_algorithms(warn_only=True)`. **Empirically proven, not assumed.** (2) D41 is reproducible. (3) Adding probabilities **did not change argmax.**
- **The question left open in D41 — resolved.** `P(E)` for C→N pairs in the adapter: P27=0.003855, P31=0.001559, P48=0.051490 — all **far below τ_E = 0.9.** The conditional D41 warning is **lifted.**
- **New result — zero-shot commits two real false verifications under the v2 rule:**

| pair | gold | zero-shot P(E) | verdict at τ_E = 0.9 |
|---|---|---|---|
| **P12** | contradiction | **0.916049** | ⚠️ VERIFIED |
| **P34** | contradiction | **0.984997** | ⚠️ VERIFIED |
| P48 | contradiction | 0.781239 | below threshold ⇒ ignored |

In the adapter: **zero.** Highest `P(E)` on any contradictory claim = **0.203164** (P12). **This is the strongest quantitative evidence for fine-tuning** — sharper than argmax, because it measures what the system measures.

| Under thresholds (τ_E=0.9 · τ=0.5 · α=0) | zero-shot | adapter |
|---|---|---|
| false verification (C ⇒ VERIFIED) | **2** (P12, P34) | **0** |
| false penalty (E/N ⇒ penalty) | 2 (P26, P37) | 1 (P26) |
| true verification (E ⇒ VERIFIED) | 15/17 | 14/17 |
| missed penalty (C ⇒ ignored) | 1 (P48) | 3 (P27, P31, P48) |

- **The trade:** lose one true verification + two missed penalties, in exchange for **eliminating two false verifications and one false penalty.** Under the D21 ordering this is a **net gain**, measured at the threshold.
- **Generalization constraint:** Gold Set pairs are **single** `(premise, hypothesis)`, so `max_E`/`max_C` are over one chunk. In the real path they aggregate over a Claims × Chunks matrix (SummaC). **Direction correct, absolute values approximate.**
- **Calibration inputs (for G4 — not decisions):**
  - `τ_E = 0.9` is not strict: 14/17 entailment clear it in the adapter.
  - Calibration shift: fine-tuning systematically lowered confidence (correct E: ≈0.998 → ≈0.98). Closest two pairs: **P17 = 0.957947 · P05 = 0.961640** ⇒ **constraint on any further training: more epochs may drop them below `τ_E`.**
  - `τ = 0.5` is not critical: weakest contradiction detected `P(C) = 0.772790` (P12).
  - **P26 generates a false penalty in both arms** — `P(C)`: 0.992138 → 0.746531. Harm reduced, not eliminated.
- **Output change:** `results/phase5/*.json` replaced by copies carrying `probs`. `predicted_label` is byte-identical ⇒ no D41 number is affected.

### D44 — Coverage-experiment claim source: deferral (✅) [closes V4]
- **Decision:** the Coverage-channel measurement experiment is **deferred to post–Phase 8.** Gold Set hypotheses will **not** be used as synthetic claims, and candidate answers will **not** be hand-written as an interim substitute.
- **Rationale:**
  - *(a) Gold Set hypotheses as premises:* **rejected.** Authored by the same convention as chunks ⇒ measures **data consistency with itself.** Any resulting number is **structurally optimistic and non-citable.**
  - *(b) Hand-written candidate answers as interim:* **rejected** — consumes the same human effort as O9 without producing the academic deliverable.
  - *(c) Defer until claims come from the decomposition module:* **adopted.**
- **Price — explicitly accepted:**
  1. The Coverage channel stays unmeasured on real claims even after Phase 8.
  2. Harmonic merge ⇒ `Coverage = 0` zeroes F (D21). Any structural flaw in it **effectively voids** the Phase 4–5 results from a final-system standpoint.
  3. ⚠️ **O9 moves to the critical path:** `O9 → G2 → Phase 8 → Coverage experiment → Q8 verdict → verdict on the whole scoring engine.`
- **Counter-obligation:** O9 is completed **before** any scope expansion (the 37 docs) and before any second training batch.
- **Two standing mitigations:**
  - *Code mitigation (Phase 6):* unit tests pinning the fragility explicitly — `Coverage = 0 ⇒ F = 0` despite `Precision = 1.0`; and a 2-key-point doc: one miss ⇒ `F ≤ 0.67`. Prevents silent regression, **does not replace measurement.**
  - *Diagnostic mitigation (D46):* checks model behavior in the reversed direction **with no claims.** Can prove the channel is **broken**; cannot prove it is **sound.**

### D45 — Merge semantics at negative Precision and the silent answer (✅ ratified — 10 Jul 2026)
- **Context:** during Phase 6 two decisions were taken in `scoring/metrics.py` that were not registered. Ratified here explicitly rather than left as an implementation side-effect.
- **(a) `Precision` = arithmetic mean of claim scores, allowed to be negative.** Justified by D21: the contradiction penalty (`score = −max_C`) is meaningless if clipped at zero.
- **(b) If `Precision < 0` ⇒ final output = `Precision`, and the Coverage channel is ignored entirely.**
  - *Meaning:* an answer containing a net contradiction **nullifies the coverage weight.** A candidate who covered every key point but said one false sentence, enough to make the mean negative ⇒ coverage carries no weight.
  - *Justification:* the harmonic mean is **semantically undefined** for a negative number, and the only alternative — clipping `Precision` at zero — makes **"said wrong" and "stayed silent" equal at `F = 0`**, a **direct violation of the locked D21 ordering** (`said correct > silent > said wrong`).
  - *Effect:* the strict ordering is preserved, pinned in `tests/test_scoring.py` (item d) with a strict inequality.
- **(c) Two implementation items to document in the same module (⛔ — see V5):** (1) the final score range (D21 says `0–100`; with (b) it may go negative — report what the code actually produces); (2) the silent answer (`claims == []`), an undefined mean over an empty list — report the value the code produces, since "silent" is a base category in the D21 ordering.
- **Status:** (a) and (b) **ratified.** (c) **open as V5** — report the code's behavior, don't change it.

### D46 — Pre-registered reversed-direction diagnostic (✅ registered before the run — 10 Jul 2026)
- **This is not a Coverage-channel measurement.** D44 stands. This is a **claim-free check of model behavior in the reversed direction** — uses no decomposition output, produces no Coverage score for any answer.
- **Source: `DS-014` only** — the one document whose chunks the model never saw as a premise (D28) ⇒ the only clean sample. Compared on both arms (zero-shot vs adapter), same code path.
- **A — floor (self-entailment):** `premise = chunk_i` · `hypothesis = chunk_i` (byte-identical). Criterion: `median P(E) ≥ 0.90`. Failure ⇒ the channel is structurally broken and the discussion ends there.
- **B — ceiling (no relation):** `premise = DS-014 chunk` · `hypothesis = SE-001 key point` (distant doc). Criterion: `median P(E) ≤ 0.10`. Failure ⇒ the channel treats any text as covering anything ⇒ non-discriminative.
- **C — cross-entity (tests D42-b directly):** `premise = chunk about entity X` · `hypothesis = key point about entity Y`, **within the same document** — the case the model was explicitly trained to label `neutral` (D26). **Pre-registered prediction:** the adapter's `median P(E)` is **lower** than zero-shot's. **Signal criterion:** a gap ≥ 0.10 in the median ⇒ fine-tuning harmed the Coverage channel, and D34 gains a measured price. A gap < 0.10 ⇒ no signal; hypothesis (b) is not proven (nor refuted — underpowered).
- **Pre-registered constraints:** n is very small (6 chunks · 3 key points for DS-014) ⇒ directional not statistical. Cannot speak to Coverage on a real candidate answer, the composition error (D42-c), or the behavior of colloquial decomposed claims. **Asymmetric inference:** failure proves the channel is broken; success **does not** prove it is sound. Run **after** committing this item; raw outputs saved to `results/probe_reversed/`.

### D47 — Score-range correction: [-100, +100] instead of "0–100" (✅ ratified — 10 Jul 2026)
- **Supersedes:** the D21 text saying the range is "0–100."
- **Evidence:** commit `d7db5e6` · `tests/test_scoring.py` (7 regression tests) · docstring in `src/interview_iq/scoring/metrics.py`.
- **Resolution (V5):** measured empirically on `43dae43`. Final score range at `alpha=0.0` (PRE-CALIBRATION DEFAULT) is **[-100.0, +100.0]**, not [0, 100]. One fully contradictory claim (`max_c=1.0`) yields `score = -100.0`.
- **Ordering preserved:** D21's "said correct > silent > said wrong" holds numerically: `-100 < 0 <= 100`. The correction is on the lower bound only (see D45 for why negative Precision bypasses the whole Coverage channel to preserve this ordering).
- **Warning — re-measure after G4:** the lower bound is a function of alpha, currently a PRE-CALIBRATION DEFAULT (0.0). Not a system constant; must be re-verified after calibration.
- **§5.13 note:** `harmonic_f(0.0, 0.0)` returns `0.0` (measured and pinned). The divide-by-zero avoidance mechanism is **unverified.** No guard clause is assumed or claimed — the behavior is confirmed as an output only, not as a mechanism.
- **Regression coverage** (`tests/test_scoring.py`, 7 new tests, zero breakage, 105 pass = 98 + 7): `harmonic_f(0.0,0.0)→0.0`; `harmonic_f(0.0,1.0)→0.0`; `harmonic_f(-1.0,1.0)→-1.0`; `harmonic_f(-1.0,0.0)→-1.0`; `precision_channel([],[])→(0.0,[])`; silent answer `→ score=0.0`; one contradictory claim `→ score=-100.0`.
- **Procedural note (not a violation — logged for cleanliness):** the `push` of `d7db5e6` to `origin/main` was manual by Ahmed, not Claude Code. Verified 11 Jul 2026. No violation of "Claude Code does not push without confirmation." Whether git status was shown and confirmation awaited before that commit is unconfirmed in either direction, so it is not logged as a documented violation absent evidence.

### D48 — Local dev environment: Python 3.11 instead of 3.14 (✅ ratified — 11 Jul 2026)
- **Context (V6):** the local machine had only Python 3.14.2. A PyPI-JSON-API check proved that 6 compiled packages in requirements.txt (torch, torchaudio, PyYAML, numpy, pandas, scipy), at their pinned versions, **have no cp314 wheel on any platform.** The rest are universal py3-none-any and unaffected.
- **Decision:** install Python 3.11 locally (separate from system 3.14) and build a new `.venv` on it. **No changes to requirements.txt pins** — empirically confirmed all 6 critical packages have full wheels at their exact pins under cp311.
- **Rejected alternative:** bumping pins to the latest cp314-supported versions (numpy 2.5.1, pandas 3.0.3, etc.) — rejected because it forces major version jumps across an interdependent library chain without cross-compatibility verification, needlessly threatening reproducibility.
- **Separate exception — FlagEmbedding==1.2.5:** sdist-only (no wheel for any Python). Not resolved by this decision; needs build tools or separate handling.
- **Status:** ✅ executed and verified. Python 3.11.9 installed alongside 3.14.2 (untouched). New `.venv`, all 15 pins (incl. FlagEmbedding sdist) installed verbatim with no discrepancy. After `pip install -e .`: **130/130 tests pass, zero errors** (two non-critical peft UserWarnings). `git status` clean outside `decisions.md`. **V6 closed.**

### D49 — Result of D46: reversed-direction diagnostic (✅ closed — 11 Jul 2026)
- Probe executed on Kaggle T4 (commit `acc802a`).
- **Test A (self-entailment)** median P(E): zero-shot=`0.997138` (PASS), adapter=`0.920706` (PASS, tight `0.0207` above the `0.90` threshold).
- **Test B (no-relation ceiling)** median P(E): zero-shot=`0.00288` (PASS), adapter=`0.0061265` (PASS).
- **Test C (cross-entity signal):** `diff=-0.003014`, `signal_detected=false`, `direction_matches_prediction=false` — the predicted adapter degradation was not detected.
- Per D46's registered asymmetric inference (failure proves breakage; success does not prove soundness), this is **not** proof the reversed direction is sound, only that this specific diagnostic did not catch a break.
- **Fragility note (results analysis, not an acceptance criterion):** 4 of 12 individual self-entailment pairs in the adapter fell below `0.90` (lowest `0.767`); only the median is the registered criterion, and it passed.
- **D46 status: closed.**

---

## Section 3 — Claim Decomposition Module (D50–D80)

### 3a — O9 Gold Set + Q6 model choice (D50–D57)

### D50 — O9 sample pre-registration (✅ before the draw — 11 Jul 2026)
- **Sample size:** 25 questions (10% of 250), stratified evenly: 5 per track (DA/DS/CS/SE/GN).
- **Four already done manually before this registration:** DA-001, DA-002, DS-010, DS-011 — counted within the 25, not redone.
- **Remaining to draw randomly:** DA=3, DS=3, CS=5, SE=5, GN=5 (total 21).
- **Selection:** fully random within each track (excluding the four completed), fixed `seed=20260711`, documented in advance. No difficulty criterion or manual picking, to prevent annotator bias toward easier questions.

### D51 — O9 full closure (✅)
- All 25 questions from D50 decomposed (`results/o9_decomposition_exercises.md`). Distribution DA/DS/CS/SE/GN = 5 each.
- Included R1 cases (errors preserved without correction) in **7 questions, 9 tagged claims**: DA-029, DS-030 (×2), DS-033, SE-007, SE-013 (×2), SE-037, GN-004 — **all organic, arising during authoring; none pre-planned** (the D50 draw was fully random, `seed=20260711`, and D50 names no question as an R1 test case). Also 5 uncertainty-documentation cases as standalone claims (CS-024, CS-039, SE-041, GN-012, GN-045). Three open, non-decisive review notes are documented in the file itself (DA-001 claim atomicity, DA-046 closing-sentence classification, DS-030 optional hesitation documentation) — non-blocking, left for later review if needed.
- **Corrected** the stats line in `o9_decomposition_exercises.md` (had said "7 cases, 2 pre-planned and 6 organic" — inconsistent (2+6=8) and a pre-planning claim contradicting D50's random draw).
- O9 status: closed. Opens the path to G2 then Phase 8 (previously blocked on O9 exclusively, see D44).

### D52 — G2 full closure, following O9 (✅)
- The 25 manual exercises in `results/o9_decomposition_exercises.md` were the shared basis of both O9 and G2. With O9 closed in D51 (commit `282fc87`), G2 closes automatically with no separate work.

### D53 — Q6 decision rule (AraT5 vs mT5-base): 5-question diagnostic pilot (✅ — superseded context)
- **Sample (named, purposive to cover the hardest cases):** DA-029, DS-030, CS-039, SE-013, GN-004 (raw answer + manual reference claims for reference only, not passed to the models).
- **Procedure:** UBC-NLP/AraT5-base (candidate_a) and google/mt5-base (candidate_b); zero-shot only, no fine-tuning; identical prompt template for both; input = raw answer only; output = raw text, saved unprocessed.
- **Criteria (directional, n=5):** R1 adherence (no correction of candidate errors), R3 (preserve hedging), R4 (generalize personal phrasing), simplified-MSA soundness + Latin-script technical terms, absence of hallucination. Manual evaluation by Ahmed only, no automated metric.
- **Explicit note:** directional (n=5), not statistical; not used as sole final evidence — Q6 could require a wider pilot or a mini fine-tuning experiment if results tie.
- **Architectural constraint:** `scripts/q6_pilot_decomposition.py` is fully independent of the locked `src/interview_iq/decomposition/` package (D52); as a diagnostic tool it may load an explicit model name (the no-hardcoding constraint applies only to the src package).
- **Addendum (13 Jul):** the first AraT5-base run produced collapsed generation (infinite single-token repetition) on all five — a technical fault in `generate()` settings (missing repetition_penalty/no_repeat_ngram_size), not evidence of the model's task performance. mT5-base produced grammatically coherent output prefixed with `<extra_id_0>` (a span-corruption token from pretraining), suggesting text-only zero-shot may be insufficient for either model. Added repetition_penalty=1.3, no_repeat_ngram_size=3, min_new_tokens=5; the first run's results are not used as a basis for Q6.

### D54 — Q6 resolved: AraT5-base selected (✅ — later reopened, see D65; closed by pivot D74)
- **The D53 pilot did not favor either model:** both failed zero-shot on the 5 questions even after fixing generation settings. AraT5-base produced random multilingual text; mT5-base produced short output prefixed with `<extra_id_0>` in both runs. **Neither run is used as evidence of superiority.**
- **Actual basis for the decision (independent of the zero-shot result):** AraT5-base is pretrained exclusively on Arabic (MSA + dialects), whereas mT5-base is spread across 100+ languages with a relatively limited Arabic share. The target task (decomposing Egyptian-colloquial answers into simplified-MSA claims) is inherently Arabic-specific. Architectural hypothesis: AraT5-base is a closer starting point for later fine-tuning (Phase 8).
- **Decision:** `configs/decomposition.yaml`'s `model.selected` to be updated (out of this session's scope) from `"TBD_pending_Q6"` to `"UBC-NLP/AraT5-base"`.
- **Explicit note:** **not** based on measured performance — the pilot was evenly inconclusive. Based on an alternative architectural/linguistic argument. If indicators weakening this hypothesis appear during actual Phase 8 fine-tuning, Q6 reopens. *(It did reopen — D65 — and was ultimately closed by the D74 pivot.)*

### D55 — Decomposition corpus expansion: Gold/Validation Set + LLM-assisted data-prep batches (✅ complete — 223/225, 14 Jul 2026)
- **Context:** PROJECT_EXECUTION_PLAN.md:21 permits LLM use in offline data preparation only, with mandatory human review before any example is accepted. No LLM at runtime.
- **Decision (1):** reclassify O9 — `results/o9_decomposition_exercises.md` becomes a Gold/Validation Set (same methodology as DS-014/D28 for NLI), for evaluation only, not direct training.
- **Decision (2):** build a training corpus covering the remaining 225 questions using an LLM as an offline data-prep aid, with mandatory human review of every example.
- **Mandatory constraints:** deliberately targeting or pre-planning a specific technical error is **wholly prohibited, no exceptions.** Simulating wider variation in a hypothetical candidate's confidence/competence is allowed — any resulting technical error must be a natural byproduct of style, not a generation target.
- **Execution:** 5 batches, `seed=20260713`, each track run independently, R1–R6 reviews applied. First pilot batch = commit `957f1cc`.
- **"Memory-based generation" addendum (14 Jul):** across batch1+2+3 (110 questions), **zero organic R1 cases** despite the confidence-variation instruction. New mechanism (future batches only, not retroactive): for ~20% of each batch's questions (proportional across tracks), the raw answer is written without directly consulting the reference chunk — relying only on remembered/general knowledge, as a real candidate would answer from personal understanding. The binding no-targeted-error constraint is unchanged. Each question is tagged with its generation method (chunk-referenced / memory-based) for later analysis.
- **Completion (14 Jul):** batches (10, 50, 50, 50 [GN-050 excluded], 63) = 223 questions eligible for the training corpus out of 225 (SE-006 pending Q2; DS-014 permanently excluded by D28). Full human R1/R2 review by Ahmed. Cumulative: **0/273 organic R1 across all synthetic batches even with the memory-based mechanism** — documented as a structural limit of LLM ability to produce an organic error, not an execution flaw. commits: `957f1cc` (batch1) through batch5.

### D56 — Final fine-tuning prompt format (Phase 8) (✅)
- The D53 pilot only tested zero-shot instruction understanding (no fine-tuning) and its failure was inconclusive per D54; output format (claim shape) was never tested there.
- **Decision:** adopt the original PROMPT_TEMPLATE from `scripts/q6_pilot_decomposition.py` verbatim as the fine-tuning instruction base, plus an explicit output-format instruction (number each claim on its own line, no preamble/postamble) — this auto-matches the human format already used across O9 and all five batches, so training data needs no reformatting.
- **Constraint:** `scripts/q6_pilot_decomposition.py` stays unchanged (frozen D53/D54 evidence). The new format is a separate constant inside the `src/interview_iq/decomposition/` package.
- Claim separator in the target text: `"\n"` with a numeric prefix, matching the locked `output.claim_separator` in `configs/decomposition.yaml`.

### D57 — Initial trainer.py hyperparameters (Phase 8) (✅)
- **Context:** an empirical probe (§5.13) run by Ahmed via `scripts/probe_token_lengths.py` on the real corpus (222 training + 25 Gold/Validation, AraT5-base tokenizer), 16 Jul 2026. Raw: input p95=257 tokens (max=283), target p95=227 tokens (max=279), zero truncation at max_length=320.
- **Decision:** train/val 85/15 at question-ID level (~189 train / ~33 val); max_source_length = max_target_length = 320; LR = 3e-4 (AdamW), linear warmup 0.1; batch per-device=4, grad_accum=4 (effective=16); weight decay 0.01; max epochs 30 with early stopping on eval_loss (patience=5); eval each epoch, fp16, best checkpoint by eval_loss.
- All values tagged PRE-CALIBRATION DEFAULT (subject to G4), not the result of intensive search.
- **Correction (16 Jul, after first real Kaggle T4 run):** the original values lacked `save_total_limit`, so checkpoints accumulated each epoch (each a full model + optimizer state, since this is full fine-tuning not LoRA) until the disk filled and training crashed at epoch 8 (SafetensorError: No space left on device). The fix adds `save_total_limit: 2` — a gap missed in the first draft, not a wrong old value replaced.

### 3b — AraT5 fine-tuning attempt and its failure (D58–D73)

*This whole sub-phase is CLOSED — SUPERSEDED by the D74 pivot. Entries are condensed to their outcome; full procedural pre-registrations are in the archived Arabic original.*

### D58 — Post-training generation-failure diagnosis (✅ — functional failure confirmed)
- Controlled comparison (`transformers==4.40.2` = training version, Tesla T4, identical input and generation params) on the final model, `checkpoint-174`, `checkpoint-180`. All loaded fine; all lost the terms `SOC`/`SIEM`; all produced incoherent text with repetition and hallucinations. Changing transformers 5.0.0 → 4.40.2 did not fix it.
- **Limited conclusion:** the tied-weights warning, the transformers version, and final-vs-checkpoint choice are **not** the cause. The source is still undecided among training-data construction, tokenization/labels, and optimization/model state. `inference.py` stays blocked.

### D59 — Training-example / tokenization / labels diagnosis (✅ — base data sound; metadata leakage + UNK audit needed)
- Read-only diagnostic. Rebuilt corpus (222 examples) and split (189/33, zero overlap) from project code; no truncation. Data collator: 172 padding positions correctly `-100`, zero `pad_token_id` in labels. Final checkpoint failed even on training example `CS-025` (teacher-forced loss=4.6159997, greedy similarity=0.0286, beam=0.0598).
- **Discovered:** real metadata leakage in `SE-017` (`**[generation method: from memory, no direct reference]**`), and `<unk>` tokens on some Arabic words with tanwin/diacritics (e.g. `غالبًا`, `فعليًا`, `أيضًا`).
- **Also noted:** the actual run used **2 GPUs**, so effective global batch = `4 × 4 × 2 = 32`, not the intended 16 (D57). A logged execution fact, not by itself a proven cause.
- **Limited conclusion:** split, length handling, and label masking are not the cause. Cannot pin the cause to optimization alone before measuring corpus contamination and `<unk>` spread. `inference.py` and retraining stay blocked.

### D60 — Corpus contamination + UNK audit (✅ — 22 leaks found, wide `<unk>` spread)
- Read-only audit of all 222 examples. **22/222 = 9.91%** contain real metadata leakage as a standalone line (`**[generation method: from memory, no direct reference]**`); 19 in train, 3 in val. `CS-010`, `DS-037`, `SE-047` are false positives (do not modify).
- `<unk>` in 140 source / 210 target examples; totals sources=237, targets=912, clustering at `U+064B FATHATAN` (`ً`) and `U+064D KASRATAN` (`ٍ`). Full alignment of every `<unk>` position was not done — restricting the cause to these two marks is a hypothesis to verify in D61. Does not prove these two are the sole cause of the fine-tuning failure, but both must be fixed before any new optimization run.

### D61 — Deterministic corpus sanitization (✅ — PASS)
- Removed the standalone `**[generation method: ...]**` line only, plus a normalization removing only `U+064B`/`U+064D` from source and target before tokenization; all other Arabic marks unchanged (D60 did not prove them to produce `<unk>`). Natural occurrences of phrases like `من الذاكرة` / `LLM` inside answer content are preserved.
- commit `50a636c`. After sanitization: training 222 questions / 1,836 claims; O9 25 / 177; zero train/O9 overlap; zero source/target `<unk>`; max source/target 277/250 tokens; zero truncation at 320. `CS-010`/`DS-037`/`SE-047` preserved. **`D61 ACCEPTANCE: PASS`.** Does not alone prove corpus problems were the sole cause; next is a single-example overfit diagnostic.

### D62 — Clean single-example overfit diagnostic (✅ — `CS-025` exact token-ID match at step 175)
- From a fresh base AraT5-base (seed=42, transformers 4.40.2), example `CS-025` reached exact token-ID match at step 175 with zero UNK/truncation ⇒ the data/training path can memorize a clean single example.

### D63 — Clean five-example trainer-path overfit diagnostic (✅ — PASS)
- Five deterministic examples from the five tracks reached `5/5` exact token-ID match at step 400 via `Seq2SeqTrainer`, with a passing padding audit (`44/44` positions → `-100`).

### D64 — Sanitized full-corpus retraining (✅ EXECUTION PASS — no QUALITY PASS)
- Fresh AraT5-base, full FT, float32, single-GPU, effective batch 16, up to step 660; early stopping at epoch 55.58; best `checkpoint-617`, best `eval_loss=1.7506462336`. Reload + tied-weight check PASS.
- Smoke generations: `CS-025` (train) near-target but not exact; `CS-003` (val) distorted terms + changed claim count; `CS-013` (O9) repetition + hallucination + over-length. **No QUALITY PASS.** Checkpoint published as a private Kaggle Dataset (Version 1, 1.14 GB, 147 files), not adopted.
- Limited conclusion: D59–D64 rule out corpus sanitization, tokenization, padding, Trainer path, and save/reload as sufficient explanations. Strong indications of weak generalization and format/content degradation on val and O9, but 3 smoke cases are too few to quantify. No new hyperparameter/architecture decision before D65.

### D65 — Deterministic validation + O9 audit (✅ EXECUTION PASS / QUALITY FAIL; Q6 reopened)
- 33 val + 25 O9 evaluated deterministically with hash verification and determinism PASS. Exact match = 0 in both splits. **Median edit similarity `0.519` (val) / `0.160` (O9)**, severe repetition `42.4% / 52%`, all CONTENT/FORMAT/LENGTH/REPETITION flags fired. D64 checkpoint functionally blocked; **Q6 reopened.**

### D66 — Controlled PEFT repair pilot + Q6 re-open (✅ EXECUTION PASS / NO REPAIR CANDIDATE)
- Single-seed LoRA comparison of AraT5-base and mT5-base on train/val only, frozen D64 control, explicit repair gates, O9 excluded. AraT5 produced no qualified checkpoint; mT5 failed the quality/structure gates at step 72. **No winner, no production adoption; Q6 stays open.**

### D67 — Decomposition Training Corpus v2 repair + ASR→decomposition input-contract freeze (✅ BLOCKED AT PHASE 0 / NO CORPUS MODIFICATION)
- Phase 0 verified 222 examples / 1,836 claims / split 189-33 / 273 self-containment flags and recovered 34 structural atomicity candidates, but found no evidence identifying which four were excluded from a former informal count of 30 — so it stopped before any corpus change.

### D68 — Canonical atomicity adjudication recovery (✅ EXECUTION PASS / CANONICAL ATOMICITY SET RECOVERED)
- Two procedurally separate passes over the 34 candidates, 64/64 propositions with literal source support each pass, 30 agreements + 4 disagreements resolved + 0 unresolved. Canonical result: **24 `NON_ATOMIC_REPAIR_REQUIRED` + 10 `INTEGRATED_SINGLE_CLAIM_FALSE_POSITIVE`** (not the provisional 20/14 or former target 30). Constraint logged: both passes are from the same Codex environment, not a human inter-annotator study.

### D69 — Decomposition Training Corpus v2 target repair + self-containment adjudication + deterministic build (✅ pre-registered)
- Pre-registered build of the Decomposition Training Corpus v2 (internally referred to during D67-D69 planning as "Gold v2"; renamed in D84 to avoid confusion with the O9 and DS-014 Gold Sets — see decisions.md's naming note) under `results/gold_v2/`, keeping the 222 Egyptian source answers byte-for-byte and repairing 3 unsupported additions + 24 atomicity keys + 273 self-containment flags via a consolidated original-index repair plan — no training, no O9, no ASR augmentation, no production integration.

### D70 — Paired original/ASR-aligned corpus input variants (✅ — dataset pipeline + tokenizer smoke test pass)
- Two paired variants per question (`original`, `asr_aligned`); `example_id` = `question_id + "__original"/"__asr"`; split on `question_id` so both variants stay in the same split; a guard raises `ValueError` on any claim mismatch between variants; GN-050 excluded from both. Result: 444 examples from 222 question_ids, 378 train / 66 val, zero overlap; real AraT5-base tokenizer produced `input_ids`/`attention_mask`/`labels` for both variants; **149 tests pass.** Proves the corpus/tokenization contract only, not model quality.

### D71 — Paired-corpus AraT5 full fine-tuning (✅ EXECUTION/CHECKPOINT PASS — QUALITY NOT YET EVALUATED)
- Fresh base AraT5-base, full FT, float32, single Tesla T4, no LoRA, split 378/66, seed=42, O9 excluded, GN-050 excluded, no old checkpoint. Best `checkpoint-543`, best `eval_loss=2.205347776412964`, best epoch 22.98; early stopping at step 732 / epoch 30.98. Published as Kaggle Model `hashemili/interview-iq-d71-arat5-paired-ft`, variation `paired-corpus-full-ft`, Version 1. Execution/checkpoint success does not prove output quality.

### D72 — Deterministic quality evaluation of D71 (✅ EXECUTION/METRICS PASS — QUALITY REJECTED FOR CLAIM DECOMPOSITION USE)
- Loaded the D71 Kaggle Model only (no fallback to base). Eval on 66 val (33 original + 33 ASR) + 25 O9 held-out, deterministic (`do_sample=false`, `num_beams=1`, `max_new_tokens=320`, float32, single GPU, no training).
- **Adopted results (`v6-authoritative-gold-context-parser`):** validation LCS F1 `0.5071960304`, validation claim-count exact `0.3333`; **O9 LCS F1 `0.1892490644`**, O9 claim-count exact `0.08`, O9 mean absolute claim-count error `2.8`, O9 repetition rate `0.24`; ASR Latin recall `0.1812590984`, original Latin recall `0.3610519332`. D71 checkpoint not adopted for runtime.
- **Verdict:** `EXECUTION/METRICS PASS — QUALITY REJECTED`. Post-hoc (D72 did not pre-register numerical thresholds), so not presented as passing/failing a registered threshold.

### D73 — Exhaustive D72 prediction error analysis (⛔ PREREGISTERED / NOT EXECUTED)
- Pre-registered analysis of all 91 predictions in `d72_examples.csv` (no training/modification), classifying errors into hallucination, semantic substitution, Latin-term corruption, repetition/degeneration, under/over-decomposition, invalid numbering, original/ASR divergence, generation-length cap — with count, share of 91, and representative examples per class.
- **Addendum (21 Jul, see D74):** the ban that blocked defining a new training experiment referred to a **new AraT5 training** experiment. After D74 there is no upcoming AraT5 training (full replacement, not incremental improvement), so the ban no longer applies as written. Executing D73 itself remains **allowed and recommended as retrospective documentation** (explaining the pivot for the defense) but is now **non-blocking.**

### 3c — Pivot to runtime LLM API + sanity gate (D74–D80)

### D74 — Pivot: amend the Zero-LLM-at-Runtime constraint (Claim Decomposition only) + full replacement of AraT5 with an LLM API (✅ architectural amendment supervisor-approved — ⛔ execution not begun)
- **Old constraint (via D55 and PROJECT_EXECUTION_PLAN.md:21):** LLM allowed in offline data prep only, with mandatory human review; no LLM at runtime.
- **New constraint:** the **Claim Decomposition module only** is exempted from the runtime ban. It may call an external LLM API (e.g. via OpenRouter, free tier) as a **full replacement** for AraT5-base fine-tuning, at actual runtime.
- **Scope — explicitly limited:** affected = Claim Decomposition only. Untouched = NLI Dual-Channel Scoring (mDeBERTa-v3 + LoRA, stays local, tested, locked), BGE-M3 chunk cap, ASR. Zero-LLM-at-runtime **stays in full force** on the rest of the pipeline. Required outside this file: PROJECT_EXECUTION_PLAN.md:21 needs a matching manual edit (append "except the Claim Decomposition module — see D74 in decisions.md").
- **Registered basis:**
  1. Empirical evidence from D65–D72: severe generalization gap between validation and O9 (LCS F1 0.507→0.189; claim-count exact 33%→8%; O9 mean absolute claim-count error 2.8; Latin recall 36%→18% on the ASR-aligned variant). Two PEFT repair attempts (D66) produced no repair candidate for AraT5 or mT5.
  2. Insufficient Arabic data for reliable fine-tuning (only 189 unique question IDs, doubled to 378 via original/ASR without real knowledge diversity — documented in the D73/GPT plan critique).
  3. Explicit supervisor approval of the pivot, based on expecting higher accuracy from a general-purpose LLM in a data-scarce setting. **[Open item: the supervisor's written approval date/minute to be added here for the defense.]**
- **Effect on other decisions:** Phase 8 (AraT5 FT) ✅ CLOSED — SUPERSEDED (not worthless failure; retrospective documentation via D73 counts as documented effort in the project journey). Q6 (AraT5 vs mT5) ✅ CLOSED BY PIVOT — **explicitly does not** resolve the original question by any empirical evidence; the decision supersedes both options and must not be read as an implicit Q6 answer. D73 becomes optional retrospective documentation.
- **Mandatory prompt constraint (non-negotiable):** the LLM must not modify or "correct" the correctness of the user's answer. Allowed tasks only: (a) colloquial→simplified-MSA normalization, (b) decomposition into claims, (c) preserving English terms in Latin script without translation or correction. No information absent from the user's original answer is added.
- **Mandatory pre-integration verification (Sanity Gate — a validity condition, not a performance study):** a sample of N (5–10) answers with deliberate technical errors or clear gaps; verify the resulting claims **preserve the same error/gap** and the model does not implicitly "correct" it. If the model corrects wrong answers, the whole NLI scoring engine becomes circular and invalid (it would score a modified answer, not the user's real one) — this touches the validity of "Answer Correctness Evaluation" itself, the project's sole goal. Without this gate, no LLM output is adopted.
- **RISK ACCEPTED (D33-style):** no isolated component-level comparison (LLM decomposition vs AraT5 baseline on the same O9 sample) before integration — measurement deliberately deferred to a full-pipeline run. Limitation to document explicitly: at full-pipeline run, three unfixed variables change together (LLM decomposition quality, uncalibrated NLI thresholds [G4 not run], BGE-M3 chunk-cap behavior) — a weak final result cannot be confidently attributed to one component without a later variable-isolating experiment.
- **Open item (Fallback):** ⛔ unresolved — Ahmed must decide: caching results used in the final evaluation/demo (instead of a live call during the defense), or a second backup model on API failure/rate limit. Closed before any final demo or full-pipeline run.

### D75 — Codex-assisted AraT5 training corpus attempt (1500-target): evidence and closure (✅ CLOSED — SUPERSEDED by D74; never training-approved)
- **Process note (documented, not concealed):** this corpus attempt (`results/decomposition_corpus_v2_codex_1500/` and related scripts) was run without prior D## pre-registration and never committed to git — a pre-registration discipline violation, logged explicitly.
- **Timeline:** supervisor approval for the D74 pivot was obtained **before** this attempt. Ahmed ran it afterward as a final independent effort to see if a larger synthetic corpus could rescue AraT5, before proceeding with the already-approved pivot. It did not cause or precede the approval.
- **Evidence:** status INCOMPLETE_RESUMABLE; DRAFT_UNREVIEWED; SYNTHETIC; NOT TRAINING-APPROVED. Target 1500 records; completed 1050 (70%) across shards 1–7; shard 8 never assembled. 229 rejections; dominant reason: NON_ATOMIC_CLAIM(S) 76+43 = 119 (~52%); then NON_SELF_CONTAINED 12, MISSING_PROPOSITION 11, CASE_MISMATCH 11, UNSUPPORTED_PROPOSITION 7; remaining term_corruption_* are mostly a punctuation mark fused to a Latin token (a normalization artifact).
- **Interpretation:** the dominant failure mode was claim-atomicity — a structural/format difficulty in the decomposition task itself, not primarily semantic incompetence or Arabic incapability. Generalizes beyond AraT5/Codex.
- **Forward implication for D74:** the mandatory sanity gate should also spot-check claim atomicity on a small sample, since this is a demonstrated structural risk independent of the model.
- **Disposition:** superseded by D74; retained as archived evidence (`archive/phase8_arat5_superseded/`), not deleted.
- **Addendum — O9 integrity (21 Jul):** an uncommitted, unexplained working-tree change to `results/o9_decomposition_exercises.md` (SE-007 answer text) was found in git status. Per the O9 immutability principle (D51/D52, same standard as P48), it was **not** silently kept — the diff was preserved at `archive/phase8_arat5_superseded/o9_uncommitted_change_2026-07-21.patch` and the file reverted to HEAD via git checkout. Origin unknown (possibly Codex). Any genuine SE-007 data issue must go through a registered decision, not a silent edit.

### D76 — First end-to-end LLM decomposition call: technical success, quality not yet adopted (✅ EXECUTION PASS — ⛔ QUALITY NOT YET VALIDATED)
- **Environment:** Python rebuilt machine-wide (Python 3.14 removed due to a version conflict with `torch==2.2.2`; Python 3.11.9 kept as the sole system default, no in-project venv, by Ahmed's explicit decision). `requirements.txt` updated with `requests==2.34.2` and `python-dotenv==1.0.1` (D74 client dependencies).
- **Test:** one hand-written Egyptian-Arabic sentence for testing only (not from O9 or any project corpus — deliberately avoiding protected data before the sanity gate exists).
- **Observed:** simplified-MSA normalization sound; meaning preserved with no addition/deletion; Latin terms (D74 constraint #3) sound and positively noted — input had `هارد ديسك` (Arabic transliteration), output converted it to `hard disk` in correct Latin script. **Open note (non-decisive):** the first claim merged two ideas into one claim — a possible atomicity issue, the same dominant failure class (52%) from the D75 corpus. Single-example evidence; not generalized.
- **Model actually used:** `nvidia/nemotron-3-nano-30b-a3b:free` — **not** the intended `google/gemma-4-31b-it:free`, which returned HTTP 429 (rate-limited upstream by Google AI Studio at test time) after exhausting retries. The retry/backoff logic (D74) worked correctly: it retried, then raised a clearly-typed exception instead of a silent failure or empty result.
- **Model choice not resolved by this test.** One successful call on one model is not enough to prefer nano over Gemma; both remain candidates.
- **Direct evidence for the D74 Fallback item:** since a specific free model can be rate-limited entirely independently of the user's own usage, the proper fallback design is a **list of candidate models tried in order**, not a single fixed model. The D74 Fallback item stays OPEN but now has concrete empirical justification.
- **Required before any production adoption:** (a) run several more varied test examples (deliberately-wrong answers, more Latin terms, longer answers) across candidate models before deciding; (b) implement and run the mandatory D74 sanity gate before any O9-adjacent use or real evaluation.

### D77 — Sanity gate design pre-registration (Claim Decomposition, D74 mandatory check) (✅ registered; executed in D78–D80)
- **Environment discovery logged (not passed silently):** git status showed `src/interview_iq/decomposition_llm/` (client.py + system_prompt.md) and `.env.example` fully untracked, and a modified/unstaged `requirements.txt` — the same D75 pattern (code relied on before being registered in git). Recommendation: a small separate commit before/parallel to writing the gate — timing is Ahmed's call.
- **Call interface confirmed from actual code (no assumption):** `from interview_iq.decomposition_llm.client import decompose_via_llm, LLMDecompositionError`; `decompose_via_llm(asr_text: str) -> DecompositionResult` (`DecompositionResult` imported from the old AraT5-era `interview_iq.decomposition.types` — a shared type, not new). **Correction to an earlier understanding (D74/D76):** there is no automatic multi-model fallback in code. `OPENROUTER_MODEL` is a single value read from `.env` once. The gemma↔nemotron switch in D76 was **manual by Ahmed**, not program behavior. The D74 Fallback item has **no code implementation yet.** A formal validation layer already exists inside `client.py` (`_parse_numbered_claims` rejects any output line not in `"N. claim"` form); the gate adds a **semantic** layer above it, not a duplicate.
- **Fixtures:** a separate file outside any tracked corpus or O9. 8 cases: CS×2 / DS×2 / DA×2 / SE×1 / GN×1 (SG-01 to SG-08). Each: `case_id`, `track`, `injected_error_type`, `answer_text` (raw ASR form), `injected_error_anchor`, `latin_terms_expected`.
- **Script execution:** direct call to `decompose_via_llm` (same production path). One model per full run (explicitly logged). Per case: raw input/response, `DecompositionResult`, actual model, timestamp, retries, any error in full. Output: `results/llm_decomposition_sanity_gate/` — raw JSON + a report with three empty human-verdict columns: `error_preserved` (YES/NO), `no_unauthorized_addition` (YES/NO), `atomicity_verdict` (ATOMIC/NON_ATOMIC/AMBIGUOUS).
- **Decision rule (pre-registered):** fully human judgment — no auto-grading (to avoid circularity). **Blocking:** any case with `error_preserved=NO` or `no_unauthorized_addition=NO` ⇒ the gate FAILS entirely (zero tolerance, both equally severe). **Non-blocking:** `atomicity_verdict=NON_ATOMIC` ⇒ logged and tracked (Q8-style), does not stop adoption. The actual PASS/FAIL result is recorded later as an update to D77 or a new D##.
- **Reference:** D74 (original requirement), D75 (atomicity-check extension), D76 (first test pattern, source of the no-real-fallback note).

### D78 — Sanity gate first execution attempt: VOID (provider unavailability, not quality failure) (⛔ VOID — 0/8 outputs)
- **Non-evidentiary on `google/gemma-4-31b-it:free` decomposition quality.** The first execution (`run_20260721T100837Z`) used gemma; all 8 cases returned `"claims": null` with HTTP 429 from OpenRouter, `provider_name: "Google AI Studio"`, `is_byok: false`, "temporarily rate-limited upstream." The retry/backoff (D74) worked: exhausted retries, raised a classified exception, no silent failure.
- **Verdict:** a provider-side availability failure (shared free-tier rate limit), not a decomposition quality failure. No output to judge against the D77 criteria. Gemma's decomposition quality remains completely unknown — neither PASS nor FAIL.

### D79 — Sanity gate second execution attempt: VOID (free-tier slug deprecated) (⛔ VOID — 0/8 outputs)
- **Non-evidentiary on `meta-llama/llama-3.3-70b-instruct` decomposition quality.** The second attempt (`run_20260721T142126Z`) used `meta-llama/llama-3.3-70b-instruct:free`; all 8 cases returned HTTP 404: "This model is unavailable for free. The paid version is available now — use this slug instead: meta-llama/llama-3.3-70b-instruct."
- **Verdict:** the free-tier slug was permanently removed from OpenRouter (unlike D78's temporary rate limit). A permanent availability failure, not a quality failure. Quality remains unknown.
- **Impact on model selection:** after D78/D79, three attempts (nemotron/D76, gemma/D78, llama/D79) failed for three entirely different reasons (quality, temporary rate-limit, permanent deprecation), none producing a valid D77 judgment prior to D80.

### D80 — Sanity gate PASS on `cohere/north-mini-code:free` (✅ PASS — 8/8, adopted as OPENROUTER_MODEL)
- **Human verdict recorded by Ahmed: `error_preserved=YES` and `no_unauthorized_addition=YES` on all eight cases.** The fourth execution (`run_20260721T142708Z`) used `cohere/north-mini-code:free` (an instruct model, unrelated to any previously failed family). 8/8 execution SUCCESS. Human review (SG-01–SG-08) confirmed every deliberately-injected WRONG_FACT error was preserved without silent correction (notably SG-08, which preserved the incorrect port 80 instead of 443 across three simultaneous errors), and every INCOMPLETE case stayed incomplete without unauthorized additions (SG-04: recall entirely absent; SG-06: LEFT JOIN entirely absent).
- **Atomicity note (non-blocking, Q8-style):** SG-05 split a single Normalization sentence into two claims (mean=0 / std=1). Ahmed's verdict: **ATOMIC** — an acceptable logical split, not excessive fragmentation.
- **Decision:** `cohere/north-mini-code:free` is adopted as the current decomposition model for `OPENROUTER_MODEL`. D74's mandatory sanity gate is now **empirically satisfied** — the first actual PASS on the full chain (client.py → OpenRouter → DecompositionResult → human judgment matching D77 criteria).

### D81 — English migration + reorganization of the decision log (✅ — 21 July 2026)
- **Decision:** the entire decision log (D1–D80) was translated from Arabic to English and reorganized into clearer thematic sections (governance snapshot; NLI module; decomposition module split into O9/Q6, AraT5 attempt, and pivot/sanity-gate; open items; methodology). Motivation: (1) consistency with the English-only convention for Claude-Code-authored content (avoids cmd.exe RTL/mojibake corruption); (2) the file had grown large and hard to navigate.
- **Faithfulness constraints applied during translation:** all numerical values, checkpoint names, commit hashes, thresholds, and model IDs carried over verbatim. Verbose procedural pre-registrations for the superseded AraT5 sub-phase (D58–D73) were condensed to their outcomes; no decision was dropped, and every D## retains its number, status, and essence.
- **Archival:** the pre-D81 Arabic original is preserved (not overwritten silently) at `archive/decisions_arabic_pre_D81_2026-07-21.md`, per the project principle that corrections are documented rather than silently overwritten. This entry is that documentation.
- **Not in scope:** this migration changes presentation only; it makes no architectural or empirical change to any decision D1–D80.

### D82 — Coverage Channel Real-Claims Experiment: Pre-Registration (⛔ PREREGISTERED / NOT EXECUTED)

**Goal:** the first actual measurement of the Coverage channel on real claims (deferred since D44, unblocked now that a decomposition module exists and passed its sanity gate — D80).

**Source:** the 25 O9 raw answers (`results/o9_decomposition_exercises.md`, D51), 5 per track.

**Procedure:**
1. For each of the 25 questions, run the raw answer through `decompose_via_llm` (same production path, single model logged explicitly per run — `cohere/north-mini-code:free`).
2. Compare the resulting claims against the question's official `key_points` field (from `reference_docs_250_FINAL_v1.json`) — **not** the O9 manual reference claims, to avoid D44's "measures data consistency with itself" problem.
3. Run the existing Phase 6 Coverage channel (NLI engine + aggregation + metrics) on the Claims × key_points matrix for each question.
4. Log per question: generated claims, per-key-point max entailment probability, final Coverage score, and key_point count (2/3/4+).

**Analytical targets (map directly to the D42 fragility hypotheses):**
- (a) OOD: does Coverage score correlate with key_point count, as in the D42 table?
- (b) learned-neutral shift: any unexpected `neutral` calls between a claim and a key point that should plausibly relate?
- (c) composition error: any key point requiring two claims jointly, uncovered by any single claim?

**Pre-registered constraints:**
- n=25 ⇒ directional judgment, not statistical. Does not prove the channel is sound, only gives the first real reading.
- Compound, not isolated (RISK-ACCEPTED style, per D74): decomposition quality itself is still unmeasured in isolation (D74), and thresholds remain PRE-CALIBRATION DEFAULT (G4 not yet run). A weak number here cannot be confidently attributed to one component.
- Read-only diagnostic: does not modify O9, key_points, or any production code.
- Execution environment: Kaggle T4 thin-runner (standing environment decision as of 21 Jul 2026 — all test/experiment execution moves to Kaggle notebooks, not local cmd.exe, going forward for all future work, not just this experiment).

**Addendum — two-arm protocol (added before execution, same registration):** the decomposition step (`cohere/north-mini-code:free`) runs once per O9 answer. The resulting claims are then run through **both** NLI arms — zero-shot base model and the fine-tuned adapter (`iq-checkpoints-nli-v1`) — same code path, matching the D40/D46/D49 convention of comparing both arms. Coverage scores are logged separately per arm, not merged. This directly tests D42-b/D46-C's prediction (the adapter's Coverage may be worse than zero-shot's due to the learned-neutral shift from HARD_POS twins) on real claims for the first time — previously only tested claim-free in D46/D49.

---

### D84 — Gold Naming Disambiguation (✅ documentation-only, no code or data changes)

**Decision:** the decomposition training corpus specified in D67-D69 (target: `results/gold_v2/`, never executed) is renamed in this file's prose from "Gold Corpus v2" to "Decomposition Training Corpus v2", to resolve the naming collision flagged as an open item (three artifacts previously all called "Gold": the O9 validation set, the DS-014 NLI Gold Set, and this training corpus).

**Scope — documentation only:**
- Changed: D67 and D69 headings/body text, the "Gold naming" open-item row, and one changelog line, all in this file (`decisions.md`).
- Not changed: the archived pre-D81 Arabic original (`archive/decisions_arabic_pre_D81_2026-07-21.md`), the already-executed D68 result artifacts (`results/d68_atomicity/d68_atomicity_candidates.md`, `results/d68_atomicity/d68_atomicity_adjudication.json`), the archived source script that produced them (`archive/phase8_arat5_superseded/scripts/d68_atomicity_run.py`), and the literal target path `results/gold_v2/` named in D69's body (D69 was never executed, so this path does not exist on disk and is preserved verbatim as what D69 actually specified).
- Rationale for the narrow scope: archived snapshots and already-executed result artifacts are historical record: renaming them would misrepresent what was actually planned/produced at the time, contrary to this project's principle that corrections are documented rather than silently overwritten (see D81's own precedent).

The two other "Gold"-named artifacts (O9 validation set, DS-014 NLI Gold Set) are unaffected and keep their existing names.

---

### D85 — ASR Module (Phase 7) + End-to-End Pipeline Orchestrator (✅ EXECUTION PASS on offline tests / ⛔ NOT YET RUN ON REAL AUDIO)

**Scope:** implements Phase 7 (ASR module: audio extraction + VAD gating + faster-whisper transcription, producing Format Spec v1.1 exactly per configs/asr.yaml) and a new end-to-end orchestrator (pipeline.py's evaluate_answer), requested for local integration by the project's fusion-module team member.

**Files:** src/interview_iq/audio/segmentation.py (extract_audio, run_vad — Silero VAD, lazy/injectable), src/interview_iq/asr/engine.py (transcribe_audio, field order read live from configs/asr.yaml), src/interview_iq/cli/run_asr.py (thin CLI), src/interview_iq/pipeline.py (new — evaluate_answer, wiring ASR → decomposition → chunk cap → NLI Precision/Coverage → compute_scoring_result, reusing every existing function unmodified, same injection convention as evaluation/gold_eval.py and scripts/coverage_channel_real_claims_experiment.py).

**Tests:** 24 new offline tests (zero network, zero real models — faster-whisper and Silero VAD both mocked via injectable backend protocols), full suite 174/174 passing.

**Two judgment calls made under ambiguity, both explicit in code docstrings, neither silently assumed:**
1. Transcript normalization is an honest no-op in this version (normalized_transcript == raw_transcript, empty log) — normalization is the Claim Decomposition module's registered responsibility per D74, not this module's.
2. `pre_answer_latency_sec` (undefined beyond its name in configs/asr.yaml / PROJECT_EXECUTION_PLAN.md) is interpreted as "seconds from this answer-segment's audio start to the first VAD-detected speech onset." Confirmed by Ahmed: retained in the output for potential use by the fusion module, but explicitly NOT used in any scoring computation in this codebase (consistent with the Linguistic Confidence Module being out of this project's scope per the 7 Jul 2026 supervisor directive).

**GPU/CPU note:** configs/asr.yaml's registered production baseline stays CPU/int8 (unchanged by this work). transcribe_audio's device_override/compute_type_override parameters allow GPU execution on Kaggle for experimentation only, without modifying the config file.

**Status:** code complete and offline-test-verified. Not yet run against real audio/video — first real-audio run is the next step (Kaggle, per the standing execution-environment decision), needed to close G3 and to empirically verify the FasterWhisperBackend/SileroVad code paths against the real libraries (per §5.13 — "documentation says X" is not "I ran it").

---

### D86 — Groq Fallback Provider for Claim Decomposition (⛔ PREREGISTERED / NOT EXECUTED)

**Goal:** resolve the long-open "D74 Fallback" item by adding a second, independent LLM API provider (Groq) that the decomposition client automatically falls back to when the primary provider (OpenRouter) returns HTTP 429, without requiring manual `.env` edits between runs.

**Trigger scope (narrow, deliberate):** fallback activates ONLY on OpenRouter HTTP 429 (rate limit exceeded). Any other OpenRouter failure (4xx auth errors, 5xx, malformed response, null content per D82 Issue 1's fix) is NOT retried against Groq — those are real errors that a different provider wouldn't fix, and conflating them would hide genuine bugs behind a provider switch.

**Candidate model:** `llama-3.1-8b-instant` on Groq — chosen for its far larger daily free-tier ceiling (14,400 req/day vs. ~1,000 for larger Groq models) and because it is an instruct model, not a reasoning model (avoiding the D76 nemotron CoT-leak failure mode by construction, same logic as the OpenRouter candidate selection in D78-D80).

**Mandatory gate before production use (same standard as D77, applied independently to this new model):** the Groq candidate must pass its own run of the D77 sanity gate (8 fixtures, human judgment on error_preserved/no_unauthorized_addition/atomicity_verdict) before being trusted as a fallback. A model that has never been quality-checked must not silently receive real decomposition traffic just because the primary provider is rate-limited.

**Transparency requirement:** any downstream consumer of decomposition output (pipeline.py's `models_used`, the sanity-gate script, the Coverage experiment script) must be able to tell which provider and model actually served a given call — never silently reported as "OPENROUTER_MODEL" when Groq actually served the request.

**Explicitly out of scope for this decision:** load-balancing or round-robin across multiple accounts on the same provider (considered and rejected as a separate, ethically distinct proposal on 22 Jul 2026 — risks account suspension across multiple people's accounts for marginal gain, per OpenRouter's own Terms of Service prohibiting "repeatedly creating accounts... to bypass rate limits"). This decision is strictly about adding one additional, independently-paid-for-by-nobody, legitimately-free second provider.

**Amendment (22 Jul 2026, before any code was written):** Ahmed decided to replace this fallback design with a full provider switch instead: Groq becomes the sole decomposition provider, and all OpenRouter-specific code is deleted from client.py (not kept dormant). Rationale given: simplicity over dual-provider complexity. This supersedes the "fallback" framing above — everything else in this decision (candidate model, mandatory D77-style sanity gate before production use, transparency requirement) still applies unchanged, now to Groq as the sole provider rather than as a fallback. Consequence: D80's sanity-gate PASS (for `cohere/north-mini-code:free` on OpenRouter) no longer covers the model actually in use — it is historical record for that now-retired provider/model pair, not evidence for Groq. A fresh sanity-gate run on Groq's `llama-3.1-8b-instant` is required (see D87) before this is trusted for any real O9/Coverage/pipeline work.

---

### D87 — Sanity Gate Result on Groq (`llama-3.3-70b-versatile`): PASS (✅ PASS — 8/8, adopted as GROQ_MODEL)

**Context:** per D86's amendment, Groq became the sole decomposition provider with all OpenRouter code removed. Two Groq candidates were run through the D77 sanity gate before either was trusted for production use.

**First attempt — `llama-3.1-8b-instant` (⛔ NOT ADOPTED, quality concerns, not a hard FAIL but not clean enough to trust):** 8/8 execution SUCCESS (`run_20260722T111921Z`). Human review found two issues: (1) SG-01 produced a claim not present in the input ("new items are added to the end of the list" — a FIFO/queue-like behavior not stated anywhere in the LIFO-describing input), a plausible `no_unauthorized_addition=NO`; (2) SG-07 exhibited literal text corruption — Cyrillic characters intermixed into an Arabic word ("للконфликтс"), a generation-quality defect independent of the pass/fail criteria. Given the ambiguity on SG-01 and the corruption on SG-07, Ahmed chose not to adopt this candidate rather than force a borderline PASS.

**Second attempt — `llama-3.3-70b-versatile` (✅ ADOPTED):** 8/8 execution SUCCESS (`run_20260722T112503Z`). Human review by Ahmed: `error_preserved=YES` and `no_unauthorized_addition=YES` on all eight cases, no text corruption, no fabricated claims. Notably, this larger model resolved both defects seen in the 8B candidate: SG-01's claims matched the input exactly (no fabricated addition), and SG-07 preserved "أسرع" (part of the injected HTTP/HTTPS speed error) and both other injected errors (port 80, no-encryption claim) with no corruption. All three deliberately-injected errors in SG-08 (speed-not-encryption framing, port 80, no additional encryption) were preserved without correction or softening.

**Atomicity:** all eight cases judged reasonably ATOMIC by Ahmed (no excessive fragmentation, no improper merging).

**Decision:** `llama-3.3-70b-versatile` (Groq) is adopted as the current decomposition model for `GROQ_MODEL`. D74's mandatory sanity gate requirement is empirically satisfied for the current sole provider. Groq's free tier for this model: 1,000 requests/day (per D86's cited figures) — ample headroom for O9-scale experiments (25 questions), repeated sanity-gate reruns, and supervisor demo sessions.

**Supersession note:** this supersedes D80 for current production use (D80's PASS was for `cohere/north-mini-code:free` on OpenRouter, a provider/model pair no longer in the codebase per D86). D80 remains accurate historical record of what was true on that date, per this project's standing principle that corrections are documented rather than silently overwritten.

---

## D88 — First real end-to-end run: three verified failure modes (2026-07-23)

**Context:** First real `evaluate_answer()` runs (SE-028 correct answer, GN-040 deliberately-wrong answer) produced inverted scores: SE-028 = -12.02, GN-040 = +4.57. A pre-registered two-arm diagnostic (frozen claims, full Precision matrices, zero-shot vs adapter, production functions reused unmodified) isolated three causes:

**F1 — LLM constraint-8 violation (GN-040):** transcript said "16 bits per Byte" (deliberate error); the decomposition claim said "8 bits, not 16" — the LLM corrected the candidate's factual error, violating system_prompt.md constraint 8. The D77 sanity gate (8/8 PASS, D87) did not catch this error type (numeric fact inside otherwise-correct sentence). Gate fixture coverage is therefore incomplete.

**F2 — Adapter degrades Precision channel on real claims (SE-028):** near-verbatim claim↔chunk pairs: zero-shot E=0.985/0.786 collapsed to 0.191/0.041 under the adapter. Derived Precision (v2 rule, pre-calibration thresholds): zero-shot +0.501 vs adapter -0.120. Extends D82/D83's Coverage finding into the Precision channel; consistent with D42-b (HARD_POS-induced drift). Directional, n=1 question.

**F3 — Base-model failures independent of the adapter:** claim0↔SE028-C01 (near-verbatim, both arms E≤0.232), claim4↔SE028-C05 (refactor claim vs refactor chunk, both arms C≥0.97), GN-040 claim2↔GN040-C02 ("8 bits" vs "8 bits", both arms N≈0.99). Zero-shot's +0.501 also includes one false-entailment VERIFIED (claim4↔C04, E=0.908 against the wrong chunk).

**Evidence:** results/pipeline_demo/{SE-028.json, GN-040.json, precision_matrix_two_arms.json}; diagnostic script committed as scripts/diag_precision_two_arms.py.

**Consequences (registered, resolution deferred to a dedicated decision):**
- Adapter role in the runtime path is now an open question for BOTH channels (supersedes open item "D82/D83 consequences" — merged here).
- D77 gate needs a numeric-fact-preservation fixture class before any further reliance on it.
- No calibration (G4) may proceed on top of an unresolved NLI-arm choice.

---

## D89 — Runtime NLI arm: zero-shot for both channels; adapter demoted to documented negative result (2026-07-23)

**Decision:** Effective immediately, the runtime default NLI arm for BOTH channels (Precision and Coverage) is the zero-shot base model (MoritzLaurer/mDeBERTa-v3-base-mnli-xnli, no adapter). The fine-tuned LoRA adapter (checkpoint27, D41) is removed from the runtime path and reclassified as a documented negative result / ablation for the dissertation.

**Basis (accumulated, all pre-registered measurements):**
- D82/D83: adapter worse than zero-shot on Coverage in 19/19 successful cases (mean 0.180 vs 0.395).
- D88-F2: adapter collapses Precision-channel entailment on real LLM-decomposed claims (near-verbatim pairs 0.985→0.191, 0.786→0.041); derived Precision zero-shot +0.501 vs adapter -0.120 (directional, n=1 question).
- Diagnosis: distribution mismatch — the adapter was trained on synthetic pairs and does not generalize to real pipeline-decomposed claims (consistent with D42-b HARD_POS-induced drift).

**Known cost (registered, not hidden):** the adapter's subject-blindness fix (Gold Set 48/48, Phase 5) and its demonstrated contradiction-detection advantage (bridge demo: wrong Stack answer scored -44.73 by adapter vs +4.08 by zero-shot) are given up at runtime. This is a documented limitation of the zero-shot default, an input to threshold calibration (G4), and a discussion point for the supervisor at the next demo.

**Reopening condition (binding):** this decision is reopenable if and only if a pre-registered experiment produces an adapter that outperforms zero-shot on BOTH channels, evaluated on the D88 diagnostic set plus an O9 sample, with acceptance criteria written and committed BEFORE the training run. The first such experiment (retraining on structurally-labeled pairs generated from real pipeline decompositions) is planned and will be registered as its own decision; it is gated on the F1 fix (D88 consequence: the generating LLM must first pass an extended sanity gate including a numeric-fact-preservation fixture) because corpus generation depends on the same model.

**Consequences:**
- Any runtime default, demo, or fusion-teammate deliverable produced from this point uses the zero-shot arm.
- In Section 4 (Open Items): mark the "D82/D83 consequences" item as RESOLVED by D88+D89, and add two new open items: (a) "F1 fix: strengthen system_prompt.md constraint 8 + add SG-09 numeric-fact fixture + re-run D77 gate at 9/9" and (b) "Fine-tuning repair experiment (structural-label corpus): register acceptance criteria, generate, train, evaluate vs zero-shot — gated on (a)".

---

## D90 — Numeric-fact-preservation fix: prompt hardening + SG-09 gate fixture (2026-07-23) (✅ EXECUTED — D92)

**Trigger:** D88 F1 — the decomposition LLM corrected a deliberately wrong numeric fact ("16 bits per Byte" → claim stated "8 bits"), violating the error-preservation constraint in system_prompt.md. The D77 gate (8 fixtures) did not cover this error class: a wrong numeric value embedded in an otherwise-correct sentence.

**Pre-registered actions (before any rerun):**
1. Harden the error-preservation constraint in system_prompt.md with an explicit numeric rule: numbers must be reproduced exactly as spoken, even when factually wrong; substituting the correct value is prohibited. One illustrative example added. The wording is generic — it must NOT reference the GN-040 bit/byte case.
2. Add fixture SG-09 (new class: NUMERIC_FACT): Egyptian-colloquial ASR-style transcript containing a numeric error different from GN-040's case, inside an otherwise broadly correct answer. Deliberate difference is an anti-overfitting measure: the gate must test generalization of the constraint, not memorization of the observed failure.
3. Gate pass rule updated: 9/9 fixtures; zero tolerance on error_preserved and no_unauthorized_addition unchanged; atomicity violations remain non-blocking.

**Acceptance:** Gate rerun on Groq llama-3.3-70b-versatile via Kaggle thin-runner. Any error_preserved=NO or no_unauthorized_addition=NO on ANY of the 9 fixtures (including the original 8) ⇒ gate FAIL. Human judgment by Ahmed as in D80/D87.

**Out of scope:** GN-040 real-audio revalidation (separate session, open item #1); NLI-arm consequences (already resolved in D89); fine-tuning experiment (pre-registration pending, blocked on this gate passing).

---

## D90-correction — D88 constraint numbering fix (2026-07-23)

D88's text ("violating system_prompt.md constraint 8") mis-identified the violated rule. Verified by direct read of system_prompt.md during D90 execution: constraint 8 is the Arabic-output rule; the error-preservation rule that GN-040 actually violated is constraint 1. D88's prose is left unmodified as historical record; this entry is the authoritative correction.

---

## D91 — Sanity-gate Kaggle thin-runner notebook: missing infrastructure (2026-07-23)

**Trigger:** D90's acceptance criterion assumed an existing Kaggle runner for the sanity gate. Verification found none exists in kaggle/runners/ or the archived Phase-8 directory. Per repo evidence, D77/D78/D79/D80/D87 were all invoked locally (`python scripts/llm_decomposition_sanity_gate.py`, local .env). This is inconsistent with the Kaggle-only experiment-execution policy (D82, 2026-07-21) for D87 (2026-07-22); no evidence confirms D87's actual execution environment.

**Action (pre-registered):** build kaggle/runners/run-sanity-gate.ipynb following the exact structural pattern of the four existing runner notebooks (fresh clone → pip install → CLI invocation of scripts/llm_decomposition_sanity_gate.py; zero logic in notebook cells). GROQ_API_KEY supplied via Kaggle Secrets (not .env — inaccessible on Kaggle). Output downloaded and reviewed locally per the D80/D87 human-judgment protocol.

**Non-blocking retrospective note:** D87's execution environment (Kaggle vs. local) cannot be confirmed from repo evidence. Logged as a gap; D87 remains closed/PASSED and is not re-litigated. Separately: the token-scrubbing safety practice in this notebook's Cell 1 traces to a real prior incident (GitHub PAT leaked in a Kaggle traceback, ~2026-07-21) that was acted on at the time but was never given its own decisions.md entry — flagged here as a documentation gap, not a new decision.

**Scope:** infrastructure required to execute D90's already-approved acceptance criterion — not a new phase.

---

## D92 — Sanity gate rerun: 9/9 PASS (2026-07-23)

**Context:** Following D90 (numeric-fact-preservation constraint hardening + SG-09 fixture) and D91 (Kaggle thin-runner notebook build + syntax fix), the D77 sanity gate was rerun on Kaggle. Run metadata: git_commit 29318ddd8da9000f42eb8edb0df6fc7bed02982f, model llama-3.3-70b-versatile, timestamp 2026-07-23T09:51:53Z. All 9 fixtures executed successfully (n_success=9, n_error=0).

**Human judgment (Ahmed, per D80/D87 protocol):** error_preserved=YES and no_unauthorized_addition=YES on all 9 cases (SG-01 through SG-09) — zero tolerance criteria met in full. atomicity_verdict: ATOMIC on 7/9 (SG-01,02,03,04,05,07,09); AMBIGUOUS on 2/9 (SG-06, SG-08) — non-blocking per D77's atomicity handling, logged/tracked as open items, not gate failures.

**Result: GATE PASS (9/9).** This closes D90's acceptance criterion. The numeric-fact-preservation fix is verified as generalizing beyond the originally observed GN-040 bit/byte case (SG-09 uses a distinct decimal-threshold statistical error and was preserved correctly), and SG-08's pre-existing embedded port-number error was independently re-confirmed preserved under the hardened constraint.

**Consequences:**
- D90 and D91 both close as fully executed (were previously tagged PREREGISTERED/NOT EXECUTED).
- GN-040 real-audio revalidation (open item, from D88) may now proceed — the prompt-level fix is gate-verified before the field retest.
- SG-06/SG-08 atomicity AMBIGUOUS status tracked as a non-blocking open item, not required to resolve before proceeding.
- Fine-tuning repair experiment (D89-b) remains blocked on its own separate pre-registration (acceptance criteria), independent of this gate result.

**Evidence:** results/llm_decomposition_sanity_gate/run_20260723T095153Z/{raw_results.json, report.md, report.csv}.

---

## D93 — F1-fix field validation: rerun evaluate_answer() zero-shot on real pilot audio (2026-07-23)

**Trigger:** D92 gate PASS (9/9) verified the hardened error-preservation constraint on synthetic fixtures. Field validation on the real D88 audio is still required.

**Investigation findings (basis for this decision):**
- evaluate_answer() already supports zero-shot natively (adapter_path defaults to None, guarded correctly). No pipeline-logic change required.
- scripts/run_pipeline_demo.py's argparse forced --adapter-path required=True (line 79) — a CLI-layer bug inconsistent with D89. Fix follows the existing, already-correct pattern in cli/run_scoring.py (optional --adapter-path, default=None, gated). Zero reimplementation.
- No notebook in kaggle/runners/ referenced run_pipeline_demo.py — built this session (D91 pattern).

**F3 status — explicitly unresolved, not closed by this decision:**
D88's F3 (zero-shot's positive SE-028 score partly explained by entailment VERIFIED against the wrong chunk, E=0.908) was never addressed in D89–D92. This session's C2 criterion below is necessary but NOT sufficient evidence of correct reasoning. F3 remains an open follow-up item, out of scope for this session.

**D89-b status update:** D92's gate PASS satisfies the D89-a gate; the fine-tuning repair experiment (D89-b: adapter retraining on structurally-labeled pairs from real pipeline decompositions) is now UNGATED. It will be registered as its own pre-registered decision in a dedicated session. This session's rerun additionally serves as the first field evidence that the fixed prompt is a sound corpus source for D89-b.

**Pre-registered procedure:**
1. Fix run_pipeline_demo.py: --adapter-path → optional, default=None (cli/run_scoring.py pattern). No adapter passed this run (D89: zero-shot is the runtime arm).
2. Build kaggle/runners/run-pipeline-demo.ipynb (thin CLI cells; ast.parse() + nbformat.validate() verified before approval).
3. Rerun on D88's two audio inputs (SE-028, GN-040), Groq llama-3.3-70b-versatile, PRE-CALIBRATION DEFAULT thresholds (τ_E=0.9, τ=0.5, α=0, k=10).

**Pre-registered success criteria (directional, n=2, not statistical):**
- C1 (F1 check, human judgment): GN-040 claims preserve "16" (not corrected to "8"). FAIL if corrected.
- C2 (direction): score(SE-028) > score(GN-040). Passing C2 validates F1's fix only — it does NOT resolve or supersede F3.
- C3 (soft, reported not gating): sign consistency under pre-calibration thresholds.

**Evidence:** results/pipeline_demo/{SE-028_v2.json, GN-040_v2.json}; kaggle/runners/run-pipeline-demo.ipynb committed. D88 originals retained.

---

## D94 — D93 outcome: C1 FAIL (new violation class), C2 PASS-fragile, F3 field-confirmed (2026-07-23)

**Run:** kaggle/runners/run-pipeline-demo.ipynb, zero-shot NLI (D89), Groq llama-3.3-70b-versatile, pre-calibration thresholds. Evidence: results/pipeline_demo/{SE-028_v2.json, GN-040_v2.json}.

**C1 — FAIL (human ruling by Ahmed):** GN-040 claim 3 reads "الـ Byte يتكون من 8 بت، وليس 16 بت كما ذكر، ولكن في النص الأصلي ذكر 16 بيت" — an editorialized correction embedded in the claim plus meta-commentary about the source text. This is a NEW violation class distinct from D88's silent correction: error preservation failed AND unauthorized addition occurred. The D92 gate (9/9 PASS on synthetic fixtures) did not predict this: no fixture contains real ASR transliteration ambiguity ("بت"/"بايت" both rendered near-identically as "بيت" in the transcript), which is the suspected trigger — the model was forced to disambiguate and injected its knowledge.

**C2 — PASS, numerically (50.83 > 3.28) but mechanistically fragile:** the direction is carried entirely by Coverage (0.516 vs 0.017). Precision is INVERTED: wrong answer 0.8 vs correct answer 0.501, because (a) the poisoned GN-040 claim scored NEUTRAL (max_e=0.002), never penalized, and (b) SE-028 claim 0 ("تكتب التست الأول قبل كتابة الكود" — the essence of TDD) was judged CONTRADICTED with max_c=0.994 against the reference: a stark false contradiction. (b) is direct field confirmation of F3 (base-model failure, adapter-independent, registered open in D93).

**C3 — soft:** both scores positive; GN-040 near zero (3.28).

**Additional field observations (registered, not criteria):**
- O-a Transliteration under-application: SE-028 shows zero Latin-script conversions (TDD itself absent from all claims; "التست"/"الكود" kept in Arabic); GN-040 is internally inconsistent (claims 0–1 keep "البيت" Arabic, claims 2–4 convert to "الـ Byte"). The constraint is applied stochastically on real audio.
- O-b Fabricated naming: SE-028 claim 2 names the cycle "دورة التطوير" — the speaker never named the cycle in the transcript ("اسمها يعني" then trailed off). Unauthorized addition of a different class (invented labels, not numeric facts).
- O-c asr_device resolved to "cpu"/int8 on a T4 Kaggle session — config review pending, correctness unaffected.

**Consequences (resolution deferred to a dedicated session — none executed today):**
- New open item: gate fixture class with REAL ASR ambiguity (بت/بايت-style near-homograph transliteration), plus fixtures probing invented labels (O-b) and transliteration consistency (O-a).
- Prompt hardening v2 candidate: forbid meta-commentary/editorial corrections inside claims; strengthen transliteration constraint.
- F3 follow-up remains open (D93), now with a concrete field case: SE028 claim 0 vs SE028-C01, max_c=0.994.
- G4 calibration remains blocked until the above are resolved (extends D88's consequence).

---

## D95 — Prompt hardening v2 + gate fixtures v2 (pre-registered) (2026-07-23)

**Trigger:** D94 registered three LLM-behavior failures on real audio that the D92 gate (9 synthetic fixtures) structurally could not catch: (C1) editorialized correction with meta-commentary, (O-a) stochastic transliteration, (O-b) invented labels. Root pattern: no fixture contained real ASR phenomena (near-homographs, spelled-out acronyms, unnamed references).

**Decision:** Harden system_prompt.md (v2) and extend the D77 sanity gate with four new fixture classes, built and evaluated together — the new fixtures are the acceptance test of the new constraints.

**Prompt v2 changes (registered before implementation):**
- P1 Claim-purity: a claim reports what the candidate asserted, verbatim in substance. Corrections, comparisons to the true value, and any meta-commentary about the transcript are forbidden inside claims — even when the candidate is factually wrong.
- P2 Transliteration (mandatory, with inline examples): English technical terms written in Arabic letters MUST appear in Latin script in claims (التست→test, الكود→code, داتا بيز→database, الخوارزم→algorithm).
- P3 Spelled-out acronyms: letter-by-letter sequences map to the acronym (تي دي دي→TDD, اس كيو ال→SQL, ايه بي اي→API).
- P4 Near-homographs: when one surface form could denote multiple terms (بيت→bit/byte), transliterate per local context but NEVER alter any asserted quantity or add disambiguation commentary; asserted numbers are copied exactly.
- P5 No invented labels: if the speaker does not name a thing, the claim must not assign it a name.

**Fixtures v2 (added to the D77 gate, same format as SG-01..09, Egyptian-Arabic ASR-style transcripts):**
- SG-10 (clear-terms transliteration + injected WRONG_FACT): transcript rich in unambiguous Arabic-letter tech terms (التست, الكود, الداتا بيز) with one deliberate factual error. Checks: all clear terms transliterated; error preserved verbatim; no additions.
- SG-11 (near-homograph, GN-040 replica class): transcript uses "بيت" for both bit and byte plus a deliberate numeric error (e.g., 16 bits per Byte). Checks: number preserved exactly; no editorial/meta text in any claim; no correction.
- SG-12 (spelled-out acronym): transcript spells an acronym in letters (تي دي دي) and never uses Latin script. Checks: acronym appears as TDD in claims; not dropped, not left as letter-names.
- SG-13 (unnamed reference): speaker describes a cycle/process, starts to name it ("اسمها يعني...") and trails off without naming it. Checks: no claim assigns any name; content otherwise decomposed normally.

**Pre-registered gate criteria for the rerun (Kaggle, next step):**
- All 13 fixtures: error_preserved and no_unauthorized_addition remain zero-tolerance (any NO ⇒ full gate FAIL).
- SG-10..13 add a transliteration_correct human check: gating for SG-10..13 only (SG-01..09 keep their original criteria unchanged — no retroactive rule change).
- Atomicity remains tracked, non-gating (unchanged from D77).
- Judgment remains fully human (Ahmed), on file-uploaded outputs.

**Explicit scope limits:** P1–P5 target the decomposition LLM only. F3 (NLI false contradiction, D93/D94) is untouched by this decision and remains open. D89-b remains gated on this decision closing successfully (corpus must be generated with prompt v2).

**Evidence when executed:** gate outputs under results/sanity_gate/ (v2 run), decisions.md outcome entry (D96).

---

## D96 — D95 gate v2 outcome: FAIL — new silent-correction class + transliteration constraint ineffective (2026-07-23)

**Run:** Kaggle sanity-gate thin-runner, commit 94597fe7a2d0dfa4ceed462a9464bd2d96979c9e (post-D95), Groq llama-3.3-70b-versatile, 13/13 executed, 0 API errors. Evidence: results/llm_decomposition_sanity_gate/run_20260723T144150Z/raw_results.json. Human judgment: Ahmed, on the full uploaded output.

**VOID run recorded (non-evidentiary, D78/D79 precedent):** first attempt run_20260723T143137Z executed on commit f1e3f49 (pre-D95: old prompt, 9 fixtures) because the D95 push had not yet reached origin. Detected by the pre-download commit/n_cases check; no judgment was performed on it.

**Verdicts (human):**
- SG-01..09: error_preserved=YES, no_unauthorized_addition=YES for all nine (original criteria; unchanged behavior from D92).
- SG-10: error_preserved=NO — the injected inverted TDD order ("code first, then test") was silently reversed to the correct definition ("test before code") in claim 1. This is a THIRD silent-correction class: ordering/logical facts, after numeric facts (D88-F1) and editorialized corrections (D94-C1). Each targeted hardening closed its seen class and the model leaked through the next unseen one. transliteration_correct=NO (التست/الكود/الداتا بيز all left in Arabic despite prompt-v2 inline examples naming these exact words).
- SG-11: error_preserved=YES, no_unauthorized_addition=YES — the 16-bit error and the speaker's own "not 8" comparison were carried verbatim with zero model commentary: the exact D94-C1 double-failure pattern did NOT recur (P1 effective). transliteration_correct=NO ("بيت" left in Arabic in all occurrences; no bit/byte resolution attempted).
- SG-12: no_unauthorized_addition=YES on content; transliteration_correct=NO — hybrid output "التي دي دي (TDD)": the acronym appeared but the letter-name spelling was retained alongside a parenthetical gloss, violating the pre-registered "as a whole, not separate letters" criterion; ruling YES would be post-hoc criterion softening. error_preserved=N/A (per D95 designation).
- SG-13: no_unauthorized_addition=YES — five descriptive claims, no invented name for the trailed-off cycle: D94 O-b did NOT recur (P5 effective). transliteration_correct=NO (الكود/التست left in Arabic). error_preserved=N/A (per D95 designation).

**Gate verdict: FAIL** — SG-10 error_preserved=NO triggers zero-tolerance; independently, transliteration_correct=0/4 on the gating cases.

**Diagnosis registered:**
- P1 (claim purity) and P5 (no invented labels) are field-effective: both D94 failure classes were reproduced in fixtures and did not recur.
- The transliteration constraint (P2/P3) is behaviorally ineffective in this model regardless of prompt strength: two successive hardenings, including inline examples of the exact failing words, produced no change (the model transliterates only what is already Latin in the input; SG-01..09 show the same pattern non-gatingly). Conclusion: transliteration is a deterministic mapping task and is a candidate for removal from the LLM entirely (post-processing glossary; closed-domain 250-question vocabulary makes this tractable). Near-homographs (بيت→bit/byte) remain the hard residual for that design.
- Error preservation fails by category, not by instance: numeric (D88) → editorial (D94) → ordering (D96). Remedy must be a generalized anti-knowledge-injection constraint, not another per-class patch; if a generalized constraint also fails the gate, model replacement re-enters via this same gate (D77–D87 precedent).

**Consequences:**
- D89-b remains HARD-GATED on a future full gate PASS (unchanged; corpus generation with a failing prompt is prohibited).
- Next session opens with D97: (a) deterministic transliteration post-processing layer design + (b) generalized preservation constraint (prompt v3) + gate rerun. Neither is executed under D96.
- Known infra issue (non-blocking, fix alongside D97): the sanity-gate notebook's verification cell hard-codes n_cases != 9 and raised a spurious RuntimeError on the valid 13-case run; it must read the expected count dynamically from sg_cases.json. The raw_results.json write completes before that cell and was unaffected.
- Documentation correction (old value named per convention): D95's evidence line reads "results/sanity_gate/"; the script's actual output root is "results/llm_decomposition_sanity_gate/". The actual path governs; D95's text stands corrected by this entry.

---

## Section 4 — Open Items

| Item | Description | Status |
|---|---|---|
| **Q1** | Decision numbering unified — the unified log D1–D80 is this file. | ✅ |
| **Q4** | Missing stage2_verdict — a documentation gap, not a methodological one. | ✅ |
| **Q5 → D35** | Accepting the 5-word overlap violation. Ratified and numerically corrected. | ✅ |
| **Q6** | AraT5 vs mT5 — CLOSED BY PIVOT (D74). Not resolved on empirical merit; superseded. | ✅ |
| **Q9** | GitHub repo — https://github.com/HashemIlI/interview-iq (private). | ✅ |
| **V1** | Checkpoint integrity (`classifier.*` keys, 50 tensors). D38. | ✅ |
| **V2** | Raw probabilities + reproducibility — PASSED (48/48). Inference deterministic. D43. | ✅ |
| **V3** | `key_points` integrity — 250/250. Check pre-existed V3. D42. | ✅ |
| **V4** | Claim source — resolved by deferral. D44. | ✅ |
| **V5** | Score range + silence semantics — resolved in D47: range [-100,+100], silence = 0.0. | ✅ |
| **V6** | Local Python environment (3.11 vs 3.14) — resolved in D48. | ✅ |
| **O9 / G2** | Manual decomposition exercises + authoring guide. Closed — see D51/D52. | ✅ |
| **Phase 8** | AraT5 fine-tuning — CLOSED, SUPERSEDED by D74. | ✅ |
| **D77–D80** | Sanity gate designed, executed, PASSED on cohere/north-mini-code:free. | ✅ |
| **D74 Fallback** | Model caching for demo, or a backup model on API failure/rate-limit. Blocks final demo/full-pipeline run. | ⛔ |
| **Q8 / D82-D83 consequences** | RESOLVED (D88+D89): Coverage channel measured on real decomposition claims (D82/D83 execution — 19/19 successful cases, adapter mean 0.180 vs zero-shot mean 0.395). Combined with D88's Precision-channel finding, this basis drove D89's decision to run both channels zero-shot at runtime. | ✅ |
| **G4** | Threshold calibration (τ_E, τ, α, k currently PRE-CALIBRATION DEFAULT). Inputs in D43. | ⛔ |
| **Q7 / O11** | Recording tech stack + session spec + team adoption. **Blocks G3** and ASR selection (Phase 7). | ⛔ |
| **G3** | Pilot videos — blocks ASR selection (tied to Q7). | ⛔ |
| **Q10 — Demo #1** | Has the Baseline Demo (D24) been shown to the supervisor? | ⛔ |
| **Q2** | 250-question review documentation + SE-006 anomaly check. | ⛔ |
| **D73** | Exhaustive D72 error analysis — non-blocking retrospective documentation. | ⛔ |
| **O1** | Option B justification paragraph — final report. | ⛔ |
| **Gold naming** | RESOLVED (D84): the decomposition training corpus (D67-D69, formerly "Gold Corpus v2") renamed to "Decomposition Training Corpus v2" in decisions.md to disambiguate from the O9 validation set and the DS-014 NLI Gold Set. The archived Arabic original and already-executed result artifacts (results/d68_atomicity/*, the literal results/gold_v2/ path referenced in D69) are left unchanged as historical record. | ✅ |
| **D89-a** | F1 fix: strengthen system_prompt.md constraint 8 + add SG-09 numeric-fact fixture + re-run D77 gate at 9/9. Pre-registered as D90 (actions defined, not yet executed). Gate PASSED 9/9 (D92). | ✅ |
| **D89-b** | Fine-tuning repair experiment (structural-label corpus): register acceptance criteria, generate, train, evaluate vs zero-shot — gated on D89-a. | ⛔ |

---

## Section 5 — Methodology Principles (do not violate)

- **§5.13 (Rule 13) — empirical ≠ inferred:** never state code/library behavior without actually running it. Applies to everyone (supervisor and Claude included). A correct result with fabricated evidence = a full violation. Logged violation instances live in D31.
- **Pre-registration discipline:** every architectural decision is registered as a D## entry **before** any experiment runs.
- **Corrections are documented explicitly**, not silently overwritten — a changelog entry names the old wrong value before replacing it.
- **Gold Set / O9 labels are never changed after seeing a result** (the P48 and O9 immutability cases — reported as a limit, not a correction).
- **Acceptance criteria constrain every confusion-matrix cell**, not only the expected column (lesson from D39).
- **Scoring-stage decision rules are written at threshold level, not argmax** (lesson from D43).
- **Post-hoc analysis is written under "results analysis," not "success criteria,"** and labeled as such.
- **val (n=15) is never cited as performance.** macro-F1 is descriptive, not a criterion.
- **HARD_POS twin pairs are never split** across the train/val boundary.
- **Arabic content is reviewed via file upload, not terminal copy-paste** — RTL corruption/mojibake is consistent in cmd.exe.
- **Coverage = 0 is a critical failure mode:** the harmonic merge zeroes F regardless of Precision — the highest-priority unresolved verification (Q8).
- **LLM generation has a structural limit for organic R1 errors:** zero organic R1 across 223 synthetic questions — a known limitation, not an implementation failure. Human-authored O9 remains essential.

---

## Changelog (condensed)

- **v3.4 (28 Jul 2026):** D103 — outcome of D102: both SE-028/GN-040 runs SUCCEEDED (commit `e7bc9fa`, verified by the notebook's commit guard); all D102 §5 glossary defect criteria PASSED (claim counts preserved 6=6/5=5, no meaning drift, no invented Latin forms, 12 substitutions across 3 terms). Four findings recorded: F4 — non-Arabic, non-Latin script (Cyrillic тест, CJK 故) emitted by the approved llama-3.3-70b-versatile model on real ASR input, undetected by the D77 gate fixtures, not mitigated by the glossary; F5 — knowledge injection and reasoning leakage under prompt v4 on GN-040 (model corrected then restored a wrong value, contaminating the claim judged CONTRADICTED); F6 — the D102 §6 conversion-rate figure is not computable, since transliteration_audit records substitutions but not undetected-term counts (denominator was never instrumented); F7 — the glossary's actual scope is wider than "substitution only" (D102 §5), also performing orthographic/diacritic/tatweel normalisation, requiring a description correction before publication. Also records an unregistered CONTRADICTED-on-correct-claim observation resembling F3 (not conflated with it, different decomposition/claim indices). No remedy applied; F3-F7 each deferred to their own decision.
- **v3.3 (28 Jul 2026):** D102 — first empirical measurement of the deterministic glossary layer on real runtime output (PRE-REGISTERED before execution, NON-GATING -- a measurement, not a pass/fail gate). Instrument: kaggle/runners/run-pipeline-demo.ipynb on SE-028/GN-040 (iq-audio-pilot), zero-shot, writing to _v3.json outputs; the pre-glossary _v2 artifacts are retained unmodified as evidence. Measurement surface is claims_raw vs claims within the same run (isolates the glossary); _v2-vs-_v3 is explicitly excluded as confounded (prompt v4 changed too). Pre-registers expected mixed output, expected ABSENT terms as orthographic variants rather than missing concepts, and an expected multi-word matcher defect (Data سيت pattern); pre-registers defect criteria (claim-count preservation, no meaning drift, no invented Latin forms). Reports a conversion-rate figure from transliteration_audit, n=2 questions, DIRECTIONAL not statistical, raw counts not percentages. Does not supersede D82/D83 (produced by a script with no glossary call site in its history); does not address F3; does not close the sg05verify EXPECTED_COMMIT warning-vs-failure gap. Also recorded: D101 carries no changelog line of its own -- backfilling it is deferred to a separate decision, not part of this entry.
- **v3.2 (27 Jul 2026):** D100 — D77 sanity gate rerun under prompt v3: FAIL (4/15 cases failed error_preserved: SG-01, SG-09, SG-10, SG-15). Regression on the D88 numeric class (SG-09) previously held by a targeted patch. Structural defect found: the gate never calls apply_glossary, so criterion 3 (transliteration_correct) is VOID for SG-10/12/15, not measured. New gate-design gap recorded (unforced distortion of an uninjected proposition, SG-14). Escalation path open but not exercised; remedy sequence deferred to gate-wiring fix + controlled comparison (D101).
- **v3.1 (27 Jul 2026):** D99 — prompt v3 (generalized anti-knowledge-injection constraint) applied; fixtures SG-14 (POLARITY) / SG-15 (CAUSAL_DIRECTION) added; sanity-gate notebook hardened (dynamic n_cases + EXPECTED_COMMIT guard); two §5.13 violations recorded (D97's false git_commit-check claim; a withdrawn per-class-patch prompt draft); criterion-3 scope corrected to SG-10..15 with SG-14 registered non-gating. Outcome registered as D100.
- **v3.0 (21 Jul 2026):** D81 — full English migration + thematic reorganization of the log (D1–D80). All figures carried over verbatim; superseded AraT5 procedural entries (D58–D73) condensed to outcomes; Arabic original archived. Added D78/D79/D80 (sanity gate execution: gemma VOID, llama VOID, cohere PASS).
- **v2.41–v2.37 (21 Jul 2026):** D74 pivot (AraT5 → runtime LLM API, supervisor-approved); D75 (Codex corpus attempt, closed/superseded); D76 (first end-to-end LLM call, nemotron after gemma 429); D77 (sanity gate design). "Zero LLM at runtime" reframed to "LLM-free correctness core."
- **v2.36–v2.33 (19–20 Jul 2026):** D70 (paired corpus), D71 (paired FT, checkpoint-543, eval_loss 2.205), D72 (quality REJECTED — O9 LCS F1 0.189), D73 (error-analysis pre-registration); D67/D68 (atomicity adjudication: 24+10), D69 (Decomposition Training Corpus v2 build pre-registration).
- **v2.32–v2.27 (18 Jul 2026):** D64 (full retrain, EXECUTION PASS/no quality), D65 (QUALITY FAIL — median edit sim 0.519/0.160, Q6 reopened), D66 (PEFT repair, NO REPAIR CANDIDATE); D62/D63 (single- and five-example overfit diagnostics PASS).
- **v2.21–v2.16 (13–16 Jul 2026):** D53–D57 (Q6 pilot, AraT5 selected on linguistic grounds, corpus expansion 223/225, prompt format, trainer hyperparameters + save_total_limit fix).
- **v2.15–v2.12 (12–13 Jul 2026):** D50–D52 (O9 sample pre-registration, O9 closure with organic R1 in 7 questions, G2 closed by consequence).
- **v2.11–v2.9 (10–11 Jul 2026):** D45 (metrics.py semantics ratified), D46 (reversed-direction diagnostic), D47 (score range [-100,+100]), D48 (Python 3.11), D49 (probe result — no signal).
- **v2.8–v2.3 (9–10 Jul 2026):** D42–D44 (Q8 reframed, 0.002 withdrawn, V4 deferred — O9 to critical path), D43 (V2 closed, 48/48 deterministic, two zero-shot false verifications), D39–D41 (Phase 5 pre-registration + PASSED result).
- **v2.2–v2.0 (9 Jul 2026):** merged the two logs (Q1 closed); D37/D38 (Kaggle staging, first fine-tuning run); D33 (G1 closed by risk acceptance); D35 rewritten; D31 expanded.
- **v1.x:** pipeline-session log (old D21–D26 numbering) — implicitly archived.

---

## D97 — Deterministic transliteration layer + generalized anti-knowledge-injection prompt (v3) + gate verification fix (2026-07-23)

**Status:** PRE-REGISTERED. Outcome registered as D98 after the v3 gate rerun on Kaggle. Component (a) implemented in this entry's commit; components (b) and (c) follow in the same session before the gate rerun.

**Motivation:** three documented silent-correction classes (numeric D88-F1, editorialized D94-C1, ordering D96/SG-10), each closed by a targeted hardening and followed by leakage through the next unseen class; and transliteration_correct=0/4 on SG-10..13 under prompt v2 despite inline examples naming the exact words that failed. Conclusion: transliteration is a deterministic task wrongly assigned to a probabilistic component, and error-preservation requires a generalized principle rather than per-class patches.

### Model input scope — VERIFIED (not assumed)
Audited from the repository this session. decompose_via_llm(asr_text: str) takes exactly one argument (src/interview_iq/decomposition_llm/client.py). The Groq payload contains exactly two messages: system = system_prompt.md loaded verbatim with no interpolation, user = the raw transcript. pipeline.py passes only asr_record["normalized_transcript"]; question text and reference chunks are first used after decomposition returns. Therefore the decomposition LLM receives NO question text, NO reference content, NO track or question ID. This property is required and must not regress.

**Path correction:** src/interview_iq/decomposition/ is a legacy stub package (NotImplementedError). The production module is src/interview_iq/decomposition_llm/. All D97 code goes in the latter.

### (a) Deterministic transliteration layer
New module src/interview_iq/decomposition_llm/transliteration.py, pure function apply_glossary(claims) -> (claims_out, audit). Runs AFTER decompose_via_llm and BEFORE the ReferenceDocument construction in pipeline.py. No LLM, no randomness, no network at runtime.

Term source (closed-domain): Latin-script terms extracted programmatically from data/refdocs/reference_docs_250_FINAL_v1.json (250 documents, 1,515 chunks, verified this session). Extraction covers single tokens and multi-token Latin sequences.

**Build-time LLM disclosure:** the Arabic transliteration surface forms are authored at BUILD TIME by an LLM (Claude Code) and committed as a static reviewed artifact, data/glossary/transliteration_glossary.json. Runtime remains fully deterministic: a file read plus literal substitution. This does not affect the "LLM-free scoring core" property, since no correctness judgement is involved, but it is recorded explicitly rather than left implicit. The artifact is human-reviewed in the commit diff.

**Deterministic safety filters, applied after authoring (revised — see revision note at the end of this entry):**
- R-A collision: if two distinct Latin terms RAW-normalize (diacritics stripped, alef variants unified — no proclitic stripping) to the same Arabic form, BOTH are removed to AMBIGUOUS. Proclitic stripping is deliberately excluded from this comparison; see the revision note (point 3) for why.
- R-B lexical collision: if an Arabic form occurs as a standalone token anywhere in the Arabic prose of the 250 documents (question text and chunk text), it is removed to AMBIGUOUS — it is a real Arabic word.
- R-D lexicon collision (added in the revision): if an Arabic form occurs in the general Arabic wordlist committed at data/glossary/arabic_wordlist.txt (MIT-licensed, ~3.49M entries, source: github.com/MustafaLinux/arabic-words-list), it is removed to AMBIGUOUS. See the revision note (point 2) for why this was escalated into D97 rather than left deferred.
- R-C length: any Arabic form of 4 characters or fewer (raised from 2 in the revision) is removed to AMBIGUOUS. The lexicon (R-D) is predominantly Modern Standard Arabic and will not catch Egyptian colloquial homographs of short technical loanwords; the length rule is the deterministic backstop for that gap. 4, not 5, so that article-carrying forms (e.g. the definite-article spellings of "test" and "code", 5 characters) survive while their bare 2–3 character stems do not.
Filter order: R-A, then R-B, then R-D, then R-C. A term with no surviving forms is dropped from the glossary entirely.

**Phonetic-only rule:** the glossary contains phonetic transliterations only — Arabic spellings that represent the ENGLISH pronunciation. Semantic Arabic translations are forbidden. Example of the distinction: an Arabic spelling pronounced "el-test" mapping to "test" is valid; the Arabic word meaning "examination" mapping to "test" is a translation and is forbidden, because substituting it would alter propositional content.

**Independence rule (pre-registered):** no term may enter the glossary because it was observed in sanity-gate outputs. A term enters only if it occurs independently in the 250-document corpus. Verified counts for the terms that failed the D96 gate, measured from the corpus this session: test = 2 documents, code = 6, database = 2, bit = 6, byte = 1. All five qualify independently. This intersection is reported again in D98.

**Retracted:** an earlier proposal in this session to select glossary terms by a document-frequency threshold is withdrawn. Measurement showed frequency does not track importance: test and database occur in 2 documents each and would be excluded by any threshold of 3 or more, while the English function words "of" and "and" occur in 9 and 4 documents respectively. Selection is by term shape and phonetic plausibility, not by count. Recorded as a correction, not silently replaced.

**Matching at runtime:** normalization (diacritics stripped, أ/إ/آ unified to ا), optional Arabic proclitics (ال، و، ب، ك، ل، ف), longest-match-first, word-boundary aware. Deterministic and order-independent for a fixed glossary.

**Lexical collision beyond the 250-document corpus (revised — see revision note point 2):** R-B only detects collisions with Arabic words that appear in the 250 documents. Measurement in the same session's review showed this is the DOMINANT failure mode, not a residual one: ورم (Worm), سكان (Scan), رام (RAM), روم (ROM), دوم (DOM), روز (Rows) and البت (bit) all survived the first filter pass despite being real, common Arabic words absent from the technical-prose corpus. The registered escalation — a frozen Arabic lexicon committed as a dependency — is therefore invoked now, as R-D, rather than deferred. Mitigation retained regardless: the gate records both raw and post-glossary claims, and every substitution performed in a run is logged, so any wrong substitution is visible and attributable.

**Not measured (§5.13):** the effect of leaving a term in Arabic on Precision/Coverage has never been measured. The assumption that it hurts is an assumption, not a result. A before/after glossary ablation on O9 is a candidate for a later session and is OUT OF SCOPE for D97.

### (b) prompt v3 — generalized anti-knowledge-injection constraint
Replaces per-class patches with a single principle plus an operational test. Retains P1 (no meta-commentary) and P5 (no invented names), both empirically effective in D96.
Principle: the model is a text normalizer, not a domain expert. Domain knowledge must never alter propositional content. Every proposition uttered by the speaker — value, order, comparison direction, polarity, scope, completeness — is carried into the claims exactly as uttered, including when the model is certain it is wrong.
Operational test, applied before emitting each claim: could a person with zero domain knowledge produce this claim from the transcript alone? If not, the claim is contaminated.
The three documented classes are retained as illustrations of the principle, not as separate rules.
The transliteration constraint in the prompt is explicitly downgraded to best-effort and non-gating, since the glossary now owns that task.

### (c) New unseen-class fixtures SG-14, SG-15, and gate notebook fix
SG-10..13 outcomes have been observed; a v3 PASS on them alone cannot distinguish generalization from a fourth patch. Two fixtures of a fourth, never-tested class:
- SG-14 — polarity inversion: the speaker negates a true property or asserts a false one.
- SG-15 — causal direction reversal: the speaker states A causes B where the fact is the reverse.
Interpretation rule (pre-registered): PASS on SG-14/15 is evidence of generalization. PASS on SG-10..13 with FAIL on SG-14/15 is recorded as a fourth patch, not a fix, and triggers the registered escalation path (model replacement evaluated under the same gate, D77–D87 precedent).
kaggle/runners/run-sanity-gate.ipynb hard-codes an expected n_cases == 9, raising a spurious RuntimeError. The expected count is read dynamically from the fixtures file. The git_commit check is unchanged — it caught VOID run 143137Z.

### Pre-registered success criteria (outcome → D98)
1. error_preserved = YES on 15/15. Any NO fails the entire gate (zero tolerance, per D77).
2. no_unauthorized_addition = YES on 15/15.
3. transliteration_correct judged on POST-glossary output, gating for SG-10..15 only; SG-01..09 keep their original criteria (no retroactive rule change). YES iff every in-glossary term was converted, no out-of-glossary term was converted incorrectly, and every AMBIGUOUS term was left unchanged.
4. residual_ambiguous_count recorded, non-gating.
5. Atomicity tracked, non-gating (unchanged from D77).
6. The gate records BOTH raw LLM claims and post-glossary claims, so any failure is attributable to its component.
7. Judgment is fully human (Ahmed) on file-uploaded outputs.

### Data recovery incident (recorded)
The gitignored data files (reference_docs_250_FINAL_v1.json, questions_250.json, gold_set_48.json, the two pairs_pilot_150_v2 files) were absent from the P:\interview-iq working tree: they are excluded from git by .gitignore and the machine transfer policy is git-only, so they were never transferred. A complete copy was found to already exist as the Kaggle dataset iq-nli-finetune-data (5 files). gold_set_48.json was verified identical by SHA-256 against the pre-move copy: 73faf09e05f452122f996649affddc273e8bbbe01c1843d88415fbc9bb06e485. reference_docs_250_FINAL_v1.json was verified as 250 documents / 1,515 chunks. Recommendation (documentation-only, separate session): record the Kaggle dataset as the designated backup location in decisions.md, and revisit whether these files should remain gitignored in a private repository.

**Revision note (same session, after first implementation review):**
Three claims in the first draft of this entry were falsified by the implementation and are corrected here rather than silently rewritten.
1. The draft asserted that R-A is the mechanism that catches bit/byte automatically. This was false. The build-time authoring produced البت for bit and البايت for Byte, which do not collide, so R-A never fired; the form actually at issue, بيت, was never authored at all. The claim is withdrawn. bit/byte is now handled by R-D (lexicon) plus R-C (length), and the outcome is reported empirically in the filter report rather than asserted in advance.
2. The draft described lexical collision with Arabic words absent from the 250-document corpus as a residual risk. Measurement showed it is the dominant case, not a residual one: ورم, سكان, رام, روم, دوم, روز and البت all survived the first filter pass. R-B alone is insufficient because it checks technical prose while the collisions are with general Arabic vocabulary. The registered escalation path (a frozen Arabic lexicon committed as a dependency) is therefore invoked now, within D97, rather than deferred.
3. The draft specified proclitic stripping for collision comparison. This produced eight false-positive removals (Bash, Cache, Code, Pod, FIFO, LIFO, Queue, catch), including Code, which is one of the terms that failed the D96 gate. Collision detection now compares raw normalized forms; proclitic stripping is retained for runtime matching only.
4. The lexicon path invoked in item 2 above was itself falsified on execution. The retrieved wordlist (3,488,449 entries) is a token dump, not a curated lexicon: it contains malformed entries (فنسور, باكاستان, الراآن, البواعجا) and it contains the transliterations themselves (تست, كود, بايت, سيرفر, كلاس, ستاك), so R-D cannot distinguish an Arabic word from a transliteration — survival became incidental (ستاك removed, الستاك retained). Separately, R-B was shown to be logically inverted: Code and Byte were removed because الكود and بايت occur in the Arabic prose of the 250 documents as transliterations used by the reference documents themselves, which is evidence that the term IS transliterated, not evidence that it is a native Arabic word. Both filters are therefore rejected and the wordlist file is not committed. Empirical outcome of this pass, recorded rather than discarded: Test, Code, Queue, RAM, Worm and Scan were all removed from the glossary, so this configuration would not have addressed the D96 transliteration failure at all. R-A is retained as verified correct after the raw-form fix, yielding exactly four genuine collisions: GET/git, Phishing/Vishing, Batch/Patch, View/Vue. R-C is retained. D97 component (a) is NOT closed. Successor design under review for the next session: delete R-B entirely; replace R-D with a frequency-ranked Arabic list truncated at a pre-registered N, looked up after proclitic stripping, with N fixed before execution and not retuned after seeing which terms survive.

**Environment finding (recorded, not acted on):** during implementation the editable install of this package was found to point at the superseded path C:\Users\Admin\Desktop\Interview IQ. It was reinstalled from P:\interview-iq and pytest 8.2.0 (already a declared dependency) was installed to run the new tests. This environment change was not part of the reviewed diff and is recorded here for completeness.

---

## D98 — Component (a) closure: glossary adjudicated by human judgment; R-B and R-D deleted; matcher normalisation asymmetry repaired (2026-07-26)

**Supersedes:** the automated-filter design registered in D97 component (a). D97 (a) was
explicitly left NOT closed; this entry closes it. D97 (b) and (c) are untouched and remain open,
and are registered together as D99.

**Measurement driving this decision.** Computed on data/glossary/transliteration_glossary.json
as committed at ccafc91, and on results/glossary/filter_report_v2.txt. All figures below were
independently recomputed at registration time and matched exactly:
- inventory 2,101 terms; 901 with >=1 authored form; 757 surviving all filters
  (1,434 forms, zero form shared by two terms — R-A verified clean)
- 379 ambiguous form-records across 250 terms:
  R-A 16 records / 8 terms · R-B 10 / 8 · R-D 352 / 239 · R-C 1 / 1
- Adjudication set (R-B union R-D) = 242 terms / 362 form-records. Intersection of R-A with the
  adjudication set = 0. No single (term, form) record fired both R-B and R-D.
- Of those 242 terms: 106 still have a surviving form (partial removal), 136 were removed entirely.
- Among surviving forms, 114 have length <= 5 after stripping a leading ال; 1,320 do not.

**Correction of a figure stated earlier in the session.** The adjudication set was first stated
as 248 terms. That figure double-counted six terms hit by more than one rule (Android, Pull,
Shell, Virus, Web under both R-B and R-D; Scrum under both R-C and R-D). The correct figure is
242 terms / 362 form-records and is the one used throughout this entry.

**Finding F — R-D is arbitrary within a single term.** R-D assigned opposite verdicts to the
bare form and the article-prefixed form of the same word, and the direction is not consistent.
Observed: Agile (الأجايل survives, أجايل removed), and the same pattern for Attack, Cloud,
Cipher, Binary, Boolean, Backdoor; Branches is the reverse (برانشز survives, البرانشز removed).
This has no linguistic explanation and is an artifact of the wordlist's tokenisation. It is a
third independent falsification of R-D, after (i) the source being a token dump containing the
transliterations themselves and (ii) R-B being logically inverted.

**Finding G — matcher normalisation asymmetry (measured, not inferred).**
src/interview_iq/decomposition_llm/transliteration.py was read in full (151 lines) as a blocking
check before this entry was written. Verdict: **INPUT ONLY**. normalize_arabic() (diacritic
stripping and alef-variant unification) is defined at lines 47–50 and applied to the incoming
claim text at line 125, but is never applied to any glossary form: _load_glossary() (lines
80–101) stores entry["forms"] verbatim, and _proclitic_prefixed_pattern() (lines 69–77) compiles
those raw strings directly via re.escape(form). Additionally, strip_proclitic() (lines 53–57) is
defined but never called anywhere in the file — dead code applying to neither side; proclitic
handling is instead done inside the regex as an optional prefix group.

Consequence, measured on the committed glossary: any form containing a character that
normalize_arabic rewrites can never match a normalised claim. **355 of 1,434 surviving forms
(24.8%) are in this state, rendering 185 of 757 terms (24.4%) completely unmatchable** — every
form of those terms is affected. Breakdown of the affected forms: 343 contain an alef variant
(أ / إ / آ), 14 contain a diacritic or tatweel. Worked example: the claim text "الأبستراكشن" is
normalised to "الابستراكشن" at line 125, while the compiled pattern still contains the raw
"الأبستراكشن", so the substitution never fires. The same applies to Access Control, Accuracy,
Activation Function, Agent, Agile, Algorithm, Analytics, Arrays, and 177 further terms.

This is a silent failure: the layer executes without error, reports success, and skips a quarter
of the glossary. It was never observed because the layer has not been run on real decomposition
output since the glossary was built. It is registered here as a measured fact, not a suspicion,
and its repair is made a precondition for closing component (a).

**Rationale for abandoning the automated-filter path entirely.** The successor design under
consideration (a frequency-ranked Arabic list truncated at a pre-registered N) would introduce an
external dependency requiring provenance verification, plus a threshold N that trades false
removals against false substitutions with no principled basis for its value, in order to decide a
set of 242 terms that a human can decide directly. The measured size of the problem does not
justify the machinery. Machine filters are retained as triage only, never as the authority.

**Governing asymmetry principle.** A missed transliteration costs NLI recall: graceful,
measurable, recoverable. A false transliteration rewrites the candidate's utterance and is the
silent-correction failure class (D88 numeric, D94 editorial, D96 ordering) reintroduced by our own
deterministic component. The two errors are not equal in cost and the design must not treat them
as such. Therefore: no substitution without positive human approval; ties resolve to AMBIGUOUS.

**Rule set after this entry:**
- **R-A — RETAINED, permanent, NOT adjudicable.** The 4 collision pairs (GET/git,
  Phishing/Vishing, Batch/Patch, View/Vue = 16 records / 8 terms) remain AMBIGUOUS by
  construction: they are undecidable without context, and context-based disambiguation is
  prohibited under D97's near-homograph ruling (option A).
- **R-B — DELETED.** Logically inverted (D97 revision note, item 2).
- **R-C — RETAINED as a hard veto:** any form of raw authored length <= 4 is never substituted,
  regardless of adjudication. Currently 1 record (Scrum). Retained as a cheap backstop for future
  glossary additions.
- **R-D — DELETED.** Non-evidentiary source (D97 revision note, item 1) plus Finding F.
- **H-1 — NEW.** Human adjudication is the sole authority for the 242-term set.

**H-1 procedure.** results/glossary/adjudication_H1_v1.tsv lists the 242 terms / 362 form-records
(columns: idx, term, form, rule, other_forms_surviving, verdict) and is reviewed by Ahmed as an
uploaded file, not via terminal (RTL corruption rule). Each record receives KEEP or AMBIGUOUS
under this decision rule, fixed before the file was seen:

> "In the context of a spoken answer to a technical interview question within the five tracks
> (DA/DS/CS/SE/GN): is there a plausible reading of this Arabic form as an ordinary Arabic word?
> If yes -> AMBIGUOUS. If no -> KEEP. Ties -> AMBIGUOUS."

**Independence rule (restated from D97, still binding).** No glossary entry may be kept, removed,
or added because it was observed in sanity-gate outputs. Neither the review-file generation nor
the adjudication may consult results/llm_decomposition_sanity_gate/, any sanity-gate fixture,
scripts/llm_decomposition_sanity_gate.py fixture definitions, or
results/o9_decomposition_exercises.md. The generating run asserted compliance explicitly. The
intersection count between final glossary terms and gate-fixture terms is reported in the closing
note.

**V-1 survivor verification, pre-registered before any result is seen.** The 757 surviving terms
are not assumed safe: their Arabic forms were authored by a build-time LLM
(meta.authored_by = "build-time LLM (Claude Code)") and have never been human-reviewed.
- **Stratum A:** all 114 surviving forms (85 terms) whose length after stripping a leading ال is
  <= 5 characters. Fully adjudicated under the H-1 rule. This is the high-risk stratum.
- **Stratum B:** 50 forms drawn uniformly at random, without replacement, from the remaining
  1,320 surviving forms, RNG seed 20260726, recorded in results/glossary/verification_V1_v1.tsv.
- **Escalation threshold, fixed now:** if Stratum B yields >= 1 AMBIGUOUS verdict, all 1,320
  remaining forms go to full adjudication before (a) may be closed. The threshold is not revisited
  after the result is seen.

**Disclosure on generation order.** adjudication_H1_v1.tsv and verification_V1_v1.tsv were
generated before this entry was committed, under the text as approved in session. The sampling
seed, strata definitions and column schema in the generated files are identical to those
registered above; no parameter was chosen or altered after any verdict was seen. Recorded here
rather than left implicit.

**Required repair R-1 (consequence of Finding G).** Before component (a) may be closed:
1. Glossary forms must be passed through the same normalize_arabic() used on the input, at load
   time in _load_glossary(), so both sides are normalised identically.
2. strip_proclitic() must be either wired in deliberately or deleted; dead code in a
   safety-relevant module is not acceptable.
3. A regression test must be added asserting that a claim containing "الأبستراكشن" yields the
   substitution "Abstraction", and that at least one diacritic-bearing form also matches. The
   test must fail against the current code and pass after the repair — this is to be demonstrated
   by running it in both states, not asserted.
4. The count of forms rendered matchable by the repair is reported and compared against the 355
   figure measured above.

**Deterministic completion step.** After adjudication, every term with at least one KEEP form
receives both the ال-prefixed and the bare variant of each KEEP form, eliminating the R-D
tokenisation artifact documented in Finding F.

**Not measured (§5.13, carried forward from D97 unchanged).** The effect of leaving a term in
Arabic on Precision and Coverage has never been measured. The assumption that it harms scoring is
an assumption, not a result. A before/after glossary ablation on O9 remains a candidate for a
later session and is OUT OF SCOPE here.

**Acceptance criteria for closing component (a) — all five required:**
1. All 362 adjudication records carry a KEEP or AMBIGUOUS verdict.
2. Stratum A (114 forms) fully adjudicated; Stratum B (50 forms) adjudicated and the escalation
   threshold either not triggered or satisfied by full adjudication.
3. Repair R-1 completed, with the before/after test states demonstrated by execution.
4. Rebuilt glossary committed, with a regenerated report stating: final KEEP terms, final KEEP
   forms, AMBIGUOUS records by origin (R-A / R-C / H-1 / V-1), and the gate-fixture intersection
   count.
5. No claim in this entry left in the form of an expectation rather than a measurement.

**Process failure recorded (§5.13, procedural).** The first Claude Code task issued for this
entry contained a literal placeholder line instructing that the D98 text be pasted in, in direct
violation of the standing rule that pre-registered decision text is supplied inline and never as
a placeholder. Claude Code correctly refused to fabricate the entry and halted at STEP 2 rather
than inventing content. The failure was in the task authoring, not the execution. Remedy adopted:
decision text is supplied to Claude Code as a file in the working tree to be appended verbatim,
never as prose to be pasted into a prompt.

**R-1 execution note (2026-07-26).** R-1 is complete and demonstrated by execution. The two
regression tests were written first and failed against the unmodified source (2 failed, 9 passed),
confirming Finding G empirically before any repair. After the repair all 11 transliteration tests
pass. Two failures elsewhere in the suite (tests/test_finetune_smoke.py, a transformers
TrainingArguments API mismatch) were confirmed pre-existing and unrelated by stashing the repair
and reproducing them identically against the unmodified tree. Measured matchability using the
actual matcher: before the repair 355 of 1,434 forms and 185 of 757 terms were not correctly
matched, in exact agreement with Finding G; after the repair, 0 and 0.

**Finding H — silent wrong-term substitution (discovered during R-1, now closed).** A first,
naive measurement counting "did any substitution fire" returned 298 broken forms, disagreeing
with the 355 figure. The discrepancy was investigated rather than reconciled by adjustment. Of
the 355, 298 produced no match at all and 57 produced a substitution for the WRONG term: in
multi-word entries whose first word carries an alef variant or diacritic (e.g. Activation
Function -> الأكتيفيشن فانكشن), the full-phrase pattern failed under the asymmetry bug while the
second word alone, an independent surviving form of a different term, matched instead — rewriting
the claim to "الاكتيفيشن Function" and leaving the intended term unrecognised. This is a false
substitution, the failure class the governing asymmetry principle of this entry exists to
prevent, and it was operating silently. All 57 are resolved by R-1 (0 wrong-term substitutions
after the repair). Recorded because it was measured, not because it was anticipated: it was not
predicted by Finding G.

**Collision check on the repair (executed).** Normalising the glossary keys could have caused two
forms of different terms to collapse onto one key and silently overwrite each other. Verified:
the 1,434 surviving forms yield 1,434 distinct normalised keys, 0 keys map to more than one term,
and 0 normalised AMBIGUOUS keys collide with a surviving key. The repair introduces no collision.

**H-1 adjudication result (2026-07-27).** All 362 form-records were adjudicated by Ahmed under
the decision rule fixed above. Outcome: 358 KEEP, 4 AMBIGUOUS, 0 blank, 0 invalid values. The
four AMBIGUOUS records are: idx 2 Address / أدرس, idx 174 List / ليست, idx 203 Node / نود,
idx 269 Scan / السكان. File integrity was verified programmatically against the source glossary
before acceptance: the term, form, rule and other_forms_surviving columns matched the generated
instrument in 362 of 362 rows, i.e. only the verdict column was modified.

**Adjudication stance, recorded as a deliberate design position rather than left implicit.** The
exception rate is 4 of 362 (1.1%). This is not inattention. The adjudicator's stated reasoning is
that the domain is closed and the context — a spoken answer to a technical interview question in
one of five tracks — resolves most apparent ambiguity: a candidate saying ورم in a security
question means Worm, not the medical sense. The rule as registered explicitly conditions judgment
on that context, so the stance is an application of the rule, not a departure from it. It is
recorded here so that it can be defended directly if questioned, rather than appearing to be an
oversight. Residual risk accepted knowingly: forms such as ورم, بيت and بت remain KEEP and will be
substituted; if a candidate uses one in its ordinary Arabic sense inside a technical answer, that
claim will be corrupted. This is the cost side of the stance and is not hidden.

**Sub-case recorded: Scan.** السكان (definite) was judged AMBIGUOUS while سكان (bare) was judged
KEEP. This was queried as a possible oversight and confirmed by the adjudicator as deliberate: the
definite form is the ordinary Arabic usage (عدد السكان), while the bare form was judged unlikely
to appear alone. The residual risk — bare سكان in an idafa construction such as سكان المحافظة,
plausible in a DA-track answer — is accepted knowingly and recorded.

**V-1 verification result (2026-07-27).** All 164 records were adjudicated: Stratum A 114,
Stratum B 50. Outcome: 163 KEEP, 1 AMBIGUOUS, 0 blank, 0 invalid. The single AMBIGUOUS record is
idx 52, Stratum A, List / الليست.

**Escalation threshold: NOT triggered.** Stratum B returned 0 AMBIGUOUS verdicts. Under the
threshold fixed before any result was seen, the remaining 1,270 surviving forms therefore do not
require full adjudication. This is a measured outcome of a pre-registered test, not an assumption
that the remainder is safe. Instrument integrity verified before acceptance: Stratum A matched the
deterministic expected set (all surviving forms of ال-stripped length <= 5) exactly; every Stratum
B row was drawn from the surviving set, every one had ال-stripped length > 5, there were no
duplicates within B and no overlap between A and B; the bare_len column was consistent with the
form column in all 164 rows.

**Consequence: the term List is fully disabled.** Both of its forms are now AMBIGUOUS — ليست via
H-1 and الليست via V-1. A candidate using either form to mean the data structure will not receive
the substitution. Accepted: ليست is a core Arabic negation particle, and the model's output
register is simplified MSA, so a false substitution here would invert the polarity of a claim.

**AMENDMENT — the deterministic completion step registered above is DELETED, not merely
constrained.** The step was written to undo Finding F, R-D's arbitrary within-term asymmetry. That
purpose has lapsed: every form R-D removed passed through explicit human adjudication in H-1, so
the asymmetry has already been repaired by hand and more reliably than an automatic rule could.
The step was measured before being written into the rebuild rather than after: it would generate
34 form-records, of which 1 already exists in the authored inventory and 33 have never been
authored by anyone and never reviewed under H-1 or V-1; 11 of those 33 fall in the short,
high-risk class. Among them the step would invent البيت for the term bit — البيت being among the
most common words in Arabic. Running the step would therefore reopen, in the final build stage,
precisely the unreviewed-form exposure that V-1 exists to measure, in exchange for 34 records
belonging to terms that already have a working KEEP form. The benefit is null and the risk is
real, so the step is removed.

**Correction, recorded rather than silently applied.** An earlier remedy proposed in session —
"run the completion step except where the generated variant was explicitly judged AMBIGUOUS" —
was insufficient and is rejected. It would have caught the three conflicts with existing verdicts
(الأدرس→أدرس, النود→نود, سكان→السكان) but would have admitted البيت, because بيت was judged KEEP
and البيت was never judged at all. The inadequacy was exposed by measuring the step's output
before adopting the fix. Recorded because the first proposal was wrong, not because the second
was right.

**Correction to a claim made in session (§5.13).** It was stated during review that the
adjudicator had distinguished ليست from الليست within H-1. That was false: الليست survived the
filters and was therefore never in the H-1 instrument; it was reviewed in V-1. The genuine
instance of that discrimination is أدرس (AMBIGUOUS) against الأدرس (KEEP), both of which were in
H-1. The false statement is recorded rather than deleted.

**Tooling incident and rule adopted.** The first H-1 pass was completed in Microsoft Excel. On
save, Excel wrote the file in a non-UTF-8 encoding and replaced every Arabic character with a
literal '?', destroying the form column irrecoverably in that copy. No data was lost: the
instrument was restored byte-exact from git (commit cc039e9) and the pass was redone in Google
Sheets, which round-trips UTF-8 correctly. Rule adopted: Microsoft Excel is never to be used to
edit UTF-8 TSV files in this project. Separately, that first pass returned KEEP on all 362 rows;
it was rejected and redone rather than accepted, and the rejection is recorded.

**Machine triage disclosed.** Before the human pass, a machine-produced shortlist of roughly 75 of
the 362 rows was supplied, flagging forms worth closer attention. It contained no verdicts. The
adjudicator reviewed all 362 rows, was free to override the shortlist in either direction, and did
so — three of the four AMBIGUOUS verdicts fall on shortlisted rows and the shortlist's other
suggestions were declined. Recorded so that the human judgment is not later mistaken for
unassisted judgment.

**One post-hoc edit recorded.** After the adjudicator reviewed a query on idx 203 (Node / نود) and
authorised the change in session, that single cell was altered from KEEP to AMBIGUOUS
programmatically rather than by re-export from Sheets. No other cell was touched. Recorded because
it is an edit made outside the instrument's normal path.

**Projected final glossary, to be confirmed by the rebuild.** KEEP: 1,791 form-records (1,433
surviving forms after removing الليست, plus 358 restored by H-1). AMBIGUOUS: 22 form-records
(R-A 16, R-C 1, H-1 4, V-1 1). Net change against the committed glossary: +357 forms, including
Test, Code, Queue, RAM and Worm — the terms whose absence motivated this entry. No form in the
final glossary lacks both an authored origin and a human verdict or a passed verification stratum.

**AMENDMENT — R-C is demoted from a hard veto to a backstop of last resort (2026-07-27).** The
rule as registered above reads: "any form of raw authored length <= 4 is never substituted,
regardless of adjudication. Currently 1 record (Scrum)." Both halves of that sentence were true
of the pre-adjudication state and were measured again before the rebuild rather than assumed.
The result:

- Surviving forms (pre-adjudication) with raw length <= 4: **0**. R-C had in fact been enforced
  strictly across the survivor set; its single filed record is an artifact of R-D having removed
  most short forms earlier in the chain.
- Forms restored by H-1 with raw length <= 4: **109**, i.e. 30% of the 358 restored records.

Applying R-C literally would therefore veto 109 human KEEP verdicts, and among them تست (Test),
كود (Code), كيو (Queue), رام (RAM), ورم (Worm) and ويب (Web) — the precise terms whose absence
from the glossary motivated this entry and whose loss produced the D96 transliteration failure.
Strict application would return the glossary to the state that made D96 fail and would render the
entire adjudication exercise inert.

The coupling is structural rather than incidental: a short English technical term transliterates
to a short Arabic string, and a short Arabic string is more likely to coincide with an ordinary
Arabic word. R-C's length proxy therefore selects the terms most needed and the forms most
dangerous by the same measure, and cannot separate them.

**Decision (Ahmed, 2026-07-27): a human verdict supersedes R-C.** R-C is retained solely as a
backstop for forms carrying no human verdict — future glossary additions, and any record never
placed before an adjudicator. It no longer overrides an explicit H-1 or V-1 verdict. This is
consistent with the governing principle of this entry, under which human adjudication is the sole
authority and machine filters are triage; the clause "regardless of adjudication" contradicted
that principle and is withdrawn.

**Consequence for Scrum.** سكرم (raw length 4) was never placed before an adjudicator: the H-1
instrument contained only records ruled by R-B or R-D, and this record is ruled by R-C. It
therefore carries no human verdict, R-C's backstop applies unchanged, and it remains AMBIGUOUS.
Its sibling السكرم was adjudicated KEEP at H-1 idx 274 and is restored, so the term remains
serviceable through that form. The R-C AMBIGUOUS count stays at 1.

**Residual risk accepted, named rather than summarised.** 109 forms of raw length <= 4 are active
in the rebuilt glossary on the strength of their H-1 verdicts alone. The highest-collision members
of that set are, at two characters: هب, نل, رو, شل, بت; and at three: باش, باج, كاش, كود, دوم, جوي,
هاش, هيب, لوس, بود, بُل, كيو, رام, روم, روز, رست, ساس, تست, تري, ويب, ويت, ورم, بيت, لوج, بوش.
Several are ordinary Arabic words. A focused second review of these thirty was offered before the
rebuild and was declined in favour of the standing H-1 verdicts; that choice is recorded, not
implied. If a future field run surfaces a false substitution, this paragraph is where to look
first, and the remedy is a targeted re-adjudication of this list rather than a re-derivation of
the whole glossary.

**Final glossary specification, to be produced and confirmed by the rebuild.** KEEP: 1,791
form-records across 892 terms — the 1,434 surviving forms less الليست, plus the 358 restored by
H-1. AMBIGUOUS: 22 form-records — R-A 16, R-C 1, H-1 4, V-1 1. No completion step is run. Every
form in the rebuilt glossary has an authored origin and either an explicit human verdict or
membership of a verification stratum that passed.

**COMPONENT (a) CLOSED (2026-07-27).** All five acceptance criteria registered in this entry are
satisfied, each by execution rather than assertion:

1. *All 362 adjudication records carry a verdict.* Satisfied: 358 KEEP, 4 AMBIGUOUS, 0 blank,
   0 invalid. Instrument integrity verified independently — term, form, rule and
   other_forms_surviving matched the generated file in 362 of 362 rows.
2. *Stratum A fully adjudicated; Stratum B adjudicated and the escalation threshold resolved.*
   Satisfied: 114 + 50 = 164 records, 163 KEEP / 1 AMBIGUOUS. Stratum B returned 0 AMBIGUOUS, so
   the threshold was not triggered and the remaining 1,270 surviving forms do not require full
   adjudication. Stratum A was confirmed to match the deterministic expected set exactly.
3. *Repair R-1 completed with before/after states demonstrated by execution.* Satisfied: the two
   regression tests failed against the unmodified source (2 failed, 9 passed) and pass after the
   repair; measured matchability moved from 355 of 1,434 forms and 185 of 757 terms broken, to
   0 and 0.
4. *Rebuilt glossary committed with a regenerated report.* Satisfied: glossary v2 contains 1,791
   KEEP form-records across 892 terms and 22 AMBIGUOUS records (R-A 16, R-C 1, H-1 4, V-1 1);
   0 raw forms shared by more than one term; 1,791 distinct normalised keys with 0 mapping to
   more than one term. results/glossary/final_glossary_report_v1.txt records the breakdown, the
   109 active forms of raw length <= 4, and a gate-fixture intersection count of 6 computed after
   adjudication was complete.
5. *No claim left as an expectation rather than a measurement.* Satisfied. Findings G and H, the
   collision check, the completion-step deletion, the R-C conflict and the regression lock were
   each measured before being written, and in three cases the measurement contradicted the
   proposal that preceded it: the naive matchability count (298 vs 355) exposed Finding H, the
   completion-step measurement exposed البيت and invalidated the first proposed remedy, and the
   R-C measurement (0 survivors vs 109 restored at length <= 4) forced the amendment above.

**Regression lock (2026-07-27).** A gap was identified after the rebuild: every test then in the
suite passed against both the old and the rebuilt glossary, so none of the 358 restored forms was
under test and a silent reversion would not have been caught.
tests/test_transliteration.py::test_h1_restored_terms_substitute was added, asserting that التست,
الكود, الكيو and الرام substitute to Test, Code, Queue and RAM. It was demonstrated by execution
to FAIL against the pre-D98 glossary and PASS against the rebuilt one. Final suite state:
tests/test_transliteration.py 12 passed; two pre-existing, unrelated failures remain in
tests/test_finetune_smoke.py (transformers TrainingArguments API mismatch), confirmed unchanged
by this work.

**Not closed by this entry, carried forward.** The effect of the glossary on Precision and
Coverage has still never been measured; the layer's benefit remains an assumption, and a
before/after ablation on O9 is a candidate for a later session. The 109 active forms of raw length
<= 4 remain the first place to look if a field run surfaces a false substitution. D97 components
(b) and (c) remain open and are registered as D99.

**Out of scope for D98:** prompt v3 (D97 b), fixtures SG-14/SG-15 (D97 c), the sanity-gate
notebook n_cases fix, and the gate rerun. These are registered together as D99.

**Unchanged:** D89-b remains HARD-GATED on a full gate PASS.

---

## D99 — Prompt v3 (generalized constraint), fixtures SG-14/SG-15, gate-notebook hardening; pre-registered rerun of the D77 sanity gate (2026-07-27)

**Status:** PRE-REGISTERED. No gate run has taken place under this entry. The rerun outcome is registered as D100.

### 0 — Relation to D97

D97 pre-registered four components. Status: (a) glossary layer — CLOSED in D98, commit ae9940e. (b) prompt v3 — applied here. (c) fixtures SG-14/SG-15 — applied in commit dfaff6a. (d) notebook `n_cases` fix — applied in commit dfaff6a, with a scope extension recorded in section 5.

Success criteria 1–7 of D97 are unchanged by this entry, with two corrections of fact recorded in sections 4 and 6.

### 1 — §5.13 violations — two, both by Claude, both recorded

**V-1. D97 asserted a check that does not exist.** D97 (c) states verbatim: "The git_commit check is unchanged — it caught VOID run 143137Z." This is false. `kaggle/runners/run-sanity-gate.ipynb` contained no git-commit verification of any kind. Established 2026-07-27 by grepping the notebook for `commit`, `rev-parse`, `HEAD`: the only occurrence of "commit" was inside the prose of an unrelated error message. The claim was written without reading the notebook. VOID run 143137Z was caught by a human reading output, not by any automated check; the protection D97 asserted never existed. Remedy in section 5.

**V-2. The first draft of prompt v3 in this session was a per-class patch.** It added a numbered constraint specific to ordering, plus a worked ordering example. D96 states verbatim that the remedy "must be a generalized anti-knowledge-injection constraint, not another per-class patch", and D97 (b) registers a single principle plus an operational test. The draft was written from a summary rather than from the text of D96 and D97, and contradicted both. It was withdrawn before commit. Recorded because the draft would have produced a gate that could pass without testing anything, and because it is the same failure mode as V-1.

### 2 — Ordering discipline

Approved 2026-07-27: SG-14 and SG-15 were authored and committed before any text of prompt v3 was written, so the fixtures cannot have been shaped to suit what v3 handles. Verifiable in `git log`, not merely asserted: `dfaff6a` contains fixtures and notebook changes only, no prompt change.

### 3 — Component (c) — fixtures SG-14 and SG-15

- **SG-14** (DS, `WRONG_FACT`, error_class POLARITY). The speaker negates a true property — that an overfitting model memorises training noise — and reinforces the inversion by asserting the model learns only the general pattern. The final clause (poor test-set performance) is deliberately correct, so error preservation is distinguishable from wholesale paraphrase failure.
- **SG-15** (SE, `WRONG_FACT`, error_class CAUSAL_DIRECTION). An explicit causal marker makes deadlock the cause of the hold-and-wait condition, reversing the true direction. The direction is stated rather than implied by sequence; otherwise the case would overlap the D96 ordering class and test nothing new.

Both injected errors are ones the model demonstrably knows to be wrong. `error_class` is recorded inside the existing `injected_error_anchor` field; no schema field was added, and SG-01..SG-13 were not modified (fixtures diff: 18 insertions, 0 deletions).

**Correction to D97 (c), affecting how SG-14 may be read.** D97 (c) designates SG-14 and SG-15 a "fourth, never-tested class". For SG-15 this holds. For SG-14 it does not: the principle registered in D97 (b), and applied verbatim in section 6, enumerates **polarity** among the properties to be carried unchanged. SG-14 is therefore an instructed case, not an unseen one, and a PASS on it is weaker evidence of generalization than D97 (c) assumed. This is an internal inconsistency in D97 between components (b) and (c), discovered while applying it.

The resolution is recorded explicitly: **the principle is applied as registered, including the word "polarity", and the inference from SG-14 is downgraded instead.** The alternative — deleting "polarity" from the principle to protect the test — would weaken the production system in order to flatter an experiment, and is rejected. **SG-15 is therefore the primary unseen-class evidence in this run**; "causal direction" is not among the enumerated properties, and "comparison direction" does not cover it.

### 4 — Criterion 3 — scope correction and one registered exception

**Scope correction.** The `_meta.gate_pass_rule` and `_meta.d95_review_instructions` in `sg_cases.json` still restrict the transliteration verdict to SG-10..SG-13, per D95. D97 criterion 3 extended it to SG-10..SG-15. The fixtures file is corrected in this entry's commit to match; only `_meta` bookkeeping fields are touched, no fixture content. Recorded because the human reviewer works from `_meta`, and it was stale.

**Glossary check performed before the fixtures were written.** All 11 Arabic-script Latin-origin forms in SG-14/SG-15 were looked up in `data/glossary/transliteration_glossary.json` v2 (1,791 forms) using the pipeline's own normalisation and word-boundary matching. Result: 3 IN_GLOSSARY, 1 PARTIAL, 7 ABSENT.

| Fixture | Form | Status |
|---|---|---|
| SG-15 | الديدلوك | IN_GLOSSARY → Deadlock |
| SG-15 | السيستم | IN_GLOSSARY → System |
| SG-15 | الابليكيشن | IN_GLOSSARY → Application (after alef normalisation) |
| SG-14 | الداتا سيت | PARTIAL — only the embedded الداتا resolves |
| SG-14 | الاوفرفيتينج · التريننج · التيست | ABSENT — glossary forms use one fewer ي |
| SG-14 | النويز | ABSENT — no Noise entry exists |
| SG-14 | الباترن | ABSENT — only the plural الباترنز exists |
| SG-15 | التريدز | ABSENT — glossary spells Thread with ث not ت; no plural entry |
| SG-15 | الريسورسيز | ABSENT — no Resource/Resources entry exists |

**Registered exception.** Criterion 3 is **non-gating for SG-14**: zero of its terms are IN_GLOSSARY, so the criterion has no reference against which to be judged. The result is recorded descriptively and excluded from that case's PASS/FAIL. Criterion 3 remains gating for SG-10..SG-13 and SG-15. This exception is registered because the pre-registered STOP RULE for the glossary check fired and the decision to proceed was taken verbally during execution; recording it is what makes that decision auditable.

**Pre-registered expectation.** The glossary holds `الداتا` and a fused `داتاسيت` with no spaced variant, so the word-boundary matcher is expected to convert the first word and leave the second, emitting `Data سيت`. If this occurs, it is a confirmed multi-word defect in the glossary, registered here so it is not read as a post-hoc finding.

**Pre-registered interaction between the two changes in (b).** SG-12 carries no injected error; its `latin_terms_expected` is `["TDD", "test", "code"]` and its sole gating criterion is criterion 3, driven by a letter-by-letter spelled acronym. Constraint 3 is downgraded to best-effort in the same run. The downgraded text retains the acronym instruction and names `تي دي دي→TDD` explicitly, so the anti-invention clause is not expected to fire on it — but this is reasoning, not measurement, and SG-12 is the case most exposed if it is wrong.

**Open item — glossary coverage gap.** Component (a) was closed in D98 on the H-1/V-1 adjudication, but the table above shows glossary v2 carries roughly one spelling variant per term while real ASR produces several: 7 of the 11 absences are spelling-variant mismatches, not missing concepts. This is not demonstrated — the 11 forms were authored from an assumption about ASR output, not sampled from it. Recorded as an open item to be measured against real transcripts from `data/audio_pilot/`. It does not reopen D98.

### 5 — Component (d) — notebook hardening

1. **As registered in D97:** the hard-coded `n_cases != 9` check now reads the expected count dynamically from `sg_cases.json` on the cloned commit.
2. **Scope extension, not in D97:** an `EXPECTED_COMMIT` guard, remedying V-1. `scripts/llm_decomposition_sanity_gate.py` already records `meta["git_commit"]` (verified: a full 40-character SHA) but nothing compared it to anything. Cell `sg05verify` now compares it against a constant set by hand before the run and raises on divergence, converting the human check that caught VOID run 143137Z into an automated one.

`EXPECTED_COMMIT` defaults to empty, which disables the guard. This is unavoidable: the SHA does not exist until the commit is made, and the notebook is inside that commit. It is filled in the Kaggle editor before running.

**Run procedure, binding from this entry forward:** `EXPECTED_COMMIT` must be set to the pushed SHA before execution. Any run whose log shows `commit guard is DISABLED` is non-evidentiary as to which commit produced it and must be labelled as such rather than cited.

Verification executed on the final notebook state, not asserted: `ast.parse()` on all 5 code cells — OK; `nbformat.validate()` — VALID.

### 6 — Component (b) — prompt v3

Applied as registered in D97 (b).

- Former constraints 1 and 2 (never correct; never add) are replaced by **constraint 1, THE PRINCIPLE**, in D97's registered wording: the model is a text normalizer, not a domain expert; domain knowledge must never alter propositional content; every proposition uttered — value, order, comparison direction, polarity, scope, completeness — is carried into the claims exactly as uttered, including when the model is certain it is wrong; and a proposition not uttered does not appear at all.
- **Constraint 2 is THE OPERATIONAL TEST**, verbatim from D97: could a person with zero domain knowledge, holding only this transcript, produce this claim? If not, the claim is contaminated.
- The documented classes (numeric D88, ordering D96, editorial/P1 D94, invented names/P5) are retained **as illustrations under the principle, not as separate rules**, and are explicitly marked non-exhaustive. No new worked example was added: D96 recorded transliteration failing 0/4 under prompt v2 *despite* inline examples naming the exact failing words, which is direct evidence that adding examples is not the effective lever.
- **Constraint 3 downgraded to best-effort and non-gating in the prompt**, since the glossary now owns transliteration. An anti-invention rule replaces the mandatory wording: where the correct Latin spelling is not known with confidence, the Arabic form is left as uttered. Rationale is asymmetry of repair — an unconverted Arabic form can be fixed later by extending the glossary; an invented Latin spelling can neither be detected nor fixed. The instruction never to drop an unfamiliar term is retained explicitly.
- Constraints 3 through 8 keep their numbers, so no cross-reference elsewhere in the prompt is invalidated.

### 7 — Failure attribution — registered before the run

Two things change at once: prompt v3, and glossary v2, which no gate has yet exercised. Attribution is fixed in advance:

| Criterion | Attributed to |
|---|---|
| 1 — `error_preserved` | prompt v3 |
| 2 — `no_unauthorized_addition` | prompt v3 |
| 3 — `transliteration_correct` (SG-10..13, SG-15) | glossary v2 |

Failure on 1 or 2 means the generalized constraint did not generalize. Failure on 3 alone means the glossary is incomplete and carries no implication about the prompt.

### 8 — Execution plan

15 fixtures (SG-01..SG-15), model `llama-3.3-70b-versatile` on Groq, run through the Kaggle thin-runner against the pushed commit with `EXPECTED_COMMIT` set. Adjudication is fully human on file-uploaded outputs (D77, D97 criterion 7).

Interpretation rule is D97's, unchanged, with the section 3 correction applied: a PASS on SG-10..SG-13 combined with a FAIL on SG-14 or SG-15 is recorded as a fourth patch rather than a fix, and triggers the registered escalation path (model replacement evaluated under the same gate, D77–D87 precedent). Given section 3, SG-15 carries the weight of the generalization claim.

Outcome registered as D100.

### 9 — Open item discovered while executing this entry: NLI fine-tune path broken by dependency drift

`python -m pytest tests` on 2026-07-27 returned 188 passed, 2 failed. Both failures are in
`tests/test_finetune_smoke.py` and share one cause: `src/interview_iq/nli/finetune.py:299` passes
`evaluation_strategy` to `TrainingArguments`, a keyword removed in the installed transformers
(4.57.6). Not caused by this entry's commits, which touch decisions.md, system_prompt.md and
sg_cases.json — none of which is imported by the NLI path. Not gate-relevant: the sanity gate
performs no training. It is recorded because the NLI module is declared closed and verified
(D41, eval_f1_macro=0.861) and the reproducibility gate is declared closed in Phase 6, yet the
retraining path does not currently execute on this environment. Deliberately NOT fixed here: an
unregistered change to the training path immediately before a gate run is the failure mode this
log exists to prevent. Also recorded: the project record's "142/142 tests green" figure is stale;
the suite now collects 190.

Separately, `python -m pytest` from the repository root has been broken since the D74 pivot —
`archive/phase8_arat5_superseded/tests/` imports modules deleted by the pivot, so collection is
interrupted and zero tests run. Verification in this entry used `python -m pytest tests`. A
pytest-config fix (`--ignore=archive`) is deferred to a separate session.

---

## D100 — D77 sanity gate rerun under prompt v3: FAIL, with regression on a previously closed class and a structural defect in the gate itself (2026-07-27)

**Status:** OUTCOME. Registered against the pre-registration in D99. No remedy is applied under this entry.

### 1 — Run validity

Run `20260727T125204Z`, model `llama-3.3-70b-versatile`, `git_commit = 02a016a649399f4ceb3daaf916ff99404d4fe391`, matching the pushed commit. `n_cases = 15`, 15 executed successfully, 0 execution errors. The `EXPECTED_COMMIT` guard introduced in D99 §5 was armed and did not fire. The run is evidentiary as to which commit produced it.

Sampling: `client.py:129` sets `"temperature": 0`. Decoding is greedy, so differences between this run and D92 are attributable to the changed prompt rather than to sampling noise. This strengthens the comparison but does not make it a controlled one — D92 and this run differ in prompt version and were not run as paired arms. The controlled comparison is pre-registered separately as D101.

### 2 — Verdict: FAIL

Four cases fail `error_preserved`. Under the D77 zero-tolerance rule a single NO fails the whole gate.

| Case | error_preserved | Note |
|---|---|---|
| SG-01 | **NO** | Entity substituted: input `الهيب` (Heap) emitted as `الهاش` (Hash) in all five claims. The injected error concerned Heap and no longer appears. |
| SG-02..SG-08 | YES | Including SG-05 (swapped Normalization/Standardization) and SG-07 (three-part rebase error), both preserved intact. |
| SG-09 | **NO** | `alpha بقيمة 0.5` and `أقل من كده` emitted as `0.05`. A silent numeric correction. |
| SG-10 | **NO** | Input states code-before-test; claims 1–2 emit test-before-code. The stated order was reversed to the correct one. |
| SG-11 | YES | 16-vs-8 preserved verbatim, no added commentary. P1 holds. |
| SG-12, SG-13 | N/A | Non-preservation tests per `_meta`. SG-13 invented no name; P5 holds. |
| SG-14 | YES (see §4) | The injected polarity survived. A different proposition did not. |
| SG-15 | **NO** | `هو اللي بيسبب` (deadlock causes hold-and-wait) emitted as `يحدث عندما` (deadlock happens when hold-and-wait). The stated causal direction was reversed to the correct one. |

`no_unauthorized_addition` = YES on all cases.

### 3 — The decisive finding: the generalized constraint lost a class that a per-class patch held

SG-09 is the D88 numeric class. It was closed by the targeted patch in D90 and passed 9/9 in D92 under prompt v2. Under prompt v3 it fails. The difference between the two prompts on this point is that D90's explicit numeric rule was demoted, per D97 (b), to one bullet in a non-exhaustive list of illustrations under the principle.

SG-10 (ordering, D96) and SG-15 (causal direction, previously untested) also fail. So the generalized principle neither held the classes the patches held, nor covered the classes they did not.

This satisfies the escalation condition registered verbatim in D96: *"if a generalized constraint also fails the gate, model replacement re-enters via this same gate (D77–D87 precedent)."* The escalation path is open. It is **not** exercised in this entry, because §5 below shows the gate was not measuring what it was specified to measure.

Recorded against the D99 §3 reading: SG-15 was designated the primary unseen-class evidence, and it failed. SG-14's partial pass carries little weight, as registered.

### 4 — A failure mode neither gate column captures

SG-14's injected polarity inversion was preserved correctly. However the clause that was deliberately left correct — `بيطلع اداؤه وحش قوي` (its performance comes out very bad) — was emitted as `يظهر أداءه قويًا` (its performance appears strong). The model inverted a proposition it was not asked about, in the direction of neither truth nor the input.

This is neither a failure to preserve an injected error nor an unauthorized addition, so both gate columns record YES and the case passes. The gate cannot currently detect unforced distortion of a proposition that carries no injected error. Registered as a gate design gap, not as a case verdict.

Separately, SG-15 claim 3 contains the CJK character `释` embedded in Arabic text (`أن ي释ع الريسورس`). Character corruption of this kind was the stated basis for rejecting `llama-3.1-8b-instant` in D87 (Cyrillic characters in SG-07). It is recorded here as a first occurrence in the approved model, not yet as a pattern.

### 5 — Structural defect: the glossary was never in the gate path

`scripts/llm_decomposition_sanity_gate.py` calls `decompose_via_llm` and records its output directly. It does not call `apply_glossary`. Evidence: `raw_results.json` records exactly one `claims` field per case; `report.md` contains no reference to the glossary or to transliteration; and `الديدلوك`, `السيستم`, `الابليكيشن` — all three verified IN_GLOSSARY during D99 §4 — appear unconverted in the SG-15 output.

Consequences, recorded rather than worked around:

- **D97 criterion 3 was not measured.** It specifies a verdict on POST-glossary output. No post-glossary output exists in this run. All transliteration verdicts for SG-10, SG-12 and SG-15 are therefore **VOID, not FAIL**.
- **D97 criterion 6 is unmet.** It requires the gate to record both raw and post-glossary claims so that failures are attributable to a component.
- **Component (a), closed in D98, has never been exercised by a gate.** The D99 §4 registered expectation about `Data سيت` was not tested.
- **The D99 §7 attribution rule is inapplicable as written**, since its third row has no measurement behind it.

The raw-claims observation stands independently of this defect and is recorded as an observation, not a criterion verdict: under v3's downgraded constraint 3 the model **translated** technical terms into Arabic words rather than leaving them transliterated — `النويز`→`الضوضاء`, `الباترن`→`النمط`, `الداتا سيت`→`مجموعة بيانات`, and in SG-03 `patterns`→`الأنماط` from Latin script in the input. Translation destroys the term and, unlike an unconverted transliteration, cannot be repaired by extending the glossary. Whether this survives the glossary layer is unknown and unmeasurable until §5's defect is fixed.

### 6 — What is deliberately not decided here

No prompt v4. No re-instatement of the numeric rule. No model replacement. Each would be a change decided on a single uncontrolled run against a gate that was not measuring one of its three criteria. The remedy sequence is: fix the gate wiring first, then run the controlled comparison pre-registered as D101, then decide.

### 7 — Correction to D99

D99 §1 recorded two §5.13 violations. A third belongs with them: during adjudication of this run Claude asserted a regression relative to D92 before establishing that decoding was greedy. The claim later held once `temperature: 0` was verified at `client.py:129`, but it was made ahead of its evidence.

---

## D101 — Glossary wiring into the gate path + prompt v4 (principle + five explicit preservation rules) (2026-07-27)

**Status:** PRE-REGISTERED before execution. Registered at HEAD 628b8f0 (D100).

**Source-verified findings (read from disk this session, not asserted):**
(a) scripts/llm_decomposition_sanity_gate.py calls decompose_via_llm and writes result.claims
    directly into raw_results.json with no intervening transformation. apply_glossary has zero
    call sites in that script.
(b) The production orchestrator evaluate_answer() calls apply_glossary(claims) at
    src/interview_iq/pipeline.py:197, immediately after decomposition.
Therefore the sanity gate has never exercised the production path.

**Consequence for prior records:** every transliteration_correct verdict recorded in D96 and
D100 was measured on an execution path that structurally could not produce the artifact being
judged. Those transliteration verdicts are marked NON-EVIDENTIARY (D78/D79 VOID precedent).
The error_preserved and no_unauthorized_addition verdicts in D96 and D100 are unaffected and
remain valid.

**Constraint 3 is not changed by this decision.** Constraint 3 downgrades transliteration to
best-effort on the stated rationale that a deterministic glossary is applied downstream. In the
gate path that premise was false. Wiring (a) makes the stated premise true; the constraint text
stands.

**Non-conflation clause:** finding (a) explains none of the four D100 error-preservation
failures (SG-01, SG-09, SG-10, SG-15). The glossary substitutes recognised Arabic forms with
Latin terms; it cannot restore an altered proposition. Prompt v4 is the sole intervention
targeting those four.

**Known adverse interaction, registered before the run:** in SG-01 the model emitted الهاش where
the speaker uttered الهيب. Once the glossary runs, a fabricated-but-recognised form is converted
to a clean Latin term, making entity substitution LESS visible in the final artifact. Judging
error preservation on post-glossary claims would be a strictly weaker test than D92/D96/D100
applied.

**Judgment surface (pre-registered; may not be revised after results are seen — P48):**
Each gate record shall carry:
  claims_raw            — LLM output, before apply_glossary
  claims_final          — after apply_glossary
  transliteration_audit — the audit dict returned by apply_glossary
Criteria bind as follows:
  error_preserved          → judged on claims_raw   (comparable with D92/D96/D100)
  no_unauthorized_addition → judged on claims_raw
  atomicity_verdict        → judged on claims_raw   (non-blocking, unchanged)
  transliteration_correct  → judged on claims_final (first evidentiary measurement in project)

**Schema change:** the record key "claims" is removed and replaced by claims_raw and
claims_final. Runs recorded before D101 keep the old key and are not migrated. A new empty
verdict column transliteration_correct is added; it did not previously exist as a column, and
D96/D100 transliteration verdicts were recorded in prose only.

**Prompt v4:** constraints 1–8 of v3 are retained verbatim. Five explicit hard preservation
rules are added as named sub-rules of constraint 1, covering the classes with observed or
anticipated failures: numeric (1a), order (1b), polarity and comparison direction (1c), causal
direction (1d), entity name (1e), each closing with a statement that they illustrate the
Principle and do not replace it, and that unlisted classes remain governed by constraint 1 in
full.

**Relation to D96:** D96 prohibited REPLACING the general principle with a per-failure patch.
v4 does not replace it; the principle and the operational test are retained unchanged and the
explicit rules sit beneath them. Evidence basis: the numeric class carried an explicit rule
under D90 and passed 9/9 in D92; that rule was removed in v3 and the class regressed to FAIL in
D100 (SG-09). No case in the record supports the principle alone being sufficient.

**Anti-overfitting condition:** no illustrative example added by v4 may reuse the content of any
fixture in the gate fixture file. Verified by explicit string check before commit.

**Success criteria (pre-registered).** One gate run, 15 cases, Groq llama-3.3-70b-versatile, on
the commit implementing this decision.
  PASS requires error_preserved in {YES, N/A} on all 15 AND no_unauthorized_addition = YES on
  all 15. Zero tolerance, unchanged from D77.
  transliteration_correct is recorded and reported for all applicable cases but is NON-BLOCKING
  for this run only, being the first evidentiary measurement of a newly wired deterministic
  component: it establishes a baseline. A poor result on it opens a decision about the glossary,
  not about the model.
  atomicity_verdict remains non-blocking.

**Stop rule (binding):**
  v4 PASSES  ⇒ the decomposition module is CLOSED; work moves to Q10.
  v4 FAILS   ⇒ immediate model replacement under the D77 gate procedure. No v5. No sixth patch.
  Replacement model also FAILS ⇒ work stops and the limit is documented as a measured
  limitation, supported by the pre-registered gate, 15 fixtures, and the D77–D101 record.

**Out of scope, unchanged:** D89-b remains HARD-GATED on a full gate PASS. F3, G4, Q2, Q7, G3,
Q10, G1, and the Gold naming collision are untouched by this decision.

---

## D102 — First empirical measurement of the deterministic glossary layer on runtime output (2026-07-28)

**Status:** PRE-REGISTERED before execution. Registered at HEAD `46384b9`. NON-GATING: this is a measurement, not a pass/fail gate, and no architectural decision is conditioned on the resulting figure.

### 1 — Motivation

The GAP-3b provenance audit (conducted at HEAD `46384b9`) established that `apply_glossary` has been called unconditionally in the runtime chain at `src/interview_iq/pipeline.py:197` since `ccafc91` (D97), but that no committed result artifact was produced after that commit. All four existing `results/pipeline_demo/*.json` artifacts predate the glossary's existence in `pipeline.py`. The layer's effect on real runtime output has therefore never been measured, and no figure characterising it exists.

### 2 — Instrument

`kaggle/runners/run-pipeline-demo.ipynb`, executed on Kaggle T4 under the thin-runner pattern. Inputs: Kaggle dataset `iq-audio-pilot` — `answer_correct.mp3` (SE-028) and `answer_wrong.mp3` (GN-040). Zero-shot on both channels (D89 runtime default; no `--adapter-path`). Outputs: `results/pipeline_demo/SE-028_v3.json` and `results/pipeline_demo/GN-040_v3.json`. The `_v2` artifacts are retained unmodified as the sole surviving evidence of pre-glossary behaviour and must not be overwritten.

### 3 — Measurement surface

The comparison is `claims_raw` against `claims` WITHIN each single run. This isolates the glossary: same audio, same ASR output, same prompt, same LLM call — the only transformation between the two fields is `apply_glossary`.

Explicitly excluded: any `_v2` against `_v3` comparison. Two variables changed between those commits (introduction of the glossary AND prompt v4), so that comparison is confounded and will not be used as evidence of glossary effect.

### 4 — Pre-registered expectations

1. Output is expected to be MIXED (partly Latin script, partly Arabic script), not fully converted. A mixed result is the expected outcome, not a failure.
2. Terms classified ABSENT are expected to be predominantly orthographic variants of registered forms rather than concepts missing from the glossary. This is the pattern already documented for SG-14 (3 IN_GLOSSARY, 1 PARTIAL, 7 ABSENT).
3. A multi-word matcher defect is expected to surface: compound forms may be partially converted (registered pattern: `الداتا سيت` → `Data سيت`). Its occurrence confirms a known defect and does not invalidate the run.

### 5 — Pre-registered defect criteria

The following indicate a fault in the layer rather than an expected limitation:

- `len(claims_raw) != len(claims)`. The glossary performs substitution only; claim count MUST be preserved. Any divergence is a defect.
- Any claim whose asserted content changes meaning after substitution.
- Any Latin form appearing in `claims` that is not a registered glossary form, which would indicate invention rather than lookup.

### 6 — Reported figure

Conversion rate: number of technical terms converted over number of technical-term occurrences detected, derived from `transliteration_audit`, reported per question and pooled across the two questions. With n=2 questions the figure is DIRECTIONAL, NOT STATISTICAL, and is reported as raw counts rather than percentages.

### 7 — Scope limits

- Does not supersede D82/D83. Those Coverage figures were produced by `scripts/coverage_channel_real_claims_experiment.py`, which has never contained a glossary call site at any commit in its history; they remain pre-glossary figures and must be labelled as such in the paper.
- Does not address F3. F3 was diagnosed on a pre-glossary artifact; whether it persists must be re-checked against `SE-028_v3.json` under a separate entry.
- Does not close the open item that `kaggle/runners/run-sanity-gate.ipynb` cell `sg05verify` treats an empty `EXPECTED_COMMIT` as a warning rather than a hard failure.
- Does not close the open item that D101 carries no `## Changelog (condensed)` line.

---

## D103 — Outcome of D102: glossary layer measured; four findings recorded (2026-07-28)

**Status:** OUTCOME. Registered against the pre-registration in D102. Executed at commit `e7bc9fa` on Kaggle T4, verified by the notebook's commit guard. No remedy is applied under this entry.

### 1 — Execution record

Both runs returned `status: SUCCESS`. Artifacts: `results/pipeline_demo/SE-028_v3.json` and `results/pipeline_demo/GN-040_v3.json`, committed immediately before this entry. Configuration as pre-registered: `llama-3.3-70b-versatile` decomposition, `nli_adapter_path: null` (zero-shot, D89 default), ASR `large-v3`. These are the first artifacts in the project produced by a pipeline containing the glossary layer.

The notebook's commit guard confirmed the cloned commit as `e7bc9fa`. A first execution attempt failed at the audio conversion cell with `AudioSegmentationError: Video file not found`, because the Kaggle dataset had not yet been attached to the session. No artifact was produced and no measurement occurred, so that attempt is not recorded as a VOID run. The dataset was then attached and the notebook executed as committed, with no in-session code modification.

### 2 — Glossary layer: all D102 §5 defect criteria passed

| Criterion | SE-028 | GN-040 |
|---|---|---|
| `len(claims_raw) == len(claims)` | 6 = 6 | 5 = 5 |
| Meaning drift after substitution | none | none |
| Invented Latin form | none | none |
| `residual_ambiguous_count` | 0 | 0 |

Substitutions: SE-028 = 7 (`التست`→`Test` ×3, `الكود`/`كود`→`Code` ×4). GN-040 = 5 (`البيت`/`بت`/`بيت`→`bit` ×5). Total 12 substitutions across 3 distinct terms.

D102 §4 expectation 1 (mixed output) confirmed. Expectations 2 and 3 were not exercised: no ABSENT classification and no multi-word compound occurred in this input.

In support of D98's human-adjudication stance: `بيت` was substituted to `bit` in all five GN-040 occurrences, including inside `مجموعة من 16 بيت`, where `bit` is the contextually correct reading rather than `byte`. The closed-domain assumption held on this input. n=2; directional, not statistical.

### 3 — F4: non-Arabic, non-Latin script emitted by the approved model

`claims_raw` contains characters from neither script:

- SE-028 claim 2: `тест` (Cyrillic), present in `claims_raw` before any glossary processing.
- GN-040 claim 2: `故` (CJK).

This is the same failure class that disqualified `llama-3.1-8b-instant` under D87 (Cyrillic characters in SG-07). It is now observed in `llama-3.3-70b-versatile`, the approved model, which passed the D77 sanity gate 8/8. The gate's fixtures did not elicit this class; real ASR input did.

Both tokens are semantically correct substitutions in the wrong script, not random corruption: `тест` is the Russian word for *test*, and `故` is the Classical Chinese connective for *therefore*, occupying the position of Arabic `لذلك` in the sentence. This is cross-lingual token substitution, a known failure mode in multilingual decoders. It follows that detection does not require semantic analysis: a script whitelist (Arabic, Latin, digits, punctuation) would flag every instance of this class. No such check exists in the pipeline.

The glossary cannot mitigate this: lookup matches registered forms, and a Cyrillic form is not registered.

Note also that NLI scored the Cyrillic-bearing claim VERIFIED at `max_e = 0.998747`. mDeBERTa is multilingual and appears to have processed the Russian token correctly. The score was therefore not degraded — but this is undocumented, unintended behaviour, not a designed property.

No remedy is registered here. Whether this warrants a new gate class, a model re-evaluation, or an output-validation layer is deferred.

### 4 — F5: knowledge injection and reasoning leakage under prompt v4

GN-040 `claims_raw` index 2, verbatim:

> `الـ Byte يتكون من 8 بت، وليس 16 بت كما ذكر، ولكن هذا ما قيل،故 سوف أتركه كما هو: الـ Byte هو مجموعة من 16 بيت.`

The model corrected the candidate's factual error (16 → 8), commented on the correction, leaked its own deliberation, then restored the original assertion. The injected error is preserved in the final position, so `error_preserved` would score YES under the D77 gate criteria, but the claim now carries the correct answer inside it.

This violates the anti-knowledge-injection principle that is the substance of prompt v3 (D99) and preservation rules 1a–1e (D101). It is the first observation of prompt v4 behaviour on real ASR input rather than on gate fixtures.

Consequence for scoring: the claim was judged CONTRADICTED at `max_c = 0.999063` against `GN040-C03`. The NLI judgment was made on mixed text containing both the wrong and the correct proposition, so the verdict cannot be attributed cleanly to the candidate's answer.

### 5 — F6: the D102 §6 figure is not computable from the instrument

D102 §6 pre-registered a conversion rate: converted terms over technical-term occurrences detected. `transliteration_audit` records substitutions only; it emits no record of terms that were detected and not converted. The numerator exists (7 and 5); the denominator was never instrumented.

Recorded as a measurement-design defect, not corrected retroactively. Only raw substitution counts are reportable from this run. This is consistent with D102 §6's own instruction to report raw counts rather than percentages, but the rate itself is unavailable. Any denominator would require instrumenting the matcher and re-running.

### 6 — F7: the layer's scope is wider than D102 §5 describes

D102 §5 characterises the glossary as performing "substitution only". Comparison of `claims_raw` to `claims` shows orthographic normalisation is also applied: `أصغر`→`اصغر`, `تُسمى`→`تسمى`, `الـ Byte`→`ال Byte` (tatweel removal), with hamza and diacritic stripping throughout.

No meaning drift resulted, so no D102 §5 criterion is breached. However, the description of the layer in D102 and in any external document is incomplete and must be corrected before publication.

### 7 — Observation, not a finding: CONTRADICTED verdict on a correct claim

SE-028 claim 4 (`تحسن وتنضف Code دون تغيير سلوكه`) received CONTRADICTED at `max_c = 0.999570` despite `max_e = 0.882707`. The proposition is correct with respect to TDD.

This resembles the F3 pattern (false CONTRADICTED on Arabic paraphrase structure). It is NOT registered as the same instance: the decomposition differs from the pre-glossary run, so claim indices are not comparable across artifacts. Recorded as an independent observation for F3's separate investigation.

### 8 — Scope limits

- Does not supersede D82/D83; those remain pre-glossary figures.
- Does not resolve F3, F4, F5, F6, or F7. Each requires its own registered decision.
- Does not close the `sg05verify` `EXPECTED_COMMIT` warning-vs-failure gap.
- Does not close the absence of a changelog line for D101.
- D89-b remains HARD-GATED on a full gate PASS.

---

## D104 — D101 v4 gate outcome: FAIL — ordering class survives a third prompt version; first transliteration measurement (2026-07-29)

**Run:** Kaggle sanity-gate thin-runner, run_20260729T192145Z, commit fc1925c5fd2780ad69d8bcef6082ef20ad37c21f, Groq llama-3.3-70b-versatile, 15/15 executed, 0 API errors. EXPECTED_COMMIT guard armed and did not fire. Dual judgment surface per D101: error_preserved and no_unauthorized_addition judged on claims_raw; transliteration_correct on claims_final. Human judgment: Ahmed.

**Verdicts — error_preserved:**
- SG-01 YES. The D100 entity-substitution regression is fixed: الهيب is preserved in all five claims (v3 emitted الهاش).
- SG-02..SG-08 YES, unchanged.
- SG-09 YES. The D100 numeric regression is fixed: alpha 0.5 preserved in claims 0 and 1 (v3 emitted 0.05).
- SG-10 **NO**. Input states code first then test; claims 0 and 1 state test before code. A silent reversal to the correct TDD order. This class has now failed under prompt v2 (D96), v3 (D100) and v4 (this run), the last of which contained an explicit ordering rule (1b).
- SG-11 YES. 16 and the speaker's own "وليس من 8" carried verbatim, no added commentary. P1 holds.
- SG-12, SG-13 N/A per fixture designation. SG-13 invented no name; P5 holds.
- SG-14 YES under its pre-registered criterion: the negation survived (دون حفظ الضوضاء). Recorded again, as in D100 §4: the deliberately-correct final clause was distorted — the speaker's اداؤه وحش قوي (very bad) became اداءه بشكل قوي (strong). This is Egyptian-dialect misparse of قوي as an adjective rather than an intensifier, not knowledge injection; it does not meet this fixture's failure condition but is a measured meaning-distortion defect.
- SG-15 YES. The D100 causal-direction regression is fixed: الديدلوك هو السبب في is preserved (v3 emitted يحدث عندما).

**no_unauthorized_addition = YES on 15/15.** No Coffman conditions in SG-15, no recall in SG-04, no LEFT JOIN in SG-06, no invented cycle name in SG-13.

**Gate verdict: FAIL** (SG-10, zero tolerance per D77).

**Net effect of prompt v4:** three of the four D100 failures were repaired (entity, numeric, causal direction) by adding explicit rules 1a–1e beneath the retained general principle. One class was not. Five prompt versions across D90, D95, D97/D99, D101 have not eliminated silent correction of the ordering class.

**Transliteration baseline — first evidentiary measurement in the project (non-blocking for this run per D101).** Substitution fired correctly in nine cases (Heap, LIFO, Process, Thread, Classification, Precision, JOIN, Rebase, Branches, Commit, Merge, Test, Code, TDD, Deadlock, Application). Four defects measured:
- T1 (SG-11, severe) The AMBIGUOUS near-homograph بيت was substituted to bit at every occurrence including those denoting Byte, so claim 2 reads "bit الكبير يتكون من 16 bit، وليس من 8". The bit/byte distinction the fixture exists to test is destroyed, and residual_ambiguous_count is 0 — the ambiguity was silently resolved, not flagged. This is the cost side named and accepted in D98, now observed destroying fixture content. It requires its own decision.
- T2 (SG-02) The matched form والثريد consumed the conjunction, producing "الفرق بين Process Thread". Word-boundary matching does not exclude the proclitic waw.
- T3 (SG-01, SG-10) The multi-word defect predicted in D99 is confirmed: الداتا ستركتشر → Data ستركتشر, and الداتا بيز → Data.
- T4 (SG-15) F4 (D103) reproduced inside the gate: claim 2 contains a CJK character, ي释ع. Cross-lingual token substitution is not confined to real-audio input.
- Also confirmed in-gate: F7 (D103) — the layer strips hamza/alef diacritics throughout (اخر, اامن, اداء), i.e. it performs orthographic normalisation beyond substitution.
- SG-14 recorded 0 substitutions, matching the D99 registered exception (0 of its 11 forms are IN_GLOSSARY).

**Consequence — binding stop rule from D101 fires:** v4 FAILED, therefore model replacement proceeds under the D77 gate procedure. No prompt v5. Pre-registered as D105.

**Barriers unchanged:** D89-b remains HARD-GATED on a full gate PASS. F3, G4, Q2, Q7, G3, Q10, G1 untouched.

---

## D105 — Model replacement: D77 amended for reasoning models; fixed candidate ladder (pre-registered) (2026-07-29)

**Status:** PRE-REGISTERED. Outcome registered separately per candidate.

**Trigger:** D104 gate FAIL fires D101's stop rule. The decomposition module's failure is a model behaviour, not a prompt defect: five prompt versions repaired four error classes and left one.

**Amendment to D77 (reasoning models).** D77 barred reasoning models after nemotron leaked chain-of-thought into the output (D76). The bar was empirical, not principled. It is amended: a reasoning model MAY be evaluated, subject to Criterion 0 below. If Criterion 0 fails, the candidate is rejected on D77 grounds and its run is recorded as non-evidentiary for the preservation criteria — not as a FAIL, since leaked reasoning invalidates the output surface rather than testing it.

**Live model inventory (verified this session via GET https://api.groq.com/openai/v1/models, not from memory):** openai/gpt-oss-120b, openai/gpt-oss-20b, openai/gpt-oss-safeguard-20b, qwen/qwen3.6-27b, allam-2-7b, llama-3.3-70b-versatile, llama-3.1-8b-instant, groq/compound, groq/compound-mini, plus whisper/orpheus/prompt-guard models. Excluded from candidacy: audio and guard models (wrong task); groq/compound and compound-mini (agentic, tool- and search-enabled — non-deterministic for this task); llama-3.1-8b-instant (rejected D87, fabricated claim on SG-01, Cyrillic characters on SG-07 — not re-tested without a decision superseding D87); llama-3.3-70b-versatile (the incumbent under replacement).

**Candidate ladder — order fixed before any run, and not to be reordered after seeing a result:**
1. openai/gpt-oss-120b
2. allam-2-7b
3. qwen/qwen3.6-27b
Rationale recorded before execution: the observed failure is instruction adherence under a competing knowledge prior, so the largest instruction-tuned candidate is tried first; allam-2-7b is Arabic-native, which is directly relevant to dialect-to-MSA normalisation, and is non-reasoning; qwen3.6-27b is a hybrid-thinking fallback.

**The only variable that changes is GROQ_MODEL.** Verified this session: client.py:47 reads it from the repo-root .env at import; scripts/llm_decomposition_sanity_gate.py has no override and no model logic of its own. Therefore for each candidate the ONLY change is the model id written into .env by the gate notebook's credentials cell. No change to system_prompt.md, sg_cases.json, the gate script, transliteration.py, or the glossary. No request-parameter changes: reasoning_effort and response_format are NOT set for these runs. Any such change would confound the comparison and must be its own pre-registered decision.

**Criteria per candidate, one gate run of 15 fixtures each:**
- Criterion 0 (new, D77 amendment): no chain-of-thought, analysis channel, or reasoning preamble appears in any claim. Judged first, by human inspection of claims_raw. Failure ⇒ candidate rejected, run non-evidentiary for criteria 1–3.
- Criterion 1: error_preserved in {YES, N/A} on all 15. Zero tolerance, unchanged from D77.
- Criterion 2: no_unauthorized_addition = YES on all 15. Zero tolerance.
- Criterion 3: transliteration_correct recorded, NON-BLOCKING — it measures the glossary, which is identical across candidates.
- atomicity_verdict tracked, non-blocking.
- Execution errors: if n_error > 0, the run is VOID for that candidate and is rerun once before judgment.

**Stop rule (binding, replaces D101's):** the first candidate to satisfy Criteria 0–2 is adopted as GROQ_MODEL and the decomposition module is CLOSED; D89-b unblocks immediately. If all three candidates fail, work on this module stops and the limit is documented as a measured limitation supported by the D77–D105 record, 15 fixtures, five prompt versions and four models.

**Out of scope, unchanged:** D89-b remains HARD-GATED until a candidate passes. F3, G4, Q2, Q7, G3, Q10, G1 untouched. T1 (the SG-11 AMBIGUOUS-substitution defect from D104) is registered as an open item and is NOT addressed by this decision — the glossary is held constant across candidates.

---

## D106 — Model replacement outcome: openai/gpt-oss-120b PASSES the gate; decomposition module CLOSED (2026-07-29)

**Candidate 1 of the D105 ladder. Two runs:**
- run_20260729T201635Z — **VOID, non-evidentiary.** n_error=1: SG-13 returned Groq HTTP 429, tokens-per-minute limit (Limit 8000, Used 7197, Requested 2699). Per D105 the run was voided and rerun once. Recorded rather than discarded (D78/D79 precedent). Note that SG-13 is the P5 invented-name test, so the class that mattered most was precisely the one unavailable.
- run_20260729T204855Z — **EVIDENTIARY.** model_used=openai/gpt-oss-120b, git_commit=eb16b3bd79c252f6b647afa5bb61369a23bcc60a, n_cases=15, n_success=15, n_error=0. EXPECTED_COMMIT guard armed and did not fire.

**Only variable changed relative to D104: GROQ_MODEL.** system_prompt.md (v4), sg_cases.json (15 fixtures), the gate script, transliteration.py and glossary v2 are unchanged; verified by an empty git diff --stat across those five paths and no edits to them since. No request-parameter changes: reasoning_effort and response_format were not set.

**Verdicts (human judgment, Ahmed):**
- **Criterion 0** (D77 amendment, no reasoning leakage): **PASS.** No chain-of-thought, analysis channel or reasoning preamble in any claim across all 15 cases. The amendment's condition is satisfied for this model.
- **Criterion 1 (error_preserved): YES on 14, N/A on SG-12, zero NO.**
  - SG-10 (ordering) preserved — claims state code first, then the test. This class had failed under prompt v2 (D96), v3 (D100) and v4 (D104) with llama-3.3-70b-versatile, the last of which contained explicit rule 1b. The failure was a model property, not a prompt defect, as D105 hypothesised.
  - SG-15 (causal direction) preserved — deadlock stated as the cause of the threads holding resources.
  - SG-14 (polarity) preserved, and the dialect distortion recorded twice previously (D100 §4 and D104, where اداؤه وحش قوي became strong performance) did not recur: rendered سيئا جدا.
  - SG-01 (entity) preserved, SG-09 (numeric 0.5) preserved, SG-11 (16 not 8) preserved, SG-03/05/07/08 preserved.
  - Judgment note, ruled non-failing: SG-11 claim 2 supplied the elided unit (وليس من 8 بيت where the speaker said مش من 8). The asserted quantity and the negation are verbatim; this is ellipsis completion, not knowledge injection.
- **Criterion 2 (no_unauthorized_addition): YES on 15/15.** No recall in SG-04, no LEFT JOIN in SG-06, no invented cycle name in SG-13, no Coffman conditions in SG-15.
- **Criterion 3 (transliteration, non-blocking):** substitution fired in six cases (Heap, Rebase, Branches, Commit, Merge, Code, JOIN). T1 from D104 recurred unchanged: SG-11's AMBIGUOUS form بيت was substituted to bit at every occurrence, so the bit/byte distinction is destroyed post-glossary. Open item; the glossary was deliberately held constant across candidates.
- **atomicity:** finer decomposition than D104 on SG-05, SG-13 and SG-15. Non-blocking, not a criterion.

**GATE VERDICT: PASS.**

**Consequences under the D105 stop rule:**
- openai/gpt-oss-120b is ADOPTED as GROQ_MODEL for claim decomposition, superseding llama-3.3-70b-versatile (D86/D87). Ladder candidates 2 and 3 (allam-2-7b, qwen/qwen3.6-27b) are not run.
- The decomposition module is CLOSED.
- **D89-b is UNBLOCKED.** The hard gate registered in D89 and reaffirmed through D96, D98, D100, D101, D104 and D105 is satisfied. Corpus generation for the fine-tuning repair experiment must use prompt v4 with openai/gpt-oss-120b and must be pre-registered before any training run.

**New behavioural finding, registered not resolved (F8):** the adopted model's term rendering differs from the incumbent's. It emits some English technical terms directly in Latin script (data structure, LIFO, precision, threads, resources, deadlock, application) while translating others into formal Arabic (الضوضاء for النويز, مجموعة البيانات for الداتا سيت). Fewer Arabic-transliterated surface forms therefore reach the glossary and substitution counts fall. The effect on NLI matching against Latin-bearing reference chunks is unmeasured and warrants its own experiment before any claim is made about it.

**Free-tier operating constraint, measured from the 429 response body rather than documentation:** openai/gpt-oss-120b on the on-demand tier is capped at 8000 tokens per minute, below the 12000 available to the incumbent. A single 15-case gate run can exhaust it. Future multi-case batches must pace requests or expect VOID runs. Not fixed under this entry.

**Known infrastructure issue:** the Kaggle notebook is not synchronised with its repo copy — a stale saved session ran with the previous GROQ_MODEL and required manual correction before the evidentiary run. Candidate fix: read the model id from a repo config file fetched by the clone instead of hardcoding it in a notebook cell. Registered, not fixed.

**Barriers status:** D89-b UNBLOCKED. Open: F3 (NLI false contradiction), T1 (glossary AMBIGUOUS substitution), F4–F7 (D103), F8 (this entry), G4, Q2, Q7, G3, Q10, G1.

## D107 — D89-b Step 0: re-derive the Coverage baseline on the production pipeline (pre-registered) (2026-07-29)

**Status:** PRE-REGISTERED. Instrument built under this entry; the run and its outcome are registered separately as D108.

**Two debts closed by one run.**
(i) D82 was executed on 22 July but its result entry was deferred pending a clean rerun after two defects were fixed (provider null-content, English-language claims). That rerun never happened, so no D83 heading exists; the figures "adapter worse than zero-shot in 19/19, mean Coverage 0.180 vs 0.395" are cited in D89, the defence deck and the manuscript draft with no artifact in this repository and no registered outcome entry. The only recoverable Kaggle artifact is run 20260722T071215Z, which is a total failure (25/25 OpenRouter HTTP 429, free-models-per-day limit 50 — the measurement that motivated D86) and contains no Coverage figures. Committed under this entry as evidence for D86, not as a Coverage result.
(ii) D89's binding reopening condition requires any new adapter to beat zero-shot on BOTH channels, evaluated on the D88 diagnostic set plus an O9 sample. A current zero-shot Coverage baseline on the production pipeline does not exist. This run produces it.

**Documentation consequence, effective immediately:** the figures 0.180 / 0.395 / 19-of-19 must be marked "pending re-derivation (D107)" wherever they appear in presentation or manuscript material until D108 supersedes them. They were obtained on a defective run, on a superseded decomposition model (cohere/north-mini-code:free), and before the glossary existed. They are not retracted as measurements; they are unsupported as current figures.

**Instrument changes required (built under this entry, before the run):**
- C1 Glossary wiring. scripts/coverage_channel_real_claims_experiment.py has no apply_glossary call site and never had one; its Coverage figures are therefore pre-glossary by architectural necessity, while production applies the glossary before NLI (pipeline.py:197). The script is wired to record both claims_raw and claims_final, following the D101 pattern including hard failure (RuntimeError, no silent fallback) if apply_glossary raises.
- C2 Pacing and resume. openai/gpt-oss-120b is capped at 8000 tokens per minute on the free tier (measured in D106). 25 decompositions at roughly 2500 tokens each permits about three calls per minute. The script gains: a per-question checkpoint written to disk immediately after each question, a --resume flag that skips questions already present in the checkpoint, and a configurable inter-call delay defaulting to 20 seconds. Without these a single 429 discards the whole run.
- No other change. The prompt, the fixtures, the glossary data, the NLI engine, metrics and aggregation are untouched. GROQ_MODEL is supplied by the environment; the script has no model logic of its own.

**Design — four arms, no additional API cost.** Decomposition runs once per question; both NLI arms and both claim surfaces are then evaluated locally. Arms: {zero-shot, adapter checkpoint27} × {claims_raw, claims_final}. Rationale registered before execution: zero-shot × claims_final is the production baseline and the reference for D89-b; adapter × claims_raw re-derives the previously published figure on a comparable surface; the raw-versus-final contrast measures the glossary's effect on the Coverage channel directly, which is finding F8 from D106.

**Sample:** the same 25 O9 questions (results/o9_sample_selection.json, D50), key_points taken from reference_docs_250_FINAL_v1.json, not the O9 manual reference claims — the D44 self-consistency trap, unchanged from D82.

**Pre-registered analysis and limits:**
- n=25 ⇒ directional, not statistical. Thresholds remain PRE-CALIBRATION DEFAULT; G4 is not unblocked by this run.
- Report per arm: mean Coverage, per-question Coverage, and the count of questions where each arm is higher.
- Decomposition failures are reported as failures; any question whose decomposition errors is excluded from all four arms and counted explicitly. If more than 5 of 25 fail, the run is VOID and rerun once, as in D105.
- This run does NOT evaluate any new adapter. It establishes the baseline that a future adapter must beat. D89-b's acceptance criteria for the new adapter will be pre-registered in their own entry before any training run, per D89's binding wording: "an adapter that outperforms zero-shot on BOTH channels, evaluated on the D88 diagnostic set plus an O9 sample, with acceptance criteria written and committed BEFORE the training run."

**Out of scope, unchanged:** F3, T1, F4–F8, G4, Q2, Q7, G3, Q10, G1.

## D108 — D107 outcome: Coverage baseline re-derived; published figures superseded; glossary effect on Coverage measured as negligible (2026-07-30)

**Run:** results/coverage_channel_real_claims/run_20260730T073157Z, commit 1f9a68c6686125496e2680848cd28aa361bf296e, decomposition openai/gpt-oss-120b (D106), prompt v4, glossary v2 applied, adapter checkpoint27 from the published Kaggle Model. 25/25 decompositions succeeded, 0 failures, all four arms scored on all 25 questions. Thresholds PRE-CALIBRATION DEFAULT (tau=0.5, tau_E=0.9, alpha=0, k=10). Judgment: Ahmed.

**Both D82 defects are gone.** The 22 July run had 6 of 25 decomposition failures (provider null-content) and 8 of 19 successes emitting English claims. This run: 0 failures, no language defect. D82's deferred registration debt is closed by this entry; no D83 heading is created retroactively, and D82 remains a pre-registration only.

**Four-arm result (mean Coverage over 25 questions):**
- zero_shot_raw 0.2888 (median 0.2823, min 0.002, max 0.868)
- zero_shot_final 0.2928 (median 0.3063, min 0.002, max 0.884)
- adapter_raw 0.1187 (median 0.0514)
- adapter_final 0.1211 (median 0.0606)

**Finding 1 — the architectural conclusion holds, the published numbers do not.** zero_shot_final exceeds adapter_final on 23 of 25 questions. The direction that justified D89 (zero-shot as the runtime arm for both channels) is reproduced independently: a different decomposition model, a different prompt version, and the glossary in place. However the previously cited figures — mean 0.395 versus 0.180, adapter worse in 19 of 19 — are NOT reproduced. Both means are lower and the win rate is 92 percent, not 100 percent. Those figures are superseded by this entry and must be replaced wherever they appear in the deck or manuscript. They are not retracted as measurements; they were obtained on a defective run with a superseded model and are simply not the current numbers.

**Documented exceptions (2 of 25):** GN-012 (zero_shot_final 0.002 vs adapter_final 0.006) and GN-042 (0.002 vs 0.006). Both arms are effectively at floor on these two questions and the margin is 0.004; the reversal is not evidence of adapter advantage, but it is recorded rather than rounded away, because the previously published claim of 19-of-19 with no exceptions is exactly the kind of absolute statement this project does not make without support.

**Finding 2 — F8 measured: the glossary does not improve the Coverage channel.** zero-shot mean rises from 0.2888 to 0.2928, a change of +0.004. Per question it raised Coverage on 13 and lowered it on 12. The effect is noise at this sample size, not improvement. This does not invalidate the glossary: its registered purpose (D97/D98) is deterministic transliteration, and D106 measured it performing that function (Heap, Rebase, Code, JOIN substituted correctly). The finding is narrower and more useful: the Coverage channel's weakness is not caused by Arabic-rendered technical terms, so it must be sought elsewhere (F3, chunk quality, thresholds). Registered as a negative result with a diagnosed scope.

**Finding 3 — Coverage is low in absolute terms, and this is now the primary open weakness.** Mean 0.293, median 0.306, with floor cases (DA-002 0.007, GN-012 0.002). No question scored exactly 0, so the harmonic merge is not nullified anywhere in this sample, but a channel averaging below 0.30 on correct-answer material is the dominant limitation of the scoring engine as configured. This is an input to G4 (threshold calibration) and is registered as an open item in its own right, not attributed to any single cause on present evidence.

**Note on D42's OOD hypothesis:** key_point_count is 3 for 21 of the 25 questions (2 for three, 4 for one), so the correlation between Coverage and key-point count that D42 hypothesised cannot be tested on this sample. Recorded as untestable here, not as absent.

**Baseline established for D89-b.** Any retrained adapter must be compared against these figures on this sample, plus the D88 diagnostic set for the Precision channel, per D89's binding reopening condition. The reference value the new adapter must beat on Coverage is zero_shot_final = 0.2928 (mean over 25 O9 questions, glossary applied, prompt v4, gpt-oss-120b). D89-b's own acceptance criteria are still to be pre-registered in their own entry before any training run.

**Open items after this entry:** low Coverage (new, this entry), F3, T1, F4-F8, G4, Q2, Q7, G3, Q10, G1.
