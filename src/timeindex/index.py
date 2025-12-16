"""
TimeIndex: A time-indexed, append-only store for Pydantic models.
"""

from bisect import bisect_left, bisect_right
from datetime import datetime, UTC
from pathlib import Path
from typing import Generic, TypeVar, Iterator, overload
import json

from pydantic import BaseModel

from .types import (
    Timestamped,
    LookupPolicy,
    TimeIndexEmpty,
    TimeIndexOutOfBounds,
    TimeIndexOrderError,
)

T = TypeVar("T", bound=BaseModel)


class TimeIndex(Generic[T]):
    """
    A generic, time-indexed data structure for timestamped Pydantic models.

    Provides append-only storage via JSONL files with efficient time-based
    retrieval using binary search.

    Example:
        >>> from pydantic import BaseModel
        >>> class State(BaseModel):
        ...     value: float
        >>> index = TimeIndex("./data/state.jsonl", State)
        >>> index.append(State(value=1.0))
        >>> index.latest().v.value
        1.0
    """

    def __init__(
        self,
        path: Path | str,
        model: type[T],
        policy: LookupPolicy = "nearest_prev",
    ):
        """
        Create or open a TimeIndex.

        Args:
            path: Path to the JSONL file (created if doesn't exist)
            model: Pydantic model class for values
            policy: Default lookup policy for time queries
        """
        self._path = Path(path)
        self._model = model
        self._policy = policy
        self._entries: list[Timestamped[T]] = []

        # Load existing entries if file exists
        if self._path.exists():
            self._load()

    def _load(self) -> None:
        """Load all entries from the JSONL file."""
        with open(self._path, "r") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    entry = Timestamped(
                        t=float(data["t"]),
                        v=self._model.model_validate(data["v"]),
                    )
                    self._entries.append(entry)
                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    raise ValueError(
                        f"Invalid entry at {self._path}:{line_num}: {e}"
                    ) from e

    def _write_entry(self, entry: Timestamped[T]) -> None:
        """Append a single entry to the JSONL file."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "a") as f:
            data = {"t": entry.t, "v": entry.v.model_dump()}
            f.write(json.dumps(data) + "\n")

    def _to_timestamp(self, t: datetime | float) -> float:
        """Convert datetime or float to unix timestamp."""
        if isinstance(t, datetime):
            return t.timestamp()
        return float(t)

    def append(self, value: T, t: datetime | float | None = None) -> Timestamped[T]:
        """
        Append a value with timestamp.

        Args:
            value: The Pydantic model instance to store
            t: Timestamp (datetime or unix float). Defaults to now.

        Returns:
            The created Timestamped entry

        Raises:
            TimeIndexOrderError: If timestamp is older than the latest entry
        """
        if t is None:
            ts = datetime.now(UTC).timestamp()
        else:
            ts = self._to_timestamp(t)

        # Enforce append-only ordering
        if self._entries and ts < self._entries[-1].t:
            raise TimeIndexOrderError(
                f"Cannot append timestamp {ts} before latest entry {self._entries[-1].t}"
            )

        entry = Timestamped(t=ts, v=value)
        self._entries.append(entry)
        self._write_entry(entry)
        return entry

    def _find_index(self, ts: float, policy: LookupPolicy) -> int:
        """
        Find the index of the entry matching the timestamp and policy.

        Returns the index into self._entries, or raises if not found.
        """
        if not self._entries:
            raise TimeIndexEmpty("Cannot query empty index")

        n = len(self._entries)

        if policy == "nearest_prev":
            # Find rightmost entry with t <= ts
            idx = bisect_right(self._entries, ts, key=lambda e: e.t) - 1
            if idx < 0:
                raise TimeIndexOutOfBounds(
                    f"No entries at or before timestamp {ts}"
                )
            return idx

        elif policy == "nearest_next":
            # Find leftmost entry with t >= ts
            idx = bisect_left(self._entries, ts, key=lambda e: e.t)
            if idx >= n:
                raise TimeIndexOutOfBounds(
                    f"No entries at or after timestamp {ts}"
                )
            return idx

        else:  # nearest
            # Find the entry with closest timestamp
            idx = bisect_left(self._entries, ts, key=lambda e: e.t)

            if idx == 0:
                return 0
            if idx >= n:
                return n - 1

            # Compare distances to idx-1 and idx
            before = self._entries[idx - 1]
            after = self._entries[idx]
            if ts - before.t <= after.t - ts:
                return idx - 1
            return idx

    @overload
    def __getitem__(self, t: datetime | float) -> T: ...

    @overload
    def __getitem__(self, t: slice) -> Iterator[Timestamped[T]]: ...

    def __getitem__(self, t: datetime | float | slice) -> T | Iterator[Timestamped[T]]:
        """
        Get value at time or iterate over time range.

        index[time] -> value at time (using default policy)
        index[start:end] -> iterator over entries in range
        """
        if isinstance(t, slice):
            start = self._to_timestamp(t.start) if t.start else None
            stop = self._to_timestamp(t.stop) if t.stop else None
            return self._range_iter(start, stop)

        ts = self._to_timestamp(t)
        idx = self._find_index(ts, self._policy)
        return self._entries[idx].v

    def get(
        self,
        t: datetime | float,
        policy: LookupPolicy | None = None,
        default: T | None = None,
    ) -> T | None:
        """
        Get value at time with explicit policy and optional default.

        Args:
            t: Query timestamp
            policy: Lookup policy (defaults to index's default)
            default: Value to return if not found (instead of raising)

        Returns:
            The value, or default if not found and default provided
        """
        try:
            ts = self._to_timestamp(t)
            idx = self._find_index(ts, policy or self._policy)
            return self._entries[idx].v
        except (TimeIndexEmpty, TimeIndexOutOfBounds):
            if default is not None:
                return default
            raise

    def get_entry(
        self,
        t: datetime | float,
        policy: LookupPolicy | None = None,
    ) -> Timestamped[T]:
        """
        Get timestamped entry at time.

        Like __getitem__ but returns the Timestamped wrapper including
        the actual timestamp of the found entry.
        """
        ts = self._to_timestamp(t)
        idx = self._find_index(ts, policy or self._policy)
        return self._entries[idx]

    def latest(self) -> Timestamped[T] | None:
        """Get the most recent entry, or None if empty."""
        if not self._entries:
            return None
        return self._entries[-1]

    def earliest(self) -> Timestamped[T] | None:
        """Get the oldest entry, or None if empty."""
        if not self._entries:
            return None
        return self._entries[0]

    def _range_iter(
        self,
        start: float | None,
        end: float | None,
    ) -> Iterator[Timestamped[T]]:
        """Iterate over entries in time range [start, end]."""
        for entry in self._entries:
            if start is not None and entry.t < start:
                continue
            if end is not None and entry.t > end:
                break
            yield entry

    def range(
        self,
        start: datetime | float,
        end: datetime | float,
    ) -> Iterator[Timestamped[T]]:
        """
        Iterate over entries in time range [start, end] inclusive.

        Args:
            start: Start timestamp (inclusive)
            end: End timestamp (inclusive)

        Yields:
            Timestamped entries in chronological order
        """
        start_ts = self._to_timestamp(start)
        end_ts = self._to_timestamp(end)
        return self._range_iter(start_ts, end_ts)

    def all(self) -> Iterator[Timestamped[T]]:
        """Iterate over all entries in chronological order."""
        return iter(self._entries)

    def __len__(self) -> int:
        """Return the number of entries."""
        return len(self._entries)

    def __bool__(self) -> bool:
        """Return True if index has any entries."""
        return bool(self._entries)

    def __repr__(self) -> str:
        return (
            f"TimeIndex({self._path!r}, {self._model.__name__}, "
            f"policy={self._policy!r}, entries={len(self._entries)})"
        )
