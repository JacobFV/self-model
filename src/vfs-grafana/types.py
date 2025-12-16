"""Type definitions for Grafana VFS."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import json


@dataclass
class GrafanaDashboard:
    """Represents a Grafana dashboard."""

    uid: str
    title: str
    url: str = ""
    description: str = ""
    tags: list[str] = field(default_factory=list)
    folder_uid: str | None = None
    folder_title: str | None = None
    version: int = 1
    created: datetime = field(default_factory=datetime.now)
    updated: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    updated_by: str = ""
    is_starred: bool = False

    def to_json(self) -> str:
        return json.dumps({
            "uid": self.uid,
            "title": self.title,
            "url": self.url,
            "description": self.description,
            "tags": self.tags,
            "folderUid": self.folder_uid,
            "folderTitle": self.folder_title,
            "version": self.version,
            "created": self.created.isoformat(),
            "updated": self.updated.isoformat(),
            "createdBy": self.created_by,
            "updatedBy": self.updated_by,
            "isStarred": self.is_starred,
        }, indent=2)


@dataclass
class GrafanaPanel:
    """Represents a Grafana dashboard panel."""

    panel_id: int
    title: str
    panel_type: str  # graph, stat, table, timeseries, etc.
    datasource: str | None = None
    targets: list[dict[str, Any]] = field(default_factory=list)
    grid_pos: dict[str, int] = field(default_factory=dict)
    options: dict[str, Any] = field(default_factory=dict)
    field_config: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps({
            "id": self.panel_id,
            "title": self.title,
            "type": self.panel_type,
            "datasource": self.datasource,
            "targets": self.targets,
            "gridPos": self.grid_pos,
            "options": self.options,
            "fieldConfig": self.field_config,
        }, indent=2)


@dataclass
class GrafanaDatasource:
    """Represents a Grafana datasource."""

    uid: str
    name: str
    datasource_type: str  # prometheus, elasticsearch, loki, etc.
    url: str
    access: str = "proxy"  # proxy or direct
    is_default: bool = False
    basic_auth: bool = False
    with_credentials: bool = False
    json_data: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps({
            "uid": self.uid,
            "name": self.name,
            "type": self.datasource_type,
            "url": self.url,
            "access": self.access,
            "isDefault": self.is_default,
            "basicAuth": self.basic_auth,
            "withCredentials": self.with_credentials,
            "jsonData": self.json_data,
        }, indent=2)


@dataclass
class GrafanaAlert:
    """Represents a Grafana alert rule."""

    uid: str
    title: str
    folder_uid: str
    condition: dict[str, Any]
    data: list[dict[str, Any]] = field(default_factory=list)
    no_data_state: str = "NoData"  # NoData, Alerting, OK
    exec_err_state: str = "Alerting"  # Alerting, OK
    for_duration: str = "5m"
    annotations: dict[str, str] = field(default_factory=dict)
    labels: dict[str, str] = field(default_factory=dict)
    is_paused: bool = False

    def to_json(self) -> str:
        return json.dumps({
            "uid": self.uid,
            "title": self.title,
            "folderUid": self.folder_uid,
            "condition": self.condition,
            "data": self.data,
            "noDataState": self.no_data_state,
            "execErrState": self.exec_err_state,
            "for": self.for_duration,
            "annotations": self.annotations,
            "labels": self.labels,
            "isPaused": self.is_paused,
        }, indent=2)


@dataclass
class GrafanaFolder:
    """Represents a Grafana folder."""

    uid: str
    title: str
    url: str = ""
    created: datetime = field(default_factory=datetime.now)
    updated: datetime = field(default_factory=datetime.now)

    def to_json(self) -> str:
        return json.dumps({
            "uid": self.uid,
            "title": self.title,
            "url": self.url,
            "created": self.created.isoformat(),
            "updated": self.updated.isoformat(),
        }, indent=2)
