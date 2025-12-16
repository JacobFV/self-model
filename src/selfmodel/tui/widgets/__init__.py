"""
Custom widgets for the self-model TUI.
"""

from .affect_gauge import AffectGauge
from .goal_list import GoalList
from .event_stream import EventStream
from .stats_panel import StatsPanel
from .constitution_panel import ConstitutionPanel
from .context_panel import ContextPanel

__all__ = [
    "AffectGauge",
    "GoalList",
    "EventStream",
    "StatsPanel",
    "ConstitutionPanel",
    "ContextPanel",
]
