# PROJECT_EXECUTION_PLAN.md
**Interview IQ — NLP Module (Answer Correctness Evaluation)**
**الإصدار:** v1.2 — 9 يوليو 2026
**الغرض:** ذاكرة التنفيذ الرسمية للمشروع. أي محادثة جديدة داخل المشروع تبدأ من هذا الملف. لا يُعاد فتح أي قرار موسوم ✅ إلا بقرار صريح من أحمد.

**مفتاح الحالة:** ✅ مقفول ونهائي · ⛔ مفتوح/معلّق · 🔶 Placeholder غير مُتحقق منه · 🗑️ ملغي

---

## 1. Project Overview

**Interview IQ** نظام Multi-Modal لتقييم مقابلات العمل التقنية بالعربية (فيديو + صوت + نص). هذا الـ Repo مسؤول عن **موديول الـ NLP فقط**، والـ deliverable الأكاديمي الوحيد فيه (بتوجيه المشرف الأكاديمي — 7 يوليو 2026) هو:

> **Answer Correctness Evaluation** — تقييم صحة إجابة المرشح مقارنةً بمرجع معتمد لكل سؤال.

🗑️ **Linguistic Confidence Module خارج النطاق نهائيًا (D20).** أي كود أو تصميم أو نقاش يخصه ملغي ولا يُعاد فتحه.

**النطاق مغلق (Closed-Domain):** 250 سؤالًا ثابتًا عبر خمسة مسارات — Data Analysis (DA)، Data Science (DS)، Cybersecurity (CS)، Software Engineering (SE)، General (GN) — 50 سؤالًا لكل مسار. *(تصحيح v1.1: كان مكتوبًا خطأً "Computer Science" — `data/questions/questions_250.json` (meta.tracks) يثبّت CS = Cybersecurity.)* لكل سؤال Reference Document مقسّم Chunks (سطر = fact واحد مكتفٍ بذاته، فصحى مبسطة، المصطلحات التقنية بحروف لاتينية).

**الثوابت المعمارية (غير قابلة للتفاوض):**
1. **Zero LLM at Runtime** — كل الـ inference محلي (Decomposition + Embedding + NLI). الـ LLM مسموح في الـ offline data prep فقط بمنهجية Knowledge Distillation مع مراجعة بشرية.
2. **التطوير محلي، التشغيل على Kaggle (D19)** — الـ Repo يعيش محليًا (Claude Code + Git)، وGitHub هو المصدر الوحيد للحقيقة. Kaggle (T4 ×2) محرك GPU فقط عبر Thin Runner Notebooks (clone + pip + أمر CLI واحد — صفر منطق داخل النوتبوك).
3. **Data Leakage prevention على مستوى Question-ID** دائمًا، ليس على مستوى الـ example.
4. كل قرار تصميمي مسنود بورقة منشورة أو موسوم صراحةً كـ empirical hyperparameter.

---

## 2. Current Architecture

**خط الأنابيب (Pipeline):**

```
Video/Audio (per-question segments via click timestamps)
   │
   ▼
[1] ASR  — faster-whisper large-v3 (baseline ✅، الاختيار النهائي ⛔ مؤجل لحين تسجيل الـ pilot videos)
   │        المخرج: Format Spec v1.1 ✅ (JSON لكل answer segment)
   ▼
[2] Claim Decomposition — Seq2Seq (AraT5 أو mT5-base) عبر Knowledge Distillation ⛔ (لم يُبنَ بعد)
   │        Split + Decontextualize + Register conversion → فصحى مبسطة + مصطلحات لاتينية
   ▼
[3] Chunk Cap — BGE-M3 Top-k (k=10 🔶) — سقف حسابي "كريم" فقط، ليس بوابة فلترة ✅
   ▼
[4] NLI — mDeBERTa-v3-base-mnli-xnli + LoRA fine-tuning ✅ (إلزامي، مُقرر تجريبيًا)
   │        Full matrix: Claims × Chunks (per SummaC)
   ▼
[5] Dual-Channel Scoring — Option B + v2 Entailment-Priority ✅ (البنية نهائية، العتبات 🔶)
          Precision channel + Coverage channel → Harmonic F-Score (0–100)
```

**تفاصيل مقفولة لكل مرحلة:**

**[1] ASR — Format Spec v1.1 ✅:** JSON لكل answer segment يحوي: `question_id`, `status` (ok/no_speech/too_short — يُحسم بـ VAD قبل الـ ASR), `raw_transcript`, `normalized_transcript`, `normalization_log`, word-level timestamps (للـ localization فقط), `vad_features` (Silero VAD على الـ waveform مباشرة), `avg_logprob` (QC فقط), `pre_answer_latency_sec`. التقطيع بالـ click timestamps قبل الترانسكريبشن. المقياس الأساسي للمفاضلة: **T-WER**، وفجوة WER−T-WER مقياس كمّي للـ forced Arabization.

