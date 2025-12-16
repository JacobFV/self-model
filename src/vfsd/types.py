"""
Core types for vfsd.
"""

from __future__ import annotations

import os
import stat
from dataclasses import dataclass, field
from datetime import datetime
from enum import IntFlag, auto
from pathlib import PurePosixPath
from typing import Any, NewType


class VFSPath(PurePosixPath):
    """
    A virtual filesystem path.

    Provides path manipulation utilities specific to VFS operations,
    including segment extraction for routing to appropriate providers.
    """

    @property
    def provider_name(self) -> str | None:
        """Extract the provider name (first path segment after root)."""
        parts = self.parts
        if len(parts) > 1:
            return parts[1]
        return None

    @property
    def provider_path(self) -> VFSPath:
        """Get the path relative to the provider root."""
        parts = self.parts
        if len(parts) > 2:
            return VFSPath(*parts[2:])
        return VFSPath(".")

    def segments(self) -> list[str]:
        """Get all path segments excluding root."""
        parts = self.parts
        if parts and parts[0] == "/":
            return list(parts[1:])
        return list(parts)


@dataclass
class VFSStats:
    """
    File/directory statistics for a VFS node.

    Mirrors the stat structure but with VFS-specific defaults.
    """

    size: int = 0
    atime: datetime = field(default_factory=datetime.now)
    mtime: datetime = field(default_factory=datetime.now)
    ctime: datetime = field(default_factory=datetime.now)

    # Permission modes
    mode: int = stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH  # 0o444 by default (read-only)

    # Ownership
    uid: int = field(default_factory=os.getuid)
    gid: int = field(default_factory=os.getgid)

    # Link count (1 for files, 2+ for directories)
    nlink: int = 1

    # Block size for efficient I/O
    blksize: int = 4096

    # Device and inode (virtual)
    dev: int = 0
    ino: int = 0

    # Additional metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def for_file(
        cls,
        size: int,
        mtime: datetime | None = None,
        writable: bool = False,
        executable: bool = False,
        **kwargs,
    ) -> VFSStats:
        """Create stats for a regular file."""
        mode = stat.S_IFREG | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH
        if writable:
            mode |= stat.S_IWUSR
        if executable:
            mode |= stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH

        return cls(
            size=size,
            mode=mode,
            mtime=mtime or datetime.now(),
            nlink=1,
            **kwargs,
        )

    @classmethod
    def for_directory(
        cls,
        mtime: datetime | None = None,
        writable: bool = False,
        **kwargs,
    ) -> VFSStats:
        """Create stats for a directory."""
        mode = stat.S_IFDIR | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        if writable:
            mode |= stat.S_IWUSR

        return cls(
            size=4096,
            mode=mode,
            mtime=mtime or datetime.now(),
            nlink=2,  # . and ..
            **kwargs,
        )

    @classmethod
    def for_symlink(
        cls,
        target_length: int,
        mtime: datetime | None = None,
        **kwargs,
    ) -> VFSStats:
        """Create stats for a symbolic link."""
        return cls(
            size=target_length,
            mode=stat.S_IFLNK | 0o777,
            mtime=mtime or datetime.now(),
            nlink=1,
            **kwargs,
        )


class VFSError(Exception):
    """Base exception for VFS operations."""

    errno: int = 5  # EIO by default

    def __init__(self, message: str, path: str | VFSPath | None = None):
        self.path = VFSPath(path) if path else None
        super().__init__(f"{message}: {path}" if path else message)


class VFSNotFoundError(VFSError):
    """Raised when a path does not exist."""

    errno: int = 2  # ENOENT

    def __init__(self, path: str | VFSPath):
        super().__init__("No such file or directory", path)


class VFSPermissionError(VFSError):
    """Raised when operation is not permitted."""

    errno: int = 13  # EACCES

    def __init__(self, path: str | VFSPath, operation: str = "access"):
        super().__init__(f"Permission denied ({operation})", path)


class VFSIOError(VFSError):
    """Raised when an I/O error occurs."""

    errno: int = 5  # EIO

    def __init__(self, message: str, path: str | VFSPath | None = None):
        super().__init__(message, path)


class VFSExistsError(VFSError):
    """Raised when a path already exists."""

    errno: int = 17  # EEXIST

    def __init__(self, path: str | VFSPath):
        super().__init__("File exists", path)


class VFSNotEmptyError(VFSError):
    """Raised when trying to remove non-empty directory."""

    errno: int = 39  # ENOTEMPTY

    def __init__(self, path: str | VFSPath):
        super().__init__("Directory not empty", path)


class VFSIsDirectoryError(VFSError):
    """Raised when a file operation is attempted on a directory."""

    errno: int = 21  # EISDIR

    def __init__(self, path: str | VFSPath):
        super().__init__("Is a directory", path)


class VFSNotDirectoryError(VFSError):
    """Raised when a directory operation is attempted on a file."""

    errno: int = 20  # ENOTDIR

    def __init__(self, path: str | VFSPath):
        super().__init__("Not a directory", path)


# Type aliases for clarity
FileHandle = NewType("FileHandle", int)
DirHandle = NewType("DirHandle", int)
