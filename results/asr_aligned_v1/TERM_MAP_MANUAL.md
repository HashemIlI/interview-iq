# TERM_MAP_MANUAL

> قاموس موحّد مقترح لتحويل المصطلحات الإنجليزية المكتوبة داخل **إجابات المستخدم فقط** إلى نطق عربي قريب من مخرجات ASR، مع إبقاء الـClaims كما هي.

## نطاق الملف

- تم استخراجه من **5 ملفات** تحتوي **223 Answer blocks**.
- الجرد مأخوذ من النص بين `**إجابة:**` و`**الـ Claims:**` فقط.
- الصيغ العربية هنا **نطق صوتي مقترح** وليست ترجمة دلالية.
- لا تستخدم Replace All على الملف كاملًا؛ استبدل داخل Answer block المحدد فقط.
- فعّل البحث غير الحساس لحالة الأحرف في VS Code، واستبدل العبارات الأطول أولًا.
- لو ظهر مصطلح له نطق شائع مختلف في فريقك، عدّل هذا القاموس أولًا ثم التزم بصيغة واحدة في كل الداتا.

## Workflow اليدوي المختصر

1. حدّد النص من بعد `**إجابة:**` إلى قبل `**الـ Claims:**`.
2. اضغط `Ctrl + H`.
3. اضغط `Alt + L` لتفعيل **Find in Selection**.
4. ابحث عن المصطلح الإنجليزي وانسخ مقابله العربي من هذا الملف.
5. نفّذ العبارات المركبة قبل الكلمات المفردة.
6. راجع الـDiff وتأكد أن الـClaims لم تتغير.

## الأكثر تكرارًا — ابدأ بها

| المصطلح الإنجليزي | النطق العربي المقترح | مرات الظهور التقريبية داخل الإجابات |
|---|---|---:|
| `HTTP` | إتش تي تي بي | 21 |
| `Features` | فيتشرز | 11 |
| `Recall` | ريكول | 11 |
| `HTTPS` | إتش تي تي بي إس | 11 |
| `Precision` | بريسيجن | 10 |
| `DNS` | دي إن إس | 10 |
| `Python` | بايثون | 9 |
| `IP` | آي بي | 9 |
| `JSON` | جيسون | 8 |
| `TLS` | تي إل إس | 8 |
| `VPN` | في بي إن | 8 |
| `Overfitting` | أوفر فيتنج | 7 |
| `GROUP BY` | جروب باي | 7 |
| `Variance` | فاريانس | 7 |
| `Private` | برايفت | 7 |
| `Stack` | ستاك | 7 |
| `Hash` | هاش | 7 |
| `Normalization` | نورمالايزيشن | 6 |
| `Primary Key` | برايمري كي | 6 |
| `JavaScript` | جافاسكريبت | 6 |
| `Accuracy` | أكيورسي | 6 |
| `64-bit` | أربعة وستين بِت | 6 |
| `Agile` | أجايل | 6 |
| `Excel` | إكسل | 6 |
| `Linux` | لينكس | 6 |
| `Bias` | باياس | 6 |
| `GET` | جيت | 6 |
| `IQR` | آي كيو آر | 6 |
| `RSA` | آر إس إيه | 6 |
| `Histogram` | هيستوجرام | 5 |
| `Interface` | إنترفيس | 5 |
| `Power BI` | باور بي آي | 5 |
| `DELETE` | ديليت | 5 |
| `Pandas` | بانداز | 5 |
| `WHERE` | وير | 5 |
| `APIs` | إيه بي آيز | 5 |
| `IPv4` | آي بي في فور | 5 |
| `Java` | جافا | 5 |
| `O(n)` | أو إن | 5 |
| `POST` | بوست | 5 |
| `REST` | ريست | 5 |
| `Salt` | سولت | 5 |
| `AES` | إيه إي إس | 5 |
| `DAX` | داكس | 5 |
| `KNN` | كي إن إن | 5 |
| `MFA` | إم إف إيه | 5 |
| `TCP` | تي سي بي | 5 |
| `TP` | تي بي | 5 |
| `Cross-Validation` | كروس فاليديشن | 4 |
| `Abstract Class` | أبستراكت كلاس | 4 |
| `Interpreter` | إنتربريتر | 4 |
| `Transformer` | ترانسفورمر | 4 |
| `Regression` | ريجريشن | 4 |
| `Bar Chart` | بار تشارت | 4 |
| `Waterfall` | ووترفول | 4 |
| `ORDER BY` | أوردر باي | 4 |
| `Outliers` | أوتلايرز | 4 |
| `Rollback` | رول باك | 4 |
| `Backend` | باك إند | 4 |
| `Cookies` | كوكيز | 4 |

## العبارات المركبة — استبدل هذه القائمة أولًا (Longest Match First)

