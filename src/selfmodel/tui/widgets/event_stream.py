"""
EventStream widget: Shows recent events in the system.
"""

from textual.widgets import Static
from datetime import datetime, UTC


class EventStream(Static):
    """
    Widget for displaying a stream of recent events.
    """

    DEFAULT_CSS = """
    EventStream {
        height: auto;
        border: solid $primary;
        padding: 1;
    }
    """

    def __init__(self, max_events: int = 20):
        super().__init__()
        self.events = []
        self.max_events = max_events

    def render(self) -> str:
        """Render the event stream."""
        lines = []
        lines.append("[bold cyan]EVENT STREAM[/bold cyan]")
        lines.append("")

        if not self.events:
            lines.append("[dim]No events yet[/dim]")
            return "\n".join(lines)

        # Show most recent events at the top
        for event in reversed(self.events[-15:]):
            timestamp = event.get("timestamp", datetime.now(UTC))
            if isinstance(timestamp, float):
                timestamp = datetime.fromtimestamp(timestamp, UTC)
            time_str = timestamp.strftime("%H:%M:%S")

            event_type = event.get("type", "unknown")
            source = event.get("source", "")
            message = event.get("message", "")

            # Color code by type
            if "error" in event_type.lower():
                color = "red"
                icon = "✗"
            elif "update" in event_type.lower():
                color = "green"
                icon = "↻"
            elif "tick" in event_type.lower():
                color = "yellow"
                icon = "⟳"
            else:
                color = "cyan"
                icon = "•"

            lines.append(f"[dim]{time_str}[/dim] [{color}]{icon}[/{color}] [bold]{source}[/bold]")
            if message:
                lines.append(f"  [dim]{message[:60]}[/dim]")

        return "\n".join(lines)

    def add_event(self, event: dict):
        """Add an event to the stream."""
        self.events.append(event)
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]
        self.refresh()

    def clear_events(self):
        """Clear all events."""
        self.events.clear()
        self.refresh()
