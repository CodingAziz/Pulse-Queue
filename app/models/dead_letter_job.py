import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.extensions import db


class DeadLetterJob(db.Model):
    __tablename__ = "dead_letter_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    original_job_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    type = Column(String(100), nullable=False)
    payload = Column(JSON, nullable=False)

    attempts = Column(String)
    last_error = Column(Text)

    failed_at = Column(DateTime, default=datetime.utcnow)

    reason = Column(String(255))