"""Prometheus VFS Provider implementation."""

from __future__ import annotations

from datetime import datetime
from typing import AsyncIterator, Any

from vfsd import CachingVFSProvider, VFSCapability, VFSNode, VFSPath
from vfsd.types import VFSNotFoundError, VFSIsDirectoryError, VFSPermissionError, VFSIOError

from .types import PromTarget, PromMetric, PromRule, PromAlert


class PrometheusVFS(CachingVFSProvider):
    """Virtual filesystem for Prometheus metrics and alerts."""

    def __init__(
        self,
        url: str,
        username: str | None = None,
        password: str | None = None,
        bearer_token: str | None = None,
        cache_ttl: int = 60,
        query_timeout: int = 30,
    ):
        super().__init__(
            name="prometheus",
            capabilities=VFSCapability.READ | VFSCapability.WRITE,
            cache_ttl_seconds=cache_ttl,
        )
        self._url = url.rstrip("/")
        self._username = username
        self._password = password
        self._bearer_token = bearer_token
        self._query_timeout = query_timeout

    async def initialize(self) -> None:
        """Initialize Prometheus API connection."""
        pass

    async def _api_call(self, endpoint: str, method: str = "GET", **kwargs) -> dict:
        """Make a Prometheus API call."""
        raise NotImplementedError("API call not implemented")

    def _parse_path(self, path: VFSPath) -> dict[str, str | None]:
        """Parse path into components."""
        segments = path.segments()
        return {
            "section": segments[0] if len(segments) >= 1 else None,
            "subsection": segments[1] if len(segments) >= 2 else None,
            "item": segments[2] if len(segments) >= 3 else None,
            "subitem": segments[3] if len(segments) >= 4 else None,
            "subsubitem": segments[4] if len(segments) >= 5 else None,
        }

    async def get_node(self, path: VFSPath) -> VFSNode:
        """Get metadata for a path."""
        if str(path) in (".", ""):
            return VFSNode.directory(name="", mtime=datetime.now())

        parsed = self._parse_path(path)

        # Root-level files
        if parsed["section"] and not parsed["subsection"]:
            if parsed["section"] in (".status.json", ".config.yaml", ".flags.json",
                                     ".runtime.json", ".build.json"):
                return VFSNode.file(name=parsed["section"], size=1000)
            # Root-level directories
            if parsed["section"] in ("targets", "metrics", "rules", "alerts", "tsdb", "query", "federation", "api"):
                return VFSNode.directory(name=parsed["section"], mtime=datetime.now())

        # Targets
        if parsed["section"] == "targets":
            if not parsed["subsection"]:
                return VFSNode.directory(name="targets", mtime=datetime.now())
            if parsed["subsection"] == ".targets.json":
                return VFSNode.file(name=".targets.json", size=2000)
            # Job directory
            if parsed["subsection"] and not parsed["item"]:
                return VFSNode.directory(name=parsed["subsection"], mtime=datetime.now())

        # Metrics
        if parsed["section"] == "metrics":
            if not parsed["subsection"]:
                return VFSNode.directory(name="metrics", mtime=datetime.now())
            if parsed["subsection"] == ".metrics.txt":
                return VFSNode.file(name=".metrics.txt", size=5000)
            # Metric name directory
            if parsed["subsection"] and not parsed["item"]:
                return VFSNode.directory(name=parsed["subsection"], mtime=datetime.now())

        # Rules
        if parsed["section"] == "rules":
            if not parsed["subsection"]:
                return VFSNode.directory(name="rules", mtime=datetime.now())
            if parsed["subsection"] == ".rules.json":
                return VFSNode.file(name=".rules.json", size=3000)
            # Rule group directory
            if parsed["subsection"] and not parsed["item"]:
                return VFSNode.directory(name=parsed["subsection"], mtime=datetime.now())

        # Alerts
        if parsed["section"] == "alerts":
            if not parsed["subsection"]:
                return VFSNode.directory(name="alerts", mtime=datetime.now())
            if parsed["subsection"] == ".alerts.json":
                return VFSNode.file(name=".alerts.json", size=2000)
            if parsed["subsection"] in ("firing", "pending", "inactive"):
                return VFSNode.directory(name=parsed["subsection"])

        # Query
        if parsed["section"] == "query":
            if not parsed["subsection"]:
                return VFSNode.directory(name="query", mtime=datetime.now())
            if parsed["subsection"] in ("instant", "range"):
                return VFSNode.directory(name=parsed["subsection"])

        # TSDB
        if parsed["section"] == "tsdb":
            if not parsed["subsection"]:
                return VFSNode.directory(name="tsdb", mtime=datetime.now())
            if parsed["subsection"] in (".status.json", "head_stats.json", "label_names.txt"):
                return VFSNode.file(name=parsed["subsection"], size=1000)
            if parsed["subsection"] == "label_values":
                return VFSNode.directory(name="label_values")

        raise VFSNotFoundError(path)

    async def list_directory(self, path: VFSPath) -> AsyncIterator[VFSNode]:
        """List contents of a directory."""
        if str(path) in (".", ""):
            # Root
            yield VFSNode.file(name=".status.json", size=1000)
            yield VFSNode.file(name=".config.yaml", size=2000)
            yield VFSNode.file(name=".flags.json", size=500)
            yield VFSNode.file(name=".runtime.json", size=500)
            yield VFSNode.file(name=".build.json", size=300)
            yield VFSNode.directory(name="targets")
            yield VFSNode.directory(name="metrics")
            yield VFSNode.directory(name="rules")
            yield VFSNode.directory(name="alerts")
            yield VFSNode.directory(name="tsdb")
            yield VFSNode.directory(name="query")
            yield VFSNode.directory(name="federation")
            yield VFSNode.directory(name="api")
            return

        parsed = self._parse_path(path)

        # Targets directory
        if parsed["section"] == "targets" and not parsed["subsection"]:
            yield VFSNode.file(name=".targets.json", size=2000)
            # Would list job names here
            return

        # Target job directory
        if parsed["section"] == "targets" and parsed["subsection"] and not parsed["item"]:
            yield VFSNode.file(name=".job.json", size=500)
            # Would list instances here
            return

        # Target instance directory
        if parsed["section"] == "targets" and parsed["subsection"] and parsed["item"] and not parsed["subitem"]:
            yield VFSNode.file(name=".target.json", size=800)
            yield VFSNode.file(name="health.txt", size=10)
            yield VFSNode.file(name="labels.json", size=300)
            yield VFSNode.file(name="last_scrape.txt", size=30)
            yield VFSNode.file(name="scrape_duration.txt", size=20)
            yield VFSNode.file(name="last_error.txt", size=200)
            return

        # Metrics directory
        if parsed["section"] == "metrics" and not parsed["subsection"]:
            yield VFSNode.file(name=".metrics.txt", size=5000)
            # Would list metric names here
            return

        # Metric detail directory
        if parsed["section"] == "metrics" and parsed["subsection"] and not parsed["item"]:
            yield VFSNode.file(name=".metric.json", size=300)
            yield VFSNode.file(name="type.txt", size=20)
            yield VFSNode.file(name="help.txt", size=200)
            yield VFSNode.directory(name="series")
            yield VFSNode.directory(name="query")
            return

        # Rules directory
        if parsed["section"] == "rules" and not parsed["subsection"]:
            yield VFSNode.file(name=".rules.json", size=3000)
            # Would list rule groups here
            return

        # Rule group directory
        if parsed["section"] == "rules" and parsed["subsection"] and not parsed["item"]:
            yield VFSNode.file(name=".group.json", size=1000)
            yield VFSNode.file(name="interval.txt", size=10)
            # Would list rule names here
            return

        # Alerts directory
        if parsed["section"] == "alerts" and not parsed["subsection"]:
            yield VFSNode.file(name=".alerts.json", size=2000)
            yield VFSNode.directory(name="firing")
            yield VFSNode.directory(name="pending")
            yield VFSNode.directory(name="inactive")
            return

        # Query directory
        if parsed["section"] == "query" and not parsed["subsection"]:
            yield VFSNode.directory(name="instant")
            yield VFSNode.directory(name="range")
            return

        # TSDB directory
        if parsed["section"] == "tsdb" and not parsed["subsection"]:
            yield VFSNode.file(name=".status.json", size=1000)
            yield VFSNode.file(name="head_stats.json", size=800)
            yield VFSNode.file(name="label_names.txt", size=500)
            yield VFSNode.directory(name="label_values")
            return

        raise VFSNotFoundError(path)

    async def read_file(self, path: VFSPath, offset: int = 0, size: int | None = None) -> bytes:
        """Read file contents."""
        node = await self.get_node(path)
        if node.is_directory:
            raise VFSIsDirectoryError(path)
        if node._cached_content:
            content = node._cached_content
            if offset:
                content = content[offset:]
            if size is not None:
                content = content[:size]
            return content
        raise VFSIOError("No content available", path)

    async def write_file(self, path: VFSPath, data: bytes, offset: int = 0) -> int:
        """Write to a file (limited support)."""
        raise VFSPermissionError(path, "write")