**[2] Decomposition — القواعد الأربع للتأليف ✅:** (أ) الحفاظ على كلمات الـ hedging مثل "غالبًا" (faithfulness)؛ (ب) تعميم الصياغات الشخصية الناقلة للمعرفة وتقييمها؛ (ج) لا يُولَّد claim ثالث للعلاقة السببية بين claimين مثبتين إلا إذا كانت السببية نفسها قابلة للتحقق مستقلًا؛ (د) كل claim يجتاز اختبار الـ self-containment.

**[4] NLI — التشخيص والعلاج ✅:** الفشل الجوهري للـ zero-shot هو **Subject Blindness** — نفس الـ claim الصحيح يسجّل E=0.999 وC=1.0 ضد chunks متعاكسة في نفس المستند، وclaims خاطئة بـ subject-swap تسجّل E=0.95+. تجاوز الـ E↔C confusion عتبة الـ 5% المسجّلة مسبقًا ⇒ **الـ Fine-tuning إلزامي بقرار تجريبي لا رأي.** إعداد LoRA المقفول: r=16، target = q/v projections، alpha=32، lr ≈ 2e-4–3e-4، والـ split على مستوى Question-ID.

**[5] Scoring — قاعدة v2 Entailment-Priority ✅ (بنيةً):**
- إذا `max_E ≥ τ_E` → **VERIFIED** (تجاهل قناة C — مبرَّر بالاتساق الداخلي للمرجع بحكم convention التأليف).
- وإلا إذا `max_C > τ` → عقوبة تناقض (`score = −max_C`).
- وإلا → معالجة Neutral (وزن α).
- قناة Coverage: اتجاه NLI معكوس (الـ key points كـ hypothesis)، تجميع max P(E) لكل key point.
- الدمج: Harmonic F-Score. العقوبة المزدوجة للتناقض **مقصودة**: قال صح > سكت > قال غلط.
- **المراجع:** FactScore (EMNLP 2023) للتفكيك الذري والتجميع الموزون؛ SummaC (TACL 2022) للـ sentence-level NLI والاحتمالات الخام بدل argmax؛ SemEval-2013 Task 7 لتمييز Contradiction عن Neutral.

**Placeholders 🔶 (PRE-CALIBRATION DEFAULT — NOT VALIDATED):** τ=0.5 · τ_E=0.9 · α=0.0 · k=10. الأربعة تدخل تجربة المعايرة البشرية.

**Symmetric Granularity ✅:** مدخلات الـ NLI دائمًا أزواج فصحى/فصحى بمصطلحات لاتينية. العامية والـ Code-Switching موجودان في طبقتي ASR والـ Decomposition فقط.

**⛔ قضية مؤجلة صراحةً — Coverage Asymmetry:** claims قصيرة كـ premise ضد chunks طويلة رسمية تعطي Coverage شبه صفري لإجابات صحيحة (مثال موثق: 0.002). مؤجلة لما بعد الـ fine-tuning. ممنوع فتحها قبل ذلك.

---

## 3. Technologies

| الطبقة | التقنية | الحالة |
|---|---|---|
| اللغة/الإطار | Python 3.10+, PyTorch, Hugging Face `transformers` | ✅ |
| Fine-tuning | `peft` (LoRA), `datasets`, `accelerate` | ✅ |
| ASR | `faster-whisper` (large-v3 baseline) | ✅ baseline / ⛔ اختيار نهائي |
| VAD | Silero VAD | ✅ |
| Embeddings | BGE-M3 (`FlagEmbedding` أو `sentence-transformers`) | ✅ |
| NLI | `MoritzLaurer/mDeBERTa-v3-base-mnli-xnli` | ✅ |
| Decomposition | AraT5 أو mT5-base (KD) | ⛔ الاختيار بينهما معلّق |
| Configuration | YAML لكل مرحلة + `config.py` مركزي | ✅ |
| Testing | `pytest` + fixtures صغيرة تعمل CPU | ✅ |
| Compute | Kaggle T4 ×2 (~30 GPU-hr/أسبوع) عبر Thin Runners | ✅ |
| التطوير | Claude Code + Git محليًا، GitHub = source of truth | ✅ (D19) |
| نقل البيانات | Kaggle Datasets للمدخلات والـ checkpoints (لا اعتماد على `/kaggle/working` بين الجلسات) | ✅ |

**Kaggle Datasets المتفق عليها:** `iq-question-bank`, `iq-reference-docs`, `iq-pilot-recordings`, `iq-kd-corpus`, `iq-nli-finetune-data`, `iq-checkpoints-*`.

---

## 4. Folder Structure

