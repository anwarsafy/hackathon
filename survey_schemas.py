"""Load and expose survey schemas (question bank) from data/survey_schemas.json."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from models import SurveySchema


_SCHEMAS: Optional[Dict[str, SurveySchema]] = None


def _load_schemas() -> Dict[str, SurveySchema]:
    global _SCHEMAS
    if _SCHEMAS is not None:
        return _SCHEMAS
    base_dir = Path(__file__).parent
    path = base_dir / "data" / "survey_schemas.json"
    if not path.exists():
        _SCHEMAS = {}
        return _SCHEMAS
    import json
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    _SCHEMAS = {}
    for survey_type, data in raw.items():
        _SCHEMAS[survey_type] = SurveySchema(**data)
    return _SCHEMAS


def list_survey_types() -> List[dict]:
    """Return list of { survey_type, name } for all loaded schemas."""
    schemas = _load_schemas()
    return [
        {"survey_type": st, "name": s.name}
        for st, s in schemas.items()
    ]


def get_schema(survey_type: str) -> Optional[SurveySchema]:
    """Return SurveySchema for the given survey_type, or None if not found."""
    return _load_schemas().get(survey_type)
