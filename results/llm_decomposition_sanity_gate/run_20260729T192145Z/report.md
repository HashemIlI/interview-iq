# D74 LLM Decomposition Sanity Gate — Review Report

- Run timestamp (UTC): 20260729T192145Z
- Model used (single model for entire run, per D77): `llama-3.3-70b-versatile`
- Git commit at run time: `fc1925c5fd2780ad69d8bcef6082ef20ad37c21f`
- Cases: 15 (15 executed successfully, 0 failed execution)

**Gate pass rule (D77, extended by D101):** PASS only if every case has `error_preserved=YES` (or N/A where designated) AND `no_unauthorized_addition=YES`. Any single NO on either column fails the whole gate. `atomicity_verdict=NON_ATOMIC` is logged and tracked separately (non-blocking, per Q8-style handling) -- it does NOT fail the gate. `transliteration_correct` is recorded for all applicable cases per D101 but is non-blocking for this run.

**Instructions for reviewer (per D101):** `error_preserved`, `no_unauthorized_addition` and `atomicity_verdict` are judged on `claims_raw` -- the LLM output BEFORE `apply_glossary` -- comparable with D92/D96/D100. `transliteration_correct` is judged on `claims_final` -- the output AFTER `apply_glossary` -- using `transliteration_audit` and `latin_terms_expected` as the checklist. Compare each against `input_answer_text`, using `injected_error_anchor` as the reference for what the deliberate flaw was. Fill in the four verdict columns below in `report.csv` (or directly in `raw_results.json`), then record the final PASS/FAIL result as a D77/D101 update or new D## in decisions.md.

## SG-01 — CS / WRONG_FACT

- **Execution status:** SUCCESS
- **Input (ASR-style):** طب يعني الهيب ده هو نوع من الداتا ستركتشر بيشتغل بنظام لايفو يعني آخر حاجة تتحط هي أول حاجة تتشال وعشان كده بنستخدمه في تخزين الـ function calls والـ recursion
- **Injected error anchor:** LIFO دي صفة الـ Stack مش الـ Heap، والـ recursion/function calls بيتخزنوا في الـ Call Stack مش الـ Heap. الغلطة لازم تفضل زي ما هي في الـ claims.
- **Latin terms expected:** heap, LIFO, function calls, recursion
- **Claims produced (raw, pre-glossary -- judge error_preserved / no_unauthorized_addition / atomicity_verdict here):**
  1. الـ هيب هو نوع من الداتا ستركتشر.
  2. الـ هيب بيشتغل بنظام لايفو.
  3. آخر حاجة تتحط في الـ هيب هي أول حاجة تتشال.
  4. نستخدم الـ هيب في تخزين الـ function calls.
  5. نستخدم الـ هيب في تخزين الـ recursion.
- **Claims produced (final, post-glossary -- judge transliteration_correct here):**
  1. ال Heap هو نوع من Data ستركتشر.
  2. ال Heap بيشتغل بنظام LIFO.
  3. اخر حاجة تتحط في ال Heap هي اول حاجة تتشال.
  4. نستخدم ال Heap في تخزين ال function calls.
  5. نستخدم ال Heap في تخزين ال recursion.
- **Transliteration audit:** 7 substitution(s), 0 residual ambiguous form(s) left untouched.
  - claim 0: `هيب` → `Heap`
  - claim 0: `الداتا` → `Data`
  - claim 1: `هيب` → `Heap`
  - claim 1: `لايفو` → `LIFO`
  - claim 2: `هيب` → `Heap`
  - claim 3: `هيب` → `Heap`
  - claim 4: `هيب` → `Heap`

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___` | transliteration_correct = `___`

## SG-02 — CS / INCOMPLETE

- **Execution status:** SUCCESS
- **Input (ASR-style):** آه يعني الفرق بين البروسيس والثريد إن كل بروسيس ليها ميموري منفصلة عن باقي البروسيسز
- **Injected error anchor:** ناقصة: مفيش ذكر إن الـ threads بتشارك نفس الـ memory جوه نفس الـ process. المفروض الـ claims متحتويش على إضافة الجزء الناقص ده من عند الموديل.
- **Latin terms expected:** process, thread, memory
- **Claims produced (raw, pre-glossary -- judge error_preserved / no_unauthorized_addition / atomicity_verdict here):**
  1. الفرق بين البروسيس والثريد هو أن كل بروسيس لها ذاكرة منفصلة عن باقي البروسيسز.
- **Claims produced (final, post-glossary -- judge transliteration_correct here):**
  1. الفرق بين Process Thread هو ان كل Process لها ذاكرة منفصلة عن باقي البروسيسز.
- **Transliteration audit:** 3 substitution(s), 0 residual ambiguous form(s) left untouched.
  - claim 0: `البروسيس` → `Process`
  - claim 0: `والثريد` → `Thread`
  - claim 0: `بروسيس` → `Process`

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___` | transliteration_correct = `___`