الهيكل المقفول (D19 / §15 v1.1 من الوثيقة الرئيسية، بعد حذف `confidence/` بموجب D20):

```
interview-iq/                          ← Repo محلي (Git)
├── README.md
├── requirements.txt
├── decisions.md                       ← سجل القرارات (بديل فقرات الدفاع أثناء التطوير)
├── PROJECT_EXECUTION_PLAN.md          ← هذا الملف
├── IMPLEMENTATION_GUIDE.md
├── configs/
│   ├── asr.yaml
│   ├── decomposition.yaml
│   ├── retrieval.yaml
│   ├── nli_finetune.yaml
│   ├── scoring.yaml
│   └── calibration.yaml
├── data/                              ← بيانات محلية صغيرة فقط (الكبيرة = Kaggle Datasets)
│   ├── questions/questions_250.json
│   ├── refdocs/reference_docs_250_FINAL_v1.json
│   ├── nli/gold_set_48.json           ← DS-014 حصريًا — evaluation only
│   └── nli/pairs_pilot_150_v2/        ← pairs_DA001_pilot_v1.json + pairs_pilot_remaining9_v2.json
├── src/interview_iq/
│   ├── __init__.py
│   ├── config.py                      ← تحميل YAML + كل الـ Hyperparameters (τ, τ_E, α, k, أسماء الموديلات)
│   ├── audio/segmentation.py          ← تقطيع بالـ click timestamps
│   ├── asr/engine.py                  ← ينتج Format Spec v1.1
│   ├── refdocs/
│   │   ├── loader.py
│   │   └── chunker.py
│   ├── decomposition/                 ← ⛔ يُبنى بعد O9 + دليل التأليف
│   ├── retrieval/chunk_cap.py         ← BGE-M3 Top-k (سقف، ليس بوابة)
│   ├── nli/
│   │   ├── engine.py                  ← inference (full matrix)
│   │   ├── dataset.py                 ← تحميل الأزواج + فحوص السلامة
│   │   └── finetune.py                ← LoRA training
│   ├── scoring/
│   │   ├── aggregation.py             ← v2 entailment-priority
│   │   └── metrics.py                 ← Precision / Coverage / Harmonic F
│   ├── evaluation/gold_eval.py        ← per-class F1 + confusion matrix على الـ Gold Set
│   ├── fusion/                        ← ⛔ خارج نطاق الـ NLP deliverable — placeholder لتكامل الفريق
│   └── cli/                           ← python -m interview_iq.cli.run_* (نُقل من الجذر، انحراف Phase 1 مصحَّح في Phase 3)
│       ├── run_asr.py
│       ├── run_nli_finetune.py
│       ├── run_nli_eval.py
│       ├── run_scoring.py
│       ├── run_calibration.py
│       └── validate_data.py
├── tests/
│   ├── fixtures/                      ← عينات صغيرة CPU-friendly
│   └── test_*.py                      ← Smoke tests لكل مرحلة
└── kaggle/runners/
    ├── run-nli-finetune.ipynb         ← clone + pip + أمر CLI فقط (اسم بشرطة — قيد تسمية Kaggle kernel slug)
    ├── run-nli-eval.ipynb
    └── run_asr.ipynb                  ← لم يُبنَ بعد (Phase 7) — الاسم قد يتغير لنفس السبب عند البناء
```

ملاحظة: تطبيق التسجيل (`app/`) يخص O11 (Tech Stack + Session Spec v1.0 + اعتماد الفريق) وهو ⛔ خارج مسار هذا الـ plan حتى يُحسم.

---

## 5. Development Rules

1. **صفر منطق داخل نوتبوكات Kaggle.** أي تعديل → محليًا → Push → إعادة تشغيل الـ Runner. نوتبوك فيه منطق = انحراف صامت عن المصدر.
2. **CPU-First:** كل CLI يعمل End-to-End محليًا على CPU بعينة من `tests/fixtures` قبل أي تشغيل Kaggle. كوتة الـ GPU تُحرق في تدريب حقيقي فقط. **يُكتب هذا البند نصًا في كل Prompt يُرسل لـ Claude Code.**
3. **GitHub = المصدر الوحيد للحقيقة.** الـ checkpoints والمخرجات تُنشر كـ Kaggle Datasets.
4. **Zero LLM at Runtime** — أي استيراد لـ API خارجي في مسار الـ inference = خطأ معماري يُرفض في الـ review.
5. **الـ Splits على مستوى Question-ID** حصريًا.
6. **HARD_POS twins لا يُفصلان أبدًا** عبر حدود train/val (زوجان بنفس نص الـ hypothesis: entailment + paired_neutral).
7. **DS-014 مستبعد نهائيًا من أي premise pool للتدريب** — مستند الـ Gold Set (48 زوجًا، evaluation only).
8. **الـ premises تأتي حصريًا من ملف المراجع الفعلي** — الـ LLM لا يخترع محتوى تقنيًا أبدًا؛ الـ premise مُدخل لا مولَّد.
9. **مرحلة واحدة لكل جلسة Claude Code.** ينفّذ، يكتب Summary، يذكر المشاكل، يتوقف وينتظر مراجعة أحمد.
10. **decisions.md يُحدَّث مع كل قرار** بمعرّف D## وحالة (✅/⛔/🔶/🗑️) — القرارات المقفولة immutable إلا بإعادة فتح صريحة.
11. أي عتبة أو hyperparameter غير مُعايَر يُطبع في اللوجات بوسم `PRE-CALIBRATION DEFAULT — NOT VALIDATED`.
12. كل ملف بيانات يمر بفحص schema + uniqueness قبل استهلاكه (chunk IDs، pair IDs، تكامل الـ twins).
13. تجريبي ≠ مُستنتَج من config. أي ادعاء عن سلوك مكتبة (peft, transformers) لا يُكتب في التوثيق إلا بعد تشغيله فعليًا وطباعة الناتج. الاستنتاج من ملف YAML أو من التوثيق الرسمي ليس تحققًا (D31, D38).

