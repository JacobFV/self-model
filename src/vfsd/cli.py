"""
VFS Daemon CLI.

Command-line interface for managing the vfsd daemon and registered providers.

Usage:
    vfsd start [--mount PATH] [--foreground]
    vfsd stop
    vfsd status
    vfsd register <provider> [--config KEY=VALUE]...
    vfsd unregister <provider>
    vfsd list [--available]
    vfsd enable <provider>
    vfsd disable <provider>
    vfsd config <provider> [KEY=VALUE]...
    vfsd refresh [<provider>]
"""

from __future__ import annotations

import argparse
import asyncio
import importlib
import json
import logging
import os
import signal
import sys
from pathlib import Path
from typing import Any

from .config import (
    VFSDConfig,
    ProviderConfig,
    KNOWN_PROVIDERS,
    get_config_dir,
    get_config_path,
)
from .daemon import VFSDaemon

logger = logging.getLogger(__name__)


def setup_logging(level: str = "INFO", log_file: str | None = None) -> None:
    """Configure logging."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    handlers: list[logging.Handler] = [logging.StreamHandler()]

    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=handlers,
    )


def parse_config_args(args: list[str]) -> dict[str, Any]:
    """Parse KEY=VALUE config arguments."""
    config = {}
    for arg in args:
        if "=" in arg:
            key, value = arg.split("=", 1)
            # Try to parse as JSON for complex values
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                pass  # Keep as string
            config[key] = value
    return config


def load_provider_class(module_path: str):
    """
    Load a provider class from a module path.

    Supports:
    - Package names: "vfs_slack" -> import vfs_slack and get default provider
    - Module paths: "vfs_slack:SlackVFS" -> import and get specific class
    - Local paths: "./my_provider" -> add to path and import
    """
    # Handle local paths
    if module_path.startswith("./") or module_path.startswith("/"):
        path = Path(module_path).resolve()
        if path.is_dir():
            sys.path.insert(0, str(path.parent))
            module_name = path.name
        else:
            sys.path.insert(0, str(path.parent))
            module_name = path.stem
    else:
        module_name = module_path

    # Handle class specification
    if ":" in module_name:
        module_name, class_name = module_name.split(":", 1)
    else:
        class_name = None

    # Import module
    module = importlib.import_module(module_name)

    # Get provider class
    if class_name:
        return getattr(module, class_name)
    elif hasattr(module, "Provider"):
        return module.Provider
    elif hasattr(module, "get_provider_class"):
        return module.get_provider_class()
    else:
        # Look for a class that looks like a provider
        for name in dir(module):
            obj = getattr(module, name)
            if (
                isinstance(obj, type)
                and name.endswith("VFS")
                and hasattr(obj, "get_node")
            ):
                return obj
        raise ImportError(f"Could not find provider class in {module_name}")


# CLI Commands


def cmd_start(args: argparse.Namespace) -> int:
    """Start the vfsd daemon."""
    config = VFSDConfig.load()

    if args.mount:
        config.daemon.mount_path = args.mount
    if args.foreground:
        config.daemon.foreground = True
    if args.log_level:
        config.daemon.log_level = args.log_level

    setup_logging(config.daemon.log_level, config.daemon.log_file)

    daemon = VFSDaemon()

    # Load enabled providers
    for prov_config in config.get_enabled_providers():
        try:
            provider_class = load_provider_class(prov_config.module)
            provider = provider_class(**prov_config.config)
            mount_point = prov_config.mount_point or f"/{prov_config.name}"
            daemon.register_provider(prov_config.name, provider, mount_point)
            logger.info(f"Loaded provider: {prov_config.name}")
        except Exception as e:
            logger.error(f"Failed to load provider {prov_config.name}: {e}")

    # Run daemon
    async def run():
        async with daemon.run(config.daemon.mount_path):
            logger.info(f"vfsd running at {config.daemon.mount_path}")
            # Wait for shutdown signal
            stop_event = asyncio.Event()

            def handle_signal():
                stop_event.set()

            loop = asyncio.get_event_loop()
            for sig in (signal.SIGTERM, signal.SIGINT):
                loop.add_signal_handler(sig, handle_signal)

            await stop_event.wait()
            logger.info("Shutting down...")

    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass

    return 0


def cmd_stop(args: argparse.Namespace) -> int:
    """Stop the vfsd daemon."""
    config = VFSDConfig.load()
    pid_file = config.daemon.pid_file or str(get_config_dir() / "vfsd.pid")

    if not Path(pid_file).exists():
        print("vfsd is not running")
        return 1

    with open(pid_file) as f:
        pid = int(f.read().strip())

    try:
        os.kill(pid, signal.SIGTERM)
        print(f"Sent SIGTERM to vfsd (pid {pid})")
        Path(pid_file).unlink(missing_ok=True)
        return 0
    except ProcessLookupError:
        print("vfsd process not found")
        Path(pid_file).unlink(missing_ok=True)
        return 1


def cmd_status(args: argparse.Namespace) -> int:
    """Show vfsd status."""
    config = VFSDConfig.load()

    print("vfsd Status")
    print("=" * 40)
    print(f"Config file: {get_config_path()}")
    print(f"Mount path: {config.daemon.mount_path}")
    print()

    providers = config.list_providers()
    if providers:
        print(f"Registered providers ({len(providers)}):")
        for p in providers:
            status = "enabled" if p.enabled else "disabled"
            auto = " [auto-mount]" if p.auto_mount else ""
            print(f"  - {p.name}: {p.module} ({status}){auto}")
    else:
        print("No providers registered")
        print()
        print("Register a provider with:")
        print("  vfsd register <provider-name>")
        print()
        print("Available providers:")
        for name, info in list(KNOWN_PROVIDERS.items())[:5]:
            print(f"  - {name}: {info['description']}")
        print(f"  ... and {len(KNOWN_PROVIDERS) - 5} more (vfsd list --available)")

    return 0


def cmd_register(args: argparse.Namespace) -> int:
    """Register a new provider."""
    config = VFSDConfig.load()
    provider_name = args.provider

    # Check if already registered
    if provider_name in config.providers:
        print(f"Provider '{provider_name}' is already registered")
        print(f"Use 'vfsd config {provider_name}' to update configuration")
        return 1

    # Determine module
    if args.module:
        module = args.module
    elif provider_name in KNOWN_PROVIDERS:
        module = KNOWN_PROVIDERS[provider_name]["module"]
    else:
        print(f"Unknown provider: {provider_name}")
        print()
        print("Specify module with --module or use a known provider:")
        for name in KNOWN_PROVIDERS:
            print(f"  - {name}")
        return 1

    # Parse config
    provider_config = parse_config_args(args.config or [])

    # Check required config for known providers
    if provider_name in KNOWN_PROVIDERS:
        info = KNOWN_PROVIDERS[provider_name]
        required = info.get("required_config", [])
        missing = [k for k in required if k not in provider_config]
        if missing:
            print(f"Missing required configuration for {provider_name}:")
            for key in missing:
                print(f"  --config {key}=<value>")
            return 1

    # Register
    config.register_provider(
        name=provider_name,
        module=module,
        config=provider_config,
        enabled=not args.disabled,
        auto_mount=args.auto_mount,
        mount_point=args.mount_point,
    )
    config.save()

    print(f"Registered provider: {provider_name}")
    if provider_config:
        print(f"Configuration: {json.dumps(provider_config, indent=2)}")

    return 0


def cmd_unregister(args: argparse.Namespace) -> int:
    """Unregister a provider."""
    config = VFSDConfig.load()

    if config.unregister_provider(args.provider):
        config.save()
        print(f"Unregistered provider: {args.provider}")
        return 0
    else:
        print(f"Provider not found: {args.provider}")
        return 1


def cmd_list(args: argparse.Namespace) -> int:
    """List providers."""
    if args.available:
        print("Available VFS Providers")
        print("=" * 60)
        for name, info in KNOWN_PROVIDERS.items():
            print(f"\n{name}")
            print(f"  Package: {info['package']}")
            print(f"  {info['description']}")
            if info.get("required_config"):
                print(f"  Required: {', '.join(info['required_config'])}")
        return 0

    config = VFSDConfig.load()
    providers = config.list_providers()

    if not providers:
        print("No providers registered")
        print("Use 'vfsd list --available' to see available providers")
        return 0

    print("Registered Providers")
    print("=" * 60)
    for p in providers:
        status = "✓" if p.enabled else "✗"
        auto = " [auto]" if p.auto_mount else ""
        print(f"\n{status} {p.name}{auto}")
        print(f"  Module: {p.module}")
        if p.mount_point:
            print(f"  Mount: {p.mount_point}")
        if p.config:
            # Mask sensitive values
            safe_config = {
                k: "***" if "token" in k.lower() or "password" in k.lower() or "secret" in k.lower() else v
                for k, v in p.config.items()
            }
            print(f"  Config: {json.dumps(safe_config)}")

    return 0


def cmd_enable(args: argparse.Namespace) -> int:
    """Enable a provider."""
    config = VFSDConfig.load()
    provider = config.get_provider(args.provider)

    if not provider:
        print(f"Provider not found: {args.provider}")
        return 1

    provider.enabled = True
    config.save()
    print(f"Enabled provider: {args.provider}")
    return 0


def cmd_disable(args: argparse.Namespace) -> int:
    """Disable a provider."""
    config = VFSDConfig.load()
    provider = config.get_provider(args.provider)

    if not provider:
        print(f"Provider not found: {args.provider}")
        return 1

    provider.enabled = False
    config.save()
    print(f"Disabled provider: {args.provider}")
    return 0


def cmd_config(args: argparse.Namespace) -> int:
    """Configure a provider."""
    config = VFSDConfig.load()
    provider = config.get_provider(args.provider)

    if not provider:
        print(f"Provider not found: {args.provider}")
        return 1

    if not args.values:
        # Show current config
        print(f"Configuration for {args.provider}:")
        if provider.config:
            for k, v in provider.config.items():
                # Mask sensitive values
                if "token" in k.lower() or "password" in k.lower() or "secret" in k.lower():
                    v = "***"
                print(f"  {k}: {v}")
        else:
            print("  (no configuration)")
        return 0

    # Update config
    new_config = parse_config_args(args.values)
    provider.config.update(new_config)
    config.save()

    print(f"Updated configuration for {args.provider}:")
    for k, v in new_config.items():
        print(f"  {k}: {v}")

    return 0


def cmd_refresh(args: argparse.Namespace) -> int:
    """Refresh provider cache."""
    # This would communicate with a running daemon
    print("Refresh command requires a running daemon")
    print("Use 'vfsd start' to start the daemon first")
    return 1


def main(argv: list[str] | None = None) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="vfsd",
        description="Virtual File System Daemon - Mount APIs as filesystems",
    )
    parser.add_argument(
        "--version", action="version", version="%(prog)s 0.1.0"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # start
    start_parser = subparsers.add_parser("start", help="Start the daemon")
    start_parser.add_argument("--mount", "-m", help="Mount path")
    start_parser.add_argument(
        "--foreground", "-f", action="store_true", help="Run in foreground"
    )
    start_parser.add_argument("--log-level", "-l", help="Log level")
    start_parser.set_defaults(func=cmd_start)

    # stop
    stop_parser = subparsers.add_parser("stop", help="Stop the daemon")
    stop_parser.set_defaults(func=cmd_stop)

    # status
    status_parser = subparsers.add_parser("status", help="Show daemon status")
    status_parser.set_defaults(func=cmd_status)

    # register
    register_parser = subparsers.add_parser("register", help="Register a provider")
    register_parser.add_argument("provider", help="Provider name")
    register_parser.add_argument("--module", help="Python module path")
    register_parser.add_argument(
        "--config", "-c", action="append", help="Config KEY=VALUE"
    )
    register_parser.add_argument(
        "--disabled", action="store_true", help="Register but don't enable"
    )
    register_parser.add_argument(
        "--auto-mount", action="store_true", help="Auto-mount on daemon start"
    )
    register_parser.add_argument("--mount-point", help="Custom mount point")
    register_parser.set_defaults(func=cmd_register)

    # unregister
    unregister_parser = subparsers.add_parser(
        "unregister", help="Unregister a provider"
    )
    unregister_parser.add_argument("provider", help="Provider name")
    unregister_parser.set_defaults(func=cmd_unregister)

    # list
    list_parser = subparsers.add_parser("list", help="List providers")
    list_parser.add_argument(
        "--available", "-a", action="store_true", help="Show available providers"
    )
    list_parser.set_defaults(func=cmd_list)

    # enable
    enable_parser = subparsers.add_parser("enable", help="Enable a provider")
    enable_parser.add_argument("provider", help="Provider name")
    enable_parser.set_defaults(func=cmd_enable)

    # disable
    disable_parser = subparsers.add_parser("disable", help="Disable a provider")
    disable_parser.add_argument("provider", help="Provider name")
    disable_parser.set_defaults(func=cmd_disable)

    # config
    config_parser = subparsers.add_parser("config", help="Configure a provider")
    config_parser.add_argument("provider", help="Provider name")
    config_parser.add_argument("values", nargs="*", help="KEY=VALUE pairs")
    config_parser.set_defaults(func=cmd_config)

    # refresh
    refresh_parser = subparsers.add_parser("refresh", help="Refresh provider cache")
    refresh_parser.add_argument("provider", nargs="?", help="Provider name (all if omitted)")
    refresh_parser.set_defaults(func=cmd_refresh)

    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
