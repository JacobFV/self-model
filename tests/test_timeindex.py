"""
Tests for the timeindex module.
"""

import tempfile
from datetime import datetime, UTC, timedelta
from pathlib import Path

import pytest
from pydantic import BaseModel

from timeindex import (
    TimeIndex,
    Timestamped,
    TimeIndexEmpty,
    TimeIndexOutOfBounds,
    TimeIndexOrderError,
)


class SampleState(BaseModel):
    value: float
    label: str = "default"


class AffectCore(BaseModel):
    valence: float
    arousal: float


@pytest.fixture
def temp_jsonl(tmp_path: Path) -> Path:
    """Return a path to a temporary JSONL file."""
    return tmp_path / "test.jsonl"


class TestTimeIndexBasics:
    def test_create_empty_index(self, temp_jsonl: Path):
        index = TimeIndex(temp_jsonl, SampleState)
        assert len(index) == 0
        assert not index
        assert index.latest() is None
        assert index.earliest() is None

    def test_append_and_retrieve_latest(self, temp_jsonl: Path):
        index = TimeIndex(temp_jsonl, SampleState)
        index.append(SampleState(value=1.0, label="first"))
        index.append(SampleState(value=2.0, label="second"))

        assert len(index) == 2
        assert index

        latest = index.latest()
        assert latest is not None
        assert latest.v.value == 2.0
        assert latest.v.label == "second"

        earliest = index.earliest()
        assert earliest is not None
        assert earliest.v.value == 1.0

    def test_append_with_explicit_timestamp(self, temp_jsonl: Path):
        index = TimeIndex(temp_jsonl, SampleState)

        t1 = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)
        t2 = datetime(2025, 1, 1, 13, 0, 0, tzinfo=UTC)

        index.append(SampleState(value=1.0), t=t1)
        index.append(SampleState(value=2.0), t=t2)

        entry = index.get_entry(t2)
        assert entry.t == t2.timestamp()
        assert entry.v.value == 2.0

    def test_append_enforces_ordering(self, temp_jsonl: Path):
        index = TimeIndex(temp_jsonl, SampleState)

        t1 = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)
        t2 = datetime(2025, 1, 1, 11, 0, 0, tzinfo=UTC)  # Before t1!

        index.append(SampleState(value=1.0), t=t1)

        with pytest.raises(TimeIndexOrderError):
            index.append(SampleState(value=2.0), t=t2)

    def test_persistence_across_instances(self, temp_jsonl: Path):
        # Write with first instance
        index1 = TimeIndex(temp_jsonl, SampleState)
        index1.append(SampleState(value=1.0))
        index1.append(SampleState(value=2.0))

        # Read with second instance
        index2 = TimeIndex(temp_jsonl, SampleState)
        assert len(index2) == 2
        assert index2.latest().v.value == 2.0


class TestTimeIndexLookup:
    def test_getitem_empty_raises(self, temp_jsonl: Path):
        index = TimeIndex(temp_jsonl, SampleState)
        with pytest.raises(TimeIndexEmpty):
            _ = index[datetime.now(UTC)]

    def test_getitem_nearest_prev(self, temp_jsonl: Path):
        index = TimeIndex(temp_jsonl, SampleState, policy="nearest_prev")

        t1 = 1000.0
        t2 = 2000.0
        t3 = 3000.0

        index.append(SampleState(value=1.0), t=t1)
        index.append(SampleState(value=2.0), t=t2)
        index.append(SampleState(value=3.0), t=t3)

        # Exact match
        assert index[t2].value == 2.0

        # Between t2 and t3 -> returns t2
        assert index[2500.0].value == 2.0

        # After t3 -> returns t3
        assert index[4000.0].value == 3.0

        # Before t1 -> raises
        with pytest.raises(TimeIndexOutOfBounds):
            _ = index[500.0]

    def test_getitem_nearest_next(self, temp_jsonl: Path):
        index = TimeIndex(temp_jsonl, SampleState, policy="nearest_next")

        t1 = 1000.0
        t2 = 2000.0
        t3 = 3000.0

        index.append(SampleState(value=1.0), t=t1)
        index.append(SampleState(value=2.0), t=t2)
        index.append(SampleState(value=3.0), t=t3)

        # Exact match
        assert index[t2].value == 2.0

        # Between t1 and t2 -> returns t2
        assert index[1500.0].value == 2.0

        # Before t1 -> returns t1
        assert index[500.0].value == 1.0

        # After t3 -> raises
        with pytest.raises(TimeIndexOutOfBounds):
            _ = index[4000.0]

    def test_getitem_nearest(self, temp_jsonl: Path):
        index = TimeIndex(temp_jsonl, SampleState, policy="nearest")

        t1 = 1000.0
        t2 = 2000.0

        index.append(SampleState(value=1.0), t=t1)
        index.append(SampleState(value=2.0), t=t2)

        # Closer to t1
        assert index[1100.0].value == 1.0

        # Closer to t2
        assert index[1900.0].value == 2.0

        # Exactly in between -> returns earlier (ties go to prev)
        assert index[1500.0].value == 1.0

        # Before all -> returns first
        assert index[0.0].value == 1.0

        # After all -> returns last
        assert index[9999.0].value == 2.0

    def test_get_with_default(self, temp_jsonl: Path):
        index = TimeIndex(temp_jsonl, SampleState, policy="nearest_prev")

        default = SampleState(value=-1.0, label="default")

        # Empty index
        result = index.get(1000.0, default=default)
        assert result.value == -1.0

        # Add entry
        index.append(SampleState(value=1.0), t=1000.0)

        # Query before -> returns default
        result = index.get(500.0, default=default)
        assert result.value == -1.0

        # Query after -> returns actual
        result = index.get(1500.0, default=default)
        assert result.value == 1.0

    def test_get_with_policy_override(self, temp_jsonl: Path):
        index = TimeIndex(temp_jsonl, SampleState, policy="nearest_prev")

        index.append(SampleState(value=1.0), t=1000.0)
        index.append(SampleState(value=2.0), t=2000.0)

        # Default policy (nearest_prev)
        assert index[1500.0].value == 1.0

        # Override to nearest_next
        assert index.get(1500.0, policy="nearest_next").value == 2.0


