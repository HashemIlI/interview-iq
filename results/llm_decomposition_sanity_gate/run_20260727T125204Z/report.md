# D74 LLM Decomposition Sanity Gate — Review Report

- Run timestamp (UTC): 20260727T125204Z
- Model used (single model for entire run, per D77): `llama-3.3-70b-versatile`
- Git commit at run time: `02a016a649399f4ceb3daaf916ff99404d4fe391`
- Cases: 15 (15 executed successfully, 0 failed execution)

**Gate pass rule (D77):** PASS only if every case has `error_preserved=YES` AND `no_unauthorized_addition=YES`. Any single NO on either column fails the whole gate. `atomicity_verdict=NON_ATOMIC` is logged and tracked separately (non-blocking, per Q8-style handling) -- it does NOT fail the gate.

**Instructions for reviewer:** for each case, compare `input_answer_text` against `claims`, using `injected_error_anchor` as the reference for what the deliberate flaw was. Fill in the three verdict columns below in `report.csv` (or directly in `raw_results.json`), then record the final PASS/FAIL result as a D77 update or new D## in decisions.md.

## SG-01 — CS / WRONG_FACT

- **Execution status:** SUCCESS
- **Input (ASR-style):** طب يعني الهيب ده هو نوع من الداتا ستركتشر بيشتغل بنظام لايفو يعني آخر حاجة تتحط هي أول حاجة تتشال وعشان كده بنستخدمه في تخزين الـ function calls والـ recursion
- **Injected error anchor:** LIFO دي صفة الـ Stack مش الـ Heap، والـ recursion/function calls بيتخزنوا في الـ Call Stack مش الـ Heap. الغلطة لازم تفضل زي ما هي في الـ claims.
- **Latin terms expected:** heap, LIFO, function calls, recursion
- **Claims produced:**
  1. الهاش هو نوع من الداتا ستركتشر.
  2. الهاش بيشتغل بنظام لايفو.
  3. آخر حاجة تتحط في الهاش هي أول حاجة تتشال.
  4. نستخدم الهاش في تخزين الـ function calls.
  5. نستخدم الهاش في تخزين الـ recursion.

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___`

## SG-02 — CS / INCOMPLETE

- **Execution status:** SUCCESS
- **Input (ASR-style):** آه يعني الفرق بين البروسيس والثريد إن كل بروسيس ليها ميموري منفصلة عن باقي البروسيسز
- **Injected error anchor:** ناقصة: مفيش ذكر إن الـ threads بتشارك نفس الـ memory جوه نفس الـ process. المفروض الـ claims متحتويش على إضافة الجزء الناقص ده من عند الموديل.
- **Latin terms expected:** process, thread, memory
- **Claims produced:**
  1. الفرق بين البروسيس والثريد هو أن كل بروسيس لها ميموري منفصلة عن باقي البروسيسز.

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___`

## SG-03 — DS / WRONG_FACT

