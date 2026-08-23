import re

from app.domain.models import Candidate, Decision, Job, JobScore


def _tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-zA-Z0-9+#.]+", text.lower()) if len(t) > 2}


def score_job(candidate: Candidate, job: Job) -> JobScore:
    description = _tokens(job.description)
    skills = {s.lower() for s in candidate.skills}
    matched = sorted(s for s in skills if s in description)
    technical = round(min(100, len(matched) / max(1, min(len(skills), 12)) * 100))

    role_tokens = _tokens(" ".join(candidate.target_roles))
    title_tokens = _tokens(job.title)
    role_match = len(role_tokens & title_tokens) / max(1, len(role_tokens & set(list(role_tokens))))
    experience = min(100, round(70 + technical * 0.3))

    country_set = {c.lower() for c in job.remote_countries}
    location = 100 if "nigeria" in country_set else (70 if job.remote and not country_set else 0)
    sponsorship = {
        "CONFIRMED": 100,
        "LIKELY": 85,
        "POSSIBLE": 60,
        "UNKNOWN": 40,
        "NOT_REQUIRED": 100,
        "NO": 0,
    }[job.sponsorship.value]

    overall = round(technical * 0.35 + experience * 0.25 + location * 0.20 + sponsorship * 0.20)
    if location == 0 and candidate.remote_from_nigeria:
        decision = Decision.REJECT
    elif overall >= 80:
        decision = Decision.APPLY
    elif overall >= 65:
        decision = Decision.INVESTIGATE
    else:
        decision = Decision.REJECT

    missing = sorted(skills - description)
    return JobScore(
        job_id=job.id,
        overall=overall,
        technical=technical,
        experience=experience,
        location=location,
        sponsorship=sponsorship,
        decision=decision,
        strengths=matched,
        missing_requirements=missing[:10],
        confidence=min(0.99, 0.55 + overall / 250),
    )
