"""ORM models."""

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Reading(Base):
    __tablename__ = "readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    metric: Mapped[str] = mapped_column(String, index=True)
    # index not required as it's included in the composite index below
    sensor_id: Mapped[str] = mapped_column(String)
    value: Mapped[float] = mapped_column(Float)
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)

    __table_args__ = (
        # Table level args, the comma defines as a tuple required by sql alchemyeven for a single index
        Index("ix_readings_sensor_metric_timestamp","sensor_id", "metric", "timestamp"),
    )