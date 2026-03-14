from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List

import pandas as pd
import streamlit as st

from models import DynamicItem, SurveyResponse
from nl_extractor import extract_response
from validator_service import HybridValidatorService


_KNOWN = {"age", "gender", "education", "job_title", "years_experience", "marital_status", "children", "monthly_income"}
_INT_FIELDS = {"age", "children"}
_FLOAT_FIELDS = {"years_experience", "monthly_income"}


def _dynamic_to_response_and_questions(
    items: List[DynamicItem],
) -> tuple[SurveyResponse, dict[str, str]]:
    """Build SurveyResponse + question_text from dynamic items (any questions)."""
    response_dict: dict[str, Any] = {}
    extras: dict[str, Any] = {}
    question_text: dict[str, str] = {}
    for item in items:
        question_text[item.field] = item.question
        v = item.value
        if v is None or (isinstance(v, str) and v.strip() == ""):
            continue
        if item.field in _INT_FIELDS:
            try:
                response_dict[item.field] = int(v) if not isinstance(v, int) else v
            except (TypeError, ValueError):
                response_dict[item.field] = v
        elif item.field in _FLOAT_FIELDS:
            try:
                response_dict[item.field] = float(v) if not isinstance(v, (int, float)) else v
            except (TypeError, ValueError):
                response_dict[item.field] = v
        elif item.field in _KNOWN:
            response_dict[item.field] = v if isinstance(v, str) else str(v)
        else:
            extras[item.field] = v
    if extras:
        response_dict["extras"] = extras
    return SurveyResponse(**response_dict), question_text


@st.cache_data
def load_samples() -> pd.DataFrame:
    base_dir = Path(__file__).parent
    csv_path = base_dir / "data" / "sample_responses.csv"
    return pd.read_csv(csv_path)


