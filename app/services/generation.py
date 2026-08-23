from __future__ import annotations

from app.domain.models import Candidate, Job
from app.services.llm import JobAnalyzer


async def generate_resume(candidate: Candidate, job: Job) -> str:
    analyzer = JobAnalyzer()
    if analyzer.client:
        return await analyzer.generate_resume(candidate, job)
    return _fallback_resume(candidate, job)


async def generate_cover_letter(candidate: Candidate, job: Job) -> str:
    analyzer = JobAnalyzer()
    if analyzer.client:
        return await analyzer.generate_cover_letter(candidate, job)
    return (
        f"Dear Hiring Team,\n\nI am applying for the {job.title} position at {job.company}. "
        f"My background includes {', '.join(candidate.skills[:6])}, with {candidate.years_experience:g} "
        "years of professional experience. I would welcome the opportunity to discuss how my backend "
        "engineering experience can contribute to your team.\n\nSincerely,\n"
        f"{candidate.name}"
    )


def _fallback_resume(candidate: Candidate, job: Job) -> str:
    skills = ", ".join(candidate.skills)
    return (
        f"{candidate.name}\n\n{job.title} | Target Role\n\n"
        f"{candidate.profile_text}\n\nRelevant skills: {skills}\n\n"
        "This document contains only candidate-provided facts."
    )
