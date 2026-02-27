from datetime import datetime
from ..extensions import db

class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)

    payload = db.Column(db.JSON, nullable=False)

    status = db.Column(
        db.String(50),
        default="PENDING",
        index=True,
        nullable=False
    )

    # Scheduling
    scheduled_at = db.Column(db.DateTime, nullable=True, index=True)

    # Retry metadata
    retry_count = db.Column(db.Integer, default=0)
    max_retries = db.Column(db.Integer, default=3)

    # Observability
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "status": self.status,
            "retry_count": self.retry_count,
            "created_at": self.created_at,
        }