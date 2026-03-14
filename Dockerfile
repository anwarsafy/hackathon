# Semantic Guardian – FastAPI backend
FROM python:3.11-slim

WORKDIR /app

# Install dependencies (no Streamlit for API-only image)
COPY requirements.txt .
RUN pip install --no-cache-dir \
    fastapi uvicorn pydantic pydantic-settings pandas openai python-dotenv

COPY main.py config.py models.py validator_service.py rules_validator.py llm_validator.py ./

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
