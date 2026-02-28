from flask import Blueprint, request, jsonify
from app.services.job_service import JobService
from app.services.rate_limiter_service import RateLimiterService
from app.services.dead_letter_service import DeadLetterService

job_bp = Blueprint("jobs", __name__, url_prefix="/jobs")

# Create Job Endpoint
@job_bp.route("/", methods=["POST"])
def create_job():
    data = request.get_json()

    client_id = request.headers.get("X-Client-ID")

    if not client_id:
        return jsonify({"error": "Missing X-Client-ID header"}), 400

    rate_limiter = RateLimiterService(capacity=20, refill_rate=2)

    if not rate_limiter.allow_request(client_id):
        return jsonify({"error": "Rate limit exceeded"}), 429

    if not data or "type" not in data or "payload" not in data:
        return jsonify({"error": "Invalid request"}), 400

    job = JobService.create_job(data)

    return jsonify({
        "id": str(job.id),
        "status": job.status.value
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

# Dead Letter Queue Job Blueprint
@job_bp.route("/dead-letter/<dlq_id>/replay", methods=["POST"])
def replay_dead_letter(dlq_id):

    job = DeadLetterService.replay_job(dlq_id)

    if not job:
        return jsonify({"error": "Dead letter job not found"}), 404

    return jsonify({"replayed_job_id": str(job.id)})

# Metrics Endpoint
@job_bp.route("/metrics", methods=["GET"])
def metrics():

    stats = JobService.get_stats()

    total_jobs = sum(count for _, count in stats)

    return jsonify({
        "total_jobs": total_jobs,
        "status_breakdown": {
            status.value: count for status, count in stats
        }
    })