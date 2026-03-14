# Semantic Guardian

**AI-powered survey data validation for logical and semantic consistency — with a focus on the Saudi labour market.**

---

## Overview

Semantic Guardian is a hybrid validation system that checks survey responses for logical errors and real-world inconsistencies. It combines **rule-based checks** with **LLM semantic analysis** to produce an explainable data quality score (0–100) and a detailed list of detected issues.

Built for researchers and data teams who need to ensure survey data quality before analysis, especially in contexts such as labour market and social surveys in Saudi Arabia.

---

## Key Features

- **Hybrid validation** — Rule-based engine for fast, deterministic checks; LLM for deeper semantic inconsistencies
- **Explainable output** — Confidence score, status (e.g. high reliability, suspicious, inconsistent), and per-issue descriptions with severity
- **REST API** — Single and batch validation endpoints; OpenAPI docs at `/docs`
- **Interactive dashboard** — Streamlit UI with English/Arabic support for manual testing and demos
- **Saudi context** — Rules and prompts tuned for local job titles, income ranges, and common survey patterns

---

## Tech Stack

| Layer        | Technology        |
|-------------|-------------------|
| API         | FastAPI           |
| Validation  | Python, Pydantic  |
| LLM         | OpenAI API        |
| Dashboard   | Streamlit         |
| Config      | pydantic-settings |

---

## Architecture

```
┌─────────────────┐     ┌──────────────────────┐     ┌─────────────────────┐
│  Client / UI    │────▶│  FastAPI (main.py)   │────▶│ HybridValidator     │
│  (Streamlit)    │     │  /validate           │     │ Service             │
└─────────────────┘     │  /batch-validate     │     └──────────┬──────────┘
                        └──────────────────────┘                │
                                                                 ├──▶ Rule-based validator (age, income, experience, …)
                                                                 └──▶ LLM semantic validator (OpenAI)
```

- **Rule engine** — Age range, experience vs age, children vs marital status, income vs employment, Saudi-specific thresholds
- **LLM validator** — Structured prompt; returns JSON list of issues with field, description, severity
- **Scoring** — Combined issues → confidence score (0–100) and status

---

## Getting Started

### Prerequisites

- Python 3.9+
- OpenAI API key (optional; system runs without it using rules only)

### Installation

```bash
git clone <repository-url>
cd hackathon
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Environment (optional, for LLM)

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4.1-mini
```

If `OPENAI_API_KEY` is not set, the API and dashboard still run; LLM validation is skipped and only rule-based validation is used.

### Run the API

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- API: `http://localhost:8000`
- Interactive docs: `http://localhost:8000/docs`

### Run the dashboard

```bash
streamlit run dashboard.py
```

Open the URL shown in the terminal to use the bilingual (EN/AR) validation UI.

### Run sample validation (CLI)

```bash
python run_examples.py
```

Runs the validator on `data/sample_responses.csv` and prints scores and issues per record.

---

## API Summary

| Method | Endpoint          | Description                    |
|--------|-------------------|--------------------------------|
| GET    | `/health`         | Health check                   |
| POST   | `/validate`       | Validate a single response     |
| POST   | `/batch-validate`| Validate multiple responses    |

Request body for `/validate`: JSON with fields such as `age`, `gender`, `education`, `job_title`, `years_experience`, `marital_status`, `children`, `monthly_income`.

Response: `confidence_score`, `status`, `issues[]`, `rule_summary`, `llm_summary`.

---

## Project Structure

| File / folder           | Purpose                                      |
|-------------------------|----------------------------------------------|
| `main.py`               | FastAPI app and routes                       |
| `validator_service.py`  | Hybrid validation and scoring                |
| `rules_validator.py`    | Rule-based validation logic                  |
| `llm_validator.py`      | LLM integration and prompt handling          |
| `models.py`             | Pydantic models (SurveyResponse, Issue, …)   |
| `config.py`             | Settings and thresholds                      |
| `dashboard.py`          | Streamlit dashboard                          |
| `run_examples.py`       | CLI demo on sample CSV                       |
| `data/sample_responses.csv` | Example survey data                      |
| `requirements.txt`      | Python dependencies                          |

---

## License

This project was developed for educational and hackathon purposes. Use and modification are at your discretion; attribute the authors when sharing or building upon it.

---

*Semantic Guardian — Survey Data Validator*
