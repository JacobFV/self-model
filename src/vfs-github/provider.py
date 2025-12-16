"""GitHub VFS Provider implementation."""

from __future__ import annotations

from datetime import datetime
from typing import AsyncIterator

from vfsd import CachingVFSProvider, VFSCapability, VFSNode, VFSPath
from vfsd.types import VFSNotFoundError, VFSIsDirectoryError, VFSPermissionError, VFSIOError

from .types import GitHubRepo, GitHubBranch, GitHubCommit, GitHubIssue, GitHubPR


class GitHubVFS(CachingVFSProvider):
    """Virtual filesystem for GitHub repositories."""

    def __init__(
        self,
        token: str,
        base_url: str | None = None,
        cache_ttl: int = 300,
        include_forks: bool = True,
        include_archived: bool = False,
    ):
        super().__init__(
            name="github",
            capabilities=VFSCapability.READ | VFSCapability.WRITE | VFSCapability.CREATE,
            cache_ttl_seconds=cache_ttl,
        )
        self._token = token
        self._base_url = base_url or "https://api.github.com"
        self._include_forks = include_forks
        self._include_archived = include_archived

    async def initialize(self) -> None:
        """Initialize and verify token."""
        pass

    async def _api_call(self, endpoint: str, method: str = "GET", **kwargs) -> dict:
        """Make a GitHub API call."""
        raise NotImplementedError("API call not implemented")

    def _parse_path(self, path: VFSPath) -> dict[str, str | None]:
        """Parse path into components: owner, repo, section, item, subitem."""
        segments = path.segments()
        return {
            "owner": segments[0] if len(segments) >= 1 else None,
            "repo": segments[1] if len(segments) >= 2 else None,
            "section": segments[2] if len(segments) >= 3 else None,
            "item": segments[3] if len(segments) >= 4 else None,
            "subitem": segments[4] if len(segments) >= 5 else None,
            "subsubitem": segments[5] if len(segments) >= 6 else None,
        }

    async def get_node(self, path: VFSPath) -> VFSNode:
        """Get metadata for a path."""
        if str(path) in (".", ""):
            return VFSNode.directory(name="", mtime=datetime.now())

        parsed = self._parse_path(path)

        # Owner directory
        if parsed["owner"] and not parsed["repo"]:
            return VFSNode.directory(name=parsed["owner"], mtime=datetime.now())

        # Repo directory
        if parsed["repo"] and not parsed["section"]:
            return VFSNode.directory(name=parsed["repo"], mtime=datetime.now())

        # Section directories
        if parsed["section"] in ("branches", "commits", "issues", "pulls", "releases", "actions", "wiki"):
            return VFSNode.directory(name=parsed["section"], mtime=datetime.now())

        raise VFSNotFoundError(path)

    async def list_directory(self, path: VFSPath) -> AsyncIterator[VFSNode]:
        """List contents of a directory."""
        if str(path) in (".", ""):
            # Root - would list organizations/users the token has access to
            return

        parsed = self._parse_path(path)

        # Repo root
        if parsed["repo"] and not parsed["section"]:
            yield VFSNode.file(name=".repo.json", size=500)
            yield VFSNode.file(name="README.md", size=1000)
            yield VFSNode.directory(name="branches")
            yield VFSNode.directory(name="tags")
            yield VFSNode.directory(name="commits")
            yield VFSNode.directory(name="issues")
            yield VFSNode.directory(name="pulls")
            yield VFSNode.directory(name="releases")
            yield VFSNode.directory(name="actions")
            yield VFSNode.directory(name="wiki")
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
        """Write to a file (create issue, comment, etc.)."""
        raise VFSPermissionError(path, "write")
