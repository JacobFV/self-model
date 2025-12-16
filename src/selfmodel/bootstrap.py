"""
Bootstrap: Initialize new profiles with starter state.

The bootstrap module provides:
- Default constitution templates
- Initial state for all nodes
- Interactive profile creation
"""

from dataclasses import dataclass
from pathlib import Path

from .profile import Profile
from .store import StateStore, open_store
from .models import (
    # Core
    SelfConstitution, Value, Role, SelfModel, Trait, WorldModel, Prior,
    # Affect
    AffectCore, AffectLabels, AffectAppraisal,
    # Cognition
    ContextNow, BeliefsNow, CognitionWorkspace,
    # Memory
    MemoryRetrievalPolicy,
    # Planning
    GoalsActive, Goal, OptionsSet, PlanActive,
    # Social
    SocialContext, AttachmentState,
)


@dataclass
class BootstrapConfig:
    """Configuration for bootstrap."""
    include_example_values: bool = True
    include_example_goals: bool = True
    base_dir: str = "state"


# Default constitution template
DEFAULT_CONSTITUTION = SelfConstitution(
    values=[
        Value(
            name="truth",
            description="Commitment to accurate beliefs over comfortable ones",
            weight=0.9,
        ),
        Value(
            name="growth",
            description="Continuous learning and improvement",
            weight=0.8,
        ),
        Value(
            name="integrity",
            description="Alignment between stated values and actions",
            weight=0.9,
        ),
        Value(
            name="agency",
            description="Maintaining capacity for autonomous choice",
            weight=0.8,
        ),
    ],
    terminal_goals=[
        "Understand myself and reality accurately",
        "Build useful things that help others",
        "Maintain genuine relationships",
    ],
    nonnegotiables=[
        "Never deceive myself about important matters",
        "Never harm others for personal gain",
        "Maintain the ability to change my mind with evidence",
    ],
    decision_principles=[
        "When uncertain, gather more information before committing",
        "Prefer reversible decisions over irreversible ones",
        "Consider long-term effects, not just immediate benefits",
        "When values conflict, prioritize based on context",
    ],
    taboos=[
        "Willful self-deception",
        "Betraying trust for convenience",
        "Abandoning principles under social pressure",
    ],
    identity_claims=[
        "I am someone who seeks truth",
        "I am someone who builds things",
        "I am someone who keeps commitments",
    ],
    roles=[
        Role(name="thinker", description="Analytical, curious explorer of ideas"),
        Role(name="builder", description="Creator of systems and solutions"),
    ],
    reward_description="Clarity of understanding, progress on meaningful work, genuine connection",
)

# Default self-model
DEFAULT_SELF_MODEL = SelfModel(
    traits=[
        Trait(name="curious", description="Drawn to understanding how things work", confidence=0.7),
        Trait(name="analytical", description="Tends to break down problems systematically", confidence=0.6),
    ],
    capabilities=["reasoning", "learning", "self-reflection"],
    limits=["attention span", "emotional regulation under stress"],
    failure_modes=[],
    cognitive_styles=["prefers depth over breadth", "thinks in systems"],
    energy_sources=["interesting problems", "meaningful progress", "good conversations"],
    energy_drains=["bureaucracy", "unclear expectations", "social performance"],
)

# Default world-model
DEFAULT_WORLD_MODEL = WorldModel(
    priors=[
        Prior(claim="Incentives shape behavior more than intentions", confidence=0.8),
        Prior(claim="Complex systems have unexpected emergent properties", confidence=0.7),
        Prior(claim="Most things are harder than they first appear", confidence=0.8),
    ],
    causal_templates=[],
    domain_maps={},
    unknowns=["What I don't know that I don't know"],
)

# Default affect state
DEFAULT_AFFECT = AffectCore(
    valence=0.0,
    arousal=0.3,
    dominance=0.5,
    tension=0.2,
    social_safety=0.7,
    body_load=0.2,
)

# Default memory retrieval policy
DEFAULT_RETRIEVAL_POLICY = MemoryRetrievalPolicy(
    recency_weight=0.3,
    salience_weight=0.3,
    similarity_weight=0.3,
    goal_relevance_weight=0.4,
    emotional_gating=0.3,
    coherence_bias=0.4,
    counter_coherence_bias=0.2,
)


