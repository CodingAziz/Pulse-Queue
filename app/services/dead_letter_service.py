from app.repositories.dead_letter_repository import DeadLetterRepository
from app.repositories.job_repository import JobRepository
from app.models.dead_letter_job import DeadLetterJob
from app.extensions import db


class DeadLetterService:

    @staticmethod
    def replay_job(dlq_id):

        dlq_job = DeadLetterJob.query.get(dlq_id)

        if not dlq_job:
            return None

        new_job = JobRepository.create_job(
            type=dlq_job.type,
            payload=dlq_job.payload,
            priority=0
        )

        db.session.delete(dlq_job)
        db.session.commit()

        return new_job