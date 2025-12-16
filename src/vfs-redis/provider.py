"""Redis VFS Provider implementation."""

from __future__ import annotations

from datetime import datetime
from typing import AsyncIterator

from vfsd import CachingVFSProvider, VFSCapability, VFSNode, VFSPath
from vfsd.types import VFSNotFoundError, VFSIsDirectoryError, VFSPermissionError, VFSIOError

from .types import RedisKey, RedisString, RedisHash, RedisList, RedisSet, RedisSortedSet, RedisStream


class RedisVFS(CachingVFSProvider):
    """Virtual filesystem for Redis databases."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        password: str | None = None,
        db: int = 0,
        url: str | None = None,
        cluster: bool = False,
        cache_ttl: int = 60,
        decode_responses: bool = True,
        key_pattern: str = "*",
    ):
        super().__init__(
            name="redis",
            capabilities=VFSCapability.READ | VFSCapability.WRITE | VFSCapability.CREATE | VFSCapability.DELETE,
            cache_ttl_seconds=cache_ttl,
        )
        self._host = host
        self._port = port
        self._password = password
        self._db = db
        self._url = url
        self._cluster = cluster
        self._decode_responses = decode_responses
        self._key_pattern = key_pattern

    async def initialize(self) -> None:
        """Initialize Redis connection."""
        pass

    async def _redis_call(self, *args) -> Any:
        """Make a Redis command call."""
        raise NotImplementedError("Redis call not implemented")

    def _parse_path(self, path: VFSPath) -> dict[str, str | None]:
        """Parse path into components: db, type, key, subpath."""
        segments = path.segments()
        return {
            "db": segments[0] if len(segments) >= 1 else None,
            "type": segments[1] if len(segments) >= 2 else None,
            "key": segments[2] if len(segments) >= 3 else None,
            "subpath": segments[3] if len(segments) >= 4 else None,
            "subsubpath": segments[4] if len(segments) >= 5 else None,
        }

    async def get_node(self, path: VFSPath) -> VFSNode:
        """Get metadata for a path."""
        if str(path) in (".", ""):
            return VFSNode.directory(name="", mtime=datetime.now())

        parsed = self._parse_path(path)

        # Root - shows .info.json, .config.json, db directories
        if not parsed["db"]:
            return VFSNode.directory(name="", mtime=datetime.now())

        # Database directory (db0, db1, etc.)
        if parsed["db"] and not parsed["type"]:
            if parsed["db"].startswith("db"):
                return VFSNode.directory(name=parsed["db"], mtime=datetime.now())
            # Special files at root
            if parsed["db"] in (".info.json", ".config.json", ".clients.json", ".memory.json"):
                return VFSNode.file(name=parsed["db"], size=1000)

        # Type directories (strings, hashes, lists, sets, zsets, streams)
        if parsed["type"] in ("strings", "hashes", "lists", "sets", "zsets", "streams"):
            if not parsed["key"]:
                return VFSNode.directory(name=parsed["type"], mtime=datetime.now())

        # Database-level files
        if parsed["db"] and parsed["type"] in (".info.json", ".keys.txt"):
            return VFSNode.file(name=parsed["type"], size=500)

        raise VFSNotFoundError(path)

    async def list_directory(self, path: VFSPath) -> AsyncIterator[VFSNode]:
        """List contents of a directory."""
        if str(path) in (".", ""):
            # Root - list metadata files and databases
            yield VFSNode.file(name=".info.json", size=2000)
            yield VFSNode.file(name=".config.json", size=1000)
            yield VFSNode.file(name=".clients.json", size=500)
            yield VFSNode.file(name=".memory.json", size=500)
            # List databases (0-15 by default)
            for i in range(16):
                yield VFSNode.directory(name=f"db{i}")
            return

        parsed = self._parse_path(path)

        # Database root
        if parsed["db"] and parsed["db"].startswith("db") and not parsed["type"]:
            yield VFSNode.file(name=".info.json", size=500)
            yield VFSNode.file(name=".keys.txt", size=1000)
            yield VFSNode.directory(name="strings")
            yield VFSNode.directory(name="hashes")
            yield VFSNode.directory(name="lists")
            yield VFSNode.directory(name="sets")
            yield VFSNode.directory(name="zsets")
            yield VFSNode.directory(name="streams")
            return

        # Type directories - list keys of that type
        if parsed["type"] in ("strings", "hashes", "lists", "sets", "zsets", "streams") and not parsed["key"]:
            # Would list keys of this type from Redis
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
        """Write to a file (set Redis value)."""
        raise VFSPermissionError(path, "write")
