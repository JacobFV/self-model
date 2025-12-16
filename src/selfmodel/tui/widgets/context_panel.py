"""
ContextPanel widget: Displays current context information.
"""

from textual.widgets import Static
from selfmodel.models import ContextNow


class ContextPanel(Static):
    """
    Widget for displaying current context.
    """

    DEFAULT_CSS = """
    ContextPanel {
        height: auto;
        border: solid $primary;
        padding: 1;
    }
    """

    def __init__(self, context: ContextNow | None = None):
        super().__init__()
        self.context = context

    def render(self) -> str:
        """Render the context panel."""
        lines = []
        lines.append("[bold cyan]CURRENT CONTEXT[/bold cyan]")
        lines.append("")

        if not self.context:
            lines.append("[dim]No context available[/dim]")
            return "\n".join(lines)

        ctx = self.context

        if ctx.current_task:
            lines.append(f"[bold]Task:[/bold] {ctx.current_task[:60]}")
        else:
            lines.append("[dim]No active task[/dim]")

        lines.append("")

        if ctx.location:
            lines.append(f"[bold]Location:[/bold] {ctx.location}")

        if ctx.social_setting:
            lines.append(f"[bold]Setting:[/bold] {ctx.social_setting}")

        if ctx.time_pressure:
            pressure_bar = "█" * int(ctx.time_pressure * 10) + "░" * (10 - int(ctx.time_pressure * 10))
            lines.append(f"[bold]Time Pressure:[/bold] [{pressure_bar}] {ctx.time_pressure:.1f}")

        if ctx.interruptions:
            lines.append(f"[bold]Interruptions:[/bold] {len(ctx.interruptions)}")

        return "\n".join(lines)

    def update_context(self, context: ContextNow):
        """Update the context and refresh the display."""
        self.context = context
        self.refresh()