- **Execution status:** SUCCESS
- **Input (ASR-style):** يعني الأوفرفيتينج ده بيحصل لما الموديل يكون بسيط جدا جدا وما بيقدرش يمسك الـ patterns اللي في الداتا فبيدي أداء ضعيف
- **Injected error anchor:** ده تعريف الـ Underfitting مش الـ Overfitting (العكس: موديل معقد بيحفظ الـ noise). الغلطة لازم تفضل زي ما هي.
- **Latin terms expected:** overfitting, patterns
- **Claims produced:**
  1. الأوفرفيتينج يحدث عندما يكون الموديل بسيطًا جدًا.
  2. الموديل البسيط لا يستطيع مسك الأنماط في البيانات.
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
  1. الـ INNER JOIN في SQL تعيد الصفوف التي لها تطابق على العمود الذي يتم إجراء الجوين عليه.
  2. عند استخدام INNER JOIN بين جدولين، تعيد النتيجة فقط الصفوف التي لها تطابق على العمود المشترك.
  3. على سبيل المثال، عند استخدام INNER JOIN بين جدول Orders وجدول Customers، تعيد النتيجة فقط الأوردرات التي لها كستمر موجود فعلا.

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___`

## SG-07 — SE / BOTH

- **Execution status:** SUCCESS
- **Input (ASR-style):** يعني الفرق بين الميرج والريبيز في الجيت إن الريبيز بيدمج البرانشز من غير ما يغير الكوميت هيستوري خالص وده أأمن دايما من الميرج ومفيش داعي نتكلم عن الكونفليكتس لأن الجيت بيحلها لوحده
- **Injected error anchor:** غلطتين مع بعض: (1) الـ rebase فعليًا بيعيد كتابة الـ commit history (عكس الادعاء)، (2) الـ conflicts محتاجة تدخل يدوي غالبًا مش 'بيحلها لوحده'. الاتنين لازم يفضلوا زي ما هم غلط.
- **Latin terms expected:** Git, merge, rebase, branches, commit history, conflicts
- **Claims produced:**
  1. الريبيز في الجيت يدمج الفرع بدون تغيير تاريخ الكوميت.
  2. الريبيز أمان أكثر من الميرج دائمًا.
  3. الجيت يحل النزاعات تلقائيًا عند استخدام الريبيز.

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___`

## SG-08 — GN / BOTH

- **Execution status:** SUCCESS
- **Input (ASR-style):** يعني الفرق بين HTTP و HTTPS إن HTTPS بس نسخة أسرع من HTTP وبتستخدم نفس البورت ثمانين وبتشتغل بنفس الطريقة بالظبط من غير أي تشفير إضافي
- **Injected error anchor:** ثلاث غلطات: (1) الفرق الجوهري تشفير (TLS/SSL) مش سرعة، (2) البورت الافتراضي لـ HTTPS هو 443 مش 80، (3) 'من غير أي تشفير' تناقض مباشر مع تعريف HTTPS نفسه. الثلاثة لازم يفضلوا زي ما هم.
- **Latin terms expected:** HTTP, HTTPS
- **Claims produced:**
  1. الـ HTTPS هي نسخة أسرع من الـ HTTP.
  2. الـ HTTPS تستخدم نفس البورت 80.
  3. الـ HTTPS تعمل بنفس الطريقة مثل الـ HTTP.
  4. لا يوجد تشفير إضافي في الـ HTTPS.

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___`

## SG-09 — DA / NUMERIC_FACT

- **Execution status:** SUCCESS
- **Input (ASR-style):** يعني بص لما بعمل A/B testing عادة بحدد significance level يعني alpha بقيمة 0.5 يعني لو الـ p-value طلع أقل من كده بارفض الـ null hypothesis وأقول في فرق حقيقي بين النسختين
- **Injected error anchor:** قيمة alpha القياسية في A/B testing هي 0.05 مش 0.5 (خطأ فاصلة عشرية واقعي في ASR للعامية). الغلطة لازم تفضل زي ما هي (0.5) في الـ claims — القيمة الصحيحة 0.05 ما ينفعش تظهر في الإخراج. حالة D90 (نسخة مُستبدلة بعد مراجعة): رقم عشري في سياق إحصائي، بعيد تمامًا عن فئتي bit-width (GN-040, illustrative example 3) وport numbers (SG-08) لتجنب أي تداخل فئوي.
- **Latin terms expected:** A/B testing, alpha, p-value, null hypothesis
- **Claims produced:**
  1. عند إجراء اختبار A/B، يتم تحديد مستوى الدلالة (significance level) عادةً بقيمة 0.05.
  2. إذا كانت قيمة p-value أقل من 0.05، يتم رفض الفرضية الصفرية (null hypothesis) ويُقال إن هناك فرقًا حقيقيًا بين النسختين.

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___`

## SG-10 — SE / WRONG_FACT

