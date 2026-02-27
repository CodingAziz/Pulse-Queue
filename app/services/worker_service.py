import time
import uuid
from datetime import datetime
from app.repositories.job_repositories import JobRepository


class WorkerService:

    def __init__(self, lock_timeout=60, poll_interval=2):
        self.worker_id = f"worker-{uuid.uuid4()}"
        self.lock_timeout = lock_timeout
        self.poll_interval = poll_interval

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
            print(f"[WorkerService] Processing {job.id}")

            # Simulated execution
            time.sleep(3)

            JobRepository.complete_job(job)

        except Exception as e:
            JobRepository.fail_job(job, e)