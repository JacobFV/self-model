"""Type definitions for Linear VFS."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import json


@dataclass
class LinearIssue:
    """Represents a Linear issue."""

    id: str
    identifier: str  # e.g., "ENG-123"
    title: str
    description: str = ""
    state: str = "backlog"
    priority: int = 0  # 0-4: none, urgent, high, medium, low
    estimate: float | None = None  # Story points
    team_id: str = ""
    team_key: str = ""
    project_id: str | None = None
    cycle_id: str | None = None
    parent_id: str | None = None
    assignee_id: str | None = None
    assignee_name: str | None = None
    creator_id: str = ""
    creator_name: str = ""
    labels: list[str] = field(default_factory=list)
    url: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None
    canceled_at: datetime | None = None
    started_at: datetime | None = None
    due_date: datetime | None = None
    children_count: int = 0
    comments_count: int = 0
    attachments_count: int = 0

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "identifier": self.identifier,
            "title": self.title,
            "description": self.description,
            "state": self.state,
            "priority": self.priority,
            "estimate": self.estimate,
            "team": {
                "id": self.team_id,
                "key": self.team_key,
            },
            "project_id": self.project_id,
            "cycle_id": self.cycle_id,
            "parent_id": self.parent_id,
            "assignee": {
                "id": self.assignee_id,
                "name": self.assignee_name,
            } if self.assignee_id else None,
            "creator": {
                "id": self.creator_id,
                "name": self.creator_name,
            },
            "labels": self.labels,
            "url": self.url,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "canceled_at": self.canceled_at.isoformat() if self.canceled_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "children_count": self.children_count,
            "comments_count": self.comments_count,
            "attachments_count": self.attachments_count,
        }, indent=2)


@dataclass
class LinearProject:
    """Represents a Linear project."""

    id: str
    name: str
    slug: str
    description: str = ""
    state: str = "planned"  # backlog, planned, started, paused, completed, canceled
    status_label: str = ""
    progress: float = 0.0  # 0.0-1.0
    team_ids: list[str] = field(default_factory=list)
    lead_id: str | None = None
    lead_name: str | None = None
    milestone_id: str | None = None
    url: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    canceled_at: datetime | None = None
    target_date: datetime | None = None
    issues_count: int = 0
    completed_issues_count: int = 0

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "state": self.state,
            "status_label": self.status_label,
            "progress": self.progress,
            "team_ids": self.team_ids,
            "lead": {
                "id": self.lead_id,
                "name": self.lead_name,
            } if self.lead_id else None,
            "milestone_id": self.milestone_id,
            "url": self.url,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "canceled_at": self.canceled_at.isoformat() if self.canceled_at else None,
            "target_date": self.target_date.isoformat() if self.target_date else None,
            "issues_count": self.issues_count,
            "completed_issues_count": self.completed_issues_count,
        }, indent=2)


@dataclass
class LinearCycle:
    """Represents a Linear cycle/sprint."""

    id: str
    number: int
    name: str
    team_id: str
    team_key: str
    start_date: datetime
    end_date: datetime
    description: str = ""
    url: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None
    auto_archived_at: datetime | None = None
    issues_count: int = 0
    completed_issues_count: int = 0
    in_progress_issues_count: int = 0
    scope_history: list[int] = field(default_factory=list)
    progress: float = 0.0

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "number": self.number,
            "name": self.name,
            "team": {
                "id": self.team_id,
                "key": self.team_key,
            },
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "description": self.description,
            "url": self.url,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "auto_archived_at": self.auto_archived_at.isoformat() if self.auto_archived_at else None,
            "issues_count": self.issues_count,
            "completed_issues_count": self.completed_issues_count,
            "in_progress_issues_count": self.in_progress_issues_count,
            "scope_history": self.scope_history,
            "progress": self.progress,
        }, indent=2)


@dataclass
class LinearTeam:
    """Represents a Linear team."""

    id: str
    key: str  # e.g., "ENG", "PROD"
    name: str
    description: str = ""
    icon: str = ""
    color: str = ""
    private: bool = False
    timezone: str = "UTC"
    url: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    issues_count: int = 0
    members_count: int = 0
    cycles_enabled: bool = True
    estimation_type: str = "notUsed"  # notUsed, exponential, fibonacci, linear, tShirt

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "key": self.key,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "color": self.color,
            "private": self.private,
            "timezone": self.timezone,
            "url": self.url,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "issues_count": self.issues_count,
            "members_count": self.members_count,
            "cycles_enabled": self.cycles_enabled,
            "estimation_type": self.estimation_type,
        }, indent=2)
