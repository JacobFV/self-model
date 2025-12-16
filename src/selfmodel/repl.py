"""
Interactive REPL for the self-model system.

Provides a command-line interface for:
- Inspecting current state
- Sending inputs
- Triggering role executions
- Monitoring events
"""

import asyncio
import json
import sys
from dataclasses import dataclass
from datetime import datetime, UTC
from pathlib import Path
from typing import Callable

from .store import StateStore, open_store
from .events import EventBus, Event, EventType
from .bootstrap import bootstrap_profile
from .llm import LLMRouter, LLMTier, DEFAULT_TIERS, MOCK_TIERS
from .llm.providers import MockProvider
from .roles import Perceiver, Appraiser, Analyst, Critic, Planner
from .loops import Orchestrator


@dataclass
class REPLConfig:
    """Configuration for the REPL."""
    profile_key: str
    base_dir: str = "state"
    use_mock: bool = True
    verbose: bool = True
    auto_bootstrap: bool = True


class SelfModelREPL:
    """
    Interactive REPL for the self-model system.

    Commands:
        help            Show available commands
        status          Show current state summary
        affect          Show affect state
        beliefs         Show current beliefs
        goals           Show active goals
        context         Show current context
        constitution    Show constitution
        self            Show self-model
        world           Show world-model

        input <text>    Send input to the system
        perceive        Run perceiver
        appraise        Run appraiser
        analyze         Run analyst
        critique <act>  Check action against constitution
        plan            Run planner

        tick            Run one instant loop tick
        session         Run one session loop tick
        start           Start orchestrator
        stop            Stop orchestrator

        history <node>  Show history for a node
        export          Export state to JSON
        events          Show recent events
        stats           Show system statistics
        quit            Exit the REPL

    Example:
        repl = SelfModelREPL(config)
        await repl.run()
    """

    def __init__(self, config: REPLConfig):
        self.config = config
        self.store: StateStore | None = None
        self.router: LLMRouter | None = None
        self.bus: EventBus | None = None
        self.orchestrator: Orchestrator | None = None

        # Event history
        self.events: list[Event] = []
        self._running = False

        # Commands
        self.commands: dict[str, Callable] = {
            "help": self._cmd_help,
            "status": self._cmd_status,
            "affect": self._cmd_affect,
            "beliefs": self._cmd_beliefs,
            "goals": self._cmd_goals,
            "context": self._cmd_context,
            "constitution": self._cmd_constitution,
            "self": self._cmd_self_model,
            "world": self._cmd_world_model,
            "input": self._cmd_input,
            "perceive": self._cmd_perceive,
            "appraise": self._cmd_appraise,
            "analyze": self._cmd_analyze,
            "critique": self._cmd_critique,
            "plan": self._cmd_plan,
            "tick": self._cmd_tick,
            "session": self._cmd_session,
            "start": self._cmd_start,
            "stop": self._cmd_stop,
            "history": self._cmd_history,
            "export": self._cmd_export,
            "events": self._cmd_events,
            "stats": self._cmd_stats,
            "quit": self._cmd_quit,
            "exit": self._cmd_quit,
        }

    async def initialize(self) -> None:
        """Initialize the REPL components."""
        # Check if profile exists
        state_dir = Path(self.config.base_dir) / self.config.profile_key

        if state_dir.exists():
            self.store = open_store(self.config.profile_key, self.config.base_dir)
            self._print(f"Loaded existing profile: {self.config.profile_key}")
        elif self.config.auto_bootstrap:
            self.store = bootstrap_profile(
                self.config.profile_key,
                base_dir=self.config.base_dir
            )
            self._print(f"Bootstrapped new profile: {self.config.profile_key}")
        else:
            raise ValueError(f"Profile {self.config.profile_key} not found")

        # Set up LLM router
        if self.config.use_mock:
            mock = MockProvider()
            self.router = LLMRouter(tiers=MOCK_TIERS, providers={"mock": mock})
            self._print("Using mock LLM provider")
        else:
            self.router = LLMRouter(tiers=DEFAULT_TIERS)
            self._print("Using default LLM providers")

        # Set up event bus
        self.bus = EventBus()

        # Subscribe to events for logging
        async def log_event(event: Event):
            self.events.append(event)
            if self.config.verbose:
                self._print(f"  [event] {event.type.value}: {event.source}")

        self.bus.subscribe(EventType.NODE_UPDATED, log_event)
        self.bus.subscribe(EventType.ERROR, log_event)

        # Create orchestrator
        self.orchestrator = Orchestrator(
            profile=self.store.profile,
            store=self.store,
            router=self.router,
            bus=self.bus,
        )

    async def run(self) -> None:
        """Run the REPL loop."""
        await self.initialize()

        self._print("\nSelf-Model REPL")
        self._print(f"Profile: {self.config.profile_key}")
        self._print("Type 'help' for commands, 'quit' to exit.\n")

        self._running = True
        while self._running:
            try:
                # Read input
                line = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: input(">> ")
                )
                line = line.strip()

                if not line:
                    continue

                # Parse command
                parts = line.split(maxsplit=1)
                cmd = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""

                # Execute command
                if cmd in self.commands:
                    await self.commands[cmd](args)
                else:
                    self._print(f"Unknown command: {cmd}. Type 'help' for commands.")

            except EOFError:
                break
            except KeyboardInterrupt:
                self._print("\nInterrupted. Type 'quit' to exit.")
            except Exception as e:
                self._print(f"Error: {e}")

    def _print(self, msg: str) -> None:
        """Print a message."""
        print(msg)

    def _format_dict(self, d: dict, indent: int = 2) -> str:
        """Format a dict for display."""
        return json.dumps(d, indent=indent, default=str)

    # ===== State inspection commands =====

    async def _cmd_help(self, args: str) -> None:
        """Show help."""
        self._print("""
Commands:
  State Inspection:
    status          Show current state summary
    affect          Show affect state
    beliefs         Show current beliefs
    goals           Show active goals
    context         Show current context
    constitution    Show constitution
    self            Show self-model
    world           Show world-model

  Interaction:
    input <text>    Send input to the system
    perceive        Run perceiver on recent input
    appraise        Run appraiser
    analyze         Run analyst (optionally: analyze <problem>)
    critique <act>  Check action against constitution
    plan            Run planner

  Execution:
    tick            Run one instant loop tick
    session         Run one session loop tick
    start           Start orchestrator
    stop            Stop orchestrator

  Utilities:
    history <node>  Show history for a node
    export          Export current state to JSON
    events          Show recent events
    stats           Show system statistics
    help            Show this help
    quit/exit       Exit the REPL
""")

    async def _cmd_status(self, args: str) -> None:
        """Show status summary."""
        now = self.store.now

        self._print("\n=== Current State ===")

        # Affect
        if now.affect_core:
            self._print(f"\nAffect:")
            self._print(f"  Valence:  {now.affect_core.valence:+.2f}")
            self._print(f"  Arousal:  {now.affect_core.arousal:.2f}")
            self._print(f"  Tension:  {now.affect_core.tension:.2f}")

        # Context
        if now.context_now:
            self._print(f"\nContext:")
            if now.context_now.current_task:
                self._print(f"  Task: {now.context_now.current_task}")
            if now.context_now.location:
                self._print(f"  Location: {now.context_now.location}")

        # Goals
        if now.goals_active and now.goals_active.goals:
            self._print(f"\nGoals ({len(now.goals_active.goals)}):")
            if now.goals_active.primary_goal:
                self._print(f"  Primary: {now.goals_active.primary_goal}")
            for g in now.goals_active.goals[:3]:
                self._print(f"  - {g.description} (p={g.priority:.1f})")

        # Beliefs
        if now.beliefs_now:
            self._print(f"\nBeliefs:")
            if now.beliefs_now.about_self:
                self._print(f"  Self: {now.beliefs_now.about_self[:80]}")
            if now.beliefs_now.about_situation:
                self._print(f"  Situation: {now.beliefs_now.about_situation[:80]}")

        self._print("")

    async def _cmd_affect(self, args: str) -> None:
        """Show affect state."""
        affect = self.store.now.affect_core
        if not affect:
            self._print("No affect state.")
            return

        self._print("\n=== Affect Core ===")
        self._print(f"Valence:      {affect.valence:+.3f}  (negative to positive)")
        self._print(f"Arousal:      {affect.arousal:.3f}   (calm to activated)")
        self._print(f"Dominance:    {affect.dominance:.3f}   (controlled to in-control)")
        self._print(f"Tension:      {affect.tension:.3f}")
        self._print(f"Social Safety:{affect.social_safety:.3f}")
        self._print(f"Body Load:    {affect.body_load:.3f}")

        labels = self.store.now.affect_labels
        if labels and labels.primary_emotion:
            self._print(f"\nPrimary emotion: {labels.primary_emotion} ({labels.primary_intensity:.1f})")

        self._print("")

    async def _cmd_beliefs(self, args: str) -> None:
        """Show beliefs."""
        beliefs = self.store.now.beliefs_now
        if not beliefs:
            self._print("No beliefs.")
            return

        self._print("\n=== Current Beliefs ===")
        if beliefs.about_self:
            self._print(f"About self: {beliefs.about_self}")
        if beliefs.about_situation:
            self._print(f"About situation: {beliefs.about_situation}")
        if beliefs.about_others:
            self._print(f"About others: {beliefs.about_others}")
        if beliefs.about_future:
            self._print(f"About future: {beliefs.about_future}")
        if beliefs.uncertainty_sources:
            self._print(f"Uncertainties: {', '.join(beliefs.uncertainty_sources)}")
        self._print("")

    async def _cmd_goals(self, args: str) -> None:
        """Show goals."""
        goals = self.store.now.goals_active
        if not goals or not goals.goals:
            self._print("No active goals.")
            return

        self._print("\n=== Active Goals ===")
        if goals.primary_goal:
            self._print(f"Primary: {goals.primary_goal}\n")

        for i, g in enumerate(goals.goals, 1):
            status_icon = {"active": "*", "paused": "-", "blocked": "!", "completed": "+"}
            icon = status_icon.get(g.status, "?")
            self._print(f"{i}. [{icon}] {g.description}")
            self._print(f"      Priority: {g.priority:.2f} | Horizon: {g.horizon} | Progress: {g.progress*100:.0f}%")
            if g.done_when:
                self._print(f"      Done when: {g.done_when}")

        if goals.blocked_goals:
            self._print(f"\nBlocked: {', '.join(goals.blocked_goals)}")
        self._print("")

    async def _cmd_context(self, args: str) -> None:
        """Show context."""
        ctx = self.store.now.context_now
        if not ctx:
            self._print("No context.")
            return

        self._print("\n=== Current Context ===")
        self._print(self._format_dict(ctx.model_dump()))

    async def _cmd_constitution(self, args: str) -> None:
        """Show constitution."""
        const = self.store.now.self_constitution
        if not const:
            self._print("No constitution.")
            return

        self._print("\n=== Self Constitution ===")

        self._print("\nValues:")
        for v in const.values:
            self._print(f"  - {v.name} ({v.weight:.1f}): {v.description}")

        self._print("\nTerminal Goals:")
        for g in const.terminal_goals:
            self._print(f"  - {g}")

        self._print("\nNon-negotiables:")
        for nn in const.nonnegotiables:
            self._print(f"  - {nn}")

        if const.taboos:
            self._print("\nTaboos:")
            for t in const.taboos:
                self._print(f"  - {t}")

        if const.identity_claims:
            self._print("\nIdentity Claims:")
            for ic in const.identity_claims:
                self._print(f"  - {ic}")

        self._print("")

    async def _cmd_self_model(self, args: str) -> None:
        """Show self-model."""
        sm = self.store.now.self_model
        if not sm:
            self._print("No self-model.")
            return

        self._print("\n=== Self Model ===")

        if sm.traits:
            self._print("\nTraits:")
            for t in sm.traits:
                self._print(f"  - {t.name}: {t.description} ({t.confidence:.1f})")

        if sm.capabilities:
            self._print(f"\nCapabilities: {', '.join(sm.capabilities)}")

        if sm.limits:
            self._print(f"\nLimits: {', '.join(sm.limits)}")

        if sm.cognitive_styles:
            self._print(f"\nCognitive styles: {', '.join(sm.cognitive_styles)}")

        if sm.energy_sources:
            self._print(f"\nEnergy sources: {', '.join(sm.energy_sources)}")

        if sm.energy_drains:
            self._print(f"\nEnergy drains: {', '.join(sm.energy_drains)}")

        self._print("")

    async def _cmd_world_model(self, args: str) -> None:
        """Show world-model."""
        wm = self.store.now.world_model
        if not wm:
            self._print("No world-model.")
            return

        self._print("\n=== World Model ===")

        if wm.priors:
            self._print("\nPriors:")
            for p in wm.priors:
                self._print(f"  - {p.claim} ({p.confidence:.1f})")

        if wm.unknowns:
            self._print(f"\nUnknowns: {', '.join(wm.unknowns)}")

        self._print("")

    # ===== Interaction commands =====

    async def _cmd_input(self, args: str) -> None:
        """Send input to the system."""
        if not args:
            self._print("Usage: input <text>")
            return

        # Store as raw input in context
        ctx = self.store.now.context_now
        if ctx:
            ctx.raw_input = args
            self.store.context_now.append(ctx)

        # Send to orchestrator
        await self.orchestrator.input(args)
        self._print(f"Input sent: {args[:50]}...")

    async def _cmd_perceive(self, args: str) -> None:
        """Run perceiver."""
        perceiver = Perceiver(self.router, self.store, self.bus)

        # Get raw input from context
        ctx = self.store.now.context_now
        input_data = args or (ctx.raw_input if ctx else None) or "No input"

        self._print(f"Running perceiver with: {input_data[:50]}...")
        result = await perceiver.execute(input_data=input_data)

        if result.success:
            self._print("Perceiver completed.")
            for msg in result.messages:
                self._print(f"  {msg}")
        else:
            self._print(f"Perceiver failed: {result.error}")

    async def _cmd_appraise(self, args: str) -> None:
        """Run appraiser."""
        appraiser = Appraiser(self.router, self.store, self.bus)

        self._print("Running appraiser...")
        result = await appraiser.execute()

        if result.success:
            self._print("Appraiser completed.")
            for msg in result.messages:
                self._print(f"  {msg}")
        else:
            self._print(f"Appraiser failed: {result.error}")

    async def _cmd_analyze(self, args: str) -> None:
        """Run analyst."""
        analyst = Analyst(self.router, self.store, self.bus)

        kwargs = {}
        if args:
            kwargs["problem"] = args
            self._print(f"Running analyst on problem: {args}")
        else:
            self._print("Running analyst...")

        result = await analyst.execute(**kwargs)

        if result.success:
            self._print("Analyst completed.")
            for msg in result.messages:
                self._print(f"  {msg}")
        else:
            self._print(f"Analyst failed: {result.error}")

    async def _cmd_critique(self, args: str) -> None:
        """Run critic on an action."""
        if not args:
            self._print("Usage: critique <action to check>")
            return

        critic = Critic(self.router, self.store, self.bus)

        self._print(f"Checking action: {args}")
        result = await critic.execute(action=args)

        if result.success:
            self._print("Critic completed.")
            if "constitution_check" in result.updates:
                check = result.updates["constitution_check"]
                self._print(f"  Aligned: {check.get('aligned', 'unknown')}")
                if check.get("concerns"):
                    self._print(f"  Concerns: {', '.join(check['concerns'])}")
        else:
            self._print(f"Critic failed: {result.error}")

    async def _cmd_plan(self, args: str) -> None:
        """Run planner."""
        planner = Planner(self.router, self.store, self.bus)

        action = args or "prioritize"
        self._print(f"Running planner (action: {action})...")
        result = await planner.execute(action=action)

        if result.success:
            self._print("Planner completed.")
            for msg in result.messages:
                self._print(f"  {msg}")
        else:
            self._print(f"Planner failed: {result.error}")

    # ===== Execution commands =====

    async def _cmd_tick(self, args: str) -> None:
        """Run one instant loop tick."""
        self._print("Running instant loop tick...")
        await self.orchestrator._instant._tick()
        self._print(f"Tick completed. Total ticks: {self.orchestrator._instant.stats.ticks}")

    async def _cmd_session(self, args: str) -> None:
        """Run one session loop tick."""
        self._print("Running session loop tick...")
        await self.orchestrator._session._tick()
        self._print(f"Session tick completed. Total: {self.orchestrator._session.stats.ticks}")

    async def _cmd_start(self, args: str) -> None:
        """Start orchestrator."""
        if self.orchestrator.running:
            self._print("Orchestrator already running.")
            return

        await self.orchestrator.start()
        self._print("Orchestrator started.")

    async def _cmd_stop(self, args: str) -> None:
        """Stop orchestrator."""
        if not self.orchestrator.running:
            self._print("Orchestrator not running.")
            return

        await self.orchestrator.stop()
        self._print("Orchestrator stopped.")

    # ===== Utility commands =====

    async def _cmd_history(self, args: str) -> None:
        """Show history for a node."""
        if not args:
            self._print("Usage: history <node_name>")
            self._print("Nodes: affect_core, beliefs_now, goals_active, context_now, ...")
            return

        node_name = args.strip()
        try:
            index = getattr(self.store, node_name)
            entries = list(index.all())

            self._print(f"\n=== History: {node_name} ({len(entries)} entries) ===")
            for entry in entries[-10:]:  # Last 10
                ts = datetime.fromtimestamp(entry.t, UTC).isoformat()
                summary = str(entry.v)[:80].replace("\n", " ")
                self._print(f"  [{ts}] {summary}")
            self._print("")
        except AttributeError:
            self._print(f"Unknown node: {node_name}")

    async def _cmd_export(self, args: str) -> None:
        """Export current state."""
        now = self.store.now

        export = {}
        for node_name in ["self_constitution", "self_model", "world_model",
                          "affect_core", "context_now", "beliefs_now", "goals_active"]:
            node_value = getattr(now, node_name, None)
            if node_value:
                export[node_name] = node_value.model_dump()

        output = json.dumps(export, indent=2, default=str)

        if args:
            # Save to file
            Path(args).write_text(output)
            self._print(f"Exported to: {args}")
        else:
            self._print(output)

    async def _cmd_events(self, args: str) -> None:
        """Show recent events."""
        if not self.events:
            self._print("No events recorded.")
            return

        n = int(args) if args else 10
        self._print(f"\n=== Recent Events (last {n}) ===")
        for event in self.events[-n:]:
            ts = datetime.fromtimestamp(event.timestamp, UTC).strftime("%H:%M:%S")
            self._print(f"  [{ts}] {event.type.value}: {event.source}")
            if event.data:
                for k, v in list(event.data.items())[:2]:
                    self._print(f"         {k}: {str(v)[:50]}")
        self._print("")

    async def _cmd_stats(self, args: str) -> None:
        """Show system statistics."""
        stats = self.orchestrator.get_stats()

        self._print("\n=== System Statistics ===")
        self._print(f"Profile: {stats['profile']}")
        self._print(f"Running: {self.orchestrator.running}")

        self._print(f"\nInstant Loop:")
        self._print(f"  Ticks: {stats['instant']['ticks']}")
        self._print(f"  Inputs: {stats['instant']['inputs_processed']}")
        self._print(f"  Errors: {stats['instant']['errors']}")

        self._print(f"\nSession Loop:")
        self._print(f"  Ticks: {stats['session']['ticks']}")
        self._print(f"  Belief updates: {stats['session']['belief_updates']}")

        self._print(f"\nLLM Usage:")
        for tier, usage in stats['llm_usage'].items():
            self._print(f"  {tier}: {usage['calls']} calls, {usage['tokens']} tokens")

        self._print(f"\nEvents recorded: {len(self.events)}")
        self._print("")

    async def _cmd_quit(self, args: str) -> None:
        """Exit the REPL."""
        if self.orchestrator and self.orchestrator.running:
            await self.orchestrator.stop()
        self._running = False
        self._print("Goodbye.")


async def run_repl(
    profile: str,
    base_dir: str = "state",
    use_mock: bool = True,
    verbose: bool = True,
) -> None:
    """
    Run the REPL.

    Args:
        profile: Profile key (e.g., "jacob-heavy-v1")
        base_dir: Base directory for state
        use_mock: Use mock LLM provider
        verbose: Show verbose output
    """
    config = REPLConfig(
        profile_key=profile,
        base_dir=base_dir,
        use_mock=use_mock,
        verbose=verbose,
    )
    repl = SelfModelREPL(config)
    await repl.run()
