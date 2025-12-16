"""
vfs-gdrive - Google Drive Virtual Filesystem

Projects Google Drive files, folders, and shared drives onto a filesystem structure.

## Filesystem Structure

```
/gdrive/
├── my-drive/
│   ├── .drive.json                     # Drive metadata
│   ├── .quota.json                     # Storage quota info
│   └── {folder}/
│       ├── .folder.json                # Folder metadata
│       └── {file-or-folder}/
│           └── ...
├── shared-drives/                      # Team/shared drives
│   └── {drive-name}/
│       ├── .drive.json
│       └── {path}/
├── shared-with-me/
│   ├── by-owner/
│   │   └── {owner-email}/
│   │       └── {file}
│   └── {file-or-folder}
├── starred/
│   └── {file} -> ../my-drive/{path}    # Symlinks to starred items
├── recent/
│   └── {file} -> ../my-drive/{path}    # Recent files
├── trash/
│   └── {file}                          # Trashed files
└── search/
    └── {query}/
        └── results/

## File Extended Attributes (xattr)

Each file supports extended attributes for Google-specific metadata:
- user.gdrive.id           # File ID
- user.gdrive.mimeType     # MIME type
- user.gdrive.webViewLink  # Web URL
- user.gdrive.owners       # JSON array of owners
- user.gdrive.shared       # true/false
- user.gdrive.permissions  # JSON permissions array
- user.gdrive.version      # File version

## Google Docs/Sheets/Slides

Google Workspace files are exported to standard formats:
- Documents -> .docx or .md (configurable)
- Spreadsheets -> .xlsx or .csv
- Presentations -> .pptx
- Drawings -> .svg or .png

Original format available via:
- {file}.gdoc.json         # Native format link

## Capabilities

- READ: Browse files, download content
- WRITE: Upload files, update content
- CREATE: Create folders, upload files
- DELETE: Move to trash, permanent delete

## Configuration

```python
GDriveVFS(
    credentials_path="~/.config/gdrive/credentials.json",
    # Or use service account
    service_account_path="service-account.json",
    cache_ttl=300,
    export_format="markdown",   # For Google Docs: markdown|docx|pdf|txt
    include_trashed=False,
)
```
"""

from .provider import GDriveVFS
from .types import GDriveFile, GDriveFolder, GDrivePermission

__all__ = ["GDriveVFS", "GDriveFile", "GDriveFolder", "GDrivePermission"]
__version__ = "0.1.0"

Provider = GDriveVFS


def get_provider_class():
    return GDriveVFS


def register(registry):
    registry.register(
        name="gdrive",
        provider_class=GDriveVFS,
        description="Google Drive files, folders, shared drives",
        required_config=["credentials_path"],
        optional_config=["cache_ttl", "export_format", "include_trashed"],
    )
