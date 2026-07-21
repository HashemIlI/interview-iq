"""Three-pass, review-gated builder for the decomposition corpus v2 pilot.

Dataset engineering only: no training, model loading, runtime change, or O9 use.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import random
import re
import statistics
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Protocol

from interview_iq.decomposition.types import GenerationSource, PilotAnswerCase, PilotCaseType

TRACKS = ("DA", "DS", "CS", "SE", "GN")
CASE_TYPES: tuple[PilotCaseType, ...] = (
    "complete_correct", "short_partial", "mixed_correctness",
    "plausible_misconception", "natural_egyptian_spoken",
)
REVIEW_STATUS = "DRAFT_UNREVIEWED"
REFERENCE_RELATIVE_PATH = "data/refdocs/reference_docs_250_FINAL_v1.json"
QUESTIONS_RELATIVE_PATH = "data/questions/questions_250.json"
O9_RELATIVE_PATH = "results/o9_decomposition_exercises.md"
PROMPT_VERSION = "answer_generation_v1"
CLAIM_PROMPT_VERSION = "claim_extraction_v1"
AUDIT_PROMPT_VERSION = "claim_audit_v1"
DETERMINISTIC_GENERATED_AT = "2026-07-20T00:00:00+03:00"

GENERATION_PROMPT_V1 = """# Answer Generation Prompt v1

Status: DRAFT_UNREVIEWED data preparation. This prompt does not create human answers.

PASS 1 ONLY. Given question_id, track, question text, authorized reference chunks,
and the Latin technical terms found in those inputs, return JSON containing exactly
five Egyptian-Arabic candidate answers: complete_correct, short_partial,
mixed_correctness, plausible_misconception, and natural_egyptian_spoken.

The five cases must differ semantically, not merely lexically. Preserve Latin technical
terms. Do not copy the reference verbatim. Preserve deliberately expressed factual
errors, negation, hedging, and uncertainty. Do not emit claims in this pass. Do not
include the case label inside answer text. These are synthetic candidate-answer cases,
not real human responses.
"""
CLAIM_EXTRACTION_PROMPT_V1 = """# Claim Extraction Prompt v1

Status: DRAFT_UNREVIEWED data preparation.

PASS 2 ONLY. You receive one candidate answer and no reference document. Return a JSON
list of atomic, self-contained claims in simplified MSA. Extract every proposition from
the answer only. Do not add, correct, or omit information. Preserve errors, negation,
hedging, uncertainty, and every Latin technical term byte-for-byte where possible.
Do not return a rendered numbered target.
"""
CLAIM_AUDIT_PROMPT_V1 = """# Independent Claim Audit Prompt v1

Status: DRAFT_UNREVIEWED data preparation.

