"""
TUI (Text User Interface) for the self-model system.

Built with Textual, provides a beautiful terminal dashboard for:
- Viewing affect state in real-time
- Managing goals and plans
- Inspecting constitution and self-model
- Sending inputs to the system
- Monitoring loop statistics
"""

from .app import SelfModelApp, run_tui

__all__ = ["SelfModelApp", "run_tui"]
