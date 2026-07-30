# D82 Coverage Channel Real-Claims Experiment — Report

- Run timestamp (UTC): 20260730T073157Z
- Git commit at run time: `1f9a68c6686125496e2680848cd28aa361bf296e`
- Decomposition model (single model for entire run, per D77 convention): `openai/gpt-oss-120b`
- NLI base model: `MoritzLaurer/mDeBERTa-v3-base-mnli-xnli`
- Adapter checkpoint: `/kaggle/input/models/hashemili/interview-iq-nli-lora/transformers/checkpoint27-mdeberta-v3-lora/1/iq-checkpoints-nli-v1`
- Questions: 25 (25 decomposed successfully, 0 decomposition failures)
- Coverage arms (D107 four-arm design): zero_shot_raw 25/25 scored, zero_shot_final 25/25 scored, adapter_raw 25/25 scored, adapter_final 25/25 scored

**Read this as a directional first reading (n=25), not a statistical result (D82/D107 pre-registered constraint).** Per the D107 four-arm design, this compares {zero-shot, adapter} against {claims_raw, claims_final} on real claims.

## DA-001 (DA)

- **Decomposition status:** SUCCESS
- **Raw answer:** الـ Structured data يعني البيانات اللي منظمة في شكل جدول، صفوف وأعمدة، زي اللي بتلاقيها في database عادي أو Excel. بتكون ليها schema ثابت من الأول، كل عمود نوعه معروف، وده بيخليها سهلة إنك تعمل عليها query بـ SQL. أما الـ Unstructured فالعكس، مفيهاش شكل ثابت، زي الصور والفيديوهات والنصوص الحرة والإيميلات، ومفيهاش schema من الأول، فبتحتاج أدوات تانية زي NoSQL أو تقنيات NLP. وفيه كمان Semi-structured زي JSON وXML، في النص بين الاتنين.
- **Claims (raw, pre-glossary):**
  1. Structured data هي البيانات التي منظمة في شكل جدول يتكون من صفوف وأعمدة.
  2. Structured data توجد في قاعدة بيانات عادية أو في Excel.
  3. Structured data لها schema ثابت من البداية.
  4. في Structured data كل عمود نوعه معروف.
  5. وجود schema ثابت يجعل Structured data سهلة لتطبيق query باستخدام SQL.
  6. Unstructured data هي العكس ولا تحتوي على شكل ثابت.
  7. Unstructured data تشمل الصور والفيديوهات والنصوص الحرة والإيميلات.
  8. Unstructured data لا تحتوي على schema من البداية.
  9. Unstructured data تحتاج إلى أدوات أخرى مثل NoSQL أو تقنيات NLP.
  10. هناك نوع Semi-structured data مثل JSON و XML.
  11. Semi-structured data يقع بين Structured data و Unstructured data.
- **Claims (final, post-glossary, D101):**
  1. Structured data هي البيانات التي منظمة في شكل جدول يتكون من صفوف واعمدة.
  2. Structured data توجد في قاعدة بيانات عادية او في Excel.
  3. Structured data لها schema ثابت من البداية.
  4. في Structured data كل عمود نوعه معروف.
  5. وجود schema ثابت يجعل Structured data سهلة لتطبيق query باستخدام SQL.
  6. Unstructured data هي العكس ولا تحتوي على شكل ثابت.
  7. Unstructured data تشمل الصور والفيديوهات والنصوص الحرة والايميلات.
  8. Unstructured data لا تحتوي على schema من البداية.
  9. Unstructured data تحتاج الى ادوات اخرى مثل NoSQL او تقنيات NLP.
  10. هناك نوع Semi-structured data مثل JSON و XML.
  11. Semi-structured data يقع بين Structured data و Unstructured data.
- **Transliteration audit:** 0 substitution(s), 0 residual ambiguous form(s) left untouched.
- **Key points:** 3 (DA001-C01, DA001-C02, DA001-C04)
- **zero_shot_raw arm:** status=SUCCESS, coverage_score=0.7220393333333334
  - per-key-point max P(entailment): [0.174906, 0.997966, 0.993246]
- **zero_shot_final arm:** status=SUCCESS, coverage_score=0.7487879999999999
  - per-key-point max P(entailment): [0.255076, 0.998042, 0.993246]
- **adapter_raw arm:** status=SUCCESS, coverage_score=0.4915563333333333
  - per-key-point max P(entailment): [0.061226, 0.969241, 0.444202]
- **adapter_final arm:** status=SUCCESS, coverage_score=0.49371800000000005
  - per-key-point max P(entailment): [0.066846, 0.970106, 0.444202]

## DA-002 (DA)

- **Decomposition status:** SUCCESS
- **Raw answer:** أول حاجة Data Collection، تجميع البيانات من مصادرها. بعدين Data Cleaning، وده أهم جزء غالبًا، بتشيل فيه القيم الناقصة والـ duplicates والأخطاء. بعد كده Data Exploration أو EDA، بتستكشف فيها البيانات بالرسم البياني والإحصاء الوصفي. بعدين Data Transformation أو Feature Engineering لتجهيز البيانات. بعد كده Analysis أو Modeling. وآخر حاجة Interpretation والـ Visualization لعرض النتائج لصانع القرار.
- **Claims (raw, pre-glossary):**
  1. Data Collection هو جمع البيانات من مصادرها.
  2. Data Cleaning هو تنظيف البيانات.
  3. المتحدث يصف أن Data Cleaning هو أهم جزء غالبًا.
  4. في Data Cleaning يتم إزالة القيم الناقصة.
  5. في Data Cleaning يتم إزالة الـ duplicates.
  6. في Data Cleaning يتم إزالة الأخطاء.
  7. Data Exploration أو EDA هو استكشاف البيانات باستخدام الرسم البياني والإحصاء الوصفي.
  8. Data Transformation أو Feature Engineering هو تجهيز البيانات.
  9. Analysis أو Modeling هو تحليل أو نمذجة البيانات.
  10. Interpretation والـ Visualization هو عرض النتائج لصانع القرار.
- **Claims (final, post-glossary, D101):**
  1. Data Collection هو جمع البيانات من مصادرها.
  2. Data Cleaning هو تنظيف البيانات.
  3. المتحدث يصف ان Data Cleaning هو اهم جزء غالبا.
  4. في Data Cleaning يتم ازالة القيم الناقصة.
  5. في Data Cleaning يتم ازالة ال duplicates.
  6. في Data Cleaning يتم ازالة الاخطاء.
  7. Data Exploration او EDA هو استكشاف البيانات باستخدام الرسم البياني والاحصاء الوصفي.
  8. Data Transformation او Feature Engineering هو تجهيز البيانات.
  9. Analysis او Modeling هو تحليل او نمذجة البيانات.
  10. Interpretation وال Visualization هو عرض النتائج لصانع القرار.
- **Transliteration audit:** 0 substitution(s), 0 residual ambiguous form(s) left untouched.
- **Key points:** 4 (DA002-C01, DA002-C03, DA002-C04, DA002-C06)
- **zero_shot_raw arm:** status=SUCCESS, coverage_score=0.006747
  - per-key-point max P(entailment): [0.010217, 0.009452, 0.005872, 0.001447]
- **zero_shot_final arm:** status=SUCCESS, coverage_score=0.006857
  - per-key-point max P(entailment): [0.015087, 0.00503, 0.005995, 0.001316]
- **adapter_raw arm:** status=SUCCESS, coverage_score=0.00601825
  - per-key-point max P(entailment): [0.014556, 0.003956, 0.004706, 0.000855]
- **adapter_final arm:** status=SUCCESS, coverage_score=0.00644825
  - per-key-point max P(entailment): [0.01574, 0.004169, 0.005009, 0.000875]

## DA-029 (DA)

- **Decomposition status:** SUCCESS
- **Raw answer:** الـ p-value بصراحة دي حاجة دايمًا بتلخبطني. إحنا في الكلية أخدناها في مادة الإحصاء بس صراحة أنا بستخدمها بشكل عملي أكتر ما بفهمها نظريًا. يعني اللي أنا حافظه إنك بتبص على الرقم، لو أقل من 0.05 يبقى تمام، النتيجة معتبرة. والفكرة على ما أعتقد إن الرقم ده بيقولك احتمال إن الفرضية الصفرية تكون صحيحة، فلو طلع صغير يبقى الاحتمال ده ضعيف فبترفضها. الـ 0.05 دي هي المتعارف عليها في أغلب الأبحاث. والدلالة الإحصائية… يعني بالنسبة لي هي إن النتيجة معتبرة ومش صدفة، بس مش هقدر أديك تعريف رياضي دقيق ليها.
- **Claims (raw, pre-glossary):**
  1. الـ p-value شيء يربك المتحدث دائمًا.
  2. المتحدث أخذ الـ p-value في مادة الإحصاء في الكلية.
  3. المتحدث يستخدم الـ p-value عمليًا أكثر مما يفهمه نظريًا.
  4. المتحدث يعتقد أنه يجب النظر إلى الرقم، وإذا كان أقل من 0.05 تكون النتيجة معتبرة.
  5. المتحدث يعتقد أن الرقم يعبّر عن احتمال أن تكون الفرضية الصفرية صحيحة.
  6. المتحدث يعتقد أنه إذا كان الرقم صغيرًا يكون الاحتمال ضعيفًا فيُرفض الفرضية الصفرية.
  7. المتحدث يقول إن الـ 0.05 هو المستوى المتعارف عليه في أغلب الأبحاث.
  8. بالنسبة للمتحدث، الدلالة الإحصائية هي أن النتيجة معتبرة وغير صدفة.
  9. المتحدث لا يستطيع إعطاء تعريف رياضي دقيق للدلالة الإحصائية.
- **Claims (final, post-glossary, D101):**
  1. ال p-value شيء يربك المتحدث دائما.
  2. المتحدث اخذ ال p-value في مادة الاحصاء في الكلية.
  3. المتحدث يستخدم ال p-value عمليا اكثر مما يفهمه نظريا.
  4. المتحدث يعتقد انه يجب النظر الى الرقم، واذا كان اقل من 0.05 تكون النتيجة معتبرة.
  5. المتحدث يعتقد ان الرقم يعبر عن احتمال ان تكون الفرضية الصفرية صحيحة.
  6. المتحدث يعتقد انه اذا كان الرقم صغيرا يكون الاحتمال ضعيفا فيرفض الفرضية الصفرية.
  7. المتحدث يقول ان ال 0.05 هو المستوى المتعارف عليه في اغلب الابحاث.
  8. بالنسبة للمتحدث، الدلالة الاحصائية هي ان النتيجة معتبرة وغير صدفة.
  9. المتحدث لا يستطيع اعطاء تعريف رياضي دقيق للدلالة الاحصائية.
- **Transliteration audit:** 0 substitution(s), 0 residual ambiguous form(s) left untouched.
- **Key points:** 3 (DA029-C01, DA029-C03, DA029-C04)
- **zero_shot_raw arm:** status=SUCCESS, coverage_score=0.282312
  - per-key-point max P(entailment): [0.381189, 0.003461, 0.462286]
- **zero_shot_final arm:** status=SUCCESS, coverage_score=0.38724566666666665
  - per-key-point max P(entailment): [0.437526, 0.00375, 0.720461]
- **adapter_raw arm:** status=SUCCESS, coverage_score=0.032897666666666665
  - per-key-point max P(entailment): [0.029577, 0.012812, 0.056304]
- **adapter_final arm:** status=SUCCESS, coverage_score=0.035752
  - per-key-point max P(entailment): [0.031198, 0.013851, 0.062207]

## DA-036 (DA)

