"""
vfs-gitlab - GitLab Virtual Filesystem

Projects GitLab groups, projects, MRs, issues, and pipelines onto a filesystem structure.

## Filesystem Structure

```
/gitlab/
├── {group}/                            # Group or user namespace
│   ├── .group.json                     # Group metadata
│   ├── members/
│   │   └── {user}.json
│   ├── subgroups/
│   │   └── {subgroup} -> ../../{group}/{subgroup}
│   │
│   └── {project}/
│       ├── .project.json               # Project metadata
│       ├── README.md
│       ├── description.md
│       ├── visibility.txt              # public/internal/private
│       │
│       ├── branches/
│       │   ├── .default -> main
│       │   └── {branch}/
│       │       ├── .branch.json
│       │       ├── protected.txt       # true/false
│       │       └── {path}/             # File tree
│       │
│       ├── tags/
│       │   └── {tag}/
│       │       ├── .tag.json
│       │       └── {path}/
│       │
│       ├── commits/
│       │   ├── recent/
│       │   │   └── {sha}.json
│       │   └── {sha}/
│       │       ├── .commit.json
│       │       ├── message.txt
│       │       └── diff.patch
│       │
│       ├── merge_requests/
│       │   ├── opened/
│       │   ├── merged/
│       │   ├── closed/
│       │   └── {iid}/                  # Internal ID
│       │       ├── .mr.json            # MR metadata
│       │       ├── title.txt           # (writable)
│       │       ├── description.md      # (writable)
│       │       ├── state.txt           # opened/merged/closed
│       │       ├── source_branch.txt
│       │       ├── target_branch.txt
│       │       ├── diff.patch          # MR diff
│       │       ├── changes/
│       │       │   └── {path}.diff
│       │       ├── commits/
│       │       │   └── {sha}.json
│       │       ├── discussions/
│       │       │   └── {id}/
│       │       │       ├── .discussion.json
│       │       │       └── notes/
│       │       │           └── {note-id}.md
│       │       ├── approvals/
│       │       │   ├── .approvals.json
│       │       │   └── approved_by/
│       │       │       └── {user}.json
│       │       └── pipelines/
│       │           └── {id} -> ../../../pipelines/{id}
│       │
│       ├── issues/
│       │   ├── opened/
│       │   ├── closed/
│       │   └── {iid}/
│       │       ├── .issue.json
│       │       ├── title.txt           # (writable)
│       │       ├── description.md      # (writable)
│       │       ├── state.txt
│       │       ├── labels.json         # (writable)
│       │       ├── assignees.json      # (writable)
│       │       ├── milestone.txt
│       │       ├── weight.txt          # (writable)
│       │       ├── time_tracking.json
│       │       └── notes/
│       │           ├── {id}.md
│       │           └── new.md
│       │
│       ├── pipelines/
│       │   ├── recent/
│       │   │   └── {id}.json
│       │   └── {id}/
│       │       ├── .pipeline.json
│       │       ├── status.txt          # running/success/failed
│       │       ├── ref.txt             # Branch/tag
│       │       ├── sha.txt
│       │       ├── duration.txt
│       │       ├── variables.json
│       │       └── jobs/
│       │           └── {job-id}/
│       │               ├── .job.json
│       │               ├── name.txt
│       │               ├── stage.txt
│       │               ├── status.txt
│       │               ├── log.txt     # Job log
│       │               └── artifacts/
│       │                   └── {path}
│       │
│       ├── environments/
│       │   └── {name}/
│       │       ├── .environment.json
│       │       ├── state.txt
│       │       └── deployments/
│       │           └── {id}.json
│       │
│       ├── releases/
│       │   └── {tag}/
│       │       ├── .release.json
│       │       ├── description.md
│       │       └── assets/
│       │           └── links/
│       │               └── {name}.url
│       │
│       ├── wiki/
│       │   └── {slug}.md
│       │
│       ├── snippets/
│       │   └── {id}/
│       │       ├── .snippet.json
│       │       └── {filename}
│       │
│       ├── container_registry/
│       │   └── {name}/
│       │       └── {tag}.json
│       │
│       └── packages/
│           └── {type}/                 # npm, maven, etc.
│               └── {name}/
│                   └── {version}.json
│
├── users/
│   └── {username}/
│       ├── .user.json
│       └── projects/
│           └── {project} -> ../../{username}/{project}
│
└── explore/                            # Explore popular/trending
    ├── starred/
    ├── trending/
    └── popular/
```

## Capabilities

- READ: Browse projects, MRs, issues, pipelines
- WRITE: Update MRs, issues, add comments
- CREATE: Create MRs, issues, branches
- DELETE: Close MRs, issues

## Configuration

```python
GitLabVFS(
    url="https://gitlab.com",       # Or self-hosted URL
    token="glpat-...",              # Personal access token
    # Or OAuth
    oauth_token=None,
    # Options
    cache_ttl=300,
    include_archived=False,
)
```
"""

from .provider import GitLabVFS
from .types import GitLabProject, GitLabMR, GitLabIssue, GitLabPipeline

__all__ = ["GitLabVFS", "GitLabProject", "GitLabMR", "GitLabIssue", "GitLabPipeline"]
__version__ = "0.1.0"

Provider = GitLabVFS


def get_provider_class():
    return GitLabVFS


def register(registry):
    registry.register(
        name="gitlab",
        provider_class=GitLabVFS,
        description="GitLab projects, MRs, issues, pipelines",
        required_config=["token"],
        optional_config=["url", "cache_ttl", "include_archived"],
    )
