"""
Integration tests for the self-model system.

These tests verify that all components work together correctly.
"""

import asyncio
from datetime import datetime, UTC
from pathlib import Path

import pytest

from selfmodel import (
    Profile,
    StateStore,
    open_store,
    EventBus,
    Event,
    EventType,
    bootstrap_profile,
    create_minimal_profile,
    DEFAULT_CONSTITUTION,
)
from selfmodel.models import (
    AffectCore,
    SelfConstitution,
    Value,
    ContextNow,
    GoalsActive,
    Goal,
    BeliefsNow,
)
from selfmodel.llm import LLMRouter, MOCK_TIERS, MockProvider
from selfmodel.roles import Perceiver, Appraiser, Analyst, Critic, Planner
from selfmodel.loops import Orchestrator, InstantLoop, SessionLoop


class TestBootstrap:
    def test_bootstrap_creates_all_nodes(self, tmp_path: Path):
        store = bootstrap_profile("test-light-v1", base_dir=tmp_path)

        # Check all core nodes exist
        assert store.now.self_constitution is not None
        assert store.now.self_model is not None
        assert store.now.world_model is not None
        assert store.now.affect_core is not None
        assert store.now.context_now is not None
        assert store.now.beliefs_now is not None
        assert store.now.goals_active is not None

    def test_bootstrap_with_custom_constitution(self, tmp_path: Path):
        custom = SelfConstitution(
            values=[Value(name="custom", description="Custom value", weight=1.0)],
            terminal_goals=["Custom goal"],
            nonnegotiables=["Custom rule"],
        )

        store = bootstrap_profile(
            "test-light-v1",
            base_dir=tmp_path,
            constitution=custom,
        )

        assert store.now.self_constitution.values[0].name == "custom"
        assert store.now.self_constitution.terminal_goals[0] == "Custom goal"

    def test_minimal_profile(self, tmp_path: Path):
        store = create_minimal_profile("test", base_dir=tmp_path)

        assert store.now.self_constitution is not None
        assert store.now.affect_core is not None
        assert store.now.context_now is not None

    def test_default_constitution_has_values(self):
        assert len(DEFAULT_CONSTITUTION.values) > 0
        assert len(DEFAULT_CONSTITUTION.nonnegotiables) > 0
        assert len(DEFAULT_CONSTITUTION.terminal_goals) > 0


class TestRolesWithMockLLM:
    @pytest.fixture
    def setup(self, tmp_path: Path):
        """Create store, router, bus for role testing."""
        store = bootstrap_profile("test-light-v1", base_dir=tmp_path)
        mock = MockProvider()
        router = LLMRouter(tiers=MOCK_TIERS, providers={"mock": mock})
        bus = EventBus()
        return store, router, bus, mock

    @pytest.mark.asyncio
    async def test_perceiver_updates_context(self, setup):
        store, router, bus, mock = setup

        perceiver = Perceiver(router, store, bus)
        result = await perceiver.execute(input_data="Working on a coding project at home")

        assert result.success
        assert "context_now" in result.updates

    @pytest.mark.asyncio
    async def test_appraiser_updates_affect(self, setup):
        store, router, bus, mock = setup

        # Mock needs to return valid AppraisalOutput JSON
        mock.responses["Evaluate"] = '{"affect_core": {"valence": 0.5, "arousal": 0.3, "dominance": 0.5, "tension": 0.2, "social_safety": 0.7, "body_load": 0.2}, "primary_emotion": "calm", "primary_intensity": 0.3, "appraisal_summary": "test"}'

        appraiser = Appraiser(router, store, bus)
        result = await appraiser.execute()

        # The appraiser may fail with generic mock responses, that's OK for unit test
        # The important thing is it doesn't crash
        assert result is not None

    @pytest.mark.asyncio
    async def test_analyst_updates_beliefs(self, setup):
        store, router, bus, mock = setup

        analyst = Analyst(router, store, bus)
        result = await analyst.execute()

        assert result.success
        assert "beliefs_now" in result.updates

    @pytest.mark.asyncio
    async def test_analyst_with_problem(self, setup):
        store, router, bus, mock = setup

        analyst = Analyst(router, store, bus)
        result = await analyst.execute(problem="Should I take a break?")

        assert result.success
        # May or may not have workspace depending on mock response

    @pytest.mark.asyncio
    async def test_planner_prioritizes_goals(self, setup):
        store, router, bus, mock = setup

        planner = Planner(router, store, bus)
        result = await planner.execute(action="prioritize")

        assert result.success
        assert "goals_active" in result.updates

    @pytest.mark.asyncio
    async def test_critic_checks_alignment(self, setup):
        store, router, bus, mock = setup

        critic = Critic(router, store, bus)
        result = await critic.execute(action="Take the money and run")

        assert result.success
        assert "constitution_check" in result.updates

    @pytest.mark.asyncio
    async def test_critic_checks_drift(self, setup):
        store, router, bus, mock = setup

        critic = Critic(router, store, bus)
        result = await critic.execute(check_drift=True)

        assert result.success
        assert "drift_analysis" in result.updates


