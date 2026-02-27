from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models.job import Job

jobs_bp = Blueprint("jobs", __name__)

@jobs_bp.route("/jobs", methods=["POST"])
def create_job():
    data = request.get_json()

    if not data or "payload" not in data:
        return {"error": "payload is required"}, 400

    job = Job(payload=data["payload"])
    db.session.add(job)
    db.session.commit()

    return jsonify(job.to_dict()), 201


@jobs_bp.route("/jobs", methods=["GET"])
def get_jobs():
    jobs = Job.query.all()
    return jsonify([j.to_dict() for j in jobs])