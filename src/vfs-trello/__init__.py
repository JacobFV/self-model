"""
vfs-trello - Trello Virtual Filesystem

Projects Trello boards, lists, cards, and checklists onto a filesystem structure.

## Filesystem Structure

```
/trello/
├── .member.json                        # Current user info
│
├── boards/
│   └── {board-id}/                     # Or {board-name} if unique
│       ├── .board.json                 # Board metadata
│       ├── name.txt                    # (writable)
│       ├── description.md              # (writable)
│       ├── url.txt
│       ├── closed.txt                  # true/false
│       ├── starred.txt
│       │
│       ├── lists/
│       │   └── {list-id}/              # Or {list-name}
│       │       ├── .list.json
│       │       ├── name.txt            # (writable)
│       │       ├── position.txt
│       │       ├── closed.txt
│       │       │
│       │       └── cards/
│       │           ├── {card-id}/      # Or {card-name}
│       │           │   └── ... (see cards/ structure)
│       │           └── new.json        # Write to create card
│       │
│       ├── cards/                      # All cards (flat)
│       │   └── {card-id}/
│       │       ├── .card.json          # Full card data
│       │       ├── name.txt            # (writable)
│       │       ├── description.md      # (writable)
│       │       ├── url.txt
│       │       ├── position.txt
│       │       ├── due.txt             # Due date (writable)
│       │       ├── due_complete.txt    # true/false (writable)
│       │       ├── closed.txt
│       │       ├── list.txt            # Current list name
│       │       │
│       │       ├── labels/
│       │       │   └── {color}.txt     # Label names
│       │       │
│       │       ├── members/
│       │       │   └── {member-id}.json
│       │       │
│       │       ├── checklists/
│       │       │   └── {checklist-id}/
│       │       │       ├── .checklist.json
│       │       │       ├── name.txt
│       │       │       └── items/
│       │       │           └── {item-id}/
│       │       │               ├── name.txt
│       │       │               └── complete.txt
│       │       │
│       │       ├── attachments/
│       │       │   └── {attachment-id}/
│       │       │       ├── .attachment.json
│       │       │       └── {filename}
│       │       │
│       │       ├── comments/
│       │       │   ├── {action-id}.md
│       │       │   └── new.md          # Write to add comment
│       │       │
│       │       ├── custom_fields/
│       │       │   └── {field-name}.txt
│       │       │
│       │       └── history/
│       │           └── {action-id}.json
│       │
│       ├── labels/
│       │   └── {label-id}/
│       │       ├── .label.json
│       │       ├── name.txt
│       │       └── color.txt
│       │
│       ├── members/
│       │   └── {member-id}/
│       │       ├── .member.json
│       │       └── type.txt            # admin/normal/observer
│       │
│       ├── custom_fields/
│       │   └── {field-id}/
│       │       ├── .field.json
│       │       ├── name.txt
│       │       └── type.txt
│       │
│       ├── power_ups/
│       │   └── {power-up-id}.json
│       │
│       └── activity/                   # Recent activity
│           └── {action-id}.json
│
├── organizations/                      # Workspaces
│   └── {org-id}/
│       ├── .organization.json
│       ├── name.txt
│       ├── description.md
│       ├── members/
│       │   └── {member-id}.json
│       └── boards/
│           └── {board-id} -> ../../boards/{board-id}
│
├── starred/                            # Starred boards
│   └── {board-id} -> ../boards/{board-id}
│
├── recent/                             # Recently viewed
│   └── {board-id} -> ../boards/{board-id}
│
└── templates/
    └── {template-id}/
        ├── .template.json
        └── ...
```

## Capabilities

- READ: Browse boards, lists, cards
- WRITE: Update cards, add comments, check items
- CREATE: Create cards, lists, checklists
- DELETE: Archive cards, delete checklists

## Configuration

```python
TrelloVFS(
    api_key="...",              # Trello API key
    token="...",                # User token
    # Options
    cache_ttl=300,
    include_closed=False,       # Include archived items
)
```
"""

from .provider import TrelloVFS
from .types import TrelloBoard, TrelloList, TrelloCard, TrelloChecklist

__all__ = ["TrelloVFS", "TrelloBoard", "TrelloList", "TrelloCard", "TrelloChecklist"]
__version__ = "0.1.0"

Provider = TrelloVFS


def get_provider_class():
    return TrelloVFS


def register(registry):
    registry.register(
        name="trello",
        provider_class=TrelloVFS,
        description="Trello boards, lists, cards, checklists",
        required_config=["api_key", "token"],
        optional_config=["cache_ttl", "include_closed"],
    )