- **Execution status:** SUCCESS
- **Input (ASR-style):** طيب يعني بص لو عايز تعمل TDD الأول المفروض تكتب الكود بتاعك الأول وبعدين تيجي تكتب التست عليه عشان تتأكد إنه شغال والداتا بيز بتاعتك المفروض تتوصل بيها من جوه التست
- **Injected error anchor:** TDD (Test-Driven Development) بالتعريف الفعلي: التست بيتكتب الأول قبل الكود عشان يوجه التطوير (دورة red-green-refactor). الإجابة عكست الترتيب (الكود الأول وبعدين التست) — دي غلطة واقعية لازم تفضل زي ما هي في الـ claims، من غير ما الموديل يصلحها للترتيب الصحيح أو يعلّق عليها.
- **Latin terms expected:** TDD, code, test, database
- **Claims produced:**
  1. عند عمل TDD، المفروض تكتب التست أولاً.
  2. بعد كتابة التست، تكتب الكود بتاعك.
  3. الغرض من كتابة التست قبل الكود هو للتأكد من أن الكود شغال بشكل صحيح.
  4. الداتا بيز المفروض تتوصل بيها من جوه التست.

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___`

## SG-11 — GN / NUMERIC_FACT

- **Execution status:** SUCCESS
- **Input (ASR-style):** طب يعني بص الـ بيت هو أصغر وحدة تخزين في الكمبيوتر وبعدين لما تجمع 16 من الـ بيت دول مع بعض بيبقى عندك وحدة أكبر اسمها برضو بيت وعشان كده بنقول إن البيت الكبير ده بيتكون من 16 بيت مش من 8
- **Injected error anchor:** الـ Byte الفعلي بيتكون من 8 bits مش 16. كلمة 'بيت' هنا استخدمت بشكل غامض للدلالة على كل من bit (الوحدة الصغيرة) و byte (الوحدة الأكبر المكوّنة من 16 منها) — تطابق شبه-حرفي حقيقي في الـ ASR المصري، تكرار متعمد لحالة GN-040 الميدانية (D94 C1 FAIL). المتحدث نفسه ذكر المقارنة بـ 8 كجزء من كلامه (مش إضافة من الموديل) — الـ claims لازم تحافظ على الرقم 16 والمقارنة بـ 8 بالظبط زي ما اتقالوا، من غير أي تعليق تفسيري أو تصحيحي إضافي من عند الموديل زي 'وليس 8 كما ذكر في الأصل' (ده بالضبط فشل D94 المزدوج: عدم حفظ + إضافة غير مصرح بها).
- **Latin terms expected:** bit, byte
- **Claims produced:**
  1. الـ بيت هو أصغر وحدة تخزين في الكمبيوتر.
  2. يُشكل جمع 16 بيت معًا وحدة أكبر تسمى أيضًا بيت.
  3. البيت الكبير يتكون من 16 بيت، وليس من 8.

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___`

## SG-12 — SE / NONE

- **Execution status:** SUCCESS
- **Input (ASR-style):** طب يعني بص أسلوب الـ تي دي دي ده معناه إنك تكتب التست الأول قبل ما تكتب أي كود يعني بتحدد الحاجة اللي عايز تتأكد منها الأول وبعدين تيجي تكتب أقل كود ممكن عشان يعديها
- **Injected error anchor:** لا توجد غلطة واقعية متعمدة في هذه الحالة — الغرض الأساسي اختبار تحويل الاختصار المهجأ حرفيًا (تي دي دي) دون أي إضافة أو حذف. error_preserved يُسجَّل N/A (لا توجد غلطة لتُحفظ)؛ no_unauthorized_addition يبقى قابلاً للتطبيق كاملاً.
- **Latin terms expected:** TDD, test, code
- **Claims produced:**
  1. أسلوب الـ TDD يعني كتابة التست قبل كتابة أي كود.
  2. يتم تحديد الحاجة التي يجب التأكد منها أولاً.
  3. ثم يتم كتابة أقل كود ممكن لتحقيقها.

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___`

## SG-13 — SE / INCOMPLETE

- **Execution status:** SUCCESS
- **Input (ASR-style):** طيب يعني في التطوير فيه خطوات بتتكرر يعني بتكتب كود وبعدين تعمل تست وبعدين تعدل وترجع تاني للخطوة الأولى اسمها يعني
- **Injected error anchor:** NO-ADDITION TEST (نوع جديد، P5): المتحدث بدأ يسمي الدورة ('اسمها يعني') وتوقف من غير ما يكمل الاسم أبدًا. هذه إعادة إنتاج مباشرة لـ D94 O-b (SE-028 claim 2 اخترع الموديل اسم 'دورة التطوير' من عنده رغم إن المتحدث ما سماهاش). الـ claims لازم تصف الخطوات (كتابة كود، عمل تست، تعديل، تكرار) من غير أي اسم يُنسب للدورة من عند الموديل — حتى لو الاسم بديهي أو شائع في الصناعة (زي 'Development Cycle' أو 'دورة التطوير').
- **Latin terms expected:** code, test
- **Claims produced:**
  1. في التطوير توجد خطوات متكررة.
  2. الخطوات المتكررة تتضمن كتابة الكود.
  3. بعد كتابة الكود، يتم إجراء الاختبار.
  4. بعد الاختبار، يتم تعديل الكود.
  5. بعد التعديل، يتم العودة إلى الخطوة الأولى.

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___`

