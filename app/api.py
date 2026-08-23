from __future__ import annotations

from uuid import UUID

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from pydantic import BaseModel, HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.qualification import score_job
from app.core.auth import require_bearer
from app.core.config import get_settings
from app.domain.models import ApplicationStatus, Candidate, Evidence, Job, JobScore
from app.infrastructure.database import get_db
from app.infrastructure.tables import DocumentRecord
from app.security.rate_limit import enforce_rate_limit
from app.services.authentication import authenticate_user, register_user
from app.services.documents import extract_candidate_signals, extract_text
from app.services.generation import generate_cover_letter, generate_resume
from app.services.job_sources import RemoteJobsSource
from app.services.llm import JobAnalyzer
from app.services.persistence import (
    candidate_from_record,
    create_application,
    get_application,
    list_applications,
    save_candidate,
    save_job,
    transition_application,
)
from app.services.persistence import (
    get_candidate as get_persisted_candidate,
)
from app.services.rag import CandidateRAG
from app.services.storage import store_document
from app.services.web_research import fetch_job_url

app = FastAPI(title="AI Job Agent", version="0.6.0", dependencies=[Depends(enforce_rate_limit)])


class ScoreRequest(BaseModel):
    candidate: Candidate
    job: Job


class ApplicationCreate(BaseModel):
    candidate: Candidate
    job: Job
    score: JobScore


class DiscoverRequest(BaseModel):
    query: str
    endpoint: HttpUrl
    limit: int = 20


class JobURLRequest(BaseModel):
    url: HttpUrl


class AuthRequest(BaseModel):
    email: str
    password: str


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "ai-job-agent"}


@app.post("/api/v1/auth/register")
async def register(request: AuthRequest, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    if len(request.password) < 12:
        raise HTTPException(status_code=422, detail="Password must contain at least 12 characters")
    try:
        token = await register_user(db, request.email, request.password)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {"access_token": token, "token_type": "bearer"}


@app.post("/api/v1/auth/login")
async def login(request: AuthRequest, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    token = await authenticate_user(db, request.email, request.password)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"access_token": token, "token_type": "bearer"}


@app.post("/api/v1/candidates", response_model=Candidate)
async def create_candidate(candidate: Candidate, db: AsyncSession = Depends(get_db), user_id: str = Depends(require_bearer)) -> Candidate:
    await save_candidate(db, UUID(user_id), candidate)
    return candidate


@app.get("/api/v1/candidates/{candidate_id}", response_model=Candidate)
async def get_candidate(candidate_id: UUID, db: AsyncSession = Depends(get_db), user_id: str = Depends(require_bearer)) -> Candidate:
    candidate = await get_persisted_candidate(db, UUID(user_id), candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate_from_record(candidate)


@app.post("/api/v1/candidates/import", response_model=Candidate)
async def import_cv(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), user_id: str = Depends(require_bearer)) -> Candidate:
    data = await file.read()
    if len(data) > get_settings().max_upload_bytes:
        raise HTTPException(status_code=413, detail="Document exceeds configured upload limit")
    text = extract_text(file.filename or "cv.txt", data)
    signals = extract_candidate_signals(text)
    candidate = Candidate(name="Imported Candidate", skills=list(signals["skills"]), profile_text=str(signals["profile_text"]))
    await save_candidate(db, UUID(user_id), candidate)
    storage_key, digest = store_document(candidate.id, data)
    db.add(DocumentRecord(candidate_id=candidate.id, storage_key=storage_key, sha256=digest, content_type=file.content_type or "application/octet-stream", size_bytes=len(data)))
    await db.commit()
    await CandidateRAG().index(db, candidate.id, candidate.profile_text)
    return candidate


@app.post("/api/v1/jobs/from-url", response_model=Job)
async def job_from_url(request: JobURLRequest, db: AsyncSession = Depends(get_db), _: str = Depends(require_bearer)) -> Job:
    job = await fetch_job_url(str(request.url))
    await save_job(db, job)
    return job


@app.post("/api/v1/jobs/discover", response_model=list[Job])
async def discover(request: DiscoverRequest, db: AsyncSession = Depends(get_db), _: str = Depends(require_bearer)) -> list[Job]:
    jobs = await RemoteJobsSource(str(request.endpoint)).search(request.query, request.limit)
    for job in jobs:
        await save_job(db, job)
    return jobs


@app.post("/api/v1/jobs/score", response_model=JobScore)
async def score(request: ScoreRequest, db: AsyncSession = Depends(get_db), user_id: str = Depends(require_bearer)) -> JobScore:
    owned_candidate = await get_persisted_candidate(db, UUID(user_id), request.candidate.id)
    if owned_candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    candidate = candidate_from_record(owned_candidate)
    result = score_job(candidate, request.job)
    retrieved = await CandidateRAG().search(db, candidate.id, f"{request.job.title} {request.job.description}")
    result.evidence.extend(Evidence(claim="Candidate knowledge-base match", source=item.source, excerpt=item.text[:500], confidence=min(1.0, item.score)) for item in retrieved)
    analysis = await JobAnalyzer().analyze(candidate, request.job)
    if analysis:
        result.strengths = analysis.strengths or result.strengths
        result.missing_requirements = analysis.concerns or result.missing_requirements
        result.confidence = min(result.confidence, analysis.factuality_confidence)
    return result


@app.post("/api/v1/applications/prepare")
async def prepare_application(request: ApplicationCreate, db: AsyncSession = Depends(get_db), user_id: str = Depends(require_bearer)):
    resume = await generate_resume(request.candidate, request.job)
    cover_letter = await generate_cover_letter(request.candidate, request.job)
    job = await save_job(db, request.job)
    try:
        return await create_application(db, UUID(user_id), request.candidate.id, job.id, request.score.overall, resume, cover_letter)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/v1/applications")
async def applications(db: AsyncSession = Depends(get_db), user_id: str = Depends(require_bearer)):
    return await list_applications(db, UUID(user_id))


@app.get("/api/v1/applications/{application_id}")
async def application(application_id: UUID, db: AsyncSession = Depends(get_db), user_id: str = Depends(require_bearer)):
    item = await get_application(db, UUID(user_id), application_id)
    if not item:
        raise HTTPException(status_code=404, detail="Application not found")
    return item


@app.post("/api/v1/applications/{application_id}/approve")
async def approve(application_id: UUID, db: AsyncSession = Depends(get_db), user_id: str = Depends(require_bearer)):
    item = await transition_application(db, UUID(user_id), application_id, ApplicationStatus.READY, ApplicationStatus.APPROVED)
    if item is None:
        raise HTTPException(status_code=409, detail="Application cannot be approved")
    return item


@app.post("/api/v1/applications/{application_id}/mark-applied")
async def applied(application_id: UUID, db: AsyncSession = Depends(get_db), user_id: str = Depends(require_bearer)):
    item = await transition_application(db, UUID(user_id), application_id, ApplicationStatus.APPROVED, ApplicationStatus.APPLIED)
    if item is None:
        raise HTTPException(status_code=409, detail="Application must be approved before being marked applied")
    return item
