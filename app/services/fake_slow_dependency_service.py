import asyncio


class FakeSlowDependencyService:
    """Simulates a slow external dependency for resilience testing."""

    async def call(self, delay: float) -> dict:
        # The delay lets us reproduce slow-provider behavior without changing the database path.
        await asyncio.sleep(delay)
        return {"status": "success", "delay": delay}

