"""
Visualization and introspection tools for the self-model.

Provides text-based visualization of:
- State graphs
- Affect timelines
- Goal hierarchies
- Constitution summaries
"""

from datetime import datetime, UTC
from typing import Literal

from .store import StateStore, NODES


def state_graph(store: StateStore, width: int = 60) -> str:
    """
    Generate a text-based visualization of the state graph.

    Args:
        store: The StateStore to visualize
        width: Width of the output

    Returns:
        Multi-line string visualization
    """
    lines = []
    now = store.now

    # Header
    lines.append("=" * width)
    lines.append(f"  STATE GRAPH: {store.profile.key}")
    lines.append("=" * width)
    lines.append("")

    # Core identity (high stability)
    lines.append("CORE IDENTITY (stable)")
    lines.append("-" * 40)
    if now.self_constitution:
        values = [v.name for v in now.self_constitution.values[:4]]
        lines.append(f"  constitution: {len(now.self_constitution.values)} values ({', '.join(values)})")
    if now.self_model:
        traits = [t.name for t in now.self_model.traits[:3]]
        lines.append(f"  self_model: {len(now.self_model.traits)} traits ({', '.join(traits)})")
    if now.world_model:
        lines.append(f"  world_model: {len(now.world_model.priors)} priors")
    lines.append("")

    # Affect (variable)
    lines.append("AFFECT (variable)")
    lines.append("-" * 40)
    if now.affect_core:
        lines.append(f"  affect_core: V={now.affect_core.valence:+.2f} A={now.affect_core.arousal:.2f} T={now.affect_core.tension:.2f}")
    if now.affect_labels and now.affect_labels.primary_emotion:
        lines.append(f"  affect_labels: {now.affect_labels.primary_emotion} ({now.affect_labels.primary_intensity:.1f})")
    lines.append("")

    # Cognition (low-medium)
    lines.append("COGNITION (transient)")
    lines.append("-" * 40)
    if now.context_now:
        task = now.context_now.current_task or "none"
        lines.append(f"  context: {task[:40]}")
    if now.beliefs_now:
        about = now.beliefs_now.about_situation or now.beliefs_now.about_self or "none"
        lines.append(f"  beliefs: {about[:40]}")
    lines.append("")

    # Planning (low-medium)
    lines.append("PLANNING (active)")
    lines.append("-" * 40)
    if now.goals_active and now.goals_active.goals:
        lines.append(f"  goals: {len(now.goals_active.goals)} active")
        if now.goals_active.primary_goal:
            lines.append(f"  primary: {now.goals_active.primary_goal[:40]}")
    if now.plan_active and now.plan_active.steps:
        lines.append(f"  plan: {len(now.plan_active.steps)} steps")
    lines.append("")

    # History stats
    lines.append("HISTORY")
    lines.append("-" * 40)
    for node_name in ["affect_core", "beliefs_now", "context_now", "goals_active"]:
        accessor = getattr(store, node_name)
        count = len(list(accessor.all()))
        lines.append(f"  {node_name}: {count} entries")
    lines.append("")

    lines.append("=" * width)

    return "\n".join(lines)


