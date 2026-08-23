from pydantic import BaseModel, Field
from openai import AsyncOpenAI

from app.core.config import get_settings
from app.domain.models import Candidate, Job


class LLMAnalysis(BaseModel):
    summary: str
    strengths: list[str] = Field(default_factory=list)
    concerns: list[str] = Field(default_factory=list)
    sponsorship_reasoning: str
    factuality_confidence: float = Field(ge=0, le=1)


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
                {
                    "role": "system",
                    "content": (
                        "You are a factual job qualification analyst. Never invent candidate "
                        "experience. Distinguish unknown sponsorship from confirmed sponsorship."
                    ),
                },
                {
                    "role": "user",
                    "content": f"CANDIDATE:\n{candidate.model_dump_json()}\nJOB:\n{job.model_dump_json()}",
                },
            ],
            text_format=LLMAnalysis,
        )
        return response.output_parsed