| المصطلح الإنجليزي | النطق العربي المقترح | مرات الظهور التقريبية |
|---|---|---:|
| `Security Information and Event Management` | سيكيوريتي إنفورميشن أند إيفنت مانجمنت | 1 |
| `Synthetic Minority Oversampling Technique` | سينثتك ماينوريتي أوفرسامبلنج تكنيك | 1 |
| `Application Programming Interface` | أبليكيشن بروجرامنج إنترفيس | 1 |
| `Generational Garbage Collection` | جينيريشنال جاربيج كوليكشن | 1 |
| `Multinomial Logistic Regression` | مالتينوميال لوجستك ريجريشن | 1 |
| `Representational State Transfer` | ريبريزنتيشنال ستيت ترانسفر | 1 |
| `Distributed Denial of Service` | ديستريبيوتد دينايل أوف سيرفيس | 1 |
| `Advanced Encryption Standard` | أدفانسد إنكريبشن ستاندرد | 1 |
| `Backpropagation Through Time` | باك بروباجيشن ثرو تايم | 1 |
| `Principal Component Analysis` | برينسيبال كومبوننت أناليسيس | 1 |
| `Stateful Inspection Firewall` | ستيتفول إنسبكشن فايروول | 1 |
| `Infrastructure as a Service` | إنفراستركشر أز أ سيرفيس | 1 |
| `Mini-batch Gradient Descent` | ميني باتش جراديانت ديسنت | 1 |
| `Natural Language Processing` | ناتشورال لانجويج بروسيسنج | 1 |
| `Stochastic Gradient Descent` | ستوكاستك جراديانت ديسنت | 1 |
| `Application Layer Firewall` | أبليكيشن لير فايروول | 1 |
| `Cross-Site Request Forgery` | كروس سايت ريكويست فورجري | 1 |
| `Inverse Document Frequency` | إنفيرس دوكيومنت فريكونسي | 1 |
| `JavaScript Object Notation` | جافاسكريبت أوبجكت نوتيشن | 1 |
| `Security Operations Center` | سيكيوريتي أوبريشنز سنتر | 1 |
| `Compile-time Polymorphism` | كومبايل تايم بوليمورفزم | 1 |
| `Data Analysis Expressions` | داتا أناليسيس إكسبريشنز | 1 |
| `Packet Filtering Firewall` | باكيت فلترنج فايروول | 1 |
| `Dimensionality Reduction` | دايمنشوناليتي ريدكشن | 1 |
| `Named Entity Recognition` | نيمد إنتيتي ريكوجنيشن | 1 |
| `Next-Generation Firewall` | نكست جينيريشن فايروول | 1 |
| `Vulnerability Assessment` | فالنرابيليتي أسيسمنت | 1 |
| `Container Orchestration` | كونتينر أوركستريشن | 1 |
| `Content Security Policy` | كونتنت سيكيوريتي بوليسي | 1 |
| `Curse of Dimensionality` | كيرس أوف دايمنشوناليتي | 1 |
| `Learning Rate Schedules` | ليرننج ريت شيديولز | 1 |
| `Transitive Dependencies` | ترانزيتف ديبندنسيز | 1 |
| `Trunk-Based Development` | ترنك بيسد ديفيلوبمنت | 1 |
| `Batch Gradient Descent` | باتش جراديانت ديسنت | 1 |
| `Continuous Integration` | كونتينيوس إنتجريشن | 1 |
| `Dynamic ARP Inspection` | داينامك آر بي إنسبكشن | 1 |
| `Garbage In Garbage Out` | جاربيج إن جاربيج آوت | 1 |
| `Long Short-Term Memory` | لونج شورت تيرم ميموري | 1 |
| `Prescriptive Analytics` | بريسكتف أناليتكس | 1 |
| `Reinforcement Learning` | رينفورسمنت ليرننج | 1 |
| `Separation of Concerns` | سيبريشن أوف كونسيرنز | 1 |
| `Simple Random Sampling` | سيمبل راندوم سامبلنج | 1 |
| `Vulnerability Scanning` | فالنرابيليتي سكاننج | 1 |
| `429 Too Many Requests` | فور هاندرد تو ناين تو ماني ريكويستس | 1 |
| `Asymmetric Encryption` | أسيمتريك إنكريبشن | 1 |
| `Bayesian Optimization` | بايزيان أوبتيميزيشن | 1 |
| `Binary Classification` | باينري كلاسيفيكيشن | 1 |
| `Certificate Authority` | سيرتيفيكيت أوثوريتي | 2 |
| `Continuous Deployment` | كونتينيوس ديبلويمنت | 1 |
| `Descriptive Analytics` | ديسكريبتف أناليتكس | 1 |
| `Google Cloud Platform` | جوجل كلاود بلاتفورم | 1 |
| `Google Compute Engine` | جوجل كومبيوت إنجن | 1 |
| `Hyperparameter Tuning` | هايبر باراميتر تيوننج | 1 |
| `Platform as a Service` | بلاتفورم أز أ سيرفيس | 1 |
| `Software as a Service` | سوفتوير أز أ سيرفيس | 1 |
| `Unsupervised Learning` | أنسوبرفايزد ليرننج | 1 |
| `Behavioral Detection` | بيهيفيورال ديتكشن | 1 |
| `Binary Cross-Entropy` | باينري كروس إنتروبي | 1 |
| `Box-and-Whisker Plot` | بوكس أند ويسكر بلوت | 1 |
| `Confounding Variable` | كونفاوندنج فاريابل | 1 |
| `Cross-Site Scripting` | كروس سايت سكريبتنج | 1 |
| `Diagnostic Analytics` | دايجنوستك أناليتكس | 1 |
| `Full Stack Developer` | فول ستاك ديفيلوبر | 1 |
| `Inversion of Control` | إنفرجن أوف كنترول | 1 |
| `Multiple Inheritance` | مالتيبل إنهيريتنس | 1 |
| `Predictive Analytics` | بريديكتف أناليتكس | 1 |
| `Runtime Polymorphism` | ران تايم بوليمورفزم | 2 |
| `Separation of Duties` | سيبريشن أوف ديوتيز | 1 |
| `Symmetric Encryption` | سيمتريك إنكريبشن | 1 |
| `Activation Function` | أكتيفيشن فانكشن | 2 |
| `Confidence Interval` | كونفيدنس إنتيرفال | 1 |
| `Continuous Delivery` | كونتينيوس ديليفري | 1 |
| `Credential Stuffing` | كريدنشل ستافنج | 1 |
| `Digital Certificate` | ديجيتال سيرتيفيكيت | 2 |
| `False Positive Rate` | فولس بوزيتف ريت | 1 |
| `Feature Engineering` | فيتشر إنجنيرنج | 1 |
| `Five-Number Summary` | فايف نامبر سامري | 1 |
| `Forward Propagation` | فوروارد بروباجيشن | 1 |
| `Logistic Regression` | لوجستك ريجريشن | 1 |
| `Normal Distribution` | نورمال ديستربيوشن | 1 |
| `Penetration Testing` | بينيترَيشن تيستنج | 2 |
| `Positional Encoding` | بوزيشنال إنكودنج | 1 |
| `Prime Factorization` | برايم فاكتورايزيشن | 1 |
| `Random Oversampling` | راندوم أوفرسامبلنج | 1 |
| `Relational Database` | ريليشنال داتابيز | 1 |
| `Self-selection Bias` | سيلف سيلكشن باياس | 1 |
| `Stratified Sampling` | ستراتيفايد سامبلنج | 1 |
| `Supervised Learning` | سوبرفايزد ليرننج | 2 |
| `Systematic Sampling` | سيستماتك سامبلنج | 1 |
| `Three-way Handshake` | ثري واي هاند شيك | 1 |
| `Arrange-Act-Assert` | أرينج أكت أسيرت | 1 |
| `Cache Invalidation` | كاش إنفاليديشن | 1 |
| `Calculated Columns` | كالكوليتد كولمنز | 1 |
| `Data Visualization` | داتا فيجوالايزيشن | 1 |
| `Digital Signatures` | ديجيتال سيجنتشرز | 2 |
| `Divide and Conquer` | ديفايد أند كونكر | 1 |
| `Exploding Gradient` | إكسبلودنج جراديانت | 1 |
| `Feature Extraction` | فيتشر إكستراكشن | 1 |
| `Garbage Collection` | جاربيج كوليكشن | 3 |
| `Horizontal Scaling` | هورايزونتال سكيلنج | 1 |
| `Imbalanced Dataset` | إمبالانسد داتا سيت | 1 |
| `Log Transformation` | لوج ترانسفورميشن | 2 |
| `Mean Squared Error` | مين سكويرد إيرور | 1 |
| `Method Overloading` | ميثود أوفرلودنج | 1 |
| `Microsoft Sentinel` | مايكروسوفت سينتينل | 1 |
| `Process Management` | بروسيس مانجمنت | 1 |
| `Red-Green-Refactor` | ريد جرين ريفاكتور | 1 |
| `Sentiment Analysis` | سنتيمنت أناليسيس | 1 |
| `Single Inheritance` | سينجل إنهيريتنس | 1 |
| `Social Engineering` | سوشيال إنجنيرنج | 1 |
| `Standard Deviation` | ستاندرد ديفييشن | 1 |
| `True Positive Rate` | ترو بوزيتف ريت | 1 |
| `Unique Constraints` | يونيك كونسترينتس | 1 |
| `Vanishing Gradient` | فانيشينج جراديانت | 2 |
| `Visual Studio Code` | فيجوال ستوديو كود | 1 |
| `Analysis Services` | أناليسيس سيرفيسز | 1 |
| `Cartesian Product` | كارتيزيان برودكت | 1 |
| `Cosine Similarity` | كوساين سيميلاريتي | 1 |
| `Data Storytelling` | داتا ستوري تيلنج | 1 |
| `Dictionary Attack` | ديكشنري أتاك | 1 |
| `Digital Forensics` | ديجيتال فورينزكس | 1 |
| `Dynamically Typed` | دايناميكلي تايبد | 1 |
| `Ensemble Learning` | إنسامبل ليرننج | 1 |
| `Feature Selection` | فيتشر سيلكشن | 1 |
| `Garbage Collector` | جاربيج كوليكتور | 1 |
| `Gradient Boosting` | جراديانت بوستنج | 1 |
| `Gradient Clipping` | جراديانت كليبنج | 1 |
| `Incident Response` | إنسيدنت ريسبونس | 1 |
| `Irreducible Error` | إيريديوسيبل إيرور | 1 |
| `L1 Regularization` | إل وان ريجولارايزيشن | 1 |
| `L2 Regularization` | إل تو ريجولارايزيشن | 1 |
| `Laplace Smoothing` | لابلاس سموذنج | 1 |
| `Least Connections` | ليست كونيكشنز | 1 |
| `Linear Regression` | لينير ريجريشن | 1 |
| `Man-in-the-Middle` | مان إن ذا ميدل | 2 |
| `Memory Management` | ميموري مانجمنت | 1 |
| `Method Overriding` | ميثود أوفرايدنج | 2 |
| `Non-response Bias` | نون ريسبونس باياس | 1 |
| `Out-of-Vocabulary` | أوت أوف فوكابيولاري | 1 |
| `Security Policies` | سيكيوريتي بوليسيز | 1 |
| `Stratified K-Fold` | ستراتيفايد كي فولد | 1 |
| `Survivorship Bias` | سرفايفورشيب باياس | 1 |
| `Time Intelligence` | تايم إنتليجنس | 1 |
| `Transfer Learning` | ترانسفر ليرننج | 1 |
| `Uniform Interface` | يونيفورم إنترفيس | 1 |
| `304 Not Modified` | ثري هاندرد فور نوت موديفايد | 1 |
| `401 Unauthorized` | فور هاندرد وان أن أوثرايزد | 1 |
| `Access Modifiers` | أكسس موديفايرز | 1 |
| `Borderline-SMOTE` | بوردرلاين سموت | 1 |
| `Business Context` | بزنس كونتكست | 1 |
| `Chain of Custody` | تشين أوف كاستودي | 1 |
| `Cluster Sampling` | كلستر سامبلنج | 1 |
| `Confusion Matrix` | كونفيوجن ماتريكس | 1 |
| `Cross-Validation` | كروس فاليديشن | 4 |
| `Defense in Depth` | ديفنس إن ديبث | 1 |
| `Development Team` | ديفيلوبمنت تيم | 1 |
| `Dimension Tables` | دايمنشن تيبلز | 1 |
| `Domain Knowledge` | دومين نولدج | 1 |
| `Double Extortion` | دابل إكستورشن | 1 |
| `Encrypted Tunnel` | إنكريبتد تانل | 1 |
| `Gradient Descent` | جراديانت ديسنت | 2 |
| `Information Gain` | إنفورميشن جين | 1 |
| `Isolation Levels` | آيزوليشن ليفلز | 1 |
| `Lateral Movement` | لاترال موفمنت | 1 |
| `Machine Learning` | ماشين ليرننج | 3 |
| `Mutual Exclusion` | ميوتشوال إكسكلوجن | 1 |
| `One-Hot Encoding` | وان هوت إنكودنج | 1 |
| `Operating System` | أوبريتنج سيستم | 1 |
| `Patch Management` | باتش مانجمنت | 1 |
| `Precision-Recall` | بريسيجن ريكول | 1 |
| `Request-Response` | ريكويست ريسبونس | 1 |
| `Snowflake Schema` | سنوفليك سكيما | 1 |
| `Software License` | سوفتوير لايسنس | 1 |
| `Space Complexity` | سبيس كومبلكسيتي | 1 |
| `Vertical Scaling` | فيرتيكال سكيلنج | 1 |
| `Window Functions` | ويندو فانكشنز | 3 |
| `Zero-Day Exploit` | زيرو داي إكسبلويت | 1 |
| `Access Controls` | أكسس كنترولز | 1 |
| `Agile Manifesto` | أجايل مانيفستو | 1 |
| `Character-level` | كاراكتر ليفل | 1 |
| `Cloud Computing` | كلاود كومبيوتنج | 1 |
| `Cohort Analysis` | كوهورت أناليسيس | 1 |
| `Commit Messages` | كوميت ميسجز | 1 |
| `Composite Index` | كومبوزت إندكس | 1 |
| `Counter Metrics` | كاونتر ميتريكس | 1 |
| `Data Dictionary` | داتا ديكشنري | 1 |
| `Data Governance` | داتا جوفرننس | 2 |
| `Data Structures` | داتا ستراكشرز | 1 |
| `Diamond Problem` | دايموند بروبلم | 1 |
| `Event Listeners` | إيفنت ليسنرز | 1 |
| `False Positives` | فولس بوزيتفز | 2 |
| `Feature Scaling` | فيتشر سكيلنج | 1 |
| `FULL OUTER JOIN` | فول أوتر جوين | 1 |
| `Full Table Scan` | فول تيبل سكان | 1 |
| `Fully Connected` | فولي كونيكتد | 1 |
| `Funnel Analysis` | فانل أناليسيس | 1 |
| `Least Privilege` | ليست بريفيليج | 1 |
| `Lessons Learned` | ليسونز ليرند | 1 |
| `Microsoft Azure` | مايكروسوفت أزور | 1 |
| `Min-Max Scaling` | مين ماكس سكيلنج | 1 |
| `Normal Equation` | نورمال إكويشن | 1 |
| `Null Hypothesis` | نال هايبوثيسس | 1 |
| `Offline Backups` | أوفلاين باك أبس | 1 |
| `Open Addressing` | أوبن أدرسينج | 1 |
| `Output Encoding` | أوتبوت إنكودنج | 1 |
| `Print Debugging` | برينت ديباجنج | 1 |
| `Product Backlog` | برودكت باك لوج | 1 |
| `Race Conditions` | ريس كونديشنز | 1 |
| `Red-Black Trees` | ريد بلاك تريز | 1 |
| `Risk Assessment` | ريسك أسيسمنت | 1 |
| `Risk Management` | ريسك مانجمنت | 1 |
| `Rolling Updates` | رولنج أبديتس | 1 |
| `Session Cookies` | سيشن كوكيز | 1 |
| `Signature-based` | سيجنتشر بيسد | 2 |
| `Smart Contracts` | سمارت كونتراكتس | 1 |
| `Sprint Planning` | سبرنت بلاننج | 1 |
| `Target Variable` | تارجت فاريابل | 1 |
| `Time Complexity` | تايم كومبلكسيتي | 1 |
| `Version Control` | فيرجن كنترول | 1 |
| `Z-score Scaling` | زي سكور سكيلنج | 1 |
| `204 No Content` | تو هاندرد فور نو كونتنت | 1 |
| `Abstract Class` | أبستراكت كلاس | 4 |
| `Apache Airflow` | أباتشي إيرفلو | 1 |
| `Business Logic` | بزنس لوجك | 1 |
| `Chain of Trust` | تشين أوف تراست | 1 |
| `Context Switch` | كونتكست سويتش | 1 |
| `Data Scientist` | داتا ساينتست | 3 |
| `Data Warehouse` | داتا ويرهاوس | 3 |
| `Decision Trees` | ديسيجن تريز | 1 |
| `Device Drivers` | ديفايس درايفرز | 1 |
| `Diffie-Hellman` | ديفي هيلمان | 1 |
| `DNS over HTTPS` | دي إن إس أوفر إتش تي تي بي إس | 1 |
| `Docker Compose` | دوكر كومبوز | 1 |
| `Extract Method` | إكستراكت ميثود | 1 |
| `False Negative` | فولس نيجاتف | 1 |
| `False Positive` | فولس بوزيتف | 1 |
| `Forensic Image` | فورينزك إيمج | 1 |
| `GitHub Actions` | جيت هب أكشنز | 1 |
| `Label Encoding` | ليبل إنكودنج | 1 |
| `Linus Torvalds` | لينوس تورفالدز | 1 |
| `Moving Average` | موفنج أفريج | 1 |
| `Neural Network` | نيورال نتورك | 1 |
| `Non-parametric` | نون بارامتريك | 1 |
| `Proxy Firewall` | بروكسي فايروول | 1 |
| `Rainbow Tables` | رينبو تيبلز | 1 |
| `Running Totals` | راننج توتالز | 1 |
| `Selection Bias` | سيلكشن باياس | 1 |
| `Self-Attention` | سيلف أتينشن | 1 |
| `Spam Filtering` | سبام فلترنج | 1 |
| `Spear Phishing` | سبير فيشينج | 1 |
| `Sprint Backlog` | سبرنت باك لوج | 1 |
| `Stack Overflow` | ستاك أوفرفلو | 3 |
| `Technical Debt` | تكنيكال دِت | 1 |
| `Term Frequency` | تيرم فريكونسي | 1 |
| `Threat Hunting` | ثريت هانتنج | 1 |
| `Vanity Metrics` | فانيتي ميتريكس | 1 |
| `Virtual Memory` | فيرتشوال ميموري | 1 |
| `Word Embedding` | وورد إمبيدنج | 1 |
| `403 Forbidden` | فور هاندرد ثري فوربيدن | 1 |
| `Anomaly-based` | أنومالي بيسد | 1 |
| `Binary Search` | باينري سيرش | 1 |
| `Cipher Suites` | سايفر سويتس | 1 |
| `Circular Wait` | سيركيولار ويت | 1 |
| `Class Weights` | كلاس ويتس | 1 |
| `Client-Server` | كلاينت سيرفر | 1 |
| `Daily Standup` | ديلي ستاند أب | 1 |
| `Data Cleaning` | داتا كليننج | 1 |
| `Decision Tree` | ديسيجن تري | 2 |
| `Deep Learning` | ديب ليرننج | 1 |
| `Desired State` | ديزايرد ستيت | 1 |
| `Feature Flags` | فيتشر فلاجز | 1 |
| `Gini Impurity` | جيني إمبيوريتي | 1 |
| `Google Sheets` | جوجل شيتس | 1 |
| `Harmonic Mean` | هارمونيك مين | 1 |
| `Hash Function` | هاش فانكشن | 1 |
| `Health Checks` | هيلث تشيكس | 1 |
| `Hidden Layers` | هيدن ليرز | 1 |
| `Hold and Wait` | هولد أند ويت | 1 |
| `IntelliJ IDEA` | إنتليج آيديا | 1 |
| `Learning Rate` | ليرننج ريت | 3 |
| `Load Balancer` | لود بالانسر | 2 |
| `Logical Error` | لوجيكال إيرور | 1 |
| `Message Queue` | ميسج كيو | 1 |
| `Microsoft 365` | مايكروسوفت ثري سيكستي فايف | 1 |
| `No Preemption` | نو بري إمبشن | 1 |
| `Out of Memory` | أوت أوف ميموري | 1 |
| `Pay-as-you-go` | باي أز يو جو | 1 |
| `Port Scanning` | بورت سكاننج | 1 |
| `Product Owner` | برودكت أونر | 1 |
| `Pull Requests` | بول ريكويستس | 2 |
| `Random Forest` | راندوم فورست | 3 |
| `Random Search` | راندوم سيرش | 1 |
| `Rate Limiting` | ريت ليمتنج | 3 |
| `Reflected XSS` | ريفلكتد إكس إس إس | 1 |
| `Remote Access` | ريموت أكسس | 1 |
| `Ruby on Rails` | روبي أون ريلز | 1 |
| `Saddle Points` | سادل بوينتس | 1 |
| `Sampling Bias` | سامبلنج باياس | 1 |
| `Sprint Review` | سبرنت ريفيو | 1 |
| `SSL Stripping` | إس إس إل ستريبنج | 1 |
| `Testing Guide` | تيستنج جايد | 1 |
| `True Negative` | ترو نيجاتف | 1 |
| `True Positive` | ترو بوزيتف | 1 |
| `Write-Through` | رايت ثرو | 1 |
| `Apache Kafka` | أباتشي كافكا | 1 |
| `Apache Spark` | أباتشي سبارك | 1 |
| `ARP Spoofing` | آر بي سبوفنج | 2 |
| `Block Cipher` | بلوك سايفر | 1 |
| `Cohort Table` | كوهورت تيبل | 1 |
| `Data Analyst` | داتا أناليست | 3 |
| `Data Leakage` | داتا ليكج | 2 |
| `DNS over TLS` | دي إن إس أوفر تي إل إس | 1 |
| `DNS Spoofing` | دي إن إس سبوفنج | 2 |
| `Feature Maps` | فيتشر مابس | 1 |
| `git checkout` | جيت تشيك آوت | 1 |
| `Hidden State` | هيدن ستيت | 1 |
| `Input/Output` | إنبوت أوتبوت | 1 |
| `Just-in-Time` | جاست إن تايم | 1 |
| `Labeled Data` | ليبلد داتا | 1 |
| `Local Minima` | لوكال مينيما | 1 |
| `Merge Commit` | ميرج كوميت | 1 |
| `Non-volatile` | نون فولاتايل | 1 |
| `Output Layer` | أوتبوت لير | 1 |
| `Parent Class` | بارنت كلاس | 1 |
| `PARTITION BY` | بارتيشن باي | 1 |
| `Peer-to-Peer` | بير تو بير | 1 |
| `Query String` | كويري سترينج | 1 |
| `Request Body` | ريكويست بادي | 1 |
| `Root Servers` | روت سيرفرز | 1 |
| `Scatter Plot` | سكاتر بلوت | 1 |
| `scikit-learn` | ساي كت ليرن | 1 |
| `Scrum Master` | سكرم ماستر | 1 |
| `Self-Healing` | سيلف هيلنج | 1 |
| `SIM Swapping` | سيم سوابنج | 1 |
| `TCP SYN Scan` | تي سي بي سين سكان | 1 |
| `Unique Index` | يونيك إندكس | 1 |
| `Unit Testing` | يونت تيستنج | 1 |
| `201 Created` | تو هاندرد وان كرييتد | 1 |
| `A/B Testing` | إيه بي تيستنج | 2 |
| `ASP.NET MVC` | إيه إس بي دوت نت إم في سي | 1 |
| `Bad Gateway` | باد جيتواي | 1 |
| `Brute Force` | بروت فورس | 2 |
| `Cache-Aside` | كاش أسايد | 1 |
| `Child Class` | تشايلد كلاس | 1 |
| `Code Points` | كود بوينتس | 1 |
| `Code Review` | كود ريفيو | 1 |
| `Code Smells` | كود سميلز | 1 |
| `CSRF Tokens` | سي إس آر إف توكنز | 1 |
| `Exact Match` | إكزاكت ماتش | 1 |
| `File System` | فايل سيستم | 1 |
| `Fine-tuning` | فاين تيوننج | 1 |
| `Foreign Key` | فورين كي | 3 |
| `GitHub Flow` | جيت هب فلو | 1 |
| `Grid Search` | جريد سيرش | 2 |
| `Input Layer` | إنبوت لير | 1 |
| `IPsec/IKEv2` | آي بي سيك آي كي إي في تو | 1 |
| `Linked List` | لينكد ليست | 2 |
| `Load Factor` | لود فاكتور | 1 |
| `Logic Gates` | لوجك جيتس | 1 |
| `Max Pooling` | ماكس بولنج | 1 |
| `Memory Leak` | ميموري ليك | 1 |
| `Model Drift` | مودل دريفت | 1 |
| `Multi-class` | مالتي كلاس | 1 |
| `Naive Bayes` | نايف بايز | 2 |
| `One-vs-Rest` | وان فيرسس ريست | 1 |
| `Open Source` | أوبن سورس | 1 |
| `Pivot Table` | بيفوت تيبل | 1 |
| `Power Pivot` | باور بيفوت | 1 |
| `Power Query` | باور كويري | 1 |
| `Primary Key` | برايمري كي | 6 |
| `Round Robin` | راوند روبن | 1 |
| `Source Code` | سورس كود | 1 |
| `Stack Trace` | ستاك تريس | 1 |
| `Star Schema` | ستار سكيما | 2 |
| `Amazon EC2` | أمازون إي سي تو | 1 |
| `Amazon SQS` | أمازون إس كيو إس | 1 |
| `Arch Linux` | آرتش لينكس | 1 |
| `Cache Miss` | كاش ميس | 1 |
| `Call Stack` | كول ستاك | 1 |
| `Cell State` | سيل ستيت | 1 |
| `Clean Code` | كلين كود | 1 |
| `CROSS JOIN` | كروس جوين | 1 |
| `Data Marts` | داتا مارتس | 2 |
| `Docker Hub` | دوكر هب | 1 |
| `Drill-down` | دريل داون | 1 |
| `Dying ReLU` | داينج ريلو | 1 |
| `End-to-End` | إند تو إند | 1 |
| `Fact Table` | فاكت تيبل | 1 |
| `git branch` | جيت برانش | 1 |
| `git commit` | جيت كوميت | 1 |
| `git rebase` | جيت ريبيس | 1 |
| `git status` | جيت ستاتس | 1 |
| `git switch` | جيت سويتش | 1 |
| `Hash Table` | هاش تيبل | 2 |
| `Heap Dumps` | هيب دامبس | 1 |
| `IBM QRadar` | آي بي إم كيو رادار | 1 |
| `INNER JOIN` | إنر جوين | 1 |
| `Leaky ReLU` | ليكي ريلو | 1 |
| `Mini-batch` | ميني باتش | 1 |
| `Non-convex` | نون كونفكس | 1 |
| `RIGHT JOIN` | رايت جوين | 1 |
| `Round Trip` | راوند تريب | 1 |
| `SQL Server` | إس كيو إل سيرفر | 2 |
| `Stored XSS` | ستورِد إكس إس إس | 1 |
| `Web Server` | ويب سيرفر | 1 |
| `Word-level` | وورد ليفل | 1 |
| `Write-Back` | رايت باك | 1 |
| `Zero Trust` | زيرو تراست | 1 |
| `Bar Chart` | بار تشارت | 4 |
| `Base Case` | بيس كيس | 1 |
| `CIA Triad` | سي آي إيه تراياد | 1 |
| `Data Link` | داتا لينك | 1 |
| `Data Mart` | داتا مارت | 1 |
| `git clone` | جيت كلون | 1 |
| `git merge` | جيت ميرج | 1 |
| `GitLab CI` | جيت لاب سي آي | 1 |
| `K-Means++` | كي مينز بلس بلس | 1 |
| `LEFT JOIN` | ليفت جوين | 2 |
| `Max Depth` | ماكس ديبث | 1 |
| `R-squared` | آر سكويرد | 2 |
| `REST APIs` | ريست إيه بي آيز | 1 |
| `Root Node` | روت نود | 1 |
| `SELF JOIN` | سيلف جوين | 1 |
| `1024 bit` | ألف أربعة وعشرين بِت | 1 |
| `2048 bit` | ألفين تمانية وأربعين بِت | 1 |
| `Big Data` | بيج داتا | 1 |
| `Box Plot` | بوكس بلوت | 3 |
| `Drop-off` | دروب أوف | 1 |
| `F1-Score` | إف وان سكور | 2 |
| `Git Flow` | جيت فلو | 2 |
| `git pull` | جيت بول | 1 |
| `git push` | جيت بوش | 1 |
| `GROUP BY` | جروب باي | 7 |
| `In-order` | إن أوردر | 1 |
| `Log Loss` | لوج لوس | 1 |
| `O(log n)` | أو لوج إن | 3 |
| `ORDER BY` | أوردر باي | 4 |
| `Power BI` | باور بي آي | 5 |
| `Zero-Day` | زيرو داي | 2 |
| `128 bit` | مية تمانية وعشرين بِت | 3 |
| `256 bit` | ميتين ستة وخمسين بِت | 1 |
| `At Risk` | أت ريسك | 1 |
| `git add` | جيت أَد | 1 |
| `git log` | جيت لوج | 1 |
| `IP Hash` | آي بي هاش | 1 |
| `K-Means` | كي مينز | 2 |
| `One-Hot` | وان هوت | 1 |
| `p-value` | بي فاليو | 2 |
| `Root CA` | روت سي إيه | 1 |
| `SHA-256` | شا تو فايف سيكس | 1 |
| `SSL/TLS` | إس إس إل تي إل إس | 2 |
| `TLS 1.3` | تي إل إس وان بوينت ثري | 1 |
| `Z-Score` | زي سكور | 2 |
| `200 OK` | تو هاندرد أو كي | 1 |
| `32-bit` | اتنين وتلاتين بِت | 4 |
| `64-bit` | أربعة وستين بِت | 6 |
| `B-Tree` | بي تري | 1 |
| `can-do` | كان دو | 1 |
| `F-beta` | إف بيتا | 1 |
| `K-Fold` | كي فولد | 1 |
| `TCP/IP` | تي سي بي آي بي | 1 |
| `TF-IDF` | تي إف آي دي إف | 1 |
| `Tier 1` | تير وان | 1 |
| `Big O` | بيج أو | 1 |
| `CI/CD` | سي آي سي دي | 1 |
| `UTF-8` | يو تي إف إيت | 2 |
| `Wi-Fi` | واي فاي | 2 |
| `is-a` | إز إيه | 2 |

