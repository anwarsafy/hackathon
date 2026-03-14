from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # LLM / OpenAI configuration
    openai_api_key: Optional[str] = None
    openai_api_base: Optional[str] = None  # Optional, for Azure / custom endpoints
    openai_model: str = "gpt-5-nano"

    # Rule thresholds
    min_age: int = 15
    max_age: int = 100
    unemployed_income_threshold: float = 2000.0
    max_reasonable_income: float = 100_000.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

