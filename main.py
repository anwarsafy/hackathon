from __future__ import annotations

from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import SurveyResponse, ValidationResult
from validator_service import HybridValidatorService

app = FastAPI(
    title="Semantic Guardian – Survey Data Validator",
    description="Hybrid rule-based + LLM semantic validator for survey responses.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

validator_service = HybridValidatorService()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/validate", response_model=ValidationResult)
def validate(response: SurveyResponse) -> ValidationResult:
    return validator_service.validate(response)


@app.post("/batch-validate", response_model=List[ValidationResult])
def batch_validate(responses: List[SurveyResponse]) -> List[ValidationResult]:
    return [validator_service.validate(r) for r in responses]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

