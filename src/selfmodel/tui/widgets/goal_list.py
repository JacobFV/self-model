"""
GoalList widget: Displays active goals with priorities.
"""

from textual.widgets import Static
from selfmodel.models import Goal


class GoalList(Static):
    """
    Widget for displaying a list of active goals.
    """

    DEFAULT_CSS = """
    GoalList {
        height: auto;
        border: solid $primary;
        padding: 1;
    }
    """

    def __init__(self, goals: list[Goal] | None = None):
        super().__init__()
        self.goals = goals or []

    def render(self) -> str:
        """Render the goal list."""
        lines = []
        lines.append("[bold cyan]ACTIVE GOALS[/bold cyan]")
        lines.append("")

        if not self.goals:
            lines.append("[dim]No active goals[/dim]")
            return "\n".join(lines)

        # Sort by priority
        sorted_goals = sorted(self.goals, key=lambda g: -g.priority)

        for goal in sorted_goals[:10]:  # Show top 10
            # Status icon
            status_icon = {
                "active": "[green]●[/green]",
                "paused": "[yellow]○[/yellow]",
                "blocked": "[red]⊘[/red]",
                "completed": "[green]✓[/green]",
                "abandoned": "[dim]✗[/dim]",
            }.get(goal.status, "?")

            # Priority bar (0-1 scale shown as bars)
            priority_bars = int(goal.priority * 5)
            priority_str = "▓" * priority_bars + "░" * (5 - priority_bars)

            # Progress bar
            progress = int(goal.progress * 10)
            progress_bar = "█" * progress + "░" * (10 - progress)

            # Description (truncated)
            desc = goal.description[:45] + "..." if len(goal.description) > 45 else goal.description

            lines.append(f"{status_icon} [{progress_bar}] {desc}")
            lines.append(f"   [dim]priority: {priority_str} {goal.priority:.2f} | horizon: {goal.horizon}[/dim]")

            if goal.serves_value:
                lines.append(f"   [dim]serves: {goal.serves_value}[/dim]")

            lines.append("")

        return "\n".join(lines)

    def update_goals(self, goals: list[Goal]):
        """Update the goal list and refresh the display."""
        self.goals = goals
        self.refresh()
