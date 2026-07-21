# decisions.md — Interview IQ / Unified Decision Log (D1–D81)
**Version:** v3.0 — 21 July 2026 (English migration + reorganization, see D81)
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

### D67 — Gold Corpus v2 repair + ASR→decomposition input-contract freeze (✅ BLOCKED AT PHASE 0 / NO CORPUS MODIFICATION)
- Phase 0 verified 222 examples / 1,836 claims / split 189-33 / 273 self-containment flags and recovered 34 structural atomicity candidates, but found no evidence identifying which four were excluded from a former informal count of 30 — so it stopped before any corpus change.

### D68 — Canonical atomicity adjudication recovery (✅ EXECUTION PASS / CANONICAL ATOMICITY SET RECOVERED)
- Two procedurally separate passes over the 34 candidates, 64/64 propositions with literal source support each pass, 30 agreements + 4 disagreements resolved + 0 unresolved. Canonical result: **24 `NON_ATOMIC_REPAIR_REQUIRED` + 10 `INTEGRATED_SINGLE_CLAIM_FALSE_POSITIVE`** (not the provisional 20/14 or former target 30). Constraint logged: both passes are from the same Codex environment, not a human inter-annotator study.

### D69 — Gold Corpus v2 target repair + self-containment adjudication + deterministic build (✅ pre-registered)
- Pre-registered build of Gold v2 under `results/gold_v2/`, keeping the 222 Egyptian source answers byte-for-byte and repairing 3 unsupported additions + 24 atomicity keys + 273 self-containment flags via a consolidated original-index repair plan — no training, no O9, no ASR augmentation, no production integration.

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
| **Q8** | Coverage channel measured on real decomposition claims. Experiment designed and pre-registered (D82) — 25 O9 answers through `decompose_via_llm` vs. official `key_points`, pending execution on Kaggle T4. | ⛔ |
| **G4** | Threshold calibration (τ_E, τ, α, k currently PRE-CALIBRATION DEFAULT). Inputs in D43. | ⛔ |
| **Q7 / O11** | Recording tech stack + session spec + team adoption. **Blocks G3** and ASR selection (Phase 7). | ⛔ |
| **G3** | Pilot videos — blocks ASR selection (tied to Q7). | ⛔ |
| **Q10 — Demo #1** | Has the Baseline Demo (D24) been shown to the supervisor? | ⛔ |
| **Q2** | 250-question review documentation + SE-006 anomaly check. | ⛔ |
| **D73** | Exhaustive D72 error analysis — non-blocking retrospective documentation. | ⛔ |
| **O1** | Option B justification paragraph — final report. | ⛔ |
| **Gold naming** | Three artifacts named "Gold" (O9 val set, DS-014 NLI Gold Set, decomposition corpus) — documentation-only rename recommended. | ⛔ |

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

- **v3.0 (21 Jul 2026):** D81 — full English migration + thematic reorganization of the log (D1–D80). All figures carried over verbatim; superseded AraT5 procedural entries (D58–D73) condensed to outcomes; Arabic original archived. Added D78/D79/D80 (sanity gate execution: gemma VOID, llama VOID, cohere PASS).
- **v2.41–v2.37 (21 Jul 2026):** D74 pivot (AraT5 → runtime LLM API, supervisor-approved); D75 (Codex corpus attempt, closed/superseded); D76 (first end-to-end LLM call, nemotron after gemma 429); D77 (sanity gate design). "Zero LLM at runtime" reframed to "LLM-free correctness core."
- **v2.36–v2.33 (19–20 Jul 2026):** D70 (paired corpus), D71 (paired FT, checkpoint-543, eval_loss 2.205), D72 (quality REJECTED — O9 LCS F1 0.189), D73 (error-analysis pre-registration); D67/D68 (atomicity adjudication: 24+10), D69 (Gold v2 build pre-registration).
- **v2.32–v2.27 (18 Jul 2026):** D64 (full retrain, EXECUTION PASS/no quality), D65 (QUALITY FAIL — median edit sim 0.519/0.160, Q6 reopened), D66 (PEFT repair, NO REPAIR CANDIDATE); D62/D63 (single- and five-example overfit diagnostics PASS).
- **v2.21–v2.16 (13–16 Jul 2026):** D53–D57 (Q6 pilot, AraT5 selected on linguistic grounds, corpus expansion 223/225, prompt format, trainer hyperparameters + save_total_limit fix).
- **v2.15–v2.12 (12–13 Jul 2026):** D50–D52 (O9 sample pre-registration, O9 closure with organic R1 in 7 questions, G2 closed by consequence).
- **v2.11–v2.9 (10–11 Jul 2026):** D45 (metrics.py semantics ratified), D46 (reversed-direction diagnostic), D47 (score range [-100,+100]), D48 (Python 3.11), D49 (probe result — no signal).
- **v2.8–v2.3 (9–10 Jul 2026):** D42–D44 (Q8 reframed, 0.002 withdrawn, V4 deferred — O9 to critical path), D43 (V2 closed, 48/48 deterministic, two zero-shot false verifications), D39–D41 (Phase 5 pre-registration + PASSED result).
- **v2.2–v2.0 (9 Jul 2026):** merged the two logs (Q1 closed); D37/D38 (Kaggle staging, first fine-tuning run); D33 (G1 closed by risk acceptance); D35 rewritten; D31 expanded.
- **v1.x:** pipeline-session log (old D21–D26 numbering) — implicitly archived.
