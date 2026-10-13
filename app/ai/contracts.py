"""Contracts shared by the assistant and its Bedrock client.

Frozen dataclasses provide lightweight immutability for the proof of concept.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Literal, Protocol

Role = Literal["system", "user", "assistant", "tool"]

# Describes a tool available to the LLM.
@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    input_schema: dict[str, Any]


# Represents the tool the LLM chose and the arguments it supplied.
@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


# Represents one message in the conversation.
@dataclass(frozen=True)
class Message:
    role: Role
    content: str
    tool_calls: tuple[ToolCall, ...] = ()
    tool_call_id: str | None = None
    tool_name: str | None = None


# Represents the parsed result returned by the model.
@dataclass(frozen=True)
class ModelResponse:
    text: str | None = None
    tool_calls: tuple[ToolCall, ...] = ()


# Describes the methods that a model client must implement.
class ModelClient(Protocol):
    async def complete(
        self,
        messages: Sequence[Message],
        tools: Sequence[ToolDefinition],
    ) -> ModelResponse:
        """Return the model's next response for the current conversation."""
