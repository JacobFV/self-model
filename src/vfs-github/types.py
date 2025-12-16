"""Type definitions for GitHub VFS."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import json


@dataclass
class GitHubRepo:
    """Represents a GitHub repository."""

    id: int
    name: str
    full_name: str
    owner: str
    description: str = ""
    default_branch: str = "main"
    private: bool = False
    fork: bool = False
    archived: bool = False
    url: str = ""
    clone_url: str = ""
    ssh_url: str = ""
    stargazers_count: int = 0
    forks_count: int = 0
    open_issues_count: int = 0
    language: str | None = None
    topics: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "name": self.name,
            "full_name": self.full_name,
            "owner": self.owner,
            "description": self.description,
            "default_branch": self.default_branch,
            "private": self.private,
            "fork": self.fork,
            "archived": self.archived,
            "url": self.url,
            "clone_url": self.clone_url,
            "stargazers_count": self.stargazers_count,
            "forks_count": self.forks_count,
            "open_issues_count": self.open_issues_count,
            "language": self.language,
            "topics": self.topics,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }, indent=2)


@dataclass
class GitHubBranch:
    """Represents a GitHub branch."""

    name: str
    sha: str
    protected: bool = False
    protection_url: str | None = None

    def to_json(self) -> str:
        return json.dumps({
            "name": self.name,
            "sha": self.sha,
            "protected": self.protected,
        }, indent=2)


@dataclass
class GitHubCommit:
    """Represents a GitHub commit."""

    sha: str
    message: str
    author_name: str
    author_email: str
    author_date: datetime
    committer_name: str
    committer_email: str
    committer_date: datetime
    parents: list[str] = field(default_factory=list)
    url: str = ""

    def to_json(self) -> str:
        return json.dumps({
            "sha": self.sha,
            "message": self.message,
            "author": {
                "name": self.author_name,
                "email": self.author_email,
                "date": self.author_date.isoformat(),
            },
            "committer": {
                "name": self.committer_name,
                "email": self.committer_email,
                "date": self.committer_date.isoformat(),
            },
            "parents": self.parents,
            "url": self.url,
        }, indent=2)


@dataclass
class GitHubIssue:
    """Represents a GitHub issue."""

    number: int
    title: str
    body: str
    state: str  # open, closed
    user: str
    labels: list[str] = field(default_factory=list)
    assignees: list[str] = field(default_factory=list)
    milestone: str | None = None
    comments_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    closed_at: datetime | None = None
    url: str = ""

    def to_json(self) -> str:
        return json.dumps({
            "number": self.number,
            "title": self.title,
            "body": self.body,
            "state": self.state,
            "user": self.user,
            "labels": self.labels,
            "assignees": self.assignees,
            "milestone": self.milestone,
            "comments": self.comments_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
            "url": self.url,
        }, indent=2)


@dataclass
class GitHubPR:
    """Represents a GitHub pull request."""

    number: int
    title: str
    body: str
    state: str  # open, closed, merged
    user: str
    head_ref: str
    base_ref: str
    head_sha: str
    base_sha: str
    draft: bool = False
    mergeable: bool | None = None
    merged: bool = False
    merged_by: str | None = None
    labels: list[str] = field(default_factory=list)
    assignees: list[str] = field(default_factory=list)
    reviewers: list[str] = field(default_factory=list)
    additions: int = 0
    deletions: int = 0
    changed_files: int = 0
    comments_count: int = 0
    review_comments_count: int = 0
    commits_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    merged_at: datetime | None = None
    url: str = ""

    def to_json(self) -> str:
        return json.dumps({
            "number": self.number,
            "title": self.title,
            "body": self.body,
            "state": self.state,
            "user": self.user,
            "head": {"ref": self.head_ref, "sha": self.head_sha},
            "base": {"ref": self.base_ref, "sha": self.base_sha},
            "draft": self.draft,
            "mergeable": self.mergeable,
            "merged": self.merged,
            "merged_by": self.merged_by,
            "labels": self.labels,
            "assignees": self.assignees,
            "reviewers": self.reviewers,
            "additions": self.additions,
            "deletions": self.deletions,
            "changed_files": self.changed_files,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "merged_at": self.merged_at.isoformat() if self.merged_at else None,
            "url": self.url,
        }, indent=2)
