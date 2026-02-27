import enum
import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    Enum,
    Text,
    JSON,
    Index
)
from sqlalchemy.dialects.postgresql import UUID
from app.extensions import db

# Job Lifecycle States
class JobStatus(enum.Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    RETRY = "retry"
    COMPLETED = "completed"
    FAILED = "failed"
    DEAD = "dead"

# Job Model
class Job(db.Model):
    __tablename__ = "jobs"

    # Identity
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Used for deduplication
    idempotency_key = Column(String(255), unique=True, index=True)

    # Core Job Data
    type = Column(String(100), nullable=False, index=True)
    payload = Column(JSON, nullable=False)

    # State Management
    status = Column(
        Enum(JobStatus),
        default=JobStatus.PENDING,
        nullable=False,
        index=True
    )

    priority = Column(Integer, default=0, index=True)

    # Scheduling
    scheduled_at = Column(DateTime, default=datetime.utcnow)
    available_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Retry Metadata
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=5)
    next_retry_at = Column(DateTime, index=True)
    last_error = Column(Text)

    # Locking (Distributed Workers)
    locked_at = Column(DateTime, index=True)
    locked_by = Column(String(100), index=True)

    # Observability
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    execution_time_ms = Column(Integer)

    # Indexes for Fast Fetching
    __table_args__ = (
        Index(
            "idx_job_fetch",
            "status",
            "priority",
            "available_at"
        ),
        Index(
            "idx_retry_lookup",
            "status",
            "next_retry_at"
        ),
    )

    # Utility Methods
    def mark_running(self, worker_id):
        self.status = JobStatus.RUNNING
        self.locked_at = datetime.utcnow()
        self.locked_by = worker_id
        self.started_at = datetime.utcnow()

    def mark_completed(self):
        self.status = JobStatus.COMPLETED
        self.finished_at = datetime.utcnow()
        self.locked_at = None
        self.locked_by = None

    def mark_failed(self, error_message):
        self.attempts += 1
        self.last_error = str(error_message)
        self.locked_at = None
        self.locked_by = None

        if self.attempts >= self.max_attempts:
            self.status = JobStatus.DEAD
        else:
            self.status = JobStatus.RETRY