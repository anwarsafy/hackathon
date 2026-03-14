from __future__ import annotations

from typing import Any, List

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from models import (
    SurveyResponse,
    SurveySchema,
    ValidateFromTextRequest,
    ValidateFromTextResponse,
    ValidateRequest,
    ValidationResult,
)
from nl_extractor import extract_response
from survey_schemas import get_schema, list_survey_types as list_survey_types_impl
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


@app.get("/survey-types")
def survey_types() -> list:
    """List available survey type ids and names."""
    return list_survey_types_impl()


@app.get("/survey-types/{survey_type}", response_model=SurveySchema)
def survey_type_schema(survey_type: str) -> SurveySchema:
    """Get full schema (questions, labels, optional question text) for a survey type."""
    schema = get_schema(survey_type)
    if schema is None:
        raise HTTPException(status_code=404, detail=f"Survey type {survey_type!r} not found")
    return schema


def _parse_validate_body(body: dict[str, Any]) -> tuple[SurveyResponse, str | None, dict[str, str] | None]:
    """Parse body as either ValidateRequest (has 'response') or plain SurveyResponse. Returns (response, survey_type, question_text)."""
    if "response" in body and body.get("response") is not None:
        req = ValidateRequest(**body)
        return req.response, req.survey_type, req.question_text
    resp = SurveyResponse(**body)
    return resp, None, None


@app.post("/validate", response_model=ValidationResult)
async def validate(request: Request) -> ValidationResult:
    """Validate one response. Body: SurveyResponse OR { response, survey_type?, question_text? }."""
    body = await request.json()
    response, survey_type, question_text = _parse_validate_body(body)
    return validator_service.validate(
        response, survey_type=survey_type, question_text=question_text
    )


@app.post("/batch-validate", response_model=List[ValidationResult])
async def batch_validate(request: Request) -> List[ValidationResult]:
    """Validate many. Body: list of SurveyResponse OR list of { response, survey_type?, question_text? }."""
    body = await request.json()
    if not isinstance(body, list):
        raise HTTPException(status_code=422, detail="Body must be a JSON array")
    results: List[ValidationResult] = []
    for item in body:
        if not isinstance(item, dict):
            raise HTTPException(status_code=422, detail="Each item must be an object")
        response, survey_type, question_text = _parse_validate_body(item)
        results.append(
            validator_service.validate(
                response, survey_type=survey_type, question_text=question_text
            )
        )
    return results


@app.post("/validate-from-text", response_model=ValidateFromTextResponse)
async def validate_from_text(req: ValidateFromTextRequest) -> ValidateFromTextResponse:
    """Extract structured response from natural language, then validate."""
    extracted, parsing_issues = extract_response(
        req.text,
        survey_type=req.survey_type,
        language_hint=req.language_hint,
    )
    validation = validator_service.validate(
        extracted,
        survey_type=req.survey_type,
        question_text=None,
    )
    return ValidateFromTextResponse(
        extracted=extracted,
        validation=validation,
        parsing_issues=parsing_issues,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