class TestTimeIndexRange:
    def test_range_query(self, temp_jsonl: Path):
        index = TimeIndex(temp_jsonl, SampleState)

        for i in range(10):
            index.append(SampleState(value=float(i)), t=float(i * 100))

        # Range [200, 500] should include entries at 200, 300, 400, 500
        entries = list(index.range(200.0, 500.0))
        assert len(entries) == 4
        assert [e.v.value for e in entries] == [2.0, 3.0, 4.0, 5.0]

    def test_slice_syntax(self, temp_jsonl: Path):
        index = TimeIndex(temp_jsonl, SampleState)

        for i in range(5):
            index.append(SampleState(value=float(i)), t=float(i * 100))

        entries = list(index[100.0:300.0])
        assert len(entries) == 3
        assert [e.v.value for e in entries] == [1.0, 2.0, 3.0]

    def test_all_iterator(self, temp_jsonl: Path):
        index = TimeIndex(temp_jsonl, SampleState)

        for i in range(3):
            index.append(SampleState(value=float(i)), t=float(i * 100))

        entries = list(index.all())
        assert len(entries) == 3
        assert [e.v.value for e in entries] == [0.0, 1.0, 2.0]


class TestTimestamped:
    def test_datetime_conversion(self):
        ts = 1734307200.0  # Some unix timestamp
        entry = Timestamped(t=ts, v=SampleState(value=1.0))

        dt = entry.datetime
        assert dt.tzinfo == UTC
        assert dt.timestamp() == ts

    def test_ordering(self):
        e1 = Timestamped(t=100.0, v=SampleState(value=1.0))
        e2 = Timestamped(t=200.0, v=SampleState(value=2.0))

        assert e1 < e2
        assert e1 <= e2
        assert e2 > e1
        assert e2 >= e1
        assert not (e1 > e2)


class TestComplexModels:
    def test_nested_model(self, temp_jsonl: Path):
        class Inner(BaseModel):
            x: int
            y: int

        class Outer(BaseModel):
            name: str
            inner: Inner

        index = TimeIndex(temp_jsonl, Outer)
        index.append(Outer(name="test", inner=Inner(x=1, y=2)))

        loaded = index.latest()
        assert loaded.v.name == "test"
        assert loaded.v.inner.x == 1
        assert loaded.v.inner.y == 2

    def test_optional_fields(self, temp_jsonl: Path):
        class WithOptional(BaseModel):
            required: str
            optional: str | None = None

        index = TimeIndex(temp_jsonl, WithOptional)
        index.append(WithOptional(required="a"))
        index.append(WithOptional(required="b", optional="opt"))

        entries = list(index.all())
        assert entries[0].v.optional is None
        assert entries[1].v.optional == "opt"


class TestRepr:
    def test_repr(self, temp_jsonl: Path):
        index = TimeIndex(temp_jsonl, SampleState, policy="nearest")
        index.append(SampleState(value=1.0))

        r = repr(index)
        assert "TimeIndex" in r
        assert "SampleState" in r
        assert "nearest" in r
        assert "entries=1" in r
