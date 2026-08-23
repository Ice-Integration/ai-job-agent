from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.agents.qualification import score_job
from app.domain.models import Candidate, Job, JobScore
from app.services.llm import JobAnalyzer

app = FastAPI(title="AI Job Agent", version="0.1.0")
candidates: dict[str, Candidate] = {}


class ScoreRequest(BaseModel):
    candidate: Candidate
    job: Job


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/candidates", response_model=Candidate)
async def create_candidate(candidate: Candidate) -> Candidate:
    candidates[str(candidate.id)] = candidate
    return candidate


@app.get("/api/v1/candidates/{candidate_id}", response_model=Candidate)
async def get_candidate(candidate_id: str) -> Candidate:
    candidate = candidates.get(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


@app.post("/api/v1/jobs/score", response_model=JobScore)
async def score(request: ScoreRequest) -> JobScore:
    result = score_job(request.candidate, request.job)
    analysis = await JobAnalyzer().analyze(request.candidate, request.job)
    if analysis:
        result.strengths = analysis.strengths or result.strengths
        result.missing_requirements = analysis.concerns or result.missing_requirements
        result.confidence = min(result.confidence, analysis.factuality_confidence)
    return result
