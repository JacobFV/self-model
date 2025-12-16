"""
Memory models: different memory stores and retrieval policies.

Memory stores are separated because "identity" != "episodic detail".
Different types of memory serve different functions and have
different retrieval needs.
"""

from pydantic import BaseModel, Field
from typing import Literal


class EpisodicMemory(BaseModel):
    """
    A time-stamped episodic memory - what happened.

    These are specific events with context, not abstract knowledge.
    """
    # When
    timestamp: str = ""  # ISO format or relative

    # What happened
    event: str
    details: str = ""

    # Context
    location: str = ""
    people: list[str] = Field(default_factory=list)

    # Subjective experience
    thoughts: str = ""
    feelings: str = ""

    # Significance
    importance: float = Field(ge=0.0, le=1.0, default=0.5)
    tags: list[str] = Field(default_factory=list)

    # Links
    related_memories: list[str] = Field(default_factory=list)


class SemanticMemory(BaseModel):
    """
    Factual/conceptual knowledge - your personal wiki.

    Facts, concepts, explanations that aren't time-bound.
    """
    # The content
    topic: str
    content: str

    # Organization
    domain: str = ""
    tags: list[str] = Field(default_factory=list)

    # Confidence and source
    confidence: float = Field(ge=0.0, le=1.0, default=0.7)
    sources: list[str] = Field(default_factory=list)

    # Links
    related: list[str] = Field(default_factory=list)


class ProceduralStep(BaseModel):
    """A single step in a procedure."""
    action: str
    notes: str = ""
    common_errors: list[str] = Field(default_factory=list)


class ProceduralMemory(BaseModel):
    """
    "How I do X" - playbooks, scripts, rituals.

    Procedural knowledge about how to accomplish things.
    """
    name: str
    description: str = ""

    # The procedure
    steps: list[ProceduralStep] = Field(default_factory=list)

    # When to use
    triggers: list[str] = Field(default_factory=list)
    contexts: list[str] = Field(default_factory=list)

    # Quality
    proficiency: float = Field(ge=0.0, le=1.0, default=0.5)
    last_used: str = ""


class RelationalMemory(BaseModel):
    """
    Model of a person - who they are, your relationship.

    Not just facts about them, but your working model of
    their mind, your dynamics, trust levels.
    """
    name: str
    relationship: str = ""  # "friend", "colleague", "family", etc.

    # Their model
    personality_summary: str = ""
    values: list[str] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)
    communication_style: str = ""

    # Your dynamics
    trust_level: float = Field(ge=0.0, le=1.0, default=0.5)
    closeness: float = Field(ge=0.0, le=1.0, default=0.5)
    history_summary: str = ""

    # Practical
    contact_info: str = ""
    last_contact: str = ""

    # Predictions
    likely_reactions: dict[str, str] = Field(default_factory=dict)


class MemoryRetrievalPolicy(BaseModel):
    """
    How memories get surfaced into context.

    This is the weighting mechanism that decides what memories
    are relevant to the current situation.

    High stability - this is part of your cognitive style.
    """
    # Relevance weights
    recency_weight: float = Field(ge=0.0, le=1.0, default=0.3)
    salience_weight: float = Field(ge=0.0, le=1.0, default=0.3)
    similarity_weight: float = Field(ge=0.0, le=1.0, default=0.3)
    goal_relevance_weight: float = Field(ge=0.0, le=1.0, default=0.4)

    # Source trust weights
    self_report_trust: float = Field(ge=0.0, le=1.0, default=0.7)
    inference_trust: float = Field(ge=0.0, le=1.0, default=0.5)
    external_trust: float = Field(ge=0.0, le=1.0, default=0.6)

    # Biases (explicit, not hidden)
    emotional_gating: float = Field(ge=0.0, le=1.0, default=0.3)
    # How much current affect influences retrieval

    coherence_bias: float = Field(ge=0.0, le=1.0, default=0.4)
    # Preference for memories that support existing narrative

    counter_coherence_bias: float = Field(ge=0.0, le=1.0, default=0.2)
    # Counter-bias to prevent self-delusion

    # Limits
    max_episodic_per_query: int = 10
    max_semantic_per_query: int = 10


class AffectiveMemory(BaseModel):
    """
    What reliably shifts affect - songs, places, interactions.

    These are indexed by their emotional effect, not their content.
    """
    trigger: str
    trigger_type: Literal["song", "place", "person", "activity", "image", "phrase", "other"] = "other"
    emotional_effect: str
    valence_shift: float = Field(ge=-1.0, le=1.0, default=0.0)
    arousal_shift: float = Field(ge=-1.0, le=1.0, default=0.0)
    reliability: float = Field(ge=0.0, le=1.0, default=0.5)
    notes: str = ""


class IdentityMemory(BaseModel):
    """
    Key moments that updated self.model or constitution.

    These are the memories that define who you are - the
    pivotal moments, decisions, realizations.
    """
    description: str
    when: str = ""

    # What changed
    before: str = ""
    after: str = ""
    what_updated: Literal["constitution", "self_model", "world_model", "other"] = "other"

    # Why it mattered
    significance: str = ""
    lessons: list[str] = Field(default_factory=list)
