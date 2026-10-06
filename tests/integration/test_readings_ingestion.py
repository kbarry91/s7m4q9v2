from fastapi.testclient import TestClient

from app.main import app
from app.rate_limiter import limiter


def test_create_reading_persists_and_can_be_queried():
    limiter.buckets.clear()

    # Given a test client and an empty reading for the target sensor.
    with TestClient(app) as client:
        # When the reading is created and queried in latest mode.
        create_response = client.post(
            "/readings",
            json={
                "sensor_id": "integration-persistence-test",
                "metric": "temperature",
                "value": 23.5,
            },
        )

        query_response = client.get(
            "/readings",
            params={
                "sensor_ids": "integration-persistence-test",
                "metrics": "temperature",
            },
        )

    # Then the reading is created with a database ID.
    assert create_response.status_code == 201
    created_reading = create_response.json()
    assert created_reading["sensor_id"] == "integration-persistence-test"
    assert created_reading["metric"] == "temperature"
    assert created_reading["value"] == 23.5
    assert created_reading["id"] > 0

    # And the stored reading is returned by the query.
    assert query_response.status_code == 200
    assert query_response.json() == [
        {
            "sensor_id": "integration-persistence-test",
            "metric": "temperature",
            "statistic": "latest",
            "value": 23.5,
        }
    ]


def test_create_reading_rejects_unknown_metric_with_422():
    # Given a test client and an unsupported metric.
    with TestClient(app) as client:
        # When the invalid reading is submitted.
        response = client.post(
            "/readings",
            json={
                "sensor_id": "integration-test",
                "metric": "pressure",
                "value": 20.0,
            },
        )

    # Then request validation rejects the unsupported metric before persistence.
    assert response.status_code == 422
