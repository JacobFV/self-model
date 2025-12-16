"""
timeindex: Time-indexed, append-only storage for Pydantic models.

A generic data structure for storing timestamped values with efficient
retrieval via binary search. Uses JSONL for persistence.

Example:
    >>> from pydantic import BaseModel
    >>> from timeindex import TimeIndex

    >>> class SensorReading(BaseModel):
    ...     temperature: float
    ...     humidity: float

    >>> readings = TimeIndex("./data/sensor.jsonl", SensorReading)
    >>> readings.append(SensorReading(temperature=22.5, humidity=0.45))

    >>> latest = readings.latest()
    >>> print(latest.v.temperature)
    22.5

    >>> # Query at specific time
    >>> from datetime import datetime, UTC
    >>> reading = readings[datetime.now(UTC)]
"""

from .types import (
    Timestamped,
    LookupPolicy,
    TimeIndexError,
    TimeIndexEmpty,
    TimeIndexOutOfBounds,
    TimeIndexOrderError,
)
from .index import TimeIndex

__all__ = [
    # Main class
    "TimeIndex",
    # Types
    "Timestamped",
    "LookupPolicy",
    # Exceptions
    "TimeIndexError",
    "TimeIndexEmpty",
    "TimeIndexOutOfBounds",
    "TimeIndexOrderError",
]
