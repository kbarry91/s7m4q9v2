"""Deterministic model client for offline tests and local learning."""

from collections.abc import Sequence

from app.ai.contracts import Message, ModelResponse, ToolDefinition


class FakeModelClient:
    # Keep scripted responses so assistant behavior can be tested without AWS.
    def __init__(self, responses: Sequence[ModelResponse]) -> None:
        self.responses = list(responses)
        self.requests: list[tuple[tuple[Message, ...], tuple[ToolDefinition, ...]]] = []

    async def complete(
        self,
        messages: Sequence[Message],
        tools: Sequence[ToolDefinition],
    ) -> ModelResponse:
        # Record the request and return the next preconfigured model response.
        self.requests.append((tuple(messages), tuple(tools)))
        if not self.responses:
            raise RuntimeError("FakeModelClient has no scripted response")

        return self.responses.pop(0)