def bootstrap_profile(
    profile: Profile | str,
    config: BootstrapConfig | None = None,
    constitution: SelfConstitution | None = None,
    base_dir: str | Path | None = None,
) -> StateStore:
    """
    Initialize a new profile with starter state.

    Args:
        profile: Profile to initialize
        config: Bootstrap configuration
        constitution: Custom constitution (uses default if not provided)
        base_dir: Base directory for state (overrides config.base_dir)

    Returns:
        Initialized StateStore
    """
    config = config or BootstrapConfig()

    if isinstance(profile, str):
        profile = Profile.parse(profile)

    # Use explicit base_dir if provided, otherwise use config
    actual_base_dir = base_dir if base_dir is not None else config.base_dir
    store = open_store(profile, actual_base_dir)

    # Initialize core nodes
    store.self_constitution.append(constitution or DEFAULT_CONSTITUTION)
    store.self_model.append(DEFAULT_SELF_MODEL)
    store.world_model.append(DEFAULT_WORLD_MODEL)

    # Initialize affect
    store.affect_core.append(DEFAULT_AFFECT)
    store.affect_labels.append(AffectLabels())
    store.affect_appraisal.append(AffectAppraisal())

    # Initialize cognition
    store.context_now.append(ContextNow(
        location="unknown",
        social_setting="alone",
        current_task="initializing",
    ))
    store.beliefs_now.append(BeliefsNow(
        about_self="Just initialized, getting oriented",
        about_situation="Starting fresh",
    ))
    store.cognition_workspace.append(CognitionWorkspace())

    # Initialize memory policy
    store.memory_retrieval_policy.append(DEFAULT_RETRIEVAL_POLICY)

    # Initialize planning
    if config.include_example_goals:
        store.goals_active.append(GoalsActive(
            goals=[
                Goal(
                    description="Get oriented and understand current situation",
                    priority=0.8,
                    horizon="immediate",
                ),
            ],
            primary_goal="Get oriented and understand current situation",
        ))
    else:
        store.goals_active.append(GoalsActive())

    store.options_set.append(OptionsSet())
    store.plan_active.append(PlanActive())

    # Initialize social
    store.social_context.append(SocialContext())
    store.attachment_state.append(AttachmentState())

    return store


def create_minimal_profile(
    name: str,
    tier: str = "light",
    version: str = "v1",
    persona: str | None = None,
    base_dir: str = "state",
) -> StateStore:
    """
    Create a minimal profile with just the essentials.

    Useful for testing or lightweight instances.
    """
    profile = Profile(name=name, tier=tier, version=version, persona=persona)
    store = open_store(profile, base_dir)

    # Just the bare minimum
    store.self_constitution.append(SelfConstitution(
        values=[Value(name="truth", description="Seek truth", weight=0.9)],
        nonnegotiables=["Be honest"],
        identity_claims=["I seek understanding"],
    ))
    store.affect_core.append(AffectCore())
    store.context_now.append(ContextNow())
    store.beliefs_now.append(BeliefsNow())
    store.goals_active.append(GoalsActive())

    return store


def create_constitution_interactive() -> SelfConstitution:
    """
    Interactive constitution builder.

    Note: This is a placeholder for a more sophisticated
    interactive session that would guide someone through
    defining their values, goals, and identity.
    """
    print("Constitution Builder")
    print("=" * 40)
    print()

    values = []
    print("Enter your core values (empty to finish):")
    while True:
        name = input("  Value name: ").strip()
        if not name:
            break
        desc = input("  Description: ").strip()
        weight = float(input("  Weight (0-1): ") or "0.7")
        values.append(Value(name=name, description=desc, weight=weight))

    goals = []
    print("\nEnter your terminal goals (empty to finish):")
    while True:
        goal = input("  Goal: ").strip()
        if not goal:
            break
        goals.append(goal)

    nonnegotiables = []
    print("\nEnter your non-negotiables (empty to finish):")
    while True:
        nn = input("  Non-negotiable: ").strip()
        if not nn:
            break
        nonnegotiables.append(nn)

    identity_claims = []
    print("\nComplete: 'I am someone who...' (empty to finish):")
    while True:
        claim = input("  I am someone who... ").strip()
        if not claim:
            break
        identity_claims.append(f"I am someone who {claim}")

    return SelfConstitution(
        values=values or DEFAULT_CONSTITUTION.values,
        terminal_goals=goals or DEFAULT_CONSTITUTION.terminal_goals,
        nonnegotiables=nonnegotiables or DEFAULT_CONSTITUTION.nonnegotiables,
        identity_claims=identity_claims or DEFAULT_CONSTITUTION.identity_claims,
    )


# CLI entry point
def main():
    """Bootstrap CLI."""
    import argparse

    parser = argparse.ArgumentParser(description="Bootstrap a self-model profile")
    parser.add_argument("profile", help="Profile key (e.g., jacob-heavy-v1)")
    parser.add_argument("--base-dir", default="state", help="Base directory for state")
    parser.add_argument("--minimal", action="store_true", help="Create minimal profile")
    parser.add_argument("--interactive", action="store_true", help="Interactive constitution builder")

    args = parser.parse_args()

    profile = Profile.parse(args.profile)
    print(f"Bootstrapping profile: {profile.key}")

    if args.interactive:
        constitution = create_constitution_interactive()
        store = bootstrap_profile(
            profile,
            config=BootstrapConfig(base_dir=args.base_dir),
            constitution=constitution,
        )
    elif args.minimal:
        store = create_minimal_profile(
            name=profile.name,
            tier=profile.tier,
            version=profile.version,
            persona=profile.persona,
            base_dir=args.base_dir,
        )
    else:
        store = bootstrap_profile(
            profile,
            config=BootstrapConfig(base_dir=args.base_dir),
        )

    print(f"Profile initialized at: {store.state_dir}")
    print(f"Constitution: {len(store.now.self_constitution.values)} values")
    print(f"Goals: {len(store.now.goals_active.goals) if store.now.goals_active else 0}")


if __name__ == "__main__":
    main()