---

## 6. Execution Roadmap

> **بوابات بشرية معلنة مسبقًا (لا يتجاوزها أي Prompt):**
> - **G1:** مراجعة Stage-4 البشرية للأزواج (أو الـ 20% retroactive spot-check الموصى به) — قبل الاعتماد على نتائج الـ fine-tuning أكاديميًا.
> - **G2:** تمارين الـ decomposition اليدوية (O9) + جلسة دليل التأليف — قبل Phase 8.
> - **G3:** تسجيل الـ pilot videos — قبل حسم اختيار الـ ASR في Phase 7.
> - **G4:** تجربة المعايرة البشرية — قبل اعتماد τ, τ_E, α, k في Phase 10.

---

### Phase 1 — Repo Scaffolding
- **الهدف:** إنشاء هيكل الـ Repo كاملًا كما في §4، بملفات فارغة/هياكل أولية، وتهيئة Git.
- **ملفات تُنشأ:** كل الشجرة في §4 (مجلدات + ملفات فارغة + `__init__.py` + `.gitignore` + `README.md` هيكلي + `requirements.txt` أولي).
- **ملفات تُعدل:** لا شيء.
- **شرط البدء:** لا شيء.
- **Deliverables:** Repo مُهيأ بـ commit أولي، شجرة مطابقة حرفيًا للخطة.

### Phase 2 — Environment & Configuration
- **الهدف:** بيئة تشغيل قابلة للتكرار + طبقة config مركزية.
- **ملفات تُنشأ:** `configs/*.yaml` (بكل الـ placeholders موسومة 🔶)، `src/interview_iq/config.py`، `tests/test_config.py`.
- **ملفات تُعدل:** `requirements.txt` (تثبيت إصدارات).
- **شرط البدء:** Phase 1 مكتملة ومراجَعة.
- **Deliverables:** `pip install -r requirements.txt` ينجح محليًا؛ `config.py` يحمّل كل YAML ويطبع وسم PRE-CALIBRATION للقيم غير المعايَرة؛ smoke test أخضر.

### Phase 3 — Data Layer (Loaders + Validators)
- **الهدف:** تحميل وفحص كل ملفات البيانات قبل أي تدريب.
- **ملفات تُنشأ:** `refdocs/loader.py`، `nli/dataset.py`، `tests/fixtures/` (عينة refdocs مصغرة + عينة أزواج)، `tests/test_data_layer.py`، `cli/validate_data.py`.
- **الفحوص الإلزامية:** schema صحيح؛ uniqueness للـ chunk IDs (1,515 chunk)؛ استبعاد DS-014 من أي premise pool تدريبي؛ تكامل HARD_POS twins (30 مجموعة)؛ توزيع الأزواج E=50/C=60/N=40 على الـ 150؛ الـ split بمستوى Question-ID مع عدم فصل الـ twins.
- **ملفات تُعدل:** `configs/nli_finetune.yaml`.
- **شرط البدء:** Phase 2 + وجود ملفات البيانات في `data/` (يضعها أحمد يدويًا).
- **Deliverables:** `validate_data` يمر بنجاح ويطبع تقريرًا؛ أي فشل يوقف الخط.

