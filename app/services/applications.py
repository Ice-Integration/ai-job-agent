from __future__ import annotations

from uuid import UUID, uuid4

from app.domain.models import Application, ApplicationStatus

_store: dict[UUID, Application] = {}


def create_application(candidate_id: UUID, job_id: UUID, match_score: float, resume: str = "", cover_letter: str = "") -> Application:
    application = Application(
        id=uuid4(),
        candidate_id=candidate_id,
        job_id=job_id,
        match_score=match_score,
        resume_text=resume,
        cover_letter=cover_letter,
        status=ApplicationStatus.READY,
    )
    _store[application.id] = application
    return application


def list_applications() -> list[Application]:
    return list(_store.values())


def get_application(application_id: UUID) -> Application | None:
    return _store.get(application_id)


def approve_application(application_id: UUID) -> Application:
    application = _store[application_id]
    if application.approval_required is not True:
        raise ValueError("Invalid approval state")
    application.status = ApplicationStatus.APPROVED
    return application


def mark_applied(application_id: UUID) -> Application:
    application = _store[application_id]
    if application.status != ApplicationStatus.APPROVED:
        raise ValueError("Application must be approved before it can be marked applied")
    application.status = ApplicationStatus.APPLIED
    return application
