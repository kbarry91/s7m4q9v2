from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint_returns_ok_with_200():
    # Given a test client for the application.
    with TestClient(app) as client:
        # When the health endpoint is requested.
        response = client.get("/health")

    # Then the API reports a healthy status.
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