PASS 3 ONLY. Independently compare one answer with its extracted JSON claim list. Check
unsupported additions, missing propositions, atomicity, self-containment, Latin-term
preservation, repetition, and case-type compliance. Do not rewrite or approve the data.
Return machine-readable findings. The reference is not used to correct candidate facts.
"""

# Atomic simplified-MSA facts authored only from the selected project references.
CORRECT_CLAIMS: dict[str, list[str]] = {
    "DA-004": [
        "Data Cleaning هو إجراء لاكتشاف البيانات غير الدقيقة أو غير المكتملة أو غير المتسقة ومعالجتها.",
        "تعالج عملية Data Cleaning القيم المفقودة Missing Values.",
        "تزيل عملية Data Cleaning السجلات المكررة Duplicates.",
        "قد تؤدي البيانات الرديئة إلى نتائج تحليل مضللة وفق مبدأ Garbage In Garbage Out.",
    ],
    "DA-010": [
        "يقيس معامل Pearson قوة العلاقة الخطية بين متغيرين رقميين.",
        "يقيس معامل Pearson اتجاه العلاقة الخطية بين متغيرين رقميين.",
        "تتراوح قيمة معامل Pearson بين -1 و +1.",
        "تشير قيمة +1 في معامل Pearson إلى علاقة خطية طردية تامة.",
        "تشير قيمة -1 في معامل Pearson إلى علاقة خطية عكسية تامة.",
        "تشير قيمة 0 في معامل Pearson إلى غياب العلاقة الخطية.",
    ],
    "DA-020": [
        "يحذف DELETE صفوفًا من الجدول.", "يمكن تقييد DELETE بشرط WHERE.",
        "يحذف TRUNCATE كل صفوف الجدول دفعة واحدة.", "يبقي TRUNCATE بنية الجدول.",
        "لا يقبل TRUNCATE شرط WHERE.", "يحذف DROP بيانات الجدول.", "يحذف DROP بنية الجدول.", "يحذف DROP فهارس الجدول.",
    ],
    "DA-045": [
        "يعتمد تحليل RFM على الحداثة Recency.", "يعتمد تحليل RFM على التكرار Frequency.", "يعتمد تحليل RFM على القيمة النقدية Monetary.",
        "تقيس Recency المدة منذ آخر شراء للعميل.", "تقيس Frequency عدد مرات شراء العميل.",
        "تقيس Monetary إجمالي إنفاق العميل.", "تستخدم شرائح RFM لتوجيه حملات تسويقية مخصصة.",
    ],
    "DS-007": [
        "Random Forest هو نموذج Ensemble يبني عددًا كبيرًا من أشجار القرار.",
        "يجمع Random Forest تنبؤات أشجار القرار للوصول إلى قرار نهائي.",
        "تتدرب كل شجرة في Random Forest على عينة عشوائية مسحوبة مع الإرجاع.",
        "يقلل Random Forest التباين Variance مقارنة بشجرة قرار واحدة.",
        "يحد Random Forest من Overfitting عبر تجميع أشجار متنوعة.",
    ],
    "DS-012": [
        "Naive Bayes مصنف احتمالي يعتمد على نظرية Bayes.",
        "يختار Naive Bayes الفئة ذات الاحتمال الأعلى.",
        "يفترض Naive Bayes استقلال Features عن بعضها بشرط معرفة الفئة.",
        "يوصف Naive Bayes بأنه Naive لأن افتراض الاستقلال مبسط ونادرًا ما يتحقق تمامًا.",
    ],
    "DS-018": [
        "تضيف L1 Regularization مجموع القيم المطلقة للأوزان إلى دالة الخسارة.",
        "تضيف L2 Regularization مجموع مربعات الأوزان إلى دالة الخسارة.",
        "قد تدفع L1 Regularization بعض الأوزان إلى الصفر تمامًا.",
        "تحقق L1 Regularization اختيار Features ضمنيًا.",
        "تقلص L2 Regularization الأوزان نحو الصفر دون تصفيرها عادة.",
    ],
    "DS-019": [
        "يشمل Feature Engineering إنشاء متغيرات مدخلة للنموذج.", "يشمل Feature Engineering تحويل المتغيرات المدخلة للنموذج.", "يشمل Feature Engineering اختيار المتغيرات المدخلة للنموذج.",
        "يهدف Feature Engineering إلى تحسين القدرة التنبؤية للنموذج.",
        "قد يشمل Feature Engineering تطبيق One-Hot Encoding على المتغيرات الفئوية.",
        "تحدد جودة Features غالبًا سقف أداء النموذج في البيانات الجدولية.",
        "يتطلب Feature Engineering الجيد فهم Domain Knowledge.",
    ],
    "CS-006": [
        "AES خوارزمية تشفير متماثل.", "AES هو اختصار Advanced Encryption Standard.",
        "تدعم AES مفاتيح بطول 128 bit.", "تدعم AES مفاتيح بطول 192 bit.",
        "تدعم AES مفاتيح بطول 256 bit.",
    ],
    "CS-037": [
        "يزور DNS Spoofing ردود DNS.",
        "يوجه DNS Spoofing الضحية إلى عنوان IP خبيث بدل الوجهة الحقيقية.",
        "قد يحقن المهاجم سجلات مزيفة في Cache خادم DNS.",
        "يستخدم DNSSEC توقيعات رقمية للتحقق من سلامة سجلات DNS.", "يستخدم DNSSEC توقيعات رقمية للتحقق من مصدر سجلات DNS.",
    ],
    "CS-041": [
        "تربط Digital Certificate مفتاحًا عامًا بهوية مالكه.",
        "توقع Certificate Authority الموثوقة Digital Certificate.",
        "تتضمن PKI إصدار الشهادات الرقمية.", "تتضمن PKI إدارة الشهادات الرقمية.", "تتضمن PKI إبطال الشهادات الرقمية.",
        "تتحقق صحة الشهادة عبر Chain of Trust تنتهي إلى Root CA موثوقة مسبقًا.",
    ],
    "CS-049": [
        "Vulnerability Scanning عملية آلية واسعة لاكتشاف الثغرات المعروفة.",
        "لا يستغل Vulnerability Scanning الثغرات المكتشفة عادة.",
        "Penetration Testing جهد يدوي معمق.", "يحاول Penetration Testing استغلال الثغرات فعليًا.",
        "Vulnerability Scanning أسرع وأرخص من Penetration Testing.",
        "Penetration Testing أعمق وأعلى تكلفة من Vulnerability Scanning.",
    ],
    "SE-002": [
        "يجمع Encapsulation البيانات والدوال التي تعمل عليها داخل Class واحدة.",
        "يقيد Encapsulation الوصول المباشر إلى البيانات.", "يمكن جعل الخصائص الحساسة private.",
        "تتيح Getters و Setters العامة التعامل المنضبط مع الخصائص private.",
        "يحمي Encapsulation سلامة البيانات.",
    ],
    "SE-003": [
        "تتيح Inheritance لصنف Child Class اكتساب خصائص Parent Class.",
        "تتيح Inheritance لصنف Child Class اكتساب دوال Parent Class.",
        "تمثل Inheritance علاقة is-a بين الصنفين.",
        "تعني Single Inheritance أن يرث الصنف من أب واحد.",
        "تعني Multiple Inheritance أن يرث الصنف من أكثر من أب.",
    ],
    "SE-006": [
        "SOLID اختصار لخمسة مبادئ في التصميم كائني التوجه.",
        "ينص Single Responsibility على أن يكون للصنف سبب واحد للتغيير.",
        "ينص Open/Closed على أن تكون المكونات مفتوحة للتوسعة ومغلقة أمام التعديل المباشر.",
        "ينص Liskov Substitution على إمكان استبدال كائن الأب بكائن من صنفه الفرعي دون كسر صحة البرنامج.",
        "يفضل Interface Segregation واجهات صغيرة متخصصة.",
        "ينص Dependency Inversion على اعتماد الوحدات على Abstractions بدل تفاصيل التنفيذ.",
    ],
    "SE-031": [
        "Refactoring هو تحسين البنية الداخلية للكود دون تغيير سلوكه الخارجي الملحوظ.",
        "يرفع Refactoring قابلية قراءة الكود.", "يرفع Refactoring قابلية صيانة الكود.",
        "تحتاج عملية Refactoring إلى اختبارات آلية للتحقق من بقاء السلوك سليمًا.",
    ],
    "GN-016": [
        "JSON صيغة نصية خفيفة لتبادل البيانات.", "يعتمد JSON على أزواج مفتاح وقيمة.", "يدعم JSON القوائم.",
        "يستخدم XML وسوم Tags تحيط بالبيانات.", "JSON أوجز من XML عادة.",
        "أصبح JSON صيغة شائعة لواجهات REST.",
    ],
    "GN-017": [
        "Python لغة برمجة عالية المستوى.", "Python لغة مفسرة Interpreted متعددة الأغراض.",
        "تتميز Python بصياغة سهلة القراءة.",
        "تملك Python منظومة مكتبات واسعة مثل NumPy و Pandas و Django و Flask.",
        "ساعدت سهولة Python على انتشارها في التعلم والنمذجة السريعة Prototyping.",
    ],
    "GN-035": [
        "AI مجال واسع لبناء أنظمة تحاكي قدرات ذهنية بشرية.",
        "Machine Learning فرع من AI يتعلم الأنماط من البيانات.",
        "لا يتطلب Machine Learning برمجة كل نمط بصورة صريحة.",
        "يحتوي مجال AI على Machine Learning.", "يحتوي Machine Learning على Deep Learning.",
    ],
    "GN-041": [
        "Recursion أسلوب تستدعي فيه الدالة نفسها.", "يفكك Recursion المشكلة إلى نسخ أصغر منها.",
        "يتطلب Recursion حالة أساس Base Case توقف سلسلة الاستدعاءات.",
        "قد يؤدي غياب Base Case إلى Stack Overflow.",
    ],
}
# Egyptian error fragment, faithful MSA claim, and audit description.
ERROR_SPECS: dict[str, dict[str, tuple[str, str, str]]] = {
"DA-004":{"mixed":("بس Missing Values الأحسن نسيبها زي ما هي دايمًا عشان ما نغيّرش الداتا.","يرى المرشح أن Missing Values يجب أن تترك دون معالجة دائمًا. || يرى المرشح أن ترك Missing Values دون معالجة يمنع تغيير البيانات.","يدعي وجوب ترك Missing Values دون معالجة دائمًا."),"misconception":("أنا فاكر يمكن Data Cleaning معناه نمسح أي صف ناقص وخلاص.","يعتقد المرشح على نحو غير مؤكد أن Data Cleaning يعني حذف كل صف ناقص فقط.","يحصر Data Cleaning على نحو غير مؤكد في حذف كل صف ناقص.")},
"DA-010":{"mixed":("وقيم Pearson بتكون من 0 لحد 1 بس.","يدعي المرشح أن قيم Pearson تقع بين 0 و1 فقط.","يقيد مجال Pearson خطأ بين 0 و1."),"misconception":("تقريبًا لو Pearson طلع 0 يبقى مفيش أي علاقة خالص بين المتغيرين.","يعتقد المرشح على نحو غير مؤكد أن قيمة Pearson التي تساوي 0 تعني غياب أي علاقة بين المتغيرين.","يخلط بين غياب العلاقة الخطية وغياب أي علاقة.")},
"DA-020":{"mixed":("و TRUNCATE ينفع معاه WHERE عادي لو عايز صفوف معينة.","يدعي المرشح أن TRUNCATE يقبل شرط WHERE لحذف صفوف محددة.","ينسب دعم WHERE خطأ إلى TRUNCATE."),"misconception":("أنا فاكر إن DROP بيمسح الداتا بس وبيسيب شكل الجدول موجود.","يعتقد المرشح أن DROP يحذف البيانات فقط ويبقي بنية الجدول.","يخلط بين DROP وإفراغ بيانات الجدول.")},
"DA-045":{"mixed":("و Recency معناها عدد مرات الشراء.","يدعي المرشح أن Recency تقيس عدد مرات الشراء.","يخلط بين Recency وFrequency."),"misconception":("على ما أفتكر RFM موديل Machine Learning بيتنبأ بالمبيعات الجاية.","يعتقد المرشح على نحو غير مؤكد أن RFM نموذج Machine Learning. || يعتقد المرشح على نحو غير مؤكد أن RFM يتنبأ بالمبيعات المستقبلية.","يصنف RFM خطأ كنموذج تنبؤ Machine Learning.")},
"DS-007":{"mixed":("بس كل شجر Random Forest لازم يتدرّب على نفس الصفوف ونفس Features بالظبط.","يدعي المرشح أن كل أشجار Random Forest تتدرب على الصفوف نفسها. || يدعي المرشح أن كل أشجار Random Forest تتدرب على Features نفسها.","يلغي العشوائية التي تنوع أشجار Random Forest."),"misconception":("أنا فاكر Random Forest بيختار أحسن Decision Tree واحدة ويرمي الباقي.","يعتقد المرشح أن Random Forest يختار أفضل Decision Tree واحدة. || يعتقد المرشح أن Random Forest يتجاهل بقية الأشجار.","يخلط التجميع باختيار شجرة واحدة.")},
"DS-012":{"mixed":("والـ Features لازم تكون مستقلة من غير ما نعرف الـclass.","يدعي المرشح أن Naive Bayes يفترض استقلال Features دون اشتراط معرفة class.","يحذف شرط الاستقلال المشروط بالفئة."),"misconception":("تقريبًا Naive Bayes ما بيشتغلش غير لو افتراض الاستقلال متحقق مية في المية.","يعتقد المرشح على نحو غير مؤكد أن Naive Bayes لا يعمل إلا إذا تحقق استقلال Features بالكامل.","يجعل افتراض الاستقلال شرط صلاحية مطلقًا.")},
"DS-018":{"mixed":("و L2 Regularization هي اللي بتصفّر Weights كتير وتعمل Feature Selection.","يدعي المرشح أن L2 Regularization تصفر Weights كثيرة. || يدعي المرشح أن L2 Regularization تحقق Feature Selection.","ينسب خاصية L1 إلى L2."),"misconception":("أنا فاكر L1 و L2 Regularization نفس العقوبة بس اسمين مختلفين.","يعتقد المرشح أن L1 و L2 Regularization تستخدمان العقوبة نفسها.","يلغي الفرق بين عقوبتي L1 وL2.")},
"DS-019":{"mixed":("و Feature Engineering ملهاش علاقة بأداء الموديل لو اخترنا Algorithm قوية.","يدعي المرشح أن Feature Engineering لا تؤثر في أداء النموذج عند اختيار Algorithm قوية.","ينفي أثر Feature Engineering على الأداء."),"misconception":("يمكن Feature Engineering معناها نزود Columns عشوائي عشان الموديل يبقى عنده داتا أكتر.","يعتقد المرشح على نحو غير مؤكد أن Feature Engineering يعني إضافة Columns عشوائية. || يعتقد المرشح على نحو غير مؤكد أن إضافة Columns عشوائية تزيد مقدار البيانات.","يخلط هندسة الخصائص بإضافة أعمدة عشوائية.")},
"CS-006":{"mixed":("و AES تشفير Asymmetric بمفتاح Public ومفتاح Private.","يدعي المرشح أن AES خوارزمية Asymmetric. || يدعي المرشح أن AES تستخدم زوج مفاتيح Public وPrivate.","يصنف AES خطأ كتشفير غير متماثل."),"misconception":("على ما أفتكر AES-256 بيعالج Block حجمها 256 bit.","يعتقد المرشح على نحو غير مؤكد أن AES-256 يعالج Block بحجم 256 bit.","يخلط طول مفتاح AES بحجم الكتلة.")},
"CS-037":{"mixed":("و DNSSEC بيمنع الهجوم لأنه بيشفّر كل DNS traffic.","يدعي المرشح أن DNSSEC يمنع DNS Spoofing عبر تشفير كل DNS traffic.","يخلط التوقيع الرقمي في DNSSEC بتشفير النقل."),"misconception":("أنا فاكر DNS Spoofing يعني المهاجم يغيّر IP على جهازه هو بس.","يعتقد المرشح أن DNS Spoofing يغير عنوان IP على جهاز المهاجم فقط.","يخلط تزوير ردود DNS بتغيير إعداد محلي لدى المهاجم.")},
"CS-041":{"mixed":("وأي Digital Certificate بتوقّع نفسها من غير Certificate Authority.","يدعي المرشح أن كل Digital Certificate توقع نفسها دون Certificate Authority.","ينفي دور جهة الإصدار الموثوقة."),"misconception":("تقريبًا PKI هي Algorithm تشفير واحدة زي AES.","يعتقد المرشح على نحو غير مؤكد أن PKI عبارة عن Algorithm تشفير واحدة مثل AES.","يخلط المنظومة الإدارية بخوارزمية تشفير.")},
"CS-049":{"mixed":("و Vulnerability Scanning دايمًا بيستغل الثغرة عشان يثبتها.","يدعي المرشح أن Vulnerability Scanning يستغل الثغرات دائمًا لإثباتها.","ينسب الاستغلال العملي للفحص الآلي."),"misconception":("أنا فاكر Penetration Testing مجرد Scan أوتوماتيك أعمق شوية.","يعتقد المرشح أن Penetration Testing مجرد Scan آلي أعمق قليلًا.","يلغي الجانب اليدوي والاستغلالي في Penetration Testing.")},
"SE-002":{"mixed":("والـ Encapsulation معناه نخلي كل Properties public عشان تبقى سهلة.","يدعي المرشح أن Encapsulation يعني جعل كل Properties public. || يرى المرشح أن جعل Properties public يسهل التعامل معها.","يعكس هدف تقييد الوصول في Encapsulation."),"misconception":("يمكن Encapsulation هو إننا نحط كل Classes في File واحدة.","يعتقد المرشح على نحو غير مؤكد أن Encapsulation يعني وضع كل Classes في File واحدة.","يخلط Encapsulation بتنظيم الملفات.")},
"SE-003":{"mixed":("و Multiple Inheritance معناها الـChild Class ليها Parent Class واحدة بس.","يدعي المرشح أن Multiple Inheritance تعني وراثة Child Class من Parent Class واحدة فقط.","يعكس تعريف Multiple Inheritance."),"misconception":("أنا فاكر Inheritance معناها ننسخ Code الـParent ونلزقه جوه الـChild.","يعتقد المرشح أن Inheritance تعني نسخ Code الصنف Parent ولصقه داخل الصنف Child.","يخلط الوراثة بالنسخ النصي للكود.")},
"SE-006":{"mixed":("و Open/Closed بيقول إن الـcode يبقى مقفول قدام Extension ومفتوح للتعديل.","يدعي المرشح أن Open/Closed يغلق code أمام Extension. || يدعي المرشح أن Open/Closed يفتح code للتعديل المباشر.","يعكس مبدأ Open/Closed."),"misconception":("على ما أفتكر SOLID دي خمس Design Patterns جاهزة بنطبقها بالحرف.","يعتقد المرشح على نحو غير مؤكد أن SOLID خمس Design Patterns جاهزة. || يعتقد المرشح على نحو غير مؤكد أن SOLID تطبق حرفيًا.","يخلط المبادئ بأنماط تصميم جاهزة.")},
"SE-031":{"mixed":("و Refactoring المفروض يغيّر Behavior عشان يضيف Features جديدة.","يدعي المرشح أن Refactoring يجب أن يغير Behavior. || يدعي المرشح أن هدف Refactoring هو إضافة Features جديدة.","يخلط Refactoring بإضافة وظائف تغير السلوك."),"misconception":("أنا فاكر Refactoring يعني نعمل Rewrite كامل للمشروع مرة واحدة.","يعتقد المرشح أن Refactoring يعني Rewrite كاملًا للمشروع دفعة واحدة.","يخلط التحسين التدريجي بإعادة الكتابة الكاملة.")},
"GN-016":{"mixed":("و JSON بيعتمد على Tags فتح وقفل زي XML.","يدعي المرشح أن JSON يعتمد على Tags فتح وإغلاق مثل XML.","ينسب بنية XML إلى JSON."),"misconception":("تقريبًا JSON لغة Programming بنشغّلها على Server.","يعتقد المرشح على نحو غير مؤكد أن JSON لغة Programming. || يعتقد المرشح على نحو غير مؤكد أن JSON تنفذ على Server.","يخلط صيغة تبادل البيانات بلغة برمجة.")},
"GN-017":{"mixed":("و Python لغة Compiled بس ومفيهاش Interpreter.","يدعي المرشح أن Python لغة Compiled فقط ولا تستخدم Interpreter.","ينفي الطبيعة المفسرة لـPython."),"misconception":("أنا فاكر Python انتشرت عشان هي أسرع من C++ في الحسابات الخام.","يعتقد المرشح أن Python انتشرت لأنها أسرع من C++ في الحسابات الخام.","يعكس مقايضة الأداء بين Python وC++.")},
"GN-035":{"mixed":("و AI هو فرع صغير جوه Machine Learning.","يدعي المرشح أن AI فرع صغير داخل Machine Learning.","يعكس العلاقة التضمينية بين AI وMachine Learning."),"misconception":("يمكن أي AI لازم يكون Deep Learning وإلا ما يبقاش AI.","يعتقد المرشح على نحو غير مؤكد أن كل AI يجب أن يكون Deep Learning.","يحصر AI في Deep Learning.")},
"GN-041":{"mixed":("و Recursion مش محتاج Base Case لأن الـfunction هتقف لوحدها.","يدعي المرشح أن Recursion لا يحتاج Base Case. || يدعي المرشح أن function العودية تتوقف تلقائيًا.","ينفي الشرط الأساسي لإيقاف Recursion."),"misconception":("أنا فاكر Recursion يعني نكرر Loop من غير ما الـfunction تنادي نفسها.","يعتقد المرشح أن Recursion يعني تكرار Loop دون استدعاء function لنفسها.","يخلط Recursion بالتكرار الحلقي فقط.")},
}

_LATIN_RE = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:\.[A-Za-z0-9]+)*(?:\+\+|#)?(?:[/_-][A-Za-z0-9]+)*")
_SECRET_VALUE_RE = re.compile(r"(?:AIza[0-9A-Za-z_-]{20,}|sk-[0-9A-Za-z_-]{16,})")

class PilotGenerationError(RuntimeError):
    """Fail-safe wrapper for provider/API failures."""

class GenerationProvider(Protocol):
    name: str
    model: str
    def generate_answers(self, document: dict[str, Any], terms: list[str]) -> tuple[dict[str, Any], Any]:
        qid = document["question_id"]
        facts = CORRECT_CLAIMS[qid]
        errors = ERROR_SPECS[qid]

        def error_claims(spec: tuple[str, str, str]) -> list[str]:
            return [part.strip() for part in spec[1].split(" || ")]

        cases = [
            ("complete_correct", "بص، " + " ".join(_egyptianize(c) + "." for c in facts), [], facts),
            ("short_partial", "باختصار، " + _egyptianize(facts[0]) + ".", [], facts[:1]),
            ("mixed_correctness", " ".join(_egyptianize(c) + "." for c in facts[:2]) + " " + errors["mixed"][0], [errors["mixed"][2]], [*facts[:2], *error_claims(errors["mixed"])]),
            ("plausible_misconception", errors["misconception"][0], [errors["misconception"][2]], error_claims(errors["misconception"])),
            ("natural_egyptian_spoken", "يعني هو... قصدي الفكرة إن " + _egyptianize(facts[0]) + "، وآه كمان " + _egyptianize(facts[1]) + ".", [], facts[:2]),
        ]
        payload_cases = []
        for case_type, answer, intended_errors, claims in cases:
            self._claims_by_answer[answer] = list(claims)
            payload_cases.append({"case_type": case_type, "answer_original": answer, "intended_errors": intended_errors})
        payload = {"question_id": qid, "cases": payload_cases}
        return payload, {"provider": self.name, "model": self.model, "response": payload}

    def extract_claims(self, answer: str) -> tuple[list[str], Any]: ...
    def audit_case(self, case_type: str, answer: str, claims: list[str]) -> tuple[dict[str, Any], Any]: ...
def extract_latin_terms(text: str) -> list[str]:
    """Return unique Latin spans in first-seen order without normalization."""
    return list(dict.fromkeys(m.group(0).strip() for m in _LATIN_RE.finditer(text)))

def _egyptianize(claim: str) -> str:
    text = claim.rstrip(".")
    replacements = (
        (" هو إجراء "," عبارة عن خطوة "),(" هو نموذج "," عبارة عن موديل "),(" هو تحسين "," معناه تحسين "),
        ("يقيس ","بيقيس "),("تقيس ","بتقيس "),("تتراوح ","بتتراوح "),
        ("تشير ","بتدل "),("تعالج ","بتعالج "),("تزيل ","بتشيل "),
        ("تضيف ","بتضيف "),("يحذف ","بيمسح "),("يمكن ","ممكن "),
        ("يبقي ","بيسيب "),("لا يقبل ","ما بيقبلش "),("يقسم ","بيقسم "),
        ("تستخدم ","بتستخدم "),("يستخدم ","بيستخدم "),("يختار ","بيختار "),
        ("يفترض ","بيفترض "),("يوصف ","بيتقال عليه "),("يجمع ","بيجمع "),
        ("تتدرب ","بتتدرب "),("يقلل ","بيقلل "),("يحد ","بيحد "),
        ("يهدف ","هدفه "),("تحدد ","بتحدد "),("يتطلب ","بيحتاج "),
        ("تدعم ","بتدعم "),("يزور ","بيزوّر "),("يوجه ","بيوجّه "),
        ("تربط ","بتربط "),("توقع ","بتمضي "),("تتحقق ","بنتأكد من "),
        ("يقيد ","بيقيّد "),("تتيح ","بتتيح "),("يحمي ","بيحمي "),
        ("تمثل ","بتمثل "),("تعني ","معناها "),("ينص Single Responsibility على أن ","مبدأ Single Responsibility بيقول إن "),("ينص Open/Closed على أن ","مبدأ Open/Closed بيقول إن "),("ينص Liskov Substitution على ","مبدأ Liskov Substitution بيقول إن "),("ينص Dependency Inversion على ","مبدأ Dependency Inversion بيقول إن "),("ينص ","بيقول "),
        ("يفضل ","بيفضّل "),("يرفع ","بيرفع "),("تحتاج ","بتحتاج "),
        ("يعتمد ","بيعتمد "),("أصبح ","بقى "),("تتميز ","بتتميز "),
        ("تملك ","عندها "),("ساعدت ","اللي ساعد هو "),("يحتوي ","جواه "),
        ("يفكك ","بيفكك "),("قد يؤدي غياب Base Case إلى ","غياب Base Case ممكن يعمل "),("قد تؤدي ","ممكن تسبب "),
    )
    for source, target in replacements:
        text = text.replace(source, target)
    return text

def simulate_asr(answer: str, case_number: int) -> tuple[str, list[str]]:
    """Limited text-only ASR simulation that preserves Latin spans."""
    text, events = answer, []
    if "،" in text or re.search(r"\.(?=\s|$)", text):
        text = text.replace("،", "")
        text = re.sub(r"\.(?=\s|$)", "", text)
        events.append("punctuation_removed")
    if case_number in {1, 4, 5}:
        normalized = text.translate(str.maketrans({"أ":"ا","إ":"ا","آ":"ا","ؤ":"و","ئ":"ي"}))
        if normalized != text:
            text = normalized
            events.append("hamza_normalized")
    if case_number in {3, 5}:
        stripped = re.sub(r"^(?:بص|باختصار|يعني)\s*", "", text).strip()
        if stripped != text:
            text = stripped
            events.append("filler_removed")
    if case_number == 4:
        repeated = re.sub(r"^انا\s+", "انا انا ", text, count=1)
        if repeated != text:
            text = repeated
            events.append("short_repetition")
    return re.sub(r"\s+", " ", text).strip(), events

def _char_ngrams(text: str, n: int = 3) -> set[str]:
    normalized = re.sub(r"\s+", " ", text.strip().lower())
    return {normalized[i:i+n] for i in range(max(0, len(normalized)-n+1))}

def text_similarity(left: str, right: str) -> float:
    a, b = _char_ngrams(left), _char_ngrams(right)
    return len(a & b) / len(a | b) if a or b else 1.0

def _quantile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    position = (len(ordered)-1)*q
    low, high = math.floor(position), math.ceil(position)
    if low == high: return ordered[low]
    return ordered[low]*(high-position)+ordered[high]*(position-low)

class LocalDeterministicProvider:
    """Offline synthetic provider; it does not impersonate human candidates."""
    name = "local_deterministic"
    model = "reference_grounded_case_builder_v1"
    def __init__(self) -> None:
        self._claims_by_answer: dict[str, list[str]] = {}
    def generate_answers(self, document: dict[str, Any], terms: list[str]) -> tuple[dict[str, Any], Any]:
        qid = document["question_id"]
        facts = CORRECT_CLAIMS[qid]
        errors = ERROR_SPECS[qid]

        def error_claims(spec: tuple[str, str, str]) -> list[str]:
            return [part.strip() for part in spec[1].split(" || ")]

        cases = [
            ("complete_correct", "بص، " + " ".join(_egyptianize(c) + "." for c in facts), [], facts),
            ("short_partial", "باختصار، " + _egyptianize(facts[0]) + ".", [], facts[:1]),
            ("mixed_correctness", " ".join(_egyptianize(c) + "." for c in facts[:2]) + " " + errors["mixed"][0], [errors["mixed"][2]], [*facts[:2], *error_claims(errors["mixed"])]),
            ("plausible_misconception", errors["misconception"][0], [errors["misconception"][2]], error_claims(errors["misconception"])),
            ("natural_egyptian_spoken", "يعني هو... قصدي الفكرة إن " + _egyptianize(facts[0]) + "، وآه كمان " + _egyptianize(facts[1]) + ".", [], facts[:2]),
        ]
        payload_cases = []
        for case_type, answer, intended_errors, claims in cases:
            self._claims_by_answer[answer] = list(claims)
            payload_cases.append({"case_type": case_type, "answer_original": answer, "intended_errors": intended_errors})
        payload = {"question_id": qid, "cases": payload_cases}
        return payload, {"provider": self.name, "model": self.model, "response": payload}

    def extract_claims(self, answer: str) -> tuple[list[str], Any]:
        if answer not in self._claims_by_answer:
            raise PilotGenerationError("Local provider has no exact answer-to-claims mapping")
        claims = list(self._claims_by_answer[answer])
        return claims, {"provider":"local_claim_extractor_v1","response":{"claims":claims}}
    def audit_case(self, case_type: str, answer: str, claims: list[str]) -> tuple[dict[str, Any], Any]:
        expected = self._claims_by_answer.get(answer, [])
        claim_text = "\n".join(claims)
        unsupported = [c for c in claims if c not in expected]
        missing = [c for c in expected if c not in claims]
        term_loss = [term for term in extract_latin_terms(answer) if term not in claim_text]
        duplicates = sorted(c for c,n in Counter(claims).items() if n>1)
        error_marked = any(x in claim_text for x in ("يدعي المرشح", "يعتقد المرشح", "يرى المرشح"))
        case_compliance = {
            "complete_correct": len(claims) >= 4,
            "short_partial": len(claims) == 1,
            "mixed_correctness": len(claims) >= 3 and error_marked,
            "plausible_misconception": 1 <= len(claims) <= 2 and error_marked,
            "natural_egyptian_spoken": len(claims) == 2 and "قصدي" in answer,
        }.get(case_type, False)
        findings = {
            "unsupported_additions": unsupported,
            "missing_propositions": missing,
            "atomicity_pass": all("؛" not in c and " || " not in c for c in claims),
            "self_containment_pass": all(len(c.split()) >= 3 for c in claims),
            "term_preservation_pass": not term_loss,
            "term_loss": term_loss,
            "repetition": duplicates,
            "case_type_compliance": case_compliance,
        }
        findings["pass"] = not unsupported and not missing and findings["atomicity_pass"] and findings["self_containment_pass"] and findings["term_preservation_pass"] and not duplicates and findings["case_type_compliance"]
        return findings, {"provider":"deterministic_rule_auditor_v1","response":findings}

class GeminiProvider:
    """Replaceable JSON provider. The environment key is never serialized."""
    name = "gemini"
    def __init__(self, model: str = "gemini-2.5-flash") -> None:
        self.model, self._api_key = model, os.environ.get("GEMINI_API_KEY","")
        if not self._api_key: raise PilotGenerationError("GEMINI_API_KEY is required for provider=gemini")
    def _request(self, prompt: str) -> tuple[Any, Any]:
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self._api_key}"
        body = json.dumps({"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"responseMimeType":"application/json","temperature":0.7}}).encode()
        request = urllib.request.Request(endpoint,data=body,headers={"Content-Type":"application/json"})
        try:
            with urllib.request.urlopen(request,timeout=120) as response: raw=json.loads(response.read().decode())
            text=raw["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(text), raw
        except (urllib.error.URLError,TimeoutError,json.JSONDecodeError,KeyError,IndexError,TypeError) as exc:
            raise PilotGenerationError(f"Gemini API failed safely: {type(exc).__name__}") from exc
    def generate_answers(self, document: dict[str, Any], terms: list[str]) -> tuple[dict[str, Any], Any]:
        qid = document["question_id"]
        facts = CORRECT_CLAIMS[qid]
        errors = ERROR_SPECS[qid]

        def error_claims(spec: tuple[str, str, str]) -> list[str]:
            return [part.strip() for part in spec[1].split(" || ")]

        cases = [
            ("complete_correct", "بص، " + " ".join(_egyptianize(c) + "." for c in facts), [], facts),
            ("short_partial", "باختصار، " + _egyptianize(facts[0]) + ".", [], facts[:1]),
            ("mixed_correctness", " ".join(_egyptianize(c) + "." for c in facts[:2]) + " " + errors["mixed"][0], [errors["mixed"][2]], [*facts[:2], *error_claims(errors["mixed"])]),
            ("plausible_misconception", errors["misconception"][0], [errors["misconception"][2]], error_claims(errors["misconception"])),
            ("natural_egyptian_spoken", "يعني هو... قصدي الفكرة إن " + _egyptianize(facts[0]) + "، وآه كمان " + _egyptianize(facts[1]) + ".", [], facts[:2]),
        ]
        payload_cases = []
        for case_type, answer, intended_errors, claims in cases:
            self._claims_by_answer[answer] = list(claims)
            payload_cases.append({"case_type": case_type, "answer_original": answer, "intended_errors": intended_errors})
        payload = {"question_id": qid, "cases": payload_cases}
        return payload, {"provider": self.name, "model": self.model, "response": payload}

    def extract_claims(self, answer: str) -> tuple[list[str], Any]:
        payload,raw=self._request(CLAIM_EXTRACTION_PROMPT_V1+"\nANSWER:\n"+answer)
        claims=payload.get("claims",payload) if isinstance(payload,dict) else payload
        if not isinstance(claims,list) or not all(isinstance(c,str) for c in claims): raise PilotGenerationError("Claim response is not a JSON string list")
        return claims,raw
    def audit_case(self, case_type: str, answer: str, claims: list[str]) -> tuple[dict[str, Any], Any]:
        payload,raw=self._request(CLAIM_AUDIT_PROMPT_V1+"\nINPUT:\n"+json.dumps({"case_type":case_type,"answer":answer,"claims":claims},ensure_ascii=False))
        if not isinstance(payload,dict): raise PilotGenerationError("Audit response is not a JSON object")
        return payload,raw

def load_project_inputs(repo_root: Path) -> tuple[list[dict[str, Any]],list[dict[str, Any]]]:
    questions=json.loads((repo_root/QUESTIONS_RELATIVE_PATH).read_text(encoding="utf-8"))["questions"]
    documents=json.loads((repo_root/REFERENCE_RELATIVE_PATH).read_text(encoding="utf-8"))["documents"]
    return questions,documents

def parse_o9_question_ids(repo_root: Path) -> set[str]:
    return set(re.findall(r"^###\s+([A-Z]{2}-\d{3})\b",(repo_root/O9_RELATIVE_PATH).read_text(encoding="utf-8"),flags=re.MULTILINE))

def select_question_ids(questions: list[dict[str,Any]],o9_ids: set[str],seed: int=42) -> list[str]:
    rng,selected=random.Random(seed),[]
    for track in TRACKS:
        eligible=sorted(q["question_id"] for q in questions if q["track"]==track and q["question_id"] not in o9_ids and q["question_id"]!="GN-050")
        if len(eligible)<4: raise ValueError(f"Track {track} has fewer than four eligible questions")
        selected.extend(sorted(rng.sample(eligible,4)))
    return selected

def sha256_file(path: Path) -> str:
    digest=hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda:handle.read(1024*1024),b""): digest.update(chunk)
    return digest.hexdigest()

def snapshot_existing_results(results_root: Path,output_dir: Path) -> dict[str,str]:
    snapshot={}
    for path in sorted(p for p in results_root.rglob("*") if p.is_file()):
        try: path.resolve().relative_to(output_dir.resolve()); continue
        except ValueError: pass
        snapshot[path.relative_to(results_root).as_posix()]=sha256_file(path)
    return snapshot

def assert_snapshot_unchanged(results_root: Path,output_dir: Path,before: dict[str,str]) -> None:
    after=snapshot_existing_results(results_root,output_dir)
    if after!=before:
        changed=sorted(set(before)^set(after)|{k for k in before.keys()&after.keys() if before[k]!=after[k]})
        raise ValueError(f"Existing results files changed during pilot build: {changed}")

def _write_json(path: Path,payload: Any) -> None:
    path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def _append_jsonl(path: Path,payload: Any) -> None:
    with path.open("a",encoding="utf-8",newline="\n") as handle: handle.write(json.dumps(payload,ensure_ascii=False)+"\n")
def _read_jsonl_by_key(path: Path,key: str) -> dict[str,dict[str,Any]]:
    if not path.exists(): return {}
    return {row[key]:row for row in (json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip())}
def _provider_from_name(name: str,model: str|None=None) -> GenerationProvider:
    if name=="local": return LocalDeterministicProvider()
    if name=="gemini": return GeminiProvider(model or os.environ.get("GEMINI_MODEL","gemini-2.5-flash"))
    raise ValueError(f"Unknown provider: {name}")
def _similarity_distribution(records: list[dict[str,Any]]) -> tuple[dict[str,float],float]:
    grouped: dict[str,list[str]]=defaultdict(list)
    for record in records: grouped[record["question_id"]].append(record["answer_original"])
    scores=[text_similarity(a[i],a[j]) for a in grouped.values() for i in range(len(a)) for j in range(i+1,len(a))]
    median=statistics.median(scores); mad=statistics.median(abs(x-median) for x in scores)
    threshold=min(1.0,median+3*mad)
    distribution={"count":len(scores),"min":min(scores),"p25":_quantile(scores,.25),"median":median,"p75":_quantile(scores,.75),"p95":_quantile(scores,.95),"max":max(scores),"mad":mad}
    return {k:round(v,6) if isinstance(v,float) else v for k,v in distribution.items()},round(threshold,6)

def validate_records(records: list[dict[str,Any]],o9_ids: set[str],similarity_threshold: float) -> dict[str,Any]:
    errors=[]; ids=[r.get("answer_case_id") for r in records]
    if len(ids)!=len(set(ids)): errors.append("duplicate answer_case_id")
    if len(records)!=100: errors.append(f"expected 100 records, found {len(records)}")
    grouped: dict[str,list[dict[str,Any]]]=defaultdict(list)
    for record in records:
        grouped[record.get("question_id","")].append(record)
        qid,case_id=record.get("question_id"),record.get("answer_case_id")
        if qid=="GN-050": errors.append("GN-050 present")
        if qid in o9_ids: errors.append(f"O9 question present: {qid}")
        if record.get("review_status")!=REVIEW_STATUS: errors.append(f"invalid review_status: {case_id}")
        claims=record.get("claims")
        if not isinstance(claims,list) or not claims or not all(isinstance(c,str) and c.strip() for c in claims): errors.append(f"invalid claims list: {case_id}")
        if any(key in record for key in ("split","training_split","validation_split")): errors.append(f"automatic split field present: {case_id}")
        original_terms=extract_latin_terms(record.get("answer_original","")); asr=record.get("answer_asr_simulated","")
        missing_asr=[term for term in original_terms if term not in asr]
        if missing_asr: errors.append(f"Latin term lost in ASR: {case_id} {missing_asr}")
        missing_claims=[term for term in record.get("latin_terms_in_answer",[]) if term not in "\n".join(claims or [])]
        if missing_claims: errors.append(f"Latin term lost in claims: {case_id} {missing_claims}")
    if len(grouped)!=20: errors.append(f"expected 20 question IDs, found {len(grouped)}")
    for qid,cases in grouped.items():
        if len(cases)!=5: errors.append(f"{qid} has {len(cases)} cases")
        if Counter(c["case_type"] for c in cases)!=Counter(CASE_TYPES): errors.append(f"{qid} case types incomplete")
        answers=[c["answer_original"].strip() for c in cases]
        if len(answers)!=len(set(answers)): errors.append(f"duplicate exact answer within {qid}")
    track_qids: dict[str,set[str]]=defaultdict(set)
    for record in records: track_qids[record.get("track","")].add(record.get("question_id", ""))
    if {t:len(track_qids[t]) for t in TRACKS}!={t:4 for t in TRACKS}: errors.append("track balance is not four question IDs each")
    near=[]; paraphrase_only=[]
    for qid,cases in sorted(grouped.items()):
        ordered=sorted(cases,key=lambda x:x["answer_case_id"]); scores=[]
        for i in range(len(ordered)):
            for j in range(i+1,len(ordered)):
                score=text_similarity(ordered[i]["answer_original"],ordered[j]["answer_original"]); scores.append(score)
                if score>=similarity_threshold: near.append({"question_id":qid,"left":ordered[i]["answer_case_id"],"right":ordered[j]["answer_case_id"],"similarity":round(score,6)})
        if scores and min(scores)>=similarity_threshold: paraphrase_only.append(qid)
    if paraphrase_only: errors.append(f"all cases near-paraphrases: {paraphrase_only}")
    if errors: raise ValueError("Pilot validation failed: "+"; ".join(dict.fromkeys(errors)))
    return {"near_duplicate_pairs":near}

def _scan_for_secrets(output_dir: Path) -> list[str]:
    hits=[]
    for path in output_dir.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".json",".jsonl",".md",".txt"} and _SECRET_VALUE_RE.search(path.read_text(encoding="utf-8")):
            hits.append(path.relative_to(output_dir).as_posix())
    return hits

def build_pilot(repo_root: Path,output_dir: Path,provider_name: str="local",model: str|None=None,seed: int=42,resume: bool=True) -> dict[str,Any]:
    repo_root,output_dir=repo_root.resolve(),output_dir.resolve(); output_dir.mkdir(parents=True,exist_ok=True)
    raw_dir=output_dir/"raw_responses"; raw_dir.mkdir(exist_ok=True)
    results_root=repo_root/"results"; protected_before=snapshot_existing_results(results_root,output_dir)
    questions,documents=load_project_inputs(repo_root); o9_ids=parse_o9_question_ids(repo_root)
    selected_ids=select_question_ids(questions,o9_ids,seed); docs_by_id={d["question_id"]:d for d in documents}; selected_docs=[docs_by_id[q] for q in selected_ids]
    provider=_provider_from_name(provider_name,model)
    paths=[raw_dir/"pass1_answers.jsonl",raw_dir/"pass2_claims.jsonl",raw_dir/"pass3_audits.jsonl"]
    if not resume:
        for path in paths:
            if path.exists(): path.unlink()
    pass1=_read_jsonl_by_key(paths[0],"question_id"); pass2=_read_jsonl_by_key(paths[1],"answer_case_id"); pass3=_read_jsonl_by_key(paths[2],"answer_case_id")
    # PASS 1: answers only. Local re-generation during resume primes its exact answer map.
    for document in selected_docs:
        terms=extract_latin_terms(document["question"]+"\n"+"\n".join(c["text"] for c in document["chunks"]))
        try: payload,raw=provider.generate_answers(document,terms)
        except Exception as exc: raise PilotGenerationError(f"PASS 1 failed safely for {document['question_id']}: {exc}") from exc
        if document["question_id"] not in pass1:
            row={"question_id":document["question_id"],"status":REVIEW_STATUS,"prompt_version":PROMPT_VERSION,"payload":payload,"raw_response":raw}; _append_jsonl(paths[0],row); pass1[document["question_id"]]=row
    intermediate=[]
    # PASS 2: receives only one answer, never a reference.
    for document in selected_docs:
        cases=pass1[document["question_id"]]["payload"]["cases"]
        if [c["case_type"] for c in cases]!=list(CASE_TYPES): raise PilotGenerationError(f"PASS 1 schema invalid for {document['question_id']}")
        for number,case in enumerate(cases,1):
            case_id=f"{document['question_id']}-A{number:02d}"
            if case_id not in pass2:
                try: claims,raw=provider.extract_claims(case["answer_original"])
                except Exception as exc: raise PilotGenerationError(f"PASS 2 failed safely for {case_id}: {exc}") from exc
                row={"answer_case_id":case_id,"status":REVIEW_STATUS,"prompt_version":CLAIM_PROMPT_VERSION,"claims":claims,"raw_response":raw}; _append_jsonl(paths[1],row); pass2[case_id]=row
            answer_asr,events=simulate_asr(case["answer_original"],number)
            intermediate.append({"document":document,"number":number,"answer_case_id":case_id,"case":case,"claims":pass2[case_id]["claims"],"answer_asr_simulated":answer_asr,"asr_simulation_events":events})
    # PASS 3: separate append-only response.
    for item in intermediate:
        case_id=item["answer_case_id"]
        if case_id not in pass3:
            try: findings,raw=provider.audit_case(item["case"]["case_type"],item["case"]["answer_original"],item["claims"])
            except Exception as exc: raise PilotGenerationError(f"PASS 3 failed safely for {case_id}: {exc}") from exc
            row={"answer_case_id":case_id,"status":REVIEW_STATUS,"prompt_version":AUDIT_PROMPT_VERSION,"findings":findings,"raw_response":raw}; _append_jsonl(paths[2],row); pass3[case_id]=row
    source=GenerationSource(provider=provider.name,model=provider.model,prompt_version=PROMPT_VERSION,generated_at=DETERMINISTIC_GENERATED_AT)
    records=[]
    for item in intermediate:
        case,claims=item["case"],item["claims"]
        records.append(PilotAnswerCase(
            question_id=item["document"]["question_id"],track=item["document"]["track"],question_text=item["document"]["question"],reference_source=REFERENCE_RELATIVE_PATH,
            answer_case_id=item["answer_case_id"],case_type=case["case_type"],generation_source=source,
            answer_original=case["answer_original"],answer_asr_simulated=item["answer_asr_simulated"],asr_simulation_events=item["asr_simulation_events"],claims=claims,
            latin_terms_in_answer=extract_latin_terms(case["answer_original"]),latin_terms_in_claims=extract_latin_terms("\n".join(claims)),intended_errors=case.get("intended_errors",[]),
        ).to_dict())
    distribution,threshold=_similarity_distribution(records); validation=validate_records(records,o9_ids,threshold)
    record_ids={r["answer_case_id"] for r in records}; failed=[case_id for case_id,row in pass3.items() if case_id in record_ids and not row["findings"].get("pass",False)]
    if failed: raise ValueError(f"Independent audit failed for cases: {failed}")
    corpus_path=output_dir/"pilot_corpus_v2_DRAFT_UNREVIEWED.jsonl"
    corpus_path.write_text("".join(json.dumps(r,ensure_ascii=False)+"\n" for r in records),encoding="utf-8",newline="\n")
    _write_json(output_dir/"selected_question_ids.json",{"status":REVIEW_STATUS,"seed":seed,"question_ids":selected_ids,"by_track":{t:[q for q in selected_ids if q.startswith(t+"-")] for t in TRACKS}})
    selected_manifest=[]
    for document in selected_docs:
        ref_text="\n".join(c["text"] for c in document["chunks"])
        selected_manifest.append({"question_id":document["question_id"],"track":document["track"],"question_text":document["question"],"reference_source":REFERENCE_RELATIVE_PATH,"reference_chunk_ids":[c["chunk_id"] for c in document["chunks"]],"latin_terms_supplied_to_answer_generator":extract_latin_terms(document["question"]+"\n"+ref_text)})
    manifest={
        "status":REVIEW_STATUS,"training_approved":False,"schema_version":"decomposition_corpus_v2_pilot/1.0","seed":seed,
        "selection_algorithm":"single random.Random(seed), sorted eligible IDs, sequential TRACKS order, sample 4 per track",
        "provider":{"name":provider.name,"model":provider.model,"api_key_environment_variable":"GEMINI_API_KEY"},
        "source_files":{QUESTIONS_RELATIVE_PATH:sha256_file(repo_root/QUESTIONS_RELATIVE_PATH),REFERENCE_RELATIVE_PATH:sha256_file(repo_root/REFERENCE_RELATIVE_PATH)},
        "o9_policy":{"held_out_at_question_id":True,"question_ids":sorted(o9_ids),"used":False},"excluded_question_ids":["GN-050"],
        "selected_questions":selected_manifest,"case_types":list(CASE_TYPES),"canonical_answer_cases":len(records),
        "asr_variant_policy":"paired fields in one canonical case; answer_asr_simulated is text-only",
        "target_rendering_decision":"OPEN_FOR_THIS_PILOT; claims JSON list is authoritative; parser/trainer unchanged",
        "automatic_splits_created":False,
        "similarity":{"metric":"character_trigram_jaccard","distribution_before_threshold":distribution,"threshold_method":"median_plus_3_MAD_clipped_at_1.0","threshold":threshold},
        "known_source_warning":"SE-006 was selected deterministically; Q2 flags its key_points count as a reference-document anomaly. The source was not modified.",
        "protected_existing_results_snapshot_count":len(protected_before),
    }
    _write_json(output_dir/"pilot_corpus_v2_manifest.json",manifest)
    for filename,content in {"generation_prompt_v1.md":GENERATION_PROMPT_V1,"claim_extraction_prompt_v1.md":CLAIM_EXTRACTION_PROMPT_V1,"claim_audit_prompt_v1.md":CLAIM_AUDIT_PROMPT_V1}.items():
        (output_dir/filename).write_text(content.rstrip()+"\n",encoding="utf-8")
    claim_counts=[len(r["claims"]) for r in records]; case_counts=Counter(r["case_type"] for r in records); track_counts=Counter(r["track"] for r in records)
    latin_answers=sum(len(r["latin_terms_in_answer"]) for r in records); latin_claims=sum(len(r["latin_terms_in_claims"]) for r in records)
    term_corruptions=sum(len(pass3[r["answer_case_id"]]["findings"].get("term_loss",[])) for r in records)
    grouped=defaultdict(list)
    for record in records: grouped[record["question_id"]].append(record)
    exact_duplicates=sum(len(items)-len({item["answer_original"] for item in items}) for items in grouped.values())
    audit={
        "status":REVIEW_STATUS,"verdict":"DATASET GENERATION PIPELINE PASS","not_training_approved":True,"record_count":len(records),"question_id_count":len(set(r["question_id"] for r in records)),
        "counts_by_track":dict(sorted(track_counts.items())),"counts_by_case_type":dict(sorted(case_counts.items())),
        "claims":{"total":sum(claim_counts),"min":min(claim_counts),"max":max(claim_counts),"mean":round(statistics.mean(claim_counts),3),"distribution":dict(sorted(Counter(claim_counts).items()))},
        "latin_terms":{"answer_unique_per_case_occurrences":latin_answers,"claim_unique_per_case_occurrences":latin_claims},
        "term_corruption_count":term_corruptions,"exact_duplicate_answer_count":exact_duplicates,"near_duplicate_pair_count":len(validation["near_duplicate_pairs"]),"near_duplicate_pairs":validation["near_duplicate_pairs"],
        "similarity":manifest["similarity"],"independent_audit_failed_cases":failed,"claims_variant_contract":"one canonical JSON claims list shared by answer_original and answer_asr_simulated",
        "secret_scan_hits":[],"automatic_splits_created":False,"existing_results_unchanged":True,
        "limitations":["All records remain DRAFT_UNREVIEWED and have not received human review.","The local provider creates synthetic candidate-answer cases; they are not human answers.","answer_asr_simulated is text corruption without audio or transcript alignment.","The rule audit is not an independent human annotation study.","Target rendering remains open; claims lists are authoritative."],
    }
    _write_json(output_dir/"pilot_corpus_v2_audit.json",audit)
    (output_dir/"pilot_corpus_v2_audit.md").write_text(f"""# Decomposition Corpus v2 Pilot Audit\n\nStatus: **{REVIEW_STATUS} / NOT TRAINING-APPROVED**\n\nVerdict: **DATASET GENERATION PIPELINE PASS**\n\n- Canonical answer cases: {len(records)}\n- Question IDs: {len(selected_ids)}\n- Counts by track: {dict(sorted(track_counts.items()))}\n- Counts by case type: {dict(sorted(case_counts.items()))}\n- Claims: total={sum(claim_counts)}, min={min(claim_counts)}, max={max(claim_counts)}, mean={statistics.mean(claim_counts):.3f}\n- Latin-term occurrences: answers={latin_answers}, claims={latin_claims}\n- Term corruptions: {term_corruptions}\n- Exact duplicates: {exact_duplicates}\n- Near-duplicate pairs at distribution-derived threshold {threshold}: {len(validation['near_duplicate_pairs'])}\n- O9 used: no; GN-050 used: no; automatic split: no\n\nThe threshold was calculated after the distribution stored in the manifest. SE-006 is a documented source warning. This pilot is synthetic, unreviewed, and not approved for training.\n""",encoding="utf-8")
    (output_dir/"README.md").write_text("""# Decomposition Corpus v2 Pilot\n\nA 100-case synthetic Dataset Engineering pilot. Every record is `DRAFT_UNREVIEWED`; nothing is human-reviewed or training-approved. `answer_asr_simulated` is paired text-only simulation, never a real or aligned transcript.\n\nRun `python scripts/generate_decomposition_pilot_v2.py --provider local`. `--provider gemini` requires `GEMINI_API_KEY`. Raw pass responses support safe resume. Claims are authoritative JSON lists; no rendered target or automatic split is created.\n""",encoding="utf-8")
    audit["secret_scan_hits"]=_scan_for_secrets(output_dir)
    if audit["secret_scan_hits"]: raise ValueError(f"Secret-like values found: {audit['secret_scan_hits']}")
    _write_json(output_dir/"pilot_corpus_v2_audit.json",audit)
    assert_snapshot_unchanged(results_root,output_dir,protected_before)
    return audit

def load_pilot_jsonl(path: Path) -> list[dict[str,Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]