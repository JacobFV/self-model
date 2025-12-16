"""
Tests for the selfmodel module.
"""

from datetime import datetime, UTC
from pathlib import Path

import pytest

from selfmodel import Profile, StateStore, open_store
from selfmodel.models import (
    AffectCore,
    SelfConstitution,
    Value,
    ContextNow,
    GoalsActive,
    Goal,
)


class TestProfile:
    def test_create_basic(self):
        p = Profile(name="jacob", tier="heavy", version="v1")
        assert p.key == "jacob-heavy-v1"

    def test_create_with_persona(self):
        p = Profile(name="jacob", persona="scholar", tier="heavy", version="v1")
        assert p.key == "jacob-scholar-heavy-v1"

    def test_parse_basic(self):
        p = Profile.parse("jacob-heavy-v1")
        assert p.name == "jacob"
        assert p.persona is None
        assert p.tier == "heavy"
        assert p.version == "v1"

    def test_parse_with_persona(self):
        p = Profile.parse("jacob-scholar-heavy-v1")
        assert p.name == "jacob"
        assert p.persona == "scholar"
        assert p.tier == "heavy"
        assert p.version == "v1"

    def test_parse_invalid(self):
        with pytest.raises(ValueError):
            Profile.parse("invalid")

        with pytest.raises(ValueError):
            Profile.parse("too-many-parts-here-oops")

    def test_state_dir(self):
        p = Profile(name="jacob", tier="heavy", version="v1")
        assert p.state_dir() == Path("state/jacob-heavy-v1")
        assert p.state_dir("custom") == Path("custom/jacob-heavy-v1")

    def test_with_tier(self):
        p = Profile(name="jacob", persona="scholar", tier="heavy", version="v1")
        p2 = p.with_tier("light")
        assert p2.key == "jacob-scholar-light-v1"
        assert p.key == "jacob-scholar-heavy-v1"  # Original unchanged

    def test_with_version(self):
        p = Profile(name="jacob", tier="heavy", version="v1")
        p2 = p.with_version("v2")
        assert p2.key == "jacob-heavy-v2"

    def test_with_persona(self):
        p = Profile(name="jacob", tier="heavy", version="v1")
        p2 = p.with_persona("engineer")
        assert p2.key == "jacob-engineer-heavy-v1"

    def test_hyphen_in_component_rejected(self):
        with pytest.raises(ValueError):
            Profile(name="jacob-smith", tier="heavy", version="v1")

    def test_str_repr(self):
        p = Profile(name="jacob", tier="heavy", version="v1")
        assert str(p) == "jacob-heavy-v1"
        assert "jacob-heavy-v1" in repr(p)


