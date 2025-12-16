"""Type definitions for GitLab VFS."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import json


@dataclass
class GitLabProject:
    """Represents a GitLab project."""

    project_id: int
    name: str
    path: str
    path_with_namespace: str
    namespace: str
    description: str = ""
    default_branch: str = "main"
    visibility: str = "private"  # public, internal, private
    archived: bool = False
    web_url: str = ""
    http_url: str = ""
    ssh_url: str = ""
    star_count: int = 0
    forks_count: int = 0
    open_issues_count: int = 0
    avatar_url: str = ""
    topics: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity_at: datetime = field(default_factory=datetime.now)

    def to_json(self) -> str:
        return json.dumps({
            "id": self.project_id,
            "name": self.name,
            "path": self.path,
            "path_with_namespace": self.path_with_namespace,
            "namespace": self.namespace,
            "description": self.description,
            "default_branch": self.default_branch,
            "visibility": self.visibility,
            "archived": self.archived,
            "web_url": self.web_url,
            "http_url_to_repo": self.http_url,
            "ssh_url_to_repo": self.ssh_url,
            "star_count": self.star_count,
            "forks_count": self.forks_count,
            "open_issues_count": self.open_issues_count,
            "topics": self.topics,
            "created_at": self.created_at.isoformat(),
            "last_activity_at": self.last_activity_at.isoformat(),
        }, indent=2)


@dataclass
class GitLabMR:
    """Represents a GitLab merge request."""

    iid: int  # Internal ID
    mr_id: int  # Global ID
    title: str
    description: str
    state: str  # opened, merged, closed
    author: str
    source_branch: str
    target_branch: str
    source_project_id: int
    target_project_id: int
    draft: bool = False
    work_in_progress: bool = False
    merged: bool = False
    merged_by: str | None = None
    merge_commit_sha: str | None = None
    squash: bool = False
    labels: list[str] = field(default_factory=list)
    assignees: list[str] = field(default_factory=list)
    reviewers: list[str] = field(default_factory=list)
    milestone: str | None = None
    has_conflicts: bool = False
    blocking_discussions_resolved: bool = True
    user_notes_count: int = 0
    upvotes: int = 0
    downvotes: int = 0
    changes_count: str = "0"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    merged_at: datetime | None = None
    web_url: str = ""

    def to_json(self) -> str:
        return json.dumps({
            "iid": self.iid,
            "id": self.mr_id,
            "title": self.title,
            "description": self.description,
            "state": self.state,
            "author": self.author,
            "source_branch": self.source_branch,
            "target_branch": self.target_branch,
            "draft": self.draft,
            "work_in_progress": self.work_in_progress,
            "merged": self.merged,
            "merged_by": self.merged_by,
            "merge_commit_sha": self.merge_commit_sha,
            "squash": self.squash,
            "labels": self.labels,
            "assignees": self.assignees,
            "reviewers": self.reviewers,
            "milestone": self.milestone,
            "has_conflicts": self.has_conflicts,
            "blocking_discussions_resolved": self.blocking_discussions_resolved,
            "user_notes_count": self.user_notes_count,
            "upvotes": self.upvotes,
            "downvotes": self.downvotes,
            "changes_count": self.changes_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "merged_at": self.merged_at.isoformat() if self.merged_at else None,
            "web_url": self.web_url,
        }, indent=2)


@dataclass
class GitLabIssue:
    """Represents a GitLab issue."""

    iid: int  # Internal ID
    issue_id: int  # Global ID
    title: str
    description: str
    state: str  # opened, closed
    author: str
    labels: list[str] = field(default_factory=list)
    assignees: list[str] = field(default_factory=list)
    milestone: str | None = None
    weight: int | None = None
    due_date: str | None = None
    time_stats: dict[str, Any] = field(default_factory=dict)
    user_notes_count: int = 0
    upvotes: int = 0
    downvotes: int = 0
    confidential: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    closed_at: datetime | None = None
    web_url: str = ""

    def to_json(self) -> str:
        return json.dumps({
            "iid": self.iid,
            "id": self.issue_id,
            "title": self.title,
            "description": self.description,
            "state": self.state,
            "author": self.author,
            "labels": self.labels,
            "assignees": self.assignees,
            "milestone": self.milestone,
            "weight": self.weight,
            "due_date": self.due_date,
            "time_stats": self.time_stats,
            "user_notes_count": self.user_notes_count,
            "upvotes": self.upvotes,
            "downvotes": self.downvotes,
            "confidential": self.confidential,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
            "web_url": self.web_url,
        }, indent=2)


@dataclass
class GitLabPipeline:
    """Represents a GitLab CI/CD pipeline."""

    pipeline_id: int
    project_id: int
    status: str  # created, waiting_for_resource, preparing, pending, running, success, failed, canceled, skipped
    ref: str  # branch or tag
    sha: str
    source: str  # push, web, trigger, schedule, api, pipeline, etc.
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    started_at: datetime | None = None
    finished_at: datetime | None = None
    duration: int | None = None  # seconds
    queued_duration: int | None = None  # seconds
    web_url: str = ""
    user: str = ""

    def to_json(self) -> str:
        return json.dumps({
            "id": self.pipeline_id,
            "project_id": self.project_id,
            "status": self.status,
            "ref": self.ref,
            "sha": self.sha,
            "source": self.source,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "duration": self.duration,
            "queued_duration": self.queued_duration,
            "web_url": self.web_url,
            "user": self.user,
        }, indent=2)


@dataclass
class GitLabJob:
    """Represents a GitLab CI/CD job."""

    job_id: int
    name: str
    stage: str
    status: str  # created, pending, running, success, failed, canceled, skipped
    ref: str
    pipeline_id: int
    created_at: datetime = field(default_factory=datetime.now)
    started_at: datetime | None = None
    finished_at: datetime | None = None
    duration: float | None = None
    queued_duration: float | None = None
    web_url: str = ""
    user: str = ""

    def to_json(self) -> str:
        return json.dumps({
            "id": self.job_id,
            "name": self.name,
            "stage": self.stage,
            "status": self.status,
            "ref": self.ref,
            "pipeline": {"id": self.pipeline_id},
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "duration": self.duration,
            "queued_duration": self.queued_duration,
            "web_url": self.web_url,
            "user": self.user,
        }, indent=2)
