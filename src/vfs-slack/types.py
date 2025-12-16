"""Type definitions for Slack VFS."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import json


@dataclass
class SlackMessage:
    """Represents a Slack message."""

    ts: str
    user_id: str
    user_name: str
    text: str
    channel_id: str = ""
    thread_ts: str | None = None
    reactions: list[dict] = field(default_factory=list)
    files: list[dict] = field(default_factory=list)
    attachments: list[dict] = field(default_factory=list)
    edited: bool = False
    is_pinned: bool = False

    @property
    def timestamp(self) -> datetime:
        return datetime.fromtimestamp(float(self.ts))

    @property
    def filename(self) -> str:
        safe_user = re.sub(r"[^\w\-]", "_", self.user_name)
        return f"{self.ts}-{safe_user}.txt"

    def to_text(self) -> str:
        lines = [f"From: {self.user_name}", f"Time: {self.timestamp.isoformat()}"]
        if self.edited:
            lines.append("(edited)")
        lines.extend(["", self.text])
        if self.reactions:
            lines.append("")
            reactions_str = " ".join(f":{r['name']}: ({r['count']})" for r in self.reactions)
            lines.append(f"Reactions: {reactions_str}")
        if self.files:
            lines.append("")
            lines.append("Attachments:")
            for f in self.files:
                lines.append(f"  - {f.get('name', 'unknown')}")
        return "\n".join(lines)

    def to_json(self) -> str:
        return json.dumps({
            "ts": self.ts,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "text": self.text,
            "channel_id": self.channel_id,
            "thread_ts": self.thread_ts,
            "reactions": self.reactions,
            "files": self.files,
            "edited": self.edited,
            "timestamp": self.timestamp.isoformat(),
        }, indent=2)


@dataclass
class SlackChannel:
    """Represents a Slack channel."""

    id: str
    name: str
    topic: str = ""
    purpose: str = ""
    is_private: bool = False
    is_archived: bool = False
    is_dm: bool = False
    is_mpim: bool = False  # Multi-person IM
    member_count: int = 0
    created: datetime = field(default_factory=datetime.now)

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "name": self.name,
            "topic": self.topic,
            "purpose": self.purpose,
            "is_private": self.is_private,
            "is_archived": self.is_archived,
            "is_dm": self.is_dm,
            "member_count": self.member_count,
            "created": self.created.isoformat(),
        }, indent=2)


@dataclass
class SlackUser:
    """Represents a Slack user."""

    id: str
    name: str
    real_name: str = ""
    display_name: str = ""
    email: str = ""
    title: str = ""
    status_text: str = ""
    status_emoji: str = ""
    is_bot: bool = False
    is_admin: bool = False
    is_owner: bool = False
    timezone: str = ""
    avatar_url: str = ""

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "name": self.name,
            "real_name": self.real_name,
            "display_name": self.display_name,
            "email": self.email,
            "title": self.title,
            "status": {"text": self.status_text, "emoji": self.status_emoji},
            "is_bot": self.is_bot,
            "is_admin": self.is_admin,
            "timezone": self.timezone,
            "avatar_url": self.avatar_url,
        }, indent=2)


@dataclass
class SlackFile:
    """Represents a Slack file."""

    id: str
    name: str
    title: str
    mimetype: str
    size: int
    url_private: str
    user_id: str
    created: datetime = field(default_factory=datetime.now)
    channels: list[str] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "name": self.name,
            "title": self.title,
            "mimetype": self.mimetype,
            "size": self.size,
            "url_private": self.url_private,
            "user_id": self.user_id,
            "created": self.created.isoformat(),
            "channels": self.channels,
        }, indent=2)


@dataclass
class SlackWorkspace:
    """Represents a Slack workspace."""

    id: str
    name: str
    domain: str
    email_domain: str = ""
    icon_url: str = ""

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "name": self.name,
            "domain": self.domain,
            "email_domain": self.email_domain,
            "icon_url": self.icon_url,
        }, indent=2)
