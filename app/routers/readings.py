"""Sensor reading ingestion endpoints."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Reading
from app.repository import ReadingRepository
from app.schemas import AggregatedReadingResponse, Metric, ReadingCreate, ReadingOut, Statistic
from app.services.query_service import QueryReadingService

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


@router.get(
    "/readings",
    response_model=list[AggregatedReadingResponse],
)
async def query_readings(
    sensor_ids: list[str] | None = Query(default=None),
    metrics: list[Metric] | None = Query(default=None),
    statistic: Statistic | None = Query(default=None),
    days: int | None = Query(default=None, ge=1, le=30),
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    repository = ReadingRepository(session)
    service = QueryReadingService(repository)

    return await service.aggregate(
        sensor_ids=sensor_ids,
        metrics=metrics,
        statistic=statistic,
        days=days,
    )