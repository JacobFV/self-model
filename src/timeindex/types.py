"""
Core types for the timeindex module.
"""

from dataclasses import dataclass
from datetime import datetime, UTC
from typing import Generic, TypeVar, Literal

T = TypeVar("T")

LookupPolicy = Literal["nearest", "nearest_prev", "nearest_next"]


@dataclass(frozen=True, slots=True)
class Timestamped(Generic[T]):
    """
    A value paired with its timestamp.

    Attributes:
        t: Unix timestamp (seconds since epoch, float for sub-second precision)
        v: The value
    """
    t: float
    v: T

    @property
    def datetime(self) -> datetime:
        """Convert timestamp to datetime (UTC)."""
        return datetime.fromtimestamp(self.t, tz=UTC)

    def __lt__(self, other: "Timestamped") -> bool:
        return self.t < other.t

    def __le__(self, other: "Timestamped") -> bool:
        return self.t <= other.t

    def __gt__(self, other: "Timestamped") -> bool:
        return self.t > other.t

    def __ge__(self, other: "Timestamped") -> bool:
        return self.t >= other.t


class TimeIndexError(Exception):
    """Base exception for timeindex errors."""
    pass


class TimeIndexEmpty(TimeIndexError):
    """Raised when querying an empty index."""
    pass


class TimeIndexOutOfBounds(TimeIndexError):
    """
    Raised when a lookup policy cannot be satisfied.

    - nearest_prev: query time is before all entries
    - nearest_next: query time is after all entries
    """
    pass


class TimeIndexOrderError(TimeIndexError):
    """Raised when attempting to append with a timestamp older than the latest entry."""
    pass
