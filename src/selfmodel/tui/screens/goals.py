"""
Goals screen: Detailed view of goal hierarchy.
"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, VerticalScroll
from textual.widgets import Header, Footer, Static
from selfmodel import StateStore


class GoalsScreen(Screen):
    """
    Full-screen view of the goal hierarchy.
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

        with VerticalScroll(id="goals-scroll"):
            yield Static(self._render_goals(), id="goals-content")

        yield Footer()

    def _render_goals(self) -> str:
        """Render the full goal hierarchy."""
        now = self.store.now
        lines = []

        # Title
        lines.append("[bold cyan]═══════════════════════════════════════════════════════[/bold cyan]")
        lines.append("[bold cyan]                   GOAL HIERARCHY                       [/bold cyan]")
        lines.append("[bold cyan]═══════════════════════════════════════════════════════[/bold cyan]")
        lines.append("")

        # Terminal goals (from constitution)
        if now.self_constitution and now.self_constitution.terminal_goals:
            lines.append("[bold yellow]TERMINAL GOALS (from constitution)[/bold yellow]")
            lines.append("[dim]───────────────────────────────────────────────────────[/dim]")
            lines.append("")
            for tg in now.self_constitution.terminal_goals:
                lines.append(f"  ★ {tg}")
            lines.append("")

        # Active goals
        if now.goals_active and now.goals_active.goals:
            lines.append("[bold yellow]ACTIVE GOALS[/bold yellow]")
            lines.append("[dim]───────────────────────────────────────────────────────[/dim]")
            lines.append("")

            # Primary goal
            if now.goals_active.primary_goal:
                lines.append(f"[bold green]PRIMARY:[/bold green] {now.goals_active.primary_goal}")
                lines.append("")

            # Sort by priority
            goals = sorted(now.goals_active.goals, key=lambda g: -g.priority)

            for goal in goals:
                # Status icon
                status_icon = {
                    "active": "[green]●[/green]",
                    "paused": "[yellow]○[/yellow]",
                    "blocked": "[red]⊘[/red]",
                    "completed": "[green]✓[/green]",
                    "abandoned": "[dim]✗[/dim]",
                }.get(goal.status, "?")

                # Horizon icon
                horizon_icon = {
                    "immediate": "→",
                    "session": "↠",
                    "daily": "↣",
                    "weekly": "⇢",
                    "long_term": "⟿",
                }.get(goal.horizon, "?")

                # Progress bar
                progress = int(goal.progress * 20)
                progress_bar = "█" * progress + "░" * (20 - progress)

                # Priority bars
                priority_bars = int(goal.priority * 10)
                priority_str = "▓" * priority_bars + "░" * (10 - priority_bars)

                lines.append(f"{status_icon} [bold]{goal.description}[/bold]")
                lines.append(f"   Progress: [{progress_bar}] {goal.progress * 100:.0f}%")
                lines.append(f"   Priority: [{priority_str}] {goal.priority:.2f}")
                lines.append(f"   Horizon: {goal.horizon} {horizon_icon}")

                if goal.serves_value:
                    lines.append(f"   [dim]Serves value: {goal.serves_value}[/dim]")

                if hasattr(goal, 'requires') and goal.requires:
                    lines.append(f"   [dim]Requires: {', '.join(goal.requires)}[/dim]")

                if hasattr(goal, 'blocked_by') and goal.blocked_by:
                    lines.append(f"   [red]Blocked by: {', '.join(goal.blocked_by)}[/red]")

                lines.append("")

        # Active conflicts
        if now.goals_active and now.goals_active.active_conflicts:
            lines.append("[bold yellow]GOAL CONFLICTS[/bold yellow]")
            lines.append("[dim]───────────────────────────────────────────────────────[/dim]")
            lines.append("")
            for conflict in now.goals_active.active_conflicts:
                lines.append(f"  [red]⚠[/red] {conflict}")
            lines.append("")

        # Current plan
        if now.plan_active and now.plan_active.steps:
            lines.append("[bold yellow]ACTIVE PLAN[/bold yellow]")
            lines.append("[dim]───────────────────────────────────────────────────────[/dim]")
            lines.append("")
            lines.append(f"[bold]Goal:[/bold] {now.plan_active.goal}")
            lines.append("")
            lines.append("[bold]Steps:[/bold]")

            for i, step in enumerate(now.plan_active.steps):
                status_icon = {
                    "pending": "○",
                    "in_progress": "[yellow]●[/yellow]",
                    "completed": "[green]✓[/green]",
                    "skipped": "[dim]↷[/dim]",
                    "failed": "[red]✗[/red]",
                }.get(step.status, "?")

                current = "[bold]→ [/bold]" if i == now.plan_active.current_step else "  "

                lines.append(f"  {current}{status_icon} {step.action}")
                if step.expected_duration:
                    lines.append(f"      [dim]Duration: {step.expected_duration}s[/dim]")

            lines.append("")

        lines.append("[bold cyan]═══════════════════════════════════════════════════════[/bold cyan]")

        return "\n".join(lines)
