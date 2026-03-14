from __future__ import annotations

from pathlib import Path
from typing import List

import pandas as pd
import streamlit as st

from models import SurveyResponse
from nl_extractor import extract_response
from survey_schemas import list_survey_types
from validator_service import HybridValidatorService


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

    # Survey type: optional, for threshold and context
    survey_types_list = list_survey_types()
    survey_type_options = [t("(default)", "(افتراضي)")] + [s["name"] for s in survey_types_list]
    survey_type_ids = [None] + [s["survey_type"] for s in survey_types_list]
    survey_type_idx = st.sidebar.selectbox(
        t("Survey type", "نوع الاستبيان"),
        range(len(survey_type_options)),
        format_func=lambda i: survey_type_options[i],
    )
    selected_survey_type = survey_type_ids[survey_type_idx]

    mode = st.sidebar.radio(
        t("Input mode", "وضع الإدخال"),
        options=[
            t("Manual entry", "إدخال يدوي"),
            t("Use sample record", "استخدام سجل تجريبي"),
            t("Natural language", "نص حر"),
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
                    survey_type=selected_survey_type,
                    language_hint=lang if lang == "English" else "ar",
                )
                result = service.validate(
                    extracted,
                    survey_type=selected_survey_type,
                    question_text=None,
                )
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

        result = service.validate(
            response,
            survey_type=selected_survey_type,
            question_text=None,
        )

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