- **Decomposition status:** SUCCESS
- **Raw answer:** بستخدم الاتنين كتير في شغلي على الـ داتا فريم. باختصار الـوك اسمه جاي من اللابل باس يعني بتديله اسم الـ index او اسم العمود بالظبط، مثلا `df.loc[5, 'salary']` هنا الـ 5 دي label مش ترتيب. اما الـ iloc فهو integer location بتديله رقم الموضع، `df.iloc[0]` يعني اول صف مهما كان اسمه. وفيه فرق مهم بيلخبط الناس: لو عملت `df.loc[2:5]` هترجعلك الصف رقم 5 كمان لان الـ loc inclusive للطرفين، لكن `df.iloc[2:5]` هتوقف عند 4.
- **Claims (raw, pre-glossary):**
  1. يستخدم المتحدث الـ loc والـ iloc كثيرًا في عمله على الـ DataFrame.
  2. اسم الـ loc يأتي من label‑based.
  3. الـ loc يُعطى اسم الـ index أو اسم العمود بالضبط.
  4. في المثال df.loc[5, 'salary'] الرقم 5 هو label وليس ترتيبًا.
  5. الـ iloc هو integer‑location.
  6. الـ iloc يُعطى رقم الموضع.
  7. في المثال df.iloc[0] يعني أول صف مهما كان اسمه.
  8. إذا استُخدم df.loc[2:5] يعيد الصف رقم 5 أيضًا لأن الـ loc شامل للطرفين.
  9. إذا استُخدم df.iloc[2:5] يتوقف عند 4.
- **Claims (final, post-glossary, D101):**
  1. يستخدم المتحدث ال loc وال iloc كثيرا في عمله على ال DataFrame.
  2. اسم ال loc ياتي من label‑based.
  3. ال loc يعطى اسم ال index او اسم العمود بالضبط.
  4. في المثال df.loc[5, 'salary'] الرقم 5 هو label وليس ترتيبا.
  5. ال iloc هو integer‑location.
  6. ال iloc يعطى رقم الموضع.
  7. في المثال df.iloc[0] يعني اول صف مهما كان اسمه.
  8. اذا استخدم df.loc[2:5] يعيد الصف رقم 5 ايضا لان ال loc شامل للطرفين.
  9. اذا استخدم df.iloc[2:5] يتوقف عند 4.
- **Transliteration audit:** 0 substitution(s), 0 residual ambiguous form(s) left untouched.
- **Key points:** 2 (DA036-C01, DA036-C02)
- **zero_shot_raw arm:** status=SUCCESS, coverage_score=0.1450905
  - per-key-point max P(entailment): [0.005058, 0.285123]
- **zero_shot_final arm:** status=SUCCESS, coverage_score=0.125303
  - per-key-point max P(entailment): [0.00483, 0.245776]
- **adapter_raw arm:** status=SUCCESS, coverage_score=0.0922105
  - per-key-point max P(entailment): [0.019796, 0.164625]
- **adapter_final arm:** status=SUCCESS, coverage_score=0.065138
  - per-key-point max P(entailment): [0.017084, 0.113192]

## DA-046 (DA)

- **Decomposition status:** SUCCESS
- **Raw answer:** الـ Time Series ببساطة أي متغيّر بتتابع قيمته على فترات زمنية متتالية، والترتيب هنا مهم جدا، مينفعش تعمل shuffle للبيانات زي ما بتعمل في أي dataset عادي. ولما بنحلّلها بنفكّكها لأربع حاجات: الـ Trend، ده الاتجاه طويل المدى؛ والـ Seasonality، ده نمط بيتكرر كل فترة ثابتة معروفة زي كل سنة أو كل أسبوع؛ والـ Cyclical component اللي بيتكرر بردو بس على فترات مش ثابتة الطول؛ وفي الآخر الـ Residual أو الـ Noise، اللي هو الجزء العشوائي اللي مقدرناش نفسّره. وأعتقد إن الفصل بين الـ Seasonality والـ Cyclicity من أكتر الحاجات اللي بيغلط فيها الناس.
- **Claims (raw, pre-glossary):**
  1. السلسلة الزمنية (Time Series) هي أي متغيّر يتتابع قيمه على فترات زمنية متتالية.
  2. الترتيب مهم جدًا في السلسلة الزمنية.
  3. لا يجوز خلط البيانات (shuffle) في السلسلة الزمنية كما يحدث في أي مجموعة بيانات عادية.
  4. عند تحليل السلسلة الزمنية يتم تفكيكها إلى أربعة مكونات.
  5. المكوّن الأول هو الاتجاه (Trend) وهو الاتجاه طويل المدى.
  6. المكوّن الثاني هو الموسمية (Seasonality) وهي نمط يتكرر كل فترة ثابتة معروفة مثل كل سنة أو كل أسبوع.
  7. المكوّن الثالث هو المكوّن الدوري (Cyclical component) وهو يتكرر أيضًا لكن على فترات غير ثابتة الطول.
  8. المكوّن الرابع هو المتبقي (Residual) أو الضوضاء (Noise) وهو الجزء العشوائي الذي لم نستطع تفسيره.
  9. الفصل بين الموسمية والدورية هو أحد أكثر الأخطاء التي يرتكبها الناس.
- **Claims (final, post-glossary, D101):**
  1. السلسلة الزمنية (Time Series) هي اي متغير يتتابع قيمه على فترات زمنية متتالية.
  2. الترتيب مهم جدا في السلسلة الزمنية.
  3. لا يجوز خلط البيانات (shuffle) في السلسلة الزمنية كما يحدث في اي مجموعة بيانات عادية.
  4. عند تحليل السلسلة الزمنية يتم تفكيكها الى اربعة مكونات.
  5. المكون الاول هو الاتجاه (Trend) وهو الاتجاه طويل المدى.
  6. المكون الثاني هو الموسمية (Seasonality) وهي نمط يتكرر كل فترة ثابتة معروفة مثل كل سنة او كل اسبوع.
  7. المكون الثالث هو المكون الدوري (Cyclical component) وهو يتكرر ايضا لكن على فترات غير ثابتة الطول.
  8. المكون الرابع هو المتبقي (Residual) او الضوضاء (Noise) وهو الجزء العشوائي الذي لم نستطع تفسيره.
  9. الفصل بين الموسمية والدورية هو احد اكثر الاخطاء التي يرتكبها الناس.
- **Transliteration audit:** 0 substitution(s), 0 residual ambiguous form(s) left untouched.
- **Key points:** 3 (DA046-C01, DA046-C02, DA046-C03)
- **zero_shot_raw arm:** status=SUCCESS, coverage_score=0.347103
  - per-key-point max P(entailment): [0.991672, 0.049069, 0.000568]
- **zero_shot_final arm:** status=SUCCESS, coverage_score=0.35655366666666666
  - per-key-point max P(entailment): [0.994937, 0.074105, 0.000619]
- **adapter_raw arm:** status=SUCCESS, coverage_score=0.10165566666666666
  - per-key-point max P(entailment): [0.257327, 0.045875, 0.001765]
- **adapter_final arm:** status=SUCCESS, coverage_score=0.14589133333333335
  - per-key-point max P(entailment): [0.391905, 0.044121, 0.001648]

## DS-008 (DS)

- **Decomposition status:** SUCCESS
- **Raw answer:** الـ KNN دي أسهل حاجة اتعلمتها. تخيل عندك نقط على رسمة، وجالك نقطة جديدة عايز تعرف هي بتاعت أنهي مجموعة. بتبص على أقرب K نقطة ليها، ولو أغلبهم أحمر يبقى هي حمرا. بس كده. المسافة بتتحسب بالـ Euclidean يعني نظرية فيثاغورس عادي. والـ K لازم تبقى رقم فردي عشان لو حصل تعادل ما نبقاش تايهين. وحاجة مهمة إنه مبيتدربش أصلًا، يعني مفيش training، هو بس بيخزّن الداتا ولما ييجي وقت الـ prediction بيبدأ يحسب، وعشان كده بطيء لو الداتا كبيرة.
- **Claims (raw, pre-glossary):**
  1. الـ KNN هو أسهل شيء تعلمته.
  2. لديك نقاط على رسم.
  3. تظهر لك نقطة جديدة تريد معرفة المجموعة التي تنتمي إليها.
  4. تنظر إلى أقرب K نقاط إلى النقطة الجديدة.
  5. إذا كان أغلب هذه النقاط أقرب أحمرًا فإن النقطة الجديدة تكون حمراء.
  6. تُحسب المسافة باستخدام Euclidean أي وفق نظرية فيثاغورس العادية.
  7. يجب أن يكون K رقمًا فرديًا لتجنب التعادل وعدم الضياع.
  8. الـ KNN لا يتدرب أصلاً ولا يوجد training.
  9. الـ KNN يقتصر على تخزين البيانات.
  10. عند وقت الـ prediction يبدأ الـ KNN بالحساب.
  11. الـ KNN يكون بطيئًا إذا كانت البيانات كبيرة.
- **Claims (final, post-glossary, D101):**
  1. ال KNN هو اسهل شيء تعلمته.
  2. لديك نقاط على رسم.
  3. تظهر لك نقطة جديدة تريد معرفة المجموعة التي تنتمي اليها.
  4. تنظر الى اقرب K نقاط الى النقطة الجديدة.
  5. اذا كان اغلب هذه النقاط اقرب احمرا فان النقطة الجديدة تكون حمراء.
  6. تحسب المسافة باستخدام Euclidean اي وفق نظرية فيثاغورس العادية.
  7. يجب ان يكون K رقما فرديا لتجنب التعادل وعدم الضياع.
  8. ال KNN لا يتدرب اصلا ولا يوجد training.
  9. ال KNN يقتصر على تخزين البيانات.
  10. عند وقت ال prediction يبدا ال KNN بالحساب.
  11. ال KNN يكون بطيئا اذا كانت البيانات كبيرة.
- **Transliteration audit:** 0 substitution(s), 0 residual ambiguous form(s) left untouched.
- **Key points:** 2 (DS008-C01, DS008-C03)
- **zero_shot_raw arm:** status=SUCCESS, coverage_score=0.19789099999999998
  - per-key-point max P(entailment): [0.356191, 0.039591]
- **zero_shot_final arm:** status=SUCCESS, coverage_score=0.245762
  - per-key-point max P(entailment): [0.471756, 0.019768]
- **adapter_raw arm:** status=SUCCESS, coverage_score=0.052925
  - per-key-point max P(entailment): [0.063685, 0.042165]
- **adapter_final arm:** status=SUCCESS, coverage_score=0.0695135
  - per-key-point max P(entailment): [0.087146, 0.051881]

## DS-010 (DS)

- **Decomposition status:** SUCCESS
- **Raw answer:** أشهر طريقة هي الـ Elbow Method، بترسم فيها الـ WCSS (within-cluster sum of squares) مقابل قيم k مختلفة، وبتدور على النقطة اللي شكلها زي الكوع. في كمان الـ Silhouette Score، بيقيس تماسك النقاط جوه الـ cluster مقارنة بأقرب cluster تاني، والقيمة القريبة من 1 معناها clustering كويس. وفيه الـ Gap Statistic اللي بتقارن الأداء بأداء بيانات random. بس في الآخر القرار مش رياضي بحت، لازم يتاخد في الاعتبار الـ domain knowledge.
- **Claims (raw, pre-glossary):**
  1. أشهر طريقة هي Elbow Method.
  2. في Elbow Method يتم رسم الـ WCSS (within-cluster sum of squares) مقابل قيم k مختلفة.
  3. في Elbow Method يتم البحث عن النقطة التي شكلها مثل الكوع.
  4. هناك أيضاً Silhouette Score.
  5. Silhouette Score يقيس تماسك النقاط داخل الـ cluster مقارنة بأقرب cluster آخر.
  6. القيمة القريبة من 1 في Silhouette Score تعني أن الـ clustering جيد.
  7. هناك أيضاً Gap Statistic.
  8. Gap Statistic يقارن الأداء بأداء بيانات random.
  9. في النهاية القرار ليس رياضيًا بحتًا ويجب أخذ الـ domain knowledge في الاعتبار.
- **Claims (final, post-glossary, D101):**
  1. اشهر طريقة هي Elbow Method.
  2. في Elbow Method يتم رسم ال WCSS (within-cluster sum of squares) مقابل قيم k مختلفة.
  3. في Elbow Method يتم البحث عن النقطة التي شكلها مثل الكوع.
  4. هناك ايضا Silhouette Score.
  5. Silhouette Score يقيس تماسك النقاط داخل ال cluster مقارنة باقرب cluster اخر.
  6. القيمة القريبة من 1 في Silhouette Score تعني ان ال clustering جيد.
  7. هناك ايضا Gap Statistic.
  8. Gap Statistic يقارن الاداء باداء بيانات random.
  9. في النهاية القرار ليس رياضيا بحتا ويجب اخذ ال domain knowledge في الاعتبار.
