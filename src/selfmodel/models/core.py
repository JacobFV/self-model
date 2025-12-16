"""
Core identity models: constitution, self-model, world-model.

These are the high-stability nodes that define "who you are" and "how you
understand reality." They update rarely and anchor the entire system.
"""

from pydantic import BaseModel, Field


class Value(BaseModel):
    """
    A core value that guides decision-making.

    Example:
        Value(
            name="truth",
            description="Commitment to accurate beliefs over comfortable ones",
            weight=0.9,
            contexts=["intellectual discourse", "self-reflection"]
        )
    """
    name: str
    description: str
    weight: float = Field(ge=0.0, le=1.0, default=0.5)
    contexts: list[str] = Field(default_factory=list)


class Role(BaseModel):
    """
    A role or identity facet with role-specific constraints.

    Example:
        Role(
            name="engineer",
            description="Builder of systems",
            constraints=["prioritize correctness", "document decisions"],
            active=True
        )
    """
    name: str
    description: str = ""
    constraints: list[str] = Field(default_factory=list)
    active: bool = True


class SelfConstitution(BaseModel):
    """
    The transferable core - your chosen self.

    This is the anchor node. High stability, rarely updated.
    It defines what you value, what you won't compromise on,
    and the kind of agent you choose to be.

    Update triggers: weekly + after major life decisions
    Objective: coherence over time, not reactivity
    """
    # What matters
    values: list[Value] = Field(default_factory=list)

    # Long-run ends
    terminal_goals: list[str] = Field(default_factory=list)

    # Hard constraints - never violate
    nonnegotiables: list[str] = Field(default_factory=list)

    # Decision heuristics: "when X, prefer Y"
    decision_principles: list[str] = Field(default_factory=list)

    # Things you won't do even if locally optimal
    taboos: list[str] = Field(default_factory=list)

    # "I am the kind of agent who..."
    identity_claims: list[str] = Field(default_factory=list)

    # Roles with their constraints
    roles: list[Role] = Field(default_factory=list)

    # What "good" feels like, in language
    reward_description: str = ""


class Trait(BaseModel):
    """
    A personality trait or behavioral pattern.

    Not astrology - conditional patterns with confidence.
    """
    name: str
    description: str = ""
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    contexts: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)


class FailureMode(BaseModel):
    """
    A known failure pattern - spiral, avoidance loop, etc.

    Naming failure modes explicitly allows the system to
    detect and intervene on them.
    """
    name: str
    description: str
    triggers: list[str] = Field(default_factory=list)
    symptoms: list[str] = Field(default_factory=list)
    interventions: list[str] = Field(default_factory=list)


class SelfModel(BaseModel):
    """
    What you believe you are, mechanistically.

    This is your predictive model of your own behavior.
    High stability, but updates based on evidence.

    Objective: predictive accuracy about your own behavior
    """
    # Conditional patterns
    traits: list[Trait] = Field(default_factory=list)

    # What you can do
    capabilities: list[str] = Field(default_factory=list)

    # What you can't do (yet)
    limits: list[str] = Field(default_factory=list)

    # Known spirals, avoidance loops, failure patterns
    failure_modes: list[FailureMode] = Field(default_factory=list)

    # Speed/rigor/obsession patterns
    cognitive_styles: list[str] = Field(default_factory=list)

    # What drains/charges you
    energy_sources: list[str] = Field(default_factory=list)
    energy_drains: list[str] = Field(default_factory=list)

    # How closeness shifts your control system
    attachment_style: str = ""
    attachment_notes: str = ""


class Prior(BaseModel):
    """
    A belief about how the world tends to work.

    Example:
        Prior(
            claim="incentives dominate narratives",
            confidence=0.8,
            domain="institutions"
        )
    """
    claim: str
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    domain: str = ""
    evidence: list[str] = Field(default_factory=list)
    counterevidence: list[str] = Field(default_factory=list)


class CausalTemplate(BaseModel):
    """
    A reusable causal mechanism / mental model.

    Example:
        CausalTemplate(
            name="reinforcing feedback loop",
            structure="A increases B, B increases A",
            examples=["addiction", "compound interest", "viral growth"]
        )
    """
    name: str
    structure: str
    examples: list[str] = Field(default_factory=list)
    domains: list[str] = Field(default_factory=list)


class WorldModel(BaseModel):
    """
    Your compressed ontology of reality.

    This is your map of how the world works - priors, causal
    templates, domain knowledge, and known unknowns.

    Objective: explain + predict environment with minimum description length
    """
    # "The world tends to..."
    priors: list[Prior] = Field(default_factory=list)

    # Reusable mechanisms
    causal_templates: list[CausalTemplate] = Field(default_factory=list)

    # Domain-specific knowledge summaries
    domain_maps: dict[str, str] = Field(default_factory=dict)

    # Things you know you don't know
    unknowns: list[str] = Field(default_factory=list)

    # How to learn the unknowns
    learning_strategies: dict[str, str] = Field(default_factory=dict)
