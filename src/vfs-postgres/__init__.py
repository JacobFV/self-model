"""
vfs-postgres - PostgreSQL Virtual Filesystem

Projects PostgreSQL databases, schemas, tables, and data onto a filesystem structure.

## Filesystem Structure

```
/postgres/
├── .server.json                        # Server info (version, settings)
├── .databases.json                     # List of databases
├── {database}/
│   ├── .database.json                  # Database info
│   ├── .extensions.json                # Installed extensions
│   ├── .settings.json                  # Database-level settings
│   └── {schema}/                       # Default: public
│       ├── .schema.json
│       │
│       ├── tables/
│       │   └── {table}/
│       │       ├── .table.json         # Table metadata
│       │       ├── schema.sql          # CREATE TABLE statement
│       │       ├── columns.json        # Column definitions
│       │       ├── constraints.json    # PKs, FKs, checks, uniques
│       │       ├── indexes.json        # Index definitions
│       │       ├── triggers.json       # Trigger definitions
│       │       ├── stats.json          # Table statistics
│       │       ├── privileges.json     # Access privileges
│       │       │
│       │       ├── data/               # Row access
│       │       │   ├── .count.txt      # Row count
│       │       │   ├── {pk}.json       # Row by primary key
│       │       │   └── query/          # Query interface
│       │       │       └── {where-clause}.jsonl
│       │       │
│       │       └── sample/             # Sample data
│       │           ├── first-10.jsonl  # First 10 rows
│       │           └── random-10.jsonl # Random 10 rows
│       │
│       ├── views/
│       │   └── {view}/
│       │       ├── .view.json
│       │       ├── definition.sql      # View definition
│       │       ├── columns.json
│       │       └── data/
│       │           └── ...
│       │
│       ├── materialized_views/
│       │   └── {mview}/
│       │       ├── .mview.json
│       │       ├── definition.sql
│       │       └── data/
│       │
│       ├── functions/
│       │   └── {function}/
│       │       ├── .function.json      # Metadata (args, return type)
│       │       ├── definition.sql      # Function body
│       │       └── overloads/          # If overloaded
│       │           └── {signature}.sql
│       │
│       ├── procedures/
│       │   └── {procedure}/
│       │       ├── .procedure.json
│       │       └── definition.sql
│       │
│       ├── types/
│       │   ├── enums/
│       │   │   └── {enum}/
│       │   │       ├── .enum.json
│       │   │       └── values.txt      # One value per line
│       │   └── composites/
│       │       └── {type}/
│       │           ├── .type.json
│       │           └── definition.sql
│       │
│       ├── sequences/
│       │   └── {sequence}/
│       │       ├── .sequence.json
│       │       ├── current.txt         # Current value
│       │       └── definition.sql
│       │
│       └── foreign_tables/
│           └── {table}/
│               └── ...
│
├── roles/
│   └── {role}/
│       ├── .role.json
│       ├── privileges.json
│       └── members.json                # Role memberships
│
└── replication/                        # If replication configured
    ├── slots/
    │   └── {slot}.json
    └── publications/
        └── {pub}.json
```

## Query Interface

Reading from special paths executes queries:
- `data/{pk}.json` - Select row by primary key
- `data/query/{where}.jsonl` - Select with WHERE clause (URL-encoded)
- `sample/first-10.jsonl` - `SELECT * LIMIT 10`
- `sample/random-10.jsonl` - `SELECT * ORDER BY RANDOM() LIMIT 10`

Writing to special paths:
- `data/new.json` - INSERT new row
- `data/{pk}.json` - UPDATE existing row
- `data/{pk}` (DELETE) - DELETE row

## Capabilities

- READ: Browse schema, read data
- WRITE: Update rows, modify schema
- CREATE: Create tables, insert rows
- DELETE: Delete rows, drop tables

## Configuration

```python
PostgresVFS(
    connection_string="postgresql://user:pass@localhost:5432/dbname",
    # Or individual params
    host="localhost",
    port=5432,
    database="mydb",
    user="postgres",
    password="...",
    # Options
    cache_ttl=300,
    row_limit=1000,             # Max rows per query
    include_system_schemas=False,
)
```
"""

from .provider import PostgresVFS
from .types import PgDatabase, PgTable, PgColumn, PgIndex

__all__ = ["PostgresVFS", "PgDatabase", "PgTable", "PgColumn", "PgIndex"]
__version__ = "0.1.0"

Provider = PostgresVFS


def get_provider_class():
    return PostgresVFS


def register(registry):
    registry.register(
        name="postgres",
        provider_class=PostgresVFS,
        description="PostgreSQL databases, schemas, tables, data",
        required_config=["connection_string"],
        optional_config=["cache_ttl", "row_limit"],
    )