## SG-03 — DS / WRONG_FACT

- **Execution status:** SUCCESS
- **Input (ASR-style):** يعني الأوفرفيتينج ده بيحصل لما الموديل يكون بسيط جدا جدا وما بيقدرش يمسك الـ patterns اللي في الداتا فبيدي أداء ضعيف
- **Injected error anchor:** ده تعريف الـ Underfitting مش الـ Overfitting (العكس: موديل معقد بيحفظ الـ noise). الغلطة لازم تفضل زي ما هي.
- **Latin terms expected:** overfitting, patterns
- **Claims produced (raw, pre-glossary -- judge error_preserved / no_unauthorized_addition / atomicity_verdict here):**
  1. الأوفرفيتينج يحدث عندما يكون الموديل بسيطًا جدًا.
  2. الموديل البسيط لا يستطيع مسك الأنماط في البيانات.
  3. الموديل البسيط يؤدي أداءً ضعيفًا.
- **Claims produced (final, post-glossary -- judge transliteration_correct here):**
  1. الاوفرفيتينج يحدث عندما يكون الموديل بسيطا جدا.
  2. الموديل البسيط لا يستطيع مسك الانماط في البيانات.
  3. الموديل البسيط يؤدي اداء ضعيفا.
- **Transliteration audit:** 0 substitution(s), 0 residual ambiguous form(s) left untouched.

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___` | transliteration_correct = `___`

## SG-04 — DS / INCOMPLETE

- **Execution status:** SUCCESS
- **Input (ASR-style):** طب لما بنقيم موديل الكلاسيفيكيشن بنبص على البريسيجن يعني هي عدد التوقعات الصح من إجمالي اللي الموديل قال إنها بوزيتيف وده أهم مقياس عندي عشان أعرف الموديل شغال كويس ولا لأ
- **Injected error anchor:** NO-ADDITION TEST: مفيش ذكر لـ recall خالص في الإجابة. الاختبار هنا مختلف عن الباقي — مش بس 'هل الغلط فضل غلط' لكن كمان 'هل الموديل هيضيف claim عن recall من عنده رغم إنه مش موجود في الإدخال'. recall لازم يفضل غايب تمامًا من الـ output.
- **Latin terms expected:** classification, precision, positive
- **Claims produced (raw, pre-glossary -- judge error_preserved / no_unauthorized_addition / atomicity_verdict here):**
  1. نقيم موديل الكلاسيفيكيشن بناءً على البريسيجن.
  2. البريسيجن هو عدد التوقعات الصحيحة من إجمالي التوقعات التي قال فيها الموديل إنها بوزيتيف.
  3. البريسيجن هو أهم مقياس لي لتحديد ما إذا كان الموديل يعمل جيدًا أم لا.
- **Claims produced (final, post-glossary -- judge transliteration_correct here):**
  1. نقيم موديل Classification بناء على Precision.
  2. Precision هو عدد التوقعات الصحيحة من اجمالي التوقعات التي قال فيها الموديل انها بوزيتيف.
  3. Precision هو اهم مقياس لي لتحديد ما اذا كان الموديل يعمل جيدا ام لا.
- **Transliteration audit:** 4 substitution(s), 0 residual ambiguous form(s) left untouched.
  - claim 0: `الكلاسيفيكيشن` → `Classification`
  - claim 0: `البريسيجن` → `Precision`
  - claim 1: `البريسيجن` → `Precision`
  - claim 2: `البريسيجن` → `Precision`

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___` | transliteration_correct = `___`

## SG-05 — DA / WRONG_FACT

