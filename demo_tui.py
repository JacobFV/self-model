#!/usr/bin/env python3
"""
Demo script to create a test profile and launch the TUI.
"""

from selfmodel import bootstrap_profile, Profile

# Create a test profile if it doesn't exist
profile = Profile.parse("demo-heavy-v1")
print(f"Creating demo profile: {profile.key}")

try:
    store = bootstrap_profile(profile, base_dir="state")
    print(f"Profile created at: {store.state_dir}")
    print(f"  Values: {len(store.now.self_constitution.values)}")
    print(f"  Goals: {len(store.now.goals_active.goals) if store.now.goals_active else 0}")
except Exception as e:
    print(f"Profile may already exist or error: {e}")

print("\nLaunching TUI...")
print("Press 'q' to quit, 'c' for constitution, 'g' for goals")

# Launch TUI
from selfmodel.tui import run_tui
run_tui(profile=profile, base_dir="state")
