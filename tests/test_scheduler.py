from app.workers.scheduler import build_scheduler


def test_scheduler_registers_discovery_job() -> None:
    scheduler = build_scheduler()
    jobs = scheduler.get_jobs()
    assert len(jobs) == 1
    assert jobs[0].id == "job-discovery"
