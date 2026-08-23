import re

from app.domain.models import Candidate


def extract_candidate_from_text(name: str, text: str) -> Candidate:
    lower = text.lower()
    known_skills = [
        "python", "fastapi", "flask", "postgresql", "mysql", "docker", "pytest",
        "tdd", "sql", "aws", "azure", "gcp", "kubernetes", "linux", "graphql",
        "redis", "typescript", "javascript", "rust", "java"
    ]
    skills = [skill for skill in known_skills if skill in lower]
    years = 0.0
    match = re.search(r"(\d+(?:\.\d+)?)\+?\s+years", lower)
    if match:
        years = float(match.group(1))
    return Candidate(name=name, skills=skills, years_experience=years, profile_text=text)