- **Execution status:** SUCCESS
- **Input (ASR-style):** يعني الـ Normalization بتحول البيانات عشان يبقى المتوسط صفر والانحراف المعياري واحد أما الـ Standardization بتحول القيم لمدى بين صفر وواحد
- **Injected error anchor:** التعريفين مقلوبين: اللي اتوصف إنه Normalization هو تعريف الـ Standardization والعكس. الغلطة لازم تفضل زي ما هي.
- **Latin terms expected:** Normalization, Standardization
- **Claims produced (raw, pre-glossary -- judge error_preserved / no_unauthorized_addition / atomicity_verdict here):**
  1. الـ Normalization تحول البيانات لجعل المتوسط صفر والانحراف المعياري واحد.
  2. الـ Standardization تحول القيم إلى مدى بين صفر وواحد.
- **Claims produced (final, post-glossary -- judge transliteration_correct here):**
  1. ال Normalization تحول البيانات لجعل المتوسط صفر والانحراف المعياري واحد.
  2. ال Standardization تحول القيم الى مدى بين صفر وواحد.
- **Transliteration audit:** 0 substitution(s), 0 residual ambiguous form(s) left untouched.

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___` | transliteration_correct = `___`

## SG-06 — DA / INCOMPLETE

- **Execution status:** SUCCESS
- **Input (ASR-style):** طب في الـ SQL لما بنستخدم INNER JOIN بين جدولين بيرجعلنا بس الصفوف اللي ليها تطابق على العمود اللي بنعمل عليه الجوين يعني مثلا لو عندي جدول Orders وجدول Customers الـ INNER JOIN هيجيب بس الأوردرات اللي ليها كستمر موجود فعلا
- **Injected error anchor:** NO-ADDITION TEST: مفيش ذكر لـ LEFT JOIN خالص في الإجابة. LEFT JOIN لازم يفضل غايب تمامًا من الـ output — الموديل ممنوع يضيفه من عنده حتى لو 'منطقيًا' كان متوقع كجزء من سؤال المقارنة.
- **Latin terms expected:** SQL, INNER JOIN, Orders, Customers
- **Claims produced (raw, pre-glossary -- judge error_preserved / no_unauthorized_addition / atomicity_verdict here):**
  1. الـ INNER JOIN في SQL تعيد الصفوف التي لها تطابق على العمود الذي يتم إجراء الجوين عليه.
  2. عند استخدام INNER JOIN بين جدولين، تعيد النتائج فقط الصفوف التي لها تطابق على العمود المشترك.
  3. على سبيل المثال، عند استخدام INNER JOIN بين جدول Orders وجدول Customers، تعيد النتائج فقط الأوردرات التي لها كستمر موجود فعلا.
- **Claims produced (final, post-glossary -- judge transliteration_correct here):**
  1. ال INNER JOIN في SQL تعيد الصفوف التي لها تطابق على العمود الذي يتم اجراء JOIN عليه.
  2. عند استخدام INNER JOIN بين جدولين، تعيد النتائج فقط الصفوف التي لها تطابق على العمود المشترك.
  3. على سبيل المثال، عند استخدام INNER JOIN بين جدول Orders وجدول Customers، تعيد النتائج فقط الاوردرات التي لها كستمر موجود فعلا.
- **Transliteration audit:** 1 substitution(s), 0 residual ambiguous form(s) left untouched.
  - claim 0: `الجوين` → `JOIN`

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___` | transliteration_correct = `___`

## SG-07 — SE / BOTH

- **Execution status:** SUCCESS
- **Input (ASR-style):** يعني الفرق بين الميرج والريبيز في الجيت إن الريبيز بيدمج البرانشز من غير ما يغير الكوميت هيستوري خالص وده أأمن دايما من الميرج ومفيش داعي نتكلم عن الكونفليكتس لأن الجيت بيحلها لوحده
- **Injected error anchor:** غلطتين مع بعض: (1) الـ rebase فعليًا بيعيد كتابة الـ commit history (عكس الادعاء)، (2) الـ conflicts محتاجة تدخل يدوي غالبًا مش 'بيحلها لوحده'. الاتنين لازم يفضلوا زي ما هم غلط.
- **Latin terms expected:** Git, merge, rebase, branches, commit history, conflicts
- **Claims produced (raw, pre-glossary -- judge error_preserved / no_unauthorized_addition / atomicity_verdict here):**
  1. الريبيز في الجيت بيدمج البرانشز من غير ما يغير تاريخ الكوميت.
  2. الريبيز أأمن دائمًا من الميرج.
  3. الجيت يحل الكونفليكتس لوحده عند استخدام الريبيز.
