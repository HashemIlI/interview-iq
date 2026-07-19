"""Authored D68 first-pass atomicity evidence in frozen candidate order.

This module contains no verification-pass or final-resolution result.
Every independent-test answer and source correspondence is authored data.
"""

from __future__ import annotations

from d68_atomicity_adjudication import INTEGRATED, NON_ATOMIC


def p(text: str, excerpt: str, correspondence: str) -> dict[str, object]:
    return {
        "proposition_text": text,
        "exact_source_excerpt": excerpt,
        "directly_source_supported": True,
        "semantic_correspondence": correspondence,
    }


def r(
    key: str,
    propositions: list[dict[str, object]],
    classification: str,
    rationale: str,
    p1_true_p2_false: bool,
    p2_true_p1_false: bool,
    test_explanation: str,
    *,
    multi: str | None = None,
    dependency: str | None = None,
) -> dict[str, object]:
    return {
        "candidate_key": key,
        "proposed_propositions": propositions,
        "first_pass_classification": classification,
        "first_pass_rationale": rationale,
        "independent_judgability_test": {
            "can_proposition_1_be_true_while_proposition_2_is_false": p1_true_p2_false,
            "can_proposition_2_be_true_while_proposition_1_is_false": p2_true_p1_false,
            "evidence_based_explanation": test_explanation,
            "multi_proposition_analysis": multi,
            "semantic_dependency": dependency,
        },
    }


