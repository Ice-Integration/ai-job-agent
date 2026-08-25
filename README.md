# AI Job Agent

An AI-native job discovery and application platform built to demonstrate end-to-end venture engineering: turning an ambiguous problem into a working product, connecting LLM capabilities to deterministic software, and keeping high-impact decisions observable, explainable, and human-controlled.

The system finds relevant opportunities, determines whether a candidate can realistically pursue them from Nigeria or through visa sponsorship, retrieves supporting candidate evidence, prepares tailored application material, and tracks outcomes.

> Portfolio focus: AI agents, product engineering, LLM integration, retrieval, structured outputs, workflow automation, evaluation, safety boundaries, and production-oriented backend architecture.

## Why this project

AI venture engineering is not only about calling an LLM. A useful product needs reliable data flows, deterministic business rules, clear failure modes, human control, and a fast path from idea to usable software.

This project combines those concerns in one product:

- LLM-powered reasoning where language understanding adds value.
- Deterministic qualification where correctness and explainability matter.
- Retrieval grounded in candidate-owned evidence.
- Structured outputs that can move through application workflows.
- Scheduled discovery and background processing.
- Human approval at the point where an external action would occur.
- Feedback and evaluation hooks for improving system quality over time.

## Product workflow

```text
Candidate CV / permitted profile data
                |
                v
       Candidate Knowledge Base
                |
        +-------+--------+
        |                |
        v                v
  Job Discovery     Direct Job URL
        |                |
        +-------+--------+
                v
       Normalize / Deduplicate
                |
                v
        Qualification Engine
                |
        +-------+--------+
        |                |
        v                v
Remote from Nigeria   Sponsorship
        |                |
        +-------+--------+
                v
       Match + Evidence
                |
        +-------+--------+
        |                |
        v                v
     Resume         Cover Letter
        |                |
        +-------+--------+
                v
         Human Approval
                |
                v
        Application State
                |
                v
        Feedback / Evals
```

## Engineering highlights

- Candidate profile storage and CV ingestion.
- PDF, DOCX, TXT and Markdown text extraction.
- PostgreSQL persistence with SQLAlchemy and Alembic.
- JWT authentication and Argon2 password hashing.
- Candidate knowledge chunks with pgvector-ready retrieval.
- OpenAI embeddings for evidence retrieval.
- OpenAI Responses API for structured AI analysis.
- Deterministic, explainable weighted job qualification.
- Separate remote-from-Nigeria and sponsorship decisions.
- Sponsorship classification across confirmed, likely, possible, unknown and no states.
- Public job URL research and pluggable JSON job-source integration.
- Scheduled discovery worker with configurable queries, intervals and deduplication.
- Resume and cover-letter generation grounded in candidate facts.
- Application preparation and lifecycle tracking.
- Functional browser dashboard for scoring and pipeline inspection.
- Docker Compose development environment with API, worker, PostgreSQL/pgvector and Redis.
- Pytest and Ruff CI.
- OpenTelemetry foundation for observability.

## AI architecture principles

The project deliberately separates probabilistic AI behavior from deterministic application behavior.

The language model can interpret and generate. It does not own application state, authorization, validation, or external-action decisions.

Candidate evidence provides grounding for generated material. The system is designed to prevent unsupported claims about employers, dates, skills, certifications, projects, metrics, salary history, or work authorization.

Job qualification uses deterministic scoring alongside AI analysis so that important decisions remain inspectable rather than becoming an opaque LLM judgment.

The application boundary remains human-controlled. The system prepares and tracks applications but does not implement prohibited automated LinkedIn interactions.

## Venture engineering decisions

1. Start with a real user problem

The product targets a concrete workflow: discovering suitable jobs, filtering opportunities that are actually actionable, and reducing the repetitive work involved in preparing applications.

2. Use AI where it creates leverage

LLMs handle semantic analysis, evidence-aware generation, and unstructured job/profile interpretation. Conventional code handles persistence, scoring rules, validation, scheduling, authentication, and state transitions.

3. Design for iteration

Job sources, discovery queries, qualification logic, prompts, and evaluation signals are separated so the product can evolve without rewriting the core workflow.

4. Keep the human in control

The system can prepare an application, but a human remains responsible for the final external action.

5. Make failure safer

Unknown sponsorship status is not silently treated as confirmed. Missing AI configuration does not prevent deterministic workflows from operating. Generated application content is constrained by candidate evidence.

## Stack

Python 3.12, FastAPI, Pydantic, OpenAI Responses API, SQLAlchemy, PostgreSQL/pgvector, Redis, APScheduler, HTTPX, PyPDF, python-docx, Docker, GitHub Actions, Pytest, Ruff and OpenTelemetry.

## Local development

```bash
cp .env.example .env
# Add OPENAI_API_KEY for LLM features.
docker compose up --build
```

API: `http://localhost:8000`

Swagger: `http://localhost:8000/docs`

Dashboard: open `web/index.html` after starting the API.

The worker runs independently and performs scheduled discovery. Configure `JOB_DISCOVERY_QUERIES`, `JOB_DISCOVERY_INTERVAL_HOURS`, `JOB_DISCOVERY_ENDPOINT`, and `JOB_DISCOVERY_LIMIT` in `.env`.

Without an OpenAI key, deterministic qualification and application workflow still operate. LLM analysis and generation fall back safely.

## API examples

Health check:

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

## What this demonstrates

This repository is intended as a practical engineering portfolio rather than an LLM demo. It demonstrates the ability to take a product problem from concept to implementation and combine AI capabilities with backend engineering, data modeling, workflow orchestration, security, testing, observability, and product constraints.

The project is especially relevant to teams building AI-native products where engineers are expected to move quickly from an idea to a working prototype, validate the result, and then harden the architecture around what users actually need.

## Responsible automation

The system is designed around a clear compliance boundary. It does not scrape or automate prohibited LinkedIn activity. Application submission remains a human-controlled step.

## Repository

GitHub: https://github.com/Ice-Integration/ai-job-agent