## SG-14 — DS / WRONG_FACT

- **Execution status:** SUCCESS
- **Input (ASR-style):** يعني الاوفرفيتينج ده بيحصل لما الموديل يتدرب على الداتا سيت بتاعة التريننج ومايحفظش النويز اللي جواها هو بيتعلم الباترن العام بس وعشان كده لما نجربه على التيست سيت بيطلع اداؤه وحش قوي
- **Injected error anchor:** error_class: POLARITY. Polarity inversion on a true property: the speaker negates that the model memorises the training noise, and reinforces the inversion by asserting the model learns only the general pattern. The final clause (poor performance on the test set) is deliberately correct. Preservation requirement: the negation must survive into the claims exactly as uttered. Any claim asserting that the model memorises the noise is a silent correction and fails the gate.
- **Latin terms expected:** overfitting, training, noise, pattern, test set, data set
- **Claims produced:**
  1. الاوفرفيتينج يحدث عندما يتدرّب الموديل على مجموعة بيانات التدريب ولا يحفظ الضوضاء الموجودة فيها.
  2. الموديل يتعلم النمط العام من مجموعة بيانات التدريب.
  3. عند اختبار الموديل على مجموعة بيانات الاختبار، يظهر أداءه قويًا.

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___`

## SG-15 — SE / WRONG_FACT

- **Execution status:** SUCCESS
- **Input (ASR-style):** الديدلوك لما بيحصل في السيستم هو اللي بيسبب ان التريدز تمسك الريسورسيز وتستنى بعضها وكل واحد فيهم مستني التاني يسيب اللي معاه وعشان كده الابليكيشن بيقف مش بيرد
- **Injected error anchor:** error_class: CAUSAL_DIRECTION. Causal direction reversal with an explicit causal marker: the speaker makes deadlock the cause of the hold-and-wait condition, whereas hold-and-wait plus circular wait produce deadlock. The final clause (the application stops responding) is deliberately correct. Preservation requirement: the stated causal direction must survive into the claims exactly as uttered. Any claim that reverses it to the correct direction is a silent correction and fails the gate. Adding the Coffman conditions, or any domain knowledge not uttered, fails criterion 2.
- **Latin terms expected:** deadlock, system, thread, resource, application
- **Claims produced:**
  1. الديدلوك هو السبب في توقف التطبيق.
  2. الديدلوك يحدث عندما تمسك التريدز الريسورسيز وتنتظر بعضها البعض.
  3. كل ثريد مستني الثريد الآخر أن ي释ع الريسورس الذي يحتفظ به.
  4. هذا الوضع يؤدي إلى توقف التطبيق عن الاستجابة.

- **Verdict (fill in):** error_preserved = `___` | no_unauthorized_addition = `___` | atomicity_verdict = `___`
