## Executive Summary – Semantic Guardian (المصحح الذكي للأخطاء المنطقية)

### 1. Problem Statement (بيان المشكلة)

**English**  
Field survey data in Saudi Arabia often contains logical and semantic inconsistencies (for example: job title contradicting education level or reported income, unrealistic combinations of age, marital status, and number of children). These errors reduce data quality, delay analysis, and require costly manual cleaning after collection. Traditional validation rules (required fields, numeric ranges, simple skip logic) are too rigid and cannot capture nuanced, cross-field contradictions.

**العربية**  
تعاني بيانات الاستبيانات الميدانية في المملكة من وجود أخطاء منطقية وتعارضات دلالية بين الإجابات (مثل تعارض المسمى الوظيفي مع المؤهل العلمي أو الدخل المصرَّح به، أو عدم منطقية العلاقة بين العمر والحالة الاجتماعية وعدد الأطفال). هذه الأخطاء تقلّل من جودة البيانات، وتؤخِّر التحليل، وتفرض عبئًا كبيرًا على فرق العمل في مرحلة التنقية اليدوية. أدوات التحقق التقليدية (مثل الحقول الإلزامية والمدى العددي البسيط) تظل جامدة وغير قادرة على كشف التناقضات السياقية المعقدة.

---

### 2. Solution Overview (وصف الحل المقترح)

**English**  
Semantic Guardian is an **intelligent validation assistant** that acts as a “semantic gatekeeper” for survey platforms. It combines deterministic rules with a Large Language Model (LLM) to:
- Evaluate each response in real time while the enumerator is filling the form.
- Detect logical and semantic inconsistencies across multiple fields (age, job title, education, income, etc.).
- Assign a **confidence score** (0–100) to each submission and provide clear, human-readable explanations and suggested corrections.

The solution is delivered as a **pluggable API + live UI** that can be integrated with existing survey systems (e.g., web forms, tablet apps, or low-code platforms).

**العربية**  
«حارس البيانات الدلالي» هو **مساعد ذكي للتحقق من الاستجابات** يعمل كـ«بوابة حارسة» أمام منصات الاستبيانات. يجمع بين قواعد منطقية ثابتة ونموذج لغوي كبير (LLM) من أجل:
- تقييم كل استجابة لحظيًّا أثناء تعبئة الاستبيان من قبل الباحث أو المشارك.
- اكتشاف التناقضات المنطقية والدلالية بين الحقول المتعددة (العمر، المسمى الوظيفي، المؤهل، الدخل، الحالة الاجتماعية، إلخ).
- منح كل استمارة **درجة ثقة** من 0 إلى 100، مع شرح مبسَّط وواضح للأخطاء المقترَحة وكيف يمكن تصحيحها.

يُقدَّم الحل في صورة **واجهة برمجية (API) + واجهة تفاعلية حية** يمكن ربطها بسهولة مع منصات الاستبيانات القائمة (نماذج ويب، تطبيقات لوحية، أو منصات منخفضة الكود).

---

### 3. Technical Methodology (المنهجية التقنية)

**English**  
Our approach follows the hackathon’s recommended methodology:

- **Hybrid engine (Rules + LLM):**  
  - Rule-based validator encodes domain knowledge and Saudi-specific heuristics (e.g., typical income bands for students vs. senior managers, unemployment with high income, age vs. experience, age vs. children).  
  - LLM-based semantic validator (via OpenAI API) uses few-shot prompting to reason about nuanced, cross-field contradictions and contextual plausibility.

- **Few-Shot Prompting & Saudi context:**  
  - Carefully engineered system prompt that explains the Saudi labour market context and common field scenarios.  
  - Few-shot examples (in Arabic and English) show the LLM how to flag clearly implausible combinations while avoiding over-flagging edge cases.

- **Real-time integration with survey flow:**  
  - Backend implemented as a **FastAPI** service exposing endpoints `/validate` and `/batch-validate`.  
  - Frontend demo implemented with **Streamlit**, providing a live form where changes are validated on demand and visual feedback is given immediately.  
  - The same API can be called from survey platforms or low-code tools (e.g., KNIME) via simple HTTP requests.

