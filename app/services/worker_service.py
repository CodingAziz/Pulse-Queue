import time
import uuid
from extensions import db
from app.models.job import JobStatus
from app.repositories.job_repository import JobRepository
from app.services.rate_limiter_service import RateLimiterService

class WorkerService:

    def __init__(self, lock_timeout=60, poll_interval=2):
        self.worker_id = f"worker-{uuid.uuid4()}"
        self.lock_timeout = lock_timeout
        self.poll_interval = poll_interval
        self.rate_limiter = RateLimiterService(
            capacity=50,
            refill_rate=5
        )

    # Main Loop
    def start(self):
        print(f"[WorkerService] Started: {self.worker_id}")

        while True:
            try:
                # Recover crashed jobs
                JobRepository.recover_stale_jobs(self.lock_timeout)

                job = JobRepository.fetch_next_job(self.worker_id)

                if not job:
                    time.sleep(self.poll_interval)
                    continue

                self.process_job(job)

            except Exception as e:
                print(f"[WorkerService] Unexpected error: {e}")
                time.sleep(5)

    # Process Job
    def process_job(self, job):
        try:
            # Rate limit actual execution
            if not self.rate_limiter.allow_request("worker"):
              job.locked_at = None
              job.locked_by = None
              job.status = JobStatus.PENDING
              db.session.commit()
              time.sleep(1)
              return

            print(f"[WorkerService] Processing {job.id}")

            # Simulated execution
            time.sleep(3)

            JobRepository.complete_job(job)

        except Exception as e:
            JobRepository.fail_job(job, e)