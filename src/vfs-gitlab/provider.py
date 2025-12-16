"""GitLab VFS Provider implementation."""

from __future__ import annotations

from datetime import datetime
from typing import AsyncIterator

from vfsd import CachingVFSProvider, VFSCapability, VFSNode, VFSPath
from vfsd.types import VFSNotFoundError, VFSIsDirectoryError, VFSPermissionError, VFSIOError

from .types import GitLabProject, GitLabMR, GitLabIssue, GitLabPipeline


class GitLabVFS(CachingVFSProvider):
    """Virtual filesystem for GitLab projects."""

    def __init__(
        self,
        token: str,
        url: str = "https://gitlab.com",
        oauth_token: str | None = None,
        cache_ttl: int = 300,
        include_archived: bool = False,
    ):
        super().__init__(
            name="gitlab",
            capabilities=VFSCapability.READ | VFSCapability.WRITE | VFSCapability.CREATE,
            cache_ttl_seconds=cache_ttl,
        )
        self._token = token
        self._url = url.rstrip("/")
        self._oauth_token = oauth_token
        self._include_archived = include_archived

    async def initialize(self) -> None:
        """Initialize and verify token."""
        pass

    async def _api_call(self, endpoint: str, method: str = "GET", **kwargs) -> dict:
        """Make a GitLab API call."""
        raise NotImplementedError("API call not implemented")

    def _parse_path(self, path: VFSPath) -> dict[str, str | None]:
        """Parse path into components: group, project, section, item, subitem."""
        segments = path.segments()
        return {
            "group": segments[0] if len(segments) >= 1 else None,
            "project": segments[1] if len(segments) >= 2 else None,
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

        # Group directory
        if parsed["group"] and not parsed["project"]:
            if parsed["group"] in ("users", "explore"):
                return VFSNode.directory(name=parsed["group"], mtime=datetime.now())
            # Regular group
            return VFSNode.directory(name=parsed["group"], mtime=datetime.now())

        # Project directory
        if parsed["project"] and not parsed["section"]:
            return VFSNode.directory(name=parsed["project"], mtime=datetime.now())

        # Project metadata files
        if parsed["project"] and parsed["section"]:
            if parsed["section"] in (".project.json", "README.md", "description.md", "visibility.txt"):
                return VFSNode.file(name=parsed["section"], size=1000)
            # Section directories
            if parsed["section"] in ("branches", "tags", "commits", "merge_requests", "issues",
                                     "pipelines", "environments", "releases", "wiki", "snippets",
                                     "container_registry", "packages"):
                return VFSNode.directory(name=parsed["section"], mtime=datetime.now())

        # Group metadata
        if parsed["group"] and parsed["project"] == ".group.json":
            return VFSNode.file(name=".group.json", size=500)

        raise VFSNotFoundError(path)

    async def list_directory(self, path: VFSPath) -> AsyncIterator[VFSNode]:
        """List contents of a directory."""
        if str(path) in (".", ""):
            # Root - would list groups/users/explore
            yield VFSNode.directory(name="users")
            yield VFSNode.directory(name="explore")
            return

        parsed = self._parse_path(path)

        # Group root
        if parsed["group"] and not parsed["project"]:
            yield VFSNode.file(name=".group.json", size=500)
            yield VFSNode.directory(name="members")
            yield VFSNode.directory(name="subgroups")
            # Would list projects here
            return

        # Project root
        if parsed["project"] and not parsed["section"]:
            yield VFSNode.file(name=".project.json", size=2000)
            yield VFSNode.file(name="README.md", size=1000)
            yield VFSNode.file(name="description.md", size=300)
            yield VFSNode.file(name="visibility.txt", size=20)
            yield VFSNode.directory(name="branches")
            yield VFSNode.directory(name="tags")
            yield VFSNode.directory(name="commits")
            yield VFSNode.directory(name="merge_requests")
            yield VFSNode.directory(name="issues")
            yield VFSNode.directory(name="pipelines")
            yield VFSNode.directory(name="environments")
            yield VFSNode.directory(name="releases")
            yield VFSNode.directory(name="wiki")
            yield VFSNode.directory(name="snippets")
            yield VFSNode.directory(name="container_registry")
            yield VFSNode.directory(name="packages")
            return

        # Merge requests directory
        if parsed["section"] == "merge_requests" and not parsed["item"]:
            yield VFSNode.directory(name="opened")
            yield VFSNode.directory(name="merged")
            yield VFSNode.directory(name="closed")
            return

        # Issues directory
        if parsed["section"] == "issues" and not parsed["item"]:
            yield VFSNode.directory(name="opened")
            yield VFSNode.directory(name="closed")
            return

        # Pipelines directory
        if parsed["section"] == "pipelines" and not parsed["item"]:
            yield VFSNode.directory(name="recent")
            return

        # MR detail
        if parsed["section"] == "merge_requests" and parsed["item"] and parsed["item"].isdigit():
            if not parsed["subitem"]:
                yield VFSNode.file(name=".mr.json", size=3000)
                yield VFSNode.file(name="title.txt", size=200, writable=True)
                yield VFSNode.file(name="description.md", size=2000, writable=True)
                yield VFSNode.file(name="state.txt", size=20)
                yield VFSNode.file(name="source_branch.txt", size=100)
                yield VFSNode.file(name="target_branch.txt", size=100)
                yield VFSNode.file(name="diff.patch", size=5000)
                yield VFSNode.directory(name="changes")
                yield VFSNode.directory(name="commits")
                yield VFSNode.directory(name="discussions")
                yield VFSNode.directory(name="approvals")
                yield VFSNode.directory(name="pipelines")
                return

        # Issue detail
        if parsed["section"] == "issues" and parsed["item"] and parsed["item"].isdigit():
            if not parsed["subitem"]:
                yield VFSNode.file(name=".issue.json", size=2000)
                yield VFSNode.file(name="title.txt", size=200, writable=True)
                yield VFSNode.file(name="description.md", size=2000, writable=True)
                yield VFSNode.file(name="state.txt", size=20)
                yield VFSNode.file(name="labels.json", size=200, writable=True)
                yield VFSNode.file(name="assignees.json", size=200, writable=True)
                yield VFSNode.file(name="milestone.txt", size=100)
                yield VFSNode.file(name="weight.txt", size=10, writable=True)
                yield VFSNode.file(name="time_tracking.json", size=300)
                yield VFSNode.directory(name="notes")
                return

        # Pipeline detail
        if parsed["section"] == "pipelines" and parsed["item"] and parsed["item"].isdigit():
            if not parsed["subitem"]:
                yield VFSNode.file(name=".pipeline.json", size=1500)
                yield VFSNode.file(name="status.txt", size=20)
                yield VFSNode.file(name="ref.txt", size=100)
                yield VFSNode.file(name="sha.txt", size=50)
                yield VFSNode.file(name="duration.txt", size=20)
                yield VFSNode.file(name="variables.json", size=500)
                yield VFSNode.directory(name="jobs")
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
        """Write to a file (update MR, issue, etc.)."""
        raise VFSPermissionError(path, "write")
