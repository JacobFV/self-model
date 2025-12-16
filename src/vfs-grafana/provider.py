"""Grafana VFS Provider implementation."""

from __future__ import annotations

from datetime import datetime
from typing import AsyncIterator, Any

from vfsd import CachingVFSProvider, VFSCapability, VFSNode, VFSPath
from vfsd.types import VFSNotFoundError, VFSIsDirectoryError, VFSPermissionError, VFSIOError

from .types import GrafanaDashboard, GrafanaPanel, GrafanaDatasource, GrafanaAlert


class GrafanaVFS(CachingVFSProvider):
    """Virtual filesystem for Grafana dashboards and alerts."""

    def __init__(
        self,
        url: str,
        api_key: str,
        username: str | None = None,
        password: str | None = None,
        cache_ttl: int = 300,
        org_id: int = 1,
    ):
        super().__init__(
            name="grafana",
            capabilities=VFSCapability.READ | VFSCapability.WRITE | VFSCapability.CREATE | VFSCapability.DELETE,
            cache_ttl_seconds=cache_ttl,
        )
        self._url = url.rstrip("/")
        self._api_key = api_key
        self._username = username
        self._password = password
        self._org_id = org_id

    async def initialize(self) -> None:
        """Initialize Grafana API connection."""
        pass

    async def _api_call(self, endpoint: str, method: str = "GET", **kwargs) -> dict:
        """Make a Grafana API call."""
        raise NotImplementedError("API call not implemented")

    def _parse_path(self, path: VFSPath) -> dict[str, str | None]:
        """Parse path into components."""
        segments = path.segments()
        return {
            "section": segments[0] if len(segments) >= 1 else None,
            "uid": segments[1] if len(segments) >= 2 else None,
            "subsection": segments[2] if len(segments) >= 3 else None,
            "item": segments[3] if len(segments) >= 4 else None,
            "subitem": segments[4] if len(segments) >= 5 else None,
        }

    async def get_node(self, path: VFSPath) -> VFSNode:
        """Get metadata for a path."""
        if str(path) in (".", ""):
            return VFSNode.directory(name="", mtime=datetime.now())

        parsed = self._parse_path(path)

        # Root-level files
        if parsed["section"] and not parsed["uid"]:
            if parsed["section"] in (".info.json", ".health.json"):
                return VFSNode.file(name=parsed["section"], size=500)
            # Root-level directories
            if parsed["section"] in ("dashboards", "folders", "datasources", "alerts",
                                     "users", "teams", "orgs", "plugins", "library", "snapshots"):
                return VFSNode.directory(name=parsed["section"], mtime=datetime.now())

        # Dashboard directory
        if parsed["section"] == "dashboards" and parsed["uid"]:
            if not parsed["subsection"]:
                return VFSNode.directory(name=parsed["uid"], mtime=datetime.now())
            if parsed["subsection"] in (".dashboard.json", "title.txt", "description.md",
                                        "tags.json", "folder.txt", "version.txt"):
                return VFSNode.file(name=parsed["subsection"], size=1000, writable=True)
            if parsed["subsection"] in ("panels", "variables", "annotations", "links", "versions", "permissions"):
                return VFSNode.directory(name=parsed["subsection"])

        # Datasource directory
        if parsed["section"] == "datasources" and parsed["uid"]:
            if not parsed["subsection"]:
                return VFSNode.directory(name=parsed["uid"], mtime=datetime.now())
            if parsed["subsection"] in (".datasource.json", "name.txt", "type.txt",
                                        "url.txt", "access.txt", "health.json"):
                return VFSNode.file(name=parsed["subsection"], size=500)
            if parsed["subsection"] == "query":
                return VFSNode.directory(name="query")

        # Alerts
        if parsed["section"] == "alerts":
            if not parsed["uid"]:
                return VFSNode.directory(name="alerts", mtime=datetime.now())
            if parsed["uid"] in ("rules", "instances", "notifications", "silences"):
                return VFSNode.directory(name=parsed["uid"])

        raise VFSNotFoundError(path)

    async def list_directory(self, path: VFSPath) -> AsyncIterator[VFSNode]:
        """List contents of a directory."""
        if str(path) in (".", ""):
            # Root
            yield VFSNode.file(name=".info.json", size=500)
            yield VFSNode.file(name=".health.json", size=200)
            yield VFSNode.directory(name="dashboards")
            yield VFSNode.directory(name="folders")
            yield VFSNode.directory(name="datasources")
            yield VFSNode.directory(name="alerts")
            yield VFSNode.directory(name="users")
            yield VFSNode.directory(name="teams")
            yield VFSNode.directory(name="orgs")
            yield VFSNode.directory(name="plugins")
            yield VFSNode.directory(name="library")
            yield VFSNode.directory(name="snapshots")
            return

        parsed = self._parse_path(path)

        # Dashboards directory
        if parsed["section"] == "dashboards" and not parsed["uid"]:
            yield VFSNode.file(name=".dashboards.json", size=2000)
            # Would list dashboard UIDs here
            return

        # Dashboard detail
        if parsed["section"] == "dashboards" and parsed["uid"] and not parsed["subsection"]:
            yield VFSNode.file(name=".dashboard.json", size=10000, writable=True)
            yield VFSNode.file(name="title.txt", size=100)
            yield VFSNode.file(name="description.md", size=500)
            yield VFSNode.file(name="tags.json", size=200)
            yield VFSNode.file(name="folder.txt", size=50)
            yield VFSNode.file(name="version.txt", size=10)
            yield VFSNode.directory(name="panels")
            yield VFSNode.directory(name="variables")
            yield VFSNode.directory(name="annotations")
            yield VFSNode.directory(name="links")
            yield VFSNode.directory(name="versions")
            yield VFSNode.directory(name="permissions")
            return

        # Datasources directory
        if parsed["section"] == "datasources" and not parsed["uid"]:
            # Would list datasource UIDs here
            return

        # Datasource detail
        if parsed["section"] == "datasources" and parsed["uid"] and not parsed["subsection"]:
            yield VFSNode.file(name=".datasource.json", size=2000)
            yield VFSNode.file(name="name.txt", size=100)
            yield VFSNode.file(name="type.txt", size=50)
            yield VFSNode.file(name="url.txt", size=200)
            yield VFSNode.file(name="access.txt", size=20)
            yield VFSNode.file(name="health.json", size=300)
            yield VFSNode.directory(name="query")
            return

        # Alerts directory
        if parsed["section"] == "alerts" and not parsed["uid"]:
            yield VFSNode.directory(name="rules")
            yield VFSNode.directory(name="instances")
            yield VFSNode.directory(name="notifications")
            yield VFSNode.directory(name="silences")
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
        """Write to a file (update dashboard, alert)."""
        raise VFSPermissionError(path, "write")
