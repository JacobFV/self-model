"""
Update loops for the self-model.

The self-model runs on multiple timescales:
- Instant loop (~100ms - 1s): perception, affect
- Session loop (~1-5 min): beliefs, goals, planning
- Consolidation loop (~daily): self-model, world-model updates

Each loop runs specific roles at their appropriate frequency.
"""

from .instant import InstantLoop
from .session import SessionLoop
from .consolidation import ConsolidationLoop
from .orchestrator import Orchestrator

__all__ = [
    "InstantLoop",
    "SessionLoop",
    "ConsolidationLoop",
    "Orchestrator",
]
