from abc import ABC, abstractmethod

from app.domain.models import Job


class JobSource(ABC):
    name: str

    @abstractmethod
    async def search(self, query: str, limit: int = 20) -> list[Job]:
        raise NotImplementedError


class StaticJobSource(JobSource):
    """Safe local adapter used for development and evaluation fixtures."""

    name = "static"

    def __init__(self, jobs: list[Job] | None = None) -> None:
        self.jobs = jobs or []

    async def search(self, query: str, limit: int = 20) -> list[Job]:
        terms = set(query.lower().split())
        ranked = sorted(
            self.jobs,
            key=lambda job: len(terms & set(job.description.lower().split())),
            reverse=True,
        )
        return ranked[:limit]
