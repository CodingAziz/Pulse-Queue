# app/routes/job_routes.py

from flask import Blueprint, request, jsonify
from app.services.job_service import JobService

job_bp = Blueprint("jobs", __name__, url_prefix="/jobs")

# Create Job
@job_bp.route("/", methods=["POST"])
def create_job():
    data = request.get_json()

    if not data or "type" not in data or "payload" not in data:
        return jsonify({"error": "Invalid request"}), 400

    job = JobService.create_job(data)

    return jsonify({
        "id": str(job.id),
        "status": job.status.value,
        "priority": job.priority
    }), 201

# Get Job Status
@job_bp.route("/<job_id>", methods=["GET"])
def get_job(job_id):
    job = JobService.get_job(job_id)

    if not job:
        return jsonify({"error": "Job not found"}), 404

    return jsonify({
        "id": str(job.id),
        "status": job.status.value,
        "attempts": job.attempts,
        "last_error": job.last_error
    })

# Metrics Endpoint
@job_bp.route("/metrics", methods=["GET"])
def metrics():
    stats = JobService.get_stats()

    return jsonify({
        status.value: count for status, count in stats
    })