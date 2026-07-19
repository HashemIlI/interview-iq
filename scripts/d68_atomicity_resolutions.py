"""Authored evidence-based resolutions for D68 pass disagreements."""

from __future__ import annotations

from d68_atomicity_adjudication import INTEGRATED, NON_ATOMIC


DISAGREEMENT_RESOLUTIONS = [
    {
        "candidate_key": "CS-003:1",
        "first_classification": NON_ATOMIC,
        "verification_classification": INTEGRATED,
        "exact_disputed_propositions": [
            "الجدار الناري يراقب حركة مرور الشبكة الداخلة والخارجة.",
            "الجدار الناري يسمح بحركة المرور أو يمنعها وفق قواعد أمنية محددة مسبقًا.",
        ],
        "exact_source_excerpts": [
            "الجدار الناري Firewall نظام أمني بيراقب حركة مرور الشبكة الداخلة والخارجة، وبيسمح بيها أو يمنعها حسب قواعد أمنية محددة مسبقًا.",
        ],
        "independent_judgability_analysis": {
            "can_proposition_1_be_true_while_proposition_2_is_false": True,
            "can_proposition_2_be_true_while_proposition_1_is_false": True,
            "evidence_based_explanation": "The source asserts two predicates. Accepting traffic monitoring does not require accepting the stated allow/deny behavior, and accepting rule enforcement does not require accepting the monitoring description. Each can be scored without changing the other's meaning.",
        },
        "final_classification": NON_ATOMIC,
        "final_rationale": "The verification pass over-integrated two separately judgeable firewall behaviors. Both are source-stated and remain complete after separation.",
    },
    {
        "candidate_key": "SE-035:1",
        "first_classification": NON_ATOMIC,
        "verification_classification": INTEGRATED,
        "exact_disputed_propositions": [
            "الجدول التجزيئي يخزن أزواج مفتاح وقيمة.",
            "الجدول التجزيئي يتيح وصولًا سريعًا عبر دالة تجزئة.",
        ],
        "exact_source_excerpts": [
            "الجدول التجزيئي Hash Table هيكل بيخزن أزواج مفتاح وقيمة، وبيتيح وصول سريع عن طريق دالة تجزئة Hash Function.",
        ],
        "independent_judgability_analysis": {
            "can_proposition_1_be_true_while_proposition_2_is_false": True,
            "can_proposition_2_be_true_while_proposition_1_is_false": True,
            "evidence_based_explanation": "The storage assertion and the speed/mechanism assertion have different truth conditions. Key-value storage can be accepted while the speed claim is rejected; hash-based access can be evaluated even if the exact storage characterization is disputed.",
        },
        "final_classification": NON_ATOMIC,
        "final_rationale": "Fast access is an additional performance/mechanism assertion, not merely a parenthetical example required to understand key-value storage.",
    },
    {
        "candidate_key": "GN-015:3",
        "first_classification": INTEGRATED,
        "verification_classification": NON_ATOMIC,
        "exact_disputed_propositions": [
            "عميل الويب يرسل طلب HTTP إلى Endpoint محددة.",
            "عميل الويب يستقبل استجابة غالبًا بصيغة JSON.",
        ],
        "exact_source_excerpts": [
            "في الويب، العميل بيبعت طلب HTTP لنقطة نهاية Endpoint محددة، وبيستقبل استجابة غالبًا بصيغة JSON.",
        ],
        "independent_judgability_analysis": {
            "can_proposition_1_be_true_while_proposition_2_is_false": False,
            "can_proposition_2_be_true_while_proposition_1_is_false": False,
            "evidence_based_explanation": "Within the asserted web exchange, the response is the response to the initiating request. The second clause presupposes that transaction and carries a response-format qualifier; isolating it would remove the governing exchange and could strand غالبًا.",
        },
        "final_classification": INTEGRATED,
        "final_rationale": "The request and its qualified response are the ordered halves of one HTTP transaction, so splitting would materially fragment the procedure asserted by the source.",
    },
    {
        "candidate_key": "GN-037:2",
        "first_classification": INTEGRATED,
        "verification_classification": NON_ATOMIC,
        "exact_disputed_propositions": [
            "أجهزة إنترنت الأشياء تجمع بيانات من البيئة المحيطة.",
            "أجهزة إنترنت الأشياء ترسل البيانات لتحليلها واتخاذ قرارات آلية أو يدوية بناءً عليها.",
        ],
        "exact_source_excerpts": [
            "الأجهزة دي بتجمع بيانات من محيطها وبتبعتها للتحليل واتخاذ قرارات آلية أو يدوية بناءً عليها.",
        ],
        "independent_judgability_analysis": {
            "can_proposition_1_be_true_while_proposition_2_is_false": True,
            "can_proposition_2_be_true_while_proposition_1_is_false": True,
            "evidence_based_explanation": "Collection and transmission/downstream use are sequential but not inseparable. Devices can collect without sending, and devices can transmit data for analysis without the same device having collected it from its surroundings. Both diagnostic propositions retain explicit subjects and objects.",
        },
        "final_classification": NON_ATOMIC,
        "final_rationale": "The first pass over-integrated an end-to-end pipeline whose collection and transmission/use stages remain independently judgeable without changing their source meaning.",
    },
]
