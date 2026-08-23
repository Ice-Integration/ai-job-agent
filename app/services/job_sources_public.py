from __future__ import annotations

import httpx

from app.domain.models import Job
from app.services.job_sources import normalize_job


class GreenhouseSource:
    name = "greenhouse"

    def __init__(self, board_token: str):
        self.board_token = board_token

    async def search(self, limit: int = 100) -> list[Job]:
        url = f"https://boards-api.greenhouse.io/v1/boards/{self.board_token}/jobs"
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(url, params={"content": "true"})
            response.raise_for_status()
            payload = response.json()
        return [normalize_job(item, self.name) for item in payload.get("jobs", [])[:limit]]


class LeverSource:
    name = "lever"

    def __init__(self, site: str):
        self.site = site

    async def search(self, limit: int = 100) -> list[Job]:
        url = f"https://api.lever.co/v0/postings/{self.site}"
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(url, params={"mode": "json"})
            response.raise_for_status()
            payload = response.json()
        jobs: list[Job] = []
        for item in payload[:limit]:
            jobs.append(
                normalize_job(
                    {
                        "title": item.get("text"),
                        "company": self.site,
                        "description": item.get("descriptionPlain") or item.get("description"),
                        "location": (item.get("categories") or {}).get("location"),
                        "url": item.get("hostedUrl") or item.get("applyUrl"),
                        "remote": "remote" in str(item).lower(),
                    },
                    self.name,
                )
            )
        return jobs
