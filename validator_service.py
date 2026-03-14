from __future__ import annotations

from typing import List

from models import Issue, IssueSource, Severity, SurveyResponse, ValidationResult
from rules_validator import RuleBasedValidator
from llm_validator import LLMSemanticValidator


class HybridValidatorService:
    """Combines rule-based and LLM-based validation, and computes confidence scores."""

    def __init__(self) -> None:
        self.rule_validator = RuleBasedValidator()
        self.llm_validator = LLMSemanticValidator()

    def _merge_issues(self, rule_issues: List[Issue], llm_issues: List[Issue]) -> List[Issue]:
        merged: List[Issue] = []

        def key(issue: Issue) -> tuple:
            return (
                (issue.field or "").lower(),
                issue.description.lower(),
                issue.source,
            )

        seen: set[tuple] = set()
        for issue in rule_issues + llm_issues:
            k = key(issue)
            if k not in seen:
                seen.add(k)
                merged.append(issue)
        return merged

    def _score_from_issues(self, issues: List[Issue]) -> int:
        # Simple, explainable heuristic for hackathon:
        # Start at 100 and subtract per issue by severity.
        score = 100
        for issue in issues:
            if issue.severity == Severity.low:
                score -= 3
            elif issue.severity == Severity.medium:
                score -= 7
            elif issue.severity == Severity.high:
                score -= 15
        score = max(0, min(100, score))
        return int(score)

    def _status_from_score(self, score: int) -> str:
        if score >= 90:
            return "high data reliability"
        if score >= 70:
            return "minor issues"
        if score >= 40:
            return "suspicious"
        return "inconsistent"

    def validate(self, response: SurveyResponse) -> ValidationResult:
        rule_issues = self.rule_validator.validate(response)
        llm_issues, llm_summary = self.llm_validator.validate(response)
        all_issues = self._merge_issues(rule_issues, llm_issues)

        score = self._score_from_issues(all_issues)
        status = self._status_from_score(score)

        rule_summary = (
            f"{len(rule_issues)} rule-based issue(s) detected."
            if rule_issues
            else "No rule-based issues detected."
        )
        llm_summary = llm_summary or (
            "LLM semantic validation not configured."
            if not llm_issues
            else f"{len(llm_issues)} LLM-derived issue(s) detected."
        )

        return ValidationResult(
            confidence_score=score,
            status=status,
            issues=all_issues,
            rule_summary=rule_summary,
            llm_summary=llm_summary,
        )

