from datetime import datetime, timedelta
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session

from app.extensions import db
from app.models.job import Job, JobStatus
from app.utils.locking import release_stale_locks
from app.services.retry_service import RetryService
from app.repositories.dead_letter_repository import DeadLetterRepository

class JobRepository:

    # Create Job (Idempotent Safe)
    @staticmethod
    def create_job(
        type: str,
        payload: dict,
        priority: int = 0,
        scheduled_at: datetime = None,
        idempotency_key: str = None,
        max_attempts: int = 5
    ) -> Job:
      try:
        if idempotency_key:
            existing = Job.query.filter_by(
                idempotency_key=idempotency_key
            ).first()
            if existing:
                return existing

        now = datetime.utcnow()

        job = Job(
            type=type,
            payload=payload,
            priority=priority,
            status = (
                JobStatus.SCHEDULED
                if scheduled_at and scheduled_at > now
                else JobStatus.PENDING
            ),
            scheduled_at=scheduled_at or now,
            available_at=scheduled_at or now,
            idempotency_key=idempotency_key,
            max_attempts=max_attempts
        )

        db.session.add(job)
        db.session.commit()
        return job
      except Exception as e:
          db.session.rollback()
          print("[ERROR] Exception occured in creating job")

    # Fetch Due Scheduled Jobs
    @staticmethod
    def fetch_due_scheduled_jobs(limit: int = 100):
      try:
        now = datetime.utcnow()

        return (
            Job.query
            .filter(
                Job.status == JobStatus.SCHEDULED,
                Job.scheduled_at <= now
            )
            .order_by(Job.scheduled_at.asc())
            .limit(limit)
            .all()
        )
      except Exception as e:
        print("[ERROR] Exception occured")
    
    @staticmethod
    def promote_scheduled_jobs(jobs):
      try:
        for job in jobs:
            job.status = JobStatus.PENDING
            job.available_at = datetime.utcnow()

        db.session.commit()
      except Exception as e:
        db.session.rollback()
        print("[ERROR] Exception occured")

    # Fetch Next Available Job (LOCKED)
    @staticmethod
    def fetch_next_job(worker_id: str):
        """
        Priority scheduling with starvation prevention (aging).
        """
        try:
          now = datetime.utcnow()

          # Aging factor: 1 priority point per 30 seconds waited
          aging_seconds = 30

          effective_priority = (
              Job.priority +
              (func.extract('epoch', now - Job.created_at) / aging_seconds)
          )

          job = (
              Job.query
              .filter(
                  Job.status.in_([JobStatus.PENDING, JobStatus.RETRY]),
                  Job.available_at <= now,
                  Job.locked_at.is_(None)
              )
              .order_by(
                  effective_priority.desc(),
                  Job.available_at.asc()
              )
              .with_for_update(skip_locked=True)
              .first()
          )

          if not job:
              return None

          job.mark_running(worker_id)
          db.session.commit()

          return job
        except Exception as e:
          db.session.rollback()
          print("[ERROR] Exception occured")

    # Complete Job
    @staticmethod
    def complete_job(job: Job):
        try:
          job.mark_completed()
          db.session.commit()
        except Exception as e:
          db.session.rollback()
          print("[ERROR] Exception occured")

    # Fail Job (Exponential Backoff)
    @staticmethod
    def fail_job(job, error):
        try:
          from app.services.retry_service import RetryService

          retry_service = RetryService()

          job.attempts += 1
          job.last_error = str(error)
          job.locked_at = None
          job.locked_by = None

          if job.attempts >= job.max_attempts:
              DeadLetterRepository.move_to_dead_letter(job)
              return

          job.status = JobStatus.RETRY
          job.available_at = retry_service.calculate_next_retry(job.attempts)

          db.session.commit()
        except Exception as e:
          db.session.rollback()
          print("[ERROR] Exception occured")

    # Recover Stale Locks (Visibility Timeout)
    @staticmethod
    def recover_stale_jobs(timeout_seconds: int = 60):
      return release_stale_locks(timeout_seconds)

    # Move Retry Jobs Back To Pending
    @staticmethod
    def fetch_retry_ready_jobs():
        now = datetime.utcnow()

        return Job.query.filter(
            and_(
                Job.status == JobStatus.RETRY,
                Job.available_at <= now
            )
        ).all()

    # Get Job By ID
    @staticmethod
    def get_job(job_id):
        return Job.query.get(job_id)

    # Get Stats (Observability)
    @staticmethod
    def get_status_counts():
        return (
            db.session.query(
                Job.status,
                db.func.count(Job.id)
            )
            .group_by(Job.status)
            .all()
        )