def affect_timeline(
    store: StateStore,
    n: int = 20,
    dimension: Literal["valence", "arousal", "tension"] = "valence",
) -> str:
    """
    Generate a text-based affect timeline.

    Args:
        store: The StateStore to visualize
        n: Number of entries to show
        dimension: Which dimension to visualize

    Returns:
        Multi-line string visualization
    """
    lines = []
    entries = list(store.affect_core.all())[-n:]

    if not entries:
        return "No affect history."

    # Header
    lines.append(f"AFFECT TIMELINE ({dimension})")
    lines.append("-" * 50)

    # Scale: -1 to 1 for valence, 0 to 1 for others
    if dimension == "valence":
        min_val, max_val = -1.0, 1.0
    else:
        min_val, max_val = 0.0, 1.0

    bar_width = 30

    for entry in entries:
        value = getattr(entry.v, dimension)
        ts = datetime.fromtimestamp(entry.t, UTC).strftime("%H:%M:%S")

        # Normalize to 0-1
        norm = (value - min_val) / (max_val - min_val)
        pos = int(norm * bar_width)

        # Build bar
        if dimension == "valence":
            # Center at 0
            mid = bar_width // 2
            if value >= 0:
                bar = " " * mid + "│" + "█" * (pos - mid) + " " * (bar_width - pos)
            else:
                bar = " " * pos + "█" * (mid - pos) + "│" + " " * (bar_width - mid)
        else:
            bar = "█" * pos + "░" * (bar_width - pos)

        lines.append(f"  {ts} [{bar}] {value:+.2f}")

    lines.append("")

    return "\n".join(lines)


def goal_hierarchy(store: StateStore) -> str:
    """
    Generate a goal hierarchy visualization.

    Args:
        store: The StateStore to visualize

    Returns:
        Multi-line string visualization
    """
    lines = []
    now = store.now

    lines.append("GOAL HIERARCHY")
    lines.append("=" * 50)

    # Terminal goals (from constitution)
    if now.self_constitution and now.self_constitution.terminal_goals:
        lines.append("")
        lines.append("Terminal Goals (from constitution):")
        for tg in now.self_constitution.terminal_goals:
            lines.append(f"  ★ {tg}")

    # Active goals
    if now.goals_active and now.goals_active.goals:
        lines.append("")
        lines.append("Active Goals:")

        # Sort by priority
        goals = sorted(now.goals_active.goals, key=lambda g: -g.priority)

        for g in goals:
            status_icon = {
                "active": "●",
                "paused": "○",
                "blocked": "⊘",
                "completed": "✓",
                "abandoned": "✗",
            }.get(g.status, "?")

            horizon_icon = {
                "immediate": "→",
                "session": "↠",
                "daily": "↣",
                "weekly": "⇢",
                "long_term": "⟿",
            }.get(g.horizon, "?")

            # Progress bar
            progress = int(g.progress * 10)
            bar = "▓" * progress + "░" * (10 - progress)

            lines.append(f"  {status_icon} [{bar}] {g.description[:35]}")
            lines.append(f"      priority: {g.priority:.1f} | horizon: {g.horizon} {horizon_icon}")
            if g.serves_value:
                lines.append(f"      serves: {g.serves_value}")
            if g.blocked_goals if hasattr(g, 'blocked_goals') else False:
                lines.append(f"      blocked by: {', '.join(g.requires[:2])}")

    # Current plan
    if now.plan_active and now.plan_active.steps:
        lines.append("")
        lines.append(f"Current Plan: {now.plan_active.goal[:40]}")
        for i, step in enumerate(now.plan_active.steps):
            status_icon = {
                "pending": "○",
                "in_progress": "●",
                "completed": "✓",
                "skipped": "↷",
                "failed": "✗",
            }.get(step.status, "?")
            current = "→ " if i == now.plan_active.current_step else "  "
            lines.append(f"  {current}{status_icon} {step.action[:40]}")

    lines.append("")
    lines.append("=" * 50)

    return "\n".join(lines)


