import time
from app.repositories.job_repositories import JobRepository


class SchedulerService:

    def __init__(self, poll_interval=5):
        self.poll_interval = poll_interval

    def start(self):
        print("[Scheduler] Started")

        while True:
            try:
                jobs = JobRepository.fetch_due_scheduled_jobs()

                if jobs:
                    print(f"[Scheduler] Promoting {len(jobs)} jobs")
                    JobRepository.promote_scheduled_jobs(jobs)

                time.sleep(self.poll_interval)

            except Exception as e:
                print(f"[Scheduler] Error: {e}")
                time.sleep(5)