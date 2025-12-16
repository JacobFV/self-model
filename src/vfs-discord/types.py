"""Type definitions for Discord VFS."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import json


@dataclass
class DiscordUser:
    """Represents a Discord user."""

    id: str
    username: str
    discriminator: str
    avatar: str | None = None
    bot: bool = False
    system: bool = False
    verified: bool = False
    email: str | None = None
    flags: int = 0
    premium_type: int | None = None
    public_flags: int = 0
    avatar_url: str = ""

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "username": self.username,
            "discriminator": self.discriminator,
            "avatar": self.avatar,
            "bot": self.bot,
            "system": self.system,
            "verified": self.verified,
            "email": self.email,
            "flags": self.flags,
            "premium_type": self.premium_type,
            "public_flags": self.public_flags,
            "avatar_url": self.avatar_url,
        }, indent=2)


@dataclass
class DiscordGuild:
    """Represents a Discord guild (server)."""

    id: str
    name: str
    icon: str | None = None
    splash: str | None = None
    banner: str | None = None
    description: str = ""
    owner_id: str = ""
    region: str = ""
    afk_channel_id: str | None = None
    afk_timeout: int = 0
    verification_level: int = 0
    default_message_notifications: int = 0
    explicit_content_filter: int = 0
    features: list[str] = field(default_factory=list)
    mfa_level: int = 0
    system_channel_id: str | None = None
    max_presences: int | None = None
    max_members: int | None = None
    vanity_url_code: str | None = None
    premium_tier: int = 0
    premium_subscription_count: int = 0
    preferred_locale: str = "en-US"
    nsfw_level: int = 0
    member_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "name": self.name,
            "icon": self.icon,
            "splash": self.splash,
            "banner": self.banner,
            "description": self.description,
            "owner_id": self.owner_id,
            "region": self.region,
            "afk_channel_id": self.afk_channel_id,
            "afk_timeout": self.afk_timeout,
            "verification_level": self.verification_level,
            "default_message_notifications": self.default_message_notifications,
            "explicit_content_filter": self.explicit_content_filter,
            "features": self.features,
            "mfa_level": self.mfa_level,
            "system_channel_id": self.system_channel_id,
            "max_presences": self.max_presences,
            "max_members": self.max_members,
            "vanity_url_code": self.vanity_url_code,
            "premium_tier": self.premium_tier,
            "premium_subscription_count": self.premium_subscription_count,
            "preferred_locale": self.preferred_locale,
            "nsfw_level": self.nsfw_level,
            "member_count": self.member_count,
            "created_at": self.created_at.isoformat(),
        }, indent=2)


@dataclass
class DiscordChannel:
    """Represents a Discord channel."""

    id: str
    type: int  # 0=text, 2=voice, 4=category, 5=announcement, 15=forum
    guild_id: str | None = None
    name: str = ""
    topic: str = ""
    position: int = 0
    nsfw: bool = False
    last_message_id: str | None = None
    bitrate: int | None = None
    user_limit: int | None = None
    rate_limit_per_user: int = 0
    parent_id: str | None = None
    last_pin_timestamp: datetime | None = None
    permissions: str | None = None
    message_count: int = 0
    member_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "type": self.type,
            "guild_id": self.guild_id,
            "name": self.name,
            "topic": self.topic,
            "position": self.position,
            "nsfw": self.nsfw,
            "last_message_id": self.last_message_id,
            "bitrate": self.bitrate,
            "user_limit": self.user_limit,
            "rate_limit_per_user": self.rate_limit_per_user,
            "parent_id": self.parent_id,
            "last_pin_timestamp": self.last_pin_timestamp.isoformat() if self.last_pin_timestamp else None,
            "permissions": self.permissions,
            "message_count": self.message_count,
            "member_count": self.member_count,
            "created_at": self.created_at.isoformat(),
        }, indent=2)


@dataclass
class DiscordMessage:
    """Represents a Discord message."""

    id: str
    channel_id: str
    author: DiscordUser
    content: str
    timestamp: datetime
    edited_timestamp: datetime | None = None
    tts: bool = False
    mention_everyone: bool = False
    mentions: list[DiscordUser] = field(default_factory=list)
    mention_roles: list[str] = field(default_factory=list)
    attachments: list[dict[str, Any]] = field(default_factory=list)
    embeds: list[dict[str, Any]] = field(default_factory=list)
    reactions: list[dict[str, Any]] = field(default_factory=list)
    pinned: bool = False
    webhook_id: str | None = None
    type: int = 0
    thread_id: str | None = None
    flags: int = 0

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "channel_id": self.channel_id,
            "author": {
                "id": self.author.id,
                "username": self.author.username,
                "discriminator": self.author.discriminator,
                "avatar": self.author.avatar,
                "bot": self.author.bot,
            },
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "edited_timestamp": self.edited_timestamp.isoformat() if self.edited_timestamp else None,
            "tts": self.tts,
            "mention_everyone": self.mention_everyone,
            "mentions": [{"id": u.id, "username": u.username} for u in self.mentions],
            "mention_roles": self.mention_roles,
            "attachments": self.attachments,
            "embeds": self.embeds,
            "reactions": self.reactions,
            "pinned": self.pinned,
            "webhook_id": self.webhook_id,
            "type": self.type,
            "thread_id": self.thread_id,
            "flags": self.flags,
        }, indent=2)
