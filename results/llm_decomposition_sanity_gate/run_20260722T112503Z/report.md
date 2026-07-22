# D74 LLM Decomposition Sanity Gate — Review Report

- Run timestamp (UTC): 20260722T112503Z
- Model used (single model for entire run, per D77): `llama-3.3-70b-versatile`
- Git commit at run time: `1b1e6c3a9ee5b596297615fdc96157336a61fe8d`
- Cases: 8 (8 executed successfully, 0 failed execution)

**Gate pass rule (D77):** PASS only if every case has `error_preserved=YES` AND `no_unauthorized_addition=YES`. Any single NO on either column fails the whole gate. `atomicity_verdict=NON_ATOMIC` is logged and tracked separately (non-blocking, per Q8-style handling) -- it does NOT fail the gate.

**Instructions for reviewer:** for each case, compare `input_answer_text` against `claims`, using `injected_error_anchor` as the reference for what the deliberate flaw was. Fill in the three verdict columns below in `report.csv` (or directly in `raw_results.json`), then record the final PASS/FAIL result as a D77 update or new D## in decisions.md.

## SG-01 — CS / WRONG_FACT

- **Execution status:** SUCCESS
- **Input (ASR-style):** طب يعني الهيب ده هو نوع من الداتا ستركتشر بيشتغل بنظام لايفو يعني آخر حاجة تتحط هي أول حاجة تتشال وعشان كده بنستخدمه في تخزين الـ function calls والـ recursion
- **Injected error anchor:** LIFO دي صفة الـ Stack مش الـ Heap، والـ recursion/function calls بيتخزنوا في الـ Call Stack مش الـ Heap. الغلطة لازم تفضل زي ما هي في الـ claims.
- **Latin terms expected:** heap, LIFO, function calls, recursion
- **Claims produced:**
  1. الهايب هو نوع من الداتا ستركتشر.
  2. الهايب يشتغل بنظام لايفو.
  3. آخر حاجة تتحط في الهايب هي أول حاجة تتشال.
  4. نستخدم الهايب في تخزين الـ function calls.
  5. نستخدم الهايب في تخزين الـ recursion.

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___`

## SG-02 — CS / INCOMPLETE

- **Execution status:** SUCCESS
- **Input (ASR-style):** آه يعني الفرق بين البروسيس والثريد إن كل بروسيس ليها ميموري منفصلة عن باقي البروسيسز
- **Injected error anchor:** ناقصة: مفيش ذكر إن الـ threads بتشارك نفس الـ memory جوه نفس الـ process. المفروض الـ claims متحتويش على إضافة الجزء الناقص ده من عند الموديل.
- **Latin terms expected:** process, thread, memory
- **Claims produced:**
  1. الفرق بين البروسيس والثريد هو أن كل بروسيس لها ذاكرة منفصلة عن باقي البروسيسز.

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___`

## SG-03 — DS / WRONG_FACT

- **Execution status:** SUCCESS
- **Input (ASR-style):** يعني الأوفرفيتينج ده بيحصل لما الموديل يكون بسيط جدا جدا وما بيقدرش يمسك الـ patterns اللي في الداتا فبيدي أداء ضعيف
- **Injected error anchor:** ده تعريف الـ Underfitting مش الـ Overfitting (العكس: موديل معقد بيحفظ الـ noise). الغلطة لازم تفضل زي ما هي.
- **Latin terms expected:** overfitting, patterns
- **Claims produced:**
  1. الأوفرفيتينج يحدث عندما يكون الموديل بسيطًا جدًا.
  2. الموديل البسيط لا يستطيع مسك الأنماط في الداتا.
  3. الموديل البسيط يؤدي أداءً ضعيفًا.

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___`

## SG-04 — DS / INCOMPLETE

- **Execution status:** SUCCESS
- **Input (ASR-style):** طب لما بنقيم موديل الكلاسيفيكيشن بنبص على البريسيجن يعني هي عدد التوقعات الصح من إجمالي اللي الموديل قال إنها بوزيتيف وده أهم مقياس عندي عشان أعرف الموديل شغال كويس ولا لأ
- **Injected error anchor:** NO-ADDITION TEST: مفيش ذكر لـ recall خالص في الإجابة. الاختبار هنا مختلف عن الباقي — مش بس 'هل الغلط فضل غلط' لكن كمان 'هل الموديل هيضيف claim عن recall من عنده رغم إنه مش موجود في الإدخال'. recall لازم يفضل غايب تمامًا من الـ output.
- **Latin terms expected:** classification, precision, positive
- **Claims produced:**
  1. نقيم موديل الكلاسيفيكيشن بناءً على البريسيجن.
  2. البريسيجن هو عدد التوقعات الصحيحة من إجمالي التوقعات التي قال فيها الموديل إنها بوزيتيف.
  3. البريسيجن هو أهم مقياس لي لتحديد ما إذا كان الموديل يعمل جيدًا أم لا.

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___`