### Phase 4 — NLI Fine-tuning Pipeline (LoRA)
- **الهدف:** تدريب LoRA على أزواج الـ pilot (150) لعلاج الـ Subject Blindness.
- **ملفات تُنشأ:** `nli/finetune.py`، `cli/run_nli_finetune.py`، `kaggle/runners/run-nli-finetune.ipynb`، `tests/test_finetune_smoke.py` (خطوة تدريب واحدة CPU على fixture).
- **الإعداد المقفول:** r=16، q/v projections، alpha=32، lr ≈ 2e-4–3e-4، split بمستوى Question-ID.
- **شرط البدء:** Phase 3 خضراء. **⚠️ بوابة G1 تُذكر صراحةً في الـ Summary:** أي نتيجة تُنتج قبل إغلاق Stage-4/spot-check توسم منهجيًا RISK ACCEPTED (كما هو مسجل في decisions.md).
- **Deliverables:** checkpoint LoRA منشور كـ `iq-checkpoints-nli-v1` على Kaggle + لوج تدريب كامل.

### Phase 5 — Gold Set Evaluation ✅ COMPLETE
- **الهدف:** تقييم الموديل المدرَّب على الـ Gold Set (48 زوجًا، DS-014).
- **ملفات تُنشأ:** `evaluation/gold_eval.py`، `cli/run_nli_eval.py`، `kaggle/runners/run-nli-eval.ipynb`.
- **المقاييس (pre-registered):** per-class F1 + confusion matrix كاملة، مع تركيز على Contradiction F1 وخلايا E↔C. **الـ baseline = الذراع zero-shot على نفس الـ 48 زوج، بنفس الـ code path (`gold_eval.py` بعلم `--zero-shot`) — وليس Demo #1.** Demo #1 (D24) سياق كيفي فقط، لا baseline رقميًا (انظر D39).
- **شرط البدء:** Phase 4 (checkpoint موجود).
- **Deliverables:** تقرير مقارنة zero-shot vs fine-tuned؛ حكم صريح: هل انكسر الـ Subject Blindness؟
- **النتيجة (9 يوليو 2026):** **الحكم = PASSED** مقابل قاعدة D39 المسجَّلة مسبقًا — C→E: 3→0، E→C: 1→0، Contradiction recall: 16/19 بلا تغيّر. التفاصيل الكاملة (المقاصة، الحالات المسمّاة P48/P26/P43، القيود) في `decisions.md` D41. المخرجات الخام per-pair لكل ذراع محفوظة في `results/phase5/`.

### Phase 6 — Retrieval Cap + Scoring Engine
- **الهدف:** بناء BGE-M3 Top-k cap + محرك الـ Dual-Channel Scoring كاملًا.
- **ملفات تُنشأ:** `retrieval/chunk_cap.py`، `nli/engine.py` (full matrix)، `scoring/aggregation.py` (v2 entailment-priority)، `scoring/metrics.py`، `cli/run_scoring.py`، اختبارات وحدات للتجميع (حالات: VERIFIED، contradiction penalty، neutral، الترتيب صح > سكوت > غلط).
- **شرط البدء:** Phase 5 (لأن سلوك التجميع يُختبر بموديل ما بعد الـ fine-tuning).
- **⛔ حاجز بدء صلب — V2 (انظر §8 وdecisions.md D41):**
  > "V2 (⛔): gold_eval_*.json store argmax labels only, no softmax/logits. Raw probabilities MUST be added to evaluation outputs before any threshold (τ_E) work. The scoring engine consumes probabilities, not argmax — see decisions.md D41."
- **Deliverables:** سكور 0–100 لكل إجابة على fixtures + لوج قرارات per-claim قابل للتفسير.

### Phase 7 — ASR Module
- **الهدف:** `audio/segmentation.py` + `asr/engine.py` منتجًا Format Spec v1.1 حرفيًا، بـ faster-whisper large-v3 كـ baseline.
- **ملفات تُنشأ:** الملفان أعلاه + `kaggle/runners/run_asr.ipynb` + fixture صوتي قصير + بروتوكول T-WER في `evaluation/`.
- **شرط البدء:** Phase 2. **بوابة G3:** المفاضلة النهائية بين المرشحين (large-v3 / ArzEn fine-tunes / whisper-small-CS) لا تتم إلا بعد الـ pilot videos.
- **Deliverables:** JSON مطابق للـ Spec لكل segment؛ سكريبت T-WER جاهز للمفاضلة لاحقًا.

### Phase 8 — Claim Decomposition (KD) ⛔ خلف بوابة G2
- **الهدف:** بناء corpus الـ KD ثم تدريب AraT5/mT5-base.
- **ملفات تُنشأ:** `decomposition/` (dataset builder + trainer + inference) + runner.
- **شرط البدء:** **O9 مكتمل + جلسة دليل التأليف مقفولة.** لا يبدأ Claude Code هنا مهما كان.
- **Deliverables:** موديل decomposition + تقييم مقابل القواعد الأربع.

