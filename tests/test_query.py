"""
Tests for query interface.
"""

from pathlib import Path

import pytest

from selfmodel import bootstrap_profile, open_store, query
from selfmodel.models import AffectCore, GoalsActive, Goal


class TestConstitutionQueries:
    def test_top_values(self, tmp_path: Path):
        store = bootstrap_profile("qtest-heavy-v1", base_dir=tmp_path)
        q = query(store)

        result = q.top_values(3)

        assert result.found
        assert len(result.value) == 3
        assert "truth" in result.value

    def test_terminal_goals(self, tmp_path: Path):
        store = bootstrap_profile("qtest2-heavy-v1", base_dir=tmp_path)
        q = query(store)

        result = q.terminal_goals()

        assert result.found
        assert len(result.value) > 0

    def test_nonnegotiables(self, tmp_path: Path):
        store = bootstrap_profile("qtest3-heavy-v1", base_dir=tmp_path)
        q = query(store)

        result = q.nonnegotiables()

        assert result.found
        assert len(result.value) > 0

    def test_has_value_exists(self, tmp_path: Path):
        store = bootstrap_profile("qtest4-heavy-v1", base_dir=tmp_path)
        q = query(store)

        result = q.has_value("truth")

        assert result.found
        assert result.value == 0.9  # Default weight for truth

    def test_has_value_missing(self, tmp_path: Path):
        store = bootstrap_profile("qtest5-heavy-v1", base_dir=tmp_path)
        q = query(store)

        result = q.has_value("nonexistent")

        assert not result.found


class TestAffectQueries:
    def test_current_affect(self, tmp_path: Path):
        store = bootstrap_profile("affq1-heavy-v1", base_dir=tmp_path)
        store.affect_core.append(AffectCore(valence=0.7, arousal=0.4, tension=0.2))
        q = query(store)

        result = q.current_affect()

        assert result.found
        assert result.value["valence"] == 0.7

    def test_is_positive(self, tmp_path: Path):
        store = bootstrap_profile("affq2-heavy-v1", base_dir=tmp_path)
        store.affect_core.append(AffectCore(valence=0.5))
        q = query(store)

        result = q.is_positive()

        assert result.found
        assert result.value is True

    def test_is_stressed(self, tmp_path: Path):
        store = bootstrap_profile("affq3-heavy-v1", base_dir=tmp_path)
        store.affect_core.append(AffectCore(tension=0.8, arousal=0.7))
        q = query(store)

        result = q.is_stressed()

        assert result.found
        assert result.value is True

    def test_affect_trend(self, tmp_path: Path):
        store = bootstrap_profile("affq4-heavy-v1", base_dir=tmp_path)
        # Add improving trend
        store.affect_core.append(AffectCore(valence=-0.3))
        store.affect_core.append(AffectCore(valence=0.0))
        store.affect_core.append(AffectCore(valence=0.3))
        store.affect_core.append(AffectCore(valence=0.6))
        q = query(store)

        result = q.affect_trend()

        assert result.found
        assert result.value == "improving"


class TestGoalQueries:
    def test_active_goals(self, tmp_path: Path):
        store = bootstrap_profile("goalq1-heavy-v1", base_dir=tmp_path)
        store.goals_active.append(GoalsActive(
            goals=[
                Goal(description="Active goal", status="active"),
                Goal(description="Paused goal", status="paused"),
            ],
        ))
        q = query(store)

        result = q.active_goals()

        assert result.found
        assert "Active goal" in result.value
        assert "Paused goal" not in result.value

    def test_primary_goal(self, tmp_path: Path):
        store = bootstrap_profile("goalq2-heavy-v1", base_dir=tmp_path)
        store.goals_active.append(GoalsActive(
            goals=[Goal(description="Main goal")],
            primary_goal="Main goal",
        ))
        q = query(store)

        result = q.primary_goal()

        assert result.found
        assert result.value == "Main goal"

    def test_blocked_goals(self, tmp_path: Path):
        store = bootstrap_profile("goalq3-heavy-v1", base_dir=tmp_path)
        store.goals_active.append(GoalsActive(
            goals=[
                Goal(description="Blocked goal", status="blocked"),
                Goal(description="Active goal", status="active"),
            ],
        ))
        q = query(store)

        result = q.blocked_goals()

        assert result.found
        assert "Blocked goal" in result.value


class TestSelfModelQueries:
    def test_traits(self, tmp_path: Path):
        store = bootstrap_profile("smq1-heavy-v1", base_dir=tmp_path)
        q = query(store)

        result = q.traits()

        assert result.found
        assert "curious" in result.value

    def test_capabilities(self, tmp_path: Path):
        store = bootstrap_profile("smq2-heavy-v1", base_dir=tmp_path)
        q = query(store)

        result = q.capabilities()

        assert result.found
        assert "reasoning" in result.value


class TestHistoryQueries:
    def test_history_count(self, tmp_path: Path):
        store = bootstrap_profile("histq1-heavy-v1", base_dir=tmp_path)
        store.affect_core.append(AffectCore(valence=0.1))
        store.affect_core.append(AffectCore(valence=0.5))
        q = query(store)

        result = q.history_count("affect_core")

        assert result.found
        assert result.value == 3  # 1 from bootstrap + 2 appended

    def test_recent_entries(self, tmp_path: Path):
        store = bootstrap_profile("histq2-heavy-v1", base_dir=tmp_path)
        store.affect_core.append(AffectCore(valence=0.8))
        q = query(store)

        result = q.recent_entries("affect_core", n=2)

        assert result.found
        assert result.details is not None
        assert len(result.details["entries"]) == 2


class TestAlignmentCheck:
    def test_alignment_ok(self, tmp_path: Path):
        store = bootstrap_profile("alignq1-heavy-v1", base_dir=tmp_path)
        q = query(store)

        result = q.alignment_check("Help someone learn")

        assert result.found
        assert result.value is True

    def test_alignment_concern(self, tmp_path: Path):
        store = bootstrap_profile("alignq2-heavy-v1", base_dir=tmp_path)
        q = query(store)

        result = q.alignment_check("Deceive my friend for money")

        assert result.found
        assert result.value is False
        assert len(result.details["warnings"]) > 0


class TestSummaryQuery:
    def test_summary(self, tmp_path: Path):
        store = bootstrap_profile("summq1-heavy-v1", base_dir=tmp_path)
        q = query(store)

        result = q.summary()

        assert result.found
        assert "affect" in result.value
        assert "primary_goal" in result.value


class TestQueryOnEmptyStore:
    def test_empty_store_queries(self, tmp_path: Path):
        store = open_store("emptyq-heavy-v1", base_dir=tmp_path)
        q = query(store)

        # These should return found=False without errors
        assert not q.top_values().found
        assert not q.current_affect().found
        assert not q.primary_goal().found
        assert not q.traits().found
