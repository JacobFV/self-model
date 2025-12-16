"""
Role system for the self-model.

Roles are specialized LLM agents that update specific nodes in the state graph.
Each role has:
- A specific purpose and set of nodes it updates
- A default LLM tier (can be overridden)
- Input/output contracts
- Prompts for the LLM

The orchestrator calls roles based on update triggers (instant, session, daily).
"""

from .base import Role, RoleResult
from .perceiver import Perceiver
from .appraiser import Appraiser
from .analyst import Analyst
from .critic import Critic
from .planner import Planner

__all__ = [
    "Role",
    "RoleResult",
    "Perceiver",
    "Appraiser",
    "Analyst",
    "Critic",
    "Planner",
]
