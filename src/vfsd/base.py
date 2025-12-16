"""
Base VFS provider interface.

All VFS implementations inherit from VFSProvider and implement the
required methods to expose their domain objects as files and directories.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, IntFlag, auto
from typing import TYPE_CHECKING, Any, AsyncIterator, Protocol, runtime_checkable

from .types import VFSPath, VFSStats, VFSNotFoundError, FileHandle


class VFSNodeType(Enum):
    """Type of VFS node."""

    FILE = "file"
    DIRECTORY = "directory"
    SYMLINK = "symlink"


class VFSCapability(IntFlag):
    """Capabilities of a VFS provider."""

    NONE = 0
    READ = auto()  # Can read files
    WRITE = auto()  # Can write/modify files
    CREATE = auto()  # Can create new files/directories
    DELETE = auto()  # Can delete files/directories
    RENAME = auto()  # Can rename/move files
    SYMLINKS = auto()  # Supports symbolic links
    XATTR = auto()  # Supports extended attributes
    WATCH = auto()  # Can watch for changes
    SEARCH = auto()  # Supports server-side search

    # Common combinations
    READ_ONLY = READ
    READ_WRITE = READ | WRITE | CREATE | DELETE | RENAME
    FULL = READ | WRITE | CREATE | DELETE | RENAME | SYMLINKS | XATTR | WATCH | SEARCH


@dataclass
class VFSNode:
    """
    Represents a node in the virtual filesystem.

    A node can be a file, directory, or symlink. It holds metadata
    and provides access to content through the provider.
    """

    name: str
    node_type: VFSNodeType
    stats: VFSStats
    provider_data: dict[str, Any] = field(default_factory=dict)

    # For symlinks
    symlink_target: str | None = None

    # Cached content (optional, for small files)
    _cached_content: bytes | None = field(default=None, repr=False)

    @property
    def is_file(self) -> bool:
        return self.node_type == VFSNodeType.FILE

    @property
    def is_directory(self) -> bool:
        return self.node_type == VFSNodeType.DIRECTORY

    @property
    def is_symlink(self) -> bool:
        return self.node_type == VFSNodeType.SYMLINK

    @classmethod
    def file(
        cls,
        name: str,
        size: int = 0,
        mtime: datetime | None = None,
        content: bytes | None = None,
        writable: bool = False,
        **provider_data,
    ) -> VFSNode:
        """Create a file node."""
        actual_size = len(content) if content else size
        return cls(
            name=name,
            node_type=VFSNodeType.FILE,
            stats=VFSStats.for_file(actual_size, mtime, writable=writable),
            provider_data=provider_data,
            _cached_content=content,
        )

    @classmethod
    def directory(
        cls,
        name: str,
        mtime: datetime | None = None,
        writable: bool = False,
        **provider_data,
    ) -> VFSNode:
        """Create a directory node."""
        return cls(
            name=name,
            node_type=VFSNodeType.DIRECTORY,
            stats=VFSStats.for_directory(mtime, writable=writable),
            provider_data=provider_data,
        )

    @classmethod
    def symlink(
        cls,
        name: str,
        target: str,
        mtime: datetime | None = None,
        **provider_data,
    ) -> VFSNode:
        """Create a symlink node."""
        return cls(
            name=name,
            node_type=VFSNodeType.SYMLINK,
            stats=VFSStats.for_symlink(len(target), mtime),
            symlink_target=target,
            provider_data=provider_data,
        )


@runtime_checkable
class VFSProvider(Protocol):
    """
    Protocol for VFS providers.

    Implement this protocol to create a virtual filesystem for any
    application or service. The provider translates paths into
    domain-specific operations.
    """

    @property
    def name(self) -> str:
        """Unique identifier for this provider (e.g., 'slack', 'github')."""
        ...

    @property
    def capabilities(self) -> VFSCapability:
        """What operations this provider supports."""
        ...

    async def get_node(self, path: VFSPath) -> VFSNode:
        """
        Get metadata for a node at the given path.

        Args:
            path: Path relative to this provider's root

        Returns:
            VFSNode with metadata

        Raises:
            VFSNotFoundError: If path doesn't exist
        """
        ...

    async def list_directory(self, path: VFSPath) -> AsyncIterator[VFSNode]:
        """
        List contents of a directory.

        Args:
            path: Path to directory relative to provider root

        Yields:
            VFSNode for each child

        Raises:
            VFSNotFoundError: If path doesn't exist
            VFSNotDirectoryError: If path is not a directory
        """
        ...

    async def read_file(
        self,
        path: VFSPath,
        offset: int = 0,
        size: int | None = None,
    ) -> bytes:
        """
        Read file contents.

        Args:
            path: Path to file
            offset: Byte offset to start reading
            size: Number of bytes to read (None = all)

        Returns:
            File contents as bytes

        Raises:
            VFSNotFoundError: If path doesn't exist
            VFSIsDirectoryError: If path is a directory
        """
        ...


class BaseVFSProvider(ABC):
    """
    Abstract base class for VFS providers with common functionality.

    Inherit from this class for a more convenient implementation
    with sensible defaults and helper methods.
    """

    def __init__(self, name: str, capabilities: VFSCapability = VFSCapability.READ):
        self._name = name
        self._capabilities = capabilities
        self._open_files: dict[FileHandle, tuple[VFSPath, int]] = {}  # handle -> (path, position)
        self._next_handle: int = 1

    @property
    def name(self) -> str:
        return self._name

    @property
    def capabilities(self) -> VFSCapability:
        return self._capabilities

    @abstractmethod
    async def get_node(self, path: VFSPath) -> VFSNode:
        """Subclasses must implement node retrieval."""
        ...

    @abstractmethod
    async def list_directory(self, path: VFSPath) -> AsyncIterator[VFSNode]:
        """Subclasses must implement directory listing."""
        ...

    @abstractmethod
    async def read_file(
        self,
        path: VFSPath,
        offset: int = 0,
        size: int | None = None,
    ) -> bytes:
        """Subclasses must implement file reading."""
        ...

    # Optional write operations (default to raising permission errors)

    async def write_file(
        self,
        path: VFSPath,
        data: bytes,
        offset: int = 0,
    ) -> int:
        """Write data to file. Override if provider supports writing."""
        from .types import VFSPermissionError

        raise VFSPermissionError(path, "write")

    async def create_file(self, path: VFSPath, mode: int = 0o644) -> VFSNode:
        """Create a new file. Override if provider supports creation."""
        from .types import VFSPermissionError

        raise VFSPermissionError(path, "create")

    async def create_directory(self, path: VFSPath, mode: int = 0o755) -> VFSNode:
        """Create a new directory. Override if provider supports creation."""
        from .types import VFSPermissionError

        raise VFSPermissionError(path, "mkdir")

    async def delete(self, path: VFSPath) -> None:
        """Delete a file or directory. Override if provider supports deletion."""
        from .types import VFSPermissionError

        raise VFSPermissionError(path, "delete")

    async def rename(self, old_path: VFSPath, new_path: VFSPath) -> None:
        """Rename/move a file. Override if provider supports renaming."""
        from .types import VFSPermissionError

        raise VFSPermissionError(old_path, "rename")

    async def read_symlink(self, path: VFSPath) -> str:
        """Read symlink target. Override if provider supports symlinks."""
        from .types import VFSPermissionError

        raise VFSPermissionError(path, "readlink")

    async def create_symlink(self, path: VFSPath, target: str) -> VFSNode:
        """Create a symlink. Override if provider supports symlinks."""
        from .types import VFSPermissionError

        raise VFSPermissionError(path, "symlink")

    # Extended attributes (optional)

    async def get_xattr(self, path: VFSPath, name: str) -> bytes:
        """Get extended attribute. Override if provider supports xattrs."""
        from .types import VFSNotFoundError

        raise VFSNotFoundError(f"{path}:{name}")

    async def set_xattr(self, path: VFSPath, name: str, value: bytes) -> None:
        """Set extended attribute. Override if provider supports xattrs."""
        from .types import VFSPermissionError

        raise VFSPermissionError(path, "setxattr")

    async def list_xattr(self, path: VFSPath) -> list[str]:
        """List extended attributes. Override if provider supports xattrs."""
        return []

    # File handle management

    def _allocate_handle(self, path: VFSPath) -> FileHandle:
        """Allocate a file handle."""
        handle = FileHandle(self._next_handle)
        self._next_handle += 1
        self._open_files[handle] = (path, 0)
        return handle

    def _release_handle(self, handle: FileHandle) -> None:
        """Release a file handle."""
        self._open_files.pop(handle, None)

    def _get_handle_path(self, handle: FileHandle) -> VFSPath | None:
        """Get path for a file handle."""
        if entry := self._open_files.get(handle):
            return entry[0]
        return None

    # Lifecycle hooks

    async def initialize(self) -> None:
        """Called when provider is registered. Override for setup."""
        pass

    async def shutdown(self) -> None:
        """Called when provider is unregistered. Override for cleanup."""
        pass

    async def refresh(self) -> None:
        """Called to refresh cached data. Override if provider caches."""
        pass


class CachingVFSProvider(BaseVFSProvider):
    """
    VFS provider with built-in caching layer.

    Subclass this for providers that benefit from caching
    API responses or computed structures.
    """

    def __init__(
        self,
        name: str,
        capabilities: VFSCapability = VFSCapability.READ,
        cache_ttl_seconds: int = 300,
    ):
        super().__init__(name, capabilities)
        self._cache: dict[str, tuple[Any, datetime]] = {}
        self._cache_ttl = cache_ttl_seconds

    def _cache_key(self, prefix: str, path: VFSPath) -> str:
        """Generate cache key."""
        return f"{prefix}:{path}"

    def _get_cached(self, key: str) -> Any | None:
        """Get cached value if not expired."""
        if entry := self._cache.get(key):
            value, timestamp = entry
            age = (datetime.now() - timestamp).total_seconds()
            if age < self._cache_ttl:
                return value
            del self._cache[key]
        return None

    def _set_cached(self, key: str, value: Any) -> None:
        """Cache a value."""
        self._cache[key] = (value, datetime.now())

    def _invalidate(self, key: str | None = None) -> None:
        """Invalidate cache entry or entire cache."""
        if key is None:
            self._cache.clear()
        else:
            self._cache.pop(key, None)

    async def refresh(self) -> None:
        """Clear the cache."""
        self._invalidate()
