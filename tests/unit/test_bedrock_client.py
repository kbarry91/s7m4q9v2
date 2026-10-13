import asyncio
import time

from app.ai.bedrock_client import BedrockConverseClient
from app.ai.contracts import Message, ToolCall, ToolDefinition


class FakeBedrockRuntimeClient:
    def __init__(self, response):
        self.response = response
        self.request = None

    def converse(self, **request):
        self.request = request
        return self.response


class SlowBedrockRuntimeClient:
    def converse(self, **request):
        time.sleep(0.05)
        return {}


def test_bedrock_client_translates_tool_call():
    runtime_client = FakeBedrockRuntimeClient(
        {
            "output": {
                "message": {
                    "content": [
                        {
                            "toolUse": {
                                "toolUseId": "call-1",
                                "name": "query_readings",
                                "input": {"days": 8},
                            }
                        }
                    ]
                }
            },
            "usage": {"inputTokens": 12, "outputTokens": 7},
        }
    )
    client = BedrockConverseClient(runtime_client, "model-id")

    response = asyncio.run(
        client.complete(
            messages=(Message(role="user", content="Average over 8 days"),),
            tools=(
                ToolDefinition(
                    name="query_readings",
                    description="Query readings",
                    input_schema={"type": "object"},
                ),
            ),
        )
    )

    assert response.tool_calls == (
        ToolCall(
            id="call-1",
            name="query_readings",
            arguments={"days": 8},
        ),
    )
    assert runtime_client.request["modelId"] == "model-id"
    assert runtime_client.request["toolConfig"]["tools"][0]["toolSpec"]["name"] == (
        "query_readings"
    )


def test_bedrock_client_times_out_slow_provider_call():
    client = BedrockConverseClient(
        SlowBedrockRuntimeClient(),
        "model-id",
        timeout_seconds=0.001,
    )

    try:
        asyncio.run(client.complete(messages=(), tools=()))
    except TimeoutError:
        pass
    else:
        raise AssertionError("Expected the Bedrock call to time out")
