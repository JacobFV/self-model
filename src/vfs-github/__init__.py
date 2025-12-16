"""
vfs-github - GitHub Virtual Filesystem

Projects GitHub repositories, branches, issues, and PRs onto a filesystem structure.

## Filesystem Structure

```
/github/
├── {owner}/
│   └── {repo}/
│       ├── .repo.json                  # Repository metadata
│       ├── README.md                   # Repo readme (if exists)
│       ├── branches/
│       │   ├── .default -> main        # Symlink to default branch
│       │   └── {branch}/
│       │       ├── .branch.json        # Branch metadata (sha, protection)
│       │       └── {path}/             # Full file tree from branch
│       │           ├── {file}          # File contents
│       │           └── {dir}/
│       ├── tags/
│       │   └── {tag}/
│       │       └── {path}/             # File tree at tag
│       ├── commits/
│       │   ├── recent/                 # Recent commits
│       │   │   └── {sha}.json
│       │   └── {sha}/
│       │       ├── .commit.json        # Commit metadata
│       │       ├── message.txt         # Commit message
│       │       └── diff.patch          # Commit diff
│       ├── issues/
│       │   ├── open/                   # Symlinks to open issues
│       │   ├── closed/                 # Symlinks to closed issues
│       │   └── {number}/
│       │       ├── .issue.json         # Issue metadata
│       │       ├── title.txt           # Issue title (writable)
│       │       ├── body.md             # Issue body (writable)
│       │       ├── labels.json         # Labels (writable)
│       │       ├── assignees.json      # Assignees (writable)
│       │       └── comments/
│       │           ├── {id}.md         # Comment content
│       │           └── new.md          # Write to add comment
│       ├── pulls/
│       │   ├── open/
│       │   ├── merged/
│       │   ├── closed/
│       │   └── {number}/
│       │       ├── .pr.json            # PR metadata
│       │       ├── title.txt
│       │       ├── body.md
│       │       ├── diff.patch          # PR diff
│       │       ├── commits/
│       │       │   └── {sha}.json
│       │       ├── files/              # Changed files
│       │       │   └── {path}.diff
│       │       ├── reviews/
│       │       │   └── {id}.json
│       │       └── comments/
│       │           └── {id}.md
│       ├── releases/
│       │   ├── latest -> {tag}         # Symlink to latest
│       │   └── {tag}/
│       │       ├── .release.json
│       │       ├── notes.md            # Release notes
│       │       └── assets/
│       │           └── {filename}      # Release assets
│       ├── actions/
│       │   ├── workflows/
│       │   │   └── {name}.yml
│       │   └── runs/
│       │       └── {id}/
│       │           ├── .run.json
│       │           └── jobs/
│       │               └── {job-id}/
│       │                   ├── .job.json
│       │                   └── log.txt
│       ├── discussions/
│       │   └── {number}/
│       │       ├── .discussion.json
│       │       ├── body.md
│       │       └── comments/
│       └── wiki/
│           └── {page-slug}.md
```

## Capabilities

- READ: Browse repos, read code, view issues/PRs
- WRITE: Update issues, PR descriptions, create comments
- CREATE: Create issues, branches, releases
- DELETE: Close issues (soft delete)

## Configuration

```python
GitHubVFS(
    token="ghp_...",            # Personal access token
    base_url=None,              # For GitHub Enterprise
    cache_ttl=300,
    include_forks=True,
    include_archived=False,
)
```
"""

from .provider import GitHubVFS
from .types import GitHubRepo, GitHubIssue, GitHubPR, GitHubCommit, GitHubBranch

__all__ = ["GitHubVFS", "GitHubRepo", "GitHubIssue", "GitHubPR", "GitHubCommit", "GitHubBranch"]
__version__ = "0.1.0"

Provider = GitHubVFS


def get_provider_class():
    return GitHubVFS


def register(registry):
    registry.register(
        name="github",
        provider_class=GitHubVFS,
        description="GitHub repos, branches, issues, PRs, actions",
        required_config=["token"],
        optional_config=["base_url", "cache_ttl", "include_forks"],
    )
