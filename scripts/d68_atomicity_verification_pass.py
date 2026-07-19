"""Independent D68 verification-pass evidence in reverse frozen order.

This module does not import the first-pass specification. Its segmentation,
tests, source correspondences, classifications, and rationales were authored
from the extracted source and claim evidence during the reverse-order review.
"""

from __future__ import annotations

from d68_atomicity_adjudication import INTEGRATED, NON_ATOMIC


def supported(text: str, excerpt: str, explanation: str) -> dict[str, object]:
    return {
        "proposition_text": text,
        "exact_source_excerpt": excerpt,
        "directly_source_supported": True,
        "semantic_correspondence": explanation,
    }


def reviewed(
    key: str,
    propositions: list[dict[str, object]],
    classification: str,
    rationale: str,
    p1_without_p2: bool,
    p2_without_p1: bool,
    test_reason: str,
    *,
    all_segments: str | None = None,
    dependency_reason: str | None = None,
) -> dict[str, object]:
    return {
        "candidate_key": key,
        "verification_propositions": propositions,
        "verification_pass_classification": classification,
        "verification_pass_rationale": rationale,
        "verification_independent_judgability_test": {
            "can_proposition_1_be_true_while_proposition_2_is_false": p1_without_p2,
            "can_proposition_2_be_true_while_proposition_1_is_false": p2_without_p1,
            "evidence_based_explanation": test_reason,
            "multi_proposition_analysis": all_segments,
            "semantic_dependency": dependency_reason,
        },
    }


