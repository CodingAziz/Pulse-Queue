def test_retry_backoff():
    from app.services.retry_service import RetryService

    retry = RetryService(base_delay=5, max_delay=100, jitter=0)

    next_time = retry.calculate_next_retry(3)

    assert next_time is not None