"""
Main Textual App for the self-model TUI.
"""

import asyncio
from pathlib import Path
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Footer
from selfmodel import StateStore, Profile, open_store
from .screens import DashboardScreen


class SelfModelApp(App):
    """
    Main TUI application for the self-model system.

    A beautiful terminal interface for monitoring and interacting with
    the cognitive self-model.
    """

    CSS = """
    Screen {
        layout: vertical;
    }

    #main-container {
        height: 1fr;
        layout: vertical;
    }

    #top-row {
        height: auto;
        layout: horizontal;
    }

    #middle-row {
        height: 1fr;
        layout: horizontal;
    }

    #affect-gauge {
        width: 1fr;
        min-width: 40;
        height: auto;
        margin: 1;
    }

    #context-panel {
        width: 1fr;
        min-width: 40;
        height: auto;
        margin: 1;
    }

    #goal-list {
        width: 1fr;
        height: 1fr;
        margin: 1;
    }

    #event-stream {
        width: 1fr;
        height: 1fr;
        margin: 1;
    }

    #stats-panel {
        height: auto;
        margin: 1;
    }

    #input-container {
        height: auto;
        margin: 1;
        padding: 1;
        border: solid $accent;
    }

    #input-container.hidden {
        display: none;
    }

    #input-label {
        height: auto;
        margin-bottom: 1;
    }

    #input-field {
        width: 100%;
    }

    #constitution-scroll, #goals-scroll {
        height: 1fr;
        padding: 2;
    }

    #constitution-content, #goals-content {
        height: auto;
    }
    """

    TITLE = "Self-Model TUI"
    SUB_TITLE = "Cognitive Self-Modeling System"

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("d", "toggle_dark", "Toggle Dark Mode"),
    ]

    def __init__(
        self,
        profile: str | Profile,
        base_dir: str | Path = "state",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.profile = profile if isinstance(profile, Profile) else Profile.parse(profile)
        self.base_dir = Path(base_dir)
        self.store = None

    def on_mount(self) -> None:
        """Initialize the app on mount."""
        # Open the state store
        try:
            self.store = open_store(self.profile, self.base_dir)
            self.sub_title = f"Profile: {self.profile.key}"
        except Exception as e:
            self.sub_title = f"Error loading profile: {e}"
            # TODO: Show error screen
            return

        # Push the dashboard screen
        self.push_screen(DashboardScreen(self.store))

    def action_toggle_dark(self) -> None:
        """Toggle dark mode."""
        self.dark = not self.dark


def run_tui(
    profile: str | Profile | None = None,
    base_dir: str | Path = "state",
):
    """
    Run the TUI app.

    Args:
        profile: Profile key or Profile instance. If None, will list available profiles.
        base_dir: Base directory for state storage.
    """
    base_path = Path(base_dir)

    # If no profile specified, try to find available profiles
    if profile is None:
        if base_path.exists():
            # List available profiles
            profiles = []
            for entry in base_path.iterdir():
                if entry.is_dir():
                    profiles.append(entry.name)

            if not profiles:
                print("No profiles found. Please create one first with:")
                print("  selfmodel bootstrap <profile-key>")
                return

            if len(profiles) == 1:
                # Auto-select the only profile
                profile = profiles[0]
                print(f"Using profile: {profile}")
            else:
                # Let user choose
                print("Available profiles:")
                for i, p in enumerate(profiles, 1):
                    print(f"  {i}. {p}")
                print("\nPlease specify a profile:")
                print("  selfmodel <profile-key>")
                return
        else:
            print("No state directory found. Please create a profile first with:")
            print("  selfmodel bootstrap <profile-key>")
            return

    # Run the app
    app = SelfModelApp(profile, base_dir)
    app.run()