VERIFICATION_PASS_RECORDS = [
    reviewed("GN-048:4", [
        supported("الرخصة الاحتكارية تقيد إتاحة الشفرة المصدرية.", "وفيه كمان رخص احتكارية، بتقيد الوصول للكود المصدري وتمنع التعديل وإعادة التوزيع.", "بتقيد الوصول للكود المصدري is the source wording for restricted source access."),
        supported("الرخصة الاحتكارية تحظر تعديل البرنامج.", "وفيه كمان رخص احتكارية، بتقيد الوصول للكود المصدري وتمنع التعديل وإعادة التوزيع.", "تمنع التعديل supplies the modification prohibition."),
        supported("الرخصة الاحتكارية تحظر إعادة توزيع البرنامج.", "وفيه كمان رخص احتكارية، بتقيد الوصول للكود المصدري وتمنع التعديل وإعادة التوزيع.", "إعادة التوزيع is governed by تمنع in the same source clause."),
    ], NON_ATOMIC, "Reverse review finds three legally distinct restrictions; conjunction does not make them one restriction.", True, True, "A license may restrict source access without forbidding modification, or forbid modification without withholding source access.", all_segments="Source access, modification, and redistribution are separate restriction dimensions; each proposition names the governing license and preserves prohibition."),
    reviewed("GN-037:2", [
        supported("أجهزة إنترنت الأشياء تجمع بيانات من البيئة المحيطة.", "الأجهزة دي بتجمع بيانات من محيطها وبتبعتها للتحليل واتخاذ قرارات آلية أو يدوية بناءً عليها.", "بتجمع بيانات من محيطها directly supports collection."),
        supported("أجهزة إنترنت الأشياء ترسل البيانات لتحليلها واتخاذ قرارات آلية أو يدوية بناءً عليها.", "الأجهزة دي بتجمع بيانات من محيطها وبتبعتها للتحليل واتخاذ قرارات آلية أو يدوية بناءً عليها.", "بتبعتها للتحليل واتخاذ قرارات supports transmission and downstream purpose."),
    ], NON_ATOMIC, "Collection and downstream transmission/use remain meaningful and scoreable after naming the devices and data in both propositions.", True, True, "Devices can collect without transmitting, and devices can transmit data supplied to them without themselves collecting it from their surroundings."),
    reviewed("GN-015:3", [
        supported("عميل الويب يرسل طلب HTTP إلى Endpoint محددة.", "في الويب، العميل بيبعت طلب HTTP لنقطة نهاية Endpoint محددة، وبيستقبل استجابة غالبًا بصيغة JSON.", "العميل بيبعت طلب HTTP لنقطة نهاية supports the request action."),
        supported("عميل الويب يستقبل استجابة غالبًا بصيغة JSON.", "في الويب، العميل بيبعت طلب HTTP لنقطة نهاية Endpoint محددة، وبيستقبل استجابة غالبًا بصيغة JSON.", "بيستقبل استجابة غالبًا بصيغة JSON supports the qualified response statement."),
    ], NON_ATOMIC, "The reverse pass initially treats outbound request and inbound response format as two observable assertions.", True, True, "A request can be sent without a response being received; a received response assertion can be evaluated separately from the endpoint wording."),
    reviewed("SE-032:8", [
        supported("Graph يمثل كيانات وعلاقاتها بعقد وحواف.", "الرسوم البيانية Graphs بتمثل الكيانات وعلاقاتها بعقد وحواف، واختيار الهيكل المناسب بيحدد كفاءة الخوارزمية بأكملها.", "The first source clause defines graph representation."),
        supported("اختيار بنية البيانات الملائمة يحدد كفاءة الخوارزمية كلها.", "الرسوم البيانية Graphs بتمثل الكيانات وعلاقاتها بعقد وحواف، واختيار الهيكل المناسب بيحدد كفاءة الخوارزمية بأكملها.", "The second source clause asserts a structure-choice consequence."),
    ], NON_ATOMIC, "One assertion defines graphs; the other generalizes about algorithm efficiency, so they require separate judgments.", True, True, "Either assertion can fail without logically deciding the other."),
    reviewed("SE-032:3", [
        supported("Linked List توصل عقدها بواسطة مؤشرات.", "القائمة المتصلة Linked List بتربط عقد بمؤشرات، وبتتيح إدراج وحذف مرنين من غير إزاحة العناصر.", "بتربط عقد بمؤشرات supports the structure."),
        supported("Linked List تسمح بإدراج وحذف مرنين من غير إزاحة العناصر.", "القائمة المتصلة Linked List بتربط عقد بمؤشرات، وبتتيح إدراج وحذف مرنين من غير إزاحة العناصر.", "The source states both operations and the من غير إزاحة restriction."),
    ], NON_ATOMIC, "Pointer organization and update behavior are independent properties of the same structure.", True, True, "The linkage description can be true while the operation guarantee is false, and the operation statement can be tested without accepting the exact linkage wording."),
    reviewed("SE-032:2", [
        supported("Array يحتفظ بعناصره في ذاكرة متجاورة.", "المصفوفة Array بتخزن العناصر في مواقع متجاورة، وبتتيح وصول مباشر بالفهرس بزمن ثابت.", "The source states contiguous locations."),
        supported("Array يوفر وصولًا مباشرًا ثابت الزمن بواسطة الفهرس.", "المصفوفة Array بتخزن العناصر في مواقع متجاورة، وبتتيح وصول مباشر بالفهرس بزمن ثابت.", "The source separately states indexed access and time."),
    ], NON_ATOMIC, "Physical layout and indexed-access complexity are different scoreable properties.", True, True, "A layout claim does not settle time complexity, and a complexity claim does not settle physical contiguity."),
    reviewed("SE-029:5", [
        supported("Code Review يوزع المعرفة بين أفراد الفريق.", "المراجعة بتنشر المعرفة بين أعضاء الفريق، وبتقلل احتكار فرد واحد لفهم أجزاء من النظام.", "تنشر المعرفة supports distribution."),
        supported("Code Review يخفض احتكار شخص واحد لفهم أجزاء النظام.", "المراجعة بتنشر المعرفة بين أعضاء الفريق، وبتقلل احتكار فرد واحد لفهم أجزاء من النظام.", "تقلل احتكار فرد واحد supplies the concentration effect."),
    ], NON_ATOMIC, "Knowledge diffusion and reduced single-person ownership are related but not identical effects.", True, True, "Some knowledge may spread without removing concentration, and concentration may fall through means other than broad diffusion."),
    reviewed("SE-022:4", [
        supported("في Desired State يعلن المستخدم المطلوب في YAML ويواصل النظام مطابقته.", "النظام بيشتغل بنموذج الحالة المرغوبة Desired State، المستخدم بيوصف المطلوب في ملفات YAML، والنظام بيشتغل باستمرار على مطابقته.", "The source binds the declared YAML state to continuous reconciliation."),
    ], INTEGRATED, "The declaration supplies the object of the system's ongoing matching, so the clauses define one feedback mechanism.", False, False, "After keeping the reference of مطابقته, there is only one declaration-and-reconciliation proposition.", dependency_reason="Isolating matching from the state it matches would alter the mechanism rather than atomize it."),
    reviewed("DA-041:7", [
        supported("Calculated Columns تحسب لكل صف وتخزن ناتجها.", "الأعمدة المحسوبة بتتحسب صف بصف وبتتخزن نتائجها، بينما المقاييس بتتحسب ديناميكيًا وقت الاستعلام حسب سياق التقرير.", "The source explicitly gives row evaluation and storage."),
        supported("Measures تحسب وقت الاستعلام ديناميكيًا وفق سياق التقرير.", "الأعمدة المحسوبة بتتحسب صف بصف وبتتخزن نتائجها، بينما المقاييس بتتحسب ديناميكيًا وقت الاستعلام حسب سياق التقرير.", "The contrasting source clause gives dynamic query-time evaluation."),
    ], NON_ATOMIC, "Each side of the calculated-column/measure comparison asserts a complete behavior.", True, True, "The calculated-column description can be accepted while the measure description is rejected, and vice versa."),
    reviewed("DA-037:5", [
        supported("subset يختار أعمدة مقارنة التكرار.", "المعامل subset بيحدد الأعمدة المعتمدة في المقارنة، والمعامل keep بيحدد أي نسخة تتحفظ.", "The first source clause identifies subset semantics."),
        supported("keep يختار نسخة السجل التي تبقى.", "المعامل subset بيحدد الأعمدة المعتمدة في المقارنة، والمعامل keep بيحدد أي نسخة تتحفظ.", "The second source clause identifies keep semantics."),
    ], NON_ATOMIC, "Two named parameters perform separate jobs and can be graded separately.", True, True, "Correct subset semantics do not imply correct keep semantics, and conversely."),
    reviewed("GN-009:4", [
        supported("Network layer تنفذ العنونة المنطقية.", "طبقة الشبكة Network مسؤولة عن العنونة المنطقية والتوجيه Routing بين الشبكات المختلفة، وبتشتغل بعناوين IP.", "العنونة المنطقية is explicitly assigned to the layer."),
        supported("Network layer توجه بين الشبكات.", "طبقة الشبكة Network مسؤولة عن العنونة المنطقية والتوجيه Routing بين الشبكات المختلفة، وبتشتغل بعناوين IP.", "التوجيه بين الشبكات is explicitly assigned."),
        supported("Network layer تستخدم عناوين IP.", "طبقة الشبكة Network مسؤولة عن العنونة المنطقية والتوجيه Routing بين الشبكات المختلفة، وبتشتغل بعناوين IP.", "بتشتغل بعناوين IP supplies the third property."),
    ], NON_ATOMIC, "The common subject does not merge addressing, routing, and IP use into one truth condition.", True, True, "Addressing can be described correctly while routing is wrong, and routing can be correct while addressing wording is wrong.", all_segments="Each of P1 addressing, P2 routing, and P3 IP use names the layer and is independently checkable."),
    reviewed("SE-047:3", [
        supported("Cache-Aside يبدأ بطلب التطبيق من cache، وعند الغياب يجلب من المصدر ويخزن.", "استراتيجية Cache-Aside بيطلب فيها التطبيق من الذاكرة المؤقتة الأول، وبيجلب من المصدر ويخزن عند الغياب Cache Miss.", "The source makes fetch-and-store conditional on cache absence after the initial lookup."),
    ], INTEGRATED, "The cache miss condition scopes the later actions inside one named strategy.", False, False, "There is no independent second proposition once عند الغياب governs fetch and store.", dependency_reason="Splitting would lose the ordered miss condition that defines when source retrieval occurs."),
    reviewed("SE-030:5", [
        supported("تراكم Technical Debt يبطئ تقدم الفريق بمرور الوقت.", "لو سيبت الدين يتراكم، بيبطئ الفريق تدريجيًا، وبيزيد الأعطال، وممكن يوصل لشل القدرة على إضافة ميزات جديدة.", "بيبطئ الفريق تدريجيًا is the source effect."),
        supported("تراكم Technical Debt يرفع عدد الأعطال.", "لو سيبت الدين يتراكم، بيبطئ الفريق تدريجيًا، وبيزيد الأعطال، وممكن يوصل لشل القدرة على إضافة ميزات جديدة.", "بيزيد الأعطال states a second effect."),
        supported("تراكم Technical Debt يمكن أن يشل إضافة ميزات جديدة.", "لو سيبت الدين يتراكم، بيبطئ الفريق تدريجيًا، وبيزيد الأعطال، وممكن يوصل لشل القدرة على إضافة ميزات جديدة.", "ممكن يوصل preserves possibility rather than certainty."),
    ], NON_ATOMIC, "The reverse review finds three severities of consequence, each independently observable.", True, True, "A team may slow without more failures, or see failures without the stated gradual slowdown.", all_segments="P1 speed, P2 failures, and P3 possible feature paralysis are separate outcomes; P3 alone carries the hedge."),
    reviewed("CS-032:2", [
        supported("SIEM يطبع صيغ السجلات إلى صيغة موحدة.", "النظام بيوحد صيغ السجلات Normalization، وبيربط الأحداث المتفرقة Correlation، عشان يكشف أنماط هجوم مش ظاهرة في مصدر واحد.", "The source names Normalization as a system action."),
        supported("SIEM يجري Correlation للأحداث المتفرقة.", "النظام بيوحد صيغ السجلات Normalization، وبيربط الأحداث المتفرقة Correlation، عشان يكشف أنماط هجوم مش ظاهرة في مصدر واحد.", "The source names correlation as another action."),
        supported("تطبيع السجلات وربط الأحداث يتيحان لـSIEM كشف نمط هجوم لا يراه مصدر منفرد.", "النظام بيوحد صيغ السجلات Normalization، وبيربط الأحداث المتفرقة Correlation، عشان يكشف أنماط هجوم مش ظاهرة في مصدر واحد.", "The diagnostic proposition restores the governing operations and system to the source's purpose clause."),
    ], NON_ATOMIC, "Normalization, correlation, and the claimed cross-source result have distinct truth conditions.", True, True, "A SIEM may normalize without correlating, or correlate without normalization.", all_segments="P3 is not a bare لكشف fragment: it names SIEM and both governing operations; its outcome remains separately scoreable from whether P1 or P2 was accurately described."),
    reviewed("CS-001:4", [
        supported("Integrity تمنع تغيير البيانات أو العبث غير المصرح وتدعمها أمثلة منها Hashing.", "السلامة Integrity معناها ضمان إن البيانات متتعدلش أو يتم العبث بيها بشكل غير مصرح به، وبتتدعم بتقنيات زي الـ Hashing والتوقيعات الرقمية Digital Signatures.", "The source combines the negated definition with Hashing as one supporting example."),
    ], INTEGRATED, "Hashing illustrates how the same Integrity property is supported; it is not a separate objective.", False, False, "Only one definition-with-example proposition survives the example rule.", dependency_reason="Removing the security property from its example would create an contextless example claim."),
    reviewed("DS-038:1", [
        supported("Transformer ظهر سنة 2017.", "الـ Transformer معمارية عصبية اتقدمت سنة 2017، وبتعتمد كليًا على آلية الانتباه Attention من غير تكرار أو التفاف.", "The introduction year appears literally in the source."),
        supported("Transformer يستخدم Attention وحده من غير recurrence أو convolution.", "الـ Transformer معمارية عصبية اتقدمت سنة 2017، وبتعتمد كليًا على آلية الانتباه Attention من غير تكرار أو التفاف.", "The source states attention-only architecture with preserved exclusions."),
    ], NON_ATOMIC, "A historical assertion and an architecture assertion require different evidence.", True, True, "One can accept the architecture while dispute the year, or accept the year while dispute the architecture."),
    reviewed("DA-017:6", [
        supported("SELF JOIN يربط الجدول بذاته لعلاقات داخلية مثل الموظف والمدير.", "SELF JOIN هو ربط الجدول بنفسه، وبيستخدم للعلاقات جوه الجدول الواحد زي علاقة الموظف بمديره.", "The same source clause gives definition, use scope, and example."),
    ], INTEGRATED, "The employee-manager relation is a clarifying example of the within-table join definition.", False, False, "There is no independently asserted effect beyond the definition and its example.", dependency_reason="Splitting the example would over-segment the single SELF JOIN explanation."),
    reviewed("GN-038:3", [
        supported("تغيير كتلة يبدل Hashها، فيقطع روابط ما بعدها ويظهر العبث.", "أي تعديل في كتلة بيغير بصمتها، فبيكسر ارتباط كل الكتل اللاحقة، وبيكشف العبث فورًا.", "The source links modification, changed fingerprint, broken chain, and detection causally."),
    ], INTEGRATED, "Every later clause is a consequence scoped by the initial block modification.", False, False, "Treating the consequences as independent would discard their triggering condition.", dependency_reason="The causal chain is the asserted mechanism; its stages are not free-standing claims here."),
    reviewed("GN-002:3", [
        supported("Memory Management تخصص الذاكرة وتحررها وقد تستخدم Virtual Memory.", "بيدير نظام التشغيل الذاكرة Memory Management بتخصيصها للعمليات وتحريرها، وبيستخدم تقنيات زي الذاكرة الافتراضية Virtual Memory.", "The source presents Virtual Memory with زي as an example inside the same function."),
    ], INTEGRATED, "The virtual-memory phrase is an example of techniques within the stated allocation/release function.", False, False, "Applying the example rule leaves one memory-management proposition.", dependency_reason="Separating the example would fragment a single function-and-technique explanation."),
    reviewed("GN-002:1", [
        supported("Operating System يتولى إدارة موارد الجهاز.", "نظام التشغيل Operating System هو البرنامج الوسيط اللي بيدير موارد الحاسوب المادية، وبيتيح للتطبيقات والمستخدمين التعامل معاها.", "The first predicate explicitly names resource management."),
        supported("Operating System يوفر للتطبيقات والمستخدمين وسيلة للتعامل مع موارد الجهاز.", "نظام التشغيل Operating System هو البرنامج الوسيط اللي بيدير موارد الحاسوب المادية، وبيتيح للتطبيقات والمستخدمين التعامل معاها.", "The second predicate explicitly names access to those resources."),
    ], NON_ATOMIC, "The shared resource referent does not prevent separate scoring of management and exposure roles.", True, True, "A system component may manage resources without exposing a user/application interface, while an intermediary may expose resources whose management is elsewhere."),
    reviewed("SE-035:1", [
        supported("Hash Table هو بنية أزواج key/value تتيح وصولًا سريعًا بواسطة Hash Function.", "الجدول التجزيئي Hash Table هيكل بيخزن أزواج مفتاح وقيمة، وبيتيح وصول سريع عن طريق دالة تجزئة Hash Function.", "The source describes structure and hash access in one sentence defining the named table."),
    ], INTEGRATED, "The reverse pass reads hash-based access as the intrinsic mechanism completing the Hash Table definition.", False, False, "On this reading there is one structure-and-mechanism proposition rather than a separable performance effect.", dependency_reason="Splitting would detach the defining access mechanism from the named data structure."),
    reviewed("CS-049:4", [
        supported("Vulnerability Scanning ينتج احتمالات ثغرات قد تشمل false positives.", "الفحص بينتج قائمة ثغرات محتملة، ممكن تحوي إنذارات كاذبة، بينما الاختبار بيأكد الثغرات الحقيقية ويقيس أثرها العملي.", "The source contains both potentiality and possible false alerts."),
        supported("Penetration Testing يتحقق من الثغرات الحقيقية.", "الفحص بينتج قائمة ثغرات محتملة، ممكن تحوي إنذارات كاذبة، بينما الاختبار بيأكد الثغرات الحقيقية ويقيس أثرها العملي.", "The test confirmation is directly stated."),
        supported("Penetration Testing يقدر أثر الثغرات في الواقع العملي.", "الفحص بينتج قائمة ثغرات محتملة، ممكن تحوي إنذارات كاذبة، بينما الاختبار بيأكد الثغرات الحقيقية ويقيس أثرها العملي.", "The practical impact measurement is directly stated."),
    ], NON_ATOMIC, "The two tools and the test's two functions create three separate scoring targets.", True, True, "Scanner uncertainty is independent of whether testing confirms vulnerabilities.", all_segments="P1 scanning, P2 validation, and P3 impact measurement are independent; uncertainty remains attached to P1."),
    reviewed("CS-010:1", [
        supported("SSL/TLS يؤمن سرية الاتصال وسلامته بالتشفير.", "SSL/TLS بروتوكول أمني بيشفر الاتصال بين العميل والخادم، وبيضمن سريته وسلامته، وTLS هو الخليفة الحديث لبروتوكول SSL المهجور.", "The security behavior is stated in the first part."),
        supported("TLS خلف SSL وأحدث منه.", "SSL/TLS بروتوكول أمني بيشفر الاتصال بين العميل والخادم، وبيضمن سريته وسلامته، وTLS هو الخليفة الحديث لبروتوكول SSL المهجور.", "The successor relation is stated in the final part."),
    ], NON_ATOMIC, "Protocol function and protocol lineage do not share a truth condition.", True, True, "Either can be accurate while the other is inaccurate."),
    reviewed("DA-049:5", [
        supported("Snowflake Schema يقلل مساحة التخزين.", "مخطط ندفة الثلج بيوفر مساحة ويقلل التكرار، مقابل استعلامات أعقد بربط جداول أكتر.", "بيوفر مساحة supports the storage assertion."),
        supported("Snowflake Schema يخفض تكرار البيانات.", "مخطط ندفة الثلج بيوفر مساحة ويقلل التكرار، مقابل استعلامات أعقد بربط جداول أكتر.", "يقلل التكرار supports redundancy reduction."),
        supported("Snowflake Schema يعقد الاستعلام بسبب زيادة joins.", "مخطط ندفة الثلج بيوفر مساحة ويقلل التكرار، مقابل استعلامات أعقد بربط جداول أكتر.", "استعلامات أعقد بربط جداول أكتر states the cost."),
    ], NON_ATOMIC, "The trade-off contains two benefits and one cost that can differ independently.", True, True, "Space use and redundancy are not the same metric.", all_segments="P1 storage, P2 redundancy, and P3 query complexity each remain meaningful if the other two are rejected."),
    reviewed("DA-038:5", [
        supported("Data Dictionary يختصر وقت تأهيل عضو الفريق الجديد.", "وبيسرع إدماج الأعضاء الجدد ويقلل اعتمادهم على المعرفة الضمنية عند الأفراد.", "يسرع إدماج supplies the onboarding effect."),
        supported("Data Dictionary يقلل اعتماد الجدد على معرفة الأفراد غير الموثقة.", "وبيسرع إدماج الأعضاء الجدد ويقلل اعتمادهم على المعرفة الضمنية عند الأفراد.", "The second source predicate supplies the dependency effect."),
    ], NON_ATOMIC, "Time-to-onboard and dependence on tacit knowledge can be measured independently.", True, True, "One can improve while the other remains unchanged."),
    reviewed("DA-038:4", [
        supported("Data Dictionary يجعل أعضاء الفريق يفهمون البيانات بصورة موحدة.", "بيوحد فهم البيانات بين أعضاء الفريق ويقلل الالتباس حول معاني الأعمدة والاختصارات.", "The first source predicate states unified understanding."),
        supported("Data Dictionary يزيل بعض غموض الأعمدة والاختصارات.", "بيوحد فهم البيانات بين أعضاء الفريق ويقلل الالتباس حول معاني الأعمدة والاختصارات.", "The second predicate states reduced ambiguity."),
    ], NON_ATOMIC, "The effects are related but separately testable: consensus and ambiguity are not identical.", True, True, "A shared interpretation can still contain ambiguous fields, and explicit fields can reduce ambiguity without full team consensus."),
    reviewed("GN-046:1", [
        supported("Encoding يحول المحارف إلى أرقام قابلة للفهم والتخزين كبتات.", "الترميز Encoding نظام لتمثيل المحارف كأرقام يفهمها الحاسوب ويخزنها كبتات.", "The source gives one computer representation-and-storage mechanism."),
    ], INTEGRATED, "The bit form is how the same numeric character representation is stored, not a second effect.", False, False, "The review identifies one encoding mechanism with no independent proposition 2.", dependency_reason="Dividing number representation from its bit storage would fragment the source's mechanism definition."),
    reviewed("GN-028:2", [
        supported("Shell يفسر الأوامر وينفذها؛ Bash مثال عليه.", "الـ Shell هو البرنامج اللي بيفسر الأوامر المكتوبة وينفذها، ومن أمثلته Bash وZsh.", "The source explicitly marks Bash as an example of the defined program."),
    ], INTEGRATED, "The example does not create another independently judgeable behavior under the rubric.", False, False, "Only the Shell definition remains as a proposition; Bash is evidence by example.", dependency_reason="A standalone Bash-example claim would be needless fragmentation."),
    reviewed("GN-006:5", [
        supported("IPv6 عرضه 128 bit.", "عنوان IPv6 بيتكون من 128 bit، وبيتكتب بصيغة سداسية عشرية Hexadecimal مفصولة بنقطتين رأسيتين، وبيوفر فضاء عناوين ضخم بيحل مشكلة النفاد.", "The source gives 128 bit."),
        supported("IPv6 يكتب Hexadecimal مع فواصل colon.", "عنوان IPv6 بيتكون من 128 bit، وبيتكتب بصيغة سداسية عشرية Hexadecimal مفصولة بنقطتين رأسيتين، وبيوفر فضاء عناوين ضخم بيحل مشكلة النفاد.", "The source gives hexadecimal and colon separators."),
        supported("IPv6 يعالج نفاد العناوين بفضاء كبير.", "عنوان IPv6 بيتكون من 128 bit، وبيتكتب بصيغة سداسية عشرية Hexadecimal مفصولة بنقطتين رأسيتين، وبيوفر فضاء عناوين ضخم بيحل مشكلة النفاد.", "The source states the large-space consequence."),
    ], NON_ATOMIC, "Three IPv6 attributes require three independent checks.", True, True, "Correct width does not imply correct notation, and correct notation does not imply correct width.", all_segments="P1 width, P2 notation, and P3 address-space effect each has an independent truth condition."),
    reviewed("SE-033:1", [
        supported("Array يستخدم مواضع ذاكرة متجاورة.", "المصفوفة Array بتخزن عناصرها في مواقع ذاكرة متجاورة، بينما عقد القائمة المتصلة Linked List بتتوزع في الذاكرة وبترتبط بمؤشرات.", "The array side is explicit."),
        supported("Linked List يوزع العقد ويربطها بمؤشرات.", "المصفوفة Array بتخزن عناصرها في مواقع ذاكرة متجاورة، بينما عقد القائمة المتصلة Linked List بتتوزع في الذاكرة وبترتبط بمؤشرات.", "The linked-list side is explicit."),
    ], NON_ATOMIC, "A comparison of two structures contains one proposition about each structure.", True, True, "The array layout may be correct while the list layout is wrong, or the reverse."),
    reviewed("SE-003:5", [
        supported("Multiple Inheritance تورث الصنف من أكثر من parent.", "الوراثة المتعددة Multiple Inheritance معناها الوراثة من أكتر من أب، وبتدعمها لغات زي C++ وPython، وممكن تسبب مشاكل زي الـ Diamond Problem.", "The source supplies the meaning."),
        supported("C++ من اللغات التي تدعم Multiple Inheritance.", "الوراثة المتعددة Multiple Inheritance معناها الوراثة من أكتر من أب، وبتدعمها لغات زي C++ وPython، وممكن تسبب مشاكل زي الـ Diamond Problem.", "The source names C++ as a supporting language."),
    ], NON_ATOMIC, "Definition and implementation-language support are different claims.", True, True, "Neither assertion logically fixes the truth of the other."),
    reviewed("CS-003:1", [
        supported("Firewall يراقب traffic ويطبق قواعد تسمح به أو تمنعه.", "الجدار الناري Firewall نظام أمني بيراقب حركة مرور الشبكة الداخلة والخارجة، وبيسمح بيها أو يمنعها حسب قواعد أمنية محددة مسبقًا.", "The source places observation and enforcement in one firewall description."),
    ], INTEGRATED, "The reverse reading treats inspection and rule enforcement as the intrinsic operation defining one firewall.", False, False, "There is one inspection-and-enforcement proposition on this reading.", dependency_reason="Separating allow/deny from the traffic it evaluates could fragment the firewall mechanism."),
    reviewed("DS-003:3", [
        supported("Classification وRegression كلاهما supervised ويعتمد تدريبهما على labeled data.", "المهمتين الاتنين من التعلم الموجه Supervised Learning، ومحتاجين بيانات موسومة عشان يتدربوا.", "The source jointly states the category and the labeled-data requirement."),
    ], INTEGRATED, "Labeled training is the qualifying definition attached to the shared supervised category.", False, False, "The reverse pass finds one category-with-requirement proposition.", dependency_reason="Independent scoring would split a necessary qualification from the classification it defines."),
    reviewed("SE-049:6", [
        supported("Horizontal Scaling لا يكاد يملك سقفًا.", "أما الـ Horizontal فتقريبًا مالوش سقف، وبيدّيك توافر أعلى، لكن بيحتاج تعقيد أكتر في التوزيع والتأكد إن البيانات متسقة بين كل السيرفرات.", "تقريبًا مالوش سقف supports the preserved approximation."),
        supported("Horizontal Scaling يرفع availability.", "أما الـ Horizontal فتقريبًا مالوش سقف، وبيدّيك توافر أعلى، لكن بيحتاج تعقيد أكتر في التوزيع والتأكد إن البيانات متسقة بين كل السيرفرات.", "بيدّيك توافر أعلى states the second property."),
    ], NON_ATOMIC, "Scale ceiling and service availability remain distinct properties despite sharing the same scaling method.", True, True, "Either property can hold without the other."),
]
