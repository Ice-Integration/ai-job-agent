from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import ApplicationStatus, Candidate, Job
from app.infrastructure.tables import ApplicationRecord, CandidateRecord, JobRecord


def job_dedupe_key(job: Job) -> str:
    value = "|".join((job.company.strip().lower(), job.title.strip().lower(), job.application_url or ""))
    return hashlib.sha256(value.encode()).hexdigest()


def candidate_from_record(record: CandidateRecord) -> Candidate:
    return Candidate.model_validate(record.profile)


async def save_candidate(session: AsyncSession, user_id: UUID, candidate: Candidate) -> CandidateRecord:
    record = CandidateRecord(id=candidate.id, user_id=user_id, name=candidate.name, location=candidate.location, profile=candidate.model_dump(mode="json"), profile_text=candidate.profile_text)
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record


async def get_candidate(session: AsyncSession, user_id: UUID, candidate_id: UUID) -> CandidateRecord | None:
    return await session.scalar(select(CandidateRecord).where(CandidateRecord.id == candidate_id, CandidateRecord.user_id == user_id))


async def save_job(session: AsyncSession, job: Job) -> JobRecord:
    key = job_dedupe_key(job)
    statement = insert(JobRecord).values(id=job.id, title=job.title, company=job.company, description=job.description, source=job.source, application_url=job.application_url, dedupe_key=key, attributes=job.model_dump(mode="json")).on_conflict_do_update(index_elements=["dedupe_key"], set_={"description": job.description, "attributes": job.model_dump(mode="json")}).returning(JobRecord)
    record = await session.scalar(statement)
    await session.commit()
    return record


async def create_application(session: AsyncSession, user_id: UUID, candidate_id: UUID, job_id: UUID, match_score: float, resume: str, cover_letter: str) -> ApplicationRecord:
    if not await get_candidate(session, user_id, candidate_id):
        raise LookupError("Candidate not found")
    record = ApplicationRecord(candidate_id=candidate_id, job_id=job_id, match_score=match_score, status=ApplicationStatus.READY.value, package={"resume": resume, "cover_letter": cover_letter})
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record


async def get_application(session: AsyncSession, user_id: UUID, application_id: UUID) -> ApplicationRecord | None:
    statement = select(ApplicationRecord).join(CandidateRecord).where(ApplicationRecord.id == application_id, CandidateRecord.user_id == user_id)
    return await session.scalar(statement)


async def list_applications(session: AsyncSession, user_id: UUID) -> list[ApplicationRecord]:
    statement = select(ApplicationRecord).join(CandidateRecord).where(CandidateRecord.user_id == user_id).order_by(ApplicationRecord.created_at.desc())
    return list((await session.scalars(statement)).all())


async def transition_application(session: AsyncSession, user_id: UUID, application_id: UUID, expected: ApplicationStatus, target: ApplicationStatus) -> ApplicationRecord | None:
    statement = update(ApplicationRecord).where(ApplicationRecord.id == application_id, ApplicationRecord.status == expected.value, ApplicationRecord.candidate_id.in_(select(CandidateRecord.id).where(CandidateRecord.user_id == user_id))).values(status=target.value, applied_at=datetime.now(UTC) if target is ApplicationStatus.APPLIED else None).returning(ApplicationRecord)
    record = await session.scalar(statement)
    await session.commit()
    return record