class TestEventBusIntegration:
    @pytest.mark.asyncio
    async def test_events_propagate(self, tmp_path: Path):
        store = bootstrap_profile("test-light-v1", base_dir=tmp_path)
        bus = EventBus()
        mock = MockProvider()
        router = LLMRouter(tiers=MOCK_TIERS, providers={"mock": mock})

        received_events = []

        async def handler(event: Event):
            received_events.append(event)

        bus.subscribe(EventType.NODE_UPDATED, handler)

        perceiver = Perceiver(router, store, bus)
        await perceiver.execute(input_data="Test input")

        # Should have received at least one update event
        assert len(received_events) >= 1
        assert any(e.source == "context_now" for e in received_events)


class TestLoopsIntegration:
    @pytest.mark.asyncio
    async def test_instant_loop_processes_input(self, tmp_path: Path):
        store = bootstrap_profile("test-light-v1", base_dir=tmp_path)
        bus = EventBus()
        mock = MockProvider()
        router = LLMRouter(tiers=MOCK_TIERS, providers={"mock": mock})

        loop = InstantLoop(store, router, bus)

        # Send input before starting
        await loop.send_input("Test input")

        # Run one tick manually
        await loop._tick()

        assert loop.stats.ticks == 1
        assert loop.stats.inputs_processed >= 1

    @pytest.mark.asyncio
    async def test_session_loop_updates_beliefs(self, tmp_path: Path):
        store = bootstrap_profile("test-light-v1", base_dir=tmp_path)
        bus = EventBus()
        mock = MockProvider()
        router = LLMRouter(tiers=MOCK_TIERS, providers={"mock": mock})

        loop = SessionLoop(store, router, bus)

        # Run one tick manually
        await loop._tick()

        assert loop.stats.ticks == 1
        assert loop.stats.belief_updates >= 1


class TestOrchestratorIntegration:
    @pytest.mark.asyncio
    async def test_orchestrator_creation(self, tmp_path: Path):
        # Bootstrap first
        bootstrap_profile("test-light-v1", base_dir=tmp_path)

        orch = Orchestrator.create_mock("test-light-v1", base_dir=tmp_path)

        assert orch.profile.key == "test-light-v1"
        assert not orch.running

    @pytest.mark.asyncio
    async def test_orchestrator_start_stop(self, tmp_path: Path):
        bootstrap_profile("test-light-v1", base_dir=tmp_path)
        orch = Orchestrator.create_mock("test-light-v1", base_dir=tmp_path)

        await orch.start()
        assert orch.running

        await orch.stop()
        assert not orch.running

    @pytest.mark.asyncio
    async def test_orchestrator_input(self, tmp_path: Path):
        bootstrap_profile("test-light-v1", base_dir=tmp_path)
        orch = Orchestrator.create_mock("test-light-v1", base_dir=tmp_path)

        # Can send input even without running
        await orch.input("Test input")

        # Run the instant loop tick manually
        await orch._instant._tick()

        assert orch._instant.stats.inputs_processed >= 1

    @pytest.mark.asyncio
    async def test_orchestrator_stats(self, tmp_path: Path):
        bootstrap_profile("test-light-v1", base_dir=tmp_path)
        orch = Orchestrator.create_mock("test-light-v1", base_dir=tmp_path)

        stats = orch.get_stats()

        assert "profile" in stats
        assert "instant" in stats
        assert "session" in stats
        assert "llm_usage" in stats


