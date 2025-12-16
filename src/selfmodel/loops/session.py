"""
Session loop: ~1-5 minute updates.

Handles:
- Belief updates
- Goal prioritization
- Planning
- Optional: reasoning tasks

This loop maintains the cognitive workspace and active plans.
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime, UTC

from ..store import StateStore
from ..events import EventBus, Event, EventType
from ..llm import LLMRouter
from ..roles import Analyst, Planner, Critic


@dataclass
class SessionLoopConfig:
    """Configuration for the session loop."""
    tick_interval: float = 60.0  # 1 minute between ticks
    beliefs_enabled: bool = True
    planning_enabled: bool = True
    critic_enabled: bool = True
    critic_interval: int = 5  # Run critic every N ticks


@dataclass
class SessionLoopStats:
    """Statistics for the session loop."""
    ticks: int = 0
    belief_updates: int = 0
    planning_updates: int = 0
    critic_checks: int = 0
    drift_warnings: int = 0
    errors: int = 0
    last_tick: datetime | None = None


class SessionLoop:
    """
    The session loop maintains beliefs and plans.

    This loop runs at a moderate frequency, updating:
    - Current beliefs about the situation
    - Active goals and priorities
    - Plans for achieving goals

    It also periodically runs the critic to check for drift.

    Example:
        loop = SessionLoop(store, router, bus)
        await loop.start()

        # Request reasoning
        await loop.request_analysis("Should I take this meeting?")

        # Later
        await loop.stop()
    """

    def __init__(
        self,
        store: StateStore,
        router: LLMRouter,
        bus: EventBus | None = None,
        config: SessionLoopConfig | None = None,
    ):
        self.store = store
        self.router = router
        self.bus = bus or EventBus()
        self.config = config or SessionLoopConfig()

        # Roles
        self._analyst = Analyst(router, store, self.bus)
        self._planner = Planner(router, store, self.bus)
        self._critic = Critic(router, store, self.bus)

        # Request queues
        self._analysis_queue: asyncio.Queue[str] = asyncio.Queue()
        self._planning_queue: asyncio.Queue[str] = asyncio.Queue()

        # State
        self._running = False
        self._task: asyncio.Task | None = None
        self.stats = SessionLoopStats()

    async def start(self) -> None:
        """Start the session loop."""
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._run())

        await self.bus.publish(Event(
            type=EventType.LOOP_TICK,
            source="session_loop",
            data={"action": "started"},
        ))

    async def stop(self) -> None:
        """Stop the session loop."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

        await self.bus.publish(Event(
            type=EventType.LOOP_TICK,
            source="session_loop",
            data={"action": "stopped", "stats": self.get_stats()},
        ))

    async def request_analysis(self, problem: str) -> None:
        """Request analysis of a problem."""
        await self._analysis_queue.put(problem)

    async def request_plan(self, goal: str) -> None:
        """Request a plan for a goal."""
        await self._planning_queue.put(goal)

    async def _run(self) -> None:
        """Main loop."""
        while self._running:
            try:
                await self._tick()
            except Exception as e:
                self.stats.errors += 1
                await self.bus.publish(Event(
                    type=EventType.ERROR,
                    source="session_loop",
                    data={"error": str(e)},
                ))

            await asyncio.sleep(self.config.tick_interval)

    async def _tick(self) -> None:
        """Single tick of the loop."""
        self.stats.ticks += 1
        self.stats.last_tick = datetime.now(UTC)

        # Update beliefs
        if self.config.beliefs_enabled:
            # Check for analysis requests
            problem = None
            try:
                problem = self._analysis_queue.get_nowait()
            except asyncio.QueueEmpty:
                pass

            result = await self._analyst.execute(problem=problem)
            if result.success:
                self.stats.belief_updates += 1

        # Handle planning requests or regular planning
        if self.config.planning_enabled:
            # Check for planning requests
            goal = None
            try:
                goal = self._planning_queue.get_nowait()
            except asyncio.QueueEmpty:
                pass

            if goal:
                result = await self._planner.execute(action="plan", goal=goal)
            else:
                # Regular goal prioritization
                result = await self._planner.execute(action="prioritize")

            if result.success:
                self.stats.planning_updates += 1

        # Run critic periodically
        if self.config.critic_enabled:
            if self.stats.ticks % self.config.critic_interval == 0:
                result = await self._critic.execute(check_drift=True)
                self.stats.critic_checks += 1

                if result.success and "drift_analysis" in result.updates:
                    drift = result.updates["drift_analysis"]
                    if drift.get("drift_detected"):
                        self.stats.drift_warnings += 1
                        await self.bus.publish(Event(
                            type=EventType.CUSTOM,
                            source="critic",
                            data={"type": "drift_warning", **drift},
                        ))

        # Emit tick event
        await self.bus.publish(Event(
            type=EventType.LOOP_TICK,
            source="session_loop",
            data={"tick": self.stats.ticks},
        ))

    def get_stats(self) -> dict:
        """Get loop statistics."""
        return {
            "ticks": self.stats.ticks,
            "belief_updates": self.stats.belief_updates,
            "planning_updates": self.stats.planning_updates,
            "critic_checks": self.stats.critic_checks,
            "drift_warnings": self.stats.drift_warnings,
            "errors": self.stats.errors,
            "last_tick": self.stats.last_tick.isoformat() if self.stats.last_tick else None,
        }

    @property
    def running(self) -> bool:
        """Whether the loop is running."""
        return self._running

    async def force_critic_check(self, action: str | None = None) -> dict:
        """
        Force an immediate critic check.

        Args:
            action: Optional action to check alignment for

        Returns:
            Critic result
        """
        result = await self._critic.execute(
            action=action,
            check_drift=action is None,
        )
        return result.updates