### Phase 9 — End-to-End Inference
- **الهدف:** خيط واحد: ASR output → claims → chunk cap → NLI matrix → score.
- **ملفات تُنشأ:** `cli/run_pipeline.py` + integration test على fixture كامل.
- **شرط البدء:** Phases 6 + 7 + 8.
- **Deliverables:** تشغيل كامل على تسجيل pilot واحد بمخرجات مفسَّرة. (بعده مباشرة: جلسة الـ Viva Simulation الموعودة — أول output حقيقي.)

### Phase 10 — Human Calibration Tooling (بوابة G4)
- **الهدف:** أدوات تجربة معايرة τ, τ_E, α, k + قاعدة الدمج فوق العتبة.
- **ملفات تُنشأ:** `cli/run_calibration.py` + إخراج جداول مقارنة للحكم البشري.
- **شرط البدء:** Phase 9.
- **Deliverables:** قيم معايَرة تحل محل وسم PRE-CALIBRATION في `configs/`.

### Phase 11 — Final Evaluation & Thesis Artifacts
- **الهدف:** تجميع كل النتائج + تحديث decisions.md النهائي + مواد الدفاع (ومنها فقرة تبرير Option B — O1).
- **شرط البدء:** Phase 10.
- **Deliverables:** تقرير نتائج نهائي + سجل قرارات مكتمل قابل للدفاع.

---

## 7. Chat Workflow — Prompts جاهزة لـ Claude Code

> اللغة الإنجليزية اختيرت للـ prompts (كفاءة tokens — نفس منطقك في جلسة المعايرة). كل Prompt: مرحلة واحدة، لا تجاوز، Summary إلزامي، توقف وانتظار المراجعة.

**PROMPT — Phase 1**
```
You are working inside the interview-iq repo. Read PROJECT_EXECUTION_PLAN.md fully before doing anything.
Execute Phase 1 ONLY: create the complete folder structure and empty files exactly as specified in Section 4 of the plan (including .gitignore, README.md skeleton, initial requirements.txt, and all __init__.py files). Initialize git and make one initial commit.
Rules: do not write any implementation logic; do not start Phase 2; CPU-only environment assumed.
When done: write a summary of everything created, list any deviations or problems, then STOP and wait for my review.
```

**PROMPT — Phase 2**
```
Phase 1 is approved. Execute Phase 2 ONLY per PROJECT_EXECUTION_PLAN.md: pin dependencies in requirements.txt; create all configs/*.yaml with the locked values and the pre-calibration placeholders (τ=0.5, τ_E=0.9, α=0.0, k=10) explicitly tagged "PRE-CALIBRATION DEFAULT — NOT VALIDATED"; implement src/interview_iq/config.py (YAML loading, central hyperparameters, prints the pre-calibration tag when loading unvalidated values); add tests/test_config.py.
CPU-First rule applies: everything must run locally on CPU. Do not touch any other phase.
When done: summary + problems, then STOP and wait for my review.
```

**PROMPT — Phase 3**
```
Phase 2 is approved. Execute Phase 3 ONLY: build the Data Layer.
Implement refdocs/loader.py, nli/dataset.py, cli/validate_data.py, small CPU fixtures under tests/fixtures/, and tests/test_data_layer.py.
Mandatory validations (hard failures, not warnings): JSON schema; chunk-ID uniqueness; DS-014 permanently excluded from any training premise pool; HARD_POS twin integrity (identical hypothesis text, labels entailment + paired_neutral, never split across train/val); pilot label distribution E=50/C=60/N=40 over 150 pairs; Question-ID-level splitting only.
CPU-First rule applies. Do not implement any model code.
When done: summary + validation report + problems, then STOP and wait for my review.
```

**PROMPT — Phase 4**
```
Phase 3 is approved and validate_data passes. Execute Phase 4 ONLY: LoRA fine-tuning pipeline for MoritzLaurer/mDeBERTa-v3-base-mnli-xnli.
Locked config: r=16, target modules q/v projections, alpha=32, lr in 2e-4–3e-4, Question-ID-level split, HARD_POS twins never split. Implement nli/finetune.py, cli/run_nli_finetune.py, kaggle/runners/run-nli-finetune.ipynb (clone + pip + one CLI line, ZERO logic), and a CPU smoke test running one training step on fixtures.
Note in your summary: results are methodologically tagged RISK ACCEPTED until the Stage-4 human review / 20% spot-check gate (G1) is closed.
When done: summary + problems, then STOP and wait for my review.
```

**PROMPT — Phase 5**
```
Phase 4 is approved and the LoRA checkpoint exists as a Kaggle Dataset. Execute Phase 5 ONLY: Gold Set evaluation.
Implement evaluation/gold_eval.py, cli/run_nli_eval.py, kaggle/runners/run-nli-eval.ipynb. Metrics are pre-registered: per-class F1 and full confusion matrix, with explicit reporting of Contradiction F1 and E↔C cells, compared against the zero-shot arm over the same 48 gold pairs (same code path, --zero-shot flag) — not Demo #1, which is qualitative context only (D39). Output a clear verdict: is Subject Blindness fixed?
CPU-First rule applies for the smoke path. When done: summary + comparison table + problems, then STOP.
```

