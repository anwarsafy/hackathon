from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # LLM / OpenAI configuration
    openai_api_key: Optional[str] = None
    openai_api_base: Optional[str] = None  # Optional, for Azure / custom endpoints
    openai_model: str = "gpt-5-nano"

    # Rule thresholds (defaults; overridden per survey_type in SURVEY_TYPE_THRESHOLDS)
    min_age: int = 15
    max_age: int = 100
    unemployed_income_threshold: float = 2000.0
    max_reasonable_income: float = 100_000.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


# Per-survey-type threshold overrides. Keys: survey_type (e.g. "labour_market", "health").
# Omitted keys fall back to Settings defaults.
SURVEY_TYPE_THRESHOLDS: Dict[str, Dict[str, Any]] = {
    "labour_market": {
        "min_age": 15,
        "max_age": 100,
        "unemployed_income_threshold": 2000.0,
        "max_reasonable_income": 100_000.0,
    },
    "health": {
        "min_age": 0,
        "max_age": 120,
        "unemployed_income_threshold": 2000.0,
        "max_reasonable_income": 100_000.0,
    },
}


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_thresholds_for_survey_type(survey_type: Optional[str] = None) -> Dict[str, Any]:
    """Return threshold dict for the given survey_type; fallback to default settings."""
    s = get_settings()
    default = {
        "min_age": s.min_age,
        "max_age": s.max_age,
        "unemployed_income_threshold": s.unemployed_income_threshold,
        "max_reasonable_income": s.max_reasonable_income,
    }
    if not survey_type or survey_type not in SURVEY_TYPE_THRESHOLDS:
        return default
    overrides = SURVEY_TYPE_THRESHOLDS[survey_type]
    return {**default, **overrides}

