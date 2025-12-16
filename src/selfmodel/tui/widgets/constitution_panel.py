"""
ConstitutionPanel widget: Displays constitution summary.
"""

from textual.widgets import Static
from selfmodel.models import SelfConstitution


class ConstitutionPanel(Static):
    """
    Widget for displaying constitution information.
    """

    DEFAULT_CSS = """
    ConstitutionPanel {
        height: auto;
        border: solid $primary;
        padding: 1;
    }
    """

    def __init__(self, constitution: SelfConstitution | None = None):
        super().__init__()
        self.constitution = constitution

    def render(self) -> str:
        """Render the constitution panel."""
        lines = []
        lines.append("[bold cyan]CONSTITUTION[/bold cyan]")
        lines.append("")

        if not self.constitution:
            lines.append("[dim]No constitution loaded[/dim]")
            return "\n".join(lines)

        const = self.constitution

        # Top values
        lines.append("[bold]Top Values:[/bold]")
        for value in const.values[:5]:
            weight_bar = "█" * int(value.weight * 10) + "░" * (10 - int(value.weight * 10))
            lines.append(f"  [{weight_bar}] {value.name} ({value.weight:.1f})")
        lines.append("")

        # Terminal goals
        if const.terminal_goals:
            lines.append("[bold]Terminal Goals:[/bold]")
            for tg in const.terminal_goals[:3]:
                lines.append(f"  ★ {tg[:50]}")
            if len(const.terminal_goals) > 3:
                lines.append(f"  [dim]...and {len(const.terminal_goals) - 3} more[/dim]")
            lines.append("")

        # Non-negotiables
        if const.nonnegotiables:
            lines.append("[bold]Non-Negotiables:[/bold]")
            for nn in const.nonnegotiables[:3]:
                lines.append(f"  ⚠ {nn[:50]}")
            if len(const.nonnegotiables) > 3:
                lines.append(f"  [dim]...and {len(const.nonnegotiables) - 3} more[/dim]")

        return "\n".join(lines)

    def update_constitution(self, constitution: SelfConstitution):
        """Update the constitution and refresh the display."""
        self.constitution = constitution
        self.refresh()