- **Transliteration audit:** 0 substitution(s), 0 residual ambiguous form(s) left untouched.
- **Key points:** 2 (DS010-C01, DS010-C03)
- **zero_shot_raw arm:** status=SUCCESS, coverage_score=0.0376205
  - per-key-point max P(entailment): [0.073423, 0.001818]
- **zero_shot_final arm:** status=SUCCESS, coverage_score=0.0665035
  - per-key-point max P(entailment): [0.131296, 0.001711]
- **adapter_raw arm:** status=SUCCESS, coverage_score=0.0176815
  - per-key-point max P(entailment): [0.025626, 0.009737]
- **adapter_final arm:** status=SUCCESS, coverage_score=0.019989
  - per-key-point max P(entailment): [0.030943, 0.009035]

## DS-011 (DS)

- **Decomposition status:** SUCCESS
- **Raw answer:** الـ SVM (Support Vector Machine) موديل تصنيف بيحاول يلاقي أفضل hyperplane يفصل بين الفئات، وبيعظّم الـ margin بينها وبين أقرب نقاط ليها (support vectors). المشكلة إن مش كل البيانات قابلة للفصل بخط مستقيم في الـ space الأصلي. وهنا بييجي دور الـ Kernel Trick، بيخليك تحسب الـ similarity بين النقاط زي لو كانت متحوّلة لـ space أعلى الأبعاد، من غير ما فعليًا تعمل التحويل، وده بيوفر حسابات كتير. من أشهر الـ kernels: RBF kernel وpolynomial kernel.
- **Claims (raw, pre-glossary):**
  1. الـ SVM (Support Vector Machine) هو نموذج تصنيف يحاول إيجاد أفضل hyperplane يفصل بين الفئات.
  2. الـ SVM يعظم الـ margin بين الفئات وأقرب نقاط لها (support vectors).
  3. ليست كل البيانات قابلة للفصل بخط مستقيم في الـ space الأصلي.
  4. الـ Kernel Trick يتيح حساب الـ similarity بين النقاط كما لو كانت محولة إلى space أعلى الأبعاد دون إجراء التحويل فعليًا.
  5. الـ Kernel Trick يوفر حسابات كثيرة.
  6. من أشهر الـ kernels هو RBF kernel.
  7. من أشهر الـ kernels هو polynomial kernel.
- **Claims (final, post-glossary, D101):**
  1. ال SVM (Support Vector Machine) هو نموذج تصنيف يحاول ايجاد افضل hyperplane يفصل بين الفئات.
  2. ال SVM يعظم ال margin بين الفئات واقرب نقاط لها (support vectors).
  3. ليست كل البيانات قابلة للفصل بخط مستقيم في ال space الاصلي.
  4. ال Kernel Trick يتيح حساب ال similarity بين النقاط كما لو كانت محولة الى space اعلى الابعاد دون اجراء التحويل فعليا.
  5. ال Kernel Trick يوفر حسابات كثيرة.
  6. من اشهر ال kernels هو RBF kernel.
  7. من اشهر ال kernels هو polynomial kernel.
- **Transliteration audit:** 0 substitution(s), 1 residual ambiguous form(s) left untouched.
- **Key points:** 3 (DS011-C01, DS011-C02, DS011-C05)
- **zero_shot_raw arm:** status=SUCCESS, coverage_score=0.489397
  - per-key-point max P(entailment): [0.29963, 0.997915, 0.170646]
- **zero_shot_final arm:** status=SUCCESS, coverage_score=0.468221
  - per-key-point max P(entailment): [0.246837, 0.997919, 0.159907]
- **adapter_raw arm:** status=SUCCESS, coverage_score=0.35799866666666663
  - per-key-point max P(entailment): [0.160745, 0.858822, 0.054429]
- **adapter_final arm:** status=SUCCESS, coverage_score=0.340637
  - per-key-point max P(entailment): [0.156323, 0.816709, 0.048879]

## DS-030 (DS)

- **Decomposition status:** SUCCESS
- **Raw answer:** XGBoostده أنا استخدمته في مشروع وطلع نتيجة أحسن من أي حاجة تانية جرّبتها، بس ما تسألنيش هو شغال إزاي بالظبط جوّه. اللي أنا فاهمه إنه بيبني كذا شجرة، ذي الـ Random Forest كده بالظبط، أشجار كتير مستقلة عن بعض وفي الآخر بياخد المتوسط أو لأ، استنى، أظن فيه حاجة إن كل شجرة بتصلّح غلطة اللي قبلها؟ لأ، أنا أظن دي حاجة تانية. خلينا نقول إنها أشجار مستقلة وبيتجمّع ناتجها في الآخر. المهم إنه سريع، وبيدعم الـ GPU، وبيتعامل مع الـ missing values لوحده من غير ما تنضّف حاجة، وفيه فيه regularization بيمنع الـ overfitting. عشان كده كل الناس في Kaggle بتستخدمه.
- **Claims (raw, pre-glossary):**
  1. المتحدث استخدم XGBoost في مشروع.
  2. XGBoost أظهر نتيجة أفضل من أي شيء آخر جربه المتحدث.
  3. المتحدث يطلب عدم سؤاله عن طريقة عمل XGBoost داخلًا.
  4. المتحدث يفهم أن XGBoost يبني عدة أشجار.
  5. الأشجار التي يبنيها XGBoost تشبه الأشجار في Random Forest.
  6. الأشجار التي يبنيها XGBoost كثيرة ومستقلة عن بعضها.
  7. المتحدث يقول إن XGBoost قد يجمع ناتج الأشجار في النهاية.
  8. المتحدث يقول إن XGBoost قد لا يجمع ناتج الأشجار في النهاية.
  9. المتحدث ظن أن كل شجرة في XGBoost تصحح خطأ الشجرة السابقة.
  10. المتحدث يرفض الفكرة السابقة ويظن أن ذلك شيء آخر.
  11. المتحدث يصف أشجار XGBoost بأنها مستقلة وتُجمع ناتجها في النهاية.
  12. XGBoost سريع.
  13. XGBoost يدعم الـ GPU.
  14. XGBoost يتعامل مع الـ missing values بنفسه دون الحاجة لتنظيف البيانات.
  15. XGBoost يحتوي على regularization يمنع الـ overfitting.
  16. كل الناس في Kaggle يستخدمون XGBoost.
- **Claims (final, post-glossary, D101):**
  1. المتحدث استخدم XGBoost في مشروع.
  2. XGBoost اظهر نتيجة افضل من اي شيء اخر جربه المتحدث.
  3. المتحدث يطلب عدم سؤاله عن طريقة عمل XGBoost داخلا.
  4. المتحدث يفهم ان XGBoost يبني عدة اشجار.
  5. الاشجار التي يبنيها XGBoost تشبه الاشجار في Random Forest.
  6. الاشجار التي يبنيها XGBoost كثيرة ومستقلة عن بعضها.
  7. المتحدث يقول ان XGBoost قد يجمع ناتج الاشجار في النهاية.
  8. المتحدث يقول ان XGBoost قد لا يجمع ناتج الاشجار في النهاية.
  9. المتحدث ظن ان كل شجرة في XGBoost تصحح خطا الشجرة السابقة.
  10. المتحدث يرفض الفكرة السابقة ويظن ان ذلك شيء اخر.
  11. المتحدث يصف اشجار XGBoost بانها مستقلة وتجمع ناتجها في النهاية.
  12. XGBoost سريع.
  13. XGBoost يدعم ال GPU.
  14. XGBoost يتعامل مع ال missing values بنفسه دون الحاجة لتنظيف البيانات.
  15. XGBoost يحتوي على regularization يمنع ال overfitting.
  16. كل الناس في Kaggle يستخدمون XGBoost.
- **Transliteration audit:** 0 substitution(s), 0 residual ambiguous form(s) left untouched.
- **Key points:** 3 (DS030-C01, DS030-C02, DS030-C03)
- **zero_shot_raw arm:** status=SUCCESS, coverage_score=0.43384500000000004
  - per-key-point max P(entailment): [0.173213, 0.994217, 0.134105]
- **zero_shot_final arm:** status=SUCCESS, coverage_score=0.408768
  - per-key-point max P(entailment): [0.112164, 0.991856, 0.122284]
- **adapter_raw arm:** status=SUCCESS, coverage_score=0.14213
  - per-key-point max P(entailment): [0.034208, 0.369667, 0.022515]
- **adapter_final arm:** status=SUCCESS, coverage_score=0.17178733333333332
  - per-key-point max P(entailment): [0.035384, 0.450293, 0.029685]

## DS-033 (DS)

- **Decomposition status:** SUCCESS
- **Raw answer:** Backpropagation… يعني الاسم نفسه بيقول: انتشار عكسي. الشبكة الأول بتشتغل من الشمال لليمين وتطلّع نتيجة، النتيجة دي بتبقى غلط في الأول طبعًا لأن الـ weights عشوائية. فبنقارن اللي طلع باللي المفروض يطلع، وبنطلّع رقم اسمه الـ loss. بعد كده بترجع بالعكس، من الآخر للأول، وبتظبط الـ weights شوية شوية عشان الغلط يقلّ. هي دي فكرة الـ gradient descent بالظبط، يعني الـ backprop والـ gradient descent نفس الحاجة عندي. وبتستخدم الـ chain rule في الرياضة عشان تعرف كل weight ساهم قد إيه في الغلط. والعملية بتتكرر مرات كتير، كل مرة اسمها epoch.
- **Claims (raw, pre-glossary):**
  1. اسم Backpropagation يعني انتشار عكسي.
  2. الشبكة الأولى تعمل من اليسار إلى اليمين وتنتج نتيجة.
  3. النتيجة تكون خاطئة في البداية لأن الأوزان (weights) عشوائية.
  4. يتم مقارنة النتيجة المتوقعة بالنتيجة الفعلية وحساب رقم يسمى loss.
  5. بعد ذلك يتم الرجوع بالعكس من النهاية إلى البداية لتعديل الأوزان تدريجياً لتقليل الخطأ.
  6. فكرة gradient descent هي نفسها فكرة Backpropagation.
  7. تُستخدم قاعدة السلسلة (chain rule) في الرياضيات لتحديد مساهمة كل وزن في الخطأ.
  8. العملية تتكرر مرات عديدة وتسمى كل مرة epoch.
- **Claims (final, post-glossary, D101):**
  1. اسم Backpropagation يعني انتشار عكسي.
  2. الشبكة الاولى تعمل من اليسار الى اليمين وتنتج نتيجة.
  3. النتيجة تكون خاطئة في البداية لان الاوزان (weights) عشوائية.
  4. يتم مقارنة النتيجة المتوقعة بالنتيجة الفعلية وحساب رقم يسمى loss.
  5. بعد ذلك يتم الرجوع بالعكس من النهاية الى البداية لتعديل الاوزان تدريجيا لتقليل الخطا.
  6. فكرة gradient descent هي نفسها فكرة Backpropagation.
  7. تستخدم قاعدة السلسلة (chain rule) في الرياضيات لتحديد مساهمة كل وزن في الخطا.
  8. العملية تتكرر مرات عديدة وتسمى كل مرة epoch.
- **Transliteration audit:** 0 substitution(s), 0 residual ambiguous form(s) left untouched.
- **Key points:** 3 (DS033-C01, DS033-C03, DS033-C05)
- **zero_shot_raw arm:** status=SUCCESS, coverage_score=0.3534743333333334
  - per-key-point max P(entailment): [0.057229, 0.98867, 0.014524]
- **zero_shot_final arm:** status=SUCCESS, coverage_score=0.3367543333333333
  - per-key-point max P(entailment): [0.009261, 0.986478, 0.014524]
- **adapter_raw arm:** status=SUCCESS, coverage_score=0.12118833333333334
  - per-key-point max P(entailment): [0.082015, 0.256066, 0.025484]
- **adapter_final arm:** status=SUCCESS, coverage_score=0.10284866666666666
  - per-key-point max P(entailment): [0.044153, 0.238909, 0.025484]

## CS-013 (CS)

