"""Type definitions for Dropbox VFS."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import json


@dataclass
class DropboxFile:
    """Represents a Dropbox file."""

    id: str
    name: str
    path_lower: str
    path_display: str
    size: int = 0
    rev: str = ""
    content_hash: str = ""
    client_modified: datetime = field(default_factory=datetime.now)
    server_modified: datetime = field(default_factory=datetime.now)
    is_downloadable: bool = True
    export_info: dict[str, str] | None = None
    has_explicit_shared_members: bool = False
    media_info: dict[str, Any] | None = None
    symlink_info: dict[str, str] | None = None
    sharing_info: dict[str, Any] | None = None
    property_groups: list[dict[str, Any]] = field(default_factory=list)
    preview_url: str | None = None

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "name": self.name,
            "path_lower": self.path_lower,
            "path_display": self.path_display,
            "size": self.size,
            "rev": self.rev,
            "content_hash": self.content_hash,
            "client_modified": self.client_modified.isoformat(),
            "server_modified": self.server_modified.isoformat(),
            "is_downloadable": self.is_downloadable,
            "export_info": self.export_info,
            "has_explicit_shared_members": self.has_explicit_shared_members,
            "media_info": self.media_info,
            "symlink_info": self.symlink_info,
            "sharing_info": self.sharing_info,
            "property_groups": self.property_groups,
            "preview_url": self.preview_url,
        }, indent=2)


@dataclass
class DropboxFolder:
    """Represents a Dropbox folder."""

    id: str
    name: str
    path_lower: str
    path_display: str
    shared_folder_id: str | None = None
    sharing_info: dict[str, Any] | None = None
    property_groups: list[dict[str, Any]] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "name": self.name,
            "path_lower": self.path_lower,
            "path_display": self.path_display,
            "shared_folder_id": self.shared_folder_id,
            "sharing_info": self.sharing_info,
            "property_groups": self.property_groups,
        }, indent=2)


@dataclass
class DropboxPaper:
    """Represents a Dropbox Paper document."""

    id: str
    name: str
    status: str = "active"  # active, archived
    owner: str = ""
    created_date: datetime = field(default_factory=datetime.now)
    last_updated_date: datetime = field(default_factory=datetime.now)
    last_editor: str | None = None
    revision: int = 1
    url: str = ""
    folder_id: str | None = None
    folder_sharing_policy_type: str | None = None

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "owner": self.owner,
            "created_date": self.created_date.isoformat(),
            "last_updated_date": self.last_updated_date.isoformat(),
            "last_editor": self.last_editor,
            "revision": self.revision,
            "url": self.url,
            "folder_id": self.folder_id,
            "folder_sharing_policy_type": self.folder_sharing_policy_type,
        }, indent=2)
