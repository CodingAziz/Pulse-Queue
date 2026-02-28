from flask import Blueprint, jsonify
from app.extensions import db, redis_client
import logging

health_bp = Blueprint("health", __name__)

logger = logging.getLogger("HealthCheck")


@health_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@health_bp.route("/health/db", methods=["GET"])
def health_db():
    try:
        db.session.execute("SELECT 1")
        return jsonify({"database": "ok"})
    except Exception as e:
        logger.error(f"DB health check failed: {str(e)}")
        return jsonify({"database": "error"}), 500


@health_bp.route("/health/redis", methods=["GET"])
def health_redis():
    try:
        redis_client.ping()
        return jsonify({"redis": "ok"})
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")
        return jsonify({"redis": "error"}), 500