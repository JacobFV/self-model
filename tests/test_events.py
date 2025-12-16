"""
Tests for the event bus system.
"""

import asyncio
import pytest

from selfmodel.events import (
    EventBus,
    Event,
    EventType,
    EventEmitter,
    get_event_bus,
    set_event_bus,
)


class TestEvent:
    def test_create_event(self):
        event = Event(
            type=EventType.NODE_UPDATED,
            source="affect_core",
            data={"valence": 0.5},
        )
        assert event.type == EventType.NODE_UPDATED
        assert event.source == "affect_core"
        assert event.data["valence"] == 0.5
        assert event.timestamp > 0

    def test_event_datetime(self):
        event = Event(type=EventType.NODE_UPDATED, source="test")
        dt = event.datetime
        assert dt is not None
        assert dt.tzinfo is not None


class TestEventBus:
    @pytest.fixture
    def bus(self):
        return EventBus()

    @pytest.mark.asyncio
    async def test_subscribe_and_publish(self, bus: EventBus):
        received = []

        async def handler(event: Event):
            received.append(event)

        bus.subscribe(EventType.NODE_UPDATED, handler)

        event = Event(type=EventType.NODE_UPDATED, source="test", data={"x": 1})
        await bus.publish(event)

        assert len(received) == 1
        assert received[0].data["x"] == 1

    @pytest.mark.asyncio
    async def test_source_filter(self, bus: EventBus):
        received = []

        async def handler(event: Event):
            received.append(event)

        bus.subscribe(EventType.NODE_UPDATED, handler, source="affect_core")

        # This should be received
        await bus.publish(Event(
            type=EventType.NODE_UPDATED,
            source="affect_core",
            data={"x": 1}
        ))

        # This should NOT be received (different source)
        await bus.publish(Event(
            type=EventType.NODE_UPDATED,
            source="context_now",
            data={"x": 2}
        ))

        assert len(received) == 1
        assert received[0].data["x"] == 1

    @pytest.mark.asyncio
    async def test_multiple_handlers(self, bus: EventBus):
        received1 = []
        received2 = []

        async def handler1(event: Event):
            received1.append(event)

        async def handler2(event: Event):
            received2.append(event)

        bus.subscribe(EventType.NODE_UPDATED, handler1)
        bus.subscribe(EventType.NODE_UPDATED, handler2)

        await bus.publish(Event(type=EventType.NODE_UPDATED, source="test"))

        assert len(received1) == 1
        assert len(received2) == 1

    @pytest.mark.asyncio
    async def test_unsubscribe(self, bus: EventBus):
        received = []

        async def handler(event: Event):
            received.append(event)

        unsubscribe = bus.subscribe(EventType.NODE_UPDATED, handler)

        await bus.publish(Event(type=EventType.NODE_UPDATED, source="test"))
        assert len(received) == 1

        unsubscribe()

        await bus.publish(Event(type=EventType.NODE_UPDATED, source="test"))
        assert len(received) == 1  # Still 1, handler was removed

    @pytest.mark.asyncio
    async def test_sync_handler(self, bus: EventBus):
        received = []

        def sync_handler(event: Event):
            received.append(event)

        bus.subscribe(EventType.NODE_UPDATED, sync_handler)
        await bus.publish(Event(type=EventType.NODE_UPDATED, source="test"))

        assert len(received) == 1

    @pytest.mark.asyncio
    async def test_history(self, bus: EventBus):
        await bus.publish(Event(type=EventType.NODE_UPDATED, source="a"))
        await bus.publish(Event(type=EventType.NODE_CREATED, source="b"))
        await bus.publish(Event(type=EventType.NODE_UPDATED, source="c"))

        history = bus.history
        assert len(history) == 3

        # Filter by source
        a_history = bus.history_for("a")
        assert len(a_history) == 1

    @pytest.mark.asyncio
    async def test_history_limit(self):
        bus = EventBus(history_size=5)

        for i in range(10):
            await bus.publish(Event(
                type=EventType.NODE_UPDATED,
                source="test",
                data={"i": i}
            ))

        assert len(bus.history) == 5
        # Should have the last 5
        assert bus.history[0].data["i"] == 5
        assert bus.history[-1].data["i"] == 9

    @pytest.mark.asyncio
    async def test_error_handling(self, bus: EventBus):
        errors = []

        async def bad_handler(event: Event):
            raise ValueError("oops")

        async def error_handler(event: Event):
            errors.append(event)

        bus.subscribe(EventType.NODE_UPDATED, bad_handler)
        bus.subscribe(EventType.ERROR, error_handler)

        # Should not raise
        await bus.publish(Event(type=EventType.NODE_UPDATED, source="test"))

        assert len(errors) == 1
        assert "oops" in errors[0].data["error"]

    @pytest.mark.asyncio
    async def test_concurrent_handlers(self, bus: EventBus):
        results = []

        async def slow_handler(event: Event):
            await asyncio.sleep(0.01)
            results.append(("slow", event.data["i"]))

        async def fast_handler(event: Event):
            results.append(("fast", event.data["i"]))

        bus.subscribe(EventType.NODE_UPDATED, slow_handler)
        bus.subscribe(EventType.NODE_UPDATED, fast_handler)

        await bus.publish(Event(
            type=EventType.NODE_UPDATED,
            source="test",
            data={"i": 1}
        ))

        # Fast handler should complete before slow
        assert len(results) == 2


class TestEventEmitter:
    @pytest.mark.asyncio
    async def test_emit(self):
        bus = EventBus()
        received = []

        async def handler(event: Event):
            received.append(event)

        bus.subscribe(EventType.NODE_UPDATED, handler)

        emitter = EventEmitter(bus, "my_source")
        await emitter.emit(EventType.NODE_UPDATED, {"value": 42})

        assert len(received) == 1
        assert received[0].source == "my_source"
        assert received[0].data["value"] == 42


class TestGlobalBus:
    def test_get_set_bus(self):
        original = get_event_bus()

        new_bus = EventBus()
        set_event_bus(new_bus)

        assert get_event_bus() is new_bus

        # Restore
        set_event_bus(original)
