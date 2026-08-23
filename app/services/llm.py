from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.domain.models import Candidate, Job


class LLMAnalysis(BaseModel):
    summary: str
    strengths: list[str] = Field(default_factory=list)
    concerns: list[str] = Field(default_factory=list)
    sponsorship_reasoning: str
    factuality_confidence: float = Field(ge=0, le=1)


class GeneratedText(BaseModel):
    content: str


class JobAnalyzer:
    def __init__(self) -> None:
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        self.model = settings.openai_model

    async def analyze(self, candidate: Candidate, job: Job) -> LLMAnalysis | None:
        if not self.client:
            return None
        response = await self.client.responses.parse(
            model=self.model,
            input=[
                {"role": "system", "content": (
                    "You are a factual job qualification analyst. Never invent candidate experience. "
                    "Separate confirmed facts from unknowns. Treat sponsorship as unknown unless evidence supports it."
                )},
                {"role": "user", "content": f"CANDIDATE:\n{candidate.model_dump_json()}\nJOB:\n{job.model_dump_json()}"},
            ],
            text_format=LLMAnalysis,
        )
        return response.output_parsed

    async def generate_resume(self, candidate: Candidate, job: Job) -> str:
        return await self._generate(
            "Create an ATS-friendly resume draft using only facts in the candidate profile. "
            "Prioritize evidence relevant to the target job. Never invent metrics, employers, dates, skills, or certifications.",
            candidate, job,
        )

    async def generate_cover_letter(self, candidate: Candidate, job: Job) -> str:
        return await self._generate(
            "Write a concise, specific cover letter for this job using only candidate-provided facts. "
            "Do not invent company knowledge or experience.", candidate, job,
        )

    async def _generate(self, instruction: str, candidate: Candidate, job: Job) -> str:
        if not self.client:
            return ""
        response = await self.client.responses.parse(
            model=self.model,
            input=[
                {"role": "system", "content": instruction},
                {"role": "user", "content": f"CANDIDATE:\n{candidate.model_dump_json()}\nJOB:\n{job.model_dump_json()}"},
            ],
            text_format=GeneratedText,
        )
        return response.output_parsed.content
