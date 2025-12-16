"""
Appraiser role: Updates affect state from context.

The Appraiser is responsible for:
- Evaluating the emotional significance of current context
- Updating dimensional affect (valence, arousal, etc.)
- Generating emotion labels and appraisals
- Identifying prediction errors

Runs in the instant loop (~100ms - 1s).
"""

from pydantic import BaseModel, Field

from ..llm import LLMTier
from ..llm.providers import Message
from ..models import AffectCore, AffectLabels, AffectAppraisal, AffectLabel
from .base import Role, RoleResult


class AppraisalOutput(BaseModel):
    """Combined output from the appraiser."""
    affect_core: AffectCore
    primary_emotion: str = ""
    primary_intensity: float = 0.0
    appraisal_summary: str = ""


class Appraiser(Role):
    """
    Updates affect state from context.

    The Appraiser evaluates the emotional significance of the current
    situation and updates:
    - affect_core: Dimensional affect (valence, arousal, dominance, etc.)
    - affect_labels: Discrete emotion hypotheses
    - affect_appraisal: Causal explanation of affect transitions
    """

    name = "appraiser"
    description = "Evaluates emotional significance and updates affect state."
    default_tier = LLMTier.MICRO  # Fast, runs frequently

    reads = ["context_now", "affect_core", "self_model", "beliefs_now"]
    writes = ["affect_core", "affect_labels", "affect_appraisal"]

    async def execute(self, **kwargs) -> RoleResult:
        """
        Evaluate context and update affect state.

        Returns:
            RoleResult with updated affect nodes
        """
        # Read current state
        context = self._read_node("context_now")
        current_affect = self._read_node("affect_core")
        self_model = self._read_node("self_model")

        if not context:
            return RoleResult(
                success=False,
                error="No context available",
            )

        # Build context description
        context_desc = self._describe_context(context)
        affect_desc = self._describe_affect(current_affect) if current_affect else "No previous affect state."
        self_desc = self._describe_self(self_model) if self_model else ""

        messages = [
            Message(
                role="user",
                content=f"""Evaluate the emotional significance of the current situation.

Current context:
{context_desc}

Previous affect state:
{affect_desc}

{self_desc}

Based on this context, determine:
1. Dimensional affect (valence -1 to 1, arousal 0-1, dominance 0-1, tension 0-1, social_safety 0-1, body_load 0-1)
2. Primary emotion and intensity
3. Brief appraisal summary (what's emotionally significant and why)

Consider:
- What emotions would naturally arise from this situation?
- What needs might be activated or threatened?
- What prediction errors (expectation violations) occurred?

Respond with JSON."""
            )
        ]

        try:
            output = await self._complete(
                messages=messages,
                response_model=AppraisalOutput,
                system=self._get_system_prompt(),
            )

            # Write affect_core
            await self._write_node("affect_core", output.affect_core)

            # Create and write affect_labels
            labels = AffectLabels(
                emotions=[AffectLabel(
                    name=output.primary_emotion,
                    intensity=output.primary_intensity,
                )] if output.primary_emotion else [],
                primary_emotion=output.primary_emotion,
                primary_intensity=output.primary_intensity,
            )
            await self._write_node("affect_labels", labels)

            # Create and write affect_appraisal
            appraisal = AffectAppraisal(
                meaning=output.appraisal_summary,
            )
            await self._write_node("affect_appraisal", appraisal)

            return RoleResult(
                success=True,
                updates={
                    "affect_core": output.affect_core.model_dump(),
                    "affect_labels": labels.model_dump(),
                    "affect_appraisal": appraisal.model_dump(),
                },
                messages=[
                    f"Affect: valence={output.affect_core.valence:.2f}, "
                    f"arousal={output.affect_core.arousal:.2f}",
                    f"Primary emotion: {output.primary_emotion} "
                    f"({output.primary_intensity:.1f})",
                ],
            )

        except Exception as e:
            return RoleResult(
                success=False,
                error=str(e),
            )

    def _describe_context(self, context) -> str:
        """Format context for the prompt."""
        parts = []
        if context.location:
            parts.append(f"Location: {context.location}")
        if context.current_task:
            parts.append(f"Task: {context.current_task}")
        if context.people_present:
            parts.append(f"People: {', '.join(context.people_present)}")
        if context.social_setting:
            parts.append(f"Setting: {context.social_setting}")
        if context.time_pressure > 0.5:
            parts.append(f"Time pressure: high ({context.time_pressure:.1f})")
        if context.raw_input:
            parts.append(f"Raw input: {context.raw_input[:200]}")
        return "\n".join(parts) if parts else "No context details."

    def _describe_affect(self, affect) -> str:
        """Format affect for the prompt."""
        return (
            f"Valence: {affect.valence:.2f} (negative to positive)\n"
            f"Arousal: {affect.arousal:.2f} (calm to activated)\n"
            f"Dominance: {affect.dominance:.2f} (controlled to in-control)\n"
            f"Tension: {affect.tension:.2f}\n"
            f"Social safety: {affect.social_safety:.2f}\n"
            f"Body load: {affect.body_load:.2f}"
        )

    def _describe_self(self, self_model) -> str:
        """Format self-model relevant info."""
        if not self_model:
            return ""

        parts = ["Relevant self-knowledge:"]
        if self_model.failure_modes:
            modes = [fm.name for fm in self_model.failure_modes[:3]]
            parts.append(f"Known failure modes: {', '.join(modes)}")
        if self_model.energy_drains:
            parts.append(f"Energy drains: {', '.join(self_model.energy_drains[:3])}")

        return "\n".join(parts)
