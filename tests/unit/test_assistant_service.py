import asyncio

from app.ai.assistant_service import AssistantService
from app.ai.contracts import ModelResponse, ToolCall
from app.ai.fake_client import FakeModelClient


class FakeQueryService:
    def __init__(self) -> None:
        self.calls = []

    async def aggregate(self, **arguments):
        self.calls.append(arguments)
        return [
            {
                "sensor_id": "sensor-1",
                "metric": "temperature",
                "statistic": "avg",
                "value": 20.8,
            }
        ]


def test_assistant_executes_allowlisted_query_and_uses_grounded_response() -> None:
    model_client = FakeModelClient(
        [
            ModelResponse(
                tool_calls=(
                    ToolCall(
                        id="call-1",
                        name="query_readings",
                        arguments={
                            "sensor_ids": ["sensor-1"],
                            "metrics": ["temperature"],
                            "days": 8,
                        },
                    ),
                )
            ),
            ModelResponse(text="The average temperature was 20.8 degrees Celsius."),
        ]
    )
    query_service = FakeQueryService()
    assistant = AssistantService(model_client, query_service)

    response = asyncio.run(
        assistant.respond("What was the average temperature for sensor-1 over 8 days?")
    )

    assert response.text == "The average temperature was 20.8 degrees Celsius."
    assert query_service.calls == [
        {
            "sensor_ids": ["sensor-1"],
            "metrics": ["temperature"],
            "statistic": None,
            "days": 8,
        }
    ]
    assert len(model_client.requests) == 2
    assert model_client.requests[0][0][0].role == "system"
    assert "Never include private" in model_client.requests[0][0][0].content
    assert "reasoning" in model_client.requests[0][0][0].content
    assert "Do not add offers" in model_client.requests[0][0][0].content
    assert "If required information is missing" in model_client.requests[0][0][0].content
    assert '"value": 20.8' in model_client.requests[1][0][-1].content


def test_assistant_removes_private_thinking_from_final_response() -> None:
    model_client = FakeModelClient(
        [
            ModelResponse(
                text=(
                    "<thinking>Need the sensor ID.</thinking>\n"
                    "Please provide the sensor ID."
                )
            )
        ]
    )

    response = asyncio.run(
        AssistantService(model_client, FakeQueryService()).respond("Average temperature")
    )

    assert response.text == "Please provide the sensor ID."
