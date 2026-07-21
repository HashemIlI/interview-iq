# D74 LLM Decomposition Sanity Gate — Review Report

- Run timestamp (UTC): 20260721T092636Z
- Model used (single model for entire run, per D77): `nvidia/nemotron-3-nano-30b-a3b:free`
- Git commit at run time: `ea34b36c4f5a18ff4d43d89fe13eef7e7823793f`
- Cases: 8 (7 executed successfully, 1 failed execution)

**Gate pass rule (D77):** PASS only if every case has `error_preserved=YES` AND `no_unauthorized_addition=YES`. Any single NO on either column fails the whole gate. `atomicity_verdict=NON_ATOMIC` is logged and tracked separately (non-blocking, per Q8-style handling) -- it does NOT fail the gate.

**Instructions for reviewer:** for each case, compare `input_answer_text` against `claims`, using `injected_error_anchor` as the reference for what the deliberate flaw was. Fill in the three verdict columns below in `report.csv` (or directly in `raw_results.json`), then record the final PASS/FAIL result as a D77 update or new D## in decisions.md.

## SG-01 — CS / WRONG_FACT

- **Execution status:** UNEXPECTED_ERROR
- **Error:** `JSONDecodeError: Expecting value: line 1587 column 1 (char 8723)`
- **Input (ASR-style):** طب يعني الهيب ده هو نوع من الداتا ستركتشر بيشتغل بنظام لايفو يعني آخر حاجة تتحط هي أول حاجة تتشال وعشان كده بنستخدمه في تخزين الـ function calls والـ recursion
- **Injected error anchor:** LIFO دي صفة الـ Stack مش الـ Heap، والـ recursion/function calls بيتخزنوا في الـ Call Stack مش الـ Heap. الغلطة لازم تفضل زي ما هي في الـ claims.
- **Latin terms expected:** heap, LIFO, function calls, recursion
- **Claims produced:**
  (none -- execution failed or NO_EXTRACTABLE_CLAIMS)

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___`

## SG-02 — CS / INCOMPLETE

- **Execution status:** SUCCESS
- **Input (ASR-style):** آه يعني الفرق بين البروسيس والثريد إن كل بروسيس ليها ميموري منفصلة عن باقي البروسيسز
- **Injected error anchor:** ناقصة: مفيش ذكر إن الـ threads بتشارك نفس الـ memory جوه نفس الـ process. المفروض الـ claims متحتويش على إضافة الجزء الناقص ده من عند الموديل.
- **Latin terms expected:** process, thread, memory
- **Claims produced:**
  1. الفرق بين process والخيط هو أن كل process لها memory منفصلة عن باقي العمليات

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___`

## SG-03 — DS / WRONG_FACT

- **Execution status:** SUCCESS
- **Input (ASR-style):** يعني الأوفرفيتينج ده بيحصل لما الموديل يكون بسيط جدا جدا وما بيقدرش يمسك الـ patterns اللي في الداتا فبيدي أداء ضعيف
- **Injected error anchor:** ده تعريف الـ Underfitting مش الـ Overfitting (العكس: موديل معقد بيحفظ الـ noise). الغلطة لازم تفضل زي ما هي.
- **Latin terms expected:** overfitting, patterns
- **Claims produced:**
  1. overfitting يحدث عندما يكون الموديل بسيطًا جدًا.
  2. الموديل لا يستطيع أن يمسك الـ patterns اللي في data.
  3. الـ overfitting يؤدي إلى أداء ضعيف.

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___`

## SG-04 — DS / INCOMPLETE

- **Execution status:** SUCCESS
- **Input (ASR-style):** طب لما بنقيم موديل الكلاسيفيكيشن بنبص على البريسيجن يعني هي عدد التوقعات الصح من إجمالي اللي الموديل قال إنها بوزيتيف وده أهم مقياس عندي عشان أعرف الموديل شغال كويس ولا لأ
- **Injected error anchor:** NO-ADDITION TEST: مفيش ذكر لـ recall خالص في الإجابة. الاختبار هنا مختلف عن الباقي — مش بس 'هل الغلط فضل غلط' لكن كمان 'هل الموديل هيضيف claim عن recall من عنده رغم إنه مش موجود في الإدخال'. recall لازم يفضل غايب تمامًا من الـ output.
- **Latin terms expected:** classification, precision, positive
- **Claims produced:**
  1. عندما نقيّم classification model نظر إلى الـ precision
  2. الـ precision هي عدد التنبؤات الصحيحة من إجمالي التنبؤات التي صُنفت إيجابية
  3. الـ precision هو أهم مقياس لمعرفة ما إذا كان classification model يعمل بشكل جيد أم لا

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___`

