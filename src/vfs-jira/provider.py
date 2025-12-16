"""Jira VFS Provider implementation."""

from __future__ import annotations

from datetime import datetime
from typing import AsyncIterator

from vfsd import CachingVFSProvider, VFSCapability, VFSNode, VFSPath
from vfsd.types import VFSNotFoundError, VFSIsDirectoryError, VFSPermissionError, VFSIOError

from .types import JiraIssue, JiraProject, JiraSprint, JiraBoard


class JiraVFS(CachingVFSProvider):
    """Virtual filesystem for Jira projects, issues, sprints, and boards."""

    def __init__(
        self,
        url: str,
        email: str,
        api_token: str,
        cache_ttl: int = 300,
    ):
        super().__init__(
            name="jira",
            capabilities=VFSCapability.READ | VFSCapability.WRITE | VFSCapability.CREATE | VFSCapability.DELETE,
            cache_ttl_seconds=cache_ttl,
        )
        self._url = url.rstrip("/")
        self._email = email
        self._api_token = api_token

    async def initialize(self) -> None:
        """Initialize and verify credentials."""
        pass

    async def _api_call(self, endpoint: str, method: str = "GET", **kwargs) -> dict:
        """Make a Jira REST API call."""
        raise NotImplementedError("API call not implemented")

    def _parse_path(self, path: VFSPath) -> dict[str, str | None]:
        """Parse path into components: project, section, item, etc."""
        segments = path.segments()
        return {
            "project_key": segments[0] if len(segments) >= 1 else None,
            "section": segments[1] if len(segments) >= 2 else None,  # issues, sprints, boards, components, etc.
            "subsection": segments[2] if len(segments) >= 3 else None,  # by-type, by-status, issue-key, etc.
            "item": segments[3] if len(segments) >= 4 else None,
            "subitem": segments[4] if len(segments) >= 5 else None,
            "subsubitem": segments[5] if len(segments) >= 6 else None,
        }

    async def get_node(self, path: VFSPath) -> VFSNode:
        """Get metadata for a path."""
        if str(path) in (".", ""):
            return VFSNode.directory(name="", mtime=datetime.now())

        parsed = self._parse_path(path)

        # Project root
        if parsed["project_key"] and not parsed["section"]:
            return VFSNode.directory(name=parsed["project_key"], mtime=datetime.now())

        # Project files
        if parsed["project_key"] and parsed["section"] in (".project.json", "description.md", "lead.json"):
            return VFSNode.file(name=parsed["section"], size=500)

        # Project sections
        if parsed["project_key"] and parsed["section"] in ("issues", "epics", "sprints", "boards", "components", "versions"):
            return VFSNode.directory(name=parsed["section"], mtime=datetime.now())

        # Issues subsections
        if parsed["project_key"] and parsed["section"] == "issues" and parsed["subsection"]:
            if parsed["subsection"] in ("by-type", "by-status"):
                return VFSNode.directory(name=parsed["subsection"], mtime=datetime.now())
            # Issue key directory (e.g., PROJ-123)
            if not parsed["item"]:
                return VFSNode.directory(name=parsed["subsection"], mtime=datetime.now())

        # Issue files
        if parsed["project_key"] and parsed["section"] == "issues" and parsed["subsection"] and parsed["item"]:
            if parsed["item"] in (".issue.json", "summary.txt", "description.md", "type.txt", "status.txt",
                                "priority.txt", "assignee.txt", "reporter.txt", "labels.json", "components.json",
                                "fix-versions.json", "story-points.txt", "time-tracking.json", "parent.txt"):
                return VFSNode.file(name=parsed["item"], size=500)
            if parsed["item"] in ("subtasks", "links", "comments", "attachments", "worklogs", "history"):
                return VFSNode.directory(name=parsed["item"], mtime=datetime.now())

        # Sprint directory
        if parsed["project_key"] and parsed["section"] == "sprints" and parsed["subsection"]:
            if parsed["subsection"] == "active":
                return VFSNode.directory(name="active", mtime=datetime.now())
            if not parsed["item"]:
                return VFSNode.directory(name=parsed["subsection"], mtime=datetime.now())

        # Board directory
        if parsed["project_key"] and parsed["section"] == "boards" and parsed["subsection"] and not parsed["item"]:
            return VFSNode.directory(name=parsed["subsection"], mtime=datetime.now())

        raise VFSNotFoundError(path)

    async def list_directory(self, path: VFSPath) -> AsyncIterator[VFSNode]:
        """List contents of a directory."""
        if str(path) in (".", ""):
            # Root - would list all accessible projects
            return

        parsed = self._parse_path(path)

        # Project root
        if parsed["project_key"] and not parsed["section"]:
            yield VFSNode.file(name=".project.json", size=500)
            yield VFSNode.file(name="description.md", size=1000)
            yield VFSNode.file(name="lead.json", size=200)
            yield VFSNode.directory(name="components")
            yield VFSNode.directory(name="versions")
            yield VFSNode.directory(name="epics")
            yield VFSNode.directory(name="issues")
            yield VFSNode.directory(name="sprints")
            yield VFSNode.directory(name="boards")
            return

        # Issues directory
        if parsed["project_key"] and parsed["section"] == "issues" and not parsed["subsection"]:
            yield VFSNode.directory(name="by-type")
            yield VFSNode.directory(name="by-status")
            # Would also yield individual issue directories
            return

        # Issue directory
        if parsed["project_key"] and parsed["section"] == "issues" and parsed["subsection"] and not parsed["item"]:
            yield VFSNode.file(name=".issue.json", size=2000)
            yield VFSNode.file(name="summary.txt", size=200)
            yield VFSNode.file(name="description.md", size=5000)
            yield VFSNode.file(name="type.txt", size=20)
            yield VFSNode.file(name="status.txt", size=20)
            yield VFSNode.file(name="priority.txt", size=20)
            yield VFSNode.file(name="assignee.txt", size=50)
            yield VFSNode.file(name="reporter.txt", size=50)
            yield VFSNode.file(name="labels.json", size=200)
            yield VFSNode.file(name="components.json", size=200)
            yield VFSNode.file(name="fix-versions.json", size=200)
            yield VFSNode.file(name="story-points.txt", size=10)
            yield VFSNode.file(name="time-tracking.json", size=100)
            yield VFSNode.directory(name="subtasks")
            yield VFSNode.directory(name="links")
            yield VFSNode.directory(name="comments")
            yield VFSNode.directory(name="attachments")
            yield VFSNode.directory(name="worklogs")
            yield VFSNode.directory(name="history")
            return

        # Sprints directory
        if parsed["project_key"] and parsed["section"] == "sprints" and not parsed["subsection"]:
            yield VFSNode.directory(name="active")
            # Would also yield sprint directories by ID
            return

        # Sprint root
        if parsed["project_key"] and parsed["section"] == "sprints" and parsed["subsection"] and not parsed["item"]:
            yield VFSNode.file(name=".sprint.json", size=500)
            yield VFSNode.file(name="goal.txt", size=500)
            yield VFSNode.file(name="dates.json", size=200)
            yield VFSNode.file(name="velocity.json", size=100)
            yield VFSNode.directory(name="issues")
            return

        # Boards directory
        if parsed["project_key"] and parsed["section"] == "boards" and not parsed["subsection"]:
            # Would yield board directories by ID
            return

        # Board root
        if parsed["project_key"] and parsed["section"] == "boards" and parsed["subsection"] and not parsed["item"]:
            yield VFSNode.file(name=".board.json", size=1000)
            yield VFSNode.file(name="type.txt", size=20)
            yield VFSNode.directory(name="columns")
            yield VFSNode.directory(name="backlog")
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
        """Write to a file (update issue fields, add comments, log work)."""
        raise VFSPermissionError(path, "write")
