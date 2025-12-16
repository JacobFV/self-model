"""
vfs-figma - Figma Virtual Filesystem

Projects Figma files, frames, components, and styles onto a filesystem structure.

## Filesystem Structure

```
/figma/
├── .user.json                          # Current user info
│
├── teams/
│   └── {team-id}/
│       ├── .team.json
│       ├── name.txt
│       │
│       └── projects/
│           └── {project-id}/
│               ├── .project.json
│               ├── name.txt
│               └── files/
│                   └── {file-key} -> ../../../../files/{file-key}
│
├── files/
│   └── {file-key}/
│       ├── .file.json                  # File metadata
│       ├── name.txt
│       ├── last_modified.txt
│       ├── version.txt
│       ├── thumbnail.png
│       │
│       ├── pages/
│       │   └── {page-id}/              # Or {page-name}
│       │       ├── .page.json
│       │       ├── name.txt
│       │       │
│       │       └── nodes/
│       │           └── {node-id}/
│       │               ├── .node.json  # Full node data
│       │               ├── name.txt
│       │               ├── type.txt    # FRAME/GROUP/COMPONENT/etc.
│       │               ├── bounds.json # x, y, width, height
│       │               │
│       │               ├── export/     # Export node
│       │               │   ├── png/
│       │               │   │   ├── 1x.png
│       │               │   │   ├── 2x.png
│       │               │   │   └── 3x.png
│       │               │   ├── svg/
│       │               │   │   └── {name}.svg
│       │               │   └── pdf/
│       │               │       └── {name}.pdf
│       │               │
│       │               ├── styles/     # Applied styles
│       │               │   ├── fill.json
│       │               │   ├── stroke.json
│       │               │   ├── text.json
│       │               │   └── effect.json
│       │               │
│       │               └── children/   # Child nodes
│       │                   └── {child-id} -> ../../{child-id}
│       │
│       ├── components/
│       │   └── {component-id}/
│       │       ├── .component.json
│       │       ├── name.txt
│       │       ├── description.md
│       │       ├── key.txt             # Component key
│       │       └── thumbnail.png
│       │
│       ├── component_sets/             # Variants
│       │   └── {set-id}/
│       │       ├── .component_set.json
│       │       └── variants/
│       │           └── {variant-id} -> ../../components/{id}
│       │
│       ├── styles/
│       │   ├── colors/
│       │   │   └── {style-id}/
│       │   │       ├── .style.json
│       │   │       ├── name.txt
│       │   │       └── value.json      # Color value
│       │   ├── text/
│       │   │   └── {style-id}/
│       │   │       ├── .style.json
│       │   │       ├── name.txt
│       │   │       └── value.json      # Text properties
│       │   ├── effects/
│       │   │   └── {style-id}/
│       │   │       └── ...
│       │   └── grids/
│       │       └── {style-id}/
│       │           └── ...
│       │
│       ├── comments/
│       │   └── {comment-id}/
│       │       ├── .comment.json
│       │       ├── message.md
│       │       ├── author.json
│       │       ├── resolved.txt
│       │       ├── position.json       # x, y coordinates
│       │       └── replies/
│       │           └── {reply-id}.md
│       │
│       ├── versions/
│       │   └── {version-id}/
│       │       ├── .version.json
│       │       ├── label.txt
│       │       ├── description.md
│       │       └── created.txt
│       │
│       └── branches/                   # Branching (Figma Organization)
│           └── {branch-key}/
│               └── ...
│
├── images/                             # Image fills
│   └── {image-hash}.png
│
├── shared/                             # Shared with me
│   └── {file-key} -> ../files/{file-key}
│
├── recent/
│   └── {file-key} -> ../files/{file-key}
│
└── drafts/
    └── {file-key} -> ../files/{file-key}
```

## Export Interface

Reading from export paths triggers exports:
- `export/png/2x.png` - Export at 2x scale
- `export/svg/{name}.svg` - Export as SVG
- `export/pdf/{name}.pdf` - Export as PDF

Export options via extended attributes:
- `user.figma.export.scale` - Scale factor
- `user.figma.export.format` - png/jpg/svg/pdf
- `user.figma.export.constraint` - SCALE/WIDTH/HEIGHT

## Capabilities

- READ: Browse files, export assets, read comments
- WRITE: Add comments, resolve comments
- CREATE: Create comments
- DELETE: Delete own comments

Note: Figma API is read-heavy. File editing is primarily done in Figma app.

## Configuration

```python
FigmaVFS(
    access_token="...",         # Personal access token
    # Or OAuth
    oauth_token=None,
    # Options
    cache_ttl=300,
    export_scale=2,             # Default export scale
    export_format="png",        # Default export format
)
```
"""

from .provider import FigmaVFS
from .types import FigmaFile, FigmaPage, FigmaNode, FigmaComponent, FigmaStyle

__all__ = ["FigmaVFS", "FigmaFile", "FigmaPage", "FigmaNode", "FigmaComponent", "FigmaStyle"]
__version__ = "0.1.0"

Provider = FigmaVFS


def get_provider_class():
    return FigmaVFS


def register(registry):
    registry.register(
        name="figma",
        provider_class=FigmaVFS,
        description="Figma files, frames, components, styles",
        required_config=["access_token"],
        optional_config=["cache_ttl", "export_scale", "export_format"],
    )
