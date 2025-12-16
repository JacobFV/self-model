"""Type definitions for Redis VFS."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import json


@dataclass
class RedisKey:
    """Represents a Redis key."""

    name: str
    key_type: str  # string, hash, list, set, zset, stream
    ttl: int | None = None  # TTL in seconds, None = no expiry
    size: int = 0  # Memory usage in bytes
    encoding: str = ""
    db: int = 0

    def to_json(self) -> str:
        return json.dumps({
            "name": self.name,
            "type": self.key_type,
            "ttl": self.ttl,
            "size": self.size,
            "encoding": self.encoding,
            "db": self.db,
        }, indent=2)


@dataclass
class RedisString:
    """Represents a Redis string value."""

    key: str
    value: str
    ttl: int | None = None
    db: int = 0

    def to_json(self) -> str:
        return json.dumps({
            "key": self.key,
            "value": self.value,
            "ttl": self.ttl,
            "db": self.db,
        }, indent=2)


@dataclass
class RedisHash:
    """Represents a Redis hash."""

    key: str
    fields: dict[str, str] = field(default_factory=dict)
    ttl: int | None = None
    db: int = 0

    def to_json(self) -> str:
        return json.dumps({
            "key": self.key,
            "fields": self.fields,
            "ttl": self.ttl,
            "db": self.db,
        }, indent=2)


@dataclass
class RedisList:
    """Represents a Redis list."""

    key: str
    values: list[str] = field(default_factory=list)
    length: int = 0
    ttl: int | None = None
    db: int = 0

    def to_json(self) -> str:
        return json.dumps({
            "key": self.key,
            "values": self.values,
            "length": self.length,
            "ttl": self.ttl,
            "db": self.db,
        }, indent=2)


@dataclass
class RedisSet:
    """Represents a Redis set."""

    key: str
    members: list[str] = field(default_factory=list)
    cardinality: int = 0
    ttl: int | None = None
    db: int = 0

    def to_json(self) -> str:
        return json.dumps({
            "key": self.key,
            "members": self.members,
            "cardinality": self.cardinality,
            "ttl": self.ttl,
            "db": self.db,
        }, indent=2)


@dataclass
class RedisSortedSet:
    """Represents a Redis sorted set."""

    key: str
    members: dict[str, float] = field(default_factory=dict)  # member -> score
    cardinality: int = 0
    ttl: int | None = None
    db: int = 0

    def to_json(self) -> str:
        return json.dumps({
            "key": self.key,
            "members": self.members,
            "cardinality": self.cardinality,
            "ttl": self.ttl,
            "db": self.db,
        }, indent=2)


@dataclass
class RedisStreamEntry:
    """Represents a Redis stream entry."""

    entry_id: str
    fields: dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_json(self) -> str:
        return json.dumps({
            "id": self.entry_id,
            "fields": self.fields,
            "timestamp": self.timestamp.isoformat(),
        }, indent=2)


@dataclass
class RedisStream:
    """Represents a Redis stream."""

    key: str
    length: int = 0
    first_entry_id: str | None = None
    last_entry_id: str | None = None
    groups: list[str] = field(default_factory=list)
    ttl: int | None = None
    db: int = 0

    def to_json(self) -> str:
        return json.dumps({
            "key": self.key,
            "length": self.length,
            "first_entry_id": self.first_entry_id,
            "last_entry_id": self.last_entry_id,
            "groups": self.groups,
            "ttl": self.ttl,
            "db": self.db,
        }, indent=2)
