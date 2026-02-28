import time

class RateLimiterService:

    def __init__(self, capacity=10, refill_rate=1.0, redis_client=None):
        self.capacity = capacity
        self.refill_rate = refill_rate
        from app.extensions import redis_client as default_redis
        self.redis = redis_client or default_redis

    def _get_bucket_key(self, client_id: str) -> str:
        return f"rate_limit:{client_id}"

    def allow_request(self, client_id: str) -> bool:
        key = self._get_bucket_key(client_id)

        current_time = time.time()

        bucket = self.redis.hmget(key, "tokens", "timestamp")

        if bucket[0] is None:
            # Initialize bucket
            self.redis.hmset(key, {
                "tokens": self.capacity - 1,
                "timestamp": current_time
            })
            self.redis.expire(key, 3600)
            return True

        tokens = float(bucket[0])
        last_timestamp = float(bucket[1])

        # Refill tokens
        elapsed = current_time - last_timestamp
        refill = elapsed * self.refill_rate
        tokens = min(self.capacity, tokens + refill)

        if tokens < 1:
            return False

        tokens -= 1

        self.redis.hmset(key, {
            "tokens": tokens,
            "timestamp": current_time
        })

        return True