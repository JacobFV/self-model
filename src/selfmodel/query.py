"""
Query interface for interrogating self-model state.

Provides structured queries for common questions about:
- Values and constitution
- Current affect and emotions
- Active goals and plans
- Beliefs and cognition
- Historical patterns
"""

from dataclasses import dataclass
from datetime import datetime, UTC
from typing import Literal

from .store import StateStore


@dataclass
class QueryResult:
    """Result of a query."""
    found: bool
    value: any = None
    message: str = ""
    details: dict | None = None


class StateQuery:
    """
    Query interface for self-model state.

    Provides structured queries for common questions about state.

    Example:
        query = StateQuery(store)

        # What are my top values?
        values = query.top_values(n=3)

        # What's my current affect?
        affect = query.current_affect()

        # What goals are blocked?
        blocked = query.blocked_goals()
    """

    def __init__(self, store: StateStore):
        self.store = store

    # ===== Constitution queries =====

    def top_values(self, n: int = 3) -> QueryResult:
        """Get the top N values by weight."""
        const = self.store.now.self_constitution
        if not const or not const.values:
            return QueryResult(found=False, message="No constitution defined")

        sorted_values = sorted(const.values, key=lambda v: -v.weight)[:n]
        return QueryResult(
            found=True,
            value=[v.name for v in sorted_values],
            details={"values": [{"name": v.name, "weight": v.weight, "description": v.description} for v in sorted_values]},
        )

    def terminal_goals(self) -> QueryResult:
        """Get terminal goals from constitution."""
        const = self.store.now.self_constitution
        if not const:
            return QueryResult(found=False, message="No constitution defined")

        return QueryResult(
            found=True,
            value=const.terminal_goals,
        )

    def nonnegotiables(self) -> QueryResult:
        """Get non-negotiables from constitution."""
        const = self.store.now.self_constitution
        if not const:
            return QueryResult(found=False, message="No constitution defined")

        return QueryResult(
            found=True,
            value=const.nonnegotiables,
        )

    def has_value(self, value_name: str) -> QueryResult:
        """Check if a specific value exists in the constitution."""
        const = self.store.now.self_constitution
        if not const:
            return QueryResult(found=False, message="No constitution defined")

        for v in const.values:
            if v.name.lower() == value_name.lower():
                return QueryResult(
                    found=True,
                    value=v.weight,
                    message=f"Value '{v.name}' exists with weight {v.weight}",
                    details={"name": v.name, "weight": v.weight, "description": v.description},
                )

        return QueryResult(
            found=False,
            message=f"Value '{value_name}' not found",
        )

    def decision_principles(self) -> QueryResult:
        """Get decision principles from constitution."""
        const = self.store.now.self_constitution
        if not const:
            return QueryResult(found=False, message="No constitution defined")

        return QueryResult(
            found=True,
            value=const.decision_principles,
        )

    # ===== Affect queries =====

    def current_affect(self) -> QueryResult:
        """Get current affect state."""
        affect = self.store.now.affect_core
        if not affect:
            return QueryResult(found=False, message="No affect state")

        return QueryResult(
            found=True,
            value={
                "valence": affect.valence,
                "arousal": affect.arousal,
                "tension": affect.tension,
            },
            details={
                "valence": affect.valence,
                "arousal": affect.arousal,
                "dominance": affect.dominance,
                "tension": affect.tension,
                "social_safety": affect.social_safety,
                "body_load": affect.body_load,
            },
        )

    def is_positive(self) -> QueryResult:
        """Check if current affect is positive."""
        affect = self.store.now.affect_core
        if not affect:
            return QueryResult(found=False, message="No affect state")

        is_positive = affect.valence > 0
        return QueryResult(
            found=True,
            value=is_positive,
            message=f"Affect is {'positive' if is_positive else 'negative'} (valence={affect.valence:.2f})",
        )

    def is_stressed(self, threshold: float = 0.6) -> QueryResult:
        """Check if currently stressed (high tension or arousal)."""
        affect = self.store.now.affect_core
        if not affect:
            return QueryResult(found=False, message="No affect state")

        stressed = affect.tension > threshold or affect.arousal > threshold
        return QueryResult(
            found=True,
            value=stressed,
            message=f"{'Stressed' if stressed else 'Not stressed'} (tension={affect.tension:.2f}, arousal={affect.arousal:.2f})",
        )

    def current_emotion(self) -> QueryResult:
        """Get current primary emotion."""
        labels = self.store.now.affect_labels
        if not labels or not labels.primary_emotion:
            return QueryResult(found=False, message="No emotion labels")

        return QueryResult(
            found=True,
            value=labels.primary_emotion,
            details={
                "emotion": labels.primary_emotion,
                "intensity": labels.primary_intensity,
            },
        )

    def affect_trend(self, n: int = 10) -> QueryResult:
        """Get affect trend over last N entries."""
        entries = list(self.store.affect_core.all())[-n:]
        if not entries:
            return QueryResult(found=False, message="No affect history")

        valences = [e.v.valence for e in entries]
        avg = sum(valences) / len(valences)
        trend = "improving" if len(valences) > 1 and valences[-1] > valences[0] else "declining" if len(valences) > 1 and valences[-1] < valences[0] else "stable"

        return QueryResult(
            found=True,
            value=trend,
            message=f"Affect is {trend} (avg valence={avg:.2f})",
            details={
                "average_valence": avg,
                "trend": trend,
                "min": min(valences),
                "max": max(valences),
                "samples": len(valences),
            },
        )

    # ===== Goal queries =====

    def active_goals(self) -> QueryResult:
        """Get all active goals."""
        goals = self.store.now.goals_active
        if not goals or not goals.goals:
            return QueryResult(found=False, message="No active goals")

        active = [g for g in goals.goals if g.status == "active"]
        return QueryResult(
            found=True,
            value=[g.description for g in active],
            details={"goals": [g.model_dump() for g in active]},
        )

    def primary_goal(self) -> QueryResult:
        """Get the primary goal."""
        goals = self.store.now.goals_active
        if not goals or not goals.primary_goal:
            return QueryResult(found=False, message="No primary goal set")

        return QueryResult(
            found=True,
            value=goals.primary_goal,
        )

    def blocked_goals(self) -> QueryResult:
        """Get all blocked goals."""
        goals = self.store.now.goals_active
        if not goals or not goals.goals:
            return QueryResult(found=False, message="No goals")

        blocked = [g for g in goals.goals if g.status == "blocked"]
        return QueryResult(
            found=True,
            value=[g.description for g in blocked],
            details={"blocked_goals": [g.model_dump() for g in blocked]},
        )

    def goal_conflicts(self) -> QueryResult:
        """Get active goal conflicts."""
        goals = self.store.now.goals_active
        if not goals:
            return QueryResult(found=False, message="No goals")

        return QueryResult(
            found=True,
            value=goals.active_conflicts,
        )

    def goals_by_horizon(self, horizon: Literal["immediate", "session", "daily", "weekly", "long_term"]) -> QueryResult:
        """Get goals by time horizon."""
        goals = self.store.now.goals_active
        if not goals or not goals.goals:
            return QueryResult(found=False, message="No goals")

        filtered = [g for g in goals.goals if g.horizon == horizon]
        return QueryResult(
            found=True,
            value=[g.description for g in filtered],
            details={"goals": [g.model_dump() for g in filtered]},
        )

    # ===== Cognition queries =====

    def current_context(self) -> QueryResult:
        """Get current context."""
        ctx = self.store.now.context_now
        if not ctx:
            return QueryResult(found=False, message="No context")

        return QueryResult(
            found=True,
            value={
                "task": ctx.current_task,
                "location": ctx.location,
                "setting": ctx.social_setting,
            },
            details=ctx.model_dump(),
        )

    def current_beliefs(self) -> QueryResult:
        """Get current beliefs."""
        beliefs = self.store.now.beliefs_now
        if not beliefs:
            return QueryResult(found=False, message="No beliefs")

        return QueryResult(
            found=True,
            value={
                "about_self": beliefs.about_self,
                "about_situation": beliefs.about_situation,
                "about_others": beliefs.about_others,
            },
            details=beliefs.model_dump(),
        )

    # ===== Self-model queries =====

    def traits(self) -> QueryResult:
        """Get self-model traits."""
        sm = self.store.now.self_model
        if not sm or not sm.traits:
            return QueryResult(found=False, message="No self-model traits")

        return QueryResult(
            found=True,
            value=[t.name for t in sm.traits],
            details={"traits": [t.model_dump() for t in sm.traits]},
        )

    def capabilities(self) -> QueryResult:
        """Get self-model capabilities."""
        sm = self.store.now.self_model
        if not sm:
            return QueryResult(found=False, message="No self-model")

        return QueryResult(
            found=True,
            value=sm.capabilities,
        )

    def limits(self) -> QueryResult:
        """Get self-model limits."""
        sm = self.store.now.self_model
        if not sm:
            return QueryResult(found=False, message="No self-model")

        return QueryResult(
            found=True,
            value=sm.limits,
        )

    def energy_state(self) -> QueryResult:
        """Get energy sources and drains."""
        sm = self.store.now.self_model
        if not sm:
            return QueryResult(found=False, message="No self-model")

        return QueryResult(
            found=True,
            value={
                "sources": sm.energy_sources,
                "drains": sm.energy_drains,
            },
        )

    # ===== World-model queries =====

    def priors(self) -> QueryResult:
        """Get world-model priors."""
        wm = self.store.now.world_model
        if not wm or not wm.priors:
            return QueryResult(found=False, message="No world-model priors")

        return QueryResult(
            found=True,
            value=[p.claim for p in wm.priors],
            details={"priors": [p.model_dump() for p in wm.priors]},
        )

    def unknowns(self) -> QueryResult:
        """Get world-model unknowns."""
        wm = self.store.now.world_model
        if not wm:
            return QueryResult(found=False, message="No world-model")

        return QueryResult(
            found=True,
            value=wm.unknowns,
        )

    # ===== History queries =====

    def history_count(self, node_name: str) -> QueryResult:
        """Get count of history entries for a node."""
        try:
            accessor = getattr(self.store, node_name)
            count = len(list(accessor.all()))
            return QueryResult(
                found=True,
                value=count,
            )
        except AttributeError:
            return QueryResult(found=False, message=f"Unknown node: {node_name}")

    def recent_entries(self, node_name: str, n: int = 5) -> QueryResult:
        """Get recent entries for a node."""
        try:
            accessor = getattr(self.store, node_name)
            entries = list(accessor.all())[-n:]
            return QueryResult(
                found=True,
                value=len(entries),
                details={
                    "entries": [
                        {"t": datetime.fromtimestamp(e.t, UTC).isoformat(), "v": e.v.model_dump()}
                        for e in entries
                    ]
                },
            )
        except AttributeError:
            return QueryResult(found=False, message=f"Unknown node: {node_name}")

    # ===== Composite queries =====

    def summary(self) -> QueryResult:
        """Get a comprehensive state summary."""
        affect = self.current_affect()
        goal = self.primary_goal()
        context = self.current_context()

        return QueryResult(
            found=True,
            value={
                "affect": affect.value if affect.found else None,
                "primary_goal": goal.value if goal.found else None,
                "context": context.value if context.found else None,
            },
            message=f"Primary goal: {goal.value if goal.found else 'None'}; "
                    f"Affect: {affect.value if affect.found else 'Unknown'}",
        )

    def alignment_check(self, action: str) -> QueryResult:
        """
        Check if an action might conflict with values/nonnegotiables.

        This is a simple keyword-based check, not LLM-based.
        """
        const = self.store.now.self_constitution
        if not const:
            return QueryResult(found=False, message="No constitution to check against")

        warnings = []
        action_lower = action.lower()

        # Check against nonnegotiables
        for nn in const.nonnegotiables:
            if any(word in action_lower for word in ["deceive", "lie", "harm", "hurt", "betray"]):
                warnings.append(f"May conflict with: {nn}")

        # Check against taboos
        for taboo in const.taboos:
            taboo_words = taboo.lower().split()
            if any(word in action_lower for word in taboo_words[:3]):
                warnings.append(f"May violate taboo: {taboo}")

        if warnings:
            return QueryResult(
                found=True,
                value=False,
                message="Potential alignment concerns found",
                details={"warnings": warnings},
            )

        return QueryResult(
            found=True,
            value=True,
            message="No obvious alignment concerns",
        )


def query(store: StateStore) -> StateQuery:
    """Create a query interface for a store."""
    return StateQuery(store)
