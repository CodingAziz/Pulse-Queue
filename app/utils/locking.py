from datetime import datetime, timedelta
from sqlalchemy import and_
from app.extensions import db
from app.models.job import Job, JobStatus


def release_stale_locks(timeout_seconds: int = 60) -> int:
    """
    Releases jobs stuck in RUNNING state beyond visibility timeout.

    Returns number of jobs recovered.
    """

    now = datetime.utcnow()
    stale_threshold = now - timedelta(seconds=timeout_seconds)

    # Use FOR UPDATE to avoid multiple workers recovering same jobs
    stale_jobs = (
        Job.query
        .filter(
            and_(
                Job.status == JobStatus.RUNNING,
                Job.locked_at.isnot(None),
                Job.locked_at < stale_threshold
            )
        )
        .with_for_update(skip_locked=True)
        .all()
    )

    recovered_count = 0

    for job in stale_jobs:
        job.status = JobStatus.PENDING
        job.locked_at = None
        job.locked_by = None
        recovered_count += 1

    db.session.commit()

    return recovered_count