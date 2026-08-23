from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import Application, ApplicationStatus
from app.infrastructure.tables import ApplicationRecord, CandidateRecord, JobRecord


async def save_candidate(session: AsyncSession, candidate) -> CandidateRecord:
    record = CandidateRecord(
        id=candidate.id,
        name=candidate.name,
        location=candidate.location,
        profile=candidate.model_dump(mode="json"),
        profile_text=candidate.profile_text,
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record


async def save_job(session: AsyncSession, job) -> JobRecord:
    record = JobRecord(
        id=job.id,
        title=job.title,
        company=job.company,
        description=job.description,
        source=job.source,
        application_url=job.application_url,
        attributes=job.model_dump(mode="json"),
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record


async def save_application(session: AsyncSession, application: Application) -> ApplicationRecord:
    record = ApplicationRecord(
        id=application.id,
        candidate_id=application.candidate_id,
        job_id=application.job_id,
        status=application.status.value,
        match_score=application.match_score,
        package={"resume": application.resume_text, "cover_letter": application.cover_letter},
        applied_at=datetime.now(UTC) if application.status is ApplicationStatus.APPLIED else None,
    )
    session.add(record)
    await session.commit()
    return record


async def list_persisted_applications(session: AsyncSession) -> list[ApplicationRecord]:
    result = await session.execute(select(ApplicationRecord).order_by(ApplicationRecord.created_at.desc()))
    return list(result.scalars())
