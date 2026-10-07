"""Data-access layer: the only place that talks to the database."""

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.persistence.models import Reading
from app.schemas import Statistic

STATISTIC_FUNCTIONS = {
    Statistic.min: func.min,
    Statistic.max: func.max,
    Statistic.avg: func.avg,
    Statistic.sum: func.sum,
}


class ReadingRepository:
    """Persists and retrieves Reading rows."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, reading: Reading) -> Reading:
        try:
            self.session.add(reading)
            await self.session.commit()
            await self.session.refresh(reading)
            return reading
        except Exception:
            await self.session.rollback()
            raise

    async def get_aggregate(
        self,
        sensor_ids: list[str] | None,
        metrics: list[str] | None,
        statistic: Statistic,
        start_timestamp: datetime,
        end_timestamp: datetime,
    ) -> list:
        agg = STATISTIC_FUNCTIONS[statistic](Reading.value)

        stmt = select(
            Reading.sensor_id,
            Reading.metric,
            agg.label("value"),
        ).where(
            Reading.timestamp >= start_timestamp,
            Reading.timestamp <= end_timestamp,
        )

        if sensor_ids:
            stmt = stmt.where(Reading.sensor_id.in_(sensor_ids))

        if metrics:
            stmt = stmt.where(Reading.metric.in_(metrics))

        stmt = stmt.group_by(Reading.sensor_id, Reading.metric)
        result = await self.session.execute(stmt)
        return result.all()

    async def get_latest(
        self,
        sensor_ids: list[str] | None,
        metrics: list[str] | None,
    ) -> list:
        ranked_readings = select(
            Reading.sensor_id,
            Reading.metric,
            Reading.value,
            func.row_number()
            .over(
                partition_by=(Reading.sensor_id, Reading.metric),
                order_by=(Reading.timestamp.desc(), Reading.id.desc()),
            )
            .label("row_number"),
        )

        if sensor_ids:
            ranked_readings = ranked_readings.where(Reading.sensor_id.in_(sensor_ids))

        if metrics:
            ranked_readings = ranked_readings.where(Reading.metric.in_(metrics))
        # create a subquery to further filter only the latest readings
        latest_readings = ranked_readings.subquery()
        stmt = select(
            latest_readings.c.sensor_id,
            latest_readings.c.metric,
            latest_readings.c.value,
        ).where(latest_readings.c.row_number == 1)

        result = await self.session.execute(stmt)
        return result.all()
