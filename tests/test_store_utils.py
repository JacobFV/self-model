"""
Tests for store utility functions: export, import, clone.
"""

import json
from pathlib import Path

import pytest

from selfmodel import (
    bootstrap_profile,
    open_store,
    export_state,
    import_state,
    clone_profile,
)
from selfmodel.models import AffectCore, GoalsActive, Goal


class TestExportState:
    def test_export_latest_only(self, tmp_path: Path):
        store = bootstrap_profile("export-test-heavy-v1", base_dir=tmp_path)

        # Add some data
        store.affect_core.append(AffectCore(valence=0.5, arousal=0.3))

        export = export_state(store, include_history=False)

        assert export["profile"] == "export-test-heavy-v1"
        assert "self_constitution" in export
        assert "affect_core" in export
        # Latest only should have dict, not list
        assert isinstance(export["affect_core"], dict)

    def test_export_with_history(self, tmp_path: Path):
        store = bootstrap_profile("export-hist-heavy-v1", base_dir=tmp_path)

        # Add multiple entries
        store.affect_core.append(AffectCore(valence=0.1))
        store.affect_core.append(AffectCore(valence=0.5))
        store.affect_core.append(AffectCore(valence=0.9))

        export = export_state(store, include_history=True)

        # With history should have list
        assert isinstance(export["affect_core"], list)
        # Bootstrap adds 1, then we add 3 = 4 total
        assert len(export["affect_core"]) == 4

    def test_export_empty_nodes_excluded(self, tmp_path: Path):
        store = open_store("empty-export-heavy-v1", base_dir=tmp_path)

        # Don't bootstrap - just open empty

        export = export_state(store, include_history=False)

        # Should only have profile key
        assert export["profile"] == "empty-export-heavy-v1"
        # No nodes exported since all empty
        assert len(export) == 1


class TestImportState:
    def test_import_basic(self, tmp_path: Path):
        # Create source data
        data = {
            "profile": "import-source-heavy-v1",
            "affect_core": {
                "valence": 0.7,
                "arousal": 0.4,
                "dominance": 0.5,
                "tension": 0.2,
                "social_safety": 0.8,
                "body_load": 0.1,
            },
        }

        store = open_store("import-test-heavy-v1", base_dir=tmp_path)
        imported = import_state(store, data)

        assert "affect_core" in imported
        assert imported["affect_core"] == 1
        assert store.now.affect_core.valence == 0.7

    def test_import_skips_unknown_nodes(self, tmp_path: Path):
        data = {
            "profile": "source",
            "unknown_node": {"foo": "bar"},
            "affect_core": {"valence": 0.5, "arousal": 0.3},
        }

        store = open_store("import-unknown-heavy-v1", base_dir=tmp_path)
        imported = import_state(store, data)

        assert "unknown_node" not in imported
        assert "affect_core" in imported

    def test_import_list_entries(self, tmp_path: Path):
        # Import history as list
        data = {
            "profile": "source",
            "affect_core": [
                {"valence": 0.1, "arousal": 0.1},
                {"valence": 0.5, "arousal": 0.3},
                {"valence": 0.9, "arousal": 0.5},
            ],
        }

        store = open_store("import-list-heavy-v1", base_dir=tmp_path)
        imported = import_state(store, data)

        assert imported["affect_core"] == 3
        assert len(list(store.affect_core.all())) == 3

    def test_round_trip(self, tmp_path: Path):
        # Create and populate a store
        store1 = bootstrap_profile("roundsrc-heavy-v1", base_dir=tmp_path)
        store1.affect_core.append(AffectCore(valence=0.8, arousal=0.6))
        store1.goals_active.append(GoalsActive(
            goals=[Goal(description="Test goal", priority=0.9)],
            primary_goal="Test goal",
        ))

        # Export
        export = export_state(store1, include_history=False)

        # Import into new store
        store2 = open_store("rounddst-heavy-v1", base_dir=tmp_path)
        import_state(store2, export)

        # Verify
        assert store2.now.affect_core.valence == 0.8
        assert store2.now.goals_active.primary_goal == "Test goal"


class TestCloneProfile:
    def test_clone_with_history(self, tmp_path: Path):
        # Create and populate source
        source = bootstrap_profile("clone-src-heavy-v1", base_dir=tmp_path)
        source.affect_core.append(AffectCore(valence=0.2))
        source.affect_core.append(AffectCore(valence=0.5))
        source.affect_core.append(AffectCore(valence=0.8))

        # Clone
        target = clone_profile(source, "clone-dst-heavy-v1", base_dir=tmp_path)

        # History should be preserved
        src_entries = list(source.affect_core.all())
        dst_entries = list(target.affect_core.all())
        assert len(dst_entries) == len(src_entries)

        # Values should match
        for s, d in zip(src_entries, dst_entries):
            assert s.v.valence == d.v.valence

    def test_clone_latest_only(self, tmp_path: Path):
        # Create and populate source
        source = bootstrap_profile("clsrc-heavy-v1", base_dir=tmp_path)
        source.affect_core.append(AffectCore(valence=0.1))
        source.affect_core.append(AffectCore(valence=0.9))

        # Clone without history
        target = clone_profile(
            source,
            "cldst-heavy-v1",
            base_dir=tmp_path,
            include_history=False,
        )

        # Should only have one entry
        dst_entries = list(target.affect_core.all())
        assert len(dst_entries) == 1
        assert dst_entries[0].v.valence == 0.9

    def test_clone_different_directories(self, tmp_path: Path):
        source_dir = tmp_path / "source"
        target_dir = tmp_path / "target"
        source_dir.mkdir()
        target_dir.mkdir()

        source = bootstrap_profile("crossdir-heavy-v1", base_dir=source_dir)

        target = clone_profile(source, "crosscopy-heavy-v1", base_dir=target_dir)

        assert target.state_dir == target_dir / "crosscopy-heavy-v1"
        assert target.now.self_constitution is not None
