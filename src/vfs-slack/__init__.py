"""
vfs-slack - Slack Virtual Filesystem

Projects Slack workspaces, channels, and messages onto a filesystem structure.

## Filesystem Structure

```
/slack/
├── {workspace-id}/
│   ├── .workspace.json              # Workspace metadata
│   ├── channels/
│   │   ├── {channel-name}/
│   │   │   ├── .channel.json        # Channel metadata (id, topic, purpose, members)
│   │   │   ├── topic.txt            # Channel topic (writable)
│   │   │   ├── purpose.txt          # Channel purpose (writable)
│   │   │   ├── pinned/              # Pinned messages
│   │   │   │   └── {ts}.txt
│   │   │   ├── messages/
│   │   │   │   ├── {ts}-{user}.txt  # Message content
│   │   │   │   ├── {ts}-{user}.json # Message with full metadata
│   │   │   │   └── new.txt          # Write here to post message
│   │   │   └── threads/
│   │   │       └── {parent-ts}/
│   │   │           ├── .thread.json # Thread metadata
│   │   │           ├── {ts}-{user}.txt
│   │   │           └── new.txt      # Write to reply
│   │   └── ...
│   ├── dms/
│   │   └── {user-name}/
│   │       ├── .conversation.json
│   │       └── messages/
│   │           └── ...
│   ├── groups/                      # Private channels / group DMs
│   │   └── {group-name}/
│   │       └── ...
│   ├── users/
│   │   ├── {user-id}.json          # User profile
│   │   └── by-name/
│   │       └── {username} -> ../{user-id}.json  # Symlinks
│   ├── files/
│   │   ├── {file-id}/
│   │   │   ├── .file.json          # File metadata
│   │   │   └── {filename}          # Actual file content
│   │   └── by-channel/
│   │       └── {channel}/ -> symlinks to files
│   ├── emoji/
│   │   └── {emoji-name}.png        # Custom emoji
│   ├── apps/
│   │   └── {app-id}.json           # Installed app info
│   └── search/
│       └── {query}.results         # Search results (read triggers search)
```

## Capabilities

- READ: Browse channels, read messages, view user profiles
- WRITE: Post messages, edit own messages, update channel topic
- CREATE: Create channels (mkdir in channels/)
- DELETE: Delete own messages

## Configuration

```python
SlackVFS(
    token="xoxb-...",           # Bot token or user token
    workspace_id="T123...",     # Optional: specific workspace
    cache_ttl=300,              # Cache TTL in seconds
    message_limit=100,          # Messages to fetch per channel
    include_archived=False,     # Include archived channels
)
```

## Usage

```bash
# Register with vfsd
vfsd register slack --config token=xoxb-your-token

# Or use programmatically
from vfs_slack import SlackVFS
provider = SlackVFS(token="xoxb-...")
```
"""

from .provider import SlackVFS
from .types import SlackMessage, SlackChannel, SlackUser, SlackFile

__all__ = ["SlackVFS", "SlackMessage", "SlackChannel", "SlackUser", "SlackFile"]
__version__ = "0.1.0"

# Entry point for vfsd discovery
Provider = SlackVFS


def get_provider_class():
    return SlackVFS


def register(registry):
    """Register with vfsd registry."""
    registry.register(
        name="slack",
        provider_class=SlackVFS,
        description="Slack workspaces, channels, messages, threads",
        required_config=["token"],
        optional_config=["workspace_id", "cache_ttl", "message_limit"],
    )
