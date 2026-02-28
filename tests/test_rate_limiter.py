class FakeRedis:
    def __init__(self):
        self.store = {}

    def hmget(self, key, *fields):
        if key not in self.store:
            return [None, None]
        return [self.store[key]["tokens"], self.store[key]["timestamp"]]

    def hmset(self, key, values):
        self.store[key] = values
        return True

    def expire(self, key, seconds):
        return True

def test_rate_limiter():
    from app.services.rate_limiter_service import RateLimiterService

    fake_redis = FakeRedis()

    limiter = RateLimiterService(
        capacity=2,
        refill_rate=0,
        redis_client=fake_redis
    )

    assert limiter.allow_request("test")
    assert limiter.allow_request("test")
    assert not limiter.allow_request("test")