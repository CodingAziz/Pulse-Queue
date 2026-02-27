import random
from datetime import datetime, timedelta

class RetryService:

    def __init__(
        self,
        base_delay: int = 5,
        max_delay: int = 300,
        jitter: int = 5
    ):
        """
        base_delay: initial retry delay in seconds
        max_delay: maximum backoff cap
        jitter: random seconds added to prevent retry storms
        """
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter

    def calculate_next_retry(self, attempts: int) -> datetime:
        """
        Exponential backoff with jitter.
        """

        # Exponential backoff
        delay = self.base_delay * (2 ** (attempts - 1))

        # Cap the delay
        delay = min(delay, self.max_delay)

        # Add jitter
        delay += random.randint(0, self.jitter)

        return datetime.utcnow() + timedelta(seconds=delay)