**العربية**  
تعتمد المنهجية التقنية على ما أوصت به المسابقة، مع تخصيص عميق للسياق السعودي:

- **محرك هجين (قواعد + نموذج لغوي):**  
  - جزء قواعد ثابتة يمثِّل المعرفة المهنية وسياق سوق العمل السعودي (مثل: حدود منطقية للدخل لطالب/متدرب، مقارنة الدخل بالمسمى الوظيفي، العلاقة بين العمر وسنوات الخبرة، العلاقة بين العمر وعدد الأطفال والحالة الاجتماعية).  
  - جزء يعتمد على نموذج لغوي كبير (LLM) عبر واجهة OpenAI API مع استخدام أسلوب **التعليم السريع (Few-Shot Prompting)** لاستخلاص تناقضات دلالية أعمق.

- **تهيئة البرومبت للسعودية (سياق عربي/إنجليزي):**  
  - برومبت منظّم يشرح للنموذج السياق السعودي وأمثلة من العمل الميداني.  
  - أمثلة تدريبية قصيرة بالعربية والإنجليزية توضِّح للنموذج كيف يميّز بين الحالات المعقولة والحالات المريبة، مع الحرص على عدم المبالغة في الإنذارات.

- **تكامل لحظي مع منصات الاستبيانات:**  
  - بناء واجهة برمجية باستخدام **FastAPI** توفر مسارات `/validate` و`/batch-validate`.  
  - بناء واجهة تفاعلية حية باستخدام **Streamlit** تُظهر للمقيِّم/الباحث درجة الثقة والقائمة المفصَّلة بالمشكلات فور إدخال البيانات.  
  - يمكن ربط الـ API مع أي منصة استبيان أو أداة منخفضة الكود من خلال طلبات HTTP بسيطة.

---

### 4. Expected Impact (الأثر المتوقع)

**English**  
- **Higher data quality:** Significant reduction in illogical and inconsistent responses before they enter the data warehouse.  
- **Lower manual cleaning cost:** Field teams and analysts spend less time fixing errors after collection.  
- **Faster decision-making:** Trustworthy, “clean-by-design” datasets accelerate reporting and policy analysis.  
- **Scalability:** The API design allows the solution to be deployed across multiple survey projects and regions with minimal changes.

**العربية**  
- **رفع جودة البيانات:** تقليل ملحوظ في الاستجابات غير المنطقية قبل دخولها لمستودعات البيانات أو أنظمة التحليل.  
- **خفض تكلفة التنقية اليدوية:** تقليل الوقت والجهد الذي تبذله الفرق الميدانية وفرق التحليل في تصحيح الأخطاء بعد انتهاء جمع البيانات.  
- **تسريع اتخاذ القرار:** بيانات موثوقة «مصمَّمة لتكون نظيفة من البداية» تسرِّع إعداد التقارير وصنع السياسات المبنية على الأدلة.  
- **قابلية التوسّع:** تصميم الـ API يتيح نشر الحل على عدّة مشاريع استبيان ومناطق مختلفة مع تعديلات بسيطة فقط.

---

### 5. Differentiation & Hackathon Fit (نقاط التميّز وملاءمة التحدي)

**English**  
- Purpose-built for the **Saudi context**, not a generic LLM demo.  
- True **orchestration** between rule-based checks and LLM reasoning, instead of relying solely on a fine-tuned model.  
- Live, bilingual UI (Arabic/English) that clearly demonstrates **real-time error detection** while filling the survey.  
- Designed to integrate with existing survey platforms through simple, well-documented APIs.

**العربية**  
- حلّ مصمَّم خصيصًا **لسوق العمل والواقع الاجتماعي في المملكة**، وليس نموذجًا لغويًّا عامًا فقط.  
- يجمع بين **القواعد المنطقية الصلبة** وقدرات النموذج اللغوي في منطق واحد منسَّق (Orchestration)، بدل الاعتماد على نموذج مدرَّب فقط.  
- واجهة تفاعلية حيّة ثنائية اللغة (عربي/إنجليزي) توضِّح بوضوح قدرة النظام على **اكتشاف الأخطاء فور إدخالها**.  
- قابل للدمج بسهولة مع منصات الاستبيانات الحالية من خلال واجهات برمجية بسيطة وموثّقة.

