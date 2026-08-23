from __future__ import annotations

import structlog

from app.domain.models import Job
from app.services.job_sources import RemoteJobsSource

log = structlog.get_logger()


async def discover_jobs(endpoint: str, queries: list[str], limit_per_query: int = 20) -> list[Job]:
    source = RemoteJobsSource(endpoint)
    seen: set[str] = set()
    jobs: list[Job] = []
    for query in queries:
        for job in await source.search(query, limit_per_query):
            key = f"{job.company.lower()}::{job.title.lower()}::{job.application_url or ''}"
            if key in seen:
                continue
            seen.add(key)
            jobs.append(job)
    log.info("job_discovery_completed", queries=len(queries), jobs=len(jobs))
    return jobs
