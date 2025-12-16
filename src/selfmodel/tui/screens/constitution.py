"""
Constitution screen: Detailed view of the self-constitution.
"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, VerticalScroll
from textual.widgets import Header, Footer, Static, Markdown
from selfmodel import StateStore


class ConstitutionScreen(Screen):
    """
    Full-screen view of the constitution.
    """

    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("q", "app.pop_screen", "Back"),
    ]

    def __init__(self, store: StateStore):
        super().__init__()
        self.store = store

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()

        with VerticalScroll(id="constitution-scroll"):
            yield Static(self._render_constitution(), id="constitution-content")

        yield Footer()

    def _render_constitution(self) -> str:
        """Render the full constitution."""
        now = self.store.now
        const = now.self_constitution

        if not const:
            return "[dim]No constitution loaded[/dim]"

        lines = []

        # Title
        lines.append("[bold cyan]═══════════════════════════════════════════════════════[/bold cyan]")
        lines.append("[bold cyan]                    CONSTITUTION                        [/bold cyan]")
        lines.append("[bold cyan]═══════════════════════════════════════════════════════[/bold cyan]")
        lines.append("")

        # Values
        lines.append("[bold yellow]VALUES[/bold yellow]")
        lines.append("[dim]───────────────────────────────────────────────────────[/dim]")
        lines.append("")
        for value in const.values:
            weight_bar = "█" * int(value.weight * 10) + "░" * (10 - int(value.weight * 10))
            lines.append(f"[bold]{value.name.upper()}[/bold]  [{weight_bar}] {value.weight:.2f}")
            if value.description:
                lines.append(f"  [dim]{value.description}[/dim]")
            lines.append("")

        # Terminal goals
        lines.append("[bold yellow]TERMINAL GOALS[/bold yellow]")
        lines.append("[dim]───────────────────────────────────────────────────────[/dim]")
        lines.append("")
        for tg in const.terminal_goals:
            lines.append(f"  ★ {tg}")
        lines.append("")

        # Non-negotiables
        lines.append("[bold yellow]NON-NEGOTIABLES[/bold yellow]")
        lines.append("[dim]───────────────────────────────────────────────────────[/dim]")
        lines.append("")
        for nn in const.nonnegotiables:
            lines.append(f"  ⚠ {nn}")
        lines.append("")

        # Taboos
        if const.taboos:
            lines.append("[bold yellow]TABOOS[/bold yellow]")
            lines.append("[dim]───────────────────────────────────────────────────────[/dim]")
            lines.append("")
            for t in const.taboos:
                lines.append(f"  ✗ {t}")
            lines.append("")

        # Identity claims
        if const.identity_claims:
            lines.append("[bold yellow]IDENTITY CLAIMS[/bold yellow]")
            lines.append("[dim]───────────────────────────────────────────────────────[/dim]")
            lines.append("")
            for ic in const.identity_claims:
                lines.append(f"  • {ic}")
            lines.append("")

        # Decision principles
        if const.decision_principles:
            lines.append("[bold yellow]DECISION PRINCIPLES[/bold yellow]")
            lines.append("[dim]───────────────────────────────────────────────────────[/dim]")
            lines.append("")
            for i, dp in enumerate(const.decision_principles, 1):
                lines.append(f"  {i}. {dp}")
            lines.append("")

        lines.append("[bold cyan]═══════════════════════════════════════════════════════[/bold cyan]")

        return "\n".join(lines)
