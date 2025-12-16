"""
Social models: social context, person models, attachment state.

Even if you want "pure System 2," your priors about other minds
are part of your policy. These nodes track the social dimension.
"""

from pydantic import BaseModel, Field
from typing import Literal


class SocialContext(BaseModel):
    """
    Current social field - who's here, stakes, norms.

    This is the immediate social context that shapes behavior.

    Update frequency: ~1-60s (when social context changes)
    """
    # Who's present
    people: list[str] = Field(default_factory=list)
    relationship_to_me: dict[str, str] = Field(default_factory=dict)

    # Setting
    setting: Literal["alone", "intimate", "small_group", "professional", "public", "anonymous"] = "alone"
    formality: float = Field(ge=0.0, le=1.0, default=0.5)

    # Stakes
    social_stakes: float = Field(ge=0.0, le=1.0, default=0.3)
    reputation_at_risk: bool = False
    trust_at_risk: bool = False

    # Norms
    active_norms: list[str] = Field(default_factory=list)
    taboos_here: list[str] = Field(default_factory=list)

    # Power dynamics
    power_differential: float = Field(ge=-1.0, le=1.0, default=0.0)
    # -1 = I have less power, +1 = I have more power

    # Current interaction
    interaction_type: str = ""  # "negotiation", "collaboration", "conflict", "casual"
    my_role: str = ""


class PersonModel(BaseModel):
    """
    Model of a specific person in current context.

    More detailed than RelationalMemory - this is the
    active working model used for prediction/interaction.
    """
    name: str
    relationship: str = ""

    # Their current state (as I perceive it)
    apparent_mood: str = ""
    apparent_goals: list[str] = Field(default_factory=list)
    apparent_concerns: list[str] = Field(default_factory=list)

    # Their model of me (theory of mind)
    their_view_of_me: str = ""
    what_they_want_from_me: str = ""

    # Predictions
    likely_next_action: str = ""
    likely_reactions: dict[str, str] = Field(default_factory=dict)

    # Trust
    my_trust_in_them: float = Field(ge=0.0, le=1.0, default=0.5)
    their_trust_in_me: float = Field(ge=0.0, le=1.0, default=0.5)

    # Notes
    active_concerns: list[str] = Field(default_factory=list)


class AttachmentState(BaseModel):
    """
    Current closeness/avoidance dynamics.

    How attachment system is activated right now.

    Update frequency: ~minutes to hours
    """
    # Activation
    attachment_system_active: bool = False
    activation_level: float = Field(ge=0.0, le=1.0, default=0.0)

    # Direction
    seeking_closeness: bool = False
    seeking_distance: bool = False
    target: str = ""

    # Triggers
    current_triggers: list[str] = Field(default_factory=list)

    # State
    felt_security: float = Field(ge=0.0, le=1.0, default=0.7)
    abandonment_fear: float = Field(ge=0.0, le=1.0, default=0.0)
    engulfment_fear: float = Field(ge=0.0, le=1.0, default=0.0)

    # Patterns active
    active_patterns: list[str] = Field(default_factory=list)
    # e.g., "protest behavior", "deactivation", "hyperactivation"


class ReputationModel(BaseModel):
    """
    How you think you're perceived by others.
    """
    # General
    perceived_competence: float = Field(ge=0.0, le=1.0, default=0.5)
    perceived_warmth: float = Field(ge=0.0, le=1.0, default=0.5)
    perceived_integrity: float = Field(ge=0.0, le=1.0, default=0.5)

    # Specific attributions
    known_for: list[str] = Field(default_factory=list)
    concerns_about_me: list[str] = Field(default_factory=list)

    # By group
    reputation_by_context: dict[str, str] = Field(default_factory=dict)
    # e.g., {"work": "reliable but intense", "friends": "fun but flaky"}

    # Recent changes
    recent_reputation_events: list[str] = Field(default_factory=list)
