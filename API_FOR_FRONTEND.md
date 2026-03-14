# Semantic Guardian – API for Frontend Team

Use this doc to integrate with the **Semantic Guardian** survey validation API.

---

## Base URL

**Production (replace after deploy):**

```
https://YOUR-BACKEND-URL
```

Example: `https://semantic-guardian-api.onrender.com` or `https://your-app.railway.app`

**OpenAPI (interactive docs):** `GET {BASE_URL}/docs`  
**OpenAPI JSON:** `GET {BASE_URL}/openapi.json`

---

## Endpoints

| Method | Path                    | Description                                      |
|--------|-------------------------|--------------------------------------------------|
| GET    | `/health`               | Health check                                    |
| GET    | `/survey-types`         | List survey type ids and names                   |
| GET    | `/survey-types/{id}`    | Get schema (questions, labels, question text)   |
| POST   | `/validate`             | Validate one response (or with survey_type/question_text) |
| POST   | `/batch-validate`       | Validate many responses (same body shapes)       |
| POST   | `/validate-from-text`   | Extract from natural language, then validate     |

---

## 1. Health check

**Request**

```http
GET /health
```

**Response**

```json
{ "status": "ok" }
```

---

## 2. Survey types

**GET /survey-types**

Returns: `[{ "survey_type": "labour_market", "name": "Labour Market Survey (Saudi context)" }, ...]`

**GET /survey-types/{survey_type}**

Returns full schema: `{ "survey_type": "...", "name": "...", "questions": [{ "id", "field", "label", "question_text", "value_type" }, ...] }`. 404 if not found.

---

## 3. Validate single response

**Request**

```http
POST /validate
Content-Type: application/json
```

**Body (two accepted shapes):**

- **Simple (backward compatible):** a single object with response fields only (no `response` key).
- **With context:** `{ "response": { ...same fields... }, "survey_type": "labour_market", "question_text": { "age": "What is your age?", "job_title": "..." } }`. Use `survey_type` to apply survey-specific thresholds; use `question_text` so the LLM can use question wording for smarter checks.

Example (simple):

```json
{
  "age": 30,
  "gender": "Female",
  "education": "Bachelor",
  "job_title": "Data Analyst",
  "years_experience": 5.0,
  "marital_status": "Single",
  "children": 0,
  "monthly_income": 4000.0
}
```

**Response**

```json
{
  "confidence_score": 85,
  "status": "high reliability",
  "issues": [
    {
      "field": "years_experience",
      "description": "Experience exceeds plausible range for age.",
      "severity": "medium",
      "source": "rule"
    }
  ],
  "rule_summary": "1 rule issue(s) found.",
  "llm_summary": null
}
```

**JavaScript example**

```js
const baseUrl = 'https://YOUR-BACKEND-URL';

const response = await fetch(`${baseUrl}/validate`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    age: 30,
    gender: 'Female',
    education: 'Bachelor',
    job_title: 'Data Analyst',
    years_experience: 5.0,
    marital_status: 'Single',
    children: 0,
    monthly_income: 4000.0,
  }),
});
const result = await response.json();
console.log(result.confidence_score, result.issues);
```

---

## 4. Batch validate

**Request**

```http
POST /batch-validate
Content-Type: application/json
```

**Body:** array of survey response objects (same shape as `/validate` body).

```json
[
  { "age": 25, "job_title": "Engineer", "years_experience": 3 },
  { "age": 45, "job_title": "Manager", "years_experience": 2 }
]
```

**Response:** array of validation results (same shape as single `/validate` response).

```json
[
  {
    "confidence_score": 90,
    "status": "high reliability",
    "issues": [],
    "rule_summary": null,
    "llm_summary": null
  },
  {
    "confidence_score": 65,
    "status": "suspicious",
    "issues": [
      {
        "field": "years_experience",
        "description": "Experience low for age.",
        "severity": "medium",
        "source": "rule"
      }
    ],
    "rule_summary": "1 rule issue(s) found.",
    "llm_summary": null
  }
]
```

**JavaScript example**

```js
const responses = [
  { age: 25, job_title: 'Engineer', years_experience: 3 },
  { age: 45, job_title: 'Manager', years_experience: 2 },
];
const res = await fetch(`${baseUrl}/batch-validate`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(responses),
});
const results = await res.json();
```

---

## 5. Validate from natural language

**POST /validate-from-text**

**Body:** `{ "text": "I am 30, male, engineer, 5 years experience, married, 2 children, income 8000 SAR", "survey_type": "labour_market", "language_hint": "en" }`. `survey_type` and `language_hint` are optional.

**Response:** `{ "extracted": SurveyResponse, "validation": ValidationResult, "parsing_issues": ["Could not determine ...", ...] }`

Requires `OPENAI_API_KEY` for extraction.

---

## Response types

- **confidence_score:** `0–100` (higher = better quality).
- **status:** e.g. `"high reliability"`, `"suspicious"`, `"inconsistent"`.
- **issues:** list of `{ field?, description, severity, source }`.
  - **severity:** `"low"` | `"medium"` | `"high"`.
  - **source:** `"rule"` | `"llm"` | `"system"`.

CORS is enabled for all origins; no auth required for these endpoints.
