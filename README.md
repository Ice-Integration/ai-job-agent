# AI Job Agent

AI-powered job discovery, qualification, research, application preparation, and tracking for remote roles and visa-sponsored opportunities.

## What it does

- Ingests a candidate CV into a structured candidate profile.
- Normalizes job descriptions from URLs or pasted text.
- Scores jobs against the candidate using deterministic rules plus an LLM explanation layer.
- Separates remote-from-Nigeria eligibility from visa sponsorship analysis.
- Produces evidence-backed recommendations instead of unsupported claims.
- Prepares tailored resume and cover-letter inputs.
- Tracks applications and outcomes.
- Keeps submission behind an explicit human approval boundary.

## Architecture

```text
CV / profile
     |
     v
Candidate Knowledge Base ---> PostgreSQL + pgvector
     |
     v
Job Discovery ---> Normalization ---> Qualification Engine
                                      |
                         +------------+------------+
                         |                         |
                  Remote eligibility        Sponsorship
                         |                         |
                         +------------+------------+
                                      v
                               Match + Evidence
                                      |
                          Resume / Cover Letter
                                      |
                               Human Approval
                                      |
                               Application
                                      |
                              Feedback / Evals
```

## Stack

Python 3.12, FastAPI, Pydantic, SQLAlchemy, PostgreSQL, pgvector, OpenAI Responses API, Redis, React/TypeScript, Docker, GitHub Actions, Pytest, Ruff, OpenTelemetry.

## Safety and compliance

The LLM does not authorize actions. Authorization, validation, persistence, and application approval stay in application code. The project does not scrape or automate prohibited LinkedIn activity. LinkedIn data must come from user-provided or permitted sources.

## Quick start

```bash
cp .env.example .env
# set OPENAI_API_KEY when using LLM features
docker compose up --build
```

API: `http://localhost:8000`
Docs: `http://localhost:8000/docs`

## API examples

Create a candidate:

```bash
curl -X POST http://localhost:8000/api/v1/candidates \
  -H 'content-type: application/json' \
  -d '{"name":"Austin Benjamin","location":"Nigeria","target_roles":["Senior Python Backend Engineer","Backend Engineer"]}'
```

Score a job:

```bash
curl -X POST http://localhost:8000/api/v1/jobs/score \
  -H 'content-type: application/json' \
  -d '{"candidate_id":"<id>","title":"Senior Python Backend Engineer","company":"Example","description":"Python FastAPI PostgreSQL Docker and REST APIs","remote":true,"remote_countries":["Nigeria"]}'
```

## Development

```bash
pip install -e '.[dev]'
ruff check .
pytest -q
```

## Roadmap

1. Candidate profile and CV ingestion
2. Job normalization and deterministic qualification
3. Evidence-backed LLM scoring
4. Public job-source connectors
5. Resume and cover-letter generation
6. Application tracker
7. Human approval workflow
8. Evaluation datasets and tracing
9. React dashboard
10. Production deployment
