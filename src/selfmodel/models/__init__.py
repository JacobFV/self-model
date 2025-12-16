"""
Pydantic models for the self-model state graph.

This module contains all the node types that make up the cognitive self-model:
- Core: constitution, self-model, world-model
- Affect: emotional state, labels, appraisals
- Cognition: context, beliefs, workspace
- Memory: stores and retrieval policies
- Planning: goals, plans, options
- Social: relationships, attachment
"""

from .core import (
    Value,
    Role,
    SelfConstitution,
    Trait,
    FailureMode,
    SelfModel,
    Prior,
    CausalTemplate,
    WorldModel,
)
from .affect import (
    AffectCore,
    AffectLabel,
    AffectLabels,
    Appraisal,
    PredictionError,
    AffectAppraisal,
)
from .cognition import (
    ContextNow,
    Belief,
    BeliefsNow,
    Hypothesis,
    CognitionWorkspace,
)
from .memory import (
    EpisodicMemory,
    SemanticMemory,
    ProceduralMemory,
    RelationalMemory,
    MemoryRetrievalPolicy,
)
from .planning import (
    Goal,
    GoalsActive,
    Option,
    OptionsSet,
    PlanStep,
    PlanActive,
)
from .social import (
    SocialContext,
    PersonModel,
    AttachmentState,
    ReputationModel,
)

__all__ = [
    # Core
    "Value",
    "Role",
    "SelfConstitution",
    "Trait",
    "FailureMode",
    "SelfModel",
    "Prior",
    "CausalTemplate",
    "WorldModel",
    # Affect
    "AffectCore",
    "AffectLabel",
    "AffectLabels",
    "Appraisal",
    "PredictionError",
    "AffectAppraisal",
    # Cognition
    "ContextNow",
    "Belief",
    "BeliefsNow",
    "Hypothesis",
    "CognitionWorkspace",
    # Memory
    "EpisodicMemory",
    "SemanticMemory",
    "ProceduralMemory",
    "RelationalMemory",
    "MemoryRetrievalPolicy",
    # Planning
    "Goal",
    "GoalsActive",
    "Option",
    "OptionsSet",
    "PlanStep",
    "PlanActive",
    # Social
    "SocialContext",
    "PersonModel",
    "AttachmentState",
    "ReputationModel",
]
