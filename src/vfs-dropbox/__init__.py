"""
vfs-dropbox - Dropbox Virtual Filesystem

Projects Dropbox files, folders, and Paper docs onto a filesystem structure.

## Filesystem Structure

```
/dropbox/
├── home/                               # User's Dropbox root
│   ├── .account.json                   # Account info
│   ├── .space.json                     # Space usage
│   └── {path}/                         # Files and folders
│       ├── {file}                      # File content
│       └── {folder}/
├── team/                               # Team folders (Business)
│   ├── .team.json
│   └── {team-folder}/
│       └── {path}/
├── shared/                             # Shared folders
│   └── {shared-folder}/
│       ├── .sharing.json               # Sharing settings
│       └── {path}/
├── links/                              # Shared links
│   └── {link-key}/
│       ├── .link.json                  # Link metadata
│       └── {file}                      # Linked content
├── paper/                              # Dropbox Paper docs
│   └── {doc-id}/
│       ├── .paper.json                 # Paper metadata
│       ├── content.md                  # Markdown content
│       ├── content.html                # HTML content
│       └── comments/
│           └── {comment-id}.md
├── requests/                           # File requests
│   └── {request-id}/
│       ├── .request.json
│       └── uploads/
└── history/                            # Version history
    └── {path}/
        └── {revision}.{ext}

## File Extended Attributes

- user.dropbox.id              # File/folder ID
- user.dropbox.rev             # Revision
- user.dropbox.content_hash    # Content hash
- user.dropbox.sharing_info    # Sharing info JSON
- user.dropbox.has_explicit_shared_members

## Capabilities

- READ: Browse files, download content
- WRITE: Upload files, modify content
- CREATE: Create folders, upload files
- DELETE: Delete files/folders

## Configuration

```python
DropboxVFS(
    access_token="...",         # OAuth2 access token
    # Or use refresh token
    app_key="...",
    app_secret="...",
    refresh_token="...",
    cache_ttl=300,
    include_deleted=False,
)
```
"""

from .provider import DropboxVFS
from .types import DropboxFile, DropboxFolder, DropboxPaper

__all__ = ["DropboxVFS", "DropboxFile", "DropboxFolder", "DropboxPaper"]
__version__ = "0.1.0"

Provider = DropboxVFS


def get_provider_class():
    return DropboxVFS


def register(registry):
    registry.register(
        name="dropbox",
        provider_class=DropboxVFS,
        description="Dropbox files, folders, Paper docs",
        required_config=["access_token"],
        optional_config=["app_key", "app_secret", "refresh_token", "cache_ttl"],
    )
