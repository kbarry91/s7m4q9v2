import asyncio
from types import SimpleNamespace

from app.schemas import Statistic
from app.services.query_service import QueryReadingService


class FakeReadingRepository:
	"""Records repository calls without using a real database."""

	def __init__(self, rows):
		self.rows = rows
		self.latest_calls = []
		self.aggregate_calls = []

	async def get_latest(self, sensor_ids, metrics):
		self.latest_calls.append((sensor_ids, metrics))
		return self.rows

	async def get_aggregate(
		self,
		sensor_ids,
		metrics,
		statistic,
		start_timestamp,
		end_timestamp,
	):
		self.aggregate_calls.append(
			{
				"sensor_ids": sensor_ids,
				"metrics": metrics,
				"statistic": statistic,
				"start_timestamp": start_timestamp,
				"end_timestamp": end_timestamp,
			}
		)
		return self.rows


def test_latest_mode_uses_latest_repository_method():
	# Arrange: provide one fake database row.
	fake_repository = FakeReadingRepository(
		[SimpleNamespace(sensor_id="sensor-1", metric="temperature", value=21.4)]
	)
	service = QueryReadingService(fake_repository)

	# Act: omit days so the service should use latest mode.
	response = asyncio.run(
		service.aggregate(
			sensor_ids=["sensor-1"],
			metrics=["temperature"],
			statistic=None,
			days=None,
		)
	)

	# Assert: latest mode and repository method selection are correct.
	assert response == [
		{
			"sensor_id": "sensor-1",
			"metric": "temperature",
			"statistic": "latest",
			"value": 21.4,
		}
	]
	assert fake_repository.latest_calls == [(["sensor-1"], ["temperature"])]
	assert fake_repository.aggregate_calls == []


def test_days_mode_defaults_to_average_and_passes_lookback():
	# Arrange: provide one fake aggregate row.
	fake_repository = FakeReadingRepository(
		[SimpleNamespace(sensor_id="sensor-1", metric="temperature", value=20.0)]
	)
	service = QueryReadingService(fake_repository)

	# Act: provide days but omit the statistic.
	response = asyncio.run(
		service.aggregate(
			sensor_ids=None,
			metrics=["temperature"],
			statistic=None,
			days=8,
		)
	)

	# Assert: aggregation defaults to average and creates a valid lookback.
	assert response[0]["statistic"] == "avg"
	assert response[0]["value"] == 20.0
	assert fake_repository.latest_calls == []
	assert len(fake_repository.aggregate_calls) == 1
	assert fake_repository.aggregate_calls[0]["statistic"] == Statistic.avg
	assert (
		fake_repository.aggregate_calls[0]["end_timestamp"]
		> fake_repository.aggregate_calls[0]["start_timestamp"]
	)