## SG-05 — DA / WRONG_FACT

- **Execution status:** SUCCESS
- **Input (ASR-style):** يعني الـ Normalization بتحول البيانات عشان يبقى المتوسط صفر والانحراف المعياري واحد أما الـ Standardization بتحول القيم لمدى بين صفر وواحد
- **Injected error anchor:** التعريفين مقلوبين: اللي اتوصف إنه Normalization هو تعريف الـ Standardization والعكس. الغلطة لازم تفضل زي ما هي.
- **Latin terms expected:** Normalization, Standardization
- **Claims produced:**
  1. الـ Normalization تحول البيانات لتصبح المتوسط صفرًا.
  2. الـ Normalization تحول البيانات لتصبح الانحراف المعياري مساويًا واحدًا.
  3. الـ Standardization تحول القيم لتتراوح بين صفر وواحد.

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___`

## SG-06 — DA / INCOMPLETE

- **Execution status:** SUCCESS
- **Input (ASR-style):** طب في الـ SQL لما بنستخدم INNER JOIN بين جدولين بيرجعلنا بس الصفوف اللي ليها تطابق على العمود اللي بنعمل عليه الجوين يعني مثلا لو عندي جدول Orders وجدول Customers الـ INNER JOIN هيجيب بس الأوردرات اللي ليها كستمر موجود فعلا
- **Injected error anchor:** NO-ADDITION TEST: مفيش ذكر لـ LEFT JOIN خالص في الإجابة. LEFT JOIN لازم يفضل غايب تمامًا من الـ output — الموديل ممنوع يضيفه من عنده حتى لو 'منطقيًا' كان متوقع كجزء من سؤال المقارنة.
- **Latin terms expected:** SQL, INNER JOIN, Orders, Customers
- **Claims produced:**
  1. في SQL عندما نستخدم INNER JOIN بين جدولين يُستخرج فقط الصفوف التي تتطابق في العمود المستخدم للجOIN.
  2. مثال على ذلك إذا كان لدينا جدول Orders وجدول Customers فإن INNER JOIN يُستخرج فقط الطلبات التي لديها عميل موجود بالفعل.

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___`

## SG-07 — SE / BOTH

- **Execution status:** SUCCESS
- **Input (ASR-style):** يعني الفرق بين الميرج والريبيز في الجيت إن الريبيز بيدمج البرانشز من غير ما يغير الكوميت هيستوري خالص وده أأمن دايما من الميرج ومفيش داعي نتكلم عن الكونفليكتس لأن الجيت بيحلها لوحده
- **Injected error anchor:** غلطتين مع بعض: (1) الـ rebase فعليًا بيعيد كتابة الـ commit history (عكس الادعاء)، (2) الـ conflicts محتاجة تدخل يدوي غالبًا مش 'بيحلها لوحده'. الاتنين لازم يفضلوا زي ما هم غلط.
- **Latin terms expected:** Git, merge, rebase, branches, commit history, conflicts
- **Claims produced:**
  1. الفرق بين الميرج والريبيز في الجيت
  2. الريبيز يدمج الفروع بدون تغيير الكوميت هيستوري خالص
  3. الريبيز أأمن دايماً من الميرج
  4. لا يوجد داعي للحديث عن الكونفليكتس
  5. الجيت يحلها لوحده

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___`

## SG-08 — GN / BOTH

- **Execution status:** SUCCESS
- **Input (ASR-style):** يعني الفرق بين HTTP و HTTPS إن HTTPS بس نسخة أسرع من HTTP وبتستخدم نفس البورت ثمانين وبتشتغل بنفس الطريقة بالظبط من غير أي تشفير إضافي
- **Injected error anchor:** ثلاث غلطات: (1) الفرق الجوهري تشفير (TLS/SSL) مش سرعة، (2) البورت الافتراضي لـ HTTPS هو 443 مش 80، (3) 'من غير أي تشفير' تناقض مباشر مع تعريف HTTPS نفسه. الثلاثة لازم يفضلوا زي ما هم.
- **Latin terms expected:** HTTP, HTTPS
- **Claims produced:**
  1. HTTPS هو نسخة أسرع من HTTP.
  2. HTTPS يستخدم نفس البورت 80.
  3. HTTPS يعمل بنفس الطريقة تمامًا دون أي تشفير إضافي.

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___`
