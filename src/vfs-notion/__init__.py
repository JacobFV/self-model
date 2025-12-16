"""
vfs-notion - Notion Virtual Filesystem

Projects Notion workspaces, pages, and databases onto a filesystem structure.

## Filesystem Structure

```
/notion/
├── {workspace}/
│   ├── .workspace.json
│   ├── pages/
│   │   └── {page-id}/
│   │       ├── .page.json              # Page metadata
│   │       ├── title.txt               # Page title (writable)
│   │       ├── icon.txt                # Page icon/emoji
│   │       ├── cover.url               # Cover image URL
│   │       ├── content.md              # Page content as markdown (writable)
│   │       ├── content.json            # Raw block structure
│   │       ├── properties/             # Page properties (if in database)
│   │       │   ├── {prop-name}.txt     # Simple properties
│   │       │   └── {prop-name}.json    # Complex properties
│   │       ├── children/               # Child pages
│   │       │   └── {child-id} -> ../../{child-id}
│   │       ├── comments/
│   │       │   ├── {comment-id}.md
│   │       │   └── new.md
│   │       └── blocks/                 # Individual blocks
│   │           └── {block-id}/
│   │               ├── .block.json
│   │               ├── content.md
│   │               └── children/
│   ├── databases/
│   │   └── {database-id}/
│   │       ├── .database.json          # Database metadata
│   │       ├── title.txt
│   │       ├── description.md
│   │       ├── schema.json             # Database schema/properties
│   │       ├── views/
│   │       │   └── {view-name}.json    # View configurations
│   │       ├── rows/
│   │       │   ├── {row-id}/           # Each row is like a page
│   │       │   │   ├── .row.json
│   │       │   │   ├── properties/
│   │       │   │   │   └── {prop}.txt
│   │       │   │   └── content.md      # Row page content
│   │       │   └── new/                # Create new row
│   │       │       └── (write properties here)
│   │       └── query/                  # Query interface
│   │           └── {filter-hash}.json  # Cached query results
│   ├── search/
│   │   └── {query}/
│   │       └── results.json
│   ├── templates/
│   │   └── {template-id}/
│   │       └── ...
│   └── shared/                         # Shared with me
│       └── {page-id} -> ../pages/{page-id}
```

## Capabilities

- READ: Browse pages, databases, read content
- WRITE: Update page content, properties
- CREATE: Create pages, database rows
- DELETE: Archive pages (soft delete)

## Configuration

```python
NotionVFS(
    token="secret_...",         # Integration token
    cache_ttl=300,
    render_markdown=True,       # Convert blocks to markdown
)
```
"""

from .provider import NotionVFS
from .types import NotionPage, NotionDatabase, NotionBlock

__all__ = ["NotionVFS", "NotionPage", "NotionDatabase", "NotionBlock"]
__version__ = "0.1.0"

Provider = NotionVFS


def get_provider_class():
    return NotionVFS


def register(registry):
    registry.register(
        name="notion",
        provider_class=NotionVFS,
        description="Notion pages, databases, blocks",
        required_config=["token"],
        optional_config=["cache_ttl", "render_markdown"],
    )
