from fastapi.testclient import TestClient

from app.ai.contracts import ModelResponse, ToolCall
from app.ai.dependencies import get_model_client
from app.ai.fake_client import FakeModelClient
from app.main import app


def test_assistant_endpoint_uses_fake_model_and_returns_answer():
    fake_client = FakeModelClient(
        [
            ModelResponse(
                tool_calls=(
                    ToolCall(
                        id="call-1",
                        name="query_readings",
                        arguments={"sensor_ids": ["sensor-1"], "days": 8},
                    ),
                )
            ),
            ModelResponse(text="The average temperature was 20.8 degrees Celsius."),
        ]
    )
    app.dependency_overrides[get_model_client] = lambda: fake_client

    try:
        with TestClient(app) as client:
            response = client.post(
                "/assistant",
                json={"message": "Average sensor-1 temperature over 8 days"},
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"answer": "The average temperature was 20.8 degrees Celsius."}


def test_assistant_endpoint_reports_unconfigured_model(monkeypatch):
    monkeypatch.delenv("BEDROCK_MODEL_ID", raising=False)

    with TestClient(app) as client:
        response = client.post(
            "/assistant",
            json={"message": "What is the latest temperature?"},
        )

    assert response.status_code == 503
    assert response.json() == {"detail": "The assistant model is not configured"}


def test_assistant_endpoint_hides_invalid_model_output():
    fake_client = FakeModelClient(
        [
            ModelResponse(
                tool_calls=(
                    ToolCall(
                        id="call-1",
                        name="query_readings",
                        arguments={"days": 31},
                    ),
                )
            )
        ]
    )
    app.dependency_overrides[get_model_client] = lambda: fake_client

    try:
        with TestClient(app) as client:
            response = client.post(
                "/assistant",
                json={"message": "Query the readings"},
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 502
    assert response.json() == {"detail": "The assistant model returned an unusable response"}
