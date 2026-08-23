from __future__ import annotations

import re
from urllib.parse import urlparse

import httpx

from app.domain.models import Job
from app.services.job_sources import classify_sponsorship


async def fetch_job_url(url: str) -> Job:
    async with httpx.AsyncClient(timeout=20, follow_redirects=True, headers={"user-agent": "AI-Job-Agent/1.0"}) as client:
        response = await client.get(url)
        response.raise_for_status()
    text = _html_to_text(response.text)
    title = _title(response.text) or "Job opportunity"
    host = urlparse(str(response.url)).netloc
    return Job(
        title=title[:200],
        company=host,
        description=text[:30000],
        application_url=str(response.url),
        source="web",
        remote="remote" in text.lower(),
        sponsorship=classify_sponsorship(text),
    )


def _title(html: str) -> str:
    match = re.search(r"<title[^>]*>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
    return re.sub(r"\s+", " ", match.group(1)).strip() if match else ""


def _html_to_text(html: str) -> str:
    text = re.sub(r"<(script|style|noscript)[^>]*>.*?</\1>", " ", html, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()
