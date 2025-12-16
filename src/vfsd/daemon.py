"""
VFS Daemon - Background process managing virtual filesystems.

The daemon coordinates multiple VFS providers, handles FUSE operations,
and provides a unified interface for mounting application-specific
virtual filesystems.
"""

from __future__ import annotations

import asyncio
import errno
import logging
import os
import signal
import stat
import sys
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, AsyncIterator

from .base import BaseVFSProvider, VFSCapability, VFSNode, VFSNodeType
from .registry import VFSRegistry
from .types import (
    VFSError,
    VFSIOError,
    VFSNotFoundError,
    VFSPath,
    VFSPermissionError,
    VFSStats,
)

logger = logging.getLogger(__name__)


@dataclass
class MountedProvider:
    """A provider mounted at a specific path."""

    provider: BaseVFSProvider
    mount_point: str  # Relative path within VFS root
    mounted_at: datetime = field(default_factory=datetime.now)
    active: bool = True


class VFSDaemon:
    """
    Virtual File System Daemon.

    Manages multiple VFS providers and exposes them through a unified
    interface. Can run as a FUSE filesystem or as an in-memory
    virtual filesystem for programmatic access.

    Usage:
        daemon = VFSDaemon()
        daemon.register_provider("slack", SlackVFS(token="..."))
        daemon.register_provider("github", GitHubVFS(token="..."))

        # Run as FUSE mount
        await daemon.mount("/mnt/vfs")

        # Or use programmatically
        async for node in daemon.list_directory("/slack/workspaces"):
            print(node.name)
    """

    def __init__(self):
        self._providers: dict[str, MountedProvider] = {}
        self._registry = VFSRegistry()
        self._running = False
        self._mount_path: Path | None = None
        self._fuse_process: asyncio.subprocess.Process | None = None
        self._event_loop: asyncio.AbstractEventLoop | None = None

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def mount_path(self) -> Path | None:
        return self._mount_path

    @property
    def providers(self) -> dict[str, MountedProvider]:
        return dict(self._providers)

    def register_provider(
        self,
        name: str,
        provider: BaseVFSProvider,
        mount_point: str | None = None,
    ) -> None:
        """
        Register a VFS provider.

        Args:
            name: Unique identifier (used as directory name)
            provider: The VFS provider instance
            mount_point: Optional custom mount point (defaults to /{name})
        """
        if name in self._providers:
            raise ValueError(f"Provider already registered: {name}")

        mount = mount_point or f"/{name}"
        self._providers[name] = MountedProvider(
            provider=provider,
            mount_point=mount.lstrip("/"),
        )
        logger.info(f"Registered provider: {name} at {mount}")

    def unregister_provider(self, name: str) -> None:
        """Unregister a VFS provider."""
        if name in self._providers:
            self._providers[name].active = False
            del self._providers[name]
            logger.info(f"Unregistered provider: {name}")

    def _resolve_provider(self, path: VFSPath) -> tuple[MountedProvider, VFSPath] | None:
        """
        Resolve a path to its provider and relative path.

        Args:
            path: Absolute path within the VFS

        Returns:
            Tuple of (provider, relative_path) or None if at root
        """
        segments = path.segments()
        if not segments:
            return None

        provider_name = segments[0]
        if provider_name not in self._providers:
            raise VFSNotFoundError(path)

        mounted = self._providers[provider_name]
        if not mounted.active:
            raise VFSNotFoundError(path)

        relative = VFSPath("/".join(segments[1:])) if len(segments) > 1 else VFSPath(".")
        return (mounted, relative)

    async def get_node(self, path: str | VFSPath) -> VFSNode:
        """
        Get node metadata for a path.

        Args:
            path: Absolute path in the VFS

        Returns:
            VFSNode with metadata
        """
        vpath = VFSPath(path) if isinstance(path, str) else path

        # Root directory
        if str(vpath) in ("/", "."):
            return VFSNode.directory(
                name="",
                mtime=datetime.now(),
            )

        resolved = self._resolve_provider(vpath)
        if resolved is None:
            return VFSNode.directory(name="", mtime=datetime.now())

        mounted, relative = resolved
        return await mounted.provider.get_node(relative)

    async def list_directory(self, path: str | VFSPath) -> AsyncIterator[VFSNode]:
        """
        List contents of a directory.

        Args:
            path: Absolute path to directory

        Yields:
            VFSNode for each child
        """
        vpath = VFSPath(path) if isinstance(path, str) else path

        # Root directory - list all providers
        if str(vpath) in ("/", "."):
            for name, mounted in self._providers.items():
                if mounted.active:
                    yield VFSNode.directory(
                        name=name,
                        mtime=mounted.mounted_at,
                        provider=name,
                    )
            return

        resolved = self._resolve_provider(vpath)
        if resolved is None:
            return

        mounted, relative = resolved
        async for node in mounted.provider.list_directory(relative):
            yield node

    async def read_file(
        self,
        path: str | VFSPath,
        offset: int = 0,
        size: int | None = None,
    ) -> bytes:
        """
        Read file contents.

        Args:
            path: Absolute path to file
            offset: Byte offset to start reading
            size: Number of bytes to read (None = all)

        Returns:
            File contents as bytes
        """
        vpath = VFSPath(path) if isinstance(path, str) else path

        resolved = self._resolve_provider(vpath)
        if resolved is None:
            raise VFSNotFoundError(vpath)

        mounted, relative = resolved
        return await mounted.provider.read_file(relative, offset, size)

    async def write_file(
        self,
        path: str | VFSPath,
        data: bytes,
        offset: int = 0,
    ) -> int:
        """
        Write data to a file.

        Args:
            path: Absolute path to file
            data: Data to write
            offset: Byte offset to start writing

        Returns:
            Number of bytes written
        """
        vpath = VFSPath(path) if isinstance(path, str) else path

        resolved = self._resolve_provider(vpath)
        if resolved is None:
            raise VFSPermissionError(vpath, "write")

        mounted, relative = resolved
        if not (mounted.provider.capabilities & VFSCapability.WRITE):
            raise VFSPermissionError(vpath, "write")

        return await mounted.provider.write_file(relative, data, offset)

    async def create(
        self,
        path: str | VFSPath,
        is_directory: bool = False,
        mode: int = 0o644,
    ) -> VFSNode:
        """
        Create a file or directory.

        Args:
            path: Absolute path for new node
            is_directory: True to create directory
            mode: Permission mode

        Returns:
            Created node
        """
        vpath = VFSPath(path) if isinstance(path, str) else path

        resolved = self._resolve_provider(vpath)
        if resolved is None:
            raise VFSPermissionError(vpath, "create")

        mounted, relative = resolved
        if not (mounted.provider.capabilities & VFSCapability.CREATE):
            raise VFSPermissionError(vpath, "create")

        if is_directory:
            return await mounted.provider.create_directory(relative, mode)
        else:
            return await mounted.provider.create_file(relative, mode)

    async def delete(self, path: str | VFSPath) -> None:
        """
        Delete a file or directory.

        Args:
            path: Absolute path to delete
        """
        vpath = VFSPath(path) if isinstance(path, str) else path

        resolved = self._resolve_provider(vpath)
        if resolved is None:
            raise VFSPermissionError(vpath, "delete")

        mounted, relative = resolved
        if not (mounted.provider.capabilities & VFSCapability.DELETE):
            raise VFSPermissionError(vpath, "delete")

        await mounted.provider.delete(relative)

    async def rename(self, old_path: str | VFSPath, new_path: str | VFSPath) -> None:
        """
        Rename/move a file or directory.

        Args:
            old_path: Current path
            new_path: New path
        """
        old_vpath = VFSPath(old_path) if isinstance(old_path, str) else old_path
        new_vpath = VFSPath(new_path) if isinstance(new_path, str) else new_path

        old_resolved = self._resolve_provider(old_vpath)
        new_resolved = self._resolve_provider(new_vpath)

        if old_resolved is None or new_resolved is None:
            raise VFSPermissionError(old_vpath, "rename")

        old_mounted, old_relative = old_resolved
        new_mounted, new_relative = new_resolved

        # Can't rename across providers
        if old_mounted.provider is not new_mounted.provider:
            raise VFSIOError("Cannot rename across providers", old_vpath)

        if not (old_mounted.provider.capabilities & VFSCapability.RENAME):
            raise VFSPermissionError(old_vpath, "rename")

        await old_mounted.provider.rename(old_relative, new_relative)

    # Lifecycle management

    async def initialize(self) -> None:
        """Initialize all providers."""
        for name, mounted in self._providers.items():
            try:
                await mounted.provider.initialize()
                logger.info(f"Initialized provider: {name}")
            except Exception as e:
                logger.error(f"Failed to initialize provider {name}: {e}")
                mounted.active = False

    async def shutdown(self) -> None:
        """Shutdown all providers and unmount."""
        self._running = False

        # Unmount if mounted
        if self._mount_path:
            await self.unmount()

        # Shutdown providers
        for name, mounted in self._providers.items():
            try:
                await mounted.provider.shutdown()
                logger.info(f"Shutdown provider: {name}")
            except Exception as e:
                logger.error(f"Error shutting down provider {name}: {e}")

    async def mount(self, path: str | Path, foreground: bool = False) -> None:
        """
        Mount the VFS at the specified path.

        This creates a FUSE filesystem at the given path. Requires
        FUSE support (macFUSE on macOS, libfuse on Linux).

        Args:
            path: Directory to mount at (must exist)
            foreground: Run in foreground (for debugging)
        """
        mount_path = Path(path)
        if not mount_path.exists():
            mount_path.mkdir(parents=True)

        self._mount_path = mount_path
        self._running = True

        logger.info(f"Mounting VFS at {mount_path}")

        # Initialize providers
        await self.initialize()

        # Start FUSE handler
        # Note: Actual FUSE integration would use pyfuse3 or fusepy
        # For now, we provide an in-process simulation
        logger.info(f"VFS daemon running (simulated mount at {mount_path})")

    async def unmount(self) -> None:
        """Unmount the VFS."""
        if self._mount_path:
            logger.info(f"Unmounting VFS from {self._mount_path}")
            # Actual unmount would use: fusermount -u {path}
            self._mount_path = None
            self._running = False

    @asynccontextmanager
    async def run(self, mount_path: str | Path | None = None):
        """
        Context manager for running the daemon.

        Usage:
            async with daemon.run("/mnt/vfs"):
                # VFS is mounted and running
                ...
            # VFS is automatically unmounted
        """
        try:
            if mount_path:
                await self.mount(mount_path)
            else:
                await self.initialize()
                self._running = True

            yield self

        finally:
            await self.shutdown()


class InMemoryVFSDaemon(VFSDaemon):
    """
    In-memory VFS daemon for testing and programmatic access.

    Doesn't require FUSE support - useful for testing providers
    or accessing VFS data without mounting.
    """

    async def mount(self, path: str | Path, foreground: bool = False) -> None:
        """Simulated mount for in-memory operation."""
        self._mount_path = Path(path)
        self._running = True
        await self.initialize()
        logger.info(f"In-memory VFS daemon running (virtual mount at {path})")
