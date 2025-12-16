"""
Analyst role: Updates beliefs and cognition workspace.

The Analyst is responsible for:
- Maintaining current beliefs about the situation
- Structured reasoning in the cognition workspace
- Generating and evaluating hypotheses
- Making decisions with rationales

Runs in the session loop (~1-5 minutes).
"""

from pydantic import BaseModel, Field

from ..llm import LLMTier
from ..llm.providers import Message
from ..models import BeliefsNow, Belief, CognitionWorkspace, Hypothesis
from .base import Role, RoleResult


class AnalysisOutput(BaseModel):
    """Output from the analyst."""
    about_self: str = ""
    about_others: str = ""
    about_situation: str = ""
    key_beliefs: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)


class ReasoningOutput(BaseModel):
    """Output for reasoning tasks."""
    problem_restatement: str = ""
    key_assumptions: list[str] = Field(default_factory=list)
    hypotheses: list[str] = Field(default_factory=list)
    recommended_action: str = ""
    rationale: str = ""
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    open_questions: list[str] = Field(default_factory=list)


class Analyst(Role):
    """
    Updates beliefs and cognition workspace.

    The Analyst maintains a coherent picture of current beliefs
    and performs structured reasoning when needed.

    Updates:
    - beliefs_now: Current situational beliefs
    - cognition_workspace: Active reasoning workspace
    """

    name = "analyst"
    description = "Maintains beliefs and performs structured reasoning."
    default_tier = LLMTier.LIGHT  # Balanced - runs periodically

    reads = ["context_now", "affect_core", "world_model", "self_model", "goals_active"]
    writes = ["beliefs_now", "cognition_workspace"]

    async def execute(
        self,
        problem: str | None = None,
        **kwargs,
    ) -> RoleResult:
        """
        Update beliefs and optionally reason about a problem.

        Args:
            problem: Optional problem to reason about

        Returns:
            RoleResult with updated beliefs and workspace
        """
        # Read current state
        context = self._read_node("context_now")
        affect = self._read_node("affect_core")
        goals = self._read_node("goals_active")

        try:
            # Always update beliefs
            beliefs_result = await self._update_beliefs(context, affect)

            # If there's a problem, do structured reasoning
            workspace_result = None
            if problem:
                workspace_result = await self._reason_about(problem, context, goals)

            updates = {"beliefs_now": beliefs_result.model_dump()}
            messages = [f"Updated beliefs: {beliefs_result.about_situation[:50]}..."]

            if workspace_result:
                updates["cognition_workspace"] = workspace_result.model_dump()
                messages.append(f"Reasoning complete: {workspace_result.decision[:50]}...")

            return RoleResult(
                success=True,
                updates=updates,
                messages=messages,
            )

        except Exception as e:
            return RoleResult(
                success=False,
                error=str(e),
            )

    async def _update_beliefs(self, context, affect) -> BeliefsNow:
        """Update current beliefs based on context."""
        context_desc = ""
        if context:
            context_desc = f"""
Context:
- Location: {context.location}
- Task: {context.current_task}
- People: {', '.join(context.people_present) if context.people_present else 'none'}
- Setting: {context.social_setting}
"""

        affect_desc = ""
        if affect:
            affect_desc = f"""
Current affect:
- Valence: {affect.valence:.2f}
- Arousal: {affect.arousal:.2f}
"""

        messages = [
            Message(
                role="user",
                content=f"""Based on the current context and state, what are the key beliefs?

{context_desc}
{affect_desc}

Provide:
1. Belief about self right now (current state, capacity, mood)
2. Belief about others present (if any)
3. Belief about the situation (what's happening, what matters)
4. Key beliefs as a list (2-5 items)
5. Overall confidence in these assessments (0-1)

Focus on actionable beliefs that inform decision-making."""
            )
        ]

        output = await self._complete(
            messages=messages,
            response_model=AnalysisOutput,
            system=self._get_system_prompt(),
        )

        beliefs = BeliefsNow(
            beliefs=[
                Belief(claim=b, confidence=output.confidence, source="inference")
                for b in output.key_beliefs
            ],
            about_self=output.about_self,
            about_others=output.about_others,
            about_situation=output.about_situation,
        )

        await self._write_node("beliefs_now", beliefs)
        return beliefs

    async def _reason_about(self, problem: str, context, goals) -> CognitionWorkspace:
        """Perform structured reasoning about a problem."""
        context_str = ""
        if context:
            context_str = f"Current context: {context.current_task or 'none'}"

        goals_str = ""
        if goals and goals.goals:
            goals_str = f"Active goals: {', '.join(g.description for g in goals.goals[:3])}"

        messages = [
            Message(
                role="user",
                content=f"""Reason through this problem systematically.

Problem: {problem}

{context_str}
{goals_str}

Provide:
1. Problem restatement (clear, specific)
2. Key assumptions you're making
3. Hypotheses to consider (2-4)
4. Recommended action
5. Rationale for recommendation
6. Confidence level (0-1)
7. Open questions that would change your analysis

Think step by step. Be explicit about uncertainty."""
            )
        ]

        output = await self._complete(
            messages=messages,
            response_model=ReasoningOutput,
            system=self._get_system_prompt(),
            tier=LLMTier.HEAVY,  # Use heavy tier for reasoning
        )

        workspace = CognitionWorkspace(
            problem_statement=output.problem_restatement or problem,
            assumptions=output.key_assumptions,
            hypotheses=[
                Hypothesis(claim=h, prior=0.5, status="active")
                for h in output.hypotheses
            ],
            decision=output.recommended_action,
            rationale=output.rationale,
            confidence=output.confidence,
            open_loops=output.open_questions,
        )

        await self._write_node("cognition_workspace", workspace)
        return workspace

    async def analyze(self, question: str) -> str:
        """
        Quick analysis without full state update.

        Useful for one-off questions.
        """
        context = self._read_node("context_now")
        beliefs = self._read_node("beliefs_now")

        context_str = ""
        if context:
            context_str = f"Current context: {context.current_task or 'unknown'}"
        if beliefs:
            context_str += f"\nCurrent beliefs: {beliefs.about_situation}"

        messages = [
            Message(
                role="user",
                content=f"""Answer this question based on current state:

{context_str}

Question: {question}

Be concise and direct."""
            )
        ]

        return await self._complete(messages=messages, system=self._get_system_prompt())
