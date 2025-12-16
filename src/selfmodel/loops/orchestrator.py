"""
Orchestrator: Manages all update loops.

The Orchestrator coordinates the instant, session, and consolidation
loops, providing a unified interface for the self-model runtime.
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime, UTC
from typing import Callable, Awaitable

from ..store import StateStore, open_store
from ..events import EventBus, Event, EventType
from ..llm import LLMRouter, LLMTier, MOCK_TIERS
from ..profile import Profile

from .instant import InstantLoop, InstantLoopConfig
from .session import SessionLoop, SessionLoopConfig
from .consolidation import ConsolidationLoop, ConsolidationLoopConfig


@dataclass
class OrchestratorConfig:
    """Configuration for the orchestrator."""
    instant_enabled: bool = True
    session_enabled: bool = True
    consolidation_enabled: bool = False  # Disabled by default (runs manually)

    instant_config: InstantLoopConfig | None = None
    session_config: SessionLoopConfig | None = None
    consolidation_config: ConsolidationLoopConfig | None = None


class Orchestrator:
    """
    Coordinates all update loops for a self-model.

    The Orchestrator is the main runtime for a self-model:
    - Manages the instant, session, and consolidation loops
    - Provides input/output interfaces
    - Handles events and callbacks

    Example:
        # Create orchestrator
        orch = Orchestrator.create("jacob-heavy-v1")

        # Start the loops
        await orch.start()

        # Send input
        await orch.input("Starting work on the project")

        # Request analysis
        await orch.analyze("Should I take this call?")

        # Stop
        await orch.stop()
    """

    def __init__(
        self,
        store: StateStore,
        router: LLMRouter,
        bus: EventBus | None = None,
        config: OrchestratorConfig | None = None,
    ):
        self.store = store
        self.router = router
        self.bus = bus or EventBus()
        self.config = config or OrchestratorConfig()

        # Create loops
        self._instant = InstantLoop(
            store, router, self.bus,
            self.config.instant_config,
        )
        self._session = SessionLoop(
            store, router, self.bus,
            self.config.session_config,
        )
        self._consolidation = ConsolidationLoop(
            store, router, self.bus,
            self.config.consolidation_config,
        )

        # Callbacks
        self._on_update: list[Callable[[Event], Awaitable[None]]] = []

        # Subscribe to events
        self.bus.subscribe(EventType.NODE_UPDATED, self._handle_node_update)

    @classmethod
    def create(
        cls,
        profile: Profile | str,
        router: LLMRouter | None = None,
        base_dir: str = "state",
        config: OrchestratorConfig | None = None,
    ) -> "Orchestrator":
        """
        Create an orchestrator for a profile.

        Args:
            profile: Profile instance or key string
            router: LLM router (creates default if not provided)
            base_dir: Base directory for state
            config: Orchestrator configuration

        Returns:
            Configured Orchestrator instance
        """
        store = open_store(profile, base_dir)
        router = router or LLMRouter()
        bus = EventBus()

        return cls(store, router, bus, config)

    @classmethod
    def create_mock(
        cls,
        profile: Profile | str = "test-light-v1",
        base_dir: str = "state",
    ) -> "Orchestrator":
        """
        Create an orchestrator with mock LLM for testing.
        """
        from ..llm import MockProvider

        store = open_store(profile, base_dir)
        mock = MockProvider()
        router = LLMRouter(tiers=MOCK_TIERS, providers={"mock": mock})
        bus = EventBus()

        return cls(store, router, bus)

    async def start(self) -> None:
        """Start all enabled loops."""
        if self.config.instant_enabled:
            await self._instant.start()

        if self.config.session_enabled:
            await self._session.start()

        if self.config.consolidation_enabled:
            await self._consolidation.start()

        await self.bus.publish(Event(
            type=EventType.PROFILE_LOADED,
            source="orchestrator",
            data={"profile": self.store.profile.key},
        ))

    async def stop(self) -> None:
        """Stop all loops."""
        await self._instant.stop()
        await self._session.stop()
        await self._consolidation.stop()

    async def input(self, text: str) -> None:
        """
        Send input to the instant loop.

        This is the primary way to feed information into the system.
        """
        await self._instant.send_input(text)

    async def analyze(self, problem: str) -> None:
        """
        Request analysis of a problem.

        The analysis will be performed in the session loop.
        """
        await self._session.request_analysis(problem)

    async def plan(self, goal: str) -> None:
        """
        Request a plan for a goal.

        The plan will be created in the session loop.
        """
        await self._session.request_plan(goal)

    async def check_alignment(self, action: str) -> dict:
        """
        Check if an action aligns with constitution.

        Returns immediately with the critic's assessment.
        """
        return await self._session.force_critic_check(action)

    async def consolidate(self) -> dict:
        """
        Run consolidation manually.

        Useful for end-of-day updates without waiting for the schedule.
        """
        return await self._consolidation.consolidate()

    def on_update(
        self,
        callback: Callable[[Event], Awaitable[None]],
    ) -> Callable[[], None]:
        """
        Register a callback for node updates.

        Returns an unsubscribe function.
        """
        self._on_update.append(callback)

        def unsubscribe():
            if callback in self._on_update:
                self._on_update.remove(callback)

        return unsubscribe

    async def _handle_node_update(self, event: Event) -> None:
        """Handle node update events."""
        for callback in self._on_update:
            try:
                await callback(event)
            except Exception:
                pass

    def get_stats(self) -> dict:
        """Get statistics from all loops."""
        return {
            "profile": self.store.profile.key,
            "instant": self._instant.get_stats(),
            "session": self._session.get_stats(),
            "consolidation": self._consolidation.get_stats(),
            "llm_usage": self.router.get_usage_summary(),
        }

    @property
    def profile(self) -> Profile:
        """The profile this orchestrator manages."""
        return self.store.profile

    @property
    def running(self) -> bool:
        """Whether any loops are running."""
        return (
            self._instant.running or
            self._session.running or
            self._consolidation.running
        )

    # Convenience accessors for current state
    @property
    def affect(self):
        """Current affect state."""
        return self.store.now.affect_core

    @property
    def context(self):
        """Current context."""
        return self.store.now.context_now

    @property
    def beliefs(self):
        """Current beliefs."""
        return self.store.now.beliefs_now

    @property
    def goals(self):
        """Current goals."""
        return self.store.now.goals_active

    @property
    def plan(self):
        """Current plan."""
        return self.store.now.plan_active
