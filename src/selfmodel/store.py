"""
StateStore: Composable time-indexed state management.

The StateStore is the main interface for accessing the self-model state.
It composes TimeIndex instances for each node type and provides:
- Time-indexed access: store[time].node_name -> value
- Latest state: store.now.node_name -> latest value
- Append: store.node_name.append(value)
"""

from dataclasses import dataclass, field
from datetime import datetime, UTC
from pathlib import Path
from typing import TYPE_CHECKING, Generic, TypeVar

from timeindex import TimeIndex, Timestamped, LookupPolicy

from .profile import Profile
from .models import (
    # Core
    SelfConstitution,
    SelfModel,
    WorldModel,
    # Affect
    AffectCore,
    AffectLabels,
    AffectAppraisal,
    # Cognition
    ContextNow,
    BeliefsNow,
    CognitionWorkspace,
    # Memory
    MemoryRetrievalPolicy,
    # Planning
    GoalsActive,
    OptionsSet,
    PlanActive,
    # Social
    SocialContext,
    AttachmentState,
)


# Node definitions: name -> (model_class, filename)
NODES = {
    # Core (high stability)
    "self_constitution": (SelfConstitution, "self_constitution.jsonl"),
    "self_model": (SelfModel, "self_model.jsonl"),
    "world_model": (WorldModel, "world_model.jsonl"),
    # Affect (variable stability)
    "affect_core": (AffectCore, "affect_core.jsonl"),
    "affect_labels": (AffectLabels, "affect_labels.jsonl"),
    "affect_appraisal": (AffectAppraisal, "affect_appraisal.jsonl"),
    # Cognition (low-medium stability)
    "context_now": (ContextNow, "context_now.jsonl"),
    "beliefs_now": (BeliefsNow, "beliefs_now.jsonl"),
    "cognition_workspace": (CognitionWorkspace, "cognition_workspace.jsonl"),
    # Memory (high stability for policy)
    "memory_retrieval_policy": (MemoryRetrievalPolicy, "memory_retrieval_policy.jsonl"),
    # Planning (low-medium stability)
    "goals_active": (GoalsActive, "goals_active.jsonl"),
    "options_set": (OptionsSet, "options_set.jsonl"),
    "plan_active": (PlanActive, "plan_active.jsonl"),
    # Social (variable stability)
    "social_context": (SocialContext, "social_context.jsonl"),
    "attachment_state": (AttachmentState, "attachment_state.jsonl"),
}


T = TypeVar("T")


class NodeAccessor(Generic[T]):
    """
    Accessor for a single node's TimeIndex.

    Provides both direct TimeIndex access and convenience methods.
    """

    def __init__(self, index: TimeIndex[T]):
        self._index = index

    def append(self, value: T, t: datetime | float | None = None) -> Timestamped[T]:
        """Append a new value."""
        return self._index.append(value, t)

    def latest(self) -> Timestamped[T] | None:
        """Get the latest entry."""
        return self._index.latest()

    @property
    def value(self) -> T | None:
        """Get the latest value (convenience for store.node.value)."""
        entry = self._index.latest()
        return entry.v if entry else None

    def __getitem__(self, t: datetime | float) -> T:
        """Get value at time."""
        return self._index[t]

    def get(self, t: datetime | float, policy: LookupPolicy | None = None, default: T | None = None) -> T | None:
        """Get value at time with policy and default."""
        return self._index.get(t, policy, default)

    def get_entry(self, t: datetime | float, policy: LookupPolicy | None = None) -> Timestamped[T]:
        """Get timestamped entry at time."""
        return self._index.get_entry(t, policy)

    def range(self, start: datetime | float, end: datetime | float):
        """Iterate over time range."""
        return self._index.range(start, end)

    def all(self):
        """Iterate over all entries."""
        return self._index.all()

    def __len__(self) -> int:
        return len(self._index)

    def __bool__(self) -> bool:
        return bool(self._index)


class StateSnapshot:
    """
    A snapshot of state at a specific time.

    Provides attribute access to node values at that time.
    Usage: snapshot.affect_core.valence
    """

    def __init__(self, store: "StateStore", t: datetime | float):
        self._store = store
        self._t = t

    def __getattr__(self, name: str):
        if name.startswith("_"):
            raise AttributeError(name)
        if name not in NODES:
            raise AttributeError(f"Unknown node: {name}")
        accessor = getattr(self._store, name)
        return accessor[self._t]


class NowSnapshot:
    """
    A snapshot of the latest state for each node.

    Provides attribute access to the latest value of each node.
    Usage: store.now.affect_core.valence
    """

    def __init__(self, store: "StateStore"):
        self._store = store

    def __getattr__(self, name: str):
        if name.startswith("_"):
            raise AttributeError(name)
        if name not in NODES:
            raise AttributeError(f"Unknown node: {name}")
        accessor = getattr(self._store, name)
        return accessor.value


