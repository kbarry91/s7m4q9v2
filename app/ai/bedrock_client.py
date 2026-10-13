"""Amazon Bedrock Converse client used by the assistant."""

import asyncio
import json
from typing import Any

from app.ai.contracts import Message, ModelResponse, ToolCall, ToolDefinition


class BedrockConverseClient:
    # Store the AWS client and the model settings used for each Converse request.
    def __init__(
        self,
        runtime_client: Any,
        model_id: str,
        max_tokens: int = 512,
        temperature: float = 0.0,
        timeout_seconds: float = 30.0,
    ) -> None:
        self.runtime_client = runtime_client
        self.model_id = model_id
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout_seconds = timeout_seconds

    async def complete(
        self,
        messages: list[Message] | tuple[Message, ...],
        tools: list[ToolDefinition] | tuple[ToolDefinition, ...],
    ) -> ModelResponse:
        # Translate our messages and tool definition into Bedrock's request format.
        system_messages = [
            {"text": message.content} for message in messages if message.role == "system"
        ]
        converse_messages = [
            self._message_to_bedrock(message) for message in messages if message.role != "system"
        ]

        request: dict[str, Any] = {
            "modelId": self.model_id,
            "messages": converse_messages,
            "inferenceConfig": {
                "maxTokens": self.max_tokens,
                "temperature": self.temperature,
            },
        }
        if system_messages:
            request["system"] = system_messages
        if tools:
            request["toolConfig"] = {"tools": [self._tool_to_bedrock(tool) for tool in tools]}

        # Invoke the llm
        response = await asyncio.wait_for(
            asyncio.to_thread(self.runtime_client.converse, **request),
            timeout=self.timeout_seconds,
        )
        return self._response_from_bedrock(response)

    @staticmethod
    def _tool_to_bedrock(tool: ToolDefinition) -> dict[str, Any]:
        # Convert the internal tool schema into Bedrock's toolSpec structure.
        return {
            "toolSpec": {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": {"json": tool.input_schema},
            }
        }

    @staticmethod
    def _message_to_bedrock(message: Message) -> dict[str, Any]:
        # Convert normal, assistant, and tool-result messages into Converse content blocks.
        if message.role == "tool":
            try:
                result = json.loads(message.content)
            except json.JSONDecodeError:
                result = {"text": message.content}
            return {
                "role": "user",
                "content": [
                    {
                        "toolResult": {
                            "toolUseId": message.tool_call_id,
                            "content": [{"json": result}],
                        }
                    }
                ],
            }

        content: list[dict[str, Any]] = []
        if message.content:
            content.append({"text": message.content})
        content.extend(
            {
                "toolUse": {
                    "toolUseId": tool_call.id,
                    "name": tool_call.name,
                    "input": tool_call.arguments,
                }
            }
            for tool_call in message.tool_calls
        )
        return {"role": message.role, "content": content}

    @staticmethod
    def _response_from_bedrock(response: dict[str, Any]) -> ModelResponse:
        # Extract either the model's final text or its requested tool call.
        content = response.get("output", {}).get("message", {}).get("content", [])
        text_parts = [item["text"] for item in content if "text" in item]
        tool_calls = tuple(
            ToolCall(
                id=item["toolUse"]["toolUseId"],
                name=item["toolUse"]["name"],
                arguments=item["toolUse"].get("input", {}),
            )
            for item in content
            if "toolUse" in item
        )
        return ModelResponse(text="".join(text_parts) or None, tool_calls=tool_calls)
