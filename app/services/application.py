from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ApplicationStatus(StrEnum):
    READY = "READY"
    APPROVED = "APPROVED"
    APPLIED = "APPLIED"
    REJECTED = "REJECTED"


class ApplicationDraft(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    candidate_id: UUID
    job_id: UUID
    resume_text: str
    cover_letter: str
    answers: dict[str, str] = Field(default_factory=dict)
    status: ApplicationStatus = ApplicationStatus.READY


class ApprovalService:
    def approve(self, draft: ApplicationDraft) -> ApplicationDraft:
        if draft.status is not ApplicationStatus.READY:
            raise ValueError("Only READY applications can be approved")
        draft.status = ApplicationStatus.APPROVED
        return draft

    def mark_applied(self, draft: ApplicationDraft) -> ApplicationDraft:
        if draft.status is not ApplicationStatus.APPROVED:
            raise ValueError("Application requires explicit approval before submission")
        draft.status = ApplicationStatus.APPLIED
        return draft
