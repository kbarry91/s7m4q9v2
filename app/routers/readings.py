"""Sensor reading ingestion endpoints."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Reading
from app.repository import ReadingRepository
from app.schemas import ReadingCreate, ReadingOut

router = APIRouter(tags=["readings"])


@router.post(
    "/readings",
    status_code=status.HTTP_201_CREATED,
    response_model=ReadingOut,
)
async def create_reading(
    payload: ReadingCreate,
    session: AsyncSession = Depends(get_session),
) -> Reading:
    # TODO:
    #  1. Build a Reading ORM object from `payload`. Apply the timestamp default:
    #     use payload.timestamp, or datetime.now(timezone.utc) if it is None.
    #  2. Persist it via ReadingRepository(session).add(...)
    #  3. Return the saved reading (FastAPI serializes it to ReadingOut).
    reading = Reading(
        sensor_id=payload.sensor_id,
        metric=payload.metric,
        value=payload.value,
        timestamp=payload.timestamp or datetime.now(timezone.utc),
    )

    # id is added once the reading is persisted in the database
    #saved_reading = await ReadingRepository(session).add(reading)
    await ReadingRepository(session).add(reading)
    
    return reading
