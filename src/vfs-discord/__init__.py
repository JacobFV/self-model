"""
vfs-discord - Discord Virtual Filesystem

Projects Discord servers, channels, messages, and threads onto a filesystem structure.

## Filesystem Structure

```
/discord/
├── .user.json                          # Current user info
├── .connections.json                   # Connected accounts
│
├── guilds/                             # Servers
│   └── {guild-id}/                     # Or {guild-name} if unique
│       ├── .guild.json                 # Server metadata
│       ├── name.txt
│       ├── description.md
│       ├── icon.png
│       ├── banner.png
│       │
│       ├── channels/
│       │   ├── by-category/
│       │   │   └── {category}/
│       │   │       └── {channel} -> ../../{channel-id}
│       │   │
│       │   └── {channel-id}/           # Or {channel-name}
│       │       ├── .channel.json
│       │       ├── name.txt
│       │       ├── topic.txt           # (writable for mods)
│       │       ├── type.txt            # text/voice/announcement/forum
│       │       │
│       │       ├── messages/
│       │       │   ├── recent/         # Recent messages
│       │       │   │   └── {id}.txt
│       │       │   ├── {message-id}/
│       │       │   │   ├── .message.json
│       │       │   │   ├── content.md  # (writable for own messages)
│       │       │   │   ├── author.json
│       │       │   │   ├── timestamp.txt
│       │       │   │   ├── edited.txt
│       │       │   │   ├── attachments/
│       │       │   │   │   └── {filename}
│       │       │   │   ├── embeds/
│       │       │   │   │   └── {index}.json
│       │       │   │   ├── reactions/
│       │       │   │   │   └── {emoji}.json
│       │       │   │   └── thread/     # If message started thread
│       │       │   │       └── ... -> ../../../threads/{id}
│       │       │   └── new.txt         # Write to send message
│       │       │
│       │       ├── threads/
│       │       │   ├── active/
│       │       │   └── {thread-id}/
│       │       │       ├── .thread.json
│       │       │       ├── name.txt
│       │       │       └── messages/
│       │       │           └── ...
│       │       │
│       │       ├── pins/
│       │       │   └── {message-id} -> ../messages/{id}
│       │       │
│       │       └── webhooks/
│       │           └── {webhook-id}.json
│       │
│       ├── voice/
│       │   └── {channel-id}/
│       │       ├── .channel.json
│       │       └── members/            # Currently connected
│       │           └── {user-id}.json
│       │
│       ├── forums/
│       │   └── {forum-id}/
│       │       ├── .forum.json
│       │       ├── tags.json
│       │       └── posts/
│       │           └── {thread-id}/
│       │               ├── .post.json
│       │               ├── title.txt
│       │               ├── tags.json
│       │               └── messages/
│       │
│       ├── roles/
│       │   └── {role-id}/
│       │       ├── .role.json
│       │       ├── name.txt
│       │       ├── color.txt
│       │       ├── permissions.json
│       │       └── members/
│       │           └── {user-id} -> ../../members/{user-id}
│       │
│       ├── members/
│       │   └── {user-id}/
│       │       ├── .member.json
│       │       ├── nickname.txt
│       │       ├── roles.json
│       │       └── joined.txt
│       │
│       ├── emojis/
│       │   └── {emoji-name}.png
│       │
│       ├── stickers/
│       │   └── {sticker-name}.png
│       │
│       ├── scheduled_events/
│       │   └── {event-id}/
│       │       ├── .event.json
│       │       ├── name.txt
│       │       ├── description.md
│       │       └── start_time.txt
│       │
│       └── audit_log/
│           └── {entry-id}.json
│
├── dms/                                # Direct messages
│   └── {user-id}/                      # Or {username}
│       ├── .channel.json
│       └── messages/
│           └── ...
│
├── group_dms/
│   └── {channel-id}/
│       ├── .channel.json
│       ├── name.txt
│       ├── members/
│       └── messages/
│
└── friends/
    ├── {user-id}.json
    └── pending/
        └── {user-id}.json
```

## Capabilities

- READ: Browse servers, channels, read messages
- WRITE: Send messages, edit own messages, update own profile
- CREATE: Create threads, add reactions
- DELETE: Delete own messages

## Configuration

```python
DiscordVFS(
    token="...",                # Bot token or user token
    # For bots
    bot=True,
    # Options
    cache_ttl=60,               # Discord data changes frequently
    message_limit=100,          # Messages to fetch per channel
    include_nsfw=False,
)
```

Note: User tokens are against Discord ToS. Use bot tokens for automation.
"""

from .provider import DiscordVFS
from .types import DiscordGuild, DiscordChannel, DiscordMessage, DiscordUser

__all__ = ["DiscordVFS", "DiscordGuild", "DiscordChannel", "DiscordMessage", "DiscordUser"]
__version__ = "0.1.0"

Provider = DiscordVFS


def get_provider_class():
    return DiscordVFS


def register(registry):
    registry.register(
        name="discord",
        provider_class=DiscordVFS,
        description="Discord servers, channels, messages, threads",
        required_config=["token"],
        optional_config=["bot", "cache_ttl", "message_limit"],
    )
