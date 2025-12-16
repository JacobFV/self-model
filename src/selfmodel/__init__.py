"""
selfmodel: A system for building transferable cognitive self-models.

This module implements a state graph for representing and updating
a cognitive self-model. Each node in the graph is a Pydantic model
stored in a time-indexed JSONL file.

Core concepts:
- Profile: Parametrized configuration (who, tier, version)
- StateStore: Main interface for accessing/updating state
- Models: Pydantic models for each node type

Example:
    from selfmodel import StateStore, Profile
    from selfmodel.models import AffectCore, SelfConstitution

    # Open a store for a profile
    store = StateStore(Profile.parse("jacob-heavy-v1"))

    # Append new state
    store.affect_core.append(AffectCore(valence=0.5, arousal=0.3))

    # Access latest state
    print(store.now.affect_core.valence)

    # Access state at a specific time
    from datetime import datetime, UTC
    print(store[datetime.now(UTC)].affect_core.valence)
"""

from .profile import Profile, get_preset, PRESETS
from .store import StateStore, open_store, NODES, import_state, export_state, clone_profile
from .events import EventBus, Event, EventType
from .bootstrap import bootstrap_profile, create_minimal_profile, DEFAULT_CONSTITUTION
from .query import StateQuery, query

__all__ = [
    # Profile
    "Profile",
    "get_preset",
    "PRESETS",
    # Store
    "StateStore",
    "open_store",
    "NODES",
    "import_state",
    "export_state",
    "clone_profile",
    # Events
    "EventBus",
    "Event",
    "EventType",
    # Bootstrap
    "bootstrap_profile",
    "create_minimal_profile",
    "DEFAULT_CONSTITUTION",
    # Query
    "StateQuery",
    "query",
]
