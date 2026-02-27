from datetime import datetime
from app.repositories.job_repository import JobRepository


class JobService:

    @staticmethod
    def create_job(data):
        return JobRepository.create_job(
            type=data["type"],
            payload=data["payload"],
            priority=data.get("priority", 0),
            scheduled_at=data.get("scheduled_at"),
            idempotency_key=data.get("idempotency_key"),
            max_attempts=data.get("max_attempts", 5)
        )

    @staticmethod
    def get_job(job_id):
        return JobRepository.get_job(job_id)

    @staticmethod
    def get_stats():
        return JobRepository.get_status_counts()