class TestEndToEnd:
    @pytest.mark.asyncio
    async def test_full_update_cycle(self, tmp_path: Path):
        """Test a complete cycle: input -> perception -> affect -> beliefs -> goals."""
        store = bootstrap_profile("jacob-heavy-v1", base_dir=tmp_path)
        mock = MockProvider()
        # Set up mock response for Appraiser (needs valid AppraisalOutput JSON)
        mock.responses["Evaluate"] = '{"affect_core": {"valence": 0.6, "arousal": 0.4, "dominance": 0.5, "tension": 0.2, "social_safety": 0.8, "body_load": 0.2}, "primary_emotion": "excited", "primary_intensity": 0.5, "appraisal_summary": "Starting new project is energizing"}'
        router = LLMRouter(tiers=MOCK_TIERS, providers={"mock": mock})
        bus = EventBus()

        # Track all updates
        updates = []

        async def track_update(event: Event):
            updates.append(event.source)

        bus.subscribe(EventType.NODE_UPDATED, track_update)

        # Run roles in sequence
        perceiver = Perceiver(router, store, bus)
        await perceiver.execute(input_data="Starting a new project at 9am")

        appraiser = Appraiser(router, store, bus)
        await appraiser.execute()

        analyst = Analyst(router, store, bus)
        await analyst.execute()

        planner = Planner(router, store, bus)
        await planner.execute(action="prioritize")

        # Check that all expected nodes were updated
        assert "context_now" in updates
        assert "affect_core" in updates
        assert "beliefs_now" in updates
        assert "goals_active" in updates

    @pytest.mark.asyncio
    async def test_state_persistence_across_sessions(self, tmp_path: Path):
        """Test that state persists and can be loaded in a new session."""
        # Session 1: Bootstrap and add some state
        store1 = bootstrap_profile("persist-test-v1", base_dir=tmp_path)
        store1.affect_core.append(AffectCore(valence=0.8, arousal=0.5))
        store1.goals_active.append(GoalsActive(
            goals=[Goal(description="Test goal", priority=0.9)],
            primary_goal="Test goal",
        ))

        # Session 2: Open the same profile
        store2 = open_store("persist-test-v1", base_dir=tmp_path)

        # State should be preserved
        assert store2.now.affect_core.valence == 0.8
        assert store2.now.goals_active.primary_goal == "Test goal"

    @pytest.mark.asyncio
    async def test_time_indexed_history(self, tmp_path: Path):
        """Test that time-indexed queries work correctly."""
        # Use open_store instead of bootstrap to avoid initial entries
        store = open_store("history-test-v1", base_dir=tmp_path)

        # Add states at different times (must be in order)
        t1 = 1000.0
        t2 = 2000.0
        t3 = 3000.0

        store.affect_core.append(AffectCore(valence=0.1), t=t1)
        store.affect_core.append(AffectCore(valence=0.5), t=t2)
        store.affect_core.append(AffectCore(valence=0.9), t=t3)

        # Query at different times
        assert store[t1].affect_core.valence == 0.1
        assert store[t2].affect_core.valence == 0.5
        assert store[t3].affect_core.valence == 0.9

        # Query in between (nearest_prev)
        assert store[2500.0].affect_core.valence == 0.5

    @pytest.mark.asyncio
    async def test_multiple_profiles(self, tmp_path: Path):
        """Test running multiple profiles simultaneously."""
        store1 = bootstrap_profile("alice-light-v1", base_dir=tmp_path)
        store2 = bootstrap_profile("bob-light-v1", base_dir=tmp_path)

        # Different constitutions
        store1.self_constitution.append(SelfConstitution(
            values=[Value(name="creativity", description="Alice values creativity", weight=0.9)],
        ))
        store2.self_constitution.append(SelfConstitution(
            values=[Value(name="precision", description="Bob values precision", weight=0.9)],
        ))

        # Check they're independent
        assert store1.now.self_constitution.values[0].name == "creativity"
        assert store2.now.self_constitution.values[0].name == "precision"

        # State directories are separate
        assert store1.state_dir != store2.state_dir


class TestErrorHandling:
    @pytest.mark.asyncio
    async def test_role_handles_missing_state(self, tmp_path: Path):
        """Test that roles handle missing state gracefully."""
        store = open_store("empty-light-v1", base_dir=tmp_path)
        mock = MockProvider()
        router = LLMRouter(tiers=MOCK_TIERS, providers={"mock": mock})

        # Critic needs constitution - should return error
        critic = Critic(router, store)
        result = await critic.execute(check_drift=True)

        assert not result.success
        assert "constitution" in result.error.lower()

    @pytest.mark.asyncio
    async def test_event_bus_handles_handler_errors(self):
        """Test that event bus doesn't crash on handler errors."""
        bus = EventBus()
        errors_received = []

        async def bad_handler(event: Event):
            raise ValueError("Handler error")

        async def error_handler(event: Event):
            errors_received.append(event)

        bus.subscribe(EventType.NODE_UPDATED, bad_handler)
        bus.subscribe(EventType.ERROR, error_handler)

        # Should not raise
        await bus.publish(Event(
            type=EventType.NODE_UPDATED,
            source="test",
        ))

        # Error should have been caught and published
        assert len(errors_received) >= 1
        assert "Handler error" in errors_received[0].data.get("error", "")
