from app.extensions import db
from app.models.dead_letter_job import DeadLetterJob


class DeadLetterRepository:

    @staticmethod
    def move_to_dead_letter(job, reason="max_attempts_exceeded"):

        dlq_job = DeadLetterJob(
            original_job_id=job.id,
            type=job.type,
            payload=job.payload,
            attempts=job.attempts,
            last_error=job.last_error,
            reason=reason
        )

        db.session.add(dlq_job)
        db.session.delete(job)
        db.session.commit()

        return dlq_job