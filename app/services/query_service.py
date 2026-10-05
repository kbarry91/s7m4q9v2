from datetime import datetime, timedelta, timezone

from app.repository import ReadingRepository
from app.schemas import Statistic


class QueryReadingService:

    def __init__(self, repository: ReadingRepository) -> None:
        self.repository = repository

    async def aggregate(
        self,
        sensor_ids: list[str] | None,
        metrics: list[str] | None,
        statistic: Statistic,
        days: int | None,
    ) -> list[dict]:
        if days is None:
            response_statistic = Statistic.latest
            response_rows = await self.repository.get_latest(
                sensor_ids=sensor_ids,
                metrics=metrics,
            )
        else:
            aggregation_statistic = statistic or Statistic.avg

            end_timestamp = datetime.now(timezone.utc)
            start_timestamp = end_timestamp - timedelta(days=days)
            response_rows = await self.repository.get_aggregate(
                sensor_ids=sensor_ids,
                metrics=metrics,
                statistic=aggregation_statistic,
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp,
            )
            response_statistic = aggregation_statistic

        # Map the response rows to dictionaries
        response_dicts = [
            {
                "sensor_id": row.sensor_id,
                "metric": row.metric,
                "statistic": response_statistic.value,
                "value": row.value,
            }
            for row in response_rows
        ]

        return response_dicts
