"""
Planner role: Manages goals and plans.

The Planner is responsible for:
- Setting and prioritizing goals
- Generating action options
- Creating and updating plans
- Tracking progress

Runs in the session loop or on demand.
"""

from pydantic import BaseModel, Field
from typing import Literal

from ..llm import LLMTier
from ..llm.providers import Message
from ..models import (
    GoalsActive, Goal,
    OptionsSet, Option,
    PlanActive, PlanStep,
)
from .base import Role, RoleResult


class GoalPrioritization(BaseModel):
    """Output from goal prioritization."""
    goals: list[str] = Field(default_factory=list)
    priorities: list[float] = Field(default_factory=list)
    primary_goal: str = ""
    rationale: str = ""


class OptionGeneration(BaseModel):
    """Output from option generation."""
    options: list[str] = Field(default_factory=list)
    pros: list[list[str]] = Field(default_factory=list)
    cons: list[list[str]] = Field(default_factory=list)
    recommended: int = 0  # Index of recommended option
    recommendation_rationale: str = ""


class PlanGeneration(BaseModel):
    """Output from plan generation."""
    steps: list[str] = Field(default_factory=list)
    step_purposes: list[str] = Field(default_factory=list)
    estimated_confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    main_risks: list[str] = Field(default_factory=list)
    fallback_plan: str = ""


