"""
Tests for visualization module.
"""

from pathlib import Path

import pytest

from selfmodel import bootstrap_profile
from selfmodel.models import AffectCore, GoalsActive, Goal
from selfmodel.viz import (
    state_graph,
    affect_timeline,
    goal_hierarchy,
    constitution_summary,
    belief_map,
    full_report,
)


class TestStateGraph:
    def test_state_graph_basic(self, tmp_path: Path):
        store = bootstrap_profile("viz-test-heavy-v1", base_dir=tmp_path)

        output = state_graph(store)

        assert "STATE GRAPH" in output
        assert "viz-test-heavy-v1" in output
        assert "CORE IDENTITY" in output
        assert "AFFECT" in output
        assert "COGNITION" in output
        assert "PLANNING" in output
        assert "HISTORY" in output

    def test_state_graph_shows_values(self, tmp_path: Path):
        store = bootstrap_profile("viz-values-heavy-v1", base_dir=tmp_path)

        output = state_graph(store)

        # Should show value names
        assert "truth" in output
        assert "growth" in output

    def test_state_graph_shows_affect(self, tmp_path: Path):
        store = bootstrap_profile("viz-affect-heavy-v1", base_dir=tmp_path)
        store.affect_core.append(AffectCore(valence=0.5, arousal=0.7, tension=0.3))

        output = state_graph(store)

        assert "V=+0.50" in output
        assert "A=0.70" in output


class TestAffectTimeline:
    def test_affect_timeline_basic(self, tmp_path: Path):
        store = bootstrap_profile("timeline-test-heavy-v1", base_dir=tmp_path)

        # Add some affect history
        store.affect_core.append(AffectCore(valence=-0.5, arousal=0.2))
        store.affect_core.append(AffectCore(valence=0.0, arousal=0.3))
        store.affect_core.append(AffectCore(valence=0.5, arousal=0.5))
        store.affect_core.append(AffectCore(valence=0.8, arousal=0.7))

        output = affect_timeline(store, n=10)

        assert "AFFECT TIMELINE" in output
        assert "valence" in output

    def test_affect_timeline_empty(self, tmp_path: Path):
        from selfmodel import open_store
        store = open_store("empty-timeline-heavy-v1", base_dir=tmp_path)

        output = affect_timeline(store)

        assert "No affect history" in output

    def test_affect_timeline_arousal(self, tmp_path: Path):
        store = bootstrap_profile("arousal-test-heavy-v1", base_dir=tmp_path)
        store.affect_core.append(AffectCore(valence=0.0, arousal=0.8))

        output = affect_timeline(store, dimension="arousal")

        assert "arousal" in output


class TestGoalHierarchy:
    def test_goal_hierarchy_basic(self, tmp_path: Path):
        store = bootstrap_profile("goals-viz-heavy-v1", base_dir=tmp_path)

        output = goal_hierarchy(store)

        assert "GOAL HIERARCHY" in output
        assert "Terminal Goals" in output
        assert "Active Goals" in output

    def test_goal_hierarchy_multiple_goals(self, tmp_path: Path):
        store = bootstrap_profile("multi-goals-heavy-v1", base_dir=tmp_path)
        store.goals_active.append(GoalsActive(
            goals=[
                Goal(description="High priority goal", priority=0.9, horizon="immediate"),
                Goal(description="Medium priority goal", priority=0.5, horizon="session"),
                Goal(description="Low priority goal", priority=0.2, horizon="daily"),
            ],
            primary_goal="High priority goal",
        ))

        output = goal_hierarchy(store)

        assert "High priority goal" in output
        assert "Medium priority goal" in output
        assert "0.9" in output or "priority: 0.9" in output


class TestConstitutionSummary:
    def test_constitution_summary_basic(self, tmp_path: Path):
        store = bootstrap_profile("const-viz-heavy-v1", base_dir=tmp_path)

        output = constitution_summary(store)

        assert "CONSTITUTION SUMMARY" in output
        assert "VALUES" in output
        assert "TERMINAL GOALS" in output
        assert "NON-NEGOTIABLES" in output
        assert "DECISION PRINCIPLES" in output

    def test_constitution_summary_shows_values(self, tmp_path: Path):
        store = bootstrap_profile("const-values-heavy-v1", base_dir=tmp_path)

        output = constitution_summary(store)

        assert "TRUTH" in output
        assert "GROWTH" in output
        assert "INTEGRITY" in output


class TestBeliefMap:
    def test_belief_map_basic(self, tmp_path: Path):
        store = bootstrap_profile("belief-viz-heavy-v1", base_dir=tmp_path)

        output = belief_map(store)

        assert "BELIEF MAP" in output
        assert "SELF-MODEL" in output
        assert "WORLD-MODEL" in output


class TestFullReport:
    def test_full_report_combines_all(self, tmp_path: Path):
        store = bootstrap_profile("report-test-heavy-v1", base_dir=tmp_path)

        output = full_report(store)

        # Should contain sections from all visualizations
        assert "STATE GRAPH" in output
        assert "CONSTITUTION SUMMARY" in output
        assert "GOAL HIERARCHY" in output
        assert "BELIEF MAP" in output

    def test_full_report_is_substantial(self, tmp_path: Path):
        store = bootstrap_profile("report-size-heavy-v1", base_dir=tmp_path)

        output = full_report(store)

        # Should be a substantial report
        assert len(output) > 1000
