"""Elasticsearch VFS Provider implementation."""

from __future__ import annotations

from datetime import datetime
from typing import AsyncIterator, Any

from vfsd import CachingVFSProvider, VFSCapability, VFSNode, VFSPath
from vfsd.types import VFSNotFoundError, VFSIsDirectoryError, VFSPermissionError, VFSIOError

from .types import ESIndex, ESDocument, ESMapping


class ElasticsearchVFS(CachingVFSProvider):
    """Virtual filesystem for Elasticsearch clusters."""

    def __init__(
        self,
        hosts: list[str],
        api_key: str | None = None,
        basic_auth: tuple[str, str] | None = None,
        ca_certs: str | None = None,
        verify_certs: bool = True,
        cache_ttl: int = 300,
        search_size: int = 100,
    ):
        super().__init__(
            name="elasticsearch",
            capabilities=VFSCapability.READ | VFSCapability.WRITE | VFSCapability.CREATE | VFSCapability.DELETE,
            cache_ttl_seconds=cache_ttl,
        )
        self._hosts = hosts
        self._api_key = api_key
        self._basic_auth = basic_auth
        self._ca_certs = ca_certs
        self._verify_certs = verify_certs
        self._search_size = search_size

    async def initialize(self) -> None:
        """Initialize Elasticsearch client."""
        pass

    async def _es_call(self, method: str, endpoint: str, **kwargs) -> dict:
        """Make an Elasticsearch API call."""
        raise NotImplementedError("Elasticsearch call not implemented")

    def _parse_path(self, path: VFSPath) -> dict[str, str | None]:
        """Parse path into components."""
        segments = path.segments()
        return {
            "section": segments[0] if len(segments) >= 1 else None,
            "index": segments[1] if len(segments) >= 2 else None,
            "subsection": segments[2] if len(segments) >= 3 else None,
            "item": segments[3] if len(segments) >= 4 else None,
            "subitem": segments[4] if len(segments) >= 5 else None,
        }

    async def get_node(self, path: VFSPath) -> VFSNode:
        """Get metadata for a path."""
        if str(path) in (".", ""):
            return VFSNode.directory(name="", mtime=datetime.now())

        parsed = self._parse_path(path)

        # Special directories at root
        if parsed["section"] and not parsed["index"]:
            if parsed["section"] in ("_cluster", "_cat", "_templates", "_component_templates",
                                     "_index_templates", "_ilm", "_snapshots", "_ingest", "_aliases", "_tasks"):
                return VFSNode.directory(name=parsed["section"], mtime=datetime.now())

        # Cluster files
        if parsed["section"] == "_cluster" and parsed["index"]:
            if parsed["index"] in ("health.json", "stats.json", "settings.json", "pending_tasks.json"):
                return VFSNode.file(name=parsed["index"], size=2000)
            if parsed["index"] == "nodes":
                return VFSNode.directory(name="nodes")

        # CAT files
        if parsed["section"] == "_cat" and parsed["index"]:
            if parsed["index"] in ("indices.txt", "shards.txt", "nodes.txt", "allocation.txt", "health.txt"):
                return VFSNode.file(name=parsed["index"], size=1000)

        # Index directory
        if parsed["section"] and not parsed["section"].startswith("_"):
            if not parsed["index"]:
                return VFSNode.directory(name=parsed["section"], mtime=datetime.now())

        raise VFSNotFoundError(path)

    async def list_directory(self, path: VFSPath) -> AsyncIterator[VFSNode]:
        """List contents of a directory."""
        if str(path) in (".", ""):
            # Root - list special directories
            yield VFSNode.directory(name="_cluster")
            yield VFSNode.directory(name="_cat")
            yield VFSNode.directory(name="_templates")
            yield VFSNode.directory(name="_component_templates")
            yield VFSNode.directory(name="_index_templates")
            yield VFSNode.directory(name="_ilm")
            yield VFSNode.directory(name="_snapshots")
            yield VFSNode.directory(name="_ingest")
            yield VFSNode.directory(name="_aliases")
            yield VFSNode.directory(name="_tasks")
            # Would list indices here
            return

        parsed = self._parse_path(path)

        # Cluster directory
        if parsed["section"] == "_cluster" and not parsed["index"]:
            yield VFSNode.file(name="health.json", size=1000)
            yield VFSNode.file(name="stats.json", size=5000)
            yield VFSNode.file(name="settings.json", size=2000)
            yield VFSNode.file(name="pending_tasks.json", size=500)
            yield VFSNode.directory(name="nodes")
            return

        # CAT directory
        if parsed["section"] == "_cat" and not parsed["index"]:
            yield VFSNode.file(name="indices.txt", size=2000)
            yield VFSNode.file(name="shards.txt", size=3000)
            yield VFSNode.file(name="nodes.txt", size=1000)
            yield VFSNode.file(name="allocation.txt", size=1500)
            yield VFSNode.file(name="health.txt", size=500)
            return

        # Index root
        if parsed["section"] and not parsed["section"].startswith("_") and not parsed["index"]:
            yield VFSNode.file(name=".index.json", size=1000)
            yield VFSNode.file(name="_settings.json", size=500, writable=True)
            yield VFSNode.file(name="_mappings.json", size=2000, writable=True)
            yield VFSNode.file(name="_aliases.json", size=300)
            yield VFSNode.file(name="_stats.json", size=1500)
            yield VFSNode.file(name="_segments.json", size=1000)
            yield VFSNode.file(name="_recovery.json", size=800)
            yield VFSNode.directory(name="_doc")
            yield VFSNode.directory(name="_search")
            yield VFSNode.directory(name="_bulk")
            yield VFSNode.directory(name="_analyze")
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
        """Write to a file (update settings, mappings, documents)."""
        raise VFSPermissionError(path, "write")