FIRST_PASS_RECORDS = [
    r("SE-049:6", [
        p("التوسع الأفقي شبه غير محدود.", "أما الـ Horizontal فتقريبًا مالوش سقف، وبيدّيك توافر أعلى، لكن بيحتاج تعقيد أكتر في التوزيع والتأكد إن البيانات متسقة بين كل السيرفرات.", "تقريبًا مالوش سقف supports the approximate horizontal-scaling limit."),
        p("التوسع الأفقي يوفر توافرًا أعلى.", "أما الـ Horizontal فتقريبًا مالوش سقف، وبيدّيك توافر أعلى، لكن بيحتاج تعقيد أكتر في التوزيع والتأكد إن البيانات متسقة بين كل السيرفرات.", "بيدّيك توافر أعلى directly supports the availability proposition."),
    ], NON_ATOMIC, "Scalability extent and availability are two properties whose truth values need not move together.", True, True, "Near-unbounded scale can be accepted while higher availability is rejected, and higher availability can be accepted without accepting near-unbounded scale."),
    r("DS-003:3", [
        p("التصنيف والانحدار مهمتان من التعلم الموجه وتتطلبان بيانات موسومة للتدريب.", "المهمتين الاتنين من التعلم الموجه Supervised Learning، ومحتاجين بيانات موسومة عشان يتدربوا.", "The same source sentence states the category and its defining labeled-training requirement."),
    ], INTEGRATED, "The labeled-data clause supplies the necessary qualification of the single supervised-learning classification.", False, False, "There is one proposition, not two independently scored propositions: the label requirement explains the stated supervised category.", dependency="Separating the requirement would fragment the category-and-definition unit."),
    r("CS-003:1", [
        p("الجدار الناري يراقب حركة مرور الشبكة الداخلة والخارجة.", "الجدار الناري Firewall نظام أمني بيراقب حركة مرور الشبكة الداخلة والخارجة، وبيسمح بيها أو يمنعها حسب قواعد أمنية محددة مسبقًا.", "بيراقب حركة مرور الشبكة الداخلة والخارجة supports the monitoring behavior."),
        p("الجدار الناري يسمح بحركة المرور أو يمنعها وفق قواعد أمنية محددة مسبقًا.", "الجدار الناري Firewall نظام أمني بيراقب حركة مرور الشبكة الداخلة والخارجة، وبيسمح بيها أو يمنعها حسب قواعد أمنية محددة مسبقًا.", "بيسمح بيها أو يمنعها حسب قواعد supports the enforcement behavior."),
    ], NON_ATOMIC, "Monitoring traffic and enforcing allow-or-deny rules are distinct firewall behaviors.", True, True, "Monitoring can be correctly attributed while enforcement is misstated, and enforcement can be correctly attributed even if the monitoring wording is rejected."),
    r("SE-003:5", [
        p("الوراثة المتعددة تعني الوراثة من أكثر من أب.", "الوراثة المتعددة Multiple Inheritance معناها الوراثة من أكتر من أب، وبتدعمها لغات زي C++ وPython، وممكن تسبب مشاكل زي الـ Diamond Problem.", "The definition is stated before the language examples."),
        p("لغة C++ تدعم الوراثة المتعددة.", "الوراثة المتعددة Multiple Inheritance معناها الوراثة من أكتر من أب، وبتدعمها لغات زي C++ وPython، وممكن تسبب مشاكل زي الـ Diamond Problem.", "C++ is explicitly named among supporting languages."),
    ], NON_ATOMIC, "The concept definition and C++ support are separately scoreable technical facts.", True, True, "The definition can be right while the language-support example is wrong, and C++ support can be right even if the definition is misstated."),
    r("SE-033:1", [
        p("المصفوفة تخزن عناصرها في مواقع ذاكرة متجاورة.", "المصفوفة Array بتخزن عناصرها في مواقع ذاكرة متجاورة، بينما عقد القائمة المتصلة Linked List بتتوزع في الذاكرة وبترتبط بمؤشرات.", "The first comparison side explicitly states contiguous array storage."),
        p("عقد القائمة المتصلة تتوزع في الذاكرة وترتبط بمؤشرات.", "المصفوفة Array بتخزن عناصرها في مواقع ذاكرة متجاورة، بينما عقد القائمة المتصلة Linked List بتتوزع في الذاكرة وبترتبط بمؤشرات.", "The second side explicitly states distributed nodes and pointer links."),
    ], NON_ATOMIC, "The comparison asserts independent memory-layout facts about two structures.", True, True, "Either structure's layout description can be accepted or rejected without determining the other."),
    r("GN-006:5", [
        p("عنوان IPv6 يتكون من 128 bit.", "عنوان IPv6 بيتكون من 128 bit، وبيتكتب بصيغة سداسية عشرية Hexadecimal مفصولة بنقطتين رأسيتين، وبيوفر فضاء عناوين ضخم بيحل مشكلة النفاد.", "The source explicitly gives the bit width."),
        p("عنوان IPv6 يكتب بصيغة سداسية عشرية تفصلها نقطتان رأسيتان.", "عنوان IPv6 بيتكون من 128 bit، وبيتكتب بصيغة سداسية عشرية Hexadecimal مفصولة بنقطتين رأسيتين، وبيوفر فضاء عناوين ضخم بيحل مشكلة النفاد.", "The source explicitly gives the written notation."),
        p("IPv6 يوفر فضاء عناوين ضخمًا يحل مشكلة النفاد.", "عنوان IPv6 بيتكون من 128 bit، وبيتكتب بصيغة سداسية عشرية Hexadecimal مفصولة بنقطتين رأسيتين، وبيوفر فضاء عناوين ضخم بيحل مشكلة النفاد.", "The source explicitly states the capacity consequence."),
    ], NON_ATOMIC, "Width, notation, and address-space consequence are three separate IPv6 assertions.", True, True, "The first two properties can vary independently; neither determines the other.", multi="P1 width, P2 notation, and P3 capacity consequence can each be scored without accepting either remaining proposition."),
    r("GN-028:2", [
        p("الـ Shell برنامج يفسر الأوامر المكتوبة وينفذها، ومن أمثلته Bash.", "الـ Shell هو البرنامج اللي بيفسر الأوامر المكتوبة وينفذها، ومن أمثلته Bash وZsh.", "The source states one definition and immediately supplies Bash as its example."),
    ], INTEGRATED, "Bash is an example inside one Shell definition, not an additional behavior needing a separate claim.", False, False, "There is no second proposition after applying the rubric's example rule.", dependency="Splitting Bash from the definition would turn a clarifying example into an over-fragmented claim."),
    r("GN-046:1", [
        p("الترميز نظام يمثل المحارف كأرقام يفهمها الحاسوب ويخزنها كبتات.", "الترميز Encoding نظام لتمثيل المحارف كأرقام يفهمها الحاسوب ويخزنها كبتات.", "The source expresses numeric representation and bit storage as one encoding mechanism."),
    ], INTEGRATED, "Representation as numbers and storage as bits are successive parts of the same encoding definition.", False, False, "The source gives one mechanism; it does not present storage as a separate effect.", dependency="Isolating bit storage would fragment how the same encoded representation is held by the computer."),
    r("DA-038:4", [
        p("قاموس البيانات يوحد فهم البيانات بين أعضاء الفريق.", "بيوحد فهم البيانات بين أعضاء الفريق ويقلل الالتباس حول معاني الأعمدة والاختصارات.", "The first clause directly states shared understanding."),
        p("قاموس البيانات يقلل الالتباس حول معاني الأعمدة والاختصارات.", "بيوحد فهم البيانات بين أعضاء الفريق ويقلل الالتباس حول معاني الأعمدة والاختصارات.", "The second clause directly states reduced ambiguity."),
    ], NON_ATOMIC, "Shared understanding and reduced ambiguity are different organizational effects.", True, True, "A team can share a general understanding while ambiguity remains, or ambiguity can fall without fully unifying understanding."),
    r("DA-038:5", [
        p("قاموس البيانات يسرع إدماج الأعضاء الجدد.", "وبيسرع إدماج الأعضاء الجدد ويقلل اعتمادهم على المعرفة الضمنية عند الأفراد.", "The source explicitly states faster onboarding."),
        p("قاموس البيانات يقلل اعتماد الأعضاء الجدد على المعرفة الضمنية لدى الأفراد.", "وبيسرع إدماج الأعضاء الجدد ويقلل اعتمادهم على المعرفة الضمنية عند الأفراد.", "The source explicitly states reduced tacit-knowledge dependence."),
    ], NON_ATOMIC, "Onboarding speed and reliance on tacit knowledge are separate outcomes.", True, True, "Either outcome can improve without establishing the other."),
    r("DA-049:5", [
        p("مخطط ندفة الثلج يوفر مساحة.", "مخطط ندفة الثلج بيوفر مساحة ويقلل التكرار، مقابل استعلامات أعقد بربط جداول أكتر.", "The source explicitly states the storage benefit."),
        p("مخطط ندفة الثلج يقلل التكرار.", "مخطط ندفة الثلج بيوفر مساحة ويقلل التكرار، مقابل استعلامات أعقد بربط جداول أكتر.", "The source explicitly states repetition reduction."),
        p("مخطط ندفة الثلج يؤدي إلى استعلامات أعقد بسبب ربط جداول أكثر.", "مخطط ندفة الثلج بيوفر مساحة ويقلل التكرار، مقابل استعلامات أعقد بربط جداول أكتر.", "The source explicitly states the query-complexity cost."),
    ], NON_ATOMIC, "The claim combines two benefits and one independent query cost.", True, True, "Space saving and repetition reduction are separately testable.", multi="P1 space, P2 repetition, and P3 query complexity are distinct trade-off dimensions and each can be scored independently."),
    r("CS-010:1", [
        p("SSL/TLS يشفر الاتصال بين العميل والخادم ويضمن سريته وسلامته.", "SSL/TLS بروتوكول أمني بيشفر الاتصال بين العميل والخادم، وبيضمن سريته وسلامته، وTLS هو الخليفة الحديث لبروتوكول SSL المهجور.", "The source explicitly states the connection-security behavior."),
        p("TLS هو الخليفة الحديث لبروتوكول SSL المهجور.", "SSL/TLS بروتوكول أمني بيشفر الاتصال بين العميل والخادم، وبيضمن سريته وسلامته، وTLS هو الخليفة الحديث لبروتوكول SSL المهجور.", "The source separately states the protocol-history relationship."),
    ], NON_ATOMIC, "Security behavior and protocol history are unrelated scoring dimensions.", True, True, "The encryption properties can be right while the historical relationship is wrong, and conversely."),
    r("CS-049:4", [
        p("فحص الثغرات ينتج قائمة ثغرات محتملة قد تحوي إنذارات كاذبة.", "الفحص بينتج قائمة ثغرات محتملة، ممكن تحوي إنذارات كاذبة، بينما الاختبار بيأكد الثغرات الحقيقية ويقيس أثرها العملي.", "The scanner clause explicitly preserves possibility of false alerts."),
        p("اختبار الاختراق يؤكد الثغرات الحقيقية.", "الفحص بينتج قائمة ثغرات محتملة، ممكن تحوي إنذارات كاذبة، بينما الاختبار بيأكد الثغرات الحقيقية ويقيس أثرها العملي.", "The source states confirmation of real vulnerabilities."),
        p("اختبار الاختراق يقيس الأثر العملي للثغرات.", "الفحص بينتج قائمة ثغرات محتملة، ممكن تحوي إنذارات كاذبة، بينما الاختبار بيأكد الثغرات الحقيقية ويقيس أثرها العملي.", "The source states practical impact measurement."),
    ], NON_ATOMIC, "Scanner uncertainty, vulnerability confirmation, and impact measurement are separate behaviors.", True, True, "Scanner output can be characterized independently of penetration-test confirmation.", multi="P1 scanner output, P2 confirmation, and P3 impact measurement are three independently scoreable tool behaviors; ممكن remains only in P1."),
    r("SE-035:1", [
        p("الجدول التجزيئي يخزن أزواج مفتاح وقيمة.", "الجدول التجزيئي Hash Table هيكل بيخزن أزواج مفتاح وقيمة، وبيتيح وصول سريع عن طريق دالة تجزئة Hash Function.", "The source directly states the stored structure."),
        p("الجدول التجزيئي يتيح وصولًا سريعًا عبر دالة تجزئة.", "الجدول التجزيئي Hash Table هيكل بيخزن أزواج مفتاح وقيمة، وبيتيح وصول سريع عن طريق دالة تجزئة Hash Function.", "The source directly states the access property and mechanism."),
    ], NON_ATOMIC, "Storage form and fast hash-based access are two properties, not a term plus a mere parenthetical definition.", True, True, "Key-value storage can hold while the claimed speed fails, and hash-based fast access can be evaluated without relying on the storage wording."),
    r("GN-002:1", [
        p("نظام التشغيل يدير موارد الحاسوب المادية.", "نظام التشغيل Operating System هو البرنامج الوسيط اللي بيدير موارد الحاسوب المادية، وبيتيح للتطبيقات والمستخدمين التعامل معاها.", "The source directly states resource management."),
        p("نظام التشغيل يتيح للتطبيقات والمستخدمين التعامل مع موارد الحاسوب.", "نظام التشغيل Operating System هو البرنامج الوسيط اللي بيدير موارد الحاسوب المادية، وبيتيح للتطبيقات والمستخدمين التعامل معاها.", "The source directly states mediated interaction with those resources."),
    ], NON_ATOMIC, "Managing resources and exposing them to applications and users are distinguishable operating-system roles.", True, True, "Resource management can be correctly described while the interaction role is rejected, and an interface role can be assessed without accepting the management assertion."),
    r("GN-002:3", [
        p("إدارة نظام التشغيل للذاكرة تشمل تخصيصها للعمليات وتحريرها، وتستخدم تقنيات مثل الذاكرة الافتراضية.", "بيدير نظام التشغيل الذاكرة Memory Management بتخصيصها للعمليات وتحريرها، وبيستخدم تقنيات زي الذاكرة الافتراضية Virtual Memory.", "The operations and virtual-memory example are stated as one explanation of memory management."),
    ], INTEGRATED, "Virtual memory is an example within the single memory-management function rather than an independent claim target.", False, False, "After applying the example rule, only one memory-management proposition remains.", dependency="Splitting the implementation example would over-fragment the definition of the same function."),
    r("GN-038:3", [
        p("تعديل كتلة يغير بصمتها فيكسر ارتباط الكتل اللاحقة ويكشف العبث.", "أي تعديل في كتلة بيغير بصمتها، فبيكسر ارتباط كل الكتل اللاحقة، وبيكشف العبث فورًا.", "The source states a single ordered condition-and-consequence mechanism."),
    ], INTEGRATED, "Hash change, broken linkage, and detection are causally scoped stages of one tamper-detection mechanism.", False, False, "There is one mechanism proposition, not independent effects detached from the triggering modification.", dependency="Splitting the causal stages would remove the condition governing the later consequences."),
    r("DA-017:6", [
        p("SELF JOIN يربط الجدول بنفسه ويستخدم لعلاقات داخل الجدول مثل علاقة الموظف بمديره.", "SELF JOIN هو ربط الجدول بنفسه، وبيستخدم للعلاقات جوه الجدول الواحد زي علاقة الموظف بمديره.", "The source states the definition, use, and employee-manager example as one unit."),
    ], INTEGRATED, "The use and employee-manager illustration clarify the SELF JOIN definition rather than add a separate technical behavior.", False, False, "The example is not treated as proposition 2 under the rubric.", dependency="Separating the example would fragment one definition-and-example unit."),
    r("DS-038:1", [
        p("قدمت معمارية Transformer عام 2017.", "الـ Transformer معمارية عصبية اتقدمت سنة 2017، وبتعتمد كليًا على آلية الانتباه Attention من غير تكرار أو التفاف.", "The source explicitly states the year."),
        p("تعتمد معمارية Transformer كليًا على الانتباه دون تكرار أو التفاف.", "الـ Transformer معمارية عصبية اتقدمت سنة 2017، وبتعتمد كليًا على آلية الانتباه Attention من غير تكرار أو التفاف.", "The source explicitly states the architecture and preserved exclusion."),
    ], NON_ATOMIC, "Historical date and architectural mechanism can be correct or incorrect independently.", True, True, "The year does not determine the architecture, and the architecture does not determine the year."),
    r("CS-001:4", [
        p("السلامة تعني منع التعديل أو العبث غير المصرح به، وتدعمها تقنيات مثل Hashing.", "السلامة Integrity معناها ضمان إن البيانات متتعدلش أو يتم العبث بيها بشكل غير مصرح به، وبتتدعم بتقنيات زي الـ Hashing والتوقيعات الرقمية Digital Signatures.", "The source states one Integrity definition with Hashing as an implementation example."),
    ], INTEGRATED, "Hashing is an example supporting the same negated Integrity definition.", False, False, "The implementation example does not create proposition 2.", dependency="Splitting would detach an example from the security property it supports."),
    r("CS-032:2", [
        p("نظام SIEM يوحد صيغ السجلات.", "النظام بيوحد صيغ السجلات Normalization، وبيربط الأحداث المتفرقة Correlation، عشان يكشف أنماط هجوم مش ظاهرة في مصدر واحد.", "The source explicitly states normalization."),
        p("نظام SIEM يربط الأحداث المتفرقة.", "النظام بيوحد صيغ السجلات Normalization، وبيربط الأحداث المتفرقة Correlation، عشان يكشف أنماط هجوم مش ظاهرة في مصدر واحد.", "The source explicitly states correlation."),
        p("توحيد السجلات وربط الأحداث يساعدان نظام SIEM على كشف أنماط هجوم لا تظهر في مصدر واحد.", "النظام بيوحد صيغ السجلات Normalization، وبيربط الأحداث المتفرقة Correlation، عشان يكشف أنماط هجوم مش ظاهرة في مصدر واحد.", "The governing subject and operations are retained for the source-stated detection purpose."),
    ], NON_ATOMIC, "Normalization, correlation, and their stated detection outcome are separately assessable.", True, True, "The system can normalize without correlating and correlate without normalizing.", multi="P1 normalization and P2 correlation are independent operations; P3 is a complete subject-governed outcome, not a bare purpose fragment, and can be evaluated independently of whether both operations were correctly described."),
    r("SE-030:5", [
        p("تراكم الدين التقني يبطئ الفريق تدريجيًا.", "لو سيبت الدين يتراكم، بيبطئ الفريق تدريجيًا، وبيزيد الأعطال، وممكن يوصل لشل القدرة على إضافة ميزات جديدة.", "The source explicitly states gradual slowdown."),
        p("تراكم الدين التقني يزيد الأعطال.", "لو سيبت الدين يتراكم، بيبطئ الفريق تدريجيًا، وبيزيد الأعطال، وممكن يوصل لشل القدرة على إضافة ميزات جديدة.", "The source explicitly states more failures."),
        p("تراكم الدين التقني قد يصل إلى شل إضافة ميزات جديدة.", "لو سيبت الدين يتراكم، بيبطئ الفريق تدريجيًا، وبيزيد الأعطال، وممكن يوصل لشل القدرة على إضافة ميزات جديدة.", "ممكن preserves the source's possibility for the strongest consequence."),
    ], NON_ATOMIC, "Slowdown, failures, and possible feature paralysis are distinct consequences.", True, True, "Slowdown and failures can occur independently.", multi="P1 slowdown, P2 failures, and P3 possible paralysis can each be judged independently; the uncertainty marker remains in P3."),
    r("SE-047:3", [
        p("في Cache-Aside يطلب التطبيق من الذاكرة المؤقتة أولًا، وعند Cache Miss يجلب من المصدر ويخزن.", "استراتيجية Cache-Aside بيطلب فيها التطبيق من الذاكرة المؤقتة الأول، وبيجلب من المصدر ويخزن عند الغياب Cache Miss.", "The source presents lookup and the miss-conditioned branch as one ordered strategy."),
    ], INTEGRATED, "The second action is directly scoped to cache absence and completes one Cache-Aside procedure.", False, False, "There is no independent proposition 2 after retaining the Cache Miss condition.", dependency="Splitting miss handling from the initial lookup would change the defined strategy."),
    r("GN-009:4", [
        p("طبقة الشبكة مسؤولة عن العنونة المنطقية.", "طبقة الشبكة Network مسؤولة عن العنونة المنطقية والتوجيه Routing بين الشبكات المختلفة، وبتشتغل بعناوين IP.", "The source explicitly states logical addressing."),
        p("طبقة الشبكة مسؤولة عن التوجيه بين الشبكات المختلفة.", "طبقة الشبكة Network مسؤولة عن العنونة المنطقية والتوجيه Routing بين الشبكات المختلفة، وبتشتغل بعناوين IP.", "The source explicitly states routing."),
        p("طبقة الشبكة تعمل بعناوين IP.", "طبقة الشبكة Network مسؤولة عن العنونة المنطقية والتوجيه Routing بين الشبكات المختلفة، وبتشتغل بعناوين IP.", "The source explicitly names IP addresses."),
    ], NON_ATOMIC, "Addressing, routing, and IP-address operation are separate network-layer facts.", True, True, "Addressing and routing can be scored independently.", multi="P1 addressing, P2 routing, and P3 IP addressing are distinct technical assertions, even though all share the same subject."),
    r("DA-037:5", [
        p("subset يحدد الأعمدة المعتمدة في المقارنة.", "المعامل subset بيحدد الأعمدة المعتمدة في المقارنة، والمعامل keep بيحدد أي نسخة تتحفظ.", "The source explicitly states subset behavior."),
        p("keep يحدد أي نسخة يحتفظ بها.", "المعامل subset بيحدد الأعمدة المعتمدة في المقارنة، والمعامل keep بيحدد أي نسخة تتحفظ.", "The source explicitly states keep behavior."),
    ], NON_ATOMIC, "The two parameters have different independently scoreable semantics.", True, True, "Either parameter description can be correct while the other is wrong."),
    r("DA-041:7", [
        p("الأعمدة المحسوبة تحسب صفًا بصف وتخزن نتائجها.", "الأعمدة المحسوبة بتتحسب صف بصف وبتتخزن نتائجها، بينما المقاييس بتتحسب ديناميكيًا وقت الاستعلام حسب سياق التقرير.", "The source explicitly states calculated-column evaluation and storage."),
        p("المقاييس تحسب ديناميكيًا وقت الاستعلام حسب سياق التقرير.", "الأعمدة المحسوبة بتتحسب صف بصف وبتتخزن نتائجها، بينما المقاييس بتتحسب ديناميكيًا وقت الاستعلام حسب سياق التقرير.", "The source explicitly states measure evaluation."),
    ], NON_ATOMIC, "The comparison makes independent assertions about calculated columns and measures.", True, True, "Either side can be evaluated without accepting the other."),
    r("SE-022:4", [
        p("في نموذج الحالة المرغوبة يصف المستخدم المطلوب في YAML ويطابقه النظام باستمرار.", "النظام بيشتغل بنموذج الحالة المرغوبة Desired State، المستخدم بيوصف المطلوب في ملفات YAML، والنظام بيشتغل باستمرار على مطابقته.", "The source gives declaration and reconciliation as the two linked stages of one mechanism."),
    ], INTEGRATED, "The system behavior is scoped to the state declared by the user, forming one desired-state mechanism.", False, False, "There is one condition-and-behavior proposition rather than two independent outcomes.", dependency="Separating reconciliation would remove the declared state that it continuously matches."),
    r("SE-029:5", [
        p("مراجعة الكود تنشر المعرفة بين أعضاء الفريق.", "المراجعة بتنشر المعرفة بين أعضاء الفريق، وبتقلل احتكار فرد واحد لفهم أجزاء من النظام.", "The source explicitly states knowledge distribution."),
        p("مراجعة الكود تقلل احتكار فرد واحد لفهم أجزاء من النظام.", "المراجعة بتنشر المعرفة بين أعضاء الفريق، وبتقلل احتكار فرد واحد لفهم أجزاء من النظام.", "The source explicitly states reduced concentration."),
    ], NON_ATOMIC, "Knowledge distribution and reduced individual concentration are separate team effects.", True, True, "Either effect can occur without fully establishing the other."),
    r("SE-032:2", [
        p("المصفوفة تخزن العناصر في مواقع متجاورة.", "المصفوفة Array بتخزن العناصر في مواقع متجاورة، وبتتيح وصول مباشر بالفهرس بزمن ثابت.", "The source explicitly states layout."),
        p("المصفوفة تتيح وصولًا مباشرًا بالفهرس بزمن ثابت.", "المصفوفة Array بتخزن العناصر في مواقع متجاورة، وبتتيح وصول مباشر بالفهرس بزمن ثابت.", "The source explicitly states indexed-access complexity."),
    ], NON_ATOMIC, "Memory layout and access complexity are distinct properties.", True, True, "Either property can be judged without assuming the other."),
    r("SE-032:3", [
        p("القائمة المتصلة تربط عقدًا بمؤشرات.", "القائمة المتصلة Linked List بتربط عقد بمؤشرات، وبتتيح إدراج وحذف مرنين من غير إزاحة العناصر.", "The source explicitly states pointer linkage."),
        p("القائمة المتصلة تتيح إدراجًا وحذفًا مرنين دون إزاحة العناصر.", "القائمة المتصلة Linked List بتربط عقد بمؤشرات، وبتتيح إدراج وحذف مرنين من غير إزاحة العناصر.", "The source explicitly states operations and preserves من غير."),
    ], NON_ATOMIC, "Structure and insertion/deletion behavior are separately scoreable.", True, True, "The pointer assertion can be right while the operation claim is wrong, and conversely."),
    r("SE-032:8", [
        p("الرسوم البيانية تمثل الكيانات وعلاقاتها بعقد وحواف.", "الرسوم البيانية Graphs بتمثل الكيانات وعلاقاتها بعقد وحواف، واختيار الهيكل المناسب بيحدد كفاءة الخوارزمية بأكملها.", "The source explicitly states graph representation."),
        p("اختيار هيكل البيانات المناسب يحدد كفاءة الخوارزمية بأكملها.", "الرسوم البيانية Graphs بتمثل الكيانات وعلاقاتها بعقد وحواف، واختيار الهيكل المناسب بيحدد كفاءة الخوارزمية بأكملها.", "The source separately states the efficiency consequence."),
    ], NON_ATOMIC, "The graph definition and the general structure-choice consequence are independent.", True, True, "The representation can be correct while the efficiency statement is rejected, and conversely."),
    r("GN-015:3", [
        p("في الويب يرسل العميل طلب HTTP إلى Endpoint ويستقبل استجابة غالبًا بصيغة JSON.", "في الويب، العميل بيبعت طلب HTTP لنقطة نهاية Endpoint محددة، وبيستقبل استجابة غالبًا بصيغة JSON.", "The source states one request-response exchange and preserves غالبًا on the response format."),
    ], INTEGRATED, "The received response is directly scoped to the initiating request in one web exchange.", False, False, "There is no independent response proposition without the corresponding request in this assertion.", dependency="Splitting the response from the request would fragment one HTTP transaction and strand the approximation qualifier."),
    r("GN-037:2", [
        p("أجهزة IoT تجمع بيانات من محيطها وترسلها للتحليل واتخاذ قرارات بناءً عليها.", "الأجهزة دي بتجمع بيانات من محيطها وبتبعتها للتحليل واتخاذ قرارات آلية أو يدوية بناءً عليها.", "The source presents collection and downstream use as one end-to-end data flow."),
    ], INTEGRATED, "Pronouns and the purpose clause connect collection, transmission, analysis, and decisions into one pipeline description.", False, False, "The first reading treats the downstream action as scoped to the same collected data, not as proposition 2.", dependency="Separating the destination and purpose would fragment the described data-flow mechanism."),
    r("GN-048:4", [
        p("الرخص الاحتكارية تقيد الوصول للكود المصدري.", "وفيه كمان رخص احتكارية، بتقيد الوصول للكود المصدري وتمنع التعديل وإعادة التوزيع.", "The source explicitly states source-code access restriction."),
        p("الرخص الاحتكارية تمنع التعديل.", "وفيه كمان رخص احتكارية، بتقيد الوصول للكود المصدري وتمنع التعديل وإعادة التوزيع.", "The source explicitly states modification prohibition."),
        p("الرخص الاحتكارية تمنع إعادة التوزيع.", "وفيه كمان رخص احتكارية، بتقيد الوصول للكود المصدري وتمنع التعديل وإعادة التوزيع.", "The source explicitly states redistribution prohibition."),
    ], NON_ATOMIC, "Source access, modification, and redistribution are independent license restrictions.", True, True, "Access restriction and modification prohibition can vary independently.", multi="P1 access, P2 modification, and P3 redistribution are three independently scoreable restrictions; prohibitive meaning is retained in each."),
]
