from app.agents.qualification import score_job
from app.domain.models import Candidate, Decision, Job, SponsorshipStatus


def candidate() -> Candidate:
    return Candidate(
        name="Austin Benjamin",
        target_roles=["Senior Python Backend Engineer"],
        skills=["Python", "FastAPI", "PostgreSQL", "Docker", "Pytest", "SQL"],
        years_experience=5,
    )


def test_strong_nigeria_remote_job_is_apply():
    job = Job(
        title="Senior Python Backend Engineer",
        company="Example",
        description="Build Python FastAPI services with PostgreSQL, Docker and Pytest.",
        remote=True,
        remote_countries=["Nigeria", "UK"],
        sponsorship=SponsorshipStatus.NOT_REQUIRED,
    )
    result = score_job(candidate(), job)
    assert result.decision is Decision.APPLY
    assert result.overall >= 80


def test_us_only_job_is_rejected_for_nigeria_remote_candidate():
    job = Job(
        title="Backend Engineer",
        company="Example",
        description="Python backend services",
        remote=True,
        remote_countries=["United States"],
        sponsorship=SponsorshipStatus.NO,
    )
    result = score_job(candidate(), job)
    assert result.decision is Decision.REJECT
    assert result.location == 0
