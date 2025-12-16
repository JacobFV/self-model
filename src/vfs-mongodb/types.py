"""Type definitions for MongoDB VFS."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import json


@dataclass
class MongoDatabase:
    """Represents a MongoDB database."""

    name: str
    size_on_disk: int  # bytes
    empty: bool
    collections_count: int
    views_count: int
    indexes_count: int
    data_size: int
    storage_size: int
    index_size: int
    created: datetime | None = None

    def to_json(self) -> str:
        return json.dumps({
            "name": self.name,
            "size_on_disk": self.size_on_disk,
            "empty": self.empty,
            "collections": self.collections_count,
            "views": self.views_count,
            "indexes": self.indexes_count,
            "data_size": self.data_size,
            "storage_size": self.storage_size,
            "index_size": self.index_size,
            "created": self.created.isoformat() if self.created else None,
        }, indent=2)


@dataclass
class MongoCollection:
    """Represents a MongoDB collection."""

    name: str
    database: str
    collection_type: str  # collection, view, timeseries
    count: int
    size: int  # bytes
    storage_size: int
    avg_obj_size: int
    total_index_size: int
    indexes_count: int
    capped: bool = False
    max_documents: int | None = None
    max_size: int | None = None
    validator: dict[str, Any] | None = None
    validation_level: str | None = None  # off, strict, moderate
    validation_action: str | None = None  # error, warn
    view_on: str | None = None  # For views
    pipeline: list[dict[str, Any]] | None = None  # For views

    def to_json(self) -> str:
        return json.dumps({
            "name": self.name,
            "database": self.database,
            "type": self.collection_type,
            "count": self.count,
            "size": self.size,
            "storage_size": self.storage_size,
            "avg_obj_size": self.avg_obj_size,
            "total_index_size": self.total_index_size,
            "indexes": self.indexes_count,
            "capped": self.capped,
            "max_documents": self.max_documents,
            "max_size": self.max_size,
            "validator": self.validator,
            "validation_level": self.validation_level,
            "validation_action": self.validation_action,
            "view_on": self.view_on,
            "pipeline": self.pipeline,
        }, indent=2)


@dataclass
class MongoDocument:
    """Represents a MongoDB document."""

    id: Any  # _id field (can be ObjectId, string, int, etc.)
    collection: str
    database: str
    data: dict[str, Any]
    size: int  # bytes
    created: datetime | None = None
    modified: datetime | None = None

    def to_json(self) -> str:
        # Convert document data to JSON, handling special types
        def convert_value(val: Any) -> Any:
            if hasattr(val, 'isoformat'):  # datetime
                return val.isoformat()
            elif isinstance(val, bytes):
                return f"<{len(val)} bytes>"
            elif hasattr(val, '__dict__'):  # Custom objects
                return str(val)
            return val

        converted_data = {k: convert_value(v) for k, v in self.data.items()}

        return json.dumps({
            "_id": str(self.id),
            "collection": self.collection,
            "database": self.database,
            "size": self.size,
            "created": self.created.isoformat() if self.created else None,
            "modified": self.modified.isoformat() if self.modified else None,
            "data": converted_data,
        }, indent=2)