## الاختصارات والأوامر وأسماء الدوال والكود

| المصطلح الإنجليزي | النطق العربي المقترح | مرات الظهور التقريبية |
|---|---|---:|
| `drop_duplicates` | دروب دوبليكيتس | 2 |
| `col_index_num` | كول إندكس نام | 2 |
| `lookup_value` | لوك أب فاليو | 1 |
| `range_lookup` | رينج لوك أب | 1 |
| `customer_id` | كاستمر آي دي | 2 |
| `example.com` | إكزامبل دوت كوم | 1 |
| `pivot_table` | بيفوت تيبل | 1 |
| `table_array` | تيبل أراي | 1 |
| `collection` | كوليكشن | 1 |
| `DENSE_RANK` | دينس رانك | 1 |
| `duplicated` | دوبليكيتد | 1 |
| `ROW_NUMBER` | رو نامبر | 1 |
| `CALCULATE` | كالكوليت | 1 |
| `makeSound` | ميك ساوند | 1 |
| `read_csv` | ريد سي إس في | 1 |
| `TOTALYTD` | توتال واي تي دي | 1 |
| `TRUNCATE` | ترانكيت | 3 |
| `withdraw` | ويذدرو | 1 |
| `Word2Vec` | وورد تو فيك | 1 |
| `AVERAGE` | أفريج | 1 |
| `CAPTCHA` | كابتشا | 1 |
| `deposit` | ديبوزت | 1 |
| `dequeue` | دي كيو | 1 |
| `develop` | ديفيلوب | 1 |
| `enqueue` | إن كيو | 1 |
| `groupby` | جروب باي | 2 |
| `VLOOKUP` | في لوك أب | 2 |
| `XLOOKUP` | إكس لوك أب | 1 |
| `ADASYN` | أداسين | 1 |
| `Argon2` | أرجون تو | 1 |
| `bcrypt` | بي كريبت | 2 |
| `concat` | كونكات | 1 |
| `DELETE` | ديليت | 5 |
| `DNSSEC` | دي إن إس سيك | 1 |
| `dropna` | دروب إن إيه | 1 |
| `except` | إكسبت | 1 |
| `fillna` | فيل إن إيه | 1 |
| `HAVING` | هافينج | 3 |
| `INSERT` | إنسيرت | 1 |
| `malloc` | مالوك | 1 |
| `scrypt` | إس كريبت | 1 |
| `subset` | ساب سيت | 1 |
| `UPDATE` | أبديت | 1 |
| `ASCII` | أسكي | 4 |
| `catch` | كاتش | 1 |
| `chmod` | تش مود | 1 |
| `chown` | تش أون | 1 |
| `CNAME` | سي نيم | 1 |
| `COUNT` | كاونت | 3 |
| `FALSE` | فولس | 1 |
| `HTTPS` | إتش تي تي بي إس | 11 |
| `macOS` | ماك أو إس | 1 |
| `merge` | ميرج | 1 |
| `mkdir` | ميك دير | 1 |
| `order` | أوردر | 1 |
| `OWASP` | أو واسب | 3 |
| `print` | برينت | 1 |
| `RDBMS` | آر دي بي إم إس | 1 |
| `SMART` | سمارت | 1 |
| `SMOTE` | سموت | 3 |
| `WHERE` | وير | 5 |
| `WHILE` | وايل | 1 |
| `X.509` | إكس فايف أو ناين | 1 |
| `AAAA` | كواد إيه | 1 |
| `ABAC` | إيه بي إيه سي | 1 |
| `ACID` | أسيد | 2 |
| `ASVS` | إيه إس في إس | 1 |
| `BERT` | بيرت | 3 |
| `beta` | بيتا | 1 |
| `BIOS` | بايوس | 1 |
| `CSRF` | سي إس آر إف | 2 |
| `CVSS` | سي في إس إس | 2 |
| `DESC` | دي إي إس سي | 1 |
| `DROP` | دروب | 2 |
| `ELSE` | إلس | 1 |
| `FIFO` | فايفو | 2 |
| `free` | فري | 1 |
| `grep` | جريب | 1 |
| `gRPC` | جي آر بي سي | 1 |
| `HSTS` | إتش إس تي إس | 1 |
| `HTML` | إتش تي إم إل | 4 |
| `HTTP` | إتش تي تي بي | 21 |
| `IPv4` | آي بي في فور | 5 |
| `IPv6` | آي بي في سكس | 2 |
| `JOIN` | جوين | 1 |
| `JSON` | جيسون | 8 |
| `keep` | كيب | 1 |
| `kill` | كيل | 1 |
| `LEAD` | ليد | 1 |
| `LIFO` | لايفو | 2 |
| `LSTM` | إل إس تي إم | 3 |
| `main` | مين | 2 |
| `NGFW` | إن جي إف دبليو | 1 |
| `NIST` | نيست | 1 |
| `NULL` | نال | 3 |
| `O(1)` | أو وان | 3 |
| `OCSP` | أو سي إس بي | 1 |
| `OLAP` | أو إل إيه بي | 1 |
| `OLTP` | أو إل تي بي | 1 |
| `OVER` | أوفر | 1 |
| `peek` | بيك | 1 |
| `POST` | بوست | 5 |
| `RANK` | رانك | 1 |
| `RBAC` | آر بي إيه سي | 2 |
| `REST` | ريست | 5 |
| `RMSE` | آر إم إس إي | 2 |
| `SIEM` | سيم | 3 |
| `SSIS` | إس إس آي إس | 1 |
| `TOTP` | تي أو تي بي | 1 |
| `WPA2` | دبليو بي إيه تو | 1 |
| `YAML` | يامِل | 1 |
| `1NF` | وان إن إف | 2 |
| `2FA` | تو فاكتور أوثنتيكيشن | 1 |
| `2NF` | تو إن إف | 2 |
| `2xx` | تو إكس إكس | 1 |
| `3NF` | ثري إن إف | 1 |
| `3xx` | ثري إكس إكس | 1 |
| `4xx` | فور إكس إكس | 1 |
| `5xx` | فايف إكس إكس | 1 |
| `ACL` | إيه سي إل | 1 |
| `AES` | إيه إي إس | 5 |
| `AND` | أند | 1 |
| `API` | إيه بي آي | 3 |
| `APT` | إيه بي تي | 1 |
| `ARP` | آر بي | 4 |
| `ASC` | إيه إس سي | 1 |
| `AUC` | إيه يو سي | 3 |
| `AUP` | إيه يو بي | 1 |
| `AVG` | أفريج | 2 |
| `AVL` | إيه في إل | 1 |
| `AWS` | إيه دبليو إس | 1 |
| `BFS` | بي إف إس | 1 |
| `BPE` | بي بي إي | 1 |
| `bps` | بتس بير سيكند | 1 |
| `BST` | بي إس تي | 2 |
| `C++` | سي بلس بلس | 4 |
| `CDN` | سي دي إن | 1 |
| `CLI` | سي إل آي | 1 |
| `CNN` | سي إن إن | 2 |
| `com` | دوت كوم | 1 |
| `CRL` | سي آر إل | 1 |
| `CSS` | سي إس إس | 3 |
| `CSV` | سي إس في | 1 |
| `DAX` | داكس | 5 |
| `DES` | دي إي إس | 2 |
| `DNS` | دي إن إس | 10 |
| `DOM` | دوم | 2 |
| `DPI` | دي بي آي | 1 |
| `DRY` | دراي | 1 |
| `EDA` | إي دي إيه | 1 |
| `EDR` | إي دي آر | 2 |
| `ELT` | إي إل تي | 2 |
| `EMA` | إي إم إيه | 1 |
| `ETL` | إي تي إل | 3 |
| `FOR` | فور | 1 |
| `GET` | جيت | 6 |
| `GPT` | جي بي تي | 2 |
| `GRU` | جي آر يو | 2 |
| `GUI` | جي يو آي | 1 |
| `IDE` | آي دي إي | 1 |
| `IDF` | آي دي إف | 1 |
| `IDS` | آي دي إس | 3 |
| `IPC` | آي بي سي | 1 |
| `IPS` | آي بي إس | 4 |
| `IQR` | آي كيو آر | 6 |
| `JVM` | جي في إم | 1 |
| `KNN` | كي إن إن | 5 |
| `KPI` | كي بي آي | 3 |
| `LAG` | لاج | 1 |
| `LRU` | إل آر يو | 1 |
| `LTV` | إل تي في | 1 |
| `MAC` | ماك | 2 |
| `MAE` | إم إيه إي | 2 |
| `man` | مان | 1 |
| `MD5` | إم دي فايف | 1 |
| `MFA` | إم إف إيه | 5 |
| `MIT` | إم آي تي | 1 |
| `MSE` | إم إس إي | 2 |
| `MTV` | إم تي في | 1 |
| `MVC` | إم في سي | 2 |
| `NAT` | نات | 1 |
| `NER` | إن إي آر | 1 |
| `NLP` | إن إل بي | 1 |
| `NOT` | نوت | 1 |
| `NSE` | إن إس إي | 1 |
| `OOP` | أو أو بي | 1 |
| `OSI` | أو إس آي | 2 |
| `PCA` | بي سي إيه | 3 |
| `PHP` | بي إتش بي | 1 |
| `PKI` | بي كي آي | 2 |
| `pop` | بوب | 1 |
| `PUT` | بوت | 1 |
| `pwd` | بي دبليو دي | 1 |
| `RAM` | رام | 3 |
| `RDP` | آر دي بي | 1 |
| `RFM` | آر إف إم | 1 |
| `RNN` | آر إن إن | 1 |
| `ROC` | آر أو سي | 4 |
| `ROM` | روم | 4 |
| `RSA` | آر إس إيه | 6 |
| `SGD` | إس جي دي | 2 |
| `SMA` | إس إم إيه | 1 |
| `SMS` | إس إم إس | 1 |
| `SOC` | سوك | 2 |
| `SQL` | إس كيو إل | 4 |
| `SSH` | إس إس إتش | 2 |
| `SSL` | إس إس إل | 1 |
| `SUM` | سام | 4 |
| `SVM` | إس في إم | 2 |
| `SVN` | إس في إن | 1 |
| `SYN` | سين | 1 |
| `TCP` | تي سي بي | 5 |
| `TDD` | تي دي دي | 2 |
| `TLD` | تي إل دي | 1 |
| `TLS` | تي إل إس | 8 |
| `try` | تراي | 1 |
| `TTL` | تي تي إل | 2 |
| `UDP` | يو دي بي | 3 |
| `URL` | يو آر إل | 3 |
| `USB` | يو إس بي | 1 |
| `VPN` | في بي إن | 8 |
| `XML` | إكس إم إل | 2 |
| `XSS` | إكس إس إس | 2 |
| `AI` | إيه آي | 1 |
| `C#` | سي شارب | 3 |
| `CA` | سي إيه | 1 |
| `cd` | سي دي | 1 |
| `CI` | سي آي | 3 |
| `cp` | سي بي | 1 |
| `F1` | إف وان | 4 |
| `F2` | إف تو | 1 |
| `FN` | إف إن | 2 |
| `FP` | إف بي | 2 |
| `GB` | جيجا بايت | 2 |
| `IF` | إف | 1 |
| `IP` | آي بي | 9 |
| `L1` | إل وان | 2 |
| `L2` | إل تو | 2 |
| `ls` | إل إس | 1 |
| `mv` | إم في | 1 |
| `MX` | إم إكس | 1 |
| `OR` | أور | 1 |
| `ps` | بي إس | 1 |
| `rm` | آر إم | 1 |
| `TF` | تي إف | 1 |
| `TN` | تي إن | 1 |
| `TP` | تي بي | 5 |
| `VM` | في إم | 1 |

