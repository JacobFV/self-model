"""
vfs-mongodb - MongoDB Virtual Filesystem

Projects MongoDB databases, collections, and documents onto a filesystem structure.

## Filesystem Structure

```
/mongodb/
├── .server.json                        # Server info, version
├── .databases.json                     # List of databases
├── {database}/
│   ├── .database.json                  # Database stats
│   ├── .stats.json                     # dbStats output
│   └── {collection}/
│       ├── .collection.json            # Collection metadata
│       ├── .stats.json                 # collStats output
│       ├── indexes/
│       │   ├── .indexes.json           # All indexes
│       │   └── {index-name}.json       # Individual index def
│       ├── schema.json                 # Inferred/validation schema
│       ├── sample.jsonl                # Sample documents
│       │
│       ├── documents/
│       │   ├── .count.txt              # Document count
│       │   ├── {_id}.json              # Document by _id
│       │   └── {_id}/                  # Or as directory for large docs
│       │       ├── .document.json      # Full document
│       │       └── {field}.json        # Individual fields
│       │
│       ├── query/                      # Query interface
│       │   ├── {filter-hash}.jsonl     # Cached query results
│       │   └── new.json                # Write query here to execute
│       │
│       ├── aggregate/                  # Aggregation interface
│       │   ├── {pipeline-hash}.jsonl   # Cached aggregation results
│       │   └── new.json                # Write pipeline here
│       │
│       └── watch/                      # Change streams
│           └── stream.jsonl            # Live change events
│
├── gridfs/                             # GridFS files
│   └── {database}/
│       └── {bucket}/                   # Default: fs
│           ├── .bucket.json
│           └── files/
│               └── {filename}          # File content
│                   # or {_id} if filename not unique
│
├── users/
│   └── {database}/
│       └── {user}.json                 # User info
│
└── replication/                        # Replica set info
    ├── .replset.json
    ├── status.json                     # rs.status()
    └── members/
        └── {member}.json
```

## Query Interface

Query syntax (write to `query/new.json`):
```json
{
  "filter": {"status": "active"},
  "projection": {"name": 1, "email": 1},
  "sort": {"created": -1},
  "limit": 100,
  "skip": 0
}
```

Aggregation syntax (write to `aggregate/new.json`):
```json
[
  {"$match": {"status": "active"}},
  {"$group": {"_id": "$category", "count": {"$sum": 1}}},
  {"$sort": {"count": -1}}
]
```

## Capabilities

- READ: Browse collections, read documents
- WRITE: Update documents
- CREATE: Create collections, insert documents
- DELETE: Delete documents, drop collections

## Configuration

```python
MongoDBVFS(
    connection_string="mongodb://localhost:27017",
    # Or individual params
    host="localhost",
    port=27017,
    username=None,
    password=None,
    auth_source="admin",
    # Options
    cache_ttl=300,
    document_limit=1000,        # Max documents per query
    infer_schema=True,          # Generate schema.json
)
```
"""

from .provider import MongoDBVFS
from .types import MongoDatabase, MongoCollection, MongoDocument

__all__ = ["MongoDBVFS", "MongoDatabase", "MongoCollection", "MongoDocument"]
__version__ = "0.1.0"

Provider = MongoDBVFS


def get_provider_class():
    return MongoDBVFS


def register(registry):
    registry.register(
        name="mongodb",
        provider_class=MongoDBVFS,
        description="MongoDB databases, collections, documents",
        required_config=["connection_string"],
        optional_config=["cache_ttl", "document_limit", "infer_schema"],
    )