- **Decomposition status:** SUCCESS
- **Raw answer:** دي أشهر ثغرة في الدنيا. الفكرة إن أنت في خانة الـ login مثلًا، بدل ما تكتب اسمك بتكتب كود SQL. الحتة الشهيرة دي `' OR 1=1 --`، اللي بتخلّي الشرط دايمًا صح فبيدخّلك من غير password. وده بيحصل لأن المبرمج بيلزّق اللي المستخدم كتبه جوّه الـ query على طول. وممكن يعمل حاجات أوحش من كده طبعًا، يسحب جدول الـ users كله، أو يمسح الداتابيز. المنع بقى… أهم حاجة إنك متبنيش الـ query بالـ concatenation، تستخدم حاجة اسمها prepared statements أو parameterized queries، الاتنين نفس الفكرة، إنك تفصل الأوامر عن الداتا. وطبعًا validation على الـ input. سمعت كمان إن الـ WAF بيساعد بس مش هيوقّفه لوحده.
- **Claims (raw, pre-glossary):**
  1. هذه أشهر ثغرة في العالم.
  2. الفكرة هي أنه في حقل تسجيل الدخول يكتب المستخدم كود SQL بدلاً من كتابة اسمه.
  3. الجزء الشهير هو `' OR 1=1 --` الذي يجعل الشرط دائماً صحيحاً.
  4. الشرط الصحيح يسمح بالدخول دون كلمة مرور.
  5. يحدث ذلك لأن المبرمج يلصق ما كتبه المستخدم داخل الاستعلام مباشرة.
  6. يمكن للمهاجم سحب جدول users بالكامل.
  7. يمكن للمهاجم مسح قاعدة البيانات.
  8. الوقاية هي عدم بناء الاستعلام بالconcatenation.
  9. الوقاية هي استخدام prepared statements أو parameterized queries.
  10. prepared statements وparameterized queries هما نفس الفكرة.
  11. الفكرة هي فصل الأوامر عن البيانات.
  12. يجب إجراء validation على الإدخال.
  13. الـ WAF يساعد في الحماية.
  14. الـ WAF لا يمنع الهجوم بمفرده.
- **Claims (final, post-glossary, D101):**
  1. هذه اشهر ثغرة في العالم.
  2. الفكرة هي انه في حقل تسجيل الدخول يكتب المستخدم Code SQL بدلا من كتابة اسمه.
  3. الجزء الشهير هو `' OR 1=1 --` الذي يجعل الشرط دائما صحيحا.
  4. الشرط الصحيح يسمح بالدخول دون كلمة مرور.
  5. يحدث ذلك لان المبرمج يلصق ما كتبه المستخدم داخل الاستعلام مباشرة.
  6. يمكن للمهاجم سحب جدول users بالكامل.
  7. يمكن للمهاجم مسح قاعدة البيانات.
  8. الوقاية هي عدم بناء الاستعلام بالconcatenation.
  9. الوقاية هي استخدام prepared statements او parameterized queries.
  10. prepared statements وparameterized queries هما نفس الفكرة.
  11. الفكرة هي فصل الاوامر عن البيانات.
  12. يجب اجراء validation على الادخال.
  13. ال WAF يساعد في الحماية.
  14. ال WAF لا يمنع الهجوم بمفرده.
- **Transliteration audit:** 1 substitution(s), 0 residual ambiguous form(s) left untouched.
  - claim 1: `كود` → `Code`
- **Key points:** 3 (CS013-C01, CS013-C02, CS013-C05)
- **zero_shot_raw arm:** status=SUCCESS, coverage_score=0.10626833333333334
  - per-key-point max P(entailment): [0.167061, 0.004619, 0.147125]
- **zero_shot_final arm:** status=SUCCESS, coverage_score=0.08203166666666667
  - per-key-point max P(entailment): [0.088712, 0.006145, 0.151238]
- **adapter_raw arm:** status=SUCCESS, coverage_score=0.019438333333333335
  - per-key-point max P(entailment): [0.034006, 0.009646, 0.014663]
- **adapter_final arm:** status=SUCCESS, coverage_score=0.019264
  - per-key-point max P(entailment): [0.031665, 0.010711, 0.015416]

## CS-024 (CS)

- **Decomposition status:** SUCCESS
- **Raw answer:** دول تلاتة أنواع بيتقالوا في الـ penetration testing. الـ Black Box يعني إنت داخل على النظام وانت مش عارف عنه أي حاجة، زي أي هاكر من بره بالظبط، بتبدأ من الصفر، بتعمل reconnaissance ومسح وكده. الـ White Box العكس، بيدّولك كل حاجة، الكود، الـ diagrams، الصلاحيات، فبتلاقي حاجات مستحيل تلاقيها من بره. والـ Gray Box في النص، يعني مثلًا بيدّولك حساب مستخدم عادي وبس، وتشوف تقدر توصل لفين منه. أنا شايف إن الـ Gray Box هو الأقرب للواقع لأن أغلب الاختراقات بتيجي من حد معاه صلاحية بسيطة أصلًا. هي بيتقال عليهم بردو في الـ software testing العادي؟ مش متأكد بصراحة.
- **Claims (raw, pre-glossary):**
  1. هناك ثلاثة أنواع تُذكر في الـ penetration testing.
  2. النوع Black Box يعني أنك تدخل إلى النظام ولا تعرف عنه شيئًا.
  3. النوع Black Box يشبه أي هاكر من الخارج.
  4. في النوع Black Box تبدأ من الصفر وتقوم بعملية reconnaissance ومسح.
  5. النوع White Box هو العكس.
  6. النوع White Box يزودك بكل شيء.
  7. النوع White Box يزودك بالكود.
  8. النوع White Box يزودك بالـ diagrams.
  9. النوع White Box يزودك بالصلاحيات.
  10. في النوع White Box تجد أشياء لا يمكن العثور عليها من الخارج.
  11. النوع Gray Box يقع في الوسط.
  12. في النوع Gray Box يزودك بحساب مستخدم عادي فقط.
  13. في النوع Gray Box يمكن للمتحدث أن يتحقق ما يمكن الوصول إليه.
  14. المتحدث يرى أن الـ Gray Box هو الأقرب إلى الواقع.
  15. السبب هو أن معظم الاختراقات تأتي من شخص لديه صلاحية بسيطة أصلاً.
  16. يُسأل ما إذا كانت هذه الأنواع تُذكر أيضًا في الـ software testing العادي.
  17. المتحدث غير متأكد من ذلك.
- **Claims (final, post-glossary, D101):**
  1. هناك ثلاثة انواع تذكر في ال penetration testing.
  2. النوع Black Box يعني انك تدخل الى النظام ولا تعرف عنه شيئا.
  3. النوع Black Box يشبه اي هاكر من الخارج.
  4. في النوع Black Box تبدا من الصفر وتقوم بعملية reconnaissance ومسح.
  5. النوع White Box هو العكس.
  6. النوع White Box يزودك بكل شيء.
  7. النوع White Box يزودك Code.
  8. النوع White Box يزودك بال diagrams.
  9. النوع White Box يزودك بالصلاحيات.
  10. في النوع White Box تجد اشياء لا يمكن العثور عليها من الخارج.
  11. النوع Gray Box يقع في الوسط.
  12. في النوع Gray Box يزودك بحساب مستخدم عادي فقط.
  13. في النوع Gray Box يمكن للمتحدث ان يتحقق ما يمكن الوصول اليه.
  14. المتحدث يرى ان ال Gray Box هو الاقرب الى الواقع.
  15. السبب هو ان معظم الاختراقات تاتي من شخص لديه صلاحية بسيطة اصلا.
  16. يسال ما اذا كانت هذه الانواع تذكر ايضا في ال software testing العادي.
  17. المتحدث غير متاكد من ذلك.
- **Transliteration audit:** 1 substitution(s), 0 residual ambiguous form(s) left untouched.
  - claim 6: `بالكود` → `Code`
- **Key points:** 3 (CS024-C01, CS024-C02, CS024-C03)
- **zero_shot_raw arm:** status=SUCCESS, coverage_score=0.3429776666666666
  - per-key-point max P(entailment): [0.980274, 0.001452, 0.047207]
- **zero_shot_final arm:** status=SUCCESS, coverage_score=0.340045
  - per-key-point max P(entailment): [0.981509, 0.001165, 0.037461]
- **adapter_raw arm:** status=SUCCESS, coverage_score=0.02581
  - per-key-point max P(entailment): [0.052126, 0.003667, 0.021637]
- **adapter_final arm:** status=SUCCESS, coverage_score=0.030120666666666667
  - per-key-point max P(entailment): [0.066709, 0.002821, 0.020832]

## CS-039 (CS)

- **Decomposition status:** SUCCESS
- **Raw answer:** الـ Sandbox من الاسم، صندوق الرمل بتاع الأطفال، يعني مكان محدود يلعب فيه براحته من غير ما يخرّب البيت. تقنيًا هي بيئة معزولة بتشغّل فيها حاجة إنت مش واثق فيها. الاستخدام اللي أنا عارفه كويس هو تحليل الفيروسات: عندك ملف مشكوك فيه، مش هتشغّله على جهازك طبعًا، فبتشغّله جوّه sandbox أو virtual machine وتقعد تتفرّج هو بيعمل إيه، بيفتح أي connections، بيكتب أي files. أنا مش متأكد لو الـ VM والـ sandbox نفس الحاجة بالظبط ولا فيه فرق تقني بينهم. برضو المتصفحات بتشتغل بالفكرة دي، وبرامج زي Word لما بتفتح ملف من الإنترنت بتفتحه في وضع محمي.
- **Claims (raw, pre-glossary):**
  1. الـ Sandbox هو اسم يشير إلى صندوق الرمل للأطفال.
  2. الـ Sandbox هو مكان محدود يمكن اللعب فيه بحرية دون إتلاف المنزل.
  3. تقنيًا الـ Sandbox هي بيئة معزولة تُشغَّل فيها شيء غير موثوق به.
  4. المتحدث يعرف أن الاستخدام الشائع للـ Sandbox هو تحليل الفيروسات.
  5. عندما يكون لديك ملف مشكوك فيه، لا تشغّله على جهازك.
  6. يتم تشغيل الملف المشكوك فيه داخل sandbox أو virtual machine.
  7. يتم مراقبة أن الملف يفتح أي connections داخل sandbox أو virtual machine.
  8. يتم مراقبة أن الملف يكتب أي files داخل sandbox أو virtual machine.
  9. المتحدث غير متأكد ما إذا كان الـ VM والـ sandbox نفس الشيء بالضبط.
  10. المتحدث غير متأكد ما إذا كان هناك فرق تقني بين الـ VM والـ sandbox.
  11. المتصفحات تعمل بنفس فكرة الـ Sandbox.
  12. برامج مثل Word عندما تفتح ملفًا من الإنترنت تفتحه في وضع محمي.
- **Claims (final, post-glossary, D101):**
  1. ال Sandbox هو اسم يشير الى صندوق الرمل للاطفال.
  2. ال Sandbox هو مكان محدود يمكن اللعب فيه بحرية دون اتلاف المنزل.
  3. تقنيا ال Sandbox هي بيئة معزولة تشغل فيها شيء غير موثوق به.
  4. المتحدث يعرف ان الاستخدام الشائع لل Sandbox هو تحليل الفيروسات.
  5. عندما يكون لديك ملف مشكوك فيه، لا تشغله على جهازك.
  6. يتم تشغيل الملف المشكوك فيه داخل sandbox او virtual machine.
  7. يتم مراقبة ان الملف يفتح اي connections داخل sandbox او virtual machine.
  8. يتم مراقبة ان الملف يكتب اي files داخل sandbox او virtual machine.
  9. المتحدث غير متاكد ما اذا كان ال VM وال sandbox نفس الشيء بالضبط.
  10. المتحدث غير متاكد ما اذا كان هناك فرق تقني بين ال VM وال sandbox.
  11. المتصفحات تعمل بنفس فكرة ال Sandbox.
  12. برامج مثل Word عندما تفتح ملفا من الانترنت تفتحه في وضع محمي.
- **Transliteration audit:** 0 substitution(s), 0 residual ambiguous form(s) left untouched.
- **Key points:** 3 (CS039-C01, CS039-C02, CS039-C03)
- **zero_shot_raw arm:** status=SUCCESS, coverage_score=0.16493433333333332
  - per-key-point max P(entailment): [0.270148, 0.013325, 0.21133]
