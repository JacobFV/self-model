# TimeIndex Specification

## Overview

`TimeIndex[T]` is a generic, time-indexed data structure for storing and retrieving timestamped values of a Pydantic model type `T`. It provides:

- **Append-only storage** via JSONL files (one JSON object per line)
- **Time-indexed access** with configurable lookup policies (nearest, nearest_prev, nearest_next)
- **Efficient retrieval** via binary search over timestamps
- **Type safety** via Pydantic models and generics

## Core Types

### `Timestamped[T]`

A wrapper that pairs a value with its timestamp:

```python
@dataclass
class Timestamped(Generic[T]):
    t: float      # Unix timestamp (seconds since epoch, with fractional ms)
    v: T          # The value (Pydantic model instance)

    @property
    def datetime(self) -> datetime:
        """Convert timestamp to datetime (UTC)"""
```

### `LookupPolicy`

Determines how to resolve queries when exact timestamp not found:

```python
LookupPolicy = Literal["nearest", "nearest_prev", "nearest_next"]
```

- `"nearest"`: Return entry with closest timestamp (before or after)
- `"nearest_prev"`: Return entry with closest timestamp <= query time (default)
- `"nearest_next"`: Return entry with closest timestamp >= query time

### `TimeIndex[T]`

The main class:

```python
class TimeIndex(Generic[T]):
    def __init__(
        self,
        path: Path | str,
        model: type[T],
        policy: LookupPolicy = "nearest_prev",
        cache_size: int | None = None,  # None = unlimited (keep all in memory)
    ): ...
```

## API

### Construction

```python
from timeindex import TimeIndex
from pydantic import BaseModel

class AffectCore(BaseModel):
    valence: float
    arousal: float

# Create or open an index
index = TimeIndex("./state/affect_core.jsonl", AffectCore)

# With explicit policy
index = TimeIndex("./state/affect_core.jsonl", AffectCore, policy="nearest")
```

### Appending Values

```python
# Append with current time
index.append(AffectCore(valence=0.5, arousal=0.3))

# Append with explicit timestamp
from datetime import datetime, UTC
index.append(AffectCore(valence=0.6, arousal=0.4), t=datetime.now(UTC))

# Append with unix timestamp
index.append(AffectCore(valence=0.7, arousal=0.5), t=1734307200.123)
```

### Retrieving by Time

```python
# Get value at specific time (uses configured policy)
value: AffectCore = index[datetime.now(UTC)]
value: AffectCore = index[1734307200.0]  # Unix timestamp

# Get with explicit policy override
value = index.get(datetime.now(UTC), policy="nearest_next")

# Get timestamped wrapper (includes the actual timestamp of the entry)
entry: Timestamped[AffectCore] = index.get_entry(datetime.now(UTC))
print(entry.t, entry.v.valence)
```

### Retrieving Latest/Earliest

```python
# Most recent entry
latest: Timestamped[AffectCore] | None = index.latest()
if latest:
    print(latest.v.valence)

# Oldest entry
earliest: Timestamped[AffectCore] | None = index.earliest()
```

### Range Queries

```python
# Iterate over time range (inclusive)
for entry in index.range(start_time, end_time):
    print(entry.t, entry.v.valence)

# Get all entries as list
all_entries: list[Timestamped[AffectCore]] = list(index.all())

# Count entries
count: int = len(index)
```

### Slicing (Optional Sugar)

```python
# Slice by time range (returns iterator)
for entry in index[start:end]:
    print(entry.t, entry.v)
```

## Storage Format (JSONL)

Each line is a JSON object with `t` (timestamp) and `v` (value):

```jsonl
{"t": 1734307200.123, "v": {"valence": 0.5, "arousal": 0.3}}
{"t": 1734307260.456, "v": {"valence": 0.6, "arousal": 0.4}}
{"t": 1734307320.789, "v": {"valence": 0.7, "arousal": 0.5}}
```

**Invariants:**
- Entries are ordered by timestamp (append enforces this)
- Timestamps are Unix epoch floats (seconds with fractional milliseconds)
- Values are Pydantic model instances serialized via `.model_dump()`
- File is append-only (no in-place edits)

## Error Handling

### `TimeIndexEmpty`

Raised when querying an empty index:

```python
try:
    value = index[now]
except TimeIndexEmpty:
    print("No entries yet")
```

### `TimeIndexOutOfBounds`

Raised when using `nearest_prev` and query time is before all entries, or `nearest_next` and query time is after all entries:

```python
try:
    value = index.get(very_old_time, policy="nearest_prev")
except TimeIndexOutOfBounds:
    print("No entries at or before that time")
```

## Thread Safety

`TimeIndex` is **not thread-safe** by default. For concurrent access:

- Multiple readers: safe (no mutation)
- Single writer + readers: use external locking
- Multiple writers: use external locking

For async contexts, the caller should ensure serialized access to `append()`.

## Memory Model

On initialization:
1. If file exists, load all entries into memory as `list[Timestamped[T]]`
2. If file doesn't exist, create empty list (file created on first append)

On append:
1. Validate new timestamp >= latest timestamp (if any)
2. Append to in-memory list
3. Append JSON line to file (with flush)

On query:
1. Binary search in-memory list
2. Return value (no disk I/O)

This means:
- Reads are O(log n) and memory-only
- Writes are O(1) amortized (list append + file append)
- Memory usage is O(n) where n = number of entries
- Startup time is O(n) for initial load

For very large indices (millions of entries), a future version can add:
- Memory-mapped file access
- Sparse loading with file offset index
- LRU cache for entries

## Example: Full Usage

```python
from datetime import datetime, UTC, timedelta
from pathlib import Path
from pydantic import BaseModel
from timeindex import TimeIndex, Timestamped

class SensorReading(BaseModel):
    temperature: float
    humidity: float

# Create index
readings = TimeIndex(Path("./data/sensor.jsonl"), SensorReading)

# Append some data
readings.append(SensorReading(temperature=22.5, humidity=0.45))
readings.append(SensorReading(temperature=22.7, humidity=0.44))
readings.append(SensorReading(temperature=22.6, humidity=0.46))

# Query latest
latest = readings.latest()
print(f"Latest: {latest.v.temperature}C at {latest.datetime}")

# Query at specific time
now = datetime.now(UTC)
one_hour_ago = now - timedelta(hours=1)

try:
    reading = readings[one_hour_ago]
    print(f"Temperature 1h ago: {reading.temperature}C")
except TimeIndexOutOfBounds:
    print("No readings that old")

# Range query
for entry in readings.range(one_hour_ago, now):
    print(f"{entry.datetime}: {entry.v.temperature}C")
```

## Design Decisions

### Why JSONL?

- Human-readable (can inspect with `cat`, `tail -f`, `jq`)
- Append-only is natural (no corruption risk from partial writes)
- Line-oriented = easy to count, split, merge
- Git-friendly (line-based diffs)

### Why Unix Timestamps?

- Compact (float vs ISO string)
- Fast comparison (numeric vs string parsing)
- Timezone-agnostic storage (always UTC)
- Fractional seconds for high-resolution timing

### Why In-Memory Index?

- Sub-millisecond queries (critical for real-time loop)
- Simple implementation
- Memory is cheap for typical use (10M entries = ~1GB)
- Can optimize later if needed

### Why Pydantic?

- Schema validation on read/write
- Automatic JSON serialization
- Type hints propagate to IDE
- Easy evolution (add fields with defaults)
