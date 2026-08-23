from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Decision(StrEnum):
    APPLY = "APPLY"
    INVESTIGATE = "INVESTIGATE"
    REJECT = "REJECT"


class SponsorshipStatus(StrEnum):
    CONFIRMED = "CONFIRMED"
    LIKELY = "LIKELY"
    POSSIBLE = "POSSIBLE"
    UNKNOWN = "UNKNOWN"
    NOT_REQUIRED = "NOT_REQUIRED"
    NO = "NO"


class ApplicationStatus(StrEnum):
    READY = "ready"
    APPROVED = "approved"
    APPLIED = "applied"
    REJECTED = "rejected"


class Candidate(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    location: str = "Nigeria"
    target_roles: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    years_experience: float = 0
    remote_from_nigeria: bool = True
    requires_sponsorship: bool = True
    achievements: list[str] = Field(default_factory=list)
    profile_text: str = ""


class Job(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str
    company: str
    description: str
    location: str | None = None
    remote: bool = False
    remote_countries: list[str] = Field(default_factory=list)
    sponsorship: SponsorshipStatus = SponsorshipStatus.UNKNOWN
    source: str | None = None
    application_url: str | None = None


class Evidence(BaseModel):
    claim: str
    source: str
    excerpt: str
    confidence: float = Field(ge=0, le=1)


class JobScore(BaseModel):
    job_id: UUID
    overall: int = Field(ge=0, le=100)
    technical: int = Field(ge=0, le=100)
    experience: int = Field(ge=0, le=100)
    location: int = Field(ge=0, le=100)
    sponsorship: int = Field(ge=0, le=100)
    decision: Decision
    strengths: list[str] = Field(default_factory=list)
    missing_requirements: list[str] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)


class Application(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    candidate_id: UUID
    job_id: UUID
    match_score: float = Field(ge=0, le=100)
    resume_text: str = ""
    cover_letter: str = ""
    approval_required: bool = True
    status: ApplicationStatus = ApplicationStatus.READY
