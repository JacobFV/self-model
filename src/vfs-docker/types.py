"""Type definitions for Docker VFS."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import json


@dataclass
class DockerContainer:
    """Represents a Docker container."""

    id: str
    name: str
    image: str
    status: str  # running, stopped, paused, restarting, removing, exited, created, dead
    state: str  # running, paused, restarting, exited, dead
    created: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None
    exit_code: int | None = None
    ports: dict[str, list[dict[str, str]]] = field(default_factory=dict)
    env: list[str] = field(default_factory=list)
    labels: dict[str, str] = field(default_factory=dict)
    mounts: list[dict[str, Any]] = field(default_factory=list)
    networks: dict[str, Any] = field(default_factory=dict)
    restart_policy: str = "no"

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "name": self.name,
            "image": self.image,
            "status": self.status,
            "state": self.state,
            "created": self.created.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "exit_code": self.exit_code,
            "ports": self.ports,
            "env": self.env,
            "labels": self.labels,
            "mounts": self.mounts,
            "networks": self.networks,
            "restart_policy": self.restart_policy,
        }, indent=2)


@dataclass
class DockerImage:
    """Represents a Docker image."""

    id: str
    tags: list[str]
    size: int
    created: datetime
    architecture: str = "amd64"
    os: str = "linux"
    author: str | None = None
    comment: str | None = None
    parent_id: str | None = None
    labels: dict[str, str] = field(default_factory=dict)
    config: dict[str, Any] = field(default_factory=dict)
    layers: list[str] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "tags": self.tags,
            "size": self.size,
            "created": self.created.isoformat(),
            "architecture": self.architecture,
            "os": self.os,
            "author": self.author,
            "comment": self.comment,
            "parent_id": self.parent_id,
            "labels": self.labels,
            "config": self.config,
            "layers": self.layers,
        }, indent=2)


@dataclass
class DockerVolume:
    """Represents a Docker volume."""

    name: str
    driver: str
    mountpoint: str
    created: datetime
    scope: str = "local"
    labels: dict[str, str] = field(default_factory=dict)
    options: dict[str, str] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps({
            "name": self.name,
            "driver": self.driver,
            "mountpoint": self.mountpoint,
            "created": self.created.isoformat(),
            "scope": self.scope,
            "labels": self.labels,
            "options": self.options,
        }, indent=2)


@dataclass
class DockerNetwork:
    """Represents a Docker network."""

    id: str
    name: str
    driver: str
    scope: str  # local, swarm, global
    created: datetime
    internal: bool = False
    attachable: bool = True
    ingress: bool = False
    ipam: dict[str, Any] = field(default_factory=dict)
    containers: dict[str, Any] = field(default_factory=dict)
    labels: dict[str, str] = field(default_factory=dict)
    options: dict[str, str] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "name": self.name,
            "driver": self.driver,
            "scope": self.scope,
            "created": self.created.isoformat(),
            "internal": self.internal,
            "attachable": self.attachable,
            "ingress": self.ingress,
            "ipam": self.ipam,
            "containers": self.containers,
            "labels": self.labels,
            "options": self.options,
        }, indent=2)