class TestStateStore:
    def test_create_store(self, tmp_path: Path):
        store = StateStore(
            Profile(name="test", tier="light", version="v1"),
            base_dir=tmp_path,
        )
        assert store.profile.key == "test-light-v1"
        assert store.state_dir == tmp_path / "test-light-v1"

    def test_create_store_from_string(self, tmp_path: Path):
        store = StateStore("test-light-v1", base_dir=tmp_path)
        assert store.profile.key == "test-light-v1"

    def test_append_and_retrieve(self, tmp_path: Path):
        store = StateStore("test-light-v1", base_dir=tmp_path)

        # Append affect state
        store.affect_core.append(AffectCore(valence=0.5, arousal=0.3))

        # Retrieve latest
        assert store.now.affect_core is not None
        assert store.now.affect_core.valence == 0.5
        assert store.now.affect_core.arousal == 0.3

    def test_multiple_appends(self, tmp_path: Path):
        store = StateStore("test-light-v1", base_dir=tmp_path)

        store.affect_core.append(AffectCore(valence=0.1, arousal=0.1))
        store.affect_core.append(AffectCore(valence=0.5, arousal=0.5))
        store.affect_core.append(AffectCore(valence=0.9, arousal=0.9))

        # Latest should be the last one
        assert store.now.affect_core.valence == 0.9

        # Should have 3 entries
        assert len(store.affect_core) == 3

    def test_time_indexed_access(self, tmp_path: Path):
        store = StateStore("test-light-v1", base_dir=tmp_path)

        t1 = 1000.0
        t2 = 2000.0
        t3 = 3000.0

        store.affect_core.append(AffectCore(valence=0.1, arousal=0.1), t=t1)
        store.affect_core.append(AffectCore(valence=0.5, arousal=0.5), t=t2)
        store.affect_core.append(AffectCore(valence=0.9, arousal=0.9), t=t3)

        # Access at specific time
        assert store[t2].affect_core.valence == 0.5

        # Access between times (nearest_prev)
        assert store[2500.0].affect_core.valence == 0.5

    def test_complex_model(self, tmp_path: Path):
        store = StateStore("test-light-v1", base_dir=tmp_path)

        constitution = SelfConstitution(
            values=[
                Value(name="truth", description="Pursue accurate beliefs", weight=0.9),
                Value(name="growth", description="Continuous improvement", weight=0.8),
            ],
            terminal_goals=["understand reality", "build useful things"],
            nonnegotiables=["never deceive myself"],
            identity_claims=["I am a builder", "I am a learner"],
        )

        store.self_constitution.append(constitution)

        loaded = store.now.self_constitution
        assert loaded is not None
        assert len(loaded.values) == 2
        assert loaded.values[0].name == "truth"
        assert loaded.terminal_goals[0] == "understand reality"

    def test_persistence(self, tmp_path: Path):
        # Write with first store
        store1 = StateStore("test-light-v1", base_dir=tmp_path)
        store1.affect_core.append(AffectCore(valence=0.7, arousal=0.4))

        # Read with second store
        store2 = StateStore("test-light-v1", base_dir=tmp_path)
        assert store2.now.affect_core.valence == 0.7

    def test_multiple_nodes(self, tmp_path: Path):
        store = StateStore("test-light-v1", base_dir=tmp_path)

        store.affect_core.append(AffectCore(valence=0.5, arousal=0.5))
        store.context_now.append(ContextNow(
            location="office",
            current_task="coding",
        ))
        store.goals_active.append(GoalsActive(
            goals=[Goal(description="finish feature", priority=0.8)],
            primary_goal="finish feature",
        ))

        assert store.now.affect_core.valence == 0.5
        assert store.now.context_now.location == "office"
        assert store.now.goals_active.primary_goal == "finish feature"

    def test_unknown_node_raises(self, tmp_path: Path):
        store = StateStore("test-light-v1", base_dir=tmp_path)

        with pytest.raises(AttributeError):
            _ = store.nonexistent_node

    def test_node_accessor_methods(self, tmp_path: Path):
        store = StateStore("test-light-v1", base_dir=tmp_path)

        t1 = 1000.0
        t2 = 2000.0

        store.affect_core.append(AffectCore(valence=0.3, arousal=0.3), t=t1)
        store.affect_core.append(AffectCore(valence=0.7, arousal=0.7), t=t2)

        # latest()
        latest = store.affect_core.latest()
        assert latest.v.valence == 0.7

        # value property
        assert store.affect_core.value.valence == 0.7

        # get() with default
        default = AffectCore(valence=0.0, arousal=0.0)
        result = store.affect_core.get(500.0, default=default)
        assert result.valence == 0.0

        # range()
        entries = list(store.affect_core.range(t1, t2))
        assert len(entries) == 2

        # all()
        all_entries = list(store.affect_core.all())
        assert len(all_entries) == 2


class TestOpenStore:
    def test_open_store_function(self, tmp_path: Path):
        store = open_store("jacob-heavy-v1", base_dir=tmp_path)
        assert store.profile.key == "jacob-heavy-v1"

    def test_open_store_with_profile(self, tmp_path: Path):
        profile = Profile(name="jacob", persona="scholar", tier="light", version="v1")
        store = open_store(profile, base_dir=tmp_path)
        assert store.profile.key == "jacob-scholar-light-v1"
