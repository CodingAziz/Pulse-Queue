from flask_sqlalchemy import SQLAlchemy
import redis
import os

db = SQLAlchemy()

def get_redis_client():
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        db=0,
        decode_responses=True
    )

redis_client = get_redis_client()