from __future__ import annotations

import json
from typing import Any, Dict, List, Tuple

from openai import OpenAI

from config import get_settings
from models import Issue, IssueSource, Severity, SurveyResponse


SYSTEM_PROMPT = """
You are "Semantic Guardian", an assistant that checks survey responses for logical
and real-world inconsistencies, with a special focus on the Saudi labour market
and Saudi society.

You receive ONE survey response with fields like:
- age
- gender
- education
- job_title
- years_experience
- marital_status
- children
- monthly_income (in Saudi Riyal SAR)

Your task:
- Identify semantic contradictions or highly implausible combinations.
- Pay attention to mismatches between job_title, education, age, and monthly_income
  in the Saudi context (e.g. student with extremely high income, unemployed with
  very high income, very young age with many children, etc.).
- Focus on things that are unlikely in the real world, not minor edge cases.
- Be conservative: only flag issues that are clearly suspicious.

You may return descriptions in either Arabic or English depending on the input,
but keep them short and clear for a field researcher.

Output STRICTLY as compact JSON with this structure:
{
  "issues": [
    {
      "field": "<primary_field_name_or_null>",
      "description": "<short human readable explanation>",
      "severity": "low|medium|high"
    }
  ],
  "overall_comment": "<one or two sentence summary>"
}

Do not include any extra keys. Do not add comments. Do not add trailing commas.
If everything looks fine, return an empty issues array and a short reassuring overall_comment.
""".strip()


class LLMSemanticValidator:
    """Semantic validator using an LLM to capture non-trivial contradictions."""

    def __init__(self) -> None:
        settings = get_settings()
        if not settings.openai_api_key:
            # Fail gracefully: we'll run in a degraded, non-LLM mode
            self.client = None
        else:
            self.client = OpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_api_base or None,
            )
        self.model = settings.openai_model

    def build_prompt(
        self,
        response: SurveyResponse,
        question_text: Dict[str, str] | None = None,
    ) -> str:
        parts = []
        if question_text:
            parts.append("Questions as shown to the respondent:")
            for field, q in sorted(question_text.items()):
                parts.append(f"  - {field}: {q}")
            parts.append("")
        parts.append("Survey response JSON:")
        parts.append(json.dumps(response.model_dump(), indent=2, sort_keys=True))
        return "\n".join(parts)

    def parse_llm_output(self, raw_text: str) -> Tuple[List[Issue], str]:
        """Parse raw JSON text returned by the LLM into issues and comment."""
        issues: List[Issue] = []
        overall_comment = ""

        try:
            data = json.loads(raw_text)
            raw_issues = data.get("issues", []) or []
            overall_comment = data.get("overall_comment", "") or ""
            for item in raw_issues:
                field = item.get("field")
                description = item.get("description") or ""
                severity_str = (item.get("severity") or "medium").lower()
                if severity_str not in {"low", "medium", "high"}:
                    severity_str = "medium"
                severity = Severity(severity_str)

                if not description:
                    continue

                issues.append(
                    Issue(
                        field=field,
                        description=description,
                        severity=severity,
                        source=IssueSource.llm,
                    )
                )
        except Exception:
            # If parsing fails, we fall back to a system issue
            issues.append(
                Issue(
                    field=None,
                    description="LLM returned an unexpected response format.",
                    severity=Severity.low,
                    source=IssueSource.system,
                )
            )
        return issues, overall_comment

    def validate(
        self,
        response: SurveyResponse,
        question_text: Dict[str, str] | None = None,
    ) -> Tuple[List[Issue], str]:
        """Run the LLM-based semantic validation.

        Returns:
            (issues, llm_summary)
        """
        if not self.client:
            # Degraded mode: no LLM, but keep interface consistent
            return [], "LLM validation skipped (no API key configured)."

        user_content = self.build_prompt(response, question_text=question_text)

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                ],
                response_format={"type": "json_object"},
            )

            raw_text = completion.choices[0].message.content or "{}"
            issues, overall_comment = self.parse_llm_output(raw_text)
            return issues, overall_comment or "LLM semantic validation completed."
        except Exception as exc:  # noqa: BLE001
            # Robust error handling for hackathon demo
            return [
                Issue(
                    field=None,
                    description=f"LLM validation failed: {exc}",
                    severity=Severity.low,
                    source=IssueSource.system,
                )
            ], "LLM validation failed; falling back to rule-based checks only."