def constitution_summary(store: StateStore) -> str:
    """
    Generate a constitution summary.

    Args:
        store: The StateStore to visualize

    Returns:
        Multi-line string visualization
    """
    lines = []
    now = store.now

    if not now.self_constitution:
        return "No constitution defined."

    const = now.self_constitution

    lines.append("CONSTITUTION SUMMARY")
    lines.append("=" * 60)
    lines.append("")

    # Values
    lines.append("VALUES")
    lines.append("-" * 40)
    for v in const.values:
        weight_bar = "█" * int(v.weight * 10) + "░" * (10 - int(v.weight * 10))
        lines.append(f"  {v.name.upper():12} [{weight_bar}] {v.weight:.1f}")
        if v.description:
            lines.append(f"                {v.description[:45]}")
    lines.append("")

    # Terminal goals
    lines.append("TERMINAL GOALS")
    lines.append("-" * 40)
    for tg in const.terminal_goals:
        lines.append(f"  ★ {tg}")
    lines.append("")

    # Non-negotiables
    lines.append("NON-NEGOTIABLES")
    lines.append("-" * 40)
    for nn in const.nonnegotiables:
        lines.append(f"  ⚠ {nn}")
    lines.append("")

    # Taboos
    if const.taboos:
        lines.append("TABOOS")
        lines.append("-" * 40)
        for t in const.taboos:
            lines.append(f"  ✗ {t}")
        lines.append("")

    # Identity claims
    if const.identity_claims:
        lines.append("IDENTITY CLAIMS")
        lines.append("-" * 40)
        for ic in const.identity_claims:
            lines.append(f"  • {ic}")
        lines.append("")

    # Decision principles
    if const.decision_principles:
        lines.append("DECISION PRINCIPLES")
        lines.append("-" * 40)
        for i, dp in enumerate(const.decision_principles, 1):
            lines.append(f"  {i}. {dp}")
        lines.append("")

    lines.append("=" * 60)

    return "\n".join(lines)


def belief_map(store: StateStore) -> str:
    """
    Generate a belief/world-model visualization.

    Args:
        store: The StateStore to visualize

    Returns:
        Multi-line string visualization
    """
    lines = []
    now = store.now

    lines.append("BELIEF MAP")
    lines.append("=" * 60)
    lines.append("")

    # Self-model beliefs
    if now.self_model:
        sm = now.self_model
        lines.append("SELF-MODEL")
        lines.append("-" * 40)

        if sm.traits:
            lines.append("  Traits:")
            for t in sm.traits[:5]:
                conf_bar = "●" * int(t.confidence * 5) + "○" * (5 - int(t.confidence * 5))
                lines.append(f"    [{conf_bar}] {t.name}: {t.description[:30]}")

        if sm.capabilities:
            lines.append(f"  Capabilities: {', '.join(sm.capabilities[:5])}")

        if sm.limits:
            lines.append(f"  Limits: {', '.join(sm.limits[:3])}")

        if sm.energy_sources:
            lines.append(f"  Energy+: {', '.join(sm.energy_sources[:3])}")

        if sm.energy_drains:
            lines.append(f"  Energy-: {', '.join(sm.energy_drains[:3])}")

        lines.append("")

    # World-model beliefs
    if now.world_model:
        wm = now.world_model
        lines.append("WORLD-MODEL")
        lines.append("-" * 40)

        if wm.priors:
            lines.append("  Priors:")
            for p in wm.priors[:5]:
                conf_bar = "●" * int(p.confidence * 5) + "○" * (5 - int(p.confidence * 5))
                lines.append(f"    [{conf_bar}] {p.claim[:45]}")

        if wm.unknowns:
            lines.append(f"  Unknowns: {', '.join(wm.unknowns[:3])}")

        lines.append("")

    # Current beliefs
    if now.beliefs_now:
        b = now.beliefs_now
        lines.append("CURRENT BELIEFS")
        lines.append("-" * 40)

        if b.about_self:
            lines.append(f"  About self: {b.about_self[:50]}")
        if b.about_situation:
            lines.append(f"  About situation: {b.about_situation[:50]}")
        if b.about_others:
            lines.append(f"  About others: {b.about_others[:50]}")

        lines.append("")

    lines.append("=" * 60)

    return "\n".join(lines)


def full_report(store: StateStore) -> str:
    """
    Generate a full state report combining all visualizations.

    Args:
        store: The StateStore to visualize

    Returns:
        Multi-line string report
    """
    sections = [
        state_graph(store),
        constitution_summary(store),
        goal_hierarchy(store),
        belief_map(store),
    ]

    return "\n\n".join(sections)