## SG-05 — DA / WRONG_FACT

- **Execution status:** SUCCESS
- **Input (ASR-style):** يعني الـ Normalization بتحول البيانات عشان يبقى المتوسط صفر والانحراف المعياري واحد أما الـ Standardization بتحول القيم لمدى بين صفر وواحد
- **Injected error anchor:** التعريفين مقلوبين: اللي اتوصف إنه Normalization هو تعريف الـ Standardization والعكس. الغلطة لازم تفضل زي ما هي.
- **Latin terms expected:** Normalization, Standardization
- **Claims produced:**
  1. الـ Normalization هي عملية تحويل البيانات بحيث يصبح المتوسط صفر والانحراف المعياري واحد.
  2. الـ Standardization هي عملية تحويل القيم إلى مدى بين صفر وواحد.

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___`

## SG-06 — DA / INCOMPLETE

- **Execution status:** SUCCESS
- **Input (ASR-style):** طب في الـ SQL لما بنستخدم INNER JOIN بين جدولين بيرجعلنا بس الصفوف اللي ليها تطابق على العمود اللي بنعمل عليه الجوين يعني مثلا لو عندي جدول Orders وجدول Customers الـ INNER JOIN هيجيب بس الأوردرات اللي ليها كستمر موجود فعلا
- **Injected error anchor:** NO-ADDITION TEST: مفيش ذكر لـ LEFT JOIN خالص في الإجابة. LEFT JOIN لازم يفضل غايب تمامًا من الـ output — الموديل ممنوع يضيفه من عنده حتى لو 'منطقيًا' كان متوقع كجزء من سؤال المقارنة.
- **Latin terms expected:** SQL, INNER JOIN, Orders, Customers
- **Claims produced:**
  1. الـ INNER JOIN في الـ SQL تعيد الصفوف التي لها تطابق على العمود الذي يتم إجراء الجوين عليه.
  2. عند استخدام الـ INNER JOIN بين جدولين، يتم إرجاع الصفوف التي لها تطابق فقط.
  3. على سبيل المثال، إذا كان هناك جدول Orders وجدول Customers، فإن الـ INNER JOIN سيعيد الأوردرات التي لها كستمر موجود فعلا في جدول Customers.

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___`

## SG-07 — SE / BOTH

- **Execution status:** SUCCESS
- **Input (ASR-style):** يعني الفرق بين الميرج والريبيز في الجيت إن الريبيز بيدمج البرانشز من غير ما يغير الكوميت هيستوري خالص وده أأمن دايما من الميرج ومفيش داعي نتكلم عن الكونفليكتس لأن الجيت بيحلها لوحده
- **Injected error anchor:** غلطتين مع بعض: (1) الـ rebase فعليًا بيعيد كتابة الـ commit history (عكس الادعاء)، (2) الـ conflicts محتاجة تدخل يدوي غالبًا مش 'بيحلها لوحده'. الاتنين لازم يفضلوا زي ما هم غلط.
- **Latin terms expected:** Git, merge, rebase, branches, commit history, conflicts
- **Claims produced:**
  1. الريبيز في الجيت يدمج الفروع بدون تغيير تاريخ الكوميت.
  2. الريبيز أمن أكثر من الميرج دائمًا.
  3. الجيت يحل النزاعات تلقائيًا عند استخدام الريبيز، لذلك لا يوجد حاجة للنقاش حولها.

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___`

## SG-08 — GN / BOTH

- **Execution status:** SUCCESS
- **Input (ASR-style):** يعني الفرق بين HTTP و HTTPS إن HTTPS بس نسخة أسرع من HTTP وبتستخدم نفس البورت ثمانين وبتشتغل بنفس الطريقة بالظبط من غير أي تشفير إضافي
- **Injected error anchor:** ثلاث غلطات: (1) الفرق الجوهري تشفير (TLS/SSL) مش سرعة، (2) البورت الافتراضي لـ HTTPS هو 443 مش 80، (3) 'من غير أي تشفير' تناقض مباشر مع تعريف HTTPS نفسه. الثلاثة لازم يفضلوا زي ما هم.
- **Latin terms expected:** HTTP, HTTPS
- **Claims produced:**
  1. الـ HTTPS هي نسخة أسرع من الـ HTTP.
  2. الـ HTTPS تستخدم نفس البورت 80.
  3. الـ HTTPS تشتغل بنفس الطريقة مثل الـ HTTP.
  4. لا يوجد تشفير إضافي في الـ HTTPS.

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___`
