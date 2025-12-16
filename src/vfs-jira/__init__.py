"""
vfs-jira - Jira Virtual Filesystem

Projects Jira projects, issues, sprints, and boards onto a filesystem structure.

## Filesystem Structure

```
/jira/
├── {project-key}/                      # e.g., "PROJ", "ENG"
│   ├── .project.json                   # Project metadata
│   ├── description.md
│   ├── lead.json                       # Project lead
│   ├── components/
│   │   └── {component}/
│   │       ├── .component.json
│   │       └── issues/                 # Issues with this component
│   ├── versions/                       # Fix versions
│   │   └── {version}/
│   │       ├── .version.json
│   │       ├── released.txt            # true/false
│   │       └── issues/
│   ├── epics/
│   │   └── {epic-key}/                 # e.g., "PROJ-100"
│   │       ├── .epic.json
│   │       ├── summary.txt
│   │       ├── description.md
│   │       └── stories/                # Child issues
│   │           └── {key} -> ../../issues/{key}
│   ├── issues/
│   │   ├── by-type/
│   │   │   ├── bug/
│   │   │   ├── story/
│   │   │   ├── task/
│   │   │   └── epic/
│   │   ├── by-status/
│   │   │   ├── open/
│   │   │   ├── in-progress/
│   │   │   ├── resolved/
│   │   │   └── closed/
│   │   └── {issue-key}/                # e.g., "PROJ-123"
│   │       ├── .issue.json             # Full issue data
│   │       ├── summary.txt             # (writable)
│   │       ├── description.md          # (writable)
│   │       ├── type.txt                # Issue type
│   │       ├── status.txt              # Current status
│   │       ├── priority.txt            # (writable)
│   │       ├── assignee.txt            # (writable)
│   │       ├── reporter.txt
│   │       ├── labels.json             # (writable)
│   │       ├── components.json         # (writable)
│   │       ├── fix-versions.json       # (writable)
│   │       ├── story-points.txt        # (writable)
│   │       ├── time-tracking.json
│   │       ├── parent.txt              # Parent issue (for subtasks)
│   │       ├── subtasks/
│   │       │   └── {key} -> ../../{key}
│   │       ├── links/                  # Issue links
│   │       │   └── {link-type}/
│   │       │       └── {key} -> ../../../{key}
│   │       ├── comments/
│   │       │   ├── {id}.md
│   │       │   └── new.md
│   │       ├── attachments/
│   │       │   └── {filename}
│   │       ├── worklogs/
│   │       │   └── {id}.json
│   │       └── history/
│   │           └── {timestamp}.json
│   ├── sprints/
│   │   ├── active/                     # Current sprint
│   │   │   └── ... -> ../{sprint-id}
│   │   └── {sprint-id}/
│   │       ├── .sprint.json
│   │       ├── goal.txt
│   │       ├── dates.json              # start/end dates
│   │       ├── velocity.json
│   │       └── issues/
│   │           └── {key} -> ../../issues/{key}
│   └── boards/
│       └── {board-id}/
│           ├── .board.json
│           ├── type.txt                # scrum/kanban
│           ├── columns/
│           │   └── {column}/
│           │       └── issues/
│           └── backlog/
│               └── issues/
├── filters/
│   └── {filter-id}/
│       ├── .filter.json
│       ├── jql.txt
│       └── results/
│           └── {key} -> ../../{project}/issues/{key}
└── users/
    └── {account-id}.json
```

## Capabilities

- READ: Browse projects, issues, sprints
- WRITE: Update issue fields, add comments, log work
- CREATE: Create issues
- DELETE: Close/delete issues

## Configuration

```python
JiraVFS(
    url="https://your-domain.atlassian.net",
    email="user@example.com",
    api_token="...",
    cache_ttl=300,
)
```
"""

from .provider import JiraVFS
from .types import JiraIssue, JiraProject, JiraSprint, JiraBoard

__all__ = ["JiraVFS", "JiraIssue", "JiraProject", "JiraSprint", "JiraBoard"]
__version__ = "0.1.0"

Provider = JiraVFS


def get_provider_class():
    return JiraVFS


def register(registry):
    registry.register(
        name="jira",
        provider_class=JiraVFS,
        description="Jira projects, issues, sprints, boards",
        required_config=["url", "email", "api_token"],
        optional_config=["cache_ttl"],
    )
