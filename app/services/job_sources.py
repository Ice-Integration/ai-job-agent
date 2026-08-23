from __future__ import annotations

import re
from abc import ABC, abstractmethod

import httpx

from app.domain.models import Job, SponsorshipStatus


class JobSource(ABC):
    name = "base"

    @abstractmethod
    async def search(self, query: str, limit: int = 20) -> list[Job]:
        raise NotImplementedError


class RemoteJobsSource(JobSource):
    """Adapter for a public JSON endpoint. Configure the endpoint in production."""
    name = "remote-json"

    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    async def search(self, query: str, limit: int = 20) -> list[Job]:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(self.endpoint, params={"search": query, "limit": limit})
            response.raise_for_status()
            payload = response.json()
        return [normalize_job(item, self.name) for item in payload.get("jobs", [])[:limit]]


def normalize_job(item: dict, source: str = "unknown") -> Job:
    description = str(item.get("description") or item.get("body") or "")
    title = str(item.get("title") or "Untitled role")
    company = str(item.get("company") or item.get("company_name") or "Unknown company")
    remote_countries = [str(x) for x in item.get("remote_countries", [])]
    location = str(item.get("location") or "")
    remote = bool(item.get("remote")) or "remote" in f"{description} {location}".lower()
    if remote and not remote_countries:
        remote_countries = infer_remote_countries(f"{description} {location}")
    sponsorship = classify_sponsorship(description)
    return Job(
        title=title,
        company=company,
        description=description,
        source=source,
        remote=remote,
        remote_countries=remote_countries,
        location=location or None,
        sponsorship=sponsorship,
        application_url=item.get("application_url") or item.get("url"),
    )


def infer_remote_countries(text: str) -> list[str]:
    value = re.sub(r"\s+", " ", text.lower())
    countries = []
    if "nigeria" in value or "africa" in value or "emea" in value or "worldwide" in value:
        countries.append("Nigeria")
    if any(p in value for p in ["us only", "united states only", "usa only"]):
        return ["United States"]
    return countries


def classify_sponsorship(text: str) -> SponsorshipStatus:
    value = re.sub(r"\s+", " ", text.lower())
    if any(p in value for p in ["no sponsorship", "without sponsorship", "will not sponsor", "sponsorship is not available"]):
        return SponsorshipStatus.NO
    if any(p in value for p in ["visa sponsorship available", "will sponsor", "sponsorship provided"]):
        return SponsorshipStatus.CONFIRMED
    if any(p in value for p in ["visa sponsorship", "immigration support", "relocation assistance"]):
        return SponsorshipStatus.LIKELY
    if any(p in value for p in ["sponsorship", "work permit support"]):
        return SponsorshipStatus.POSSIBLE
    return SponsorshipStatus.UNKNOWN
