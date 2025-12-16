"""
Consolidation loop: ~daily/sleep updates.

Handles:
- Self-model updates
- World-model updates
- Memory consolidation
- Identity maintenance

This loop runs rarely but performs deep updates to stable nodes.
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime, UTC
from pydantic import BaseModel, Field

from ..store import StateStore
from ..events import EventBus, Event, EventType
from ..llm import LLMRouter, LLMTier
from ..llm.providers import Message
from ..models import SelfModel, WorldModel


class SelfModelUpdate(BaseModel):
    """Proposed update to self-model."""
    new_traits: list[str] = Field(default_factory=list)
    new_capabilities: list[str] = Field(default_factory=list)
    new_limits: list[str] = Field(default_factory=list)
    new_failure_modes: list[str] = Field(default_factory=list)
    cognitive_style_notes: str = ""
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)


class WorldModelUpdate(BaseModel):
    """Proposed update to world-model."""
    new_priors: list[str] = Field(default_factory=list)
    updated_priors: list[str] = Field(default_factory=list)
    new_unknowns: list[str] = Field(default_factory=list)
    resolved_unknowns: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)


@dataclass
class ConsolidationLoopConfig:
    """Configuration for the consolidation loop."""
    tick_interval: float = 3600.0 * 24  # Daily by default
    self_model_enabled: bool = True
    world_model_enabled: bool = True
    review_window_hours: int = 24  # How far back to look


@dataclass
class ConsolidationLoopStats:
    """Statistics for the consolidation loop."""
    ticks: int = 0
    self_model_updates: int = 0
    world_model_updates: int = 0
    errors: int = 0
    last_tick: datetime | None = None


class ConsolidationLoop:
    """
    The consolidation loop maintains stable identity nodes.

    This loop runs infrequently (e.g., daily) and performs
    deep analysis to update:
    - self_model: What you believe about yourself
    - world_model: What you believe about reality

    These are the "slow variables" that define identity.

    Example:
        loop = ConsolidationLoop(store, router, bus)

        # Run consolidation manually
        await loop.consolidate()

        # Or run on a schedule
        await loop.start()
    """

    def __init__(
        self,
        store: StateStore,
        router: LLMRouter,
        bus: EventBus | None = None,
        config: ConsolidationLoopConfig | None = None,
    ):
        self.store = store
        self.router = router
        self.bus = bus or EventBus()
        self.config = config or ConsolidationLoopConfig()

        # State
        self._running = False
        self._task: asyncio.Task | None = None
        self.stats = ConsolidationLoopStats()

    async def start(self) -> None:
        """Start the consolidation loop."""
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._run())

        await self.bus.publish(Event(
            type=EventType.LOOP_TICK,
            source="consolidation_loop",
            data={"action": "started"},
        ))

    async def stop(self) -> None:
        """Stop the consolidation loop."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _run(self) -> None:
        """Main loop."""
        while self._running:
            try:
                await self.consolidate()
            except Exception as e:
                self.stats.errors += 1
                await self.bus.publish(Event(
                    type=EventType.ERROR,
                    source="consolidation_loop",
                    data={"error": str(e)},
                ))

            await asyncio.sleep(self.config.tick_interval)

    async def consolidate(self) -> dict:
        """
        Run consolidation manually.

        Reviews recent state and proposes updates to stable nodes.

        Returns:
            Summary of updates made
        """
        self.stats.ticks += 1
        self.stats.last_tick = datetime.now(UTC)

        updates = {}

        # Update self-model
        if self.config.self_model_enabled:
            result = await self._update_self_model()
            if result:
                updates["self_model"] = result
                self.stats.self_model_updates += 1

        # Update world-model
        if self.config.world_model_enabled:
            result = await self._update_world_model()
            if result:
                updates["world_model"] = result
                self.stats.world_model_updates += 1

        await self.bus.publish(Event(
            type=EventType.LOOP_TICK,
            source="consolidation_loop",
            data={"action": "consolidated", "updates": list(updates.keys())},
        ))

        return updates

    async def _update_self_model(self) -> dict | None:
        """Update self-model based on recent experience."""
        # Get current self-model
        current = self.store.self_model.value

        # Get recent affect patterns
        recent_affect = list(self.store.affect_core.all())[-100:]  # Last 100 entries

        # Get recent cognition
        recent_beliefs = list(self.store.beliefs_now.all())[-20:]
        recent_workspace = list(self.store.cognition_workspace.all())[-10:]

        # Summarize patterns
        affect_summary = self._summarize_affect(recent_affect)
        cognition_summary = self._summarize_cognition(recent_beliefs, recent_workspace)

        current_summary = ""
        if current:
            traits = ", ".join(t.name for t in current.traits[:5]) if current.traits else "none"
            current_summary = f"""
Current self-model:
- Traits: {traits}
- Capabilities: {', '.join(current.capabilities[:3]) if current.capabilities else 'none'}
- Limits: {', '.join(current.limits[:3]) if current.limits else 'none'}
"""

        messages = [
            Message(
                role="user",
                content=f"""Review recent experience and propose self-model updates.

{current_summary}

Recent affect patterns:
{affect_summary}

Recent cognition:
{cognition_summary}

Based on this evidence, propose updates to the self-model:
1. New traits discovered (patterns of behavior/experience)
2. New capabilities demonstrated
3. New limits encountered
4. New failure modes identified
5. Notes on cognitive style

Only propose updates with clear evidence. Be conservative - identity should be stable.
Confidence: how confident are you in these updates (0-1)?"""
            )
        ]

        try:
            response = await self.router.complete(
                tier=LLMTier.HEAVY,
                messages=messages,
                response_model=SelfModelUpdate,
                system="You are updating a cognitive self-model. Be evidence-based and conservative.",
            )

            if response.parsed and response.parsed.confidence > 0.3:
                # Apply updates (in a real system, you'd merge carefully)
                # For now, just record what was proposed
                return response.parsed.model_dump()

        except Exception:
            pass

        return None

    async def _update_world_model(self) -> dict | None:
        """Update world-model based on recent experience."""
        current = self.store.world_model.value

        # Get recent beliefs for world-model evidence
        recent_beliefs = list(self.store.beliefs_now.all())[-20:]

        beliefs_summary = ""
        if recent_beliefs:
            belief_claims = []
            for entry in recent_beliefs[-5:]:
                if entry.v.about_situation:
                    belief_claims.append(entry.v.about_situation)
            beliefs_summary = "\n".join(f"- {b}" for b in belief_claims)

        current_summary = ""
        if current:
            priors = "\n".join(f"- {p.claim}" for p in current.priors[:5]) if current.priors else "none"
            current_summary = f"""
Current world-model priors:
{priors}

Current unknowns:
{', '.join(current.unknowns[:5]) if current.unknowns else 'none'}
"""

        messages = [
            Message(
                role="user",
                content=f"""Review recent beliefs and propose world-model updates.

{current_summary}

Recent situational beliefs:
{beliefs_summary}

Based on this, propose updates:
1. New priors (general beliefs about how the world works)
2. Priors that should be updated (with new evidence)
3. New unknowns discovered
4. Unknowns that have been resolved

Be conservative - priors should be general patterns, not specific situations.
Confidence: how confident in these updates (0-1)?"""
            )
        ]

        try:
            response = await self.router.complete(
                tier=LLMTier.HEAVY,
                messages=messages,
                response_model=WorldModelUpdate,
                system="You are updating a world-model. Focus on general patterns, not specifics.",
            )

            if response.parsed and response.parsed.confidence > 0.3:
                return response.parsed.model_dump()

        except Exception:
            pass

        return None

    def _summarize_affect(self, entries) -> str:
        """Summarize affect patterns."""
        if not entries:
            return "No recent affect data."

        # Calculate averages
        valences = [e.v.valence for e in entries]
        arousals = [e.v.arousal for e in entries]

        avg_valence = sum(valences) / len(valences)
        avg_arousal = sum(arousals) / len(arousals)

        # Find extremes
        min_valence = min(valences)
        max_valence = max(valences)

        return f"""
- Average valence: {avg_valence:.2f} (range: {min_valence:.2f} to {max_valence:.2f})
- Average arousal: {avg_arousal:.2f}
- Samples: {len(entries)}
"""

    def _summarize_cognition(self, beliefs, workspace) -> str:
        """Summarize cognition patterns."""
        parts = []

        if beliefs:
            recent_situations = [
                e.v.about_situation for e in beliefs[-5:]
                if e.v.about_situation
            ]
            if recent_situations:
                parts.append("Recent situations: " + "; ".join(recent_situations[:3]))

        if workspace:
            recent_problems = [
                e.v.problem_statement for e in workspace[-3:]
                if e.v.problem_statement
            ]
            if recent_problems:
                parts.append("Recent problems: " + "; ".join(recent_problems[:2]))

        return "\n".join(parts) if parts else "No recent cognition data."

    def get_stats(self) -> dict:
        """Get loop statistics."""
        return {
            "ticks": self.stats.ticks,
            "self_model_updates": self.stats.self_model_updates,
            "world_model_updates": self.stats.world_model_updates,
            "errors": self.stats.errors,
            "last_tick": self.stats.last_tick.isoformat() if self.stats.last_tick else None,
        }

    @property
    def running(self) -> bool:
        """Whether the loop is running."""
        return self._running
