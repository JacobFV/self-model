"""Notion VFS Provider implementation."""

from __future__ import annotations

from datetime import datetime
from typing import AsyncIterator

from vfsd import CachingVFSProvider, VFSCapability, VFSNode, VFSPath
from vfsd.types import VFSNotFoundError, VFSIsDirectoryError, VFSPermissionError, VFSIOError

from .types import NotionPage, NotionDatabase, NotionBlock


class NotionVFS(CachingVFSProvider):
    """Virtual filesystem for Notion workspaces, pages, and databases."""

    def __init__(
        self,
        token: str,
        cache_ttl: int = 300,
        render_markdown: bool = True,
    ):
        super().__init__(
            name="notion",
            capabilities=VFSCapability.READ | VFSCapability.WRITE | VFSCapability.CREATE | VFSCapability.DELETE,
            cache_ttl_seconds=cache_ttl,
        )
        self._token = token
        self._render_markdown = render_markdown

    async def initialize(self) -> None:
        """Initialize and verify token."""
        pass

    async def _api_call(self, endpoint: str, method: str = "GET", **kwargs) -> dict:
        """Make a Notion API call."""
        raise NotImplementedError("API call not implemented")

    def _parse_path(self, path: VFSPath) -> dict[str, str | None]:
        """Parse path into components: workspace, section, item, etc."""
        segments = path.segments()
        return {
            "workspace": segments[0] if len(segments) >= 1 else None,
            "section": segments[1] if len(segments) >= 2 else None,  # pages, databases, search
            "item_id": segments[2] if len(segments) >= 3 else None,  # page-id, database-id
            "subsection": segments[3] if len(segments) >= 4 else None,  # content, properties, blocks, etc.
            "subitem": segments[4] if len(segments) >= 5 else None,
            "subsubitem": segments[5] if len(segments) >= 6 else None,
        }

    async def get_node(self, path: VFSPath) -> VFSNode:
        """Get metadata for a path."""
        if str(path) in (".", ""):
            return VFSNode.directory(name="", mtime=datetime.now())

        parsed = self._parse_path(path)

        # Workspace root
        if parsed["workspace"] and not parsed["section"]:
            return VFSNode.directory(name=parsed["workspace"], mtime=datetime.now())

        # Top-level sections
        if parsed["section"] in ("pages", "databases", "search", "templates", "shared"):
            return VFSNode.directory(name=parsed["section"], mtime=datetime.now())

        # Page directory
        if parsed["section"] == "pages" and parsed["item_id"] and not parsed["subsection"]:
            return VFSNode.directory(name=parsed["item_id"], mtime=datetime.now())

        # Page files
        if parsed["section"] == "pages" and parsed["item_id"] and parsed["subsection"]:
            if parsed["subsection"] in (".page.json", "title.txt", "icon.txt", "cover.url", "content.md", "content.json"):
                return VFSNode.file(name=parsed["subsection"], size=500)
            if parsed["subsection"] in ("properties", "children", "comments", "blocks"):
                return VFSNode.directory(name=parsed["subsection"], mtime=datetime.now())

        # Database directory
        if parsed["section"] == "databases" and parsed["item_id"] and not parsed["subsection"]:
            return VFSNode.directory(name=parsed["item_id"], mtime=datetime.now())

        # Database files/directories
        if parsed["section"] == "databases" and parsed["item_id"] and parsed["subsection"]:
            if parsed["subsection"] in (".database.json", "title.txt", "description.md", "schema.json"):
                return VFSNode.file(name=parsed["subsection"], size=500)
            if parsed["subsection"] in ("views", "rows", "query"):
                return VFSNode.directory(name=parsed["subsection"], mtime=datetime.now())

        raise VFSNotFoundError(path)

    async def list_directory(self, path: VFSPath) -> AsyncIterator[VFSNode]:
        """List contents of a directory."""
        if str(path) in (".", ""):
            # Root - would list workspaces
            return

        parsed = self._parse_path(path)

        # Workspace root
        if parsed["workspace"] and not parsed["section"]:
            yield VFSNode.file(name=".workspace.json", size=500)
            yield VFSNode.directory(name="pages")
            yield VFSNode.directory(name="databases")
            yield VFSNode.directory(name="search")
            yield VFSNode.directory(name="templates")
            yield VFSNode.directory(name="shared")
            return

        # Pages directory
        if parsed["section"] == "pages" and not parsed["item_id"]:
            # Would list all accessible pages
            return

        # Page root
        if parsed["section"] == "pages" and parsed["item_id"] and not parsed["subsection"]:
            yield VFSNode.file(name=".page.json", size=500)
            yield VFSNode.file(name="title.txt", size=100)
            yield VFSNode.file(name="icon.txt", size=10)
            yield VFSNode.file(name="cover.url", size=100)
            yield VFSNode.file(name="content.md", size=5000)
            yield VFSNode.file(name="content.json", size=10000)
            yield VFSNode.directory(name="properties")
            yield VFSNode.directory(name="children")
            yield VFSNode.directory(name="comments")
            yield VFSNode.directory(name="blocks")
            return

        # Databases directory
        if parsed["section"] == "databases" and not parsed["item_id"]:
            # Would list all accessible databases
            return

        # Database root
        if parsed["section"] == "databases" and parsed["item_id"] and not parsed["subsection"]:
            yield VFSNode.file(name=".database.json", size=1000)
            yield VFSNode.file(name="title.txt", size=100)
            yield VFSNode.file(name="description.md", size=500)
            yield VFSNode.file(name="schema.json", size=2000)
            yield VFSNode.directory(name="views")
            yield VFSNode.directory(name="rows")
            yield VFSNode.directory(name="query")
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
        """Write to a file (update page content, properties, etc.)."""
        raise VFSPermissionError(path, "write")
