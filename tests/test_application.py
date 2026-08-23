import pytest
from uuid import uuid4

from app.services.application import ApprovalService, ApplicationDraft, ApplicationStatus


def draft() -> ApplicationDraft:
    return ApplicationDraft(
        candidate_id=uuid4(),
        job_id=uuid4(),
        resume_text="resume",
        cover_letter="letter",
    )


def test_application_requires_approval():
    service = ApprovalService()
    with pytest.raises(ValueError):
        service.mark_applied(draft())


def test_approved_application_can_be_marked_applied():
    service = ApprovalService()
    approved = service.approve(draft())
    applied = service.mark_applied(approved)
    assert applied.status is ApplicationStatus.APPLIED
