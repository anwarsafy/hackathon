from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from models import SurveyResponse
from validator_service import HybridValidatorService


def main() -> None:
    base_dir = Path(__file__).parent
    csv_path = base_dir / "data" / "sample_responses.csv"

    df = pd.read_csv(csv_path)

    service = HybridValidatorService()

    print(f"Loaded {len(df)} sample survey responses from {csv_path}")
    print("-" * 80)

    def na_none(v):
        return None if pd.isna(v) else v

    for idx, row in df.iterrows():
        response = SurveyResponse(
            age=int(row["age"]) if not pd.isna(row["age"]) else None,
            gender=na_none(row.get("gender")),
            education=na_none(row.get("education")),
            job_title=na_none(row.get("job_title")),
            years_experience=float(row["years_experience"])
            if not pd.isna(row["years_experience"])
            else None,
            marital_status=na_none(row.get("marital_status")),
            children=int(row["children"]) if not pd.isna(row["children"]) else None,
            monthly_income=float(row["monthly_income"])
            if not pd.isna(row["monthly_income"])
            else None,
        )

        result = service.validate(response)

        print(f"Record #{idx}: age={response.age}, job_title={response.job_title}")
        print(
            f"  -> confidence_score={result.confidence_score}, status='{result.status}'"
        )
        if result.issues:
            for issue in result.issues:
                print(
                    f"     - [{issue.source}/{issue.severity}] field={issue.field!r}: {issue.description}"
                )
        else:
            print("     - No issues detected.")
        print()

    # Show one example JSON payload for documentation purposes
    example_response = SurveyResponse(
        age=19,
        gender="Female",
        education="PhD",
        job_title="Researcher",
        years_experience=1,
        marital_status="Single",
        children=0,
        monthly_income=3000,
    )
    example_result = service.validate(example_response)
    print("Example API-style JSON response for a single record:")
    print(json.dumps(example_result.model_dump(), indent=2))


if __name__ == "__main__":
    main()

