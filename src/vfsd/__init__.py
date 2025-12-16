"""
vfsd - Virtual File System Daemon

A framework for creating application-specific virtual filesystems that project
API abstractions onto file-like interfaces. Mount Slack channels as directories,
GitHub repos as file trees, databases as queryable paths, etc.

## CLI Usage

    # Start the daemon
    vfsd start --mount /mnt/vfs

    # Register a provider extension
    vfsd register vfs-slack
    vfsd register vfs-github --token $GITHUB_TOKEN

    # List registered providers
    vfsd list

    # Unregister a provider
    vfsd unregister vfs-slack

    # Check status
    vfsd status

## Programmatic Usage

    from vfsd import VFSDaemon, VFSProvider, VFSNode

    daemon = VFSDaemon()
    daemon.load_config()  # Load from ~/.config/vfsd/config.json

    await daemon.mount("/mnt/vfs")

## Extension Development

Create a new VFS provider as a Python package with entry point:

    # pyproject.toml
    [project.entry-points."vfsd.providers"]
    slack = "vfs_slack:SlackVFS"

Or register via CLI config:

    vfsd register ./my-custom-vfs --name custom
"""

from .base import VFSProvider, VFSNode, VFSNodeType, VFSCapability, BaseVFSProvider, CachingVFSProvider
from .daemon import VFSDaemon, InMemoryVFSDaemon
from .registry import VFSRegistry, vfs_provider, ProviderInfo
from .config import VFSDConfig, ProviderConfig
from .cli import main as cli_main
from .types import (
    VFSPath,
    VFSStats,
    VFSError,
    VFSPermissionError,
    VFSNotFoundError,
    VFSIOError,
)

__all__ = [
    # Core classes
    "VFSProvider",
    "VFSNode",
    "VFSNodeType",
    "VFSCapability",
    "BaseVFSProvider",
    "CachingVFSProvider",
    "VFSDaemon",
    "InMemoryVFSDaemon",
    "VFSRegistry",
    "vfs_provider",
    "ProviderInfo",
    # Config
    "VFSDConfig",
    "ProviderConfig",
    # CLI
    "cli_main",
    # Types
    "VFSPath",
    "VFSStats",
    # Errors
    "VFSError",
    "VFSPermissionError",
    "VFSNotFoundError",
    "VFSIOError",
]

__version__ = "0.1.0"
