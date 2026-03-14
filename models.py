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

