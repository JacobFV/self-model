"""
Cognition models: context, beliefs, and reasoning workspace.

These nodes represent the "thinking bandwidth" - what's currently
in focus, what you believe right now, and the active reasoning process.
"""

from pydantic import BaseModel, Field
from typing import Literal


class ContextNow(BaseModel):
    """
    Current situation summary - the immediate context.

    This is what's happening right now: environment, constraints,
    time pressure, social setting, stakes.

    Update frequency: ~100ms - 1s (instant loop)
    Low stability - changes constantly.
    """
    # Physical/environmental
    location: str = ""
    environment_description: str = ""
    time_of_day: str = ""

    # Temporal
    time_pressure: float = Field(ge=0.0, le=1.0, default=0.3)
    deadline: str | None = None

    # Social
    people_present: list[str] = Field(default_factory=list)
    social_setting: str = ""  # "alone", "intimate", "professional", "public"
    social_stakes: float = Field(ge=0.0, le=1.0, default=0.3)

    # Task
    current_task: str = ""
    task_stakes: float = Field(ge=0.0, le=1.0, default=0.5)

    # Constraints
    active_constraints: list[str] = Field(default_factory=list)

    # Raw input (if coming from sensors/lifelog)
    raw_input: str = ""
    input_source: str = ""  # "manual", "lifelog", "sensor", "api"


class Belief(BaseModel):
    """
    A specific belief held right now with confidence and evidence.
    """
    claim: str
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    evidence: list[str] = Field(default_factory=list)
    source: str = ""  # "observation", "inference", "memory", "told"
    domain: str = ""  # "self", "world", "social", "task"


class BeliefsNow(BaseModel):
    """
    What you think is true right now.

    These are the active beliefs informing current reasoning.
    Lower stability than world_model priors - these are contextual.

    Update frequency: ~1-60s (session loop)
    """
    beliefs: list[Belief] = Field(default_factory=list)

    # Quick access to key situational beliefs
    about_self: str = ""      # Current self-state belief
    about_others: str = ""    # Beliefs about others present
    about_situation: str = "" # Belief about what's happening


class Hypothesis(BaseModel):
    """
    A hypothesis under consideration in the reasoning workspace.
    """
    claim: str
    prior: float = Field(ge=0.0, le=1.0, default=0.5)
    evidence_for: list[str] = Field(default_factory=list)
    evidence_against: list[str] = Field(default_factory=list)
    tests: list[str] = Field(default_factory=list)  # What would change your mind
    status: Literal["active", "accepted", "rejected", "deferred"] = "active"


class CognitionWorkspace(BaseModel):
    """
    The analytical reasoning workspace - explicit "System 2" thinking.

    This is where you do structured reasoning: defining problems,
    generating hypotheses, tracking assumptions, making decisions.

    This is where "System 2 identity" lives - not in voice or style,
    but in consistent reasoning invariants.

    Update frequency: as needed during active reasoning
    Objective: keep thinking clean, minimize self-contradiction, ship decisions
    """
    # The problem at hand
    problem_statement: str = ""

    # Constraints on solutions
    constraints: list[str] = Field(default_factory=list)

    # Explicit assumptions being made
    assumptions: list[str] = Field(default_factory=list)

    # Hypotheses under consideration
    hypotheses: list[Hypothesis] = Field(default_factory=list)

    # Short derivations / reasoning steps
    derivations: list[str] = Field(default_factory=list)

    # Decision + rationale (when reached)
    decision: str = ""
    rationale: str = ""

    # Things being avoided / deferred
    open_loops: list[str] = Field(default_factory=list)

    # Confidence in current reasoning
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)

    # What would change this conclusion
    falsifiers: list[str] = Field(default_factory=list)
