"""Type definitions for Notion VFS."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import json


@dataclass
class NotionPage:
    """Represents a Notion page."""

    id: str
    title: str
    parent_id: str | None = None
    parent_type: str = "page"  # page, database, workspace
    icon: str | None = None  # Emoji or URL
    cover: str | None = None  # Cover image URL
    archived: bool = False
    url: str = ""
    public_url: str | None = None
    created_time: datetime = field(default_factory=datetime.now)
    last_edited_time: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    last_edited_by: str = ""
    properties: dict[str, Any] = field(default_factory=dict)
    has_children: bool = False
    children_count: int = 0

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "title": self.title,
            "parent": {
                "id": self.parent_id,
                "type": self.parent_type,
            } if self.parent_id else None,
            "icon": self.icon,
            "cover": self.cover,
            "archived": self.archived,
            "url": self.url,
            "public_url": self.public_url,
            "created_time": self.created_time.isoformat(),
            "last_edited_time": self.last_edited_time.isoformat(),
            "created_by": self.created_by,
            "last_edited_by": self.last_edited_by,
            "properties": self.properties,
            "has_children": self.has_children,
            "children_count": self.children_count,
        }, indent=2)


@dataclass
class NotionDatabase:
    """Represents a Notion database."""

    id: str
    title: str
    description: str = ""
    parent_id: str | None = None
    parent_type: str = "page"
    icon: str | None = None
    cover: str | None = None
    archived: bool = False
    url: str = ""
    public_url: str | None = None
    created_time: datetime = field(default_factory=datetime.now)
    last_edited_time: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    last_edited_by: str = ""
    properties: dict[str, Any] = field(default_factory=dict)  # Database schema
    is_inline: bool = False
    rows_count: int = 0

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "parent": {
                "id": self.parent_id,
                "type": self.parent_type,
            } if self.parent_id else None,
            "icon": self.icon,
            "cover": self.cover,
            "archived": self.archived,
            "url": self.url,
            "public_url": self.public_url,
            "created_time": self.created_time.isoformat(),
            "last_edited_time": self.last_edited_time.isoformat(),
            "created_by": self.created_by,
            "last_edited_by": self.last_edited_by,
            "properties": self.properties,
            "is_inline": self.is_inline,
            "rows_count": self.rows_count,
        }, indent=2)


@dataclass
class NotionBlock:
    """Represents a Notion block (content element)."""

    id: str
    type: str  # paragraph, heading_1, heading_2, heading_3, bulleted_list_item, etc.
    parent_id: str
    archived: bool = False
    has_children: bool = False
    created_time: datetime = field(default_factory=datetime.now)
    last_edited_time: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    last_edited_by: str = ""
    content: dict[str, Any] = field(default_factory=dict)  # Block-specific content
    text_content: str = ""  # Plain text representation
    children: list[NotionBlock] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "type": self.type,
            "parent_id": self.parent_id,
            "archived": self.archived,
            "has_children": self.has_children,
            "created_time": self.created_time.isoformat(),
            "last_edited_time": self.last_edited_time.isoformat(),
            "created_by": self.created_by,
            "last_edited_by": self.last_edited_by,
            "content": self.content,
            "text_content": self.text_content,
            "children_count": len(self.children),
        }, indent=2)