- **zero_shot_final arm:** status=SUCCESS, coverage_score=0.132814
  - per-key-point max P(entailment): [0.190374, 0.011164, 0.196904]
- **adapter_raw arm:** status=SUCCESS, coverage_score=0.05136266666666667
  - per-key-point max P(entailment): [0.06804, 0.016727, 0.069321]
- **adapter_final arm:** status=SUCCESS, coverage_score=0.041468
  - per-key-point max P(entailment): [0.02995, 0.030215, 0.064239]

## CS-047 (CS)

- **Decomposition status:** SUCCESS
- **Raw answer:** Privilege Escalation… يعني إنت دخلت النظام بس بصلاحية ضعيفة، user عادي، ومش قادر تعمل حاجة مفيدة. فبتدوّر على طريقة تطلّع بيها فوق. النوع اللي كل الناس بتعرفه هو الـ Vertical، إنك من user عادي تبقى root أو admin، وده اللي بيديك النظام كله. بيتم عادةً باستغلال exploit في الـ kernel أو حاجة في النظام متظبطة غلط، زي service شغالة بصلاحيات عالية وانت تقدر تعدّل عليها. وفيه نوع تاني اسمه Horizontal، وده يعني تروح لحساب حد تاني زيّك في المستوى. صراحة ده أخف كتير من الأول لأنك في الآخر لسه user عادي.
- **Claims (raw, pre-glossary):**
  1. Privilege Escalation يعني أنك دخلت النظام بصلاحية ضعيفة كـ user عادي ولا تستطيع القيام بشيء مفيد.
  2. تبحث عن طريقة للارتقاء إلى صلاحية أعلى.
  3. النوع المعروف هو Vertical.
  4. Vertical يعني أن يصبح الـ user العادي root أو admin.
  5. هذا يمنحك كامل النظام.
  6. يتم ذلك عادةً باستغلال exploit في الـ kernel أو خطأ في النظام.
  7. مثال ذلك هو service تعمل بصلاحيات عالية ويمكن تعديلها.
  8. هناك نوع آخر يسمى Horizontal.
  9. Horizontal يعني الانتقال إلى حساب شخص آخر في نفس المستوى.
  10. هذا النوع أخف كثيراً من النوع الأول لأنك تظل user عادي في النهاية.
- **Claims (final, post-glossary, D101):**
  1. Privilege Escalation يعني انك دخلت النظام بصلاحية ضعيفة ك user عادي ولا تستطيع القيام بشيء مفيد.
  2. تبحث عن طريقة للارتقاء الى صلاحية اعلى.
  3. النوع المعروف هو Vertical.
  4. Vertical يعني ان يصبح ال user العادي root او admin.
  5. هذا يمنحك كامل النظام.
  6. يتم ذلك عادة باستغلال exploit في ال kernel او خطا في النظام.
  7. مثال ذلك هو service تعمل بصلاحيات عالية ويمكن تعديلها.
  8. هناك نوع اخر يسمى Horizontal.
  9. Horizontal يعني الانتقال الى حساب شخص اخر في نفس المستوى.
  10. هذا النوع اخف كثيرا من النوع الاول لانك تظل user عادي في النهاية.
- **Transliteration audit:** 0 substitution(s), 0 residual ambiguous form(s) left untouched.
- **Key points:** 3 (CS047-C01, CS047-C02, CS047-C03)
- **zero_shot_raw arm:** status=SUCCESS, coverage_score=0.6021470000000001
  - per-key-point max P(entailment): [0.033952, 0.997971, 0.774518]
- **zero_shot_final arm:** status=SUCCESS, coverage_score=0.6163263333333333
  - per-key-point max P(entailment): [0.046198, 0.998077, 0.804704]
- **adapter_raw arm:** status=SUCCESS, coverage_score=0.3116946666666667
  - per-key-point max P(entailment): [0.016936, 0.866133, 0.052015]
- **adapter_final arm:** status=SUCCESS, coverage_score=0.32437266666666664
  - per-key-point max P(entailment): [0.018194, 0.898924, 0.056]

## CS-048 (CS)

- **Decomposition status:** SUCCESS
- **Raw answer:** الـ Firewall العادي بيشتغل على مستوى الشبكة، يعني بيقولك الـ IP ده مسموح والـ port ده مقفول، وخلاص. هو مبيفهمش إنت بتبعت إيه جوّه الـ packet أصلًا. فلو حد باعت SQL Injection على port 80، الـ firewall هيعدّيها عادي لأن الـ port ده مفتوح ومفروض يبقى مفتوح. هنا بييجي دور الـ WAF، ده firewall متخصّص للـ web، بيقعد يقرا الـ requests اللي جاية للموقع ويشوف فيها حاجة مريبة ولا لأ. فبيمسك حاجات زي الـ SQL Injection والـ XSS. أنا فاكر إنه بيشتغل على الـ layer 7، اللي هي الـ application layer، لكن مش هقدر أقولك بالظبط بيميّز الطلب الخبيث إزاي — أظن عن طريق قواعد أو patterns جاهزة عنده.
- **Claims (raw, pre-glossary):**
  1. الـ Firewall العادي يعمل على مستوى الشبكة.
  2. الـ Firewall العادي يحدد ما إذا كان الـ IP مسموحًا والـ port مقفولًا.
  3. الـ Firewall العادي لا يفهم محتوى الـ packet.
  4. إذا أرسل أحد هجوم SQL Injection عبر port 80، فإن الـ Firewall يمرره عاديًا لأن الـ port مفتوح ومفترض أن يكون مفتوحًا.
  5. الـ WAF هو firewall متخصص للويب.
  6. الـ WAF يقرأ الـ requests الواردة إلى الموقع.
  7. الـ WAF يتحقق مما إذا كان الـ requests يحتوي على شيء مريب.
  8. الـ WAF يلتقط هجمات SQL Injection.
  9. الـ WAF يلتقط هجمات XSS.
  10. الـ WAF يعمل على الـ layer 7، وهو طبقة التطبيق.
  11. المتحدث لا يستطيع تحديد بالضبط كيف يميز الـ WAF الطلب الخبيث.
  12. المتحدث يظن أن الـ WAF يميز الطلب الخبيث عبر قواعد أو patterns جاهزة لديه.
- **Claims (final, post-glossary, D101):**
  1. ال Firewall العادي يعمل على مستوى الشبكة.
  2. ال Firewall العادي يحدد ما اذا كان ال IP مسموحا وال port مقفولا.
  3. ال Firewall العادي لا يفهم محتوى ال packet.
  4. اذا ارسل احد هجوم SQL Injection عبر port 80، فان ال Firewall يمرره عاديا لان ال port مفتوح ومفترض ان يكون مفتوحا.
  5. ال WAF هو firewall متخصص للويب.
  6. ال WAF يقرا ال requests الواردة الى الموقع.
  7. ال WAF يتحقق مما اذا كان ال requests يحتوي على شيء مريب.
  8. ال WAF يلتقط هجمات SQL Injection.
  9. ال WAF يلتقط هجمات XSS.
  10. ال WAF يعمل على ال layer 7، وهو طبقة التطبيق.
  11. المتحدث لا يستطيع تحديد بالضبط كيف يميز ال WAF الطلب الخبيث.
  12. المتحدث يظن ان ال WAF يميز الطلب الخبيث عبر قواعد او patterns جاهزة لديه.
- **Transliteration audit:** 0 substitution(s), 0 residual ambiguous form(s) left untouched.
- **Key points:** 4 (CS048-C01, CS048-C02, CS048-C03, CS048-C06)
- **zero_shot_raw arm:** status=SUCCESS, coverage_score=0.36411175
  - per-key-point max P(entailment): [0.254959, 0.001603, 0.998705, 0.20118]
- **zero_shot_final arm:** status=SUCCESS, coverage_score=0.3531615
  - per-key-point max P(entailment): [0.230381, 0.001642, 0.998753, 0.18187]
- **adapter_raw arm:** status=SUCCESS, coverage_score=0.2631625
  - per-key-point max P(entailment): [0.105071, 0.007015, 0.909757, 0.030807]
- **adapter_final arm:** status=SUCCESS, coverage_score=0.2655155
  - per-key-point max P(entailment): [0.089756, 0.005944, 0.924991, 0.041371]

## SE-007 (SE)

- **Decomposition status:** SUCCESS
- **Raw answer:** الـ Design Patterns هي حلول جاهزة لمشاكل بتتكرر في التصميم. يعني مش أول واحد يقابل المشكلة دي، فناس قبلك حلّوها ووثّقوا الحل، وانت بتستخدمه. أشهر حاجة فيهم الـ Singleton، وده إنك تضمن إن الـ class ده يبقى ليه instance واحدة بس في البرنامج كله، بستخدمه كتير في الـ database connection مثلًا. وفيه الـ Factory، بيبني objects من غير ما تحدد الـ class بتاعها بالظبط. التقسيم بتاعهم… فيه Creational، ودي بتاعت الإنشاء زي اللي قلتهم، وفيه Structural، ودي بتاعت التركيب، زي الـ Adapter والـ Observer… وفيه نوع تالت مش جاي في دماغي… آه، Behavioral، ودي بتاعت السلوك والتواصل بين الـ objects.
- **Claims (raw, pre-glossary):**
  1. الـ Design Patterns هي حلول جاهزة لمشاكل تتكرر في التصميم.
  2. الـ Design Patterns ليست أول من يواجه المشكلة، بل تم حلها وتوثيقها من قبل أشخاص قبلك.
  3. الـ Singleton يضمن أن الـ class له instance واحدة فقط في البرنامج كله.
  4. الـ Singleton يُستخدم كثيرًا في الـ database connection.
  5. الـ Factory يبني objects دون تحديد الـ class الخاصة بها بدقة.
  6. تصنيف الـ Design Patterns يتضمن فئة Creational التي تتعلق بالإنشاء.
  7. تصنيف الـ Design Patterns يتضمن فئة Structural التي تتعلق بالتركيب.
  8. فئة Structural تشمل الـ Adapter والـ Observer.
  9. تصنيف الـ Design Patterns يتضمن فئة Behavioral التي تتعلق بالسلوك والتواصل بين الـ objects.
- **Claims (final, post-glossary, D101):**
  1. ال Design Patterns هي حلول جاهزة لمشاكل تتكرر في التصميم.
  2. ال Design Patterns ليست اول من يواجه المشكلة، Pull تم حلها وتوثيقها من قبل اشخاص قبلك.
  3. ال Singleton يضمن ان ال class له instance واحدة فقط في البرنامج كله.
  4. ال Singleton يستخدم كثيرا في ال database connection.
  5. ال Factory يبني objects دون تحديد ال class الخاصة بها بدقة.
  6. تصنيف ال Design Patterns يتضمن فئة Creational التي تتعلق بالانشاء.
  7. تصنيف ال Design Patterns يتضمن فئة Structural التي تتعلق بالتركيب.
  8. فئة Structural تشمل ال Adapter وال Observer.
  9. تصنيف ال Design Patterns يتضمن فئة Behavioral التي تتعلق بالسلوك والتواصل بين ال objects.
- **Transliteration audit:** 1 substitution(s), 1 residual ambiguous form(s) left untouched.
  - claim 1: `بل` → `Pull`
- **Key points:** 2 (SE007-C01, SE007-C02)
- **zero_shot_raw arm:** status=SUCCESS, coverage_score=0.10439799999999999
  - per-key-point max P(entailment): [0.001321, 0.207475]
- **zero_shot_final arm:** status=SUCCESS, coverage_score=0.064479
  - per-key-point max P(entailment): [0.002099, 0.126859]
- **adapter_raw arm:** status=SUCCESS, coverage_score=0.032325
  - per-key-point max P(entailment): [0.005214, 0.059436]
- **adapter_final arm:** status=SUCCESS, coverage_score=0.025471999999999998
  - per-key-point max P(entailment): [0.005924, 0.04502]

## SE-013 (SE)

