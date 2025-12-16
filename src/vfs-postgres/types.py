"""Type definitions for PostgreSQL VFS."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import json


@dataclass
class PgDatabase:
    """Represents a PostgreSQL database."""

    name: str
    owner: str
    encoding: str
    collation: str
    ctype: str
    size: int  # bytes
    created: datetime | None = None
    tablespace: str = "pg_default"
    connection_limit: int = -1
    extensions: list[str] = field(default_factory=list)
    schemas: list[str] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps({
            "name": self.name,
            "owner": self.owner,
            "encoding": self.encoding,
            "collation": self.collation,
            "ctype": self.ctype,
            "size": self.size,
            "created": self.created.isoformat() if self.created else None,
            "tablespace": self.tablespace,
            "connection_limit": self.connection_limit,
            "extensions": self.extensions,
            "schemas": self.schemas,
        }, indent=2)


@dataclass
class PgTable:
    """Represents a PostgreSQL table."""

    name: str
    schema: str
    database: str
    owner: str
    table_type: str  # BASE TABLE, VIEW, FOREIGN TABLE, etc.
    row_count: int
    size: int  # bytes
    created: datetime | None = None
    last_vacuum: datetime | None = None
    last_analyze: datetime | None = None
    has_indexes: bool = False
    has_triggers: bool = False
    has_rules: bool = False
    tablespace: str | None = None
    comment: str | None = None

    def to_json(self) -> str:
        return json.dumps({
            "name": self.name,
            "schema": self.schema,
            "database": self.database,
            "owner": self.owner,
            "type": self.table_type,
            "row_count": self.row_count,
            "size": self.size,
            "created": self.created.isoformat() if self.created else None,
            "last_vacuum": self.last_vacuum.isoformat() if self.last_vacuum else None,
            "last_analyze": self.last_analyze.isoformat() if self.last_analyze else None,
            "has_indexes": self.has_indexes,
            "has_triggers": self.has_triggers,
            "has_rules": self.has_rules,
            "tablespace": self.tablespace,
            "comment": self.comment,
        }, indent=2)


@dataclass
class PgColumn:
    """Represents a PostgreSQL column."""

    name: str
    table: str
    schema: str
    position: int
    data_type: str
    is_nullable: bool
    default_value: str | None = None
    max_length: int | None = None
    numeric_precision: int | None = None
    numeric_scale: int | None = None
    is_primary_key: bool = False
    is_foreign_key: bool = False
    is_unique: bool = False
    foreign_key_table: str | None = None
    foreign_key_column: str | None = None
    comment: str | None = None

    def to_json(self) -> str:
        return json.dumps({
            "name": self.name,
            "table": self.table,
            "schema": self.schema,
            "position": self.position,
            "data_type": self.data_type,
            "is_nullable": self.is_nullable,
            "default_value": self.default_value,
            "max_length": self.max_length,
            "numeric_precision": self.numeric_precision,
            "numeric_scale": self.numeric_scale,
            "is_primary_key": self.is_primary_key,
            "is_foreign_key": self.is_foreign_key,
            "is_unique": self.is_unique,
            "foreign_key_table": self.foreign_key_table,
            "foreign_key_column": self.foreign_key_column,
            "comment": self.comment,
        }, indent=2)


@dataclass
class PgIndex:
    """Represents a PostgreSQL index."""

    name: str
    table: str
    schema: str
    index_type: str  # btree, hash, gist, gin, etc.
    columns: list[str]
    is_unique: bool
    is_primary: bool
    is_valid: bool
    size: int  # bytes
    definition: str
    condition: str | None = None  # For partial indexes
    tablespace: str | None = None

    def to_json(self) -> str:
        return json.dumps({
            "name": self.name,
            "table": self.table,
            "schema": self.schema,
            "type": self.index_type,
            "columns": self.columns,
            "is_unique": self.is_unique,
            "is_primary": self.is_primary,
            "is_valid": self.is_valid,
            "size": self.size,
            "definition": self.definition,
            "condition": self.condition,
            "tablespace": self.tablespace,
        }, indent=2)
