"""
StatsPanel widget: Shows system statistics and metrics.
"""

from textual.widgets import Static


class StatsPanel(Static):
    """
    Widget for displaying system statistics.
    """

    DEFAULT_CSS = """
    StatsPanel {
        height: auto;
        border: solid $primary;
        padding: 1;
    }
    """

    def __init__(self):
        super().__init__()
        self.stats = {
            "instant_ticks": 0,
            "session_ticks": 0,
            "inputs_processed": 0,
            "llm_calls": 0,
            "uptime": 0,
        }

    def render(self) -> str:
        """Render the statistics panel."""
        lines = []
        lines.append("[bold cyan]SYSTEM STATS[/bold cyan]")
        lines.append("")

        lines.append(f"[bold]Instant Ticks:[/bold]  {self.stats['instant_ticks']:,}")
        lines.append(f"[bold]Session Ticks:[/bold] {self.stats['session_ticks']:,}")
        lines.append(f"[bold]Inputs:[/bold]        {self.stats['inputs_processed']:,}")
        lines.append(f"[bold]LLM Calls:[/bold]     {self.stats['llm_calls']:,}")

        # Format uptime
        uptime = self.stats['uptime']
        if uptime < 60:
            uptime_str = f"{uptime:.0f}s"
        elif uptime < 3600:
            uptime_str = f"{uptime/60:.1f}m"
        else:
            uptime_str = f"{uptime/3600:.1f}h"
        lines.append(f"[bold]Uptime:[/bold]        {uptime_str}")

        return "\n".join(lines)

    def update_stats(self, stats: dict):
        """Update statistics and refresh the display."""
        self.stats.update(stats)
        self.refresh()
