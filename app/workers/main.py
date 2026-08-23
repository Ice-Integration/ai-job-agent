from __future__ import annotations

import asyncio

from app.workers.scheduler import build_scheduler


async def main() -> None:
    scheduler = build_scheduler()
    scheduler.start()
    try:
        await asyncio.Event().wait()
    finally:
        scheduler.shutdown(wait=False)


if __name__ == "__main__":
    asyncio.run(main())
