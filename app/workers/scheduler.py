from __future__ import annotations

import os

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.workers.discovery import discover_jobs

log = structlog.get_logger()


async def scheduled_discovery() -> None:
    endpoint = os.getenv("JOB_DISCOVERY_ENDPOINT", "https://remotive.com/api/remote-jobs")
    raw_queries = os.getenv(
        "JOB_DISCOVERY_QUERIES",
        "python backend engineer,senior python backend,AI backend engineer,software engineer",
    )
    queries = [item.strip() for item in raw_queries.split(",") if item.strip()]
    await discover_jobs(endpoint, queries, int(os.getenv("JOB_DISCOVERY_LIMIT", "20")))


def build_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(
        scheduled_discovery,
        "interval",
        hours=int(os.getenv("JOB_DISCOVERY_INTERVAL_HOURS", "6")),
        id="job-discovery",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    return scheduler