**PROMPT — Phase 6**
```
Phase 5 is approved. Execute Phase 6 ONLY: retrieval cap + scoring engine.
BLOCKER (V2, decisions.md D41): gold_eval_*.json currently store argmax labels only, no softmax/logits. Before any threshold (τ_E) work, nli/engine.py's full Claims × Chunks matrix MUST output raw per-class probabilities (not argmax) for every (claim, chunk) pair — the scoring engine (max_E ≥ τ_E, max_C > τ) consumes probabilities, not labels. If evaluation/gold_eval.py or its CLI is touched in this phase, it must also be extended to persist probabilities, not just argmax.
Implement retrieval/chunk_cap.py (BGE-M3 Top-k, k from config, cap not gate), nli/engine.py (full Claims × Chunks matrix per SummaC, raw probabilities per pair), scoring/aggregation.py implementing v2 entailment-priority exactly (max_E ≥ τ_E → VERIFIED ignoring C; elif max_C > τ → score = −max_C; else neutral with weight α), scoring/metrics.py (Precision, Coverage with reversed NLI direction, Harmonic F), cli/run_scoring.py, and unit tests covering: VERIFIED case, contradiction penalty, neutral handling, and the ranking correct > silent > wrong.
All thresholds come from config and log the PRE-CALIBRATION tag. CPU-First applies.
When done: summary + problems, then STOP.
```

**PROMPT — Phase 7**
```
Execute Phase 7 ONLY: ASR module. Implement audio/segmentation.py (click-timestamp segmentation) and asr/engine.py producing Format Spec v1.1 EXACTLY: question_id, status (ok/no_speech/too_short decided by Silero VAD before ASR), raw_transcript, normalized_transcript, normalization_log, word-level timestamps, vad_features (Silero VAD on the waveform directly, never from Whisper timestamps), avg_logprob (QC only), pre_answer_latency_sec. Baseline model: faster-whisper large-v3. Add kaggle/runners/run_asr.ipynb and a short audio fixture. Also add the T-WER evaluation script (final ASR model selection is gated on pilot videos — do NOT make a selection).
When done: summary + problems, then STOP.
```

**PROMPT — Phase 8 (⛔ محجوز — لا يُرسل قبل إغلاق O9 ودليل التأليف)**
```
Gate G2 is closed (manual decomposition exercises done, annotation guide locked — confirmed by Ahmed). Execute Phase 8 ONLY: claim decomposition via Knowledge Distillation.
Build decomposition/ (KD dataset builder consuming the human-reviewed corpus, AraT5/mT5-base trainer, inference), enforcing the four locked annotation rules (hedging preserved; personal framing generalized; no third causal claim unless independently verifiable; self-containment test). Add the Kaggle runner.
When done: summary + problems, then STOP.
```

**PROMPT — Phase 9**
```
Phases 6, 7, and 8 are approved. Execute Phase 9 ONLY: end-to-end inference.
Implement cli/run_pipeline.py chaining: ASR Format Spec v1.1 JSON → decomposition → BGE-M3 cap → full NLI matrix → dual-channel score, with a per-claim decision log. Add one full integration test on fixtures (CPU).
When done: summary + one worked example output + problems, then STOP.
```

**PROMPT — Phase 10**
```
Phase 9 is approved. Execute Phase 10 ONLY: human calibration tooling for τ, τ_E, α, k and the above-threshold merge rule. Implement cli/run_calibration.py producing side-by-side comparison tables over a labeled sample for human judgment. Do NOT pick final values yourself — output artifacts for Ahmed's decision only.
When done: summary + problems, then STOP.
```

**PROMPT — Phase 11**
```
Phase 10 is approved and calibrated values are committed to configs. Execute Phase 11 ONLY: final evaluation report generation and thesis artifacts — aggregate all metrics, produce the final results report, and update decisions.md to its final state (all D## entries with correct status markers). Flag anything still marked 🔶 or ⛔.
When done: summary + problems, then STOP.
```

---

## 8. Open Questions / Missing Information

مسجّلة بلا افتراضات — كل بند يحتاج قرارًا صريحًا من أحمد:

| # | البند | التفصيل |
|---|---|---|
| Q1 | **تعارض ترقيم القرارات D##** | ✅ **CLOSED** — انظر `decisions.md` (السجل الموحّد D1–D40، v2.2). |
| Q2 | **حالة ملف المراجع** | القفزة من 47 مستندًا مراجَعًا إلى `reference_docs_250_FINAL_v1.json` (250/250) غير موثقة كمرحلة انتقال؛ والاسم FINAL يناقض metadata الداخلية (DRAFT / "AI-generated, pending expert review"). مطلوب: توثيق الانتقال + توحيد الاسم/الميتاداتا قبل التسليم الأكاديمي. أحمد يتحمل مسؤولية الدفاع عن حالة المراجعة. |
| Q3 | **بوابة G1 (Stage-4)** | ✅ **CLOSED** — انظر `decisions.md` D33 (مغلقة بقرار قبول المخاطرة، لا بإتمام المراجعة). |
| Q4 | **stage2_verdict ناقص في 135/150 زوجًا** | ✅ **CLOSED** — انظر `decisions.md` (فجوة توثيق في v1 القديم، لا فجوة منهجية؛ `validate_data` أكد وجوده على 15/15). |
| Q5 | **مخالفة قاعدة الـ 5-word overlap** | ✅ **CLOSED** — انظر `decisions.md` D35 وD40 (الرقم المعتمد 65/150، وارتباط تام وضار بمحور N/¬N موثّق منفصلًا). |
| Q6 | **اختيار AraT5 vs mT5-base** | لم يُحسم. مؤجل طبيعيًا لبوابة G2 لكنه يظل مفتوحًا. |
| Q7 | **O11 — تطبيق التسجيل** | Tech Stack + Session Spec v1.0 + اعتماد الفريق كله معلّق؛ فرق الوجه والصوت يعتمدون على نفس التطبيق والـ timestamps. خارج هذا الـ plan لكنه blocking للـ pilot videos (وبالتالي لبوابة G3). |
| Q8 | **Coverage Asymmetry** | ⛔ **ACTIVE الآن** — تأجيل D34 انتهى بانتهاء Phase 5. مفتوحة كبند مستقل يحتاج قرارًا صريحًا قبل Phase 6/9. |
| Q9 | **مستودع GitHub** | ✅ **CLOSED** — انظر `decisions.md` D19 (الريبو: https://github.com/HashemIlI/interview-iq، private). |
| Q10 | **الديمو الأساسي D24** | Demo #1 zero-shot نُفذ فعليًا (5 أسئلة). هل عرضه للمشرف تم أم لا يزال deliverable معلقًا؟ |
| V1 | **تحقق الـ checkpoint** | ✅ **CLOSED** — مفاتيح `classifier.*` مؤكَّدة داخل `adapter_model.safetensors` (50 tensor)، نُفِّذ كأول خلية في `kaggle/runners/run-nli-eval.ipynb` قبل Phase 5. انظر `decisions.md` D38/D40/D41. |
| V2 | **الاحتمالات الخام في مخرجات التقييم** | ⛔ **يحجب Phase 6.** `gold_eval_*.json` لا تحفظان softmax/logits — argmax فقط. محرك الـ scoring يستهلك احتمالات خام، لا labels. انظر `decisions.md` D41. |

---

## سجل التغييرات
- **v1.2 (9 يوليو 2026):** Phase 5 وُسمت ✅ COMPLETE بنتيجة PASSED مقابل D39 (C→E 3→0، E→C 1→0، Contradiction recall 16/19 بلا تغيّر) — التفاصيل في `decisions.md` D41، المخرجات الخام في `results/phase5/`. إضافة حاجز بدء صلب V2 على Phase 6 (الاحتمالات الخام مطلوبة قبل أي عمل على τ_E) في §6 وتحديث Phase 6 prompt في §7 ليطلب مخرجات احتمالية لا argmax. في §8: V1 أُغلقت (✅)، V2 أُضيفت كحاجز مفتوح على Phase 6، Q8 (Coverage Asymmetry) أصبحت ACTIVE بانتهاء تأجيل D34.
- **v1.1 (9 يوليو 2026):** تصحيح CS = Cybersecurity (كانت مكتوبة خطأً Computer Science — راجع Task 2f)؛ تحديث أسماء نوتبوكات Kaggle إلى الصيغة بالشرطة (`run-nli-finetune.ipynb` / `run-nli-eval.ipynb`) في §4 و§7؛ تصحيح baseline الـ Phase 5 إلى الذراع zero-shot على نفس الـ 48 زوج (D39) بدلًا من Demo #1؛ إغلاق Q1/Q4/Q5/Q9 بإحالة إلى `decisions.md`؛ إضافة بند V1 (تحقق الـ checkpoint) كحاجز على تشغيل Phase 5؛ إضافة القاعدة 13 (تجريبي ≠ مُستنتَج من config) إلى §5.
- **v1.0 (8 يوليو 2026):** الإصدار الأول.

---

*نهاية الوثيقة v1.2 — أي قرار سابق لم يظهر هنا أو تناقض داخلي: يُبلَّغ فورًا لإصدار جديد.*