class Planner(Role):
    """
    Manages goals, options, and plans.

    The Planner handles the action-selection system:
    - What do I want to achieve? (goals)
    - What can I do? (options)
    - What's my plan? (plan)
    """

    name = "planner"
    description = "Manages goals, generates options, and creates plans."
    default_tier = LLMTier.LIGHT

    reads = ["context_now", "beliefs_now", "self_constitution", "goals_active"]
    writes = ["goals_active", "options_set", "plan_active"]

    async def execute(
        self,
        action: Literal["prioritize", "generate_options", "plan"] = "prioritize",
        goal: str | None = None,
        **kwargs,
    ) -> RoleResult:
        """
        Execute planning action.

        Args:
            action: What to do ("prioritize", "generate_options", "plan")
            goal: Goal to plan for (required for "plan" action)

        Returns:
            RoleResult with planning outputs
        """
        try:
            if action == "prioritize":
                return await self._prioritize_goals()
            elif action == "generate_options":
                return await self._generate_options()
            elif action == "plan":
                if not goal:
                    return RoleResult(
                        success=False,
                        error="Goal required for planning",
                    )
                return await self._create_plan(goal)
            else:
                return RoleResult(
                    success=False,
                    error=f"Unknown action: {action}",
                )
        except Exception as e:
            return RoleResult(
                success=False,
                error=str(e),
            )

    async def _prioritize_goals(self) -> RoleResult:
        """Prioritize current goals."""
        context = self._read_node("context_now")
        constitution = self._read_node("self_constitution")
        current_goals = self._read_node("goals_active")

        # Gather existing goals
        existing = []
        if current_goals and current_goals.goals:
            existing = [g.description for g in current_goals.goals]

        context_str = ""
        if context:
            context_str = f"Current context: {context.current_task or 'none'}"

        values_str = ""
        if constitution and constitution.values:
            values_str = "Values: " + ", ".join(v.name for v in constitution.values[:5])

        messages = [
            Message(
                role="user",
                content=f"""Review and prioritize goals.

{context_str}
{values_str}

Current goals:
{chr(10).join(f'- {g}' for g in existing) if existing else '(none defined)'}

Consider:
1. Alignment with values
2. Current context and constraints
3. Dependencies between goals
4. Time horizons

Output:
- goals: list of goals (keep existing or modify)
- priorities: priority score for each (0-1)
- primary_goal: the single most important goal right now
- rationale: why this prioritization"""
            )
        ]

        output = await self._complete(
            messages=messages,
            response_model=GoalPrioritization,
            system=self._get_system_prompt(),
        )

        # Create GoalsActive
        goals = GoalsActive(
            goals=[
                Goal(
                    description=g,
                    priority=output.priorities[i] if i < len(output.priorities) else 0.5,
                )
                for i, g in enumerate(output.goals)
            ],
            primary_goal=output.primary_goal,
        )

        await self._write_node("goals_active", goals)

        return RoleResult(
            success=True,
            updates={"goals_active": goals.model_dump()},
            messages=[
                f"Primary goal: {output.primary_goal}",
                f"Total goals: {len(output.goals)}",
            ],
        )

    async def _generate_options(self) -> RoleResult:
        """Generate action options for current situation."""
        context = self._read_node("context_now")
        goals = self._read_node("goals_active")
        beliefs = self._read_node("beliefs_now")

        context_str = ""
        if context:
            context_str = f"Context: {context.current_task or 'none'}"

        goal_str = ""
        if goals and goals.primary_goal:
            goal_str = f"Primary goal: {goals.primary_goal}"

        beliefs_str = ""
        if beliefs:
            beliefs_str = f"Situation: {beliefs.about_situation}"

        messages = [
            Message(
                role="user",
                content=f"""Generate action options for the current situation.

{context_str}
{goal_str}
{beliefs_str}

Generate 3-5 distinct options. For each option:
- State the action clearly
- List pros (2-3)
- List cons (1-3)

Then recommend one option and explain why.

Consider:
- Feasibility given constraints
- Alignment with goals
- Reversibility
- Information value"""
            )
        ]

        output = await self._complete(
            messages=messages,
            response_model=OptionGeneration,
            system=self._get_system_prompt(),
        )

        # Create OptionsSet
        options = OptionsSet(
            context_summary=context_str,
            options=[
                Option(
                    description=opt,
                    pros=output.pros[i] if i < len(output.pros) else [],
                    cons=output.cons[i] if i < len(output.cons) else [],
                )
                for i, opt in enumerate(output.options)
            ],
            recommended=output.options[output.recommended] if output.options else "",
            recommendation_rationale=output.recommendation_rationale,
        )

        await self._write_node("options_set", options)

        return RoleResult(
            success=True,
            updates={"options_set": options.model_dump()},
            messages=[
                f"Generated {len(output.options)} options",
                f"Recommended: {options.recommended[:50]}...",
            ],
        )

    async def _create_plan(self, goal: str) -> RoleResult:
        """Create a plan for achieving a goal."""
        context = self._read_node("context_now")
        beliefs = self._read_node("beliefs_now")

        context_str = ""
        if context:
            context_str = f"Context: {context.current_task or 'none'}"
            if context.active_constraints:
                context_str += f"\nConstraints: {', '.join(context.active_constraints)}"

        beliefs_str = ""
        if beliefs:
            beliefs_str = f"Current understanding: {beliefs.about_situation}"

        messages = [
            Message(
                role="user",
                content=f"""Create a concrete plan to achieve this goal.

Goal: {goal}

{context_str}
{beliefs_str}

Create a step-by-step plan:
- Each step should be a concrete action
- Include the purpose of each step
- Keep it to 3-7 steps
- Identify main risks
- Include a fallback plan

Consider:
- Current constraints and resources
- Dependencies between steps
- What could go wrong
- How to verify progress"""
            )
        ]

        output = await self._complete(
            messages=messages,
            response_model=PlanGeneration,
            system=self._get_system_prompt(),
            tier=LLMTier.HEAVY,  # Use heavy for planning
        )

        # Create PlanActive
        plan = PlanActive(
            goal=goal,
            context=context_str,
            steps=[
                PlanStep(
                    action=step,
                    purpose=output.step_purposes[i] if i < len(output.step_purposes) else "",
                )
                for i, step in enumerate(output.steps)
            ],
            confidence=output.estimated_confidence,
            main_risks=output.main_risks,
            fallback_plan=output.fallback_plan,
        )

        await self._write_node("plan_active", plan)

        return RoleResult(
            success=True,
            updates={"plan_active": plan.model_dump()},
            messages=[
                f"Created plan with {len(output.steps)} steps",
                f"Confidence: {output.estimated_confidence:.0%}",
                f"Main risks: {', '.join(output.main_risks[:2])}",
            ],
        )

    async def set_goal(self, goal: str, priority: float = 0.8) -> RoleResult:
        """
        Quick method to add a new goal.
        """
        current = self._read_node("goals_active")

        goals_list = []
        if current and current.goals:
            goals_list = list(current.goals)

        goals_list.append(Goal(description=goal, priority=priority))

        # Re-sort by priority
        goals_list.sort(key=lambda g: g.priority, reverse=True)

        goals = GoalsActive(
            goals=goals_list,
            primary_goal=goals_list[0].description if goals_list else goal,
        )

        await self._write_node("goals_active", goals)

        return RoleResult(
            success=True,
            updates={"goals_active": goals.model_dump()},
            messages=[f"Added goal: {goal}"],
        )
