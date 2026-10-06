"""Pydantic request/response schemas for the API layer."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class Metric(str, Enum):
    temperature = "temperature"
    humidity = "humidity"
    wind_speed = "wind_speed"

class Statistic (str, Enum):
    min = "min"
    max = "max"
    avg = "avg"
    sum = "sum"
    latest = "latest"

class ReadingCreate(BaseModel):
    """Incoming payload for a single sensor reading."""

    sensor_id: str = Field(
        min_length=1, max_length=64, description="Unique identifier of the sensor"
    )
    metric: Metric = Field(description="Which metric this reading is for")
    value: float = Field(
        description="Measured value in the metric's canonical unit "
        "(temperature °C, humidity %, wind_speed m/s)"
    )
    timestamp: datetime | None = Field(
        default=None,
        description="When the measurement was taken (UTC); defaults to now if omitted",
    )


class ReadingOut(BaseModel):
    """A stored reading returned to clients."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Server-assigned identifier of the stored reading")
    sensor_id: str = Field(description="Unique identifier of the sensor")
    metric: Metric = Field(description="Which metric this reading is for")
    value: float = Field(description="Measured value in the metric's canonical unit")
    timestamp: datetime = Field(description="When the measurement was taken (UTC)")


class AggregatedReadingResponse(BaseModel):
    """Response schema for aggregated sensor readings."""

    sensor_id: str = Field(description="Unique identifier of the sensor")
    metric: Metric = Field(description="Which metric this reading is for")
    statistic: Statistic = Field(description="Which statistic to compute")
    value: float = Field(description="Computed value of the requested statistic")
