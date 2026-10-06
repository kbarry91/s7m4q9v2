from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.rate_limiter import limiter


def test_readings_average_over_lookback_period():
    sensor_id = "integration-query-average-test"
    readings = [10.0, 20.0, 30.0]
    limiter.buckets.clear()

    # Given known readings have been persisted for one sensor.
    with TestClient(app) as client:
        for value in readings:
            response = client.post(
                "/readings",
                json={
                    "sensor_id": sensor_id,
                    "metric": "temperature",
                    "value": value,
                    "timestamp": "2026-10-01T08:00:00Z",
                },
            )
            assert response.status_code == 201

        # When the average is requested for the previous 30 days.
        response = client.get(
            "/readings",
            params={
                "sensor_ids": sensor_id,
                "metrics": "temperature",
                "statistic": "avg",
                "days": 30,
            },
        )

    # Then the aggregate response contains the expected average.
    assert response.status_code == 200
    assert response.json() == [
        {
            "sensor_id": sensor_id,
            "metric": "temperature",
            "statistic": "avg",
            "value": 20.0,
        }
    ]


def test_readings_rejects_invalid_days_values():
    # Given a test client for the application.
    with TestClient(app) as client:
        # When lookback values outside the allowed range are requested.
        zero_days_response = client.get("/readings", params={"days": 0})
        thirty_one_days_response = client.get("/readings", params={"days": 31})

    # Then request validation rejects both invalid query values.
    assert zero_days_response.status_code == 422
    assert thirty_one_days_response.status_code == 422


def test_readings_supports_min_max_and_sum_statistics():
    sensor_id = f"integration-query-statistics-{uuid4().hex}"
    limiter.buckets.clear()

    # Given known readings have been persisted for one sensor.
    with TestClient(app) as client:
        for value in [10.0, 20.0, 30.0]:
            create_response = client.post(
                "/readings",
                json={
                    "sensor_id": sensor_id,
                    "metric": "temperature",
                    "value": value,
                    "timestamp": "2026-10-01T08:00:00Z",
                },
            )
            assert create_response.status_code == 201

        # When the min, max, and sum statistics are requested.
        responses = {
            statistic: client.get(
                "/readings",
                params={
                    "sensor_ids": sensor_id,
                    "metrics": "temperature",
                    "statistic": statistic,
                    "days": 30,
                },
            )
            for statistic in ["min", "max", "sum"]
        }

    # Then each aggregate returns the expected value.
    expected_values = {"min": 10.0, "max": 30.0, "sum": 60.0}
    for statistic, response in responses.items():
        assert response.status_code == 200
        assert response.json()[0]["statistic"] == statistic
        assert response.json()[0]["value"] == expected_values[statistic]
