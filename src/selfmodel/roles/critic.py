"""
Critic role: Checks coherence with constitution.

The Critic is responsible for:
- Checking proposed actions against constitution
- Detecting identity drift
- Flagging violations of nonnegotiables
- Maintaining value alignment

Runs when decisions are made or periodically to check drift.
"""

from pydantic import BaseModel, Field

from ..llm import LLMTier
from ..llm.providers import Message
from ..models import SelfConstitution
from .base import Role, RoleResult


class ConstitutionCheck(BaseModel):
    """Result of checking against constitution."""
    aligned: bool = True
    violations: list[str] = Field(default_factory=list)
    concerns: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)


class DriftAnalysis(BaseModel):
    """Analysis of identity drift."""
    drift_detected: bool = False
    drift_direction: str = ""
    drift_severity: float = Field(ge=0.0, le=1.0, default=0.0)
    affected_values: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class Critic(Role):
    """
    Checks coherence with constitution and detects drift.

    The Critic ensures that:
    - Proposed actions align with values
    - Nonnegotiables are not violated
    - Identity drift is detected early
    - Decision principles are applied

    This role is critical for maintaining stable identity.
    """

    name = "critic"
    description = "Checks value alignment and detects identity drift."
    default_tier = LLMTier.HEAVY  # Important decisions need careful evaluation

    reads = ["self_constitution", "self_model", "affect_appraisal", "plan_active", "goals_active"]
    writes = []  # Critic doesn't write directly, it advises

    async def execute(
        self,
        action: str | None = None,
        check_drift: bool = False,
        **kwargs,
    ) -> RoleResult:
        """
        Check alignment or detect drift.

        Args:
            action: Optional action to check against constitution
            check_drift: Whether to perform drift analysis

        Returns:
            RoleResult with alignment/drift analysis
        """
        constitution = self._read_node("self_constitution")

        if not constitution:
            return RoleResult(
                success=False,
                error="No constitution defined - cannot check alignment",
            )

        try:
            results = {}
            messages = []

            if action:
                check = await self._check_action(action, constitution)
                results["constitution_check"] = check.model_dump()

                if check.aligned:
                    messages.append(f"Action aligned with constitution (confidence: {check.confidence:.0%})")
                else:
                    messages.append(f"ALIGNMENT WARNING: {', '.join(check.violations)}")

                if check.concerns:
                    messages.append(f"Concerns: {', '.join(check.concerns)}")

            if check_drift:
                drift = await self._analyze_drift(constitution)
                results["drift_analysis"] = drift.model_dump()

                if drift.drift_detected:
                    messages.append(
                        f"DRIFT DETECTED: {drift.drift_direction} "
                        f"(severity: {drift.drift_severity:.0%})"
                    )
                else:
                    messages.append("No significant identity drift detected")

            return RoleResult(
                success=True,
                updates=results,
                messages=messages,
            )

        except Exception as e:
            return RoleResult(
                success=False,
                error=str(e),
            )

    async def check_action(self, action: str) -> ConstitutionCheck:
        """
        Check if an action aligns with constitution.

        Public convenience method.
        """
        constitution = self._read_node("self_constitution")
        if not constitution:
            return ConstitutionCheck(
                aligned=False,
                violations=["No constitution defined"],
            )
        return await self._check_action(action, constitution)

    async def _check_action(
        self,
        action: str,
        constitution: SelfConstitution,
    ) -> ConstitutionCheck:
        """Check an action against the constitution."""
        # Format constitution for prompt
        const_desc = self._format_constitution(constitution)

        messages = [
            Message(
                role="user",
                content=f"""Evaluate this proposed action against the constitution.

CONSTITUTION:
{const_desc}

PROPOSED ACTION:
{action}

Check for:
1. Violations of nonnegotiables (hard failures)
2. Conflicts with values (soft concerns)
3. Violation of taboos
4. Inconsistency with identity claims
5. Failure to apply relevant decision principles

Be strict about nonnegotiables - any violation means not aligned.
Be nuanced about values - consider context and tradeoffs.

Respond with:
- aligned: true/false
- violations: list of hard violations (if any)
- concerns: list of soft concerns (if any)
- suggestions: how to modify action to align better
- confidence: 0-1 in your assessment"""
            )
        ]

        return await self._complete(
            messages=messages,
            response_model=ConstitutionCheck,
            system=self._get_system_prompt(),
        )

    async def _analyze_drift(self, constitution: SelfConstitution) -> DriftAnalysis:
        """Analyze recent state for identity drift."""
        # Get recent affect and goals
        affect = self._read_node("affect_appraisal")
        goals = self._read_node("goals_active")
        plan = self._read_node("plan_active")

        recent_state = []
        if affect and affect.meaning:
            recent_state.append(f"Recent affect meaning: {affect.meaning}")
        if goals and goals.primary_goal:
            recent_state.append(f"Primary goal: {goals.primary_goal}")
        if plan and plan.goal:
            recent_state.append(f"Active plan: {plan.goal}")

        recent_str = "\n".join(recent_state) if recent_state else "No recent state available"

        const_desc = self._format_constitution(constitution)

        messages = [
            Message(
                role="user",
                content=f"""Analyze for identity drift - is the recent behavior/state
consistent with the defined constitution?

CONSTITUTION:
{const_desc}

RECENT STATE:
{recent_str}

Look for:
1. Gradual departure from stated values
2. Pursuing goals inconsistent with terminal goals
3. Emotional patterns that suggest value conflict
4. Actions that contradict identity claims

Identity drift is subtle - it's not about single violations but patterns
of moving away from the defined self.

Respond with:
- drift_detected: true/false
- drift_direction: if detected, describe the direction (e.g., "toward short-term over long-term")
- drift_severity: 0-1 (0 = no drift, 1 = severe departure)
- affected_values: which values are being deprioritized
- recommendations: how to course-correct"""
            )
        ]

        return await self._complete(
            messages=messages,
            response_model=DriftAnalysis,
            system=self._get_system_prompt(),
        )

    def _format_constitution(self, constitution: SelfConstitution) -> str:
        """Format constitution for prompts."""
        parts = []

        if constitution.values:
            values_str = ", ".join(
                f"{v.name} ({v.weight:.1f})" for v in constitution.values[:5]
            )
            parts.append(f"Values: {values_str}")

        if constitution.terminal_goals:
            parts.append(f"Terminal goals: {', '.join(constitution.terminal_goals[:3])}")

        if constitution.nonnegotiables:
            parts.append(f"Nonnegotiables: {', '.join(constitution.nonnegotiables)}")

        if constitution.taboos:
            parts.append(f"Taboos: {', '.join(constitution.taboos)}")

        if constitution.decision_principles:
            parts.append(f"Decision principles: {'; '.join(constitution.decision_principles[:3])}")

        if constitution.identity_claims:
            parts.append(f"Identity claims: {'; '.join(constitution.identity_claims[:3])}")

        return "\n".join(parts)
