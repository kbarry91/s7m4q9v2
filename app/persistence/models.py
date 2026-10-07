"""ORM models for persisted sensor readings."""

from datetime import datetime

from sqlalchemy import DateTime, Float, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.db import Base


class Reading(Base):
    __tablename__ = "readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    metric: Mapped[str] = mapped_column(String, index=True)
    sensor_id: Mapped[str] = mapped_column(String(64))
    value: Mapped[float] = mapped_column(Float)
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)

    __table_args__ = (
        Index(
            "ix_readings_sensor_metric_timestamp",
            "sensor_id",
            "metric",
            "timestamp",
        ),
    )
