"""
AffectGauge widget: Displays affect dimensions as gauges/bars.
"""

from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Container


class AffectGauge(Static):
    """
    Widget for displaying affect state with visual gauges.

    Shows valence, arousal, and tension as horizontal bars.
    """

    DEFAULT_CSS = """
    AffectGauge {
        height: auto;
        border: solid $primary;
        padding: 1;
    }

    AffectGauge .gauge-container {
        height: auto;
        margin: 0 1;
    }

    AffectGauge .gauge-label {
        width: 12;
        text-align: right;
        padding-right: 1;
    }

    AffectGauge .gauge-bar {
        width: 1fr;
    }

    AffectGauge .gauge-value {
        width: 8;
        text-align: right;
    }
    """

    def __init__(self, valence: float = 0.0, arousal: float = 0.0, tension: float = 0.0):
        super().__init__()
        self.valence = valence
        self.arousal = arousal
        self.tension = tension

    def render(self) -> str:
        """Render the affect gauges."""
        lines = []
        lines.append("[bold cyan]AFFECT STATE[/bold cyan]")
        lines.append("")

        # Valence (-1 to +1)
        lines.append(self._render_gauge("Valence", self.valence, -1.0, 1.0, centered=True))
        lines.append("")

        # Arousal (0 to 1)
        lines.append(self._render_gauge("Arousal", self.arousal, 0.0, 1.0))
        lines.append("")

        # Tension (0 to 1)
        lines.append(self._render_gauge("Tension", self.tension, 0.0, 1.0))

        return "\n".join(lines)

    def _render_gauge(self, label: str, value: float, min_val: float, max_val: float, centered: bool = False) -> str:
        """Render a single gauge bar."""
        bar_width = 30

        # Normalize value to 0-1 range
        norm = (value - min_val) / (max_val - min_val)
        norm = max(0.0, min(1.0, norm))

        if centered:
            # For valence, center at 0
            mid = bar_width // 2
            if value >= 0:
                # Positive: draw from center to right
                pos = int(norm * bar_width)
                bar_start = " " * mid
                bar_filled = "[green]" + "█" * (pos - mid) + "[/green]"
                bar_empty = "░" * (bar_width - pos)
                bar = bar_start + "│" + bar_filled + bar_empty
                color = "green"
            else:
                # Negative: draw from left to center
                pos = int(norm * bar_width)
                bar_filled = "[red]" + "█" * (mid - pos) + "[/red]"
                bar_mid = "│"
                bar_empty = " " * (bar_width - mid)
                bar = " " * pos + bar_filled + bar_mid + bar_empty
                color = "red"
        else:
            # Regular left-to-right bar
            pos = int(norm * bar_width)
            if value > 0.7:
                color = "red"
            elif value > 0.4:
                color = "yellow"
            else:
                color = "green"
            bar = f"[{color}]" + "█" * pos + f"[/{color}]" + "░" * (bar_width - pos)

        value_str = f"{value:+.2f}" if centered else f"{value:.2f}"
        return f"[bold]{label:>10}[/bold]  [{bar}]  {value_str}"

    def update_affect(self, valence: float, arousal: float, tension: float):
        """Update the affect values and refresh the display."""
        self.valence = valence
        self.arousal = arousal
        self.tension = tension
        self.refresh()
