import time
import uuid
from app.extensions import db
from app.models.job import JobStatus
from app.repositories.job_repository import JobRepository
from app.services.rate_limiter_service import RateLimiterService
import logging
from datetime import datetime

class WorkerService:

    def __init__(self, lock_timeout=60, poll_interval=2):
        self.worker_id = f"worker-{uuid.uuid4()}"
        self.lock_timeout = lock_timeout
        self.poll_interval = poll_interval
        self.rate_limiter = RateLimiterService(
            capacity=50,
            refill_rate=5
        )
        self.logger = logging.getLogger("WorkerService")

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
          start_time = datetime.utcnow()

          if not self.rate_limiter.allow_request("worker"):
              self.logger.warning("Worker rate limited")
              time.sleep(1)
              return

          self.logger.info(f"Processing job {job.id}")

          # Simulated execution
          time.sleep(3)

          execution_time = (
              datetime.utcnow() - start_time
          ).total_seconds() * 1000

          job.execution_time_ms = int(execution_time)

          JobRepository.complete_job(job)

          self.logger.info(
              f"Completed job {job.id} in {execution_time:.2f} ms"
          )

      except Exception as e:
          self.logger.error(
              f"Job {job.id} failed: {str(e)}"
          )
          JobRepository.fail_job(job, e)