## الكلمات المفردة وأسماء الأدوات والتقنيات

| المصطلح الإنجليزي | النطق العربي المقترح | مرات الظهور التقريبية |
|---|---|---:|
| `Features` | فيتشرز | 11 |
| `Recall` | ريكول | 11 |
| `Precision` | بريسيجن | 10 |
| `Python` | بايثون | 9 |
| `Hash` | هاش | 7 |
| `Overfitting` | أوفر فيتنج | 7 |
| `Private` | برايفت | 7 |
| `Stack` | ستاك | 7 |
| `Variance` | فاريانس | 7 |
| `Accuracy` | أكيورسي | 6 |
| `Agile` | أجايل | 6 |
| `Bias` | باياس | 6 |
| `Excel` | إكسل | 6 |
| `JavaScript` | جافاسكريبت | 6 |
| `Linux` | لينكس | 6 |
| `Normalization` | نورمالايزيشن | 6 |
| `APIs` | إيه بي آيز | 5 |
| `Histogram` | هيستوجرام | 5 |
| `Interface` | إنترفيس | 5 |
| `Java` | جافا | 5 |
| `O(n)` | أو إن | 5 |
| `Pandas` | بانداز | 5 |
| `Salt` | سولت | 5 |
| `Backend` | باك إند | 4 |
| `Bit` | بِت | 4 |
| `Cookies` | كوكيز | 4 |
| `Django` | جانجو | 4 |
| `Git` | جيت | 4 |
| `Hashing` | هاشينج | 4 |
| `Heap` | هيب | 4 |
| `Interpreter` | إنتربريتر | 4 |
| `Outliers` | أوتلايرز | 4 |
| `Public` | بابلك | 4 |
| `Regression` | ريجريشن | 4 |
| `Rollback` | رول باك | 4 |
| `Tableau` | تابلو | 4 |
| `Transformer` | ترانسفورمر | 4 |
| `Waterfall` | ووترفول | 4 |
| `Bagging` | باجنج | 3 |
| `Boosting` | بوستنج | 3 |
| `Byte` | بايت | 3 |
| `Caching` | كاشنج | 3 |
| `Classification` | كلاسيفيكيشن | 3 |
| `Compiler` | كومبايلر | 3 |
| `Debugger` | ديباجر | 3 |
| `Hyperparameters` | هايبر باراميترز | 3 |
| `IaaS` | آي إيه إيه إس | 3 |
| `Integrity` | إنتيجريتي | 3 |
| `Kubernetes` | كوبرنيتس | 3 |
| `Localhost` | لوكال هوست | 3 |
| `Median` | ميديان | 3 |
| `NumPy` | نامباي | 3 |
| `Pseudocode` | سودو كود | 3 |
| `SaaS` | إس إيه إيه إس | 3 |
| `Scaling` | سكيلنج | 3 |
| `Sigmoid` | سيجمويد | 3 |
| `Standardization` | ستاندردايزيشن | 3 |
| `Trojan` | تروجان | 3 |
| `Android` | أندرويد | 2 |
| `Angular` | أنجولار | 2 |
| `Animal` | أنيمال | 2 |
| `Array` | أراي | 2 |
| `Availability` | أفيليبيليتي | 2 |
| `Backdoor` | باك دور | 2 |
| `Berkeley` | بيركلي | 2 |
| `Binary` | باينري | 2 |
| `Bins` | بينز | 2 |
| `Bug` | بَج | 2 |
| `Cache` | كاش | 2 |
| `Cat` | كات | 2 |
| `Categorical` | كاتيجوريكال | 2 |
| `Confidentiality` | كونفيدنشاليتي | 2 |
| `Consistency` | كونسيستنسي | 2 |
| `Container` | كونتينر | 2 |
| `Controller` | كنترولر | 2 |
| `Correlation` | كوريليشن | 2 |
| `Customers` | كاستمرز | 2 |
| `DDoS` | دي دوس | 2 |
| `Docker` | دوكر | 2 |
| `Dog` | دوج | 2 |
| `Encapsulation` | إنكابسوليشن | 2 |
| `Ensemble` | إنسامبل | 2 |
| `Extract` | إكستراكت | 2 |
| `Frontend` | فرونت إند | 2 |
| `Go` | جو | 2 |
| `Gradient` | جراديانت | 2 |
| `Image` | إيمج | 2 |
| `Inheritance` | إنهيريتنس | 2 |
| `Interpreted` | إنتربريتد | 2 |
| `Iterative` | إتيريتف | 2 |
| `Load` | لود | 2 |
| `Matplotlib` | ماتبلوتليب | 2 |
| `Mean` | مين | 2 |
| `Microservices` | مايكروسيرفيسز | 2 |
| `Microsoft` | مايكروسوفت | 2 |
| `Mode` | مود | 2 |
| `Model` | مودل | 2 |
| `Monolith` | مونوليث | 2 |
| `Nmap` | إن ماب | 2 |
| `Node.js` | نود جي إس | 2 |
| `Orders` | أوردرز | 2 |
| `PaaS` | بي إيه إيه إس | 2 |
| `Parameters` | باراميترز | 2 |
| `Patch` | باتش | 2 |
| `Phishing` | فيشينج | 2 |
| `Pipes` | بايبس | 2 |
| `Polymorphism` | بوليمورفزم | 2 |
| `PostgreSQL` | بوستجري إس كيو إل | 2 |
| `Process` | بروسيس | 2 |
| `Queue` | كيو | 2 |
| `Refactoring` | ريفاكتورنج | 2 |
| `ReLU` | ريلو | 2 |
| `Rust` | راست | 2 |
| `Scrum` | سكرم | 2 |
| `Seaborn` | سيبورن | 2 |
| `Segmentation` | سيجمنتيشن | 2 |
| `Softmax` | سوفت ماكس | 2 |
| `Subword` | ساب وورد | 2 |
| `Symmetric` | سيمتريك | 2 |
| `Transform` | ترانسفورم | 2 |
| `Unicode` | يونيكود | 2 |
| `View` | فيو | 2 |
| `Visualization` | فيجوالايزيشن | 2 |
| `Weights` | ويتس | 2 |
| `Windows` | ويندوز | 2 |
| `Abstraction` | أبستراكشن | 1 |
| `Accept` | أكسِبت | 1 |
| `Action` | أكشن | 1 |
| `Actionable` | أكشنابل | 1 |
| `AdaBoost` | أدا بوست | 1 |
| `Adam` | آدم | 1 |
| `Adleman` | أدلمان | 1 |
| `Admin` | أدمن | 1 |
| `Agent` | إيجنت | 1 |
| `Algorithm` | ألجوريثم | 1 |
| `AlphaGo` | ألفا جو | 1 |
| `Anomalies` | أنوماليز | 1 |
| `Asset` | أسيت | 1 |
| `Assets` | أسيتس | 1 |
| `Asymmetric` | أسيمتريك | 1 |
| `Atomic` | أتومك | 1 |
| `Atomicity` | أتوميسيتي | 1 |
| `Attention` | أتينشن | 1 |
| `Authentication` | أوثنتيكيشن | 1 |
| `Authoritative` | أوثوريتاتيف | 1 |
| `Authorization` | أوثورايزيشن | 1 |
| `Avoid` | أفويد | 1 |
| `Azure` | أزور | 1 |
| `Backpropagation` | باك بروباجيشن | 1 |
| `Baiting` | بيتنج | 1 |
| `Balance` | بالانس | 1 |
| `BankAccount` | بانك أكاونت | 1 |
| `Baseline` | بيسلاين | 1 |
| `Bash` | باش | 1 |
| `Bayes` | بايز | 1 |
| `Bernoulli` | برنولي | 1 |
| `Biases` | باياسز | 1 |
| `Biometrics` | بايومتريكس | 1 |
| `Bitcoin` | بيتكوين | 1 |
| `Blockchain` | بلوك تشين | 1 |
| `Booting` | بوتنج | 1 |
| `Bootstrap` | بوتستراب | 1 |
| `Botnets` | بوت نتس | 1 |
| `Branches` | برانشز | 1 |
| `Branching` | برانشينج | 1 |
| `Breakpoints` | بريك بوينتس | 1 |
| `Build` | بيلد | 1 |
| `Bytecode` | بايت كود | 1 |
| `Cacheability` | كاشابيليتي | 1 |
| `Capping` | كابنج | 1 |
| `Causation` | كوزيشن | 1 |
| `CentOS` | سينت أو إس | 1 |
| `Centroids` | سينترويدز | 1 |
| `Chaining` | تشيننج | 1 |
| `Champions` | تشامبيونز | 1 |
| `Class` | كلاس | 1 |
| `Classes` | كلاسز | 1 |
| `Client` | كلاينت | 1 |
| `ClientHello` | كلاينت هلو | 1 |
| `Clustering` | كلسترنج | 1 |
| `Clusters` | كلسترز | 1 |
| `Collision` | كوليشن | 1 |
| `Commits` | كوميتس | 1 |
| `Committed` | كوميتد | 1 |
| `Compiled` | كومبايلد | 1 |
| `Completeness` | كومبليتنس | 1 |
| `Consensus` | كونسينسوس | 1 |
| `Constructor` | كونستركتور | 1 |
| `Constructors` | كونستركتورز | 1 |
| `Consumer` | كونسيومر | 1 |
| `Containers` | كونتينرز | 1 |
| `Containment` | كونتينمنت | 1 |
| `Context` | كونتكست | 1 |
| `Continuous` | كونتينيوس | 1 |
| `Contract` | كونتراكت | 1 |
| `Convenience` | كونفينيانس | 1 |
| `Conversion` | كونفرجن | 1 |
| `Convolution` | كونفوليوشن | 1 |
| `Copyleft` | كوبي ليفت | 1 |
| `Corpus` | كوربس | 1 |
| `Correctness` | كوريكتنس | 1 |
| `Dashboard` | داشبورد | 1 |
| `Dashboards` | داشبوردز | 1 |
| `DataFrame` | داتا فريم | 1 |
| `Deadlock` | ديدلوك | 1 |
| `Debian` | ديبيان | 1 |
| `Debugging` | ديباجنج | 1 |
| `Decision` | ديسيجن | 1 |
| `Decoupling` | دي كابلنج | 1 |
| `Deletion` | ديليشن | 1 |
| `Denormalization` | دي نورمالايزيشن | 1 |
| `Deploy` | ديبلوي | 1 |
| `Deterministic` | ديترمينيستك | 1 |
| `DevOps` | ديف أوبس | 1 |
| `Diamond` | دايموند | 1 |
| `Digest` | دايجست | 1 |
| `Dimensional` | دايمنشنال | 1 |
| `Discrete` | ديسكريت | 1 |
| `Distributed` | ديستريبيوتد | 1 |
| `Distribution` | ديستريبيوشن | 1 |
| `Divergence` | دايفرجنس | 1 |
| `Dockerfile` | دوكر فايل | 1 |
| `Duplicates` | دوبليكيتس | 1 |
| `Durability` | ديورابيليتي | 1 |
| `Eclipse` | إكليبس | 1 |
| `Elasticity` | إلاستيسيتي | 1 |
| `Embeddings` | إمبيدنجز | 1 |
| `Encoding` | إنكودنج | 1 |
| `Encryption` | إنكريبشن | 1 |
| `End` | إند | 1 |
| `Endpoint` | إندبوينت | 1 |
| `Entropy` | إنتروبي | 1 |
| `Environment` | إنفايرونمنت | 1 |
| `Eradication` | إيراديكيشن | 1 |
| `Error` | إيرور | 1 |
| `Exception` | إكسبشن | 1 |
| `Exploitation` | إكسبلويتيشن | 1 |
| `Exploration` | إكسبلوريشن | 1 |
| `Factorial` | فاكتوريال | 1 |
| `Fedora` | فيدورا | 1 |
| `Fields` | فيلدز | 1 |
| `Filters` | فلترز | 1 |
| `Finiteness` | فاينتنس | 1 |
| `Firewall` | فايروول | 1 |
| `Firmware` | فيرموير | 1 |
| `Flask` | فلاسك | 1 |
| `Flowchart` | فلو تشارت | 1 |
| `Forget` | فورجت | 1 |
| `Framework` | فريمورك | 1 |
| `Frequency` | فريكونسي | 1 |
| `Gaussian` | جاوسيان | 1 |
| `Getters` | جيترز | 1 |
| `GitHub` | جيت هب | 1 |
| `GloVe` | جلوف | 1 |
| `Gmail` | جي ميل | 1 |
| `GPUs` | جي بي يوز | 1 |
| `GraphQL` | جراف كيو إل | 1 |
| `Graphs` | جرافس | 1 |
| `Green` | جرين | 1 |
| `Guidelines` | جايدلاينز | 1 |
| `Hadoop` | هادوب | 1 |
| `Handshake` | هاند شيك | 1 |
| `Headers` | هيدرز | 1 |
| `Hexadecimal` | هيكساديسيمال | 1 |
| `Hierarchical` | هيراركيكال | 1 |
| `Homoscedasticity` | هوموسكيداستيسيتي | 1 |
| `Honeypot` | هاني بوت | 1 |
| `Horizontal` | هورايزونتال | 1 |
| `Hotfixes` | هوت فيكسز | 1 |
| `HttpOnly` | إتش تي تي بي أونلي | 1 |
| `Hybrid` | هايبرد | 1 |
| `Hypervisor` | هايبرفايزر | 1 |
| `Idempotent` | آيديمبوتنت | 1 |
| `Identification` | آيدنتيفيكيشن | 1 |
| `Identity` | آيدنتيتي | 1 |
| `IIoT` | آي آي أو تي | 1 |
| `Imputation` | إمبيوتيشن | 1 |
| `Index` | إندكس | 1 |
| `Indicator` | إنديكيتور | 1 |
| `Inertia` | إنيرشيا | 1 |
| `Inline` | إنلاين | 1 |
| `Input` | إنبوت | 1 |
| `Interpretability` | إنتربريتبيليتي | 1 |
| `IoT` | آي أو تي | 1 |
| `Isolation` | آيزوليشن | 1 |
| `Iterations` | إتيريشنز | 1 |
| `Jenkins` | جينكنز | 1 |
| `Kanban` | كانبان | 1 |
| `Kernel` | كيرنل | 1 |
| `Keylogger` | كي لوجر | 1 |
| `Kubeflow` | كيوب فلو | 1 |
| `Lagging` | لاجنج | 1 |
| `Lasso` | لاسو | 1 |
| `Latency` | ليتنسي | 1 |
| `Leading` | ليدنج | 1 |
| `Leaves` | ليفز | 1 |
| `Library` | لايبراري | 1 |
| `Lodash` | لوداش | 1 |
| `Logger` | لوجر | 1 |
| `Logging` | لوجنج | 1 |
| `Macro` | ماكرو | 1 |
| `Malware` | مالوير | 1 |
| `Measures` | ميجرز | 1 |
| `Metric` | ميتريك | 1 |
| `Micro` | مايكرو | 1 |
| `Mitigate` | ميتيجيت | 1 |
| `MLflow` | إم إل فلو | 1 |
| `MLOps` | إم إل أوبس | 1 |
| `Mocks` | موكس | 1 |
| `Monetary` | مونيتري | 1 |
| `Multilevel` | مالتي ليفل | 1 |
| `Multinomial` | مالتينوميال | 1 |
| `MySQL` | ماي إس كيو إل | 1 |
| `Naive` | نايف | 1 |
| `Network` | نتورك | 1 |
| `Neuron` | نيورون | 1 |
| `Neurons` | نيورونز | 1 |
| `Nodes` | نودز | 1 |
| `Objects` | أوبجكتس | 1 |
| `Offline` | أوفلاين | 1 |
| `OpenVPN` | أوبن في بي إن | 1 |
| `Oracle` | أوراكل | 1 |
| `Output` | أوتبوت | 1 |
| `Oversampling` | أوفرسامبلنج | 1 |
| `Overselling` | أوفر سيلنج | 1 |
| `Ownership` | أونرشيب | 1 |
| `Parametric` | بارامتريك | 1 |
| `Passive` | باسيف | 1 |
| `Pearson` | بيرسون | 1 |
| `Pepper` | بيبر | 1 |
| `Physical` | فيزيكال | 1 |
| `Pipeline` | بايبلاين | 1 |
| `Pipelines` | بايبلاينز | 1 |
| `Plaintext` | بلين تكست | 1 |
| `Pod` | بود | 1 |
| `Pointers` | بوينترز | 1 |
| `Poisoning` | بويزنج | 1 |
| `Policy` | بوليسي | 1 |
| `Pooling` | بولنج | 1 |
| `Port` | بورت | 1 |
| `Ports` | بورتس | 1 |
| `Preparation` | بريپيريشن | 1 |
| `Pretexting` | بريتكسنج | 1 |
| `Procedures` | بروسيدجرز | 1 |
| `Producer` | بروديوسر | 1 |
| `Profilers` | بروفايلرز | 1 |
| `Protected` | بروتكتد | 1 |
| `Prototyping` | بروتوتايبنج | 1 |
| `Pruning` | بروننج | 1 |
| `Push` | بوش | 1 |
| `PyCharm` | باي تشارم | 1 |
| `PyTorch` | باي تورش | 1 |
| `RabbitMQ` | رابيت إم كيو | 1 |
| `Randomization` | راندومايزيشن | 1 |
| `Ranks` | رانكس | 1 |
| `Ransomware` | رانسوم وير | 1 |
| `React` | رياكت | 1 |
| `Rebase` | ريبيس | 1 |
| `Recency` | ريسينسي | 1 |
| `Recovery` | ريكفري | 1 |
| `Recursion` | ريكيرجن | 1 |
| `Recursive` | ريكيرسف | 1 |
| `Red` | ريد | 1 |
| `Redundancy` | ريدندنسي | 1 |
| `Refactor` | ريفاكتور | 1 |
| `Reference` | ريفيرنس | 1 |
| `Registry` | ريجستري | 1 |
| `Regularization` | ريجولارايزيشن | 1 |
| `Rehashing` | ريهاشينج | 1 |
| `Releases` | ريليزز | 1 |
| `Remediation` | ريميديشن | 1 |
| `Rendering` | ريندرنج | 1 |
| `Repository` | ريبوزيتوري | 1 |
| `Reproducibility` | ريبروډيوسيبيليتي | 1 |
| `Request` | ريكويست | 1 |
| `Resolver` | ريزولفر | 1 |
| `Resources` | ريسورسز | 1 |
| `Response` | ريسبونس | 1 |
| `Retention` | ريتنشن | 1 |
| `Retrospective` | ريتروسبيكتف | 1 |
| `Reward` | ريوارد | 1 |
| `Risk` | ريسك | 1 |
| `Rivest` | ريفست | 1 |
| `Rounds` | راوندز | 1 |
| `Routers` | راوترز | 1 |
| `Routing` | راوتنج | 1 |
| `Ruby` | روبي | 1 |
| `Runtime` | ران تايم | 1 |
| `Safe` | سيف | 1 |
| `SameSite` | سيم سايت | 1 |
| `Sampling` | سامبلنج | 1 |
| `Scalability` | سكيلابيليتي | 1 |
| `Scanners` | سكانرز | 1 |
| `Scripts` | سكريبتس | 1 |
| `Series` | سيريز | 1 |
| `Server` | سيرفر | 1 |
| `ServerHello` | سيرفر هلو | 1 |
| `Session` | سيشن | 1 |
| `Setter` | سيتر | 1 |
| `Setters` | سيترز | 1 |
| `Shamir` | شامير | 1 |
| `Shell` | شيل | 1 |
| `Simpson` | سيمبسون | 1 |
| `Singleton` | سينجلتون | 1 |
| `Skewed` | سكيوود | 1 |
| `Skewness` | سكيو نس | 1 |
| `Smishing` | سميشينج | 1 |
| `Spam` | سبام | 1 |
| `Sparse` | سبارس | 1 |
| `Spearman` | سبيرمان | 1 |
| `Splunk` | سبلانك | 1 |
| `Spring` | سبرينج | 1 |
| `Sprint` | سبرنت | 1 |
| `Sprints` | سبرنتس | 1 |
| `Staging` | ستيجنج | 1 |
| `Standards` | ستاندردز | 1 |
| `Start` | ستارت | 1 |
| `State` | ستيت | 1 |
| `Stateless` | ستيتلس | 1 |
| `Statelessness` | ستيتلسنس | 1 |
| `Static` | ستاتك | 1 |
| `Stubs` | ستابس | 1 |
| `Syntax` | سينتاكس | 1 |
| `Tags` | تاجز | 1 |
| `Tailgating` | تيل جيتنج | 1 |
| `Talend` | تالند | 1 |
| `Tanh` | تانش | 1 |
| `TensorFlow` | تنسرفلو | 1 |
| `Terminal` | تيرمنال | 1 |
| `Test` | تيست | 1 |
| `Thread` | ثريد | 1 |
| `Threat` | ثريت | 1 |
| `Threshold` | ثريشولد | 1 |
| `Tokenization` | توكينايزيشن | 1 |
| `Tokens` | توكنز | 1 |
| `Top` | توب | 1 |
| `Tradeoff` | تريد أوف | 1 |
| `Transaction` | ترانزاكشن | 1 |
| `Transactions` | ترانزاكشنز | 1 |
| `Transfer` | ترانسفر | 1 |
| `Transport` | ترانسبورت | 1 |
| `Ubuntu` | أوبونتو | 1 |
| `Underfitting` | أندر فيتنج | 1 |
| `Undersampling` | أندرسامبلنج | 1 |
| `Undo` | أندو | 1 |
| `URLs` | يو آر إلز | 1 |
| `Value` | فاليو | 1 |
| `Variety` | فرايتي | 1 |
| `Velocity` | فيلوسيتي | 1 |
| `Veracity` | فيراسيتي | 1 |
| `Vertical` | فيرتيكال | 1 |
| `Virus` | فايرس | 1 |
| `Vishing` | فيشينج | 1 |
| `Volatile` | فولاتايل | 1 |
| `Volume` | فوليوم | 1 |
| `Vue` | فيو | 1 |
| `Vulnerability` | فالنرابيليتي | 1 |
| `WannaCry` | وانا كراي | 1 |
| `Wazuh` | وازوه | 1 |
| `WebSockets` | ويب سوكيتس | 1 |
| `Weight` | ويت | 1 |
| `Weighted` | ويتد | 1 |
| `Weighting` | ويتنج | 1 |
| `Whaling` | ويلنج | 1 |
| `Whiskers` | ويسكرز | 1 |
| `WireGuard` | واير جارد | 1 |
| `WordPiece` | وورد بيس | 1 |
| `Worm` | وورم | 1 |
| `XGBoost` | إكس جي بوست | 1 |
| `Zsh` | زي شيل | 1 |

