"""Type definitions for Jira VFS."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import json


@dataclass
class JiraIssue:
    """Represents a Jira issue."""

    id: str
    key: str  # e.g., "PROJ-123"
    summary: str
    description: str = ""
    issue_type: str = "Task"  # Bug, Story, Task, Epic, Subtask
    status: str = "Open"
    priority: str = "Medium"
    resolution: str | None = None
    project_key: str = ""
    project_name: str = ""
    assignee_id: str | None = None
    assignee_name: str | None = None
    reporter_id: str = ""
    reporter_name: str = ""
    creator_id: str = ""
    creator_name: str = ""
    labels: list[str] = field(default_factory=list)
    components: list[str] = field(default_factory=list)
    fix_versions: list[str] = field(default_factory=list)
    affects_versions: list[str] = field(default_factory=list)
    epic_key: str | None = None
    parent_key: str | None = None
    story_points: float | None = None
    time_estimate: int | None = None  # Seconds
    time_spent: int | None = None  # Seconds
    time_remaining: int | None = None  # Seconds
    url: str = ""
    created: datetime = field(default_factory=datetime.now)
    updated: datetime = field(default_factory=datetime.now)
    resolved: datetime | None = None
    due_date: datetime | None = None
    comments_count: int = 0
    attachments_count: int = 0
    subtasks_count: int = 0
    links_count: int = 0
    watchers_count: int = 0

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "key": self.key,
            "summary": self.summary,
            "description": self.description,
            "type": self.issue_type,
            "status": self.status,
            "priority": self.priority,
            "resolution": self.resolution,
            "project": {
                "key": self.project_key,
                "name": self.project_name,
            },
            "assignee": {
                "id": self.assignee_id,
                "name": self.assignee_name,
            } if self.assignee_id else None,
            "reporter": {
                "id": self.reporter_id,
                "name": self.reporter_name,
            },
            "creator": {
                "id": self.creator_id,
                "name": self.creator_name,
            },
            "labels": self.labels,
            "components": self.components,
            "fix_versions": self.fix_versions,
            "affects_versions": self.affects_versions,
            "epic_key": self.epic_key,
            "parent_key": self.parent_key,
            "story_points": self.story_points,
            "time_tracking": {
                "estimate": self.time_estimate,
                "spent": self.time_spent,
                "remaining": self.time_remaining,
            } if self.time_estimate or self.time_spent else None,
            "url": self.url,
            "created": self.created.isoformat(),
            "updated": self.updated.isoformat(),
            "resolved": self.resolved.isoformat() if self.resolved else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "comments_count": self.comments_count,
            "attachments_count": self.attachments_count,
            "subtasks_count": self.subtasks_count,
            "links_count": self.links_count,
            "watchers_count": self.watchers_count,
        }, indent=2)


@dataclass
class JiraProject:
    """Represents a Jira project."""

    id: str
    key: str  # e.g., "PROJ"
    name: str
    description: str = ""
    project_type: str = "software"  # software, service_desk, business
    style: str = "classic"  # classic, next-gen
    lead_id: str = ""
    lead_name: str = ""
    url: str = ""
    avatar_url: str = ""
    created: datetime = field(default_factory=datetime.now)
    updated: datetime = field(default_factory=datetime.now)
    archived: bool = False
    deleted: bool = False
    issue_types: list[str] = field(default_factory=list)
    components: list[str] = field(default_factory=list)
    versions: list[str] = field(default_factory=list)
    issues_count: int = 0

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "key": self.key,
            "name": self.name,
            "description": self.description,
            "project_type": self.project_type,
            "style": self.style,
            "lead": {
                "id": self.lead_id,
                "name": self.lead_name,
            },
            "url": self.url,
            "avatar_url": self.avatar_url,
            "created": self.created.isoformat(),
            "updated": self.updated.isoformat(),
            "archived": self.archived,
            "deleted": self.deleted,
            "issue_types": self.issue_types,
            "components": self.components,
            "versions": self.versions,
            "issues_count": self.issues_count,
        }, indent=2)


@dataclass
class JiraSprint:
    """Represents a Jira sprint."""

    id: int
    name: str
    state: str = "future"  # future, active, closed
    board_id: int = 0
    goal: str = ""
    start_date: datetime | None = None
    end_date: datetime | None = None
    complete_date: datetime | None = None
    created_date: datetime = field(default_factory=datetime.now)
    origin_board_id: int | None = None
    issues_count: int = 0
    completed_issues_count: int = 0
    incomplete_issues_count: int = 0
    punted_issues_count: int = 0
    velocity: float = 0.0

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "name": self.name,
            "state": self.state,
            "board_id": self.board_id,
            "goal": self.goal,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "complete_date": self.complete_date.isoformat() if self.complete_date else None,
            "created_date": self.created_date.isoformat(),
            "origin_board_id": self.origin_board_id,
            "issues_count": self.issues_count,
            "completed_issues_count": self.completed_issues_count,
            "incomplete_issues_count": self.incomplete_issues_count,
            "punted_issues_count": self.punted_issues_count,
            "velocity": self.velocity,
        }, indent=2)


@dataclass
class JiraBoard:
    """Represents a Jira board."""

    id: int
    name: str
    type: str = "scrum"  # scrum, kanban, simple
    filter_id: int | None = None
    location_project_key: str | None = None
    location_project_name: str | None = None
    url: str = ""
    created: datetime = field(default_factory=datetime.now)
    admin_count: int = 0
    columns: list[dict[str, Any]] = field(default_factory=list)
    sub_query: str | None = None

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "filter_id": self.filter_id,
            "location": {
                "project_key": self.location_project_key,
                "project_name": self.location_project_name,
            } if self.location_project_key else None,
            "url": self.url,
            "created": self.created.isoformat(),
            "admin_count": self.admin_count,
            "columns": self.columns,
            "sub_query": self.sub_query,
        }, indent=2)
