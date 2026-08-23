from __future__ import annotations

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.agents.qualification import score_job
from app.domain.models import Candidate, Job, JobScore
from app.services.applications import (
    approve_application,
    create_application,
    get_application,
    list_applications,
    mark_applied,
)
from app.services.documents import extract_candidate_signals, extract_text
from app.services.generation import generate_cover_letter, generate_resume
from app.services.llm import JobAnalyzer

app = FastAPI(title="AI Job Agent", version="0.2.0")
candidates: dict[str, Candidate] = {}


class ScoreRequest(BaseModel):
    candidate: Candidate
    job: Job


class ApplicationCreate(BaseModel):
    candidate: Candidate
    job: Job
    score: JobScore


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


@app.post("/api/v1/candidates/import")
async def import_cv(file: UploadFile = File(...)) -> Candidate:
    data = await file.read()
    text = extract_text(file.filename or "cv.txt", data)
    signals = extract_candidate_signals(text)
    candidate = Candidate(
        name="Imported Candidate",
        skills=list(signals["skills"]),
        profile_text=str(signals["profile_text"]),
    )
    candidates[str(candidate.id)] = candidate
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


@app.post("/api/v1/applications/prepare")
async def prepare_application(request: ApplicationCreate):
    resume = await generate_resume(request.candidate, request.job)
    cover_letter = await generate_cover_letter(request.candidate, request.job)
    return create_application(request.candidate.id, request.job.id, request.score.overall, resume, cover_letter)


@app.get("/api/v1/applications")
async def applications():
    return list_applications()


@app.post("/api/v1/applications/{application_id}/approve")
async def approve(application_id: str):
    try:
        return approve_application(__import__("uuid").UUID(application_id))
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/v1/applications/{application_id}/mark-applied")
async def applied(application_id: str):
    try:
        return mark_applied(__import__("uuid").UUID(application_id))
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/v1/applications/{application_id}")
async def application(application_id: str):
    item = get_application(__import__("uuid").UUID(application_id))
    if not item:
        raise HTTPException(status_code=404, detail="Application not found")
    return item
