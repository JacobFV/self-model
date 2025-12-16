"""
VFS Provider Registry.

Manages registration and discovery of VFS providers.
"""

from __future__ import annotations

import importlib
import pkgutil
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Type

if TYPE_CHECKING:
    from .base import VFSProvider, BaseVFSProvider


@dataclass
class ProviderInfo:
    """Metadata about a registered provider."""

    name: str
    provider_class: Type[BaseVFSProvider]
    description: str
    required_config: list[str] = field(default_factory=list)
    optional_config: list[str] = field(default_factory=list)
    version: str = "0.1.0"


class VFSRegistry:
    """
    Registry for VFS providers.

    Supports both manual registration and automatic discovery
    of providers from installed packages.
    """

    _instance: VFSRegistry | None = None
    _providers: dict[str, ProviderInfo]
    _factories: dict[str, Callable[..., BaseVFSProvider]]

    def __new__(cls) -> VFSRegistry:
        """Singleton pattern for global registry."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._providers = {}
            cls._instance._factories = {}
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset the registry (mainly for testing)."""
        cls._instance = None

    def register(
        self,
        name: str,
        provider_class: Type[BaseVFSProvider],
        description: str = "",
        required_config: list[str] | None = None,
        optional_config: list[str] | None = None,
        factory: Callable[..., BaseVFSProvider] | None = None,
    ) -> None:
        """
        Register a VFS provider.

        Args:
            name: Unique identifier for the provider
            provider_class: The provider class
            description: Human-readable description
            required_config: List of required config keys
            optional_config: List of optional config keys
            factory: Optional factory function for creating instances
        """
        self._providers[name] = ProviderInfo(
            name=name,
            provider_class=provider_class,
            description=description,
            required_config=required_config or [],
            optional_config=optional_config or [],
        )

        if factory:
            self._factories[name] = factory
        else:
            self._factories[name] = provider_class

    def unregister(self, name: str) -> None:
        """Remove a provider from the registry."""
        self._providers.pop(name, None)
        self._factories.pop(name, None)

    def get_info(self, name: str) -> ProviderInfo | None:
        """Get provider info by name."""
        return self._providers.get(name)

    def list_providers(self) -> list[ProviderInfo]:
        """List all registered providers."""
        return list(self._providers.values())

    def create_provider(self, name: str, **config) -> BaseVFSProvider:
        """
        Create a provider instance.

        Args:
            name: Provider name
            **config: Configuration for the provider

        Returns:
            Configured provider instance

        Raises:
            KeyError: If provider not registered
            ValueError: If required config missing
        """
        if name not in self._providers:
            raise KeyError(f"Provider not registered: {name}")

        info = self._providers[name]

        # Validate required config
        missing = [key for key in info.required_config if key not in config]
        if missing:
            raise ValueError(f"Missing required config for {name}: {missing}")

        factory = self._factories[name]
        return factory(**config)

    def discover_providers(self, package_name: str | None = None) -> list[str]:
        """
        Discover and register providers from installed packages.

        Discovery methods (in order):
        1. Entry points: Packages with "vfsd.providers" entry point
        2. Naming convention: Installed packages named "vfs_*" or "vfs-*"
        3. Explicit package: If package_name provided, search that package

        Args:
            package_name: Optional specific package to search

        Returns:
            List of discovered provider names
        """
        discovered = []

        # Method 1: Entry points (Python 3.9+)
        try:
            from importlib.metadata import entry_points

            eps = entry_points()
            # Handle both old and new entry_points API
            if hasattr(eps, "select"):
                vfs_eps = eps.select(group="vfsd.providers")
            else:
                vfs_eps = eps.get("vfsd.providers", [])

            for ep in vfs_eps:
                try:
                    provider_class = ep.load()
                    if hasattr(provider_class, "name"):
                        self._factories[ep.name] = provider_class
                        discovered.append(ep.name)
                except Exception:
                    continue
        except ImportError:
            pass

        # Method 2: Naming convention (vfs_* or vfs-* packages)
        try:
            from importlib.metadata import distributions

            for dist in distributions():
                name = dist.metadata.get("Name", "")
                if name.startswith("vfs-") or name.startswith("vfs_"):
                    # Convert package name to module name
                    module_name = name.replace("-", "_")
                    try:
                        module = importlib.import_module(module_name)
                        if hasattr(module, "register"):
                            module.register(self)
                            # Extract provider name from package name
                            provider_name = name.replace("vfs-", "").replace("vfs_", "")
                            if provider_name not in discovered:
                                discovered.append(provider_name)
                    except Exception:
                        continue
        except ImportError:
            pass

        # Method 3: Explicit package search
        if package_name:
            try:
                package = importlib.import_module(package_name)
                if hasattr(package, "__path__"):
                    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
                        try:
                            module = importlib.import_module(f"{package_name}.{module_name}")
                            if hasattr(module, "register"):
                                module.register(self)
                                discovered.append(module_name)
                        except Exception:
                            continue
            except ImportError:
                pass

        return discovered

    def discover_local_providers(self, search_paths: list[str] | None = None) -> list[str]:
        """
        Discover providers from local filesystem paths.

        Useful for development or custom providers not installed as packages.

        Args:
            search_paths: List of paths to search (default: ~/.config/vfsd/providers)

        Returns:
            List of discovered provider names
        """
        import sys
        from pathlib import Path

        discovered = []

        if search_paths is None:
            from .config import get_providers_dir
            search_paths = [str(get_providers_dir())]

        for search_path in search_paths:
            path = Path(search_path)
            if not path.exists():
                continue

            for item in path.iterdir():
                if item.is_dir() and (item / "__init__.py").exists():
                    # Add to path and try to import
                    if str(path) not in sys.path:
                        sys.path.insert(0, str(path))
                    try:
                        module = importlib.import_module(item.name)
                        if hasattr(module, "register"):
                            module.register(self)
                            discovered.append(item.name)
                    except Exception:
                        continue

        return discovered


# Decorator for easy provider registration
def vfs_provider(
    name: str,
    description: str = "",
    required_config: list[str] | None = None,
    optional_config: list[str] | None = None,
):
    """
    Decorator to register a VFS provider class.

    Usage:
        @vfs_provider("slack", description="Slack workspace VFS", required_config=["token"])
        class SlackVFS(BaseVFSProvider):
            ...
    """

    def decorator(cls: Type[BaseVFSProvider]) -> Type[BaseVFSProvider]:
        registry = VFSRegistry()
        registry.register(
            name=name,
            provider_class=cls,
            description=description,
            required_config=required_config,
            optional_config=optional_config,
        )
        return cls

    return decorator
