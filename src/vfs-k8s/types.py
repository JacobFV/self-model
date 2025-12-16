"""Type definitions for Kubernetes VFS."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import json


@dataclass
class K8sPod:
    """Represents a Kubernetes pod."""

    name: str
    namespace: str
    uid: str
    phase: str  # Pending, Running, Succeeded, Failed, Unknown
    node_name: str | None = None
    created: datetime = field(default_factory=datetime.now)
    started_at: datetime | None = None
    ip: str | None = None
    labels: dict[str, str] = field(default_factory=dict)
    annotations: dict[str, str] = field(default_factory=dict)
    containers: list[dict[str, Any]] = field(default_factory=list)
    init_containers: list[dict[str, Any]] = field(default_factory=list)
    conditions: list[dict[str, Any]] = field(default_factory=list)
    owner_references: list[dict[str, Any]] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps({
            "name": self.name,
            "namespace": self.namespace,
            "uid": self.uid,
            "phase": self.phase,
            "node_name": self.node_name,
            "created": self.created.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ip": self.ip,
            "labels": self.labels,
            "annotations": self.annotations,
            "containers": self.containers,
            "init_containers": self.init_containers,
            "conditions": self.conditions,
            "owner_references": self.owner_references,
        }, indent=2)


@dataclass
class K8sDeployment:
    """Represents a Kubernetes deployment."""

    name: str
    namespace: str
    uid: str
    replicas: int
    ready_replicas: int
    available_replicas: int
    updated_replicas: int
    created: datetime
    labels: dict[str, str] = field(default_factory=dict)
    annotations: dict[str, str] = field(default_factory=dict)
    selector: dict[str, str] = field(default_factory=dict)
    strategy: str = "RollingUpdate"
    conditions: list[dict[str, Any]] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps({
            "name": self.name,
            "namespace": self.namespace,
            "uid": self.uid,
            "replicas": self.replicas,
            "ready_replicas": self.ready_replicas,
            "available_replicas": self.available_replicas,
            "updated_replicas": self.updated_replicas,
            "created": self.created.isoformat(),
            "labels": self.labels,
            "annotations": self.annotations,
            "selector": self.selector,
            "strategy": self.strategy,
            "conditions": self.conditions,
        }, indent=2)


@dataclass
class K8sService:
    """Represents a Kubernetes service."""

    name: str
    namespace: str
    uid: str
    service_type: str  # ClusterIP, NodePort, LoadBalancer, ExternalName
    cluster_ip: str | None
    created: datetime
    labels: dict[str, str] = field(default_factory=dict)
    annotations: dict[str, str] = field(default_factory=dict)
    selector: dict[str, str] = field(default_factory=dict)
    ports: list[dict[str, Any]] = field(default_factory=list)
    external_ips: list[str] = field(default_factory=list)
    load_balancer_ip: str | None = None
    external_name: str | None = None

    def to_json(self) -> str:
        return json.dumps({
            "name": self.name,
            "namespace": self.namespace,
            "uid": self.uid,
            "type": self.service_type,
            "cluster_ip": self.cluster_ip,
            "created": self.created.isoformat(),
            "labels": self.labels,
            "annotations": self.annotations,
            "selector": self.selector,
            "ports": self.ports,
            "external_ips": self.external_ips,
            "load_balancer_ip": self.load_balancer_ip,
            "external_name": self.external_name,
        }, indent=2)


@dataclass
class K8sConfigMap:
    """Represents a Kubernetes ConfigMap."""

    name: str
    namespace: str
    uid: str
    created: datetime
    data: dict[str, str] = field(default_factory=dict)
    binary_data: dict[str, bytes] = field(default_factory=dict)
    labels: dict[str, str] = field(default_factory=dict)
    annotations: dict[str, str] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps({
            "name": self.name,
            "namespace": self.namespace,
            "uid": self.uid,
            "created": self.created.isoformat(),
            "data": self.data,
            "binary_data": {k: f"<{len(v)} bytes>" for k, v in self.binary_data.items()},
            "labels": self.labels,
            "annotations": self.annotations,
        }, indent=2)


@dataclass
class K8sSecret:
    """Represents a Kubernetes Secret."""

    name: str
    namespace: str
    uid: str
    secret_type: str  # Opaque, kubernetes.io/service-account-token, etc.
    created: datetime
    data: dict[str, bytes] = field(default_factory=dict)
    labels: dict[str, str] = field(default_factory=dict)
    annotations: dict[str, str] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps({
            "name": self.name,
            "namespace": self.namespace,
            "uid": self.uid,
            "type": self.secret_type,
            "created": self.created.isoformat(),
            "data": {k: f"<{len(v)} bytes>" for k, v in self.data.items()},
            "labels": self.labels,
            "annotations": self.annotations,
        }, indent=2)