def main() -> None:
    st.set_page_config(page_title="Semantic Guardian – Survey Data Validator", layout="centered")

    # Language toggle (English / Arabic)
    lang = st.sidebar.radio(
        "Language / اللغة",
        options=["English", "العربية"],
        index=0,
    )

    def t(en: str, ar: str) -> str:
        return en if lang == "English" else ar

    st.title(t("Semantic Guardian – Survey Data Validator", "حارس البيانات الدكي – مدقق استجابات الاستبيان"))
    st.markdown(
        t(
            "Hybrid **rule-based** + **LLM semantic** engine for catching logical errors in survey responses in real time.",
            "محرك يجمع بين **قواعد منطقية** و **نموذج لغوي ذكي** لاكتشاف الأخطاء المنطقية في بيانات الاستبيانات في الوقت الفعلي، مع تهيئة خاصة لسوق العمل في السعودية.",
        )
    )

    service = HybridValidatorService()
    samples = load_samples()

    # All-in-one: single flow, no survey type selector
    mode = st.sidebar.radio(
        t("Input mode", "وضع الإدخال"),
        options=[
            t("Manual entry", "إدخال يدوي"),
            t("Use sample record", "استخدام سجل تجريبي"),
            t("Natural language", "نص حر"),
            t("Dynamic (any questions)", "ديناميكي (أي أسئلة)"),
        ],
    )

    if mode == t("Natural language", "نص حر"):
        st.subheader(t("Paste respondent text", "الصق نص إجابة المستجيب"))
        nl_text = st.text_area(
            t(
                "Enter free-text (e.g. “I am 30, engineer, 5 years experience, married, 2 children, 8000 SAR”)",
                "أدخل نصاً حراً (مثال: أنا ٣٠ سنة، مهندس، ٥ سنوات خبرة، متزوج، ولدان، ٨٠٠٠ ريال)",
            ),
            height=120,
        )
        if st.button(t("Extract and validate", "استخراج والتحقق")):
            if not nl_text.strip():
                st.warning(t("Please enter some text.", "يرجى إدخال نص."))
            else:
                extracted, parsing_issues = extract_response(
                    nl_text.strip(),
                    survey_type=None,
                    language_hint=lang if lang == "English" else "ar",
                )
                result = service.validate(extracted, survey_type=None, question_text=None)
                st.subheader(t("Extracted response", "الاستجابة المستخرجة"))
                st.json(extracted.model_dump())
                if parsing_issues:
                    st.warning(t("Parsing notes: ", "ملاحظات الاستخراج: ") + "; ".join(parsing_issues))
                st.subheader(t("Data quality score", "درجة جودة البيانات"))
                st.metric(
                    label=t("Confidence score (0–100)", "درجة الثقة (0–100)"),
                    value=result.confidence_score,
                    delta=None,
                )
                st.write(t("**Status:** ", "**الحالة:** ") + str(result.status))
                st.subheader(t("Detected issues", "المشكلات المكتشفة"))
                if result.issues:
                    issue_rows = [
                        {"field": i.field, "description": i.description, "severity": i.severity.value, "source": i.source.value}
                        for i in result.issues
                    ]
                    st.table(issue_rows)
                else:
                    st.success(t("No issues detected.", "لا توجد مشكلات."))
                with st.expander(t("Raw validation JSON", "استجابة التحقق الخام")):
                    st.json(result.model_dump())
        st.stop()

    if mode == t("Dynamic (any questions)", "ديناميكي (أي أسئلة)"):
        st.subheader(t("Dynamic: any questions from your form", "ديناميكي: أي أسئلة من النموذج"))
        st.markdown(
            t(
                "Paste a JSON array of `{ \"field\", \"question\", \"value\" }`. Works with **all questions** your frontend sends.",
                "الصق مصفوفة JSON من `{ \"field\", \"question\", \"value\" }`. يعمل مع **جميع الأسئلة** التي يرسلها الواجهة.",
            )
        )
        dynamic_json = st.text_area(
            t("JSON array of items", "مصفوفة JSON للعناصر"),
            value='[\n  {"field": "age", "question": "What is your age?", "value": 30},\n  {"field": "job_title", "question": "Your job?", "value": "Engineer"},\n  {"field": "monthly_income", "question": "Monthly income (SAR)?", "value": 8000}\n]',
            height=220,
        )
        if st.button(t("Validate dynamic", "تحقق ديناميكي")):
            try:
                raw = json.loads(dynamic_json)
                if not isinstance(raw, list):
                    st.error(t("Must be a JSON array.", "يجب أن تكون مصفوفة JSON."))
                else:
                    items = [DynamicItem(**x) for x in raw]
                    response, question_text = _dynamic_to_response_and_questions(items)
                    result = service.validate(response, survey_type=None, question_text=question_text)
                    st.subheader(t("Data quality score", "درجة جودة البيانات"))
                    st.metric(t("Confidence score (0–100)", "درجة الثقة (0–100)"), result.confidence_score)
                    st.write(t("**Status:** ", "**الحالة:** ") + result.status)
                    if result.issues:
                        st.table([{"field": i.field, "description": i.description, "severity": i.severity.value} for i in result.issues])
                    else:
                        st.success(t("No issues detected.", "لا توجد مشكلات."))
                    with st.expander(t("Raw JSON", "JSON الخام")):
                        st.json(result.model_dump())
            except json.JSONDecodeError as e:
                st.error(t("Invalid JSON: ", "JSON غير صالح: ") + str(e))
            except Exception as e:
                st.error(str(e))
        st.stop()

    if mode == t("Use sample record", "استخدام سجل تجريبي"):
        idx = st.sidebar.number_input(
            t("Sample index", "رقم العينة"),
            min_value=0,
            max_value=len(samples) - 1,
            value=0,
            step=1,
        )
        row = samples.iloc[int(idx)]
        default_values = dict(row)
    else:
        default_values = {
            "age": 30,
            "gender": "Female",
            "education": "Bachelor",
            "job_title": "Data Analyst",
            "years_experience": 5.0,
            "marital_status": "Single",
            "children": 0,
            "monthly_income": 4000.0,
        }

    st.subheader(t("Survey response", "بيانات المستجيب"))
    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input(t("Age", "العمر"), min_value=0, max_value=120, value=int(default_values["age"]))
        gender = st.text_input(t("Gender", "الجنس"), value=str(default_values.get("gender", "")))
        education = st.text_input(
            t("Education", "المؤهل العلمي"),
            value=str(default_values.get("education", "")),
            help=t(
                "e.g., Primary School, High School, Bachelor, Master, PhD",
                "مثال: ابتدائي، ثانوي، بكالوريوس، ماجستير، دكتوراه",
            ),
        )
        marital_status = st.text_input(
            t("Marital status", "الحالة الاجتماعية"),
            value=str(default_values.get("marital_status", "")),
            help=t("e.g., Single, Married, Divorced", "مثال: أعزب، متزوج، مطلّق"),
        )

    with col2:
        job_title = st.text_input(
            t("Job title", "المسمى الوظيفي"),
            value=str(default_values.get("job_title", "")),
            help=t(
                "e.g., Unemployed, Student, Doctor, CEO",
                "مثال: عاطل، طالب، طبيب، مهندس، مدير تنفيذي",
            ),
        )
        years_experience = st.number_input(
            t("Years of experience", "سنوات الخبرة"),
            min_value=0.0,
            max_value=80.0,
            step=0.5,
            value=float(default_values.get("years_experience", 0.0)),
        )
        children = st.number_input(
            t("Number of children", "عدد الأطفال"),
            min_value=0,
            max_value=20,
            value=int(default_values.get("children", 0)),
        )
        monthly_income = st.number_input(
            t("Monthly income (SAR)", "الدخل الشهري (ريال سعودي)"),
            min_value=0.0,
            max_value=200000.0,
            step=100.0,
            value=float(default_values.get("monthly_income", 0.0)),
        )

    if st.button(t("Validate response", "تحقق من الاستجابة")):
        response = SurveyResponse(
            age=int(age),
            gender=gender or None,
            education=education or None,
            job_title=job_title or None,
            years_experience=float(years_experience),
            marital_status=marital_status or None,
            children=int(children),
            monthly_income=float(monthly_income),
        )

        result = service.validate(response, survey_type=None, question_text=None)

        st.subheader(t("Data quality score", "درجة جودة البيانات"))
        st.metric(
            label=t("Confidence score (0–100)", "درجة الثقة (0–100)"),
            value=result.confidence_score,
            delta=None,
        )
        st.write(t("**Status:** ", "**الحالة:** ") + str(result.status))

        st.subheader(t("Detected issues", "المشكلات المكتشفة"))
        if result.issues:
            issue_rows: List[dict] = []
            for issue in result.issues:
                issue_rows.append(
                    {
                        "field": issue.field,
                        "description": issue.description,
                        "severity": issue.severity.value,
                        "source": issue.source.value,
                    }
                )
            st.table(issue_rows)
        else:
            st.success(t("No issues detected. Response looks consistent.", "لا توجد مشكلات. تبدو الاستجابة متسقة."))

        with st.expander(t("Raw JSON response", "استجابة JSON الخام")):
            st.json(result.model_dump())

        st.markdown(
            t("**Rule-based summary:** ", "**ملخص القواعد المنطقية:** ") + (result.rule_summary or "")
        )
        st.markdown(
            t("**LLM summary:** ", "**ملخص النموذج اللغوي:** ") + (result.llm_summary or "")
        )


if __name__ == "__main__":
    main()

