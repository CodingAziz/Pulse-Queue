import time
from app.extensions import redis_client


class RateLimiterService:

    def __init__(
        self,
        capacity: int = 10,
        refill_rate: float = 1.0
    ):
        """
        capacity: max tokens
        refill_rate: tokens per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate

    def _get_bucket_key(self, client_id: str) -> str:
        return f"rate_limit:{client_id}"

    def allow_request(self, client_id: str) -> bool:
        key = self._get_bucket_key(client_id)

        current_time = time.time()

        bucket = redis_client.hmget(key, "tokens", "timestamp")

        if bucket[0] is None:
            # Initialize bucket
            redis_client.hmset(key, {
                "tokens": self.capacity - 1,
                "timestamp": current_time
            })
            redis_client.expire(key, 3600)
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

        redis_client.hmset(key, {
            "tokens": tokens,
            "timestamp": current_time
        })

        return True