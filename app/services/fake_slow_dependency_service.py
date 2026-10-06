import asyncio


class FakeSlowDependencyService:
    """Simulates a slow external dependency for resilience testing."""

    async def call(self, delay: float) -> dict:
        await asyncio.sleep(delay)
        return {"status": "success", "delay": delay}

