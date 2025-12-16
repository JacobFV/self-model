"""Type definitions for Google Drive VFS."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import json


@dataclass
class GDriveFile:
    """Represents a Google Drive file."""

    id: str
    name: str
    mime_type: str
    size: int = 0
    parent_id: str | None = None
    parent_path: str = ""
    web_view_link: str = ""
    web_content_link: str = ""
    icon_link: str = ""
    thumbnail_link: str | None = None
    description: str = ""
    starred: bool = False
    trashed: bool = False
    explicitly_trashed: bool = False
    shared: bool = False
    owned_by_me: bool = True
    writers_can_share: bool = True
    viewed_by_me: bool = False
    modified_by_me: bool = False
    version: int = 1
    original_filename: str | None = None
    file_extension: str | None = None
    md5_checksum: str | None = None
    created_time: datetime = field(default_factory=datetime.now)
    modified_time: datetime = field(default_factory=datetime.now)
    viewed_by_me_time: datetime | None = None
    modified_by_me_time: datetime | None = None
    shared_with_me_time: datetime | None = None
    owner_names: list[str] = field(default_factory=list)
    owner_emails: list[str] = field(default_factory=list)
    last_modifying_user_name: str | None = None
    last_modifying_user_email: str | None = None
    sharing_user_name: str | None = None
    sharing_user_email: str | None = None
    permissions_count: int = 0
    export_links: dict[str, str] = field(default_factory=dict)  # For Google Workspace files

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "name": self.name,
            "mime_type": self.mime_type,
            "size": self.size,
            "parent_id": self.parent_id,
            "parent_path": self.parent_path,
            "web_view_link": self.web_view_link,
            "web_content_link": self.web_content_link,
            "icon_link": self.icon_link,
            "thumbnail_link": self.thumbnail_link,
            "description": self.description,
            "starred": self.starred,
            "trashed": self.trashed,
            "explicitly_trashed": self.explicitly_trashed,
            "shared": self.shared,
            "owned_by_me": self.owned_by_me,
            "writers_can_share": self.writers_can_share,
            "viewed_by_me": self.viewed_by_me,
            "modified_by_me": self.modified_by_me,
            "version": self.version,
            "original_filename": self.original_filename,
            "file_extension": self.file_extension,
            "md5_checksum": self.md5_checksum,
            "created_time": self.created_time.isoformat(),
            "modified_time": self.modified_time.isoformat(),
            "viewed_by_me_time": self.viewed_by_me_time.isoformat() if self.viewed_by_me_time else None,
            "modified_by_me_time": self.modified_by_me_time.isoformat() if self.modified_by_me_time else None,
            "shared_with_me_time": self.shared_with_me_time.isoformat() if self.shared_with_me_time else None,
            "owners": [{"name": name, "email": email} for name, email in zip(self.owner_names, self.owner_emails)],
            "last_modifying_user": {
                "name": self.last_modifying_user_name,
                "email": self.last_modifying_user_email,
            } if self.last_modifying_user_name else None,
            "sharing_user": {
                "name": self.sharing_user_name,
                "email": self.sharing_user_email,
            } if self.sharing_user_name else None,
            "permissions_count": self.permissions_count,
            "export_links": self.export_links,
        }, indent=2)


@dataclass
class GDriveFolder:
    """Represents a Google Drive folder."""

    id: str
    name: str
    parent_id: str | None = None
    parent_path: str = ""
    web_view_link: str = ""
    icon_link: str = ""
    description: str = ""
    starred: bool = False
    trashed: bool = False
    explicitly_trashed: bool = False
    shared: bool = False
    owned_by_me: bool = True
    created_time: datetime = field(default_factory=datetime.now)
    modified_time: datetime = field(default_factory=datetime.now)
    owner_names: list[str] = field(default_factory=list)
    owner_emails: list[str] = field(default_factory=list)
    last_modifying_user_name: str | None = None
    last_modifying_user_email: str | None = None
    folder_color_rgb: str | None = None
    children_count: int = 0
    permissions_count: int = 0

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "name": self.name,
            "parent_id": self.parent_id,
            "parent_path": self.parent_path,
            "web_view_link": self.web_view_link,
            "icon_link": self.icon_link,
            "description": self.description,
            "starred": self.starred,
            "trashed": self.trashed,
            "explicitly_trashed": self.explicitly_trashed,
            "shared": self.shared,
            "owned_by_me": self.owned_by_me,
            "created_time": self.created_time.isoformat(),
            "modified_time": self.modified_time.isoformat(),
            "owners": [{"name": name, "email": email} for name, email in zip(self.owner_names, self.owner_emails)],
            "last_modifying_user": {
                "name": self.last_modifying_user_name,
                "email": self.last_modifying_user_email,
            } if self.last_modifying_user_name else None,
            "folder_color_rgb": self.folder_color_rgb,
            "children_count": self.children_count,
            "permissions_count": self.permissions_count,
        }, indent=2)


@dataclass
class GDrivePermission:
    """Represents a Google Drive permission/sharing setting."""

    id: str
    type: str  # user, group, domain, anyone
    role: str  # owner, organizer, fileOrganizer, writer, commenter, reader
    email_address: str | None = None
    display_name: str | None = None
    domain: str | None = None
    allow_file_discovery: bool = False
    deleted: bool = False
    pending_owner: bool = False
    expiration_time: datetime | None = None
    permission_details: list[dict[str, Any]] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "type": self.type,
            "role": self.role,
            "email_address": self.email_address,
            "display_name": self.display_name,
            "domain": self.domain,
            "allow_file_discovery": self.allow_file_discovery,
            "deleted": self.deleted,
            "pending_owner": self.pending_owner,
            "expiration_time": self.expiration_time.isoformat() if self.expiration_time else None,
            "permission_details": self.permission_details,
        }, indent=2)
