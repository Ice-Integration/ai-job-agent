from uuid import uuid4

import pytest

from app.services.applications import approve_application, create_application, mark_applied


def test_application_requires_approval_before_applied():
    application = create_application(uuid4(), uuid4(), 91)
    with pytest.raises(ValueError):
        mark_applied(application.id)
    approved = approve_application(application.id)
    assert approved.status.value == "approved"
    applied = mark_applied(application.id)
    assert applied.status.value == "applied"
