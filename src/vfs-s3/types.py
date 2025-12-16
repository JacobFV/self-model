"""Type definitions for S3 VFS."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import json


@dataclass
class S3Bucket:
    """Represents an S3 bucket."""

    name: str
    creation_date: datetime
    region: str = "us-east-1"
    versioning: str = "Disabled"  # Enabled, Suspended, Disabled
    encryption: str | None = None
    public_access_blocked: bool = True
    lifecycle_rules: int = 0
    replication_enabled: bool = False
    logging_enabled: bool = False
    tags: dict[str, str] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps({
            "name": self.name,
            "creation_date": self.creation_date.isoformat(),
            "region": self.region,
            "versioning": self.versioning,
            "encryption": self.encryption,
            "public_access_blocked": self.public_access_blocked,
            "lifecycle_rules": self.lifecycle_rules,
            "replication_enabled": self.replication_enabled,
            "logging_enabled": self.logging_enabled,
            "tags": self.tags,
        }, indent=2)


@dataclass
class S3Object:
    """Represents an S3 object."""

    key: str
    bucket: str
    size: int
    etag: str
    last_modified: datetime
    storage_class: str = "STANDARD"
    version_id: str | None = None
    content_type: str | None = None
    content_encoding: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)
    tags: dict[str, str] = field(default_factory=dict)
    owner: str | None = None
    is_delete_marker: bool = False

    def to_json(self) -> str:
        return json.dumps({
            "key": self.key,
            "bucket": self.bucket,
            "size": self.size,
            "etag": self.etag,
            "last_modified": self.last_modified.isoformat(),
            "storage_class": self.storage_class,
            "version_id": self.version_id,
            "content_type": self.content_type,
            "content_encoding": self.content_encoding,
            "metadata": self.metadata,
            "tags": self.tags,
            "owner": self.owner,
            "is_delete_marker": self.is_delete_marker,
        }, indent=2)


@dataclass
class S3Version:
    """Represents a version of an S3 object."""

    key: str
    bucket: str
    version_id: str
    size: int
    etag: str
    last_modified: datetime
    is_latest: bool
    storage_class: str = "STANDARD"
    is_delete_marker: bool = False
    owner: str | None = None

    def to_json(self) -> str:
        return json.dumps({
            "key": self.key,
            "bucket": self.bucket,
            "version_id": self.version_id,
            "size": self.size,
            "etag": self.etag,
            "last_modified": self.last_modified.isoformat(),
            "is_latest": self.is_latest,
            "storage_class": self.storage_class,
            "is_delete_marker": self.is_delete_marker,
            "owner": self.owner,
        }, indent=2)
