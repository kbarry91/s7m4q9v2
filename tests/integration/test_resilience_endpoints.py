from fastapi.testclient import TestClient

from app.main import app
from app.rate_limiter import limiter


def test_post_readings_returns_429_after_bucket_is_exhausted():
    # Given a fresh rate-limit bucket for this test client.
    limiter.buckets.clear()

    with TestClient(app) as client:
        # When six ingestion requests are sent in rapid succession.
        responses = [
            client.post(
                "/readings",
                json={
                    "sensor_id": "integration-rate-limit-test",
                    "metric": "temperature",
                    "value": value,
                },
            )
            for value in range(1, 7)
        ]

    # Then five requests succeed and the sixth is rejected.
    assert [response.status_code for response in responses] == [
        201,
        201,
        201,
        201,
        201,
        429,
    ]
    assert responses[-1].headers["retry-after"] == "1"


def test_slow_dependency_is_disabled_by_default(monkeypatch):
    # Given the test dependency is disabled.
    monkeypatch.delenv("TEST_DEPENDENCY_ENABLED", raising=False)

    with TestClient(app) as client:
        # When the test-only endpoint is requested while disabled.
        response = client.get("/test/slow-dependency", params={"delay": 0})

    # Then the endpoint is reported as unavailable.
    assert response.status_code == 404


def test_slow_dependency_times_out(monkeypatch):
    # Given the test dependency is enabled with a short timeout.
    monkeypatch.setenv("TEST_DEPENDENCY_ENABLED", "true")
    monkeypatch.setenv("TEST_DEPENDENCY_TIMEOUT_SECONDS", "0.01")

    with TestClient(app) as client:
        # When the simulated dependency exceeds the configured timeout.
        response = client.get("/test/slow-dependency", params={"delay": 0.1})

    # Then the API returns a gateway timeout.
    assert response.status_code == 504