- **Decomposition status:** SUCCESS
- **Raw answer:** SQL يعني جداول. صفوف وأعمدة وعلاقات بين الجداول، وقبل ما تبدأ لازم تحدد الـ schema، الجدول ده فيه كام عمود وكل عمود نوعه إيه. لو عايز تضيف عمود بعد كده لازم تعمل migration ودي وجعة دماغ. الـ NoSQL زي MongoDB، بتخزّن documents شكلها زي الـ JSON، وكل document ممكن يكون مختلف عن التاني خالص، فمفيش schema يقيّدك. ومفيش فيها علاقات خالص، إنت بتحطّ الداتا كلها جوّه بعضها. وعمومًا الـ NoSQL أسرع من الـ SQL، وبتـ scale أحسن لما الداتا تكبر جدًا. بس لسه الـ SQL هي المستخدمة في أي حاجة فيها فلوس أو معاملات، عشان الـ ACID.
- **Claims (raw, pre-glossary):**
  1. SQL يعني جداول.
  2. جداول SQL تتكون من صفوف وأعمدة.
  3. جداول SQL تحتوي على علاقات بين الجداول.
  4. قبل البدء يجب تحديد الـ schema.
  5. الجدول يحتوي على عدد من الأعمدة.
  6. كل عمود في الجدول له نوع محدد.
  7. إذا أردت إضافة عمود لاحقًا يجب إجراء migration.
  8. الـ migration يعتبر وجعة دماغ.
  9. الـ NoSQL مثل MongoDB يخزن documents على شكل JSON.
  10. كل document قد يكون مختلفًا تمامًا عن document آخر.
  11. لا يوجد schema يقيّد الـ NoSQL.
  12. لا توجد علاقات في الـ NoSQL.
  13. في الـ NoSQL يتم وضع البيانات كلها داخل بعضها.
  14. عمومًا الـ NoSQL أسرع من الـ SQL.
  15. الـ NoSQL يوسع (scale) بشكل أفضل عندما تكبر البيانات كثيرًا.
  16. لا يزال الـ SQL هو المستخدم في أي شيء يحتوي على أموال أو معاملات.
  17. السبب هو الـ ACID.
- **Claims (final, post-glossary, D101):**
  1. SQL يعني جداول.
  2. جداول SQL تتكون من صفوف واعمدة.
  3. جداول SQL تحتوي على علاقات بين الجداول.
  4. قبل البدء يجب تحديد ال schema.
  5. الجدول يحتوي على عدد من الاعمدة.
  6. كل عمود في الجدول له نوع محدد.
  7. اذا اردت اضافة عمود لاحقا يجب اجراء migration.
  8. ال migration يعتبر وجعة دماغ.
  9. ال NoSQL مثل MongoDB يخزن documents على شكل JSON.
  10. كل document قد يكون مختلفا تماما عن document اخر.
  11. لا يوجد schema يقيد ال NoSQL.
  12. لا توجد علاقات في ال NoSQL.
  13. في ال NoSQL يتم وضع البيانات كلها داخل بعضها.
  14. عموما ال NoSQL اسرع من ال SQL.
  15. ال NoSQL يوسع (scale) بشكل افضل عندما تكبر البيانات كثيرا.
  16. لا يزال ال SQL هو المستخدم في اي شيء يحتوي على اموال او معاملات.
  17. السبب هو ال ACID.
- **Transliteration audit:** 0 substitution(s), 0 residual ambiguous form(s) left untouched.
- **Key points:** 3 (SE013-C01, SE013-C02, SE013-C04)
- **zero_shot_raw arm:** status=SUCCESS, coverage_score=0.08537533333333334
  - per-key-point max P(entailment): [0.069152, 0.182645, 0.004329]
- **zero_shot_final arm:** status=SUCCESS, coverage_score=0.14921066666666669
  - per-key-point max P(entailment): [0.057282, 0.382232, 0.008118]
- **adapter_raw arm:** status=SUCCESS, coverage_score=0.047159
  - per-key-point max P(entailment): [0.031502, 0.105137, 0.004838]
- **adapter_final arm:** status=SUCCESS, coverage_score=0.060597333333333336
  - per-key-point max P(entailment): [0.038804, 0.136459, 0.006529]

## SE-027 (SE)

- **Decomposition status:** SUCCESS
- **Raw answer:** الفرق في حجم الحتة اللي بتختبرها. الـ Unit test بتختبر أصغر حاجة، function واحدة بس، وبتفترض إن كل حاجة حواليها شغالة، فبتعمل mock للحاجات دي. الـ Integration بقى بتشوف الحتتين لما يتركّبوا مع بعض بيشتغلوا صح ولا لأ، لأن كل واحد لوحده ممكن يبقى مظبوط بس لما يتكلّموا مع بعض تحصل مشكلة، خصوصًا في الـ API calls والـ database. والـ End-to-End، ده بيشغّل التطبيق كله ويعمل زي ما المستخدم بيعمل بالظبط، يفتح الصفحة، يكتب، يدوس، ويتأكد إن النتيجة ظهرت. صراحة أنا في مشاريعي بكتب unit tests بس، الـ E2E عمري ما اشتغلت عليها بجد، بس اللي سامعه إنها بطيئة وبتفشل من غير سبب أحيانًا.
- **Claims (raw, pre-glossary):**
  1. الفرق في حجم الجزء الذي يتم اختباره.
  2. اختبار الـ Unit test يختبر أصغر جزء.
  3. اختبار الـ Unit test يختبر دالة واحدة فقط.
  4. اختبار الـ Unit test يفترض أن كل شيء حوله يعمل.
  5. اختبار الـ Unit test يستخدم mock لتلك الأشياء.
  6. اختبار الـ Integration يراقب الجزأين عندما يركبان معًا إذا كانا يعملان بشكل صحيح أم لا.
  7. كل جزء بمفرده قد يكون صحيحًا.
  8. عند تواصل الجزأين قد تحدث مشكلة.
  9. المشكلة تحدث خاصة في استدعاءات الـ API وقاعدة البيانات.
  10. اختبار الـ End-to-End يشغل التطبيق بالكامل.
  11. اختبار الـ End-to-End يقوم بما يفعله المستخدم بالضبط.
  12. المستخدم يفتح الصفحة.
  13. المستخدم يكتب.
  14. المستخدم يضغط.
  15. المستخدم يتأكد من ظهور النتيجة.
  16. في مشاريعي أكتب اختبارات الـ unit tests فقط.
  17. لم أعمل على اختبارات الـ E2E فعليًا.
  18. سمعت أن اختبارات الـ E2E بطيئة.
  19. سمعت أن اختبارات الـ E2E تفشل دون سبب أحيانًا.
- **Claims (final, post-glossary, D101):**
  1. الفرق في حجم الجزء الذي يتم اختباره.
  2. اختبار ال Unit test يختبر اصغر جزء.
  3. اختبار ال Unit test يختبر دالة واحدة فقط.
  4. اختبار ال Unit test يفترض ان كل شيء حوله يعمل.
  5. اختبار ال Unit test يستخدم mock لتلك الاشياء.
  6. اختبار ال Integration يراقب الجزاين عندما يركبان معا اذا كانا يعملان بشكل صحيح ام لا.
  7. كل جزء بمفرده قد يكون صحيحا.
  8. عند تواصل الجزاين قد تحدث مشكلة.
  9. المشكلة تحدث خاصة في استدعاءات ال API وقاعدة البيانات.
  10. اختبار ال End-to-End يشغل التطبيق بالكامل.
  11. اختبار ال End-to-End يقوم بما يفعله المستخدم بالضبط.
  12. المستخدم يفتح الصفحة.
  13. المستخدم يكتب.
  14. المستخدم يضغط.
  15. المستخدم يتاكد من ظهور النتيجة.
  16. في مشاريعي اكتب اختبارات ال unit tests فقط.
  17. لم اعمل على اختبارات ال E2E فعليا.
  18. سمعت ان اختبارات ال E2E بطيئة.
  19. سمعت ان اختبارات ال E2E تفشل دون سبب احيانا.
- **Transliteration audit:** 0 substitution(s), 0 residual ambiguous form(s) left untouched.
- **Key points:** 3 (SE027-C01, SE027-C02, SE027-C03)
- **zero_shot_raw arm:** status=SUCCESS, coverage_score=0.7921636666666667
  - per-key-point max P(entailment): [0.984556, 0.404248, 0.987687]
- **zero_shot_final arm:** status=SUCCESS, coverage_score=0.8038663333333332
  - per-key-point max P(entailment): [0.980478, 0.442074, 0.989047]
- **adapter_raw arm:** status=SUCCESS, coverage_score=0.2253993333333333
  - per-key-point max P(entailment): [0.562804, 0.018757, 0.094637]
- **adapter_final arm:** status=SUCCESS, coverage_score=0.23209000000000002
  - per-key-point max P(entailment): [0.587257, 0.019414, 0.089599]

## SE-037 (SE)

- **Decomposition status:** SUCCESS
- **Raw answer:** Big O ده بيقيس سرعة الـ algorithm، بس مش بالثانية، لأ، بيقيسها بالنسبة لحجم الداتا. يعني بيقولك لو الداتا بقت الضعف، الوقت هيبقى كام. O(n) يعني لو الداتا اتضاعفت الوقت هيتضاعف، خطي. O(n²) دي وحشة، لو الداتا اتضاعفت الوقت هيبقى أربع أضعاف، ودي بتحصل لما تعمل loop جوّه loop. وفيه O(1) وده أحسن حاجة، وقت ثابت مهما كبرت الداتا، زي ما توصل لعنصر في list بالـ index. و binary search أظن دي O(n log n). المهم فيه إنه بيخليك تعرف الكود بتاعك هيستحمل لما الداتا تكبر ولا هيقع.
- **Claims (raw, pre-glossary):**
  1. Big O يقيس سرعة الـ algorithm.
  2. Big O لا يقيس السرعة بالثانية.
  3. Big O يقيس السرعة بالنسبة إلى حجم البيانات.
  4. إذا تضاعفت البيانات، يتغير الوقت وفقًا للـ Big O.
  5. O(n) يعني إذا تضاعفت البيانات، الوقت يتضاعف.
  6. O(n) هو سلوك خطي.
  7. O(n²) يعني إذا تضاعفت البيانات، الوقت يصبح أربعة أضعاف.
  8. O(n²) يحدث عندما تكون هناك حلقة داخل حلقة.
  9. O(1) هو الأفضل.
  10. O(1) يعني وقت ثابت مهما كبرت البيانات.
  11. O(1) يشبه الوصول إلى عنصر في list بالـ index.
  12. binary search هو O(n log n).
  13. هذا يساعد على معرفة ما إذا كان الكود سيتحمل عندما تكبر البيانات أم سيفشل.
- **Claims (final, post-glossary, D101):**
  1. Big O يقيس سرعة ال algorithm.
  2. Big O لا يقيس السرعة بالثانية.
  3. Big O يقيس السرعة بالنسبة الى حجم البيانات.
  4. اذا تضاعفت البيانات، يتغير الوقت وفقا لل Big O.
  5. O(n) يعني اذا تضاعفت البيانات، الوقت يتضاعف.
  6. O(n) هو سلوك خطي.
  7. O(n²) يعني اذا تضاعفت البيانات، الوقت يصبح اربعة اضعاف.
  8. O(n²) يحدث عندما تكون هناك حلقة داخل حلقة.
  9. O(1) هو الافضل.
  10. O(1) يعني وقت ثابت مهما كبرت البيانات.
  11. O(1) يشبه الوصول الى عنصر في list بال index.
  12. binary search هو O(n log n).
  13. هذا يساعد على معرفة ما اذا كان Code سيتحمل عندما تكبر البيانات ام سيفشل.
- **Transliteration audit:** 1 substitution(s), 0 residual ambiguous form(s) left untouched.
  - claim 12: `الكود` → `Code`
- **Key points:** 3 (SE037-C01, SE037-C02, SE037-C06)
- **zero_shot_raw arm:** status=SUCCESS, coverage_score=0.08232533333333333
  - per-key-point max P(entailment): [0.139047, 0.107213, 0.000716]
- **zero_shot_final arm:** status=SUCCESS, coverage_score=0.07602866666666667
  - per-key-point max P(entailment): [0.120204, 0.107213, 0.000669]
