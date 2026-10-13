import asyncio

from app.ai.contracts import Message, ModelResponse, ToolCall, ToolDefinition
from app.ai.fake_client import FakeModelClient


def test_fake_model_client_returns_scripted_tool_call() -> None:
    tool = ToolDefinition(
        name="query_readings",
        description="Query stored weather readings",
        input_schema={"type": "object"},
    )
    expected = ModelResponse(
        tool_calls=(
            ToolCall(
                id="call-1",
                name="query_readings",
                arguments={"sensor_ids": ["sensor-1"], "days": 8},
            ),
        )
    )
    client = FakeModelClient([expected])

    response = asyncio.run(
        client.complete(
            messages=(Message(role="user", content="Average sensor-1 over 8 days"),),
            tools=(tool,),
        )
    )

    assert response == expected
    assert client.requests[0][0][0].content == "Average sensor-1 over 8 days"
    assert client.requests[0][1][0].name == "query_readings"
