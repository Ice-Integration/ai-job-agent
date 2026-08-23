# AI Job Agent

AI Job Agent is a production-oriented AI engineering system for finding jobs that a candidate can realistically perform from Nigeria or relocate to with sponsorship, ranking those jobs against a verified candidate profile, preparing tailored application material, and tracking outcomes.

## Core workflow

```text
CV / permitted profile data
        |
        v
Candidate Knowledge Base
        |
        +----> Job Discovery
        |          |
        |          v
        |      Job Normalization
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
- Deterministic job qualification with explainable weighted scoring.
- Separate remote-from-Nigeria and sponsorship decisions.
- Sponsorship classification with confirmed, likely, possible, unknown and no states.
- Public job URL research.
- Pluggable JSON job-source adapter.
- OpenAI Responses API structured analysis.
- ATS-oriented resume generation using candidate facts only.
- Cover-letter generation using candidate facts only.
- Application preparation and lifecycle tracking.
- Mandatory human approval before an application can be marked applied.
- Functional browser dashboard for scoring and pipeline inspection.
- Pytest and Ruff CI.
- Docker Compose with PostgreSQL/pgvector and Redis infrastructure.
- Explicit compliance boundary for LinkedIn. The project does not scrape or automate prohibited LinkedIn activity.

## Safety model

The language model does not authorize actions. Application code controls validation, persistence and state transitions.

The agent must not invent employers, dates, skills, certifications, projects, metrics, salary history or work authorization. Sponsorship is never treated as confirmed without supporting evidence.

Application submission remains a human-controlled boundary. The system prepares and tracks applications but does not implement prohibited automated LinkedIn interactions.

## Stack

Python 3.12, FastAPI, Pydantic, OpenAI Responses API, SQLAlchemy, PostgreSQL/pgvector, Redis, HTTPX, PyPDF, python-docx, Docker, GitHub Actions, Pytest, Ruff and OpenTelemetry.

## Run locally

```bash
cp .env.example .env
# Add OPENAI_API_KEY for LLM features.
docker compose up --build
```

API: http://localhost:8000
Swagger: http://localhost:8000/docs
Dashboard: open `web/index.html` after starting the API.

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

Prepare an application:

```text
POST /api/v1/applications/prepare
```

Then explicitly approve it:

```text
POST /api/v1/applications/{id}/approve
```

Only an approved application can transition to `applied`.

## Testing

```bash
pip install -e '.[dev]'
ruff check .
pytest -q
```

## Architecture principles

1. Deterministic rules own authorization and state transitions.
2. LLMs provide reasoning and generation, not permissions.
3. Candidate claims must be grounded in candidate evidence.
4. Remote eligibility is distinct from visa sponsorship.
5. Unknown sponsorship stays unknown.
6. Application submission requires explicit human approval.
7. Job sources are adapters so providers can be added without changing the domain.
8. Evaluation and factuality checks are part of the application design.

## Roadmap

The repository is structured for the next production hardening steps: persistent SQLAlchemy repositories, pgvector candidate retrieval, company research connectors, additional public job-source adapters, scheduled discovery workers, OpenTelemetry traces, evaluation datasets, authentication/RBAC, rate limiting, encrypted document storage, deployment manifests and a full React/TypeScript dashboard.

## Portfolio value

This project demonstrates backend engineering and AI engineering together: clean domain models, deterministic scoring, RAG-ready knowledge storage, structured LLM outputs, tool adapters, document ingestion, human approval, evaluation, security boundaries, Docker and CI/CD.
