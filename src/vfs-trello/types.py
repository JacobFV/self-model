"""Type definitions for Trello VFS."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import json


@dataclass
class TrelloBoard:
    """Represents a Trello board."""

    id: str
    name: str
    desc: str = ""
    url: str = ""
    short_url: str = ""
    closed: bool = False
    starred: bool = False
    pinned: bool = False
    id_organization: str | None = None
    organization_name: str = ""
    prefs: dict[str, Any] = field(default_factory=dict)
    label_names: dict[str, str] = field(default_factory=dict)
    power_ups: list[str] = field(default_factory=list)
    subscribed: bool = False
    date_last_activity: datetime = field(default_factory=datetime.now)
    date_last_view: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "name": self.name,
            "desc": self.desc,
            "url": self.url,
            "short_url": self.short_url,
            "closed": self.closed,
            "starred": self.starred,
            "pinned": self.pinned,
            "id_organization": self.id_organization,
            "organization_name": self.organization_name,
            "prefs": self.prefs,
            "label_names": self.label_names,
            "power_ups": self.power_ups,
            "subscribed": self.subscribed,
            "date_last_activity": self.date_last_activity.isoformat(),
            "date_last_view": self.date_last_view.isoformat(),
            "created_at": self.created_at.isoformat(),
        }, indent=2)


@dataclass
class TrelloList:
    """Represents a Trello list."""

    id: str
    name: str
    id_board: str
    closed: bool = False
    pos: float = 0.0
    subscribed: bool = False
    soft_limit: int | None = None

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "name": self.name,
            "id_board": self.id_board,
            "closed": self.closed,
            "pos": self.pos,
            "subscribed": self.subscribed,
            "soft_limit": self.soft_limit,
        }, indent=2)


@dataclass
class TrelloCard:
    """Represents a Trello card."""

    id: str
    name: str
    desc: str = ""
    url: str = ""
    short_url: str = ""
    id_board: str = ""
    id_list: str = ""
    list_name: str = ""
    closed: bool = False
    pos: float = 0.0
    due: datetime | None = None
    due_complete: bool = False
    due_reminder: int | None = None
    start: datetime | None = None
    subscribed: bool = False
    id_members: list[str] = field(default_factory=list)
    id_labels: list[str] = field(default_factory=list)
    labels: list[dict[str, Any]] = field(default_factory=list)
    id_checklists: list[str] = field(default_factory=list)
    id_attachments: list[str] = field(default_factory=list)
    badges: dict[str, Any] = field(default_factory=dict)
    cover: dict[str, Any] | None = None
    custom_field_items: list[dict[str, Any]] = field(default_factory=list)
    date_last_activity: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "name": self.name,
            "desc": self.desc,
            "url": self.url,
            "short_url": self.short_url,
            "id_board": self.id_board,
            "id_list": self.id_list,
            "list_name": self.list_name,
            "closed": self.closed,
            "pos": self.pos,
            "due": self.due.isoformat() if self.due else None,
            "due_complete": self.due_complete,
            "due_reminder": self.due_reminder,
            "start": self.start.isoformat() if self.start else None,
            "subscribed": self.subscribed,
            "id_members": self.id_members,
            "id_labels": self.id_labels,
            "labels": self.labels,
            "id_checklists": self.id_checklists,
            "id_attachments": self.id_attachments,
            "badges": self.badges,
            "cover": self.cover,
            "custom_field_items": self.custom_field_items,
            "date_last_activity": self.date_last_activity.isoformat(),
            "created_at": self.created_at.isoformat(),
        }, indent=2)


@dataclass
class TrelloChecklist:
    """Represents a Trello checklist."""

    id: str
    name: str
    id_card: str
    id_board: str
    pos: float = 0.0
    check_items: list[dict[str, Any]] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "name": self.name,
            "id_card": self.id_card,
            "id_board": self.id_board,
            "pos": self.pos,
            "check_items": self.check_items,
        }, indent=2)
