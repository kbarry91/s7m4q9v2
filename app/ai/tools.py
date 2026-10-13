"""Allowlisted tools exposed to the conversational assistant."""

from typing import Any

from pydantic import BaseModel, Field

from app.ai.contracts import ToolDefinition
from app.schemas import AggregationStatistic, Metric


# Defines the arguments and tool for querying weather readings.
class QueryReadingsArguments(BaseModel):
    sensor_ids: list[str] | None = None
    metrics: list[Metric] | None = None
    statistic: AggregationStatistic | None = None
    days: int | None = Field(default=None, ge=1, le=30)


QUERY_READINGS_TOOL = ToolDefinition(
    name="query_readings",
    description="Query stored weather readings without changing data.",
    input_schema=QueryReadingsArguments.model_json_schema(),
)


def query_readings_tool_result(rows: list[dict[str, Any]]) -> dict[str, Any]:
    # Wrap database rows in the JSON shape sent back to Bedrock as a tool result.
    return {"readings": rows}