## رموز حساسة للسياق — لا تستخدم عليها Replace All

| الرمز | النطق المقترح | ملاحظة |
|---|---|---|
| `A` | إيه | حرف/اسم نسخة في A/B Testing؛ لا تستبدله إلا داخل السياق المقصود. |
| `B` | بي | حرف/اسم نسخة في A/B Testing؛ لا تستبدله إلا داخل السياق المقصود. |
| `C` | سي | قد يعني لغة C أو متغيرًا؛ راجع السياق. |
| `R` | آر | قد يعني لغة R أو رمزًا؛ راجع السياق. |
| `K` | كي | قد يعني عدد المجموعات/الجيران/الأجزاء؛ راجع السياق. |
| `k` | كي | متغير رياضي؛ راجع السياق. |
| `n` | إن | متغير للحجم؛ راجع السياق. |
| `n-1` | إن ناقص واحد | صيغة رياضية؛ استبدلها فقط عند تمثيل النطق. |
| `w` | دبليو | وزن في معادلة؛ راجع السياق. |
| `b` | بي | انحياز في معادلة؛ راجع السياق. |
| `y` | واي | متغير ناتج في معادلة؛ راجع السياق. |
| `wx` | دبليو إكس | جزء من معادلة؛ راجع السياق. |
| `Q1` | كيو وان | الربيع الأول. |
| `Q3` | كيو ثري | الربيع الثالث. |

## أمثلة سريعة

```text
Primary Key  → برايمري كي
Foreign Key  → فورين كي
Power BI     → باور بي آي
SQL          → إس كيو إل
VLOOKUP      → في لوك أب
Node.js      → نود جي إس
Backend      → باك إند
Frontend     → فرونت إند
DELETE       → ديليت
TRUNCATE     → ترانكيت
DROP         → دروب
```

## قاعدة أخيرة

لو المصطلح موجود في الإجابة داخل مثال برمجي أو معادلة، اسأل نفسك: **هل المرشح كان سينطق الاسم فعلًا أم يتهجّاه حرفًا حرفًا؟** ثم استخدم نفس القرار في كل ظهور مماثل.
