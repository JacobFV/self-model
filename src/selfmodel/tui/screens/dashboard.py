"""
Dashboard screen: Main view with all key information.
"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Input
from selfmodel import StateStore
from ..widgets import (
    AffectGauge,
    GoalList,
    EventStream,
    StatsPanel,
    ContextPanel,
)


class DashboardScreen(Screen):
    """
    Main dashboard screen showing:
    - Affect state
    - Active goals
    - Current context
    - Event stream
    - System stats
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("c", "show_constitution", "Constitution"),
        ("g", "show_goals", "Goals"),
        ("i", "input_mode", "Input"),
        ("/", "command", "Command"),
    ]

    def __init__(self, store: StateStore):
        super().__init__()
        self.store = store

    def compose(self) -> ComposeResult:
        """Create child widgets for the dashboard."""
        yield Header()

        # Main content area
        with Container(id="main-container"):
            # Top row: Affect and Context
            with Horizontal(id="top-row"):
                yield AffectGauge(id="affect-gauge")
                yield ContextPanel(id="context-panel")

            # Middle row: Goals and Events
            with Horizontal(id="middle-row"):
                yield GoalList(id="goal-list")
                yield EventStream(id="event-stream")

            # Bottom row: Stats
            yield StatsPanel(id="stats-panel")

        # Input area (initially hidden)
        with Container(id="input-container", classes="hidden"):
            yield Static("Enter message:", id="input-label")
            yield Input(placeholder="Type your message here...", id="input-field")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the dashboard with current state."""
        self.refresh_data()
        self.set_interval(1.0, self.refresh_data)  # Auto-refresh every second

    def refresh_data(self) -> None:
        """Refresh all widgets with current state."""
        now = self.store.now

        # Update affect gauge
        if now.affect_core:
            affect_gauge = self.query_one("#affect-gauge", AffectGauge)
            affect_gauge.update_affect(
                now.affect_core.valence,
                now.affect_core.arousal,
                now.affect_core.tension,
            )

        # Update goals
        if now.goals_active and now.goals_active.goals:
            goal_list = self.query_one("#goal-list", GoalList)
            goal_list.update_goals(now.goals_active.goals)

        # Update context
        if now.context_now:
            context_panel = self.query_one("#context-panel", ContextPanel)
            context_panel.update_context(now.context_now)

    def action_refresh(self) -> None:
        """Manual refresh action."""
        self.refresh_data()
        event_stream = self.query_one("#event-stream", EventStream)
        event_stream.add_event({
            "type": "refresh",
            "source": "dashboard",
            "message": "Manual refresh triggered",
        })

    def action_show_constitution(self) -> None:
        """Switch to constitution screen."""
        from .constitution import ConstitutionScreen
        self.app.push_screen(ConstitutionScreen(self.store))

    def action_show_goals(self) -> None:
        """Switch to goals screen."""
        from .goals import GoalsScreen
        self.app.push_screen(GoalsScreen(self.store))

    def action_input_mode(self) -> None:
        """Enter input mode."""
        input_container = self.query_one("#input-container")
        input_container.remove_class("hidden")
        input_field = self.query_one("#input-field", Input)
        input_field.focus()

    def action_command(self) -> None:
        """Open command palette."""
        # TODO: Implement command palette
        pass

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        message = event.value
        if message:
            # Add to event stream
            event_stream = self.query_one("#event-stream", EventStream)
            event_stream.add_event({
                "type": "input",
                "source": "user",
                "message": f"Input: {message}",
            })

            # TODO: Send to the system for processing

            # Clear and hide input
            input_field = self.query_one("#input-field", Input)
            input_field.value = ""
            input_container = self.query_one("#input-container")
            input_container.add_class("hidden")
