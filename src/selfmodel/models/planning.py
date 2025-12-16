"""
Planning models: goals, options, and plans.

These nodes represent the action-selection system - what you're
trying to achieve, what options you have, and what you're doing.
"""

from pydantic import BaseModel, Field
from typing import Literal


class Goal(BaseModel):
    """
    An active goal with priority and context.
    """
    description: str
    priority: float = Field(ge=0.0, le=1.0, default=0.5)

    # Classification
    horizon: Literal["immediate", "session", "daily", "weekly", "long_term"] = "session"
    domain: str = ""  # "work", "health", "relationship", "learning", etc.

    # Status
    status: Literal["active", "paused", "blocked", "completed", "abandoned"] = "active"
    progress: float = Field(ge=0.0, le=1.0, default=0.0)

    # Dependencies
    requires: list[str] = Field(default_factory=list)
    conflicts_with: list[str] = Field(default_factory=list)

    # Success criteria
    done_when: str = ""

    # Link to constitution
    serves_value: str = ""  # Which value/terminal_goal this serves


class GoalsActive(BaseModel):
    """
    Current objectives with weights.

    This is the active goal stack - what you're trying to achieve
    right now, ordered by priority.

    Update frequency: ~minutes (session loop)
    """
    goals: list[Goal] = Field(default_factory=list)

    # Quick access
    primary_goal: str = ""
    blocked_goals: list[str] = Field(default_factory=list)

    # Conflict detection
    active_conflicts: list[str] = Field(default_factory=list)


class Option(BaseModel):
    """
    A possible action under consideration.
    """
    description: str

    # Evaluation
    expected_value: float = 0.0
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)

    # Pros and cons
    pros: list[str] = Field(default_factory=list)
    cons: list[str] = Field(default_factory=list)

    # Requirements
    requirements: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)

    # Reversibility
    reversible: bool = True
    reversal_cost: str = ""

    # Constitution check
    violates_constitution: bool = False
    constitution_notes: str = ""


class OptionsSet(BaseModel):
    """
    Generated action options for current situation.

    Low stability - regenerated as context changes.
    """
    context_summary: str = ""
    options: list[Option] = Field(default_factory=list)

    # Best option (if evaluated)
    recommended: str = ""
    recommendation_rationale: str = ""

    # What's been ruled out
    rejected: list[str] = Field(default_factory=list)
    rejection_reasons: dict[str, str] = Field(default_factory=dict)


class PlanStep(BaseModel):
    """
    A single step in a plan.
    """
    action: str
    purpose: str = ""

    # Status
    status: Literal["pending", "in_progress", "completed", "skipped", "failed"] = "pending"

    # Dependencies
    depends_on: list[int] = Field(default_factory=list)  # indices of prior steps

    # Timing
    estimated_duration: str = ""
    deadline: str | None = None

    # Notes
    notes: str = ""
    blockers: list[str] = Field(default_factory=list)


class PlanActive(BaseModel):
    """
    The currently active plan.

    Low-medium stability - may be revised as execution proceeds.

    Update frequency: as needed during execution
    """
    # What this plan is for
    goal: str = ""
    context: str = ""

    # The steps
    steps: list[PlanStep] = Field(default_factory=list)

    # Progress
    current_step: int = 0
    status: Literal["active", "paused", "completed", "abandoned"] = "active"

    # Confidence
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    main_risks: list[str] = Field(default_factory=list)

    # Fallback
    fallback_plan: str = ""

    # Learning
    lessons_so_far: list[str] = Field(default_factory=list)