- **Claims produced (final, post-glossary -- judge transliteration_correct here):**
  1. Rebase في الجيت بيدمج Branches من غير ما يغير تاريخ Commit.
  2. Rebase اامن دائما من Merge.
  3. الجيت يحل الكونفليكتس لوحده عند استخدام Rebase.
- **Transliteration audit:** 6 substitution(s), 2 residual ambiguous form(s) left untouched.
  - claim 0: `الريبيز` → `Rebase`
  - claim 0: `البرانشز` → `Branches`
  - claim 0: `الكوميت` → `Commit`
  - claim 1: `الريبيز` → `Rebase`
  - claim 1: `الميرج` → `Merge`
  - claim 2: `الريبيز` → `Rebase`

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___` | transliteration_correct = `___`

## SG-08 — GN / BOTH

- **Execution status:** SUCCESS
- **Input (ASR-style):** يعني الفرق بين HTTP و HTTPS إن HTTPS بس نسخة أسرع من HTTP وبتستخدم نفس البورت ثمانين وبتشتغل بنفس الطريقة بالظبط من غير أي تشفير إضافي
- **Injected error anchor:** ثلاث غلطات: (1) الفرق الجوهري تشفير (TLS/SSL) مش سرعة، (2) البورت الافتراضي لـ HTTPS هو 443 مش 80، (3) 'من غير أي تشفير' تناقض مباشر مع تعريف HTTPS نفسه. الثلاثة لازم يفضلوا زي ما هم.
- **Latin terms expected:** HTTP, HTTPS
- **Claims produced (raw, pre-glossary -- judge error_preserved / no_unauthorized_addition / atomicity_verdict here):**
  1. الـ HTTPS هي نسخة أسرع من الـ HTTP.
  2. الـ HTTPS تستخدم نفس البورت 80.
  3. الـ HTTPS تعمل بنفس الطريقة مثل الـ HTTP بدون أي تشفير إضافي.
- **Claims produced (final, post-glossary -- judge transliteration_correct here):**
  1. ال HTTPS هي نسخة اسرع من ال HTTP.
  2. ال HTTPS تستخدم نفس البورت 80.
  3. ال HTTPS تعمل بنفس الطريقة مثل ال HTTP بدون اي تشفير اضافي.
- **Transliteration audit:** 0 substitution(s), 0 residual ambiguous form(s) left untouched.

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___` | transliteration_correct = `___`

## SG-09 — DA / NUMERIC_FACT

- **Execution status:** SUCCESS
- **Input (ASR-style):** يعني بص لما بعمل A/B testing عادة بحدد significance level يعني alpha بقيمة 0.5 يعني لو الـ p-value طلع أقل من كده بارفض الـ null hypothesis وأقول في فرق حقيقي بين النسختين
- **Injected error anchor:** قيمة alpha القياسية في A/B testing هي 0.05 مش 0.5 (خطأ فاصلة عشرية واقعي في ASR للعامية). الغلطة لازم تفضل زي ما هي (0.5) في الـ claims — القيمة الصحيحة 0.05 ما ينفعش تظهر في الإخراج. حالة D90 (نسخة مُستبدلة بعد مراجعة): رقم عشري في سياق إحصائي، بعيد تمامًا عن فئتي bit-width (GN-040, illustrative example 3) وport numbers (SG-08) لتجنب أي تداخل فئوي.
- **Latin terms expected:** A/B testing, alpha, p-value, null hypothesis
- **Claims produced (raw, pre-glossary -- judge error_preserved / no_unauthorized_addition / atomicity_verdict here):**
  1. عند إجراء اختبار A/B، يحدد عادةً مستوى الدلالة (significance level) أو Alpha بقيمة 0.5.
  2. إذا كانت قيمة p-value أقل من 0.5، يرفض الـ null hypothesis.
  3. عند رفض الـ null hypothesis، يُقال إن هناك فرقًا حقيقيًا بين النسختين.
