# Semantic Guardian

**AI-powered survey data validation for logical and semantic consistency — with a focus on the Saudi labour market.**

- **Repository:** [github.com/anwarsafy/hackathon](https://github.com/anwarsafy/hackathon)
- **Live API (example):** [hackathon-beie.onrender.com](https://hackathon-beie.onrender.com) · [Interactive docs](https://hackathon-beie.onrender.com/docs)

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Configuration](#configuration)
- [Running Locally](#running-locally)
- [API Reference (Server)](#api-reference-server)
- [Data Models](#data-models)
- [Validation Logic](#validation-logic)
- [Deployment](#deployment)
- [Frontend Integration](#frontend-integration)
- [License](#license)

---

## Overview

Semantic Guardian is a **hybrid validation system** that checks survey responses for logical errors and real-world inconsistencies. It combines a **rule-based engine** (fast, deterministic) with **LLM semantic analysis** (OpenAI) to produce an explainable data quality score (0–100) and a detailed list of detected issues.

It is built for researchers and data teams who need to ensure survey data quality before analysis, especially in contexts such as labour market and social surveys in Saudi Arabia. The system can run with or without an OpenAI API key: without a key, only rule-based validation is used.

---

## Key Features

- **Hybrid validation** — Rule-based engine for fast, deterministic checks; optional LLM for deeper semantic inconsistencies.
- **Explainable output** — Confidence score (0–100), status label (e.g. high data reliability, suspicious, inconsistent), and per-issue descriptions with severity and source (rule / llm / system).
- **REST API** — Single and batch validation endpoints; OpenAPI (Swagger) docs at `/docs`, JSON schema at `/openapi.json`.
- **Interactive dashboard** — Streamlit UI with English/Arabic support for manual testing and demos.
- **Saudi context** — Rules and prompts tuned for local job titles, income ranges (SAR), and common survey patterns.
- **CORS enabled** — API allows all origins for easy frontend integration; no authentication required for the provided endpoints.

---

## Tech Stack

| Layer        | Technology        |
|-------------|--------------------|
| API         | FastAPI            |
| Server      | Uvicorn            |
| Validation  | Python, Pydantic  |
| LLM         | OpenAI API (Chat Completions) |
| Dashboard   | Streamlit          |
| Config      | pydantic-settings  |
| Data        | Pandas (CLI/samples) |

---

## Architecture

```
┌─────────────────┐     ┌──────────────────────┐     ┌─────────────────────┐
│  Client / UI    │────▶│  FastAPI (main.py)    │────▶│ HybridValidator       │
│  (Streamlit or  │     │  /validate            │     │ Service               │
│   any HTTP)     │     │  /batch-validate     │     └──────────┬────────────┘
└─────────────────┘     │  /health              │                │
                        └──────────────────────┘                ├──▶ RuleBasedValidator (age, income, experience, Saudi rules)
                                                                 └──▶ LLMSemanticValidator (OpenAI; optional)
```

- **Rule engine** — Validates age range, experience vs age, children vs marital status, income vs employment, income reasonableness, and Saudi-specific thresholds (job titles, income bands).
- **LLM validator** — Sends the response JSON to the OpenAI Chat Completions API with a structured prompt; expects JSON with `issues` and `overall_comment`. If the key is missing or the call fails, the API continues with rule-based results only.
- **Scoring** — Merged issues are deduplicated; score is computed by starting at 100 and subtracting by severity (low/medium/high). Status is derived from the final score (e.g. ≥90 → high data reliability, ≥70 → minor issues, ≥40 → suspicious, &lt;40 → inconsistent).

---

## Project Structure

| File or folder            | Purpose |
|---------------------------|--------|
| `main.py`                 | FastAPI app, CORS, routes: `/health`, `/validate`, `/batch-validate`. |
| `validator_service.py`    | Hybrid validation: merges rule + LLM issues, computes score and status. |
| `rules_validator.py`      | Rule-based validation (age, experience, children, income, Saudi context). |
| `llm_validator.py`        | LLM integration (OpenAI Chat Completions), prompt and JSON parsing. |
| `models.py`               | Pydantic models: `SurveyResponse`, `Issue`, `ValidationResult`, enums. |
| `config.py`               | Settings (OpenAI, rule thresholds) via env and `.env`. |
| `dashboard.py`            | Streamlit dashboard (EN/AR), manual or sample-based input. |
| `run_examples.py`         | CLI: runs validator on `data/sample_responses.csv`. |
| `data/sample_responses.csv` | Example survey rows for demo and CLI. |
| `requirements.txt`       | Python dependencies. |
| `Dockerfile`              | Docker image for the FastAPI API (production). |
| `Dockerfile.dashboard`    | Docker image for the Streamlit dashboard. |
| `render.yaml`             | Render Blueprint for backend deploy. |
| `.dockerignore`           | Excludes `.venv`, `.git`, etc. from Docker build. |
| `.streamlit/config.toml`  | Streamlit server/config for cloud deploy. |
| `API_FOR_FRONTEND.md`     | API summary and examples for frontend developers. |
| `DEPLOY.md`               | Deployment instructions (Render, Streamlit, etc.). |

---

## Installation & Setup

### Prerequisites

- **Python 3.9+**
- **OpenAI API key** (optional) — if not set, only rule-based validation runs.

### Installation

```bash
git clone https://github.com/anwarsafy/hackathon.git
cd hackathon
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Environment (optional, for LLM)

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

- If `OPENAI_API_KEY` is not set, the API and dashboard still run; LLM validation is skipped and only rule-based validation is used.
- `OPENAI_MODEL` defaults to the value in `config.py` (overridable via env). Use any Chat Completions model that supports JSON mode (e.g. `gpt-4o-mini`, `gpt-4.1-mini`).
- Optional: `OPENAI_API_BASE` for Azure or custom endpoints.

---

## Configuration

Configuration is centralized in `config.py` via `pydantic-settings`. Environment variables take precedence over `.env`.

| Variable / setting           | Type    | Default        | Description |
|-----------------------------|--------|----------------|-------------|
| `OPENAI_API_KEY`            | string | `None`         | OpenAI API key; if missing, LLM is disabled. |
| `OPENAI_API_BASE`           | string | `None`         | Optional base URL (e.g. Azure, proxy). |
| `OPENAI_MODEL`              | string | `gpt-5-nano`*  | Chat Completions model name. |
| `min_age`                   | int    | `15`           | Minimum valid age for rule checks. |
| `max_age`                   | int    | `100`          | Maximum valid age. |
| `unemployed_income_threshold` | float | `2000.0`     | Max plausible income when job suggests unemployed. |
| `max_reasonable_income`     | float  | `100_000.0`    | Cap for “reasonable” monthly income (SAR). |

\* Override `OPENAI_MODEL` in env with a real model (e.g. `gpt-4o-mini`) for production.

---

## Running Locally

### Run the API server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- API base: `http://localhost:8000`
- Interactive docs (Swagger): `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

### Run the dashboard

```bash
streamlit run dashboard.py
```

Open the URL shown in the terminal. The dashboard supports English and Arabic and can use manual input or sample records from `data/sample_responses.csv`.

### Run sample validation (CLI)

```bash
python run_examples.py
```

Reads `data/sample_responses.csv`, builds `SurveyResponse` objects, runs the hybrid validator, and prints confidence score, status, and issues per record. Also prints one example JSON response for documentation.

---

## API Reference (Server)

Base URL (local): `http://localhost:8000`  
Base URL (example production): `https://hackathon-beie.onrender.com`

All request/response bodies are JSON. The API uses **CORS** with `allow_origins=["*"]` and does not require authentication for the endpoints below.

---

### Health check

**`GET /health`**

Checks that the service is running.

**Response**

- Status: `200 OK`
- Body: `{ "status": "ok" }`

**Example**

```bash
curl -s http://localhost:8000/health
```

---

### Validate a single response

**`POST /validate`**

Validates one survey response and returns a confidence score, status, and list of issues.

**Request**

- **Headers:** `Content-Type: application/json`
- **Body:** JSON object matching the `SurveyResponse` model. All fields are optional; at least one field is typically provided for meaningful validation.

| Field             | Type   | Required | Description |
|-------------------|--------|----------|-------------|
| `age`             | int    | No       | Respondent age (years). |
| `gender`          | string | No       | Gender. |
| `education`       | string | No       | Education level. |
| `job_title`       | string | No       | Job title (used in rule and LLM checks). |
| `years_experience`| float  | No       | Total work experience (years). |
| `marital_status`  | string | No       | e.g. Single, Married. |
| `children`        | int    | No       | Number of children. |
| `monthly_income`  | float  | No       | Monthly income (e.g. SAR). |
| `extras`          | object | No       | Extra key-value pairs (passed through). |

**Response**

- Status: `200 OK`
- Body: `ValidationResult`

| Field              | Type   | Description |
|--------------------|--------|-------------|
| `confidence_score` | int    | 0–100; higher = better quality. |
| `status`           | string | e.g. `"high data reliability"`, `"minor issues"`, `"suspicious"`, `"inconsistent"`. |
| `issues`           | array  | List of `Issue` objects. |
| `rule_summary`     | string | Summary of rule-based findings (or “No rule-based issues detected.”). |
| `llm_summary`      | string | LLM summary or message if LLM skipped/failed. |

Each **Issue** has:

| Field         | Type   | Description |
|---------------|--------|-------------|
| `field`       | string \| null | Primary field (e.g. `"age"`, `"monthly_income"`). |
| `description` | string | Human-readable explanation. |
| `severity`    | string | `"low"`, `"medium"`, or `"high"`. |
| `source`      | string | `"rule"`, `"llm"`, or `"system"`. |

**Example request**

```bash
curl -s -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{"age":30,"gender":"Female","education":"Bachelor","job_title":"Data Analyst","years_experience":5,"marital_status":"Single","children":0,"monthly_income":4000}'
```

**Example response**

```json
{
  "confidence_score": 90,
  "status": "high data reliability",
  "issues": [],
  "rule_summary": "No rule-based issues detected.",
  "llm_summary": "LLM semantic validation completed."
}
```

**JavaScript example**

```js
const baseUrl = 'https://hackathon-beie.onrender.com';
const res = await fetch(`${baseUrl}/validate`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    age: 30,
    gender: 'Female',
    education: 'Bachelor',
    job_title: 'Data Analyst',
    years_experience: 5,
    marital_status: 'Single',
    children: 0,
    monthly_income: 4000,
  }),
});
const result = await res.json();
console.log(result.confidence_score, result.status, result.issues);
```

---

### Batch validate

**`POST /batch-validate`**

Validates multiple survey responses in one request.

**Request**

- **Headers:** `Content-Type: application/json`
- **Body:** JSON array of objects, each having the same shape as the body for `POST /validate` (each element is a `SurveyResponse`).

**Response**

- Status: `200 OK`
- Body: Array of `ValidationResult` objects, one per input response, in the same order.

**Example request**

```bash
curl -s -X POST http://localhost:8000/batch-validate \
  -H "Content-Type: application/json" \
  -d '[{"age":25,"job_title":"Engineer","years_experience":3},{"age":45,"job_title":"Manager","years_experience":2}]'
```

**Example response**

```json
[
  {
    "confidence_score": 90,
    "status": "high data reliability",
    "issues": [],
    "rule_summary": "No rule-based issues detected.",
    "llm_summary": "LLM semantic validation completed."
  },
  {
    "confidence_score": 78,
    "status": "minor issues",
    "issues": [
      {
        "field": "years_experience",
        "description": "Years of experience (2) is low for age (45).",
        "severity": "medium",
        "source": "rule"
      }
    ],
    "rule_summary": "1 rule-based issue(s) detected.",
    "llm_summary": "..."
  }
]
```

---

### OpenAPI (Swagger) documentation

- **Interactive UI:** `GET /docs` — try all endpoints from the browser.
- **OpenAPI JSON:** `GET /openapi.json` — machine-readable schema.

---

## Data Models

- **SurveyResponse** — Input survey record. Fields: `age`, `gender`, `education`, `job_title`, `years_experience`, `marital_status`, `children`, `monthly_income`, `extras`. All optional; validators treat `None` as “not provided”. Pydantic validators enforce non-negative values for `age`, `years_experience`, and `children`.
- **Issue** — Single finding: `field`, `description`, `severity` (enum: low/medium/high), `source` (rule/llm/system).
- **ValidationResult** — Output of validation: `confidence_score` (0–100), `status`, `issues[]`, `rule_summary`, `llm_summary`.
- **Severity** — `low`, `medium`, `high`.
- **IssueSource** — `rule`, `llm`, `system`.

---

## Validation Logic

### Rule-based checks (`rules_validator.py`)

1. **Age range** — Age &lt; `min_age` or &gt; `max_age` (configurable).
2. **Experience vs age** — `years_experience` cannot exceed `max(0, age - 15)`.
3. **Children vs age and marital status** — Age &lt; 18 with `children` &gt; 0; or marital status “Single” with `children` &gt; 0.
4. **Income vs employment** — Unemployed-like job titles with income above `unemployed_income_threshold`; student/intern with very high income.
5. **Income reasonableness** — Negative income; income above `max_reasonable_income`.
6. **Saudi context** — Low-income roles (e.g. student, intern, cashier) with very high income; unemployed keywords with high income; senior roles with very low income (SAR thresholds).

All rule issues have `source: "rule"` and a severity (medium/high as appropriate).

### LLM validation (`llm_validator.py`)

- Used only if `OPENAI_API_KEY` is set.
- Sends the survey response (as JSON) to OpenAI **Chat Completions** with a system prompt that defines “Semantic Guardian” and asks for JSON: `{ "issues": [...], "overall_comment": "..." }`.
- Response is parsed; each item becomes an `Issue` with `source: "llm"`.
- On any exception (e.g. API error, parse error), a single system issue is added and the API continues with rule-based results; no 500.

### Scoring (`validator_service.py`)

- Issues from rules and LLM are merged and deduplicated (by field, description, source).
- Score starts at 100; for each issue: low −3, medium −7, high −15; then clamped to 0–100.
- Status from score: ≥90 → high data reliability; ≥70 → minor issues; ≥40 → suspicious; &lt;40 → inconsistent.

---

## Deployment

### Backend (FastAPI API)

- **Render (recommended, free tier):** Connect the GitHub repo, create a **Web Service**, set **Runtime** to **Python 3** (or **Docker** if using the Dockerfile). For Python: **Build command** `pip install -r requirements.txt`, **Start command** `uvicorn main:app --host 0.0.0.0 --port $PORT`. Add `OPENAI_API_KEY` (and optionally `OPENAI_MODEL`) in Environment Variables. Free instances spin down after inactivity (cold start ~50 s on first request).
- **Docker:** `docker build -t semantic-guardian-api .` then `docker run -p 8000:8000 -e OPENAI_API_KEY=sk-... semantic-guardian-api`. The root `Dockerfile` runs `uvicorn main:app --host 0.0.0.0 --port 8000`.
- **Blueprint:** Optional `render.yaml` in the repo for Render Blueprint deploy (see `DEPLOY.md`).

### Dashboard (Streamlit)

- **Streamlit Community Cloud:** [share.streamlit.io](https://share.streamlit.io) → New app from GitHub repo, **Main file path** `dashboard.py`. Add `OPENAI_API_KEY` in Secrets if you want LLM in the cloud app.
- **Docker:** Use `Dockerfile.dashboard`; exposes port 8501 and runs `streamlit run dashboard.py`.

Detailed steps (including free hosting) are in **[DEPLOY.md](DEPLOY.md)**.

---

## Frontend Integration

- **Base URL** — Use your deployed API URL (e.g. `https://hackathon-beie.onrender.com`). No auth for the documented endpoints.
- **Documentation for frontend team** — Share **[API_FOR_FRONTEND.md](API_FOR_FRONTEND.md)** and the base URL, or point them to `{BASE_URL}/docs` for interactive Swagger.
- **CORS** — Enabled for all origins; frontends can call `/validate` and `/batch-validate` from any domain.

---

## License

This project was developed for educational and hackathon purposes. Use and modification are at your discretion; attribute the authors when sharing or building upon it.

---

*Semantic Guardian — Survey Data Validator*