- **adapter_raw arm:** status=SUCCESS, coverage_score=0.038907000000000004
  - per-key-point max P(entailment): [0.092112, 0.021943, 0.002666]
- **adapter_final arm:** status=SUCCESS, coverage_score=0.038316
  - per-key-point max P(entailment): [0.090535, 0.021943, 0.00247]

## SE-041 (SE)

- **Decomposition status:** SUCCESS
- **Raw answer:** Multithreading يعني تشغّل أكتر من حاجة في نفس الوقت جوّه البرنامج الواحد، بدل ما تستنى المهمة تخلص وبعدين تبدأ اللي بعدها. مفيدة جدًا لما يكون عندك حاجات بتستنى، زي إنك بتقرا من ملف أو بتنزّل من الإنترنت. الـ Race Condition بقى دي المشكلة الكلاسيكية، بتحصل لما thread-ين يشتغلوا على نفس المتغير في نفس اللحظة. المثال اللي دايمًا بيتقال: حساب بنكي فيه 100 جنيه واتنين بيسحبوا 100 في نفس الثانية، لو الاتنين قروا الرصيد قبل ما حد يحدّثه، الاتنين هيسحبوا وهيبقى الرصيد بالسالب. الحل إنك تقفل الحتة دي بحيث واحد بس يدخلها، وده اسمه lock أو mutex — أنا مش فاهم الفرق بينهم بصراحة، بستخدم اللي اللغة بتديهولي.
- **Claims (raw, pre-glossary):**
  1. Multithreading يعني تشغيل أكثر من شيء في نفس الوقت داخل البرنامج الواحد.
  2. Multithreading يتيح عدم انتظار انتهاء المهمة قبل بدء المهمة التالية.
  3. Multithreading مفيد عندما تكون هناك عمليات تنتظر.
  4. من أمثلة الفائدة القراءة من ملف.
  5. من أمثلة الفائدة التنزيل من الإنترنت.
  6. الـ Race Condition هي المشكلة الكلاسيكية التي تحدث عندما يعمل خيطان على نفس المتغير في نفس اللحظة.
  7. الحساب البنكي في المثال يحتوي على 100 جنيه.
  8. في المثال، شخصان يسحبان 100 جنيه في نفس الثانية.
  9. إذا قرأ الاثنان الرصيد قبل أن يحدث أحدهما تحديثاً، سيقوم الاثنان بالسحب ويصبح الرصيد سالباً.
  10. الحل هو إغلاق الجزء بحيث يدخل إليه خيط واحد فقط.
  11. هذا الإغلاق يسمى lock أو mutex.
  12. المتحدث لا يفهم الفرق بين lock و mutex.
  13. المتحدث يستخدم ما توفره اللغة بين lock و mutex.
- **Claims (final, post-glossary, D101):**
  1. Multithreading يعني تشغيل اكثر من شيء في نفس الوقت داخل البرنامج الواحد.
  2. Multithreading يتيح عدم انتظار انتهاء المهمة قبل بدء المهمة التالية.
  3. Multithreading مفيد عندما تكون هناك عمليات تنتظر.
  4. من امثلة الفائدة القراءة من ملف.
  5. من امثلة الفائدة التنزيل من الانترنت.
  6. ال Race Condition هي المشكلة الكلاسيكية التي تحدث عندما يعمل خيطان على نفس المتغير في نفس اللحظة.
  7. الحساب البنكي في المثال يحتوي على 100 جنيه.
  8. في المثال، شخصان يسحبان 100 جنيه في نفس الثانية.
  9. اذا قرا الاثنان الرصيد قبل ان يحدث احدهما تحديثا، سيقوم الاثنان بالسحب ويصبح الرصيد سالبا.
  10. الحل هو اغلاق الجزء بحيث يدخل اليه خيط واحد فقط.
  11. هذا الاغلاق يسمى lock او mutex.
  12. المتحدث لا يفهم الفرق بين lock و mutex.
  13. المتحدث يستخدم ما توفره اللغة بين lock و mutex.
- **Transliteration audit:** 0 substitution(s), 0 residual ambiguous form(s) left untouched.
- **Key points:** 3 (SE041-C01, SE041-C03, SE041-C05)
- **zero_shot_raw arm:** status=SUCCESS, coverage_score=0.3285686666666667
  - per-key-point max P(entailment): [0.001855, 0.971064, 0.012787]
- **zero_shot_final arm:** status=SUCCESS, coverage_score=0.32867133333333337
  - per-key-point max P(entailment): [0.002163, 0.971064, 0.012787]
- **adapter_raw arm:** status=SUCCESS, coverage_score=0.05098033333333333
  - per-key-point max P(entailment): [0.005903, 0.122478, 0.02456]
- **adapter_final arm:** status=SUCCESS, coverage_score=0.051087
  - per-key-point max P(entailment): [0.006223, 0.122478, 0.02456]

## GN-004 (GN)

- **Decomposition status:** SUCCESS
- **Raw answer:** الـ CPU هي المخ بتاع الجهاز، هي اللي بتنفّذ كل حاجة. أي برنامج انت بتشغّله في الآخر بيتحوّل لتعليمات والـ CPU بتنفّذها واحدة ورا التانية بسرعة رهيبة، بالمليارات في الثانية، وده اللي بيتقاس بالـ GHz. جواها الـ ALU، ودي الحاسبة، بتعمل جمع وطرح ومقارنات. وفيه الـ Control Unit اللي بينظّم الشغل ويقول لكل جزء يعمل إيه وإمتى. وفيه الـ Registers، ذاكرة صغيرة جدًا وسريعة جدًا جوّه المعالج نفسه. وطبعًا فيه الـ RAM والـ Cache، دول برضو جوّه الـ CPU وبيخزّنوا الداتا اللي بيشتغل عليها.
- **Claims (raw, pre-glossary):**
  1. الـ CPU هو المخ الخاص بالجهاز.
  2. الـ CPU ينفّذ كل شيء.
  3. أي برنامج يتم تشغيله يتحول إلى تعليمات.
  4. الـ CPU ينفّذ التعليمات واحدةً تلو الأخرى بسرعة رهيبة بالمليارات في الثانية.
  5. سرعة الـ CPU تُقاس بالـ GHz.
  6. داخل الـ CPU يوجد الـ ALU.
  7. الـ ALU هو الحاسبة ويقوم بعمليات الجمع والطرح والمقارنات.
  8. داخل الـ CPU يوجد الـ Control Unit.
  9. الـ Control Unit ينظم العمل ويخبر كل جزء بما يجب عليه فعله ومتى.
  10. داخل الـ CPU يوجد الـ Registers.
  11. الـ Registers هي ذاكرة صغيرة جدًا وسريعة جدًا داخل المعالج نفسه.
  12. داخل الـ CPU يوجد الـ RAM والـ Cache.
  13. الـ RAM والـ Cache يخزّنان البيانات التي يعمل عليها المعالج.
- **Claims (final, post-glossary, D101):**
  1. ال CPU هو المخ الخاص بالجهاز.
  2. ال CPU ينفذ كل شيء.
  3. اي برنامج يتم تشغيله يتحول الى تعليمات.
  4. ال CPU ينفذ التعليمات واحدة تلو الاخرى بسرعة رهيبة بالمليارات في الثانية.
  5. سرعة ال CPU تقاس بال GHz.
  6. داخل ال CPU يوجد ال ALU.
  7. ال ALU هو الحاسبة ويقوم بعمليات الجمع والطرح والمقارنات.
  8. داخل ال CPU يوجد ال Control Unit.
  9. ال Control Unit ينظم العمل ويخبر كل جزء بما يجب عليه فعله ومتى.
  10. داخل ال CPU يوجد ال Registers.
  11. ال Registers هي ذاكرة صغيرة جدا وسريعة جدا داخل المعالج نفسه.
  12. داخل ال CPU يوجد ال RAM وال Cache.
  13. ال RAM وال Cache يخزنان البيانات التي يعمل عليها المعالج.
- **Transliteration audit:** 0 substitution(s), 0 residual ambiguous form(s) left untouched.
- **Key points:** 3 (GN004-C01, GN004-C02, GN004-C03)
- **zero_shot_raw arm:** status=SUCCESS, coverage_score=0.8681933333333333
  - per-key-point max P(entailment): [0.727703, 0.998902, 0.877975]
- **zero_shot_final arm:** status=SUCCESS, coverage_score=0.8841253333333333
  - per-key-point max P(entailment): [0.824458, 0.998933, 0.828985]
- **adapter_raw arm:** status=SUCCESS, coverage_score=0.35172800000000004
  - per-key-point max P(entailment): [0.023415, 0.977994, 0.053775]
- **adapter_final arm:** status=SUCCESS, coverage_score=0.345211
  - per-key-point max P(entailment): [0.020842, 0.980248, 0.034543]

## GN-012 (GN)

- **Decomposition status:** SUCCESS
- **Raw answer:** الاتنين عشان الموقع يفتكرك. الـ Cookie بيتحطّ على جهازك، في المتصفح، وعشان كده انت تقدر تشوفه وتمسحه لو عايز. وده اللي بيخلّي الموقع يفضل فاكرك مسجّل دخول حتى لو قفلت الصفحة. الـ Session بقى بيبقى على السيرفر، يعني الداتا نفسها مش عندك، اللي عندك بس رقم أو كود. الفرق العملي إن الـ Cookie ممكن حد يعبث فيه لأنه عندك، فالحاجات المهمة بيحطّوها في الـ session. والـ session بيقفل لما تقفل المتصفح غالبًا أو بعد وقت من غير حركة. صراحة الاتنين مربوطين ببعض بشكل ما مش قادر أفصّله بالظبط.
- **Claims (raw, pre-glossary):**
  1. الـ Cookie تُوضع على جهاز المستخدم في المتصفح.
  2. يستطيع المستخدم رؤية الـ Cookie وحذفها إذا أراد.
  3. الـ Cookie تجعل الموقع يظل يتذكر تسجيل دخول المستخدم حتى إذا أغلق الصفحة.
  4. الـ Session تُخزن على الخادم.
  5. بيانات الـ Session ليست لدى المستخدم، بل يملك المستخدم فقط رقمًا أو رمزًا يخص الـ Session.
  6. يمكن لأي شخص التلاعب بالـ Cookie لأنها موجودة على جهاز المستخدم.
  7. تُخزن المعلومات المهمة في الـ Session.
  8. الـ Session تُغلق عندما يُغلق المتصفح غالبًا.
  9. الـ Session تُغلق بعد فترة من عدم النشاط.
  10. الـ Cookie والـ Session مرتبطان ببعضهما بطريقة غير محددة لا يمكن فصلها بدقة.
- **Claims (final, post-glossary, D101):**
  1. ال Cookie توضع على جهاز المستخدم في المتصفح.
  2. يستطيع المستخدم رؤية ال Cookie وحذفها اذا اراد.
  3. ال Cookie تجعل الموقع يظل يتذكر تسجيل دخول المستخدم حتى اذا اغلق الصفحة.
  4. ال Session تخزن على الخادم.
  5. بيانات ال Session ليست لدى المستخدم، Pull يملك المستخدم فقط رقما او رمزا يخص ال Session.
  6. يمكن لاي شخص التلاعب بال Cookie لانها موجودة على جهاز المستخدم.
  7. تخزن المعلومات المهمة في ال Session.
  8. ال Session تغلق عندما يغلق المتصفح غالبا.
  9. ال Session تغلق بعد فترة من عدم النشاط.
  10. ال Cookie وال Session مرتبطان ببعضهما بطريقة غير محددة لا يمكن فصلها بدقة.
- **Transliteration audit:** 1 substitution(s), 1 residual ambiguous form(s) left untouched.
  - claim 4: `بل` → `Pull`
- **Key points:** 3 (GN012-C01, GN012-C02, GN012-C03)
- **zero_shot_raw arm:** status=SUCCESS, coverage_score=0.0016543333333333334
  - per-key-point max P(entailment): [0.000956, 0.003246, 0.000761]
- **zero_shot_final arm:** status=SUCCESS, coverage_score=0.001796
  - per-key-point max P(entailment): [0.000885, 0.003683, 0.00082]