- **Claims produced (final, post-glossary -- judge transliteration_correct here):**
  1. عند اجراء اختبار A/B، يحدد عادة مستوى الدلالة (significance level) او Alpha بقيمة 0.5.
  2. اذا كانت قيمة p-value اقل من 0.5، يرفض ال null hypothesis.
  3. عند رفض ال null hypothesis، يقال ان هناك فرقا حقيقيا بين النسختين.
- **Transliteration audit:** 0 substitution(s), 0 residual ambiguous form(s) left untouched.

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___` | transliteration_correct = `___`

## SG-10 — SE / WRONG_FACT

- **Execution status:** SUCCESS
- **Input (ASR-style):** طيب يعني بص لو عايز تعمل TDD الأول المفروض تكتب الكود بتاعك الأول وبعدين تيجي تكتب التست عليه عشان تتأكد إنه شغال والداتا بيز بتاعتك المفروض تتوصل بيها من جوه التست
- **Injected error anchor:** TDD (Test-Driven Development) بالتعريف الفعلي: التست بيتكتب الأول قبل الكود عشان يوجه التطوير (دورة red-green-refactor). الإجابة عكست الترتيب (الكود الأول وبعدين التست) — دي غلطة واقعية لازم تفضل زي ما هي في الـ claims، من غير ما الموديل يصلحها للترتيب الصحيح أو يعلّق عليها.
- **Latin terms expected:** TDD, code, test, database
- **Claims produced (raw, pre-glossary -- judge error_preserved / no_unauthorized_addition / atomicity_verdict here):**
  1. عند عمل TDD، المفروض تكتب التست قبل الكود.
  2. التست بيتم كتابته قبل الكود عشان يتأكد إنه شغال.
  3. الداتا المفروض تتوصل بيها من جوه التست.
- **Claims produced (final, post-glossary -- judge transliteration_correct here):**
  1. عند عمل TDD، المفروض تكتب Test قبل Code.
  2. Test بيتم كتابته قبل Code عشان يتاكد انه شغال.
  3. Data المفروض تتوصل بيها من جوه Test.
- **Transliteration audit:** 6 substitution(s), 0 residual ambiguous form(s) left untouched.
  - claim 0: `التست` → `Test`
  - claim 0: `الكود` → `Code`
  - claim 1: `التست` → `Test`
  - claim 1: `الكود` → `Code`
  - claim 2: `الداتا` → `Data`
  - claim 2: `التست` → `Test`

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___` | transliteration_correct = `___`

## SG-11 — GN / NUMERIC_FACT

- **Execution status:** SUCCESS
- **Input (ASR-style):** طب يعني بص الـ بيت هو أصغر وحدة تخزين في الكمبيوتر وبعدين لما تجمع 16 من الـ بيت دول مع بعض بيبقى عندك وحدة أكبر اسمها برضو بيت وعشان كده بنقول إن البيت الكبير ده بيتكون من 16 بيت مش من 8
- **Injected error anchor:** الـ Byte الفعلي بيتكون من 8 bits مش 16. كلمة 'بيت' هنا استخدمت بشكل غامض للدلالة على كل من bit (الوحدة الصغيرة) و byte (الوحدة الأكبر المكوّنة من 16 منها) — تطابق شبه-حرفي حقيقي في الـ ASR المصري، تكرار متعمد لحالة GN-040 الميدانية (D94 C1 FAIL). المتحدث نفسه ذكر المقارنة بـ 8 كجزء من كلامه (مش إضافة من الموديل) — الـ claims لازم تحافظ على الرقم 16 والمقارنة بـ 8 بالظبط زي ما اتقالوا، من غير أي تعليق تفسيري أو تصحيحي إضافي من عند الموديل زي 'وليس 8 كما ذكر في الأصل' (ده بالضبط فشل D94 المزدوج: عدم حفظ + إضافة غير مصرح بها).
- **Latin terms expected:** bit, byte
- **Claims produced (raw, pre-glossary -- judge error_preserved / no_unauthorized_addition / atomicity_verdict here):**
  1. الـ بيت هو أصغر وحدة تخزين في الكمبيوتر.
  2. يُشكل جمع 16 بيت معًا وحدة أكبر تسمى بيت.
  3. البيت الكبير يتكون من 16 بيت، وليس من 8.
