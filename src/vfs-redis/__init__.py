"""
vfs-redis - Redis Virtual Filesystem

Projects Redis databases and data structures onto a filesystem structure.

## Filesystem Structure

```
/redis/
├── .info.json                          # Redis INFO output
├── .config.json                        # Redis CONFIG
├── .clients.json                       # Connected clients
├── .memory.json                        # Memory stats
│
├── db{n}/                              # Database 0-15
│   ├── .info.json                      # Database stats (keys, expires)
│   ├── .keys.txt                       # All keys (one per line)
│   │
│   ├── strings/                        # String keys
│   │   └── {key}                       # String value as file content
│   │       # Reading returns the value
│   │       # Writing sets the value
│   │
│   ├── hashes/                         # Hash keys
│   │   └── {key}/
│   │       ├── .hash.json              # Full hash as JSON
│   │       └── {field}                 # Individual field values
│   │           # Reading returns field value
│   │           # Writing sets field value
│   │
│   ├── lists/                          # List keys
│   │   └── {key}/
│   │       ├── .list.json              # Full list as JSON array
│   │       ├── .length.txt             # List length
│   │       ├── {index}                 # Element by index
│   │       ├── head                    # First element
│   │       ├── tail                    # Last element
│   │       └── range/
│   │           └── {start}-{stop}.json # Range slice
│   │
│   ├── sets/                           # Set keys
│   │   └── {key}/
│   │       ├── .set.json               # Full set as JSON array
│   │       ├── .cardinality.txt        # Set size
│   │       ├── .members.txt            # Members (one per line)
│   │       └── contains/
│   │           └── {member}            # Check membership (exists = true)
│   │
│   ├── zsets/                          # Sorted set keys
│   │   └── {key}/
│   │       ├── .zset.json              # Full sorted set with scores
│   │       ├── .cardinality.txt
│   │       ├── by-rank/
│   │       │   └── {start}-{stop}.json # By rank range
│   │       ├── by-score/
│   │       │   └── {min}-{max}.json    # By score range
│   │       └── {member}.score          # Individual member score
│   │
│   ├── streams/                        # Stream keys
│   │   └── {key}/
│   │       ├── .stream.json            # Stream info
│   │       ├── .length.txt
│   │       ├── entries/
│   │       │   └── {id}.json           # Individual entries
│   │       ├── range/
│   │       │   └── {start}-{end}.jsonl # Range of entries
│   │       ├── groups/                 # Consumer groups
│   │       │   └── {group}/
│   │       │       ├── .group.json
│   │       │       ├── pending.json
│   │       │       └── consumers/
│   │       │           └── {consumer}.json
│   │       └── tail.jsonl              # Latest entries (live)
│   │
│   ├── json/                           # RedisJSON keys
│   │   └── {key}/
│   │       ├── .json                   # Full JSON document
│   │       └── {path}                  # JSONPath access
│   │
│   └── timeseries/                     # RedisTimeSeries keys
│       └── {key}/
│           ├── .ts.json                # Time series info
│           ├── latest.json             # Latest sample
│           └── range/
│               └── {from}-{to}.jsonl   # Time range
│
├── pubsub/                             # Pub/Sub
│   ├── channels/
│   │   └── {channel}/
│   │       ├── .info.json
│   │       └── messages.jsonl          # Live messages (streaming)
│   └── patterns/
│       └── {pattern}/
│           └── messages.jsonl
│
├── cluster/                            # Cluster mode
│   ├── .info.json
│   ├── nodes/
│   │   └── {node-id}.json
│   └── slots.json
│
└── sentinel/                           # Sentinel mode
    ├── masters/
    │   └── {name}.json
    └── replicas/
        └── {master}/
            └── {replica}.json
```

## Key Patterns

Reading from special patterns:
- `strings/{key}` - GET key
- `hashes/{key}/{field}` - HGET key field
- `lists/{key}/{index}` - LINDEX key index
- `sets/{key}/.members.txt` - SMEMBERS key
- `zsets/{key}/by-score/0-100.json` - ZRANGEBYSCORE key 0 100 WITHSCORES

Writing:
- `strings/{key}` - SET key value
- `hashes/{key}/{field}` - HSET key field value
- `lists/{key}/push` - RPUSH key value
- `sets/{key}/add` - SADD key value
- `zsets/{key}/{member}.score` - ZADD key score member

## Capabilities

- READ: Browse keys, read values
- WRITE: Set values, update data structures
- CREATE: Create keys
- DELETE: Delete keys, remove elements

## Configuration

```python
RedisVFS(
    host="localhost",
    port=6379,
    password=None,
    db=0,                       # Default database
    # Or connection URL
    url="redis://localhost:6379/0",
    # Cluster mode
    cluster=False,
    # Options
    cache_ttl=60,
    decode_responses=True,      # Decode bytes to strings
    key_pattern="*",            # Filter keys
)
```
"""

from .provider import RedisVFS
from .types import RedisKey, RedisString, RedisHash, RedisList, RedisSet, RedisSortedSet, RedisStream

__all__ = ["RedisVFS", "RedisKey", "RedisString", "RedisHash", "RedisList", "RedisSet", "RedisSortedSet", "RedisStream"]
__version__ = "0.1.0"

Provider = RedisVFS


def get_provider_class():
    return RedisVFS


def register(registry):
    registry.register(
        name="redis",
        provider_class=RedisVFS,
        description="Redis keys, hashes, lists, sets, streams",
        required_config=[],
        optional_config=["host", "port", "password", "db", "url", "cache_ttl"],
    )