- **adapter_raw arm:** status=SUCCESS, coverage_score=0.005653333333333333
  - per-key-point max P(entailment): [0.002335, 0.010501, 0.004124]
- **adapter_final arm:** status=SUCCESS, coverage_score=0.0057143333333333325
  - per-key-point max P(entailment): [0.002199, 0.011163, 0.003781]

## GN-042 (GN)

- **Decomposition status:** SUCCESS
- **Raw answer:** دي سهلة. الـ Syntax Error هو إنك كتبت غلط، نسيت قوس، نسيت فاصلة منقوطة، كتبت الكلمة غلط. الكود ده مش هيشتغل أصلًا، الـ compiler هيرفضه ويقولك السطر فيه إيه. في اللغات المفسَّرة زي Python مفيش syntax errors أصلًا لأن مفيش compiler… لأ، غلط، Python برضو بترفض الكود لو الـ syntax غلط، بس بترفضه وقت التشغيل. المهم، الـ Logical Error بقى ده أوحش بكتير، الكود شغال تمام، مفيش أي رسالة خطأ، بس النتيجة غلط. زي إنك تكتب `if x > 5` وانت قصدك `if x >= 5`. مفيش حاجة هتقولك، لازم انت تكتشفه بنفسك، يا إما بالـ testing يا إما لما حد يشتكي.
- **Claims (raw, pre-glossary):**
  1. هذا سهل.
  2. خطأ Syntax Error يحدث عندما تكتب خطأ.
  3. خطأ Syntax Error يحدث عندما تنسى قوسًا.
  4. خطأ Syntax Error يحدث عندما تنسى فاصلة منقوطة.
  5. خطأ Syntax Error يحدث عندما تكتب الكلمة خطأ.
  6. هذا الكود لن يعمل أصلاً.
  7. الـ compiler سيرفض الكود.
  8. الـ compiler سيخبرك بما فيه السطر.
  9. في اللغات المفسَّرة مثل Python لا توجد أخطاء Syntax Error أصلاً لأنه لا يوجد compiler.
  10. Python أيضًا ترفض الكود إذا كان الـ syntax خطأ.
  11. Python ترفض الكود وقت التشغيل.
  12. خطأ Logical Error هو أسوأ كثيرًا.
  13. الكود يعمل تمامًا.
  14. لا تظهر أي رسالة خطأ.
  15. النتيجة خاطئة.
  16. مثال: كتابة `if x > 5` وأنت تقصد `if x >= 5`.
  17. لا شيء سيخبرك.
  18. يجب عليك اكتشاف الخطأ بنفسك.
  19. يمكنك اكتشاف الخطأ بالـ testing.
  20. يمكنك اكتشاف الخطأ عندما يشتكي أحد.
- **Claims (final, post-glossary, D101):**
  1. هذا سهل.
  2. خطا Syntax Error يحدث عندما تكتب خطا.
  3. خطا Syntax Error يحدث عندما تنسى قوسا.
  4. خطا Syntax Error يحدث عندما تنسى فاصلة منقوطة.
  5. خطا Syntax Error يحدث عندما تكتب الكلمة خطا.
  6. هذا Code لن يعمل اصلا.
  7. ال compiler سيرفض Code.
  8. ال compiler سيخبرك بما فيه السطر.
  9. في اللغات المفسرة مثل Python لا توجد اخطاء Syntax Error اصلا لانه لا يوجد compiler.
  10. Python ايضا ترفض Code اذا كان ال syntax خطا.
  11. Python ترفض Code وقت التشغيل.
  12. خطا Logical Error هو اسوا كثيرا.
  13. Code يعمل تماما.
  14. لا تظهر اي رسالة خطا.
  15. النتيجة خاطئة.
  16. مثال: كتابة `if x > 5` وانت تقصد `if x >= 5`.
  17. لا شيء سيخبرك.
  18. يجب عليك اكتشاف الخطا بنفسك.
  19. يمكنك اكتشاف الخطا بال testing.
  20. يمكنك اكتشاف الخطا عندما يشتكي احد.
- **Transliteration audit:** 5 substitution(s), 0 residual ambiguous form(s) left untouched.
  - claim 5: `الكود` → `Code`
  - claim 6: `الكود` → `Code`
  - claim 9: `الكود` → `Code`
  - claim 10: `الكود` → `Code`
  - claim 12: `الكود` → `Code`
- **Key points:** 2 (GN042-C01, GN042-C04)
- **zero_shot_raw arm:** status=SUCCESS, coverage_score=0.0035275000000000003
  - per-key-point max P(entailment): [0.005097, 0.001958]
- **zero_shot_final arm:** status=SUCCESS, coverage_score=0.0023344999999999998
  - per-key-point max P(entailment): [0.002468, 0.002201]
- **adapter_raw arm:** status=SUCCESS, coverage_score=0.007377
  - per-key-point max P(entailment): [0.01127, 0.003484]
- **adapter_final arm:** status=SUCCESS, coverage_score=0.006089
  - per-key-point max P(entailment): [0.009037, 0.003141]

## GN-045 (GN)

- **Decomposition status:** SUCCESS
- **Raw answer:** SDK يعني Software Development Kit. هي حزمة بتنزّلها عشان تقدر تطوّر لحاجة معينة، زي مثلًا Android SDK لو هتعمل تطبيق أندرويد، أو SDK بتاع خدمة زي Firebase عشان تربطها ببرنامجك. جواها الأدوات والمكتبات اللي بتحتاجها. وفيها documentation طبعًا. صراحة الفرق بينها وبين مجرد library عادي مش واضح ليا أوي، أظن الـ SDK أشمل، فيها أدوات مش بس كود، زي emulator مثلًا في حالة الأندرويد.
- **Claims (raw, pre-glossary):**
  1. SDK هو اختصار لـ Software Development Kit.
  2. SDK هو حزمة تُنزل لتتمكن من التطوير لشيء معين.
  3. Android SDK هو مثال على SDK يُستخدم لإنشاء تطبيق أندرويد.
  4. SDK لخدمة Firebase هو مثال آخر يُستخدم لتربط الخدمة ببرنامجك.
  5. SDK يحتوي على الأدوات والمكتبات التي تحتاجها.
  6. SDK يحتوي على documentation.
  7. الفرق بين SDK و library عادي غير واضح للمتحدث.
  8. المتحدث يظن أن SDK أشمل من library عادي.
  9. SDK يحتوي على أدوات ليست مجرد كود.
  10. emulator هو مثال على أداة موجودة في SDK في حالة الأندرويد.
- **Claims (final, post-glossary, D101):**
  1. SDK هو اختصار ل Software Development Kit.
  2. SDK هو حزمة تنزل لتتمكن من التطوير لشيء معين.
  3. Android SDK هو مثال على SDK يستخدم لانشاء تطبيق Android.
  4. SDK لخدمة Firebase هو مثال اخر يستخدم لتربط الخدمة ببرنامجك.
  5. SDK يحتوي على الادوات والمكتبات التي تحتاجها.
  6. SDK يحتوي على documentation.
  7. الفرق بين SDK و library عادي غير واضح للمتحدث.
  8. المتحدث يظن ان SDK اشمل من library عادي.
  9. SDK يحتوي على ادوات ليست مجرد Code.
  10. emulator هو مثال على اداة موجودة في SDK في حالة Android.
- **Transliteration audit:** 3 substitution(s), 1 residual ambiguous form(s) left untouched.
  - claim 2: `اندرويد` → `Android`
  - claim 8: `كود` → `Code`
  - claim 9: `الاندرويد` → `Android`
- **Key points:** 3 (GN045-C01, GN045-C02, GN045-C05)
- **zero_shot_raw arm:** status=SUCCESS, coverage_score=0.06812433333333333
  - per-key-point max P(entailment): [0.004247, 0.001026, 0.1991]
- **zero_shot_final arm:** status=SUCCESS, coverage_score=0.027409666666666666
  - per-key-point max P(entailment): [0.004033, 0.001153, 0.077043]
- **adapter_raw arm:** status=SUCCESS, coverage_score=0.011949333333333333
  - per-key-point max P(entailment): [0.011574, 0.003097, 0.021177]
- **adapter_final arm:** status=SUCCESS, coverage_score=0.009618666666666666
  - per-key-point max P(entailment): [0.010865, 0.003441, 0.01455]

## GN-047 (GN)

- **Decomposition status:** SUCCESS
- **Raw answer:** الـ Regex دي حاجة أنا بكرهها وبحبها في نفس الوقت. هي طريقة إنك تدوّر على نمط في نص، مش كلمة محددة، لأ، شكل. يعني مثلًا عايز كل الأرقام اللي في صفحة، أو عايز تتأكد إن اللي المستخدم كتبه شكله شكل إيميل فعلًا: حروف، بعدين @، بعدين حروف، بعدين نقطة، بعدين com أو أي حاجة. بتُستخدم كتير في الـ validation دي، وفي البحث والاستبدال في الـ editors، وفي تنضيف الداتا. بس المشكلة إنها بتبقى شكلها زي الطلاسم، أنا بنفسي لما بكتب regex ومبيشتغلش برجع أنسخ واحد جاهز من الإنترنت وأعدّل فيه، ولما برجع أقراه بعد أسبوع مبقاش فاهمه.
- **Claims (raw, pre-glossary):**
  1. الـ Regex هو شيء أكرهه.
  2. الـ Regex هو شيء أحبه.
  3. الـ Regex طريقة للبحث عن نمط في نص وليس كلمة محددة بل شكل.
  4. أريد استخراج جميع الأرقام الموجودة في صفحة باستخدام الـ Regex.
  5. أريد التأكد من أن ما كتبه المستخدم يبدو كإيميل فعليًا باستخدام الـ Regex.
  6. نمط الإيميل يتكون من حروف ثم الرمز @ ثم حروف ثم نقطة ثم com أو أي شيء آخر.
  7. الـ Regex تُستخدم كثيرًا في الـ validation.
  8. الـ Regex تُستخدم في البحث والاستبدال في الـ editors.
  9. الـ Regex تُستخدم في تنقية البيانات.
  10. الـ Regex تبدو كطلاسم.
  11. عندما أكتب الـ Regex ولا يعمل، أستنسخ واحدًا جاهزًا من الإنترنت وأعدّل فيه.
  12. عندما أعود لقراءة الـ Regex بعد أسبوع لا أفهمه.
- **Claims (final, post-glossary, D101):**
  1. ال Regex هو شيء اكرهه.
  2. ال Regex هو شيء احبه.
  3. ال Regex طريقة للبحث عن نمط في نص وليس كلمة محددة Pull شكل.
  4. اريد استخراج جميع الارقام الموجودة في صفحة باستخدام ال Regex.
  5. اريد التاكد من ان ما كتبه المستخدم يبدو كايميل فعليا باستخدام ال Regex.
  6. نمط الايميل يتكون من حروف ثم الرمز @ ثم حروف ثم نقطة ثم com او اي شيء اخر.
  7. ال Regex تستخدم كثيرا في ال validation.
  8. ال Regex تستخدم في البحث والاستبدال في ال editors.
  9. ال Regex تستخدم في تنقية البيانات.
  10. ال Regex تبدو كطلاسم.
  11. عندما اكتب ال Regex ولا يعمل، استنسخ واحدا جاهزا من الانترنت واعدل فيه.
  12. عندما اعود لقراءة ال Regex بعد اسبوع لا افهمه.
- **Transliteration audit:** 1 substitution(s), 0 residual ambiguous form(s) left untouched.
  - claim 2: `بل` → `Pull`
- **Key points:** 3 (GN047-C01, GN047-C04, GN047-C05)
- **zero_shot_raw arm:** status=SUCCESS, coverage_score=0.2903116666666667
  - per-key-point max P(entailment): [0.868391, 0.001114, 0.00143]
- **zero_shot_final arm:** status=SUCCESS, coverage_score=0.3062643333333333
  - per-key-point max P(entailment): [0.9157, 0.001461, 0.001632]
- **adapter_raw arm:** status=SUCCESS, coverage_score=0.10825266666666666
  - per-key-point max P(entailment): [0.315056, 0.007315, 0.002387]
- **adapter_final arm:** status=SUCCESS, coverage_score=0.11971666666666668
  - per-key-point max P(entailment): [0.350046, 0.006423, 0.002681]
