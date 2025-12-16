"""
Instant loop: ~100ms - 1s updates.

Handles:
- Perception (context updates)
- Affect (emotional state)

This is the tight loop that processes immediate inputs.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Callable, Awaitable

from ..store import StateStore
from ..events import EventBus, Event, EventType
from ..llm import LLMRouter
from ..roles import Perceiver, Appraiser


@dataclass
class InstantLoopConfig:
    """Configuration for the instant loop."""
    tick_interval: float = 0.5  # seconds between ticks
    perception_enabled: bool = True
    affect_enabled: bool = True
    max_queue_size: int = 100


@dataclass
class InstantLoopStats:
    """Statistics for the instant loop."""
    ticks: int = 0
    inputs_processed: int = 0
    perception_updates: int = 0
    affect_updates: int = 0
    errors: int = 0
    last_tick: datetime | None = None


class InstantLoop:
    """
    The instant loop processes inputs and updates affect.

    This loop runs continuously at high frequency, processing
    incoming inputs and maintaining emotional state.

    Example:
        loop = InstantLoop(store, router, bus)
        await loop.start()

        # Send input
        await loop.send_input("Received an important email")

        # Later
        await loop.stop()
    """

    def __init__(
        self,
        store: StateStore,
        router: LLMRouter,
        bus: EventBus | None = None,
        config: InstantLoopConfig | None = None,
    ):
        self.store = store
        self.router = router
        self.bus = bus or EventBus()
        self.config = config or InstantLoopConfig()

        # Input queue
        self._input_queue: asyncio.Queue[str] = asyncio.Queue(
            maxsize=self.config.max_queue_size
        )

        # Roles
        self._perceiver = Perceiver(router, store, self.bus)
        self._appraiser = Appraiser(router, store, self.bus)

        # State
        self._running = False
        self._task: asyncio.Task | None = None
        self.stats = InstantLoopStats()

    async def start(self) -> None:
        """Start the instant loop."""
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._run())

        await self.bus.publish(Event(
            type=EventType.LOOP_TICK,
            source="instant_loop",
            data={"action": "started"},
        ))

    async def stop(self) -> None:
        """Stop the instant loop."""
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
            source="instant_loop",
            data={"action": "stopped", "stats": self.get_stats()},
        ))

    async def send_input(self, input_text: str) -> None:
        """
        Send input to be processed by the loop.

        Non-blocking - adds to queue.
        """
        try:
            self._input_queue.put_nowait(input_text)
        except asyncio.QueueFull:
            # Drop oldest if full
            try:
                self._input_queue.get_nowait()
            except asyncio.QueueEmpty:
                pass
            self._input_queue.put_nowait(input_text)

    async def _run(self) -> None:
        """Main loop."""
        while self._running:
            try:
                await self._tick()
            except Exception as e:
                self.stats.errors += 1
                await self.bus.publish(Event(
                    type=EventType.ERROR,
                    source="instant_loop",
                    data={"error": str(e)},
                ))

            await asyncio.sleep(self.config.tick_interval)

    async def _tick(self) -> None:
        """Single tick of the loop."""
        self.stats.ticks += 1
        self.stats.last_tick = datetime.now(UTC)

        # Process any inputs
        inputs_to_process = []
        while not self._input_queue.empty():
            try:
                inputs_to_process.append(self._input_queue.get_nowait())
            except asyncio.QueueEmpty:
                break

        # Run perception if we have inputs
        if inputs_to_process and self.config.perception_enabled:
            combined_input = "\n".join(inputs_to_process)
            result = await self._perceiver.execute(input_data=combined_input)
            if result.success:
                self.stats.perception_updates += 1
            self.stats.inputs_processed += len(inputs_to_process)

        # Always run affect update (even without new input)
        if self.config.affect_enabled:
            result = await self._appraiser.execute()
            if result.success:
                self.stats.affect_updates += 1

        # Emit tick event
        await self.bus.publish(Event(
            type=EventType.LOOP_TICK,
            source="instant_loop",
            data={
                "tick": self.stats.ticks,
                "inputs": len(inputs_to_process),
            },
        ))

    def get_stats(self) -> dict:
        """Get loop statistics."""
        return {
            "ticks": self.stats.ticks,
            "inputs_processed": self.stats.inputs_processed,
            "perception_updates": self.stats.perception_updates,
            "affect_updates": self.stats.affect_updates,
            "errors": self.stats.errors,
            "last_tick": self.stats.last_tick.isoformat() if self.stats.last_tick else None,
        }

    @property
    def running(self) -> bool:
        """Whether the loop is running."""
        return self._running
