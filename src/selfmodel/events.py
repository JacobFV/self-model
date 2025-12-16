"""
EventBus: Real-time pub/sub for state updates.

The EventBus enables reactive updates - when one node changes,
other components can be notified and respond. This is critical
for the real-time hybrid loop.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Any, Callable, Awaitable, TypeVar
from enum import Enum, auto


class EventType(Enum):
    """Types of events that can be published."""
    NODE_UPDATED = auto()      # A node's state was updated
    NODE_CREATED = auto()      # First entry in a node
    PROFILE_LOADED = auto()    # A profile was loaded
    LOOP_TICK = auto()         # An update loop ticked
    ERROR = auto()             # An error occurred
    CUSTOM = auto()            # Custom event


@dataclass(frozen=True)
class Event:
    """
    An event that occurred in the system.

    Attributes:
        type: The type of event
        source: What generated the event (e.g., "affect_core", "instant_loop")
        data: Event-specific data
        timestamp: When the event occurred
    """
    type: EventType
    source: str
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=lambda: datetime.now(UTC).timestamp())

    @property
    def datetime(self) -> datetime:
        return datetime.fromtimestamp(self.timestamp, tz=UTC)


# Type for event handlers
EventHandler = Callable[[Event], Awaitable[None]]
SyncEventHandler = Callable[[Event], None]


class EventBus:
    """
    Async pub/sub event bus for real-time state updates.

    Features:
    - Subscribe to specific event types or sources
    - Async handlers for non-blocking updates
    - Event history for debugging
    - Wildcard subscriptions

    Example:
        bus = EventBus()

        async def on_affect_update(event: Event):
            print(f"Affect changed: {event.data}")

        bus.subscribe(EventType.NODE_UPDATED, on_affect_update, source="affect_core")
        await bus.publish(Event(
            type=EventType.NODE_UPDATED,
            source="affect_core",
            data={"valence": 0.5}
        ))
    """

    def __init__(self, history_size: int = 1000):
        self._handlers: dict[EventType, list[tuple[EventHandler, str | None]]] = {}
        self._history: list[Event] = []
        self._history_size = history_size
        self._lock = asyncio.Lock()

    def subscribe(
        self,
        event_type: EventType,
        handler: EventHandler | SyncEventHandler,
        source: str | None = None,
    ) -> Callable[[], None]:
        """
        Subscribe to events.

        Args:
            event_type: Type of event to subscribe to
            handler: Async or sync callback function
            source: Optional source filter (only receive events from this source)

        Returns:
            Unsubscribe function
        """
        # Wrap sync handlers in async
        if not asyncio.iscoroutinefunction(handler):
            sync_handler = handler
            async def async_wrapper(event: Event):
                sync_handler(event)
            handler = async_wrapper

        if event_type not in self._handlers:
            self._handlers[event_type] = []

        entry = (handler, source)
        self._handlers[event_type].append(entry)

        def unsubscribe():
            if event_type in self._handlers:
                try:
                    self._handlers[event_type].remove(entry)
                except ValueError:
                    pass

        return unsubscribe

    async def publish(self, event: Event) -> None:
        """
        Publish an event to all subscribers.

        Handlers are called concurrently for performance.
        """
        async with self._lock:
            # Add to history
            self._history.append(event)
            if len(self._history) > self._history_size:
                self._history = self._history[-self._history_size:]

        # Get matching handlers
        handlers = self._handlers.get(event.type, [])
        tasks = []

        for handler, source_filter in handlers:
            if source_filter is None or source_filter == event.source:
                tasks.append(self._safe_call(handler, event))

        if tasks:
            await asyncio.gather(*tasks)

    async def _safe_call(self, handler: EventHandler, event: Event) -> None:
        """Call a handler with error protection."""
        try:
            await handler(event)
        except Exception as e:
            # Publish error event (but don't recurse)
            if event.type != EventType.ERROR:
                error_event = Event(
                    type=EventType.ERROR,
                    source="event_bus",
                    data={
                        "error": str(e),
                        "handler": handler.__name__,
                        "original_event": event.source,
                    }
                )
                # Direct call to avoid infinite recursion
                error_handlers = self._handlers.get(EventType.ERROR, [])
                for h, _ in error_handlers:
                    try:
                        await h(error_event)
                    except:
                        pass

    def publish_sync(self, event: Event) -> None:
        """
        Publish an event synchronously (for non-async contexts).

        Note: This creates a new event loop if needed. Prefer publish() in async code.
        """
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.publish(event))
        except RuntimeError:
            asyncio.run(self.publish(event))

    @property
    def history(self) -> list[Event]:
        """Get recent event history."""
        return list(self._history)

    def clear_history(self) -> None:
        """Clear event history."""
        self._history.clear()

    def history_for(self, source: str) -> list[Event]:
        """Get history filtered by source."""
        return [e for e in self._history if e.source == source]


class EventEmitter:
    """
    Mixin for classes that emit events.

    Provides convenient emit() method.
    """

    def __init__(self, bus: EventBus, source: str):
        self._bus = bus
        self._source = source

    async def emit(
        self,
        event_type: EventType,
        data: dict[str, Any] | None = None,
    ) -> None:
        """Emit an event from this source."""
        event = Event(
            type=event_type,
            source=self._source,
            data=data or {},
        )
        await self._bus.publish(event)

    def emit_sync(
        self,
        event_type: EventType,
        data: dict[str, Any] | None = None,
    ) -> None:
        """Emit an event synchronously."""
        event = Event(
            type=event_type,
            source=self._source,
            data=data or {},
        )
        self._bus.publish_sync(event)


# Global event bus singleton (can be replaced for testing)
_global_bus: EventBus | None = None


def get_event_bus() -> EventBus:
    """Get the global event bus."""
    global _global_bus
    if _global_bus is None:
        _global_bus = EventBus()
    return _global_bus


def set_event_bus(bus: EventBus) -> None:
    """Set the global event bus (for testing)."""
    global _global_bus
    _global_bus = bus
