import asyncio

from fastapi import APIRouter, HTTPException, Query

from app.config import test_dependency_enabled, test_dependency_timeout_seconds
from app.services.test_dependency_service import TestDependencyService


router = APIRouter(prefix="/test", tags=["testing"])
test_dependency_bulkhead = asyncio.Semaphore(2)
test_dependency_admission = asyncio.Lock()

"""
Request arrives
  -> acquire admission lock
  -> check whether bulkhead is full
  -> acquire one bulkhead slot
  -> release admission lock
  -> run slow dependency
  -> release bulkhead slot in finally
  """
@router.get("/slow-dependency")
async def slow_dependency(
    delay: float = Query(default=0.0, ge=0.0, le=10.0),
) -> dict:

    if not test_dependency_enabled():
        raise HTTPException(status_code=404, detail="Test dependency disabled")

    async with test_dependency_admission:
        if test_dependency_bulkhead.locked():
            raise HTTPException(
                status_code=503,
                detail="Test dependency is at maximum capacity",
            )

        await test_dependency_bulkhead.acquire()

    test_service = TestDependencyService()

    try:
        return await asyncio.wait_for(
            test_service.call(delay),
            timeout=test_dependency_timeout_seconds(),
        )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Test dependency timed out",
        )
    finally:
        test_dependency_bulkhead.release()