- **Claims produced (final, post-glossary -- judge transliteration_correct here):**
  1. ال bit هو اصغر وحدة تخزين في Computer.
  2. يشكل جمع 16 bit معا وحدة اكبر تسمى bit.
  3. bit الكبير يتكون من 16 bit، وليس من 8.
- **Transliteration audit:** 6 substitution(s), 0 residual ambiguous form(s) left untouched.
  - claim 0: `بيت` → `bit`
  - claim 0: `الكمبيوتر` → `Computer`
  - claim 1: `بيت` → `bit`
  - claim 1: `بيت` → `bit`
  - claim 2: `البيت` → `bit`
  - claim 2: `بيت` → `bit`

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___` | transliteration_correct = `___`

## SG-12 — SE / NONE

- **Execution status:** SUCCESS
- **Input (ASR-style):** طب يعني بص أسلوب الـ تي دي دي ده معناه إنك تكتب التست الأول قبل ما تكتب أي كود يعني بتحدد الحاجة اللي عايز تتأكد منها الأول وبعدين تيجي تكتب أقل كود ممكن عشان يعديها
- **Injected error anchor:** لا توجد غلطة واقعية متعمدة في هذه الحالة — الغرض الأساسي اختبار تحويل الاختصار المهجأ حرفيًا (تي دي دي) دون أي إضافة أو حذف. error_preserved يُسجَّل N/A (لا توجد غلطة لتُحفظ)؛ no_unauthorized_addition يبقى قابلاً للتطبيق كاملاً.
- **Latin terms expected:** TDD, test, code
- **Claims produced (raw, pre-glossary -- judge error_preserved / no_unauthorized_addition / atomicity_verdict here):**
  1. أسلوب الـ TDD يعني كتابة التست قبل كتابة أي كود.
  2. يتم تحديد الحاجة التي يجب التأكد منها أولاً.
  3. ثم يتم كتابة أقل كود ممكن لاجتياز التست.
- **Claims produced (final, post-glossary -- judge transliteration_correct here):**
  1. اسلوب ال TDD يعني كتابة Test قبل كتابة اي Code.
  2. يتم تحديد الحاجة التي يجب التاكد منها اولا.
  3. ثم يتم كتابة اقل Code ممكن لاجتياز Test.
- **Transliteration audit:** 4 substitution(s), 0 residual ambiguous form(s) left untouched.
  - claim 0: `التست` → `Test`
  - claim 0: `كود` → `Code`
  - claim 2: `كود` → `Code`
  - claim 2: `التست` → `Test`

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___` | transliteration_correct = `___`

## SG-13 — SE / INCOMPLETE

- **Execution status:** SUCCESS
- **Input (ASR-style):** طيب يعني في التطوير فيه خطوات بتتكرر يعني بتكتب كود وبعدين تعمل تست وبعدين تعدل وترجع تاني للخطوة الأولى اسمها يعني
- **Injected error anchor:** NO-ADDITION TEST (نوع جديد، P5): المتحدث بدأ يسمي الدورة ('اسمها يعني') وتوقف من غير ما يكمل الاسم أبدًا. هذه إعادة إنتاج مباشرة لـ D94 O-b (SE-028 claim 2 اخترع الموديل اسم 'دورة التطوير' من عنده رغم إن المتحدث ما سماهاش). الـ claims لازم تصف الخطوات (كتابة كود، عمل تست، تعديل، تكرار) من غير أي اسم يُنسب للدورة من عند الموديل — حتى لو الاسم بديهي أو شائع في الصناعة (زي 'Development Cycle' أو 'دورة التطوير').
- **Latin terms expected:** code, test
- **Claims produced (raw, pre-glossary -- judge error_preserved / no_unauthorized_addition / atomicity_verdict here):**
  1. في التطوير، هناك خطوات متكررة.
  2. الخطوات المتكررة تتضمن كتابة الكود.
  3. بعد كتابة الكود، يتم إجراء الاختبار.
  4. بعد الاختبار، يتم التعديل.
  5. بعد التعديل، يتم العودة إلى الخطوة الأولى.
- **Claims produced (final, post-glossary -- judge transliteration_correct here):**
  1. في التطوير، هناك خطوات متكررة.
  2. الخطوات المتكررة تتضمن كتابة Code.
  3. بعد كتابة Code، يتم اجراء الاختبار.
  4. بعد الاختبار، يتم التعديل.
  5. بعد التعديل، يتم العودة الى الخطوة الاولى.
