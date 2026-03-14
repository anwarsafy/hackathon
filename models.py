from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class IssueSource(str, Enum):
    rule = "rule"
    llm = "llm"
    system = "system"


class SurveyResponse(BaseModel):
    age: Optional[int] = Field(None, description="Age of the respondent in years")
    gender: Optional[str] = None
    education: Optional[str] = None
    job_title: Optional[str] = None
    years_experience: Optional[float] = Field(
        None, description="Total years of work experience"
    )
    marital_status: Optional[str] = None
    children: Optional[int] = None
    monthly_income: Optional[float] = None

    # For extensibility in a hackathon setting
    extras: Dict[str, Any] = Field(default_factory=dict)

    @validator("age")
    def non_negative_age(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 0:
            raise ValueError("age must be non-negative")
        return v

    @validator("years_experience")
    def non_negative_experience(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("years_experience must be non-negative")
        return v

    @validator("children")
    def non_negative_children(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 0:
            raise ValueError("children must be non-negative")
        return v


class Issue(BaseModel):
    field: Optional[str] = Field(
        None, description="Primary field associated with the detected issue"
    )
    description: str
    severity: Severity = Severity.medium
    source: IssueSource = IssueSource.system


class ValidationResult(BaseModel):
    confidence_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Overall data quality score between 0 and 100",
    )
    status: str
    issues: List[Issue] = Field(default_factory=list)
    rule_summary: Optional[str] = None
    llm_summary: Optional[str] = None


# --- Survey schema & request wrappers (question-aware, NL input) ---


class SurveyQuestion(BaseModel):
    id: str
    field: str
    label: str
    question_text: Optional[str] = None
    value_type: Optional[str] = None  # e.g. "number", "text", "choice"


class SurveySchema(BaseModel):
    survey_type: str
    name: str
    questions: List[SurveyQuestion] = Field(default_factory=list)


class ValidateRequest(BaseModel):
    """Richer validation request: response + optional survey type and question text."""
    response: SurveyResponse
    survey_type: Optional[str] = None
    question_text: Optional[Dict[str, str]] = None  # field name -> question text


class ValidateFromTextRequest(BaseModel):
    """Request to validate from natural language input."""
    text: str
    survey_type: Optional[str] = None
    language_hint: Optional[str] = None


class ValidateFromTextResponse(BaseModel):
    """Response for validate-from-text: extracted response + validation + parsing issues."""
    extracted: SurveyResponse
    validation: ValidationResult
    parsing_issues: List[str] = Field(default_factory=list)


# --- Dynamic: any questions from frontend ---


class DynamicItem(BaseModel):
    """One question-answer pair (any field name)."""
    field: str
    question: str = Field(..., description="Question text shown to respondent")
    value: Any = None  # number, string, or null


class ValidateDynamicRequest(BaseModel):
    """Validate using any list of question-answer pairs. Works with all questions the frontend sends."""
    items: List[DynamicItem] = Field(..., description="List of field, question text, and value")

