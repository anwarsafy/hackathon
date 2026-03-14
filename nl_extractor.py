"""Extract structured SurveyResponse from natural language using LLM."""
from __future__ import annotations

import json
from typing import List, Optional, Tuple

from config import get_settings
from models import SurveyResponse
from openai import OpenAI


EXTRACT_SYSTEM_PROMPT = """
You are a survey data extractor. Given free-text from a respondent (in any language, e.g. English or Arabic),
extract structured fields for a survey response. Output ONLY valid JSON with no markdown or explanation.

Allowed fields (all optional; include only if you can determine a value):
- age (integer, years)
- gender (string)
- education (string)
- job_title (string)
- years_experience (number)
- marital_status (string)
- children (integer)
- monthly_income (number; if currency mentioned assume SAR unless stated otherwise)
- extras (object for any other key-value pairs)

If something is ambiguous or missing, omit that field. Do not invent values.
If the text mentions income in another currency, convert to SAR if you know the rate, or put a note in extras.
Output format: a single JSON object with only the fields you could extract. Example: {"age": 30, "job_title": "Engineer", "years_experience": 5}
""".strip()


def extract_response(
    text: str,
    survey_type: Optional[str] = None,
    language_hint: Optional[str] = None,
) -> Tuple[SurveyResponse, List[str]]:
    """
    Extract a structured SurveyResponse from natural language text.
    Returns (response, parsing_issues). parsing_issues lists any uncertainties (e.g. "Could not determine years_experience").
    """
    settings = get_settings()
    if not settings.openai_api_key:
        return (
            SurveyResponse(),
            ["LLM required for extraction; OPENAI_API_KEY not configured."],
        )

    client = OpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_api_base or None,
    )
    model = settings.openai_model

    user_parts = [f"Respondent text:\n{text}"]
    if survey_type:
        user_parts.append(f"\nSurvey type context: {survey_type}")
    if language_hint:
        user_parts.append(f"\nLanguage hint: {language_hint}")
    user_content = "\n".join(user_parts)

    parsing_issues: List[str] = []

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": EXTRACT_SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            response_format={"type": "json_object"},
        )
        raw = completion.choices[0].message.content or "{}"
        data = json.loads(raw)

        # Build SurveyResponse; only pass known SurveyResponse fields
        known_fields = {
            "age", "gender", "education", "job_title", "years_experience",
            "marital_status", "children", "monthly_income", "extras",
        }
        response_dict: dict = {}
        extras: dict = {}
        for k, v in data.items():
            if k in known_fields:
                if k == "extras" and isinstance(v, dict):
                    extras.update(v)
                elif v is not None:
                    response_dict[k] = v
            else:
                extras[k] = v
        if extras:
            response_dict["extras"] = extras

        response = SurveyResponse(**response_dict)

        # Optional: add parsing_issues for missing key fields if we want to signal uncertainty
        if not response.age and "age" not in data:
            parsing_issues.append("Could not determine age")
        if response.job_title is None and "job_title" not in data:
            parsing_issues.append("Could not determine job_title")
        if response.monthly_income is None and "monthly_income" not in data:
            parsing_issues.append("Could not determine monthly_income")

        return response, parsing_issues

    except Exception as e:
        parsing_issues.append(f"Extraction failed: {e}")
        return SurveyResponse(), parsing_issues