- **Transliteration audit:** 2 substitution(s), 0 residual ambiguous form(s) left untouched.
  - claim 1: `الكود` → `Code`
  - claim 2: `الكود` → `Code`

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___` | transliteration_correct = `___`

## SG-14 — DS / WRONG_FACT

- **Execution status:** SUCCESS
- **Input (ASR-style):** يعني الاوفرفيتينج ده بيحصل لما الموديل يتدرب على الداتا سيت بتاعة التريننج ومايحفظش النويز اللي جواها هو بيتعلم الباترن العام بس وعشان كده لما نجربه على التيست سيت بيطلع اداؤه وحش قوي
- **Injected error anchor:** error_class: POLARITY. Polarity inversion on a true property: the speaker negates that the model memorises the training noise, and reinforces the inversion by asserting the model learns only the general pattern. The final clause (poor performance on the test set) is deliberately correct. Preservation requirement: the negation must survive into the claims exactly as uttered. Any claim asserting that the model memorises the noise is a silent correction and fails the gate.
- **Latin terms expected:** overfitting, training, noise, pattern, test set, data set
- **Claims produced (raw, pre-glossary -- judge error_preserved / no_unauthorized_addition / atomicity_verdict here):**
  1. الاوفرفيتينج يحدث عندما يتدرب الموديل على مجموعة بيانات التدريب ويتعلم النمط العام دون حفظ الضوضاء الموجودة فيها.
  2. عندما يتم اختبار الموديل على مجموعة بيانات الاختبار، يظهر أداءه بشكل قوي.
- **Claims produced (final, post-glossary -- judge transliteration_correct here):**
  1. الاوفرفيتينج يحدث عندما يتدرب الموديل على مجموعة بيانات التدريب ويتعلم النمط العام دون حفظ الضوضاء الموجودة فيها.
  2. عندما يتم اختبار الموديل على مجموعة بيانات الاختبار، يظهر اداءه بشكل قوي.
- **Transliteration audit:** 0 substitution(s), 0 residual ambiguous form(s) left untouched.

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___` | transliteration_correct = `___`

## SG-15 — SE / WRONG_FACT

- **Execution status:** SUCCESS
- **Input (ASR-style):** الديدلوك لما بيحصل في السيستم هو اللي بيسبب ان التريدز تمسك الريسورسيز وتستنى بعضها وكل واحد فيهم مستني التاني يسيب اللي معاه وعشان كده الابليكيشن بيقف مش بيرد
- **Injected error anchor:** error_class: CAUSAL_DIRECTION. Causal direction reversal with an explicit causal marker: the speaker makes deadlock the cause of the hold-and-wait condition, whereas hold-and-wait plus circular wait produce deadlock. The final clause (the application stops responding) is deliberately correct. Preservation requirement: the stated causal direction must survive into the claims exactly as uttered. Any claim that reverses it to the correct direction is a silent correction and fails the gate. Adding the Coffman conditions, or any domain knowledge not uttered, fails criterion 2.
- **Latin terms expected:** deadlock, system, thread, resource, application
- **Claims produced (raw, pre-glossary -- judge error_preserved / no_unauthorized_addition / atomicity_verdict here):**
  1. الديدلوك هو السبب في حدوث التمسك بالموارد في النظام.
  2. التريدز تمسك الموارد وتنتظر بعضها البعض.
  3. كل تريد مستني التريد الآخر أن ي释ع الموارد التي يحتفظ بها.
  4. بسبب ذلك، تتعطل الابليكيشن ولا ترد.
- **Claims produced (final, post-glossary -- judge transliteration_correct here):**
  1. Deadlock هو السبب في حدوث التمسك بالموارد في النظام.
  2. التريدز تمسك الموارد وتنتظر بعضها البعض.
  3. كل تريد مستني التريد الاخر ان ي释ع الموارد التي يحتفظ بها.
  4. بسبب ذلك، تتعطل Application ولا ترد.
- **Transliteration audit:** 2 substitution(s), 0 residual ambiguous form(s) left untouched.
  - claim 0: `الديدلوك` → `Deadlock`
  - claim 3: `الابليكيشن` → `Application`

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___` | transliteration_correct = `___`
