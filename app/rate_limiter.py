import time

from fastapi import HTTPException, Request


class TokenBucketRateLimiter:

    def __init__(
        self,
        capacity: int = 5,
        refill_rate: float = 1.0,
    ) -> None:
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.buckets = {}

    def _create_bucket(self) -> dict:
        return {
            "tokens": self.capacity,
            "last_refill_time": time.monotonic(),
        }

    def _get_bucket(self, client_key: str) -> dict:
        if client_key not in self.buckets:
            self.buckets[client_key] = self._create_bucket()
        return self.buckets[client_key]

    def _refill_bucket(self, bucket: dict) -> None:
        current_time = time.monotonic()
        elapsed_time = current_time - bucket["last_refill_time"]

        earned_tokens = elapsed_time * self.refill_rate
        new_tokens = min(self.capacity, bucket["tokens"] + earned_tokens)
        bucket["tokens"] = new_tokens
        bucket["last_refill_time"] = current_time

    def allow_request(self, client_key: str) -> bool:
        bucket = self._get_bucket(client_key)
        self._refill_bucket(bucket)

        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            return True

        return False

limiter = TokenBucketRateLimiter()

async def enforce_rate_limit(request: Request) -> None:
    client_key = request.client.host if request.client else "unknown-ip"

    if not limiter.allow_request(client_key):
            # PoC policy: one token refills per second, so clients can retry after
            # one second.
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={"Retry-After": "1"},
        )