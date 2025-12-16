"""
VFS Daemon Configuration.

Manages persistent configuration for registered providers and daemon settings.
Configuration is stored in ~/.config/vfsd/config.json (or XDG_CONFIG_HOME).
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


def get_config_dir() -> Path:
    """Get the configuration directory."""
    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config:
        base = Path(xdg_config)
    else:
        base = Path.home() / ".config"
    return base / "vfsd"


def get_config_path() -> Path:
    """Get the configuration file path."""
    return get_config_dir() / "config.json"


def get_providers_dir() -> Path:
    """Get the directory for local provider installations."""
    return get_config_dir() / "providers"


@dataclass
class ProviderConfig:
    """Configuration for a registered VFS provider."""

    name: str
    module: str  # Python module path (e.g., "vfs_slack" or "./local/path")
    enabled: bool = True
    auto_mount: bool = False
    mount_point: str | None = None  # Custom mount point override
    config: dict[str, Any] = field(default_factory=dict)  # Provider-specific config

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> ProviderConfig:
        return cls(**data)


@dataclass
class DaemonConfig:
    """Configuration for the VFS daemon itself."""

    mount_path: str = "/tmp/vfsd"
    foreground: bool = False
    log_level: str = "INFO"
    log_file: str | None = None
    pid_file: str | None = None
    socket_path: str | None = None  # Unix socket for IPC
    cache_ttl: int = 300  # Default cache TTL in seconds
    max_cache_size: int = 1000  # Max cached entries

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> DaemonConfig:
        return cls(**data)


@dataclass
class VFSDConfig:
    """
    Complete vfsd configuration.

    Manages registered providers and daemon settings.
    """

    daemon: DaemonConfig = field(default_factory=DaemonConfig)
    providers: dict[str, ProviderConfig] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path | None = None) -> VFSDConfig:
        """Load configuration from file."""
        config_path = path or get_config_path()

        if not config_path.exists():
            return cls()

        with open(config_path) as f:
            data = json.load(f)

        daemon = DaemonConfig.from_dict(data.get("daemon", {}))
        providers = {
            name: ProviderConfig.from_dict(pdata)
            for name, pdata in data.get("providers", {}).items()
        }

        return cls(daemon=daemon, providers=providers)

    def save(self, path: Path | None = None) -> None:
        """Save configuration to file."""
        config_path = path or get_config_path()
        config_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "daemon": self.daemon.to_dict(),
            "providers": {
                name: prov.to_dict() for name, prov in self.providers.items()
            },
        }

        with open(config_path, "w") as f:
            json.dump(data, f, indent=2)

    def register_provider(
        self,
        name: str,
        module: str,
        config: dict[str, Any] | None = None,
        enabled: bool = True,
        auto_mount: bool = False,
        mount_point: str | None = None,
    ) -> ProviderConfig:
        """Register a new provider."""
        provider = ProviderConfig(
            name=name,
            module=module,
            enabled=enabled,
            auto_mount=auto_mount,
            mount_point=mount_point,
            config=config or {},
        )
        self.providers[name] = provider
        return provider

    def unregister_provider(self, name: str) -> bool:
        """Unregister a provider. Returns True if it existed."""
        if name in self.providers:
            del self.providers[name]
            return True
        return False

    def get_provider(self, name: str) -> ProviderConfig | None:
        """Get provider config by name."""
        return self.providers.get(name)

    def list_providers(self) -> list[ProviderConfig]:
        """List all registered providers."""
        return list(self.providers.values())

    def get_enabled_providers(self) -> list[ProviderConfig]:
        """List enabled providers."""
        return [p for p in self.providers.values() if p.enabled]

    def get_auto_mount_providers(self) -> list[ProviderConfig]:
        """List providers configured for auto-mount."""
        return [p for p in self.providers.values() if p.enabled and p.auto_mount]


# Known provider packages (for discovery and suggestions)
KNOWN_PROVIDERS = {
    "slack": {
        "package": "vfs-slack",
        "module": "vfs_slack",
        "description": "Slack workspaces, channels, messages, threads",
        "required_config": ["token"],
    },
    "github": {
        "package": "vfs-github",
        "module": "vfs_github",
        "description": "GitHub repos, branches, issues, PRs, files",
        "required_config": ["token"],
    },
    "linear": {
        "package": "vfs-linear",
        "module": "vfs_linear",
        "description": "Linear issues, projects, cycles, roadmaps",
        "required_config": ["api_key"],
    },
    "notion": {
        "package": "vfs-notion",
        "module": "vfs_notion",
        "description": "Notion pages, databases, blocks",
        "required_config": ["token"],
    },
    "jira": {
        "package": "vfs-jira",
        "module": "vfs_jira",
        "description": "Jira projects, issues, sprints, boards",
        "required_config": ["url", "email", "api_token"],
    },
    "gdrive": {
        "package": "vfs-gdrive",
        "module": "vfs_gdrive",
        "description": "Google Drive files, folders, shared drives",
        "required_config": ["credentials_path"],
    },
    "dropbox": {
        "package": "vfs-dropbox",
        "module": "vfs_dropbox",
        "description": "Dropbox files, folders, Paper docs",
        "required_config": ["access_token"],
    },
    "s3": {
        "package": "vfs-s3",
        "module": "vfs_s3",
        "description": "AWS S3 buckets and objects",
        "required_config": [],  # Uses AWS credentials chain
        "optional_config": ["region", "profile"],
    },
    "docker": {
        "package": "vfs-docker",
        "module": "vfs_docker",
        "description": "Docker containers, images, volumes, networks",
        "required_config": [],  # Uses docker socket
        "optional_config": ["socket_path"],
    },
    "k8s": {
        "package": "vfs-k8s",
        "module": "vfs_k8s",
        "description": "Kubernetes pods, deployments, services, configmaps",
        "required_config": [],  # Uses kubeconfig
        "optional_config": ["kubeconfig", "context"],
    },
    "postgres": {
        "package": "vfs-postgres",
        "module": "vfs_postgres",
        "description": "PostgreSQL databases, schemas, tables, rows",
        "required_config": ["connection_string"],
    },
    "mongodb": {
        "package": "vfs-mongodb",
        "module": "vfs_mongodb",
        "description": "MongoDB databases, collections, documents",
        "required_config": ["connection_string"],
    },
    "redis": {
        "package": "vfs-redis",
        "module": "vfs_redis",
        "description": "Redis keys, hashes, lists, sets, streams",
        "required_config": [],
        "optional_config": ["host", "port", "password", "db"],
    },
    "elasticsearch": {
        "package": "vfs-elasticsearch",
        "module": "vfs_elasticsearch",
        "description": "Elasticsearch indices, documents, mappings",
        "required_config": ["hosts"],
        "optional_config": ["api_key", "username", "password"],
    },
    "grafana": {
        "package": "vfs-grafana",
        "module": "vfs_grafana",
        "description": "Grafana dashboards, panels, datasources, alerts",
        "required_config": ["url", "api_key"],
    },
    "prometheus": {
        "package": "vfs-prometheus",
        "module": "vfs_prometheus",
        "description": "Prometheus targets, metrics, rules, alerts",
        "required_config": ["url"],
    },
    "gitlab": {
        "package": "vfs-gitlab",
        "module": "vfs_gitlab",
        "description": "GitLab projects, MRs, issues, pipelines, wiki",
        "required_config": ["token"],
        "optional_config": ["url"],
    },
    "discord": {
        "package": "vfs-discord",
        "module": "vfs_discord",
        "description": "Discord servers, channels, messages, threads",
        "required_config": ["token"],
    },
    "trello": {
        "package": "vfs-trello",
        "module": "vfs_trello",
        "description": "Trello boards, lists, cards, checklists",
        "required_config": ["api_key", "token"],
    },
    "figma": {
        "package": "vfs-figma",
        "module": "vfs_figma",
        "description": "Figma files, frames, components, styles",
        "required_config": ["access_token"],
    },
}