class StateStore:
    """
    Main interface for self-model state.

    Composes TimeIndex instances for each node and provides:
    - Attribute access to nodes: store.affect_core
    - Time-indexed snapshots: store[time].affect_core
    - Latest state: store.now.affect_core

    Example:
        store = StateStore(Profile.parse("jacob-heavy-v1"))

        # Append new state
        store.affect_core.append(AffectCore(valence=0.5, arousal=0.3))

        # Get latest
        print(store.now.affect_core.valence)

        # Get at specific time
        print(store[yesterday].affect_core.valence)
    """

    def __init__(
        self,
        profile: Profile | str,
        base_dir: Path | str = "state",
        policy: LookupPolicy = "nearest_prev",
    ):
        if isinstance(profile, str):
            profile = Profile.parse(profile)

        self._profile = profile
        self._base_dir = Path(base_dir)
        self._policy = policy
        self._state_dir = profile.state_dir(self._base_dir)

        # Initialize TimeIndex for each node
        self._indices: dict[str, TimeIndex] = {}
        for name, (model_class, filename) in NODES.items():
            path = self._state_dir / filename
            self._indices[name] = TimeIndex(path, model_class, policy)

    @property
    def profile(self) -> Profile:
        """The profile this store is for."""
        return self._profile

    @property
    def state_dir(self) -> Path:
        """The directory containing state files."""
        return self._state_dir

    @property
    def now(self) -> NowSnapshot:
        """Access the latest state for all nodes."""
        return NowSnapshot(self)

    def __getitem__(self, t: datetime | float) -> StateSnapshot:
        """Get a snapshot of state at a specific time."""
        return StateSnapshot(self, t)

    def __getattr__(self, name: str) -> NodeAccessor:
        """Get a node accessor by name."""
        if name.startswith("_"):
            raise AttributeError(name)
        if name not in NODES:
            raise AttributeError(f"Unknown node: {name}")
        return NodeAccessor(self._indices[name])

    def __repr__(self) -> str:
        return f"StateStore({self._profile.key!r}, {self._state_dir})"


def open_store(
    profile: Profile | str,
    base_dir: Path | str = "state",
    policy: LookupPolicy = "nearest_prev",
) -> StateStore:
    """
    Open a StateStore for a profile.

    Convenience function for creating a StateStore.

    Args:
        profile: Profile instance or key string (e.g., "jacob-heavy-v1")
        base_dir: Base directory for state files
        policy: Default lookup policy for time queries

    Returns:
        StateStore instance
    """
    return StateStore(profile, base_dir, policy)


def import_state(
    store: StateStore,
    data: dict,
    overwrite: bool = False,
) -> dict[str, int]:
    """
    Import state from a dictionary (e.g., from JSON export).

    Args:
        store: The StateStore to import into
        data: Dictionary with node_name -> model_data mapping
        overwrite: If True, clear existing state before import

    Returns:
        Dictionary mapping node names to number of entries imported
    """
    imported = {}

    for node_name, node_data in data.items():
        if node_name == "profile":
            continue  # Skip metadata
        if node_name not in NODES:
            continue  # Skip unknown nodes

        model_class, _ = NODES[node_name]
        accessor = getattr(store, node_name)

        # Parse the model
        if isinstance(node_data, dict):
            model = model_class(**node_data)
            accessor.append(model)
            imported[node_name] = 1
        elif isinstance(node_data, list):
            # List of entries (from history export)
            for entry in node_data:
                model = model_class(**entry)
                accessor.append(model)
            imported[node_name] = len(node_data)

    return imported


def export_state(
    store: StateStore,
    include_history: bool = False,
) -> dict:
    """
    Export state to a dictionary.

    Args:
        store: The StateStore to export from
        include_history: If True, include all historical entries

    Returns:
        Dictionary with node_name -> model_data mapping
    """
    export = {"profile": store.profile.key}

    for node_name in NODES:
        accessor = getattr(store, node_name)

        if include_history:
            # Export all entries
            entries = list(accessor.all())
            if entries:
                export[node_name] = [
                    {"t": e.t, **e.v.model_dump()}
                    for e in entries
                ]
        else:
            # Export only latest
            value = accessor.value
            if value:
                export[node_name] = value.model_dump()

    return export


def clone_profile(
    source_store: StateStore,
    target_profile: Profile | str,
    base_dir: Path | str = "state",
    include_history: bool = True,
) -> StateStore:
    """
    Clone a profile to a new profile key.

    Args:
        source_store: The source StateStore
        target_profile: The target profile key
        base_dir: Base directory for state files
        include_history: If True, copy all history; if False, only latest state

    Returns:
        The new StateStore
    """
    if isinstance(target_profile, str):
        target_profile = Profile.parse(target_profile)

    target_store = StateStore(target_profile, base_dir)

    for node_name in NODES:
        source_accessor = getattr(source_store, node_name)
        target_accessor = getattr(target_store, node_name)

        if include_history:
            # Copy all entries
            for entry in source_accessor.all():
                target_accessor.append(entry.v, entry.t)
        else:
            # Copy only latest
            value = source_accessor.value
            if value:
                target_accessor.append(value)

    return target_store
