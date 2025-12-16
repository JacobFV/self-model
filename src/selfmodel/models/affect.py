"""
Affect models: emotional state, labels, and appraisals.

Emotions are not poetry - they're control variables that shape
attention, decision-making, and action. Modeling them explicitly
allows the system to predict behavior and intervene safely.
"""

from pydantic import BaseModel, Field


class AffectCore(BaseModel):
    """
    Continuous affect state - the nervous system's regime.

    These are dimensional measures that update frequently (instant loop).
    They don't tell you *what* you're feeling, just the shape of it.

    Update frequency: ~100ms - 1s
    Objective: track your nervous-system regime
    """
    # Bad <-> Good (-1 to 1)
    valence: float = Field(ge=-1.0, le=1.0, default=0.0)

    # Calm <-> Activated (0 to 1)
    arousal: float = Field(ge=0.0, le=1.0, default=0.5)

    # Controlled <-> In-control (0 to 1)
    dominance: float = Field(ge=0.0, le=1.0, default=0.5)

    # Internal pressure / stress (0 to 1)
    tension: float = Field(ge=0.0, le=1.0, default=0.3)

    # Felt safety in social context (0 to 1)
    social_safety: float = Field(ge=0.0, le=1.0, default=0.7)

    # Physical load: fatigue, hunger, pain (0 to 1)
    body_load: float = Field(ge=0.0, le=1.0, default=0.3)


class AffectLabel(BaseModel):
    """
    A discrete emotion hypothesis with action tendency.

    This converts dimensional affect into interpretable categories
    that have implications for behavior.

    Example:
        AffectLabel(
            name="anxiety",
            intensity=0.7,
            trigger="upcoming presentation",
            object="potential judgment",
            action_tendency="avoid/prepare"
        )
    """
    name: str  # "anxiety", "curiosity", "shame", "desire", etc.
    intensity: float = Field(ge=0.0, le=1.0, default=0.5)
    trigger: str | None = None  # What caused it
    object: str | None = None   # What it's about
    action_tendency: str | None = None  # "avoid", "approach", "freeze", "confront"


class Need(BaseModel):
    """
    An unmet need generating motivational pressure.
    """
    name: str  # "connection", "autonomy", "competence", "rest"
    deficit: float = Field(ge=0.0, le=1.0, default=0.5)
    proposed_satisfaction: str = ""


class AffectLabels(BaseModel):
    """
    Interpretable emotion hypotheses and needs.

    Converts continuous affect into actionable categories.

    Update frequency: ~1-10s
    Objective: convert continuous affect into actionable hypotheses
    """
    emotions: list[AffectLabel] = Field(default_factory=list)
    needs: list[Need] = Field(default_factory=list)

    # Dominant emotion (for quick access)
    primary_emotion: str | None = None
    primary_intensity: float = 0.0


class Appraisal(BaseModel):
    """
    A cognitive appraisal driving affect.

    Appraisals are the "why" behind emotions - the interpretation
    of events that generates the emotional response.
    """
    type: str  # "threat", "loss", "violation", "opportunity", "status_change"
    target: str  # What was appraised
    evaluation: str  # The judgment made
    intensity: float = Field(ge=0.0, le=1.0, default=0.5)


class PredictionError(BaseModel):
    """
    A violated expectation that updated affect.

    Tracking prediction errors helps understand why emotional
    state changed and supports learning.
    """
    expected: str
    actual: str
    domain: str = ""  # "social", "task", "self", "world"
    magnitude: float = Field(ge=0.0, le=1.0, default=0.5)
    implications: str = ""


class AffectAppraisal(BaseModel):
    """
    The causal explanation of affect transitions.

    This node answers "why did my emotional state change?"
    It bridges perception/context to felt affect.

    Update frequency: ~1-30s (after significant affect changes)
    Objective: generate causal explanation of affect transitions

    Note: constitution can read appraisal but not be rewritten by it
    (unless explicitly allowed) - this prevents mood-driven identity drift.
    """
    # Cognitive appraisals driving current affect
    appraisals: list[Appraisal] = Field(default_factory=list)

    # Violated expectations
    prediction_errors: list[PredictionError] = Field(default_factory=list)

    # High-level meaning assignment
    meaning: str = ""  # "What this implies about me/the world"

    # Attribution
    cause_internal: float = Field(ge=0.0, le=1.0, default=0.5)  # vs external
    cause_stable: float = Field(ge=0.0, le=1.0, default=0.5)    # vs temporary
    cause_global: float = Field(ge=0.0, le=1.0, default=0.5)    # vs specific
