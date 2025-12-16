"""Figma VFS Provider implementation."""

from __future__ import annotations

from datetime import datetime
from typing import AsyncIterator

from vfsd import CachingVFSProvider, VFSCapability, VFSNode, VFSPath
from vfsd.types import VFSNotFoundError, VFSIsDirectoryError, VFSPermissionError, VFSIOError

from .types import FigmaFile, FigmaPage, FigmaNode, FigmaComponent, FigmaStyle


class FigmaVFS(CachingVFSProvider):
    """Virtual filesystem for Figma files, frames, components, and styles."""

    def __init__(
        self,
        access_token: str,
        oauth_token: str | None = None,
        cache_ttl: int = 300,
        export_scale: int = 2,
        export_format: str = "png",
    ):
        super().__init__(
            name="figma",
            capabilities=VFSCapability.READ | VFSCapability.WRITE | VFSCapability.CREATE | VFSCapability.DELETE,
            cache_ttl_seconds=cache_ttl,
        )
        self._access_token = access_token
        self._oauth_token = oauth_token
        self._export_scale = export_scale
        self._export_format = export_format

    async def initialize(self) -> None:
        """Initialize and verify token."""
        pass

    async def _api_call(self, endpoint: str, method: str = "GET", **kwargs) -> dict:
        """Make a Figma API call."""
        raise NotImplementedError("API call not implemented")

    def _parse_path(self, path: VFSPath) -> dict[str, str | None]:
        """Parse path into components.

        Expected paths:
        - teams/{team-id}
        - teams/{team-id}/projects/{project-id}
        - files/{file-key}
        - files/{file-key}/pages/{page-id}
        - files/{file-key}/pages/{page-id}/nodes/{node-id}
        - files/{file-key}/components/{component-id}
        - files/{file-key}/styles/{style-category}/{style-id}
        - images/{image-hash}.png
        - shared/{file-key}
        - recent/{file-key}
        """
        segments = path.segments()

        if len(segments) == 0:
            return {"section": None}

        section = segments[0]  # teams, files, images, shared, recent, drafts

        return {
            "section": section,
            "team_id": segments[1] if len(segments) >= 2 and section == "teams" else None,
            "file_key": segments[1] if len(segments) >= 2 and section in ("files", "shared", "recent", "drafts") else None,
            "subsection": segments[2] if len(segments) >= 3 else None,
            "item_id": segments[3] if len(segments) >= 4 else None,
            "subitem": segments[4] if len(segments) >= 5 else None,
            "subitem_id": segments[5] if len(segments) >= 6 else None,
            "export_format": segments[6] if len(segments) >= 7 else None,
            "export_file": segments[7] if len(segments) >= 8 else None,
        }

    async def get_node(self, path: VFSPath) -> VFSNode:
        """Get metadata for a path."""
        if str(path) in (".", ""):
            return VFSNode.directory(name="", mtime=datetime.now())

        parsed = self._parse_path(path)

        # Root-level sections
        if parsed["section"] and not parsed["team_id"] and not parsed["file_key"]:
            if parsed["section"] in ("teams", "files", "images", "shared", "recent", "drafts"):
                return VFSNode.directory(name=parsed["section"], mtime=datetime.now())

        # Special files at root
        if parsed["section"] == ".user.json":
            return VFSNode.file(name=".user.json", size=500)

        # Team directory
        if parsed["team_id"] and not parsed["subsection"]:
            return VFSNode.directory(name=parsed["team_id"], mtime=datetime.now())

        # Team metadata files
        if parsed["subsection"] in (".team.json", "name.txt"):
            return VFSNode.file(name=parsed["subsection"], size=300)

        # Team subsections
        if parsed["subsection"] == "projects":
            return VFSNode.directory(name="projects", mtime=datetime.now())

        # File directory
        if parsed["file_key"] and not parsed["subsection"]:
            return VFSNode.directory(name=parsed["file_key"], mtime=datetime.now())

        # File subsections
        if parsed["subsection"] in ("pages", "components", "component_sets", "styles", "comments", "versions", "branches"):
            return VFSNode.directory(name=parsed["subsection"], mtime=datetime.now())

        # File metadata files
        if parsed["subsection"] in (".file.json", "name.txt", "last_modified.txt", "version.txt", "thumbnail.png"):
            return VFSNode.file(name=parsed["subsection"], size=500)

        # Page directory
        if parsed["item_id"] and parsed["subsection"] == "pages":
            return VFSNode.directory(name=parsed["item_id"], mtime=datetime.now())

        # Page metadata files
        if parsed["subitem"] in (".page.json", "name.txt"):
            return VFSNode.file(name=parsed["subitem"], size=500)

        # Nodes directory
        if parsed["subitem"] == "nodes":
            return VFSNode.directory(name="nodes", mtime=datetime.now())

        # Node directory
        if parsed["subitem_id"] and parsed["subitem"] == "nodes":
            return VFSNode.directory(name=parsed["subitem_id"], mtime=datetime.now())

        # Node metadata files
        if parsed["export_format"] in (".node.json", "name.txt", "type.txt", "bounds.json"):
            return VFSNode.file(name=parsed["export_format"], size=500)

        # Node subsections
        if parsed["export_format"] in ("export", "styles", "children"):
            return VFSNode.directory(name=parsed["export_format"], mtime=datetime.now())

        # Export format directories
        if parsed["export_file"] in ("png", "svg", "pdf", "jpg"):
            return VFSNode.directory(name=parsed["export_file"], mtime=datetime.now())

        # Component directory
        if parsed["item_id"] and parsed["subsection"] == "components":
            return VFSNode.directory(name=parsed["item_id"], mtime=datetime.now())

        # Component metadata files
        if parsed["subitem"] in (".component.json", "name.txt", "description.md", "key.txt", "thumbnail.png"):
            return VFSNode.file(name=parsed["subitem"], size=500)

        # Styles directory categories
        if parsed["item_id"] and parsed["subsection"] == "styles":
            if parsed["item_id"] in ("colors", "text", "effects", "grids"):
                return VFSNode.directory(name=parsed["item_id"], mtime=datetime.now())

        # Style directory
        if parsed["subitem"] and parsed["subsection"] == "styles":
            return VFSNode.directory(name=parsed["subitem"], mtime=datetime.now())

        # Style metadata files
        if parsed["export_format"] in (".style.json", "name.txt", "value.json"):
            return VFSNode.file(name=parsed["export_format"], size=500)

        raise VFSNotFoundError(path)

    async def list_directory(self, path: VFSPath) -> AsyncIterator[VFSNode]:
        """List contents of a directory."""
        if str(path) in (".", ""):
            # Root - list top-level sections
            yield VFSNode.file(name=".user.json", size=500)
            yield VFSNode.directory(name="teams")
            yield VFSNode.directory(name="files")
            yield VFSNode.directory(name="images")
            yield VFSNode.directory(name="shared")
            yield VFSNode.directory(name="recent")
            yield VFSNode.directory(name="drafts")
            return

        parsed = self._parse_path(path)

        # Teams section
        if parsed["section"] == "teams" and not parsed["team_id"]:
            # List all teams - would fetch from API
            return

        # Team root
        if parsed["team_id"] and not parsed["subsection"]:
            yield VFSNode.file(name=".team.json", size=500)
            yield VFSNode.file(name="name.txt", size=100)
            yield VFSNode.directory(name="projects")
            return

        # Projects section
        if parsed["subsection"] == "projects" and not parsed["item_id"]:
            # List all projects - would fetch from API
            return

        # Files section
        if parsed["section"] == "files" and not parsed["file_key"]:
            # List all files - would fetch from API
            return

        # File root
        if parsed["file_key"] and not parsed["subsection"]:
            yield VFSNode.file(name=".file.json", size=1000)
            yield VFSNode.file(name="name.txt", size=100)
            yield VFSNode.file(name="last_modified.txt", size=50)
            yield VFSNode.file(name="version.txt", size=50)
            yield VFSNode.file(name="thumbnail.png", size=50000)
            yield VFSNode.directory(name="pages")
            yield VFSNode.directory(name="components")
            yield VFSNode.directory(name="component_sets")
            yield VFSNode.directory(name="styles")
            yield VFSNode.directory(name="comments")
            yield VFSNode.directory(name="versions")
            yield VFSNode.directory(name="branches")
            return

        # Pages section
        if parsed["subsection"] == "pages" and not parsed["item_id"]:
            # List all pages - would fetch from API
            return

        # Page root
        if parsed["item_id"] and parsed["subsection"] == "pages" and not parsed["subitem"]:
            yield VFSNode.file(name=".page.json", size=500)
            yield VFSNode.file(name="name.txt", size=100)
            yield VFSNode.directory(name="nodes")
            return

        # Nodes section
        if parsed["subitem"] == "nodes" and not parsed["subitem_id"]:
            # List all nodes in page - would fetch from API
            return

        # Node root
        if parsed["subitem_id"] and parsed["subitem"] == "nodes" and not parsed["export_format"]:
            yield VFSNode.file(name=".node.json", size=1000)
            yield VFSNode.file(name="name.txt", size=100)
            yield VFSNode.file(name="type.txt", size=50)
            yield VFSNode.file(name="bounds.json", size=200)
            yield VFSNode.directory(name="export")
            yield VFSNode.directory(name="styles")
            yield VFSNode.directory(name="children")
            return

        # Export section
        if parsed["export_format"] == "export" and not parsed["export_file"]:
            yield VFSNode.directory(name="png")
            yield VFSNode.directory(name="svg")
            yield VFSNode.directory(name="pdf")
            yield VFSNode.directory(name="jpg")
            return

        # PNG export
        if parsed["export_file"] == "png":
            yield VFSNode.file(name="1x.png", size=50000)
            yield VFSNode.file(name="2x.png", size=100000)
            yield VFSNode.file(name="3x.png", size=150000)
            return

        # Components section
        if parsed["subsection"] == "components" and not parsed["item_id"]:
            # List all components - would fetch from API
            return

        # Component root
        if parsed["item_id"] and parsed["subsection"] == "components" and not parsed["subitem"]:
            yield VFSNode.file(name=".component.json", size=1000)
            yield VFSNode.file(name="name.txt", size=100)
            yield VFSNode.file(name="description.md", size=500)
            yield VFSNode.file(name="key.txt", size=50)
            yield VFSNode.file(name="thumbnail.png", size=50000)
            return

        # Styles section
        if parsed["subsection"] == "styles" and not parsed["item_id"]:
            yield VFSNode.directory(name="colors")
            yield VFSNode.directory(name="text")
            yield VFSNode.directory(name="effects")
            yield VFSNode.directory(name="grids")
            return

        # Style category
        if parsed["item_id"] and parsed["subsection"] == "styles" and not parsed["subitem"]:
            # List all styles in category - would fetch from API
            return

        # Style root
        if parsed["subitem"] and parsed["subsection"] == "styles" and not parsed["export_format"]:
            yield VFSNode.file(name=".style.json", size=500)
            yield VFSNode.file(name="name.txt", size=100)
            yield VFSNode.file(name="value.json", size=500)
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
        """Write to a file (add comments, resolve comments, etc.)."""
        raise VFSPermissionError(path, "write")
