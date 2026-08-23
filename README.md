# AI Job Agent

AI Job Agent is a production-oriented AI engineering system for finding jobs that a candidate can realistically perform from Nigeria or relocate to with sponsorship, ranking those jobs against a verified candidate profile, preparing tailored application material, and tracking outcomes.

## Core workflow

```text
CV / permitted profile data
        |
        v
Candidate Knowledge Base
        |
        +----> Scheduled Job Discovery
        |          |
        |          v
        |      Job Normalization / Deduplication
        |          |
        |          v
        +----> Qualification Engine
                   |
          +--------+--------+
          |                 |
   Remote from Nigeria   Sponsorship
          |                 |
          +--------+--------+
                   |
                   v
             Match + Evidence
                   |
          +--------+--------+
          |                 |
       Resume          Cover Letter
          |                 |
          +--------+--------+
                   v
            Human Approval
                   |
                   v
             Application
                   |
                   v
             Feedback/Evals
```

## Implemented capabilities

- Candidate profile storage and CV import.
- PDF, DOCX, TXT and Markdown text extraction.
- PostgreSQL persistence through SQLAlchemy and Alembic.
- JWT authentication and Argon2 password hashing.
- Candidate knowledge chunks and pgvector-ready retrieval.
- OpenAI embeddings for candidate evidence retrieval.
- Deterministic job qualification with explainable weighted scoring.
- Separate remote-from-Nigeria and sponsorship decisions.
- Sponsorship classification with confirmed, likely, possible, unknown and no states.
- Public job URL research.
- Pluggable JSON job-source adapter.
- Scheduled job discovery worker with configurable queries, interval and deduplication.
- Docker Compose API, worker, PostgreSQL/pgvector and Redis services.
- OpenAI Responses API structured analysis.
- ATS-oriented resume generation using candidate facts only.
- Cover-letter generation using candidate facts only.
- Application preparation and lifecycle tracking.
- Mandatory human approval before an application can be marked applied.
- Functional browser dashboard for scoring and pipeline inspection.
- Pytest and Ruff CI.
- OpenTelemetry foundation.
- Explicit compliance boundary for LinkedIn. The project does not scrape or automate prohibited LinkedIn activity.

## Safety model

The language model does not authorize actions. Application code controls validation, persistence and state transitions.

The agent must not invent employers, dates, skills, certifications, projects, metrics, salary history or work authorization. Sponsorship is never treated as confirmed without supporting evidence.

Application submission remains a human-controlled boundary. The system prepares and tracks applications but does not implement prohibited automated LinkedIn interactions.

## Stack

Python 3.12, FastAPI, Pydantic, OpenAI Responses API, SQLAlchemy, PostgreSQL/pgvector, Redis, APScheduler, HTTPX, PyPDF, python-docx, Docker, GitHub Actions, Pytest, Ruff and OpenTelemetry.

## Run locally

```bash
cp .env.example .env
# Add OPENAI_API_KEY for LLM features.
docker compose up --build
```

API: http://localhost:8000
Swagger: http://localhost:8000/docs
Dashboard: open `web/index.html` after starting the API.

The worker runs independently and performs scheduled discovery. Configure `JOB_DISCOVERY_QUERIES`, `JOB_DISCOVERY_INTERVAL_HOURS`, `JOB_DISCOVERY_ENDPOINT`, and `JOB_DISCOVERY_LIMIT` in `.env`.

Without an OpenAI key, deterministic qualification and application workflow still operate. LLM analysis and generation fall back safely.

## Main API

Health:

```bash
curl http://localhost:8000/health
```

Score a job:

```bash
curl -X POST http://localhost:8000/api/v1/jobs/score \
  -H 'content-type: application/json' \
  -d '{"candidate":{"name":"Austin Benjamin","target_roles":["Senior Python Backend Engineer"],"skills":["Python","FastAPI","PostgreSQL","Docker","Pytest"],"years_experience":5},"job":{"title":"Senior Python Backend Engineer","company":"Example","description":"Python FastAPI PostgreSQL Docker Pytest","remote":true,"remote_countries":["Nigeria"],"sponsorship":"NOT_REQUIRED"}}'
```

Import a CV:

```bash
curl -X POST http://localhost:8000/api/v1/candidates/import -F 'file=@CV.pdf'
```

Research a job URL:

```bash
curl -X POST http://localhost:8000/api/v1/jobs/from-url \
  -H 'content-type: application/json' \
  -d '{"url":"https://example.com/jobs/backend-engineer"}'
```
