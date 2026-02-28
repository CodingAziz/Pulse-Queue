def test_priority_ordering(app):
    from app.repositories.job_repository import JobRepository

    with app.app_context():
        JobRepository.create_job(
            type="low",
            payload={},
            priority=1
        )

        JobRepository.create_job(
            type="high",
            payload={},
            priority=10
        )

        job = JobRepository.fetch_next_job("worker1")

        assert job.type == "high"

def test_scheduler_promotes(app):
    from datetime import datetime, timedelta
    from app.repositories.job_repository import JobRepository
    from app.models.job import JobStatus

    with app.app_context():
        future_time = datetime.utcnow() + timedelta(seconds=5)

        job = JobRepository.create_job(
            type="delayed",
            payload={},
            scheduled_at=future_time
        )

        assert job.status == JobStatus.SCHEDULED