from __future__ import annotations

from typing import List

from config import get_settings
from models import Issue, IssueSource, Severity, SurveyResponse


class RuleBasedValidator:
    """Collection of deterministic rules for quick, explainable checks."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def validate(self, response: SurveyResponse) -> List[Issue]:
        issues: List[Issue] = []

        self._check_age_range(response, issues)
        self._check_experience_vs_age(response, issues)
        self._check_children_vs_age_and_marital_status(response, issues)
        self._check_income_vs_employment(response, issues)
        self._check_income_reasonableness(response, issues)
        self._check_saudi_context_specific(response, issues)

        return issues

    def _add_issue(
        self,
        issues: List[Issue],
        field: str | None,
        description: str,
        severity: Severity,
    ) -> None:
        issues.append(
            Issue(
                field=field,
                description=description,
                severity=severity,
                source=IssueSource.rule,
            )
        )

    def _check_age_range(self, response: SurveyResponse, issues: List[Issue]) -> None:
        if response.age is None:
            return
        if response.age < self.settings.min_age:
            self._add_issue(
                issues,
                "age",
                f"Age {response.age} is below the expected minimum of {self.settings.min_age} for this survey.",
                Severity.medium,
            )
        if response.age > self.settings.max_age:
            self._add_issue(
                issues,
                "age",
                f"Age {response.age} seems unrealistically high.",
                Severity.high,
            )

    def _check_experience_vs_age(
        self, response: SurveyResponse, issues: List[Issue]
    ) -> None:
        if response.age is None or response.years_experience is None:
            return
        # Assume work rarely starts before 15
        max_experience = max(response.age - 15, 0)
        if response.years_experience > max_experience:
            self._add_issue(
                issues,
                "years_experience",
                f"Years of experience ({response.years_experience}) exceeds plausible maximum based on age ({response.age}).",
                Severity.high,
            )

    def _check_children_vs_age_and_marital_status(
        self, response: SurveyResponse, issues: List[Issue]
    ) -> None:
        if response.age is not None and response.children is not None:
            if response.age < 18 and response.children > 0:
                self._add_issue(
                    issues,
                    "children",
                    f"Respondent is {response.age} years old but reports {response.children} children.",
                    Severity.high,
                )

        if response.marital_status and response.children is not None:
            if response.marital_status.lower() == "single" and response.children > 0:
                self._add_issue(
                    issues,
                    "marital_status",
                    f"Marital status is 'Single' but respondent reports {response.children} children.",
                    Severity.medium,
                )

    def _check_income_vs_employment(
        self, response: SurveyResponse, issues: List[Issue]
    ) -> None:
        if response.job_title is None or response.monthly_income is None:
            return

        title = response.job_title.lower()
        unemployed_keywords = ["unemployed", "no job", "jobless"]
        low_income_roles = ["student", "intern"]

        if any(k in title for k in unemployed_keywords):
            if response.monthly_income > self.settings.unemployed_income_threshold:
                self._add_issue(
                    issues,
                    "monthly_income",
                    f"Job title suggests unemployment ('{response.job_title}') but monthly income is {response.monthly_income}.",
                    Severity.high,
                )

        if any(k in title for k in low_income_roles):
            if response.monthly_income is not None and response.monthly_income > (
                self.settings.max_reasonable_income * 0.5
            ):
                self._add_issue(
                    issues,
                    "monthly_income",
                    f"Role '{response.job_title}' usually has modest income but reported monthly income is {response.monthly_income}.",
                    Severity.medium,
                )

    def _check_income_reasonableness(
        self, response: SurveyResponse, issues: List[Issue]
    ) -> None:
        if response.monthly_income is None:
            return
        if response.monthly_income < 0:
            self._add_issue(
                issues,
                "monthly_income",
                "Monthly income cannot be negative.",
                Severity.high,
            )
        if response.monthly_income > self.settings.max_reasonable_income:
            self._add_issue(
                issues,
                "monthly_income",
                f"Monthly income {response.monthly_income} appears unrealistically high.",
                Severity.medium,
            )

    def _check_saudi_context_specific(
        self, response: SurveyResponse, issues: List[Issue]
    ) -> None:
        """Heuristics tailored for the Saudi labour market / context.

        These are intentionally simple and explainable – good for a hackathon demo.
        """
        if response.job_title is None or response.monthly_income is None:
            return

        title = response.job_title.strip().lower()
        income = response.monthly_income

        # Saudi-specific low income roles where very high income is suspicious
        sa_low_income_roles = [
            "student",
            "طالب",
            "intern",
            "متدرب",
            "cashier",
            "كاشير",
            "مندوب مبيعات",
        ]

        if any(k in title for k in sa_low_income_roles) and income > 20000:
            self._add_issue(
                issues,
                "monthly_income",
                f"Role '{response.job_title}' usually has modest income in the Saudi market, "
                f"but reported monthly income is {income}.",
                Severity.high,
            )

        # "Unemployed" / "عاطل" / "بدون عمل" with non‑trivial income
        sa_unemployed_keywords = ["unemployed", "no job", "jobless", "عاطل", "بدون عمل"]
        if any(k in title for k in sa_unemployed_keywords) and income > 3000:
            self._add_issue(
                issues,
                "monthly_income",
                f"Job title suggests no employment in Saudi context ('{response.job_title}') "
                f"but reported income is {income} SAR.",
                Severity.high,
            )

        # Very low income for senior-sounding roles
        senior_roles = ["manager", "مدير", "director", "مدير عام", "ceo", "رئيس تنفيذي"]
        if any(k in title for k in senior_roles) and income < 4000:
            self._add_issue(
                issues,
                "monthly_income",
                f"Job title '{response.job_title}' suggests a senior role in Saudi organisations, "
                f"but income {income} SAR is unusually low.",
                Severity.medium,
            )

