"""
vfs-linear - Linear Virtual Filesystem

Projects Linear workspaces, teams, issues, and projects onto a filesystem structure.

## Filesystem Structure

```
/linear/
├── {workspace}/
│   ├── .workspace.json
│   ├── me/                             # Current user
│   │   ├── .user.json
│   │   ├── assigned/                   # Issues assigned to me
│   │   │   └── {issue-id} -> ../../teams/{team}/issues/{id}
│   │   ├── created/                    # Issues I created
│   │   └── watching/                   # Issues I'm watching
│   ├── teams/
│   │   └── {team-key}/                 # e.g., "ENG", "PROD"
│   │       ├── .team.json
│   │       ├── members.json
│   │       ├── labels/
│   │       │   └── {label}.json
│   │       ├── states/                 # Workflow states
│   │       │   └── {state}.json
│   │       └── issues/
│   │           ├── by-state/
│   │           │   ├── backlog/
│   │           │   ├── todo/
│   │           │   ├── in-progress/
│   │           │   └── done/
│   │           └── {issue-id}/         # e.g., "ENG-123"
│   │               ├── .issue.json     # Full issue data
│   │               ├── title.txt       # (writable)
│   │               ├── description.md  # (writable)
│   │               ├── state.txt       # Current state (writable)
│   │               ├── priority.txt    # 0-4 (writable)
│   │               ├── estimate.txt    # Story points (writable)
│   │               ├── labels.json     # (writable)
│   │               ├── assignee.txt    # (writable)
│   │               ├── parent.txt      # Parent issue ID
│   │               ├── children/       # Sub-issues
│   │               │   └── {id} -> ../../{id}
│   │               ├── comments/
│   │               │   ├── {id}.md
│   │               │   └── new.md      # Write to comment
│   │               ├── attachments/
│   │               │   └── {filename}
│   │               └── history/
│   │                   └── {timestamp}.json
│   ├── projects/
│   │   └── {project-slug}/
│   │       ├── .project.json
│   │       ├── description.md
│   │       ├── status.txt              # backlog/planned/started/completed
│   │       ├── progress.json           # Completion stats
│   │       ├── milestones/
│   │       │   └── {milestone}/
│   │       │       ├── .milestone.json
│   │       │       └── issues/
│   │       └── issues/                 # Issues in this project
│   │           └── {id} -> ../../teams/{team}/issues/{id}
│   ├── cycles/
│   │   ├── current -> {number}
│   │   └── {number}/
│   │       ├── .cycle.json
│   │       ├── progress.json
│   │       └── issues/
│   ├── roadmaps/
│   │   └── {roadmap-slug}/
│   │       ├── .roadmap.json
│   │       └── projects/
│   │           └── {project} -> ../../projects/{project}
│   ├── views/                          # Custom views/filters
│   │   └── {view-name}/
│   │       ├── .view.json
│   │       └── issues/
│   └── integrations/
│       └── {integration}.json
```

## Capabilities

- READ: Browse issues, projects, cycles
- WRITE: Update issue fields, add comments
- CREATE: Create issues (write to teams/{team}/issues/new/)

## Configuration

```python
LinearVFS(
    api_key="lin_api_...",
    cache_ttl=300,
    workspace_id=None,          # Auto-detect if not specified
)
```
"""

from .provider import LinearVFS
from .types import LinearIssue, LinearProject, LinearCycle, LinearTeam

__all__ = ["LinearVFS", "LinearIssue", "LinearProject", "LinearCycle", "LinearTeam"]
__version__ = "0.1.0"

Provider = LinearVFS


def get_provider_class():
    return LinearVFS


def register(registry):
    registry.register(
        name="linear",
        provider_class=LinearVFS,
        description="Linear issues, projects, cycles, roadmaps",
        required_config=["api_key"],
        optional_config=["workspace_id", "cache_ttl"],
    )
