import asyncio

from fastapi import APIRouter, HTTPException, Query

from app.config import get_test_dependency_timeout_seconds, is_test_dependency_enabled
from app.services.fake_slow_dependency_service import FakeSlowDependencyService


router = APIRouter(prefix="/test", tags=["testing"])
# This endpoint is disabled by default and exists only to exercise resilience behavior.
# Enable it with TEST_DEPENDENCY_ENABLED=true when starting the application.
test_dependency_bulkhead = asyncio.Semaphore(2)
test_dependency_admission = asyncio.Lock()

# Admission is serialized only long enough to check capacity and claim a slot.
# The semaphore then limits slow dependency calls to two concurrent operations.
@router.get("/slow-dependency")
async def slow_dependency(
    delay: float = Query(default=0.0, ge=0.0, le=10.0),
) -> dict:

    if not is_test_dependency_enabled():
        raise HTTPException(status_code=404, detail="Test dependency disabled")

    async with test_dependency_admission:
        if test_dependency_bulkhead.locked():
            raise HTTPException(
                status_code=503,
                detail="Test dependency is at maximum capacity",
            )

        await test_dependency_bulkhead.acquire()

    test_service = FakeSlowDependencyService()

    try:
        # Stop waiting for a slow dependency after the configured timeout.
        return await asyncio.wait_for(
            test_service.call(delay),
            timeout=get_test_dependency_timeout_seconds(),
        )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Test dependency timed out",
        )
    finally:
        # Always return the slot, including when the call times out.
        test_dependency_bulkhead.release()
