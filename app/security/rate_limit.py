from __future__ import annotations

from fastapi import HTTPException, Request, status
from redis.asyncio import Redis

from app.core.config import get_settings


async def enforce_rate_limit(request: Request) -> None:
    settings = get_settings()
    client = Redis.from_url(settings.redis_url, decode_responses=True)
    key = f"rate:{request.client.host if request.client else 'unknown'}"
    try:
        async with client.pipeline(transaction=True) as pipe:
            pipe.incr(key)
            pipe.expire(key, settings.rate_limit_window_seconds, nx=True)
            count, _ = await pipe.execute()
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Rate limiter unavailable") from exc
    finally:
        await client.aclose()
    if count > settings.rate_limit_requests:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")
