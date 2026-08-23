from app.domain.models import SponsorshipStatus
from app.services.job_sources import classify_sponsorship, normalize_job


def test_no_sponsorship_wins_over_generic_sponsorship_keyword():
    assert classify_sponsorship("We do not offer visa sponsorship") is SponsorshipStatus.NO


def test_confirmed_sponsorship():
    assert classify_sponsorship("Visa sponsorship available for this role") is SponsorshipStatus.CONFIRMED


def test_worldwide_remote_infers_nigeria():
    job = normalize_job(
        {"title": "Backend Engineer", "company": "X", "description": "Remote worldwide Python role"}
    )
    assert job.remote is True
    assert "Nigeria" in job.remote_countries
