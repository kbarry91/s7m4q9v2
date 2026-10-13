"""Bounded conversational tool loop for the Bedrock assistant."""

import json
import re
from dataclasses import dataclass

from app.ai.contracts import Message, ModelClient
from app.ai.tools import QUERY_READINGS_TOOL, QueryReadingsArguments, query_readings_tool_result
from app.services.query_service import QueryReadingService

ASSISTANT_SYSTEM_PROMPT = """You answer weather-reading questions using the query_readings tool.
Use the tool result as authoritative. Do not perform a second aggregation over
already-aggregated values. Report each sensor separately when multiple sensors
are returned. State only the requested metric, statistic, scope, time period,
and value. Do not add offers, suggestions, greetings, or extra explanation.
Never include private reasoning, thinking tags, or scratch calculations.
If required information is missing, ask only for the specific missing
parameter(s) in one concise sentence. Do not guess.
"""


def _clean_model_text(text: str) -> str:
    # Remove reasoning markup before model text is returned to the API client.
    text = re.sub(
        r"<(?:thinking|think)>.*?</(?:thinking|think)>",
        "",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return text.strip()


@dataclass(frozen=True)
class AssistantResponse:
    text: str


class AssistantService:
    # Keep the model client and existing query service together for one assistant request.
    def __init__(
        self,
        model_client: ModelClient,
        query_service: QueryReadingService,
        max_tool_turns: int = 2,
    ) -> None:
        self.model_client = model_client
        self.query_service = query_service
        self.max_tool_turns = max_tool_turns

    async def respond(self, user_message: str) -> AssistantResponse:
        # Let Bedrock choose the query tool, execute it locally, then request the final answer.
        messages = [
            Message(role="system", content=ASSISTANT_SYSTEM_PROMPT),
            Message(role="user", content=user_message),
        ]

        # Repeat the model/tool exchange for the allowed number of turns.
        for _ in range(self.max_tool_turns):

            # Ask the model to interpret the request and choose a tool.
            response = await self.model_client.complete(
                messages=messages,
                tools=(QUERY_READINGS_TOOL,),
            )
            if not response.tool_calls:
                if response.text is None:
                    raise RuntimeError("Model returned neither text nor a tool call")
                return AssistantResponse(text=_clean_model_text(response.text))

            if len(response.tool_calls) != 1:
                raise RuntimeError("Only one tool call is supported per assistant turn")

            # Validate the tool call
            tool_call = response.tool_calls[0]
            if tool_call.name != QUERY_READINGS_TOOL.name:
                raise RuntimeError(f"Unsupported assistant tool: {tool_call.name}")

            # Extract and validate the tool call arguments
            arguments = QueryReadingsArguments.model_validate(tool_call.arguments)
            rows = await self.query_service.aggregate(**arguments.model_dump())
            messages.extend(
                [
                    Message(
                        role="assistant",
                        content="",
                        tool_calls=(tool_call,),
                    ),
                    Message(
                        role="tool",
                        content=json.dumps(query_readings_tool_result(rows)),
                        tool_call_id=tool_call.id,
                        tool_name=tool_call.name,
                    ),
                ]
            )

        raise RuntimeError("Assistant exceeded the maximum number of tool turns")
