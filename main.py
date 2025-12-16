"""
Self-Model CLI: Main entry point.

Commands:
    selfmodel bootstrap <profile>  - Initialize a new profile
    selfmodel repl <profile>       - Interactive REPL
    selfmodel status <profile>     - Show profile status
    selfmodel run <profile>        - Run the orchestrator
    selfmodel export <profile>     - Export state to JSON
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path


def cmd_bootstrap(args):
    """Bootstrap a new profile."""
    from selfmodel import bootstrap_profile, Profile
    from selfmodel.models import SelfConstitution, Value

    profile = Profile.parse(args.profile)
    print(f"Bootstrapping profile: {profile.key}")

    # Custom constitution if provided
    constitution = None
    if args.constitution:
        const_path = Path(args.constitution)
        if const_path.exists():
            data = json.loads(const_path.read_text())
            constitution = SelfConstitution(**data)
            print(f"Using custom constitution from: {args.constitution}")

    store = bootstrap_profile(
        profile,
        base_dir=args.base_dir,
        constitution=constitution,
    )

    print(f"Profile initialized at: {store.state_dir}")
    print(f"  Values: {len(store.now.self_constitution.values)}")
    print(f"  Goals: {len(store.now.goals_active.goals) if store.now.goals_active else 0}")


def cmd_repl(args):
    """Run interactive REPL."""
    from selfmodel.repl import run_repl

    print(f"Starting REPL for profile: {args.profile}")
    asyncio.run(run_repl(
        profile=args.profile,
        base_dir=args.base_dir,
        use_mock=args.mock,
        verbose=not args.quiet,
    ))


def cmd_status(args):
    """Show profile status."""
    from selfmodel import open_store

    store = open_store(args.profile, args.base_dir)
    now = store.now

    print(f"\nProfile: {args.profile}")
    print(f"State dir: {store.state_dir}")
    print()

    # Constitution
    if now.self_constitution:
        print("Constitution:")
        print(f"  Values: {len(now.self_constitution.values)}")
        print(f"  Terminal goals: {len(now.self_constitution.terminal_goals)}")
        print(f"  Non-negotiables: {len(now.self_constitution.nonnegotiables)}")

    # Self-model
    if now.self_model:
        print("Self-model:")
        print(f"  Traits: {len(now.self_model.traits)}")
        print(f"  Capabilities: {len(now.self_model.capabilities)}")

    # Affect
    if now.affect_core:
        print("Affect:")
        print(f"  Valence: {now.affect_core.valence:+.2f}")
        print(f"  Arousal: {now.affect_core.arousal:.2f}")
        print(f"  Tension: {now.affect_core.tension:.2f}")

    # Context
    if now.context_now:
        print("Context:")
        if now.context_now.current_task:
            print(f"  Task: {now.context_now.current_task}")
        if now.context_now.location:
            print(f"  Location: {now.context_now.location}")

    # Goals
    if now.goals_active and now.goals_active.goals:
        print(f"Goals ({len(now.goals_active.goals)}):")
        if now.goals_active.primary_goal:
            print(f"  Primary: {now.goals_active.primary_goal}")
        for g in now.goals_active.goals[:3]:
            print(f"  - {g.description} (p={g.priority:.1f})")

    # History counts
    print("\nHistory:")
    nodes = ["affect_core", "beliefs_now", "context_now", "goals_active"]
    for node_name in nodes:
        index = getattr(store, node_name)
        entries = list(index.all())
        print(f"  {node_name}: {len(entries)} entries")


def cmd_run(args):
    """Run the orchestrator."""
    from selfmodel import open_store, EventBus
    from selfmodel.llm import LLMRouter, DEFAULT_TIERS, MOCK_TIERS
    from selfmodel.llm.providers import MockProvider
    from selfmodel.loops import Orchestrator

    store = open_store(args.profile, args.base_dir)
    bus = EventBus()

    # Set up router
    if args.mock:
        mock = MockProvider()
        router = LLMRouter(tiers=MOCK_TIERS, providers={"mock": mock})
        print("Using mock LLM provider")
    else:
        router = LLMRouter(tiers=DEFAULT_TIERS)
        print("Using default LLM providers")

    orch = Orchestrator(
        profile=store.profile,
        store=store,
        router=router,
        bus=bus,
    )

    async def run():
        print(f"Starting orchestrator for: {args.profile}")
        print("Press Ctrl+C to stop.\n")

        await orch.start()

        try:
            while True:
                await asyncio.sleep(1)
                stats = orch.get_stats()
                print(f"\r  Instant ticks: {stats['instant']['ticks']:4d} | "
                      f"Session ticks: {stats['session']['ticks']:4d} | "
                      f"Inputs: {stats['instant']['inputs_processed']:4d}",
                      end="", flush=True)
        except KeyboardInterrupt:
            print("\n\nStopping orchestrator...")
            await orch.stop()
            print("Done.")

    asyncio.run(run())


def cmd_export(args):
    """Export profile state to JSON."""
    from selfmodel import open_store

    store = open_store(args.profile, args.base_dir)
    now = store.now

    export = {"profile": args.profile}

    nodes = [
        "self_constitution", "self_model", "world_model",
        "affect_core", "affect_labels", "affect_appraisal",
        "context_now", "beliefs_now", "cognition_workspace",
        "goals_active", "options_set", "plan_active",
        "social_context", "attachment_state",
    ]

    for node_name in nodes:
        node_value = getattr(now, node_name, None)
        if node_value:
            export[node_name] = node_value.model_dump()

    output = json.dumps(export, indent=2, default=str)

    if args.output:
        Path(args.output).write_text(output)
        print(f"Exported to: {args.output}")
    else:
        print(output)


def cmd_input(args):
    """Send input to a profile."""
    from selfmodel import open_store, EventBus
    from selfmodel.llm import LLMRouter, MOCK_TIERS
    from selfmodel.llm.providers import MockProvider
    from selfmodel.roles import Perceiver, Appraiser

    store = open_store(args.profile, args.base_dir)
    bus = EventBus()
    mock = MockProvider()
    router = LLMRouter(tiers=MOCK_TIERS, providers={"mock": mock})

    async def run():
        # Run perceiver
        perceiver = Perceiver(router, store, bus)
        result = await perceiver.execute(input_data=args.text)
        print(f"Perceiver: {'OK' if result.success else result.error}")

        # Run appraiser
        appraiser = Appraiser(router, store, bus)
        result = await appraiser.execute()
        print(f"Appraiser: {'OK' if result.success else result.error}")

        # Show updated state
        now = store.now
        if now.context_now:
            print(f"\nContext: {now.context_now.current_task}")
        if now.affect_core:
            print(f"Affect: valence={now.affect_core.valence:+.2f}, arousal={now.affect_core.arousal:.2f}")

    asyncio.run(run())


def cmd_import(args):
    """Import state from JSON file."""
    from selfmodel import open_store, import_state

    # Load JSON
    data = json.loads(Path(args.file).read_text())

    # Open or create store
    store = open_store(args.profile, args.base_dir)

    # Import state
    imported = import_state(store, data)

    print(f"Imported state into profile: {args.profile}")
    for node_name, count in imported.items():
        print(f"  {node_name}: {count} entries")


def cmd_clone(args):
    """Clone a profile to a new key."""
    from selfmodel import open_store, clone_profile

    source = open_store(args.source, args.base_dir)

    target = clone_profile(
        source,
        args.target,
        args.base_dir,
        include_history=not args.latest_only,
    )

    print(f"Cloned {args.source} -> {args.target}")
    print(f"Target state dir: {target.state_dir}")


def cmd_viz(args):
    """Visualize profile state."""
    from selfmodel import open_store
    from selfmodel.viz import (
        state_graph,
        constitution_summary,
        goal_hierarchy,
        belief_map,
        affect_timeline,
        full_report,
    )

    store = open_store(args.profile, args.base_dir)

    viz_funcs = {
        "graph": state_graph,
        "constitution": constitution_summary,
        "goals": goal_hierarchy,
        "beliefs": belief_map,
        "report": full_report,
    }

    if args.view == "affect":
        print(affect_timeline(store, n=args.limit, dimension=args.dimension))
    elif args.view in viz_funcs:
        print(viz_funcs[args.view](store))
    else:
        print(f"Unknown view: {args.view}")


def cmd_query(args):
    """Query profile state."""
    from selfmodel import open_store, query

    store = open_store(args.profile, args.base_dir)
    q = query(store)

    # Map query names to methods
    query_methods = {
        "values": lambda: q.top_values(5),
        "terminal-goals": q.terminal_goals,
        "nonnegotiables": q.nonnegotiables,
        "affect": q.current_affect,
        "emotion": q.current_emotion,
        "stress": q.is_stressed,
        "trend": q.affect_trend,
        "goals": q.active_goals,
        "primary-goal": q.primary_goal,
        "blocked": q.blocked_goals,
        "conflicts": q.goal_conflicts,
        "context": q.current_context,
        "beliefs": q.current_beliefs,
        "traits": q.traits,
        "capabilities": q.capabilities,
        "limits": q.limits,
        "energy": q.energy_state,
        "priors": q.priors,
        "unknowns": q.unknowns,
        "summary": q.summary,
    }

    if args.query_name == "check" and args.action:
        result = q.alignment_check(args.action)
    elif args.query_name == "history" and args.node:
        result = q.recent_entries(args.node, n=args.limit)
    elif args.query_name == "has-value" and args.value:
        result = q.has_value(args.value)
    elif args.query_name in query_methods:
        result = query_methods[args.query_name]()
    else:
        print(f"Unknown query: {args.query_name}")
        print("Available queries: " + ", ".join(query_methods.keys()))
        print("Special queries: check <action>, history <node>, has-value <value>")
        return

    # Print result
    if not result.found:
        print(f"Not found: {result.message}")
    else:
        if result.message:
            print(f"Result: {result.message}")
        if result.value is not None:
            if isinstance(result.value, (list, dict)):
                print(json.dumps(result.value, indent=2, default=str))
            else:
                print(f"Value: {result.value}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Self-Model: Cognitive self-modeling system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  selfmodel bootstrap jacob-heavy-v1
  selfmodel repl jacob-heavy-v1
  selfmodel status jacob-heavy-v1
  selfmodel run jacob-heavy-v1 --mock
  selfmodel export jacob-heavy-v1 -o state.json
  selfmodel input jacob-heavy-v1 "Working on a new project"

Profile format: {name}[-{persona}]-{tier}-{version}
  tier: heavy, light, micro
  example: jacob-heavy-v1, alice-scholar-light-v2
""",
    )

    parser.add_argument(
        "--base-dir", "-d",
        default="state",
        help="Base directory for state storage (default: state)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # bootstrap
    p_bootstrap = subparsers.add_parser("bootstrap", help="Initialize a new profile")
    p_bootstrap.add_argument("profile", help="Profile key (e.g., jacob-heavy-v1)")
    p_bootstrap.add_argument("--constitution", "-c", help="Path to custom constitution JSON")
    p_bootstrap.set_defaults(func=cmd_bootstrap)

    # repl
    p_repl = subparsers.add_parser("repl", help="Interactive REPL")
    p_repl.add_argument("profile", help="Profile key")
    p_repl.add_argument("--mock", "-m", action="store_true", default=True,
                        help="Use mock LLM provider (default: True)")
    p_repl.add_argument("--no-mock", action="store_false", dest="mock",
                        help="Use real LLM providers")
    p_repl.add_argument("--quiet", "-q", action="store_true",
                        help="Suppress verbose output")
    p_repl.set_defaults(func=cmd_repl)

    # status
    p_status = subparsers.add_parser("status", help="Show profile status")
    p_status.add_argument("profile", help="Profile key")
    p_status.set_defaults(func=cmd_status)

    # run
    p_run = subparsers.add_parser("run", help="Run the orchestrator")
    p_run.add_argument("profile", help="Profile key")
    p_run.add_argument("--mock", "-m", action="store_true", default=True,
                       help="Use mock LLM provider (default: True)")
    p_run.add_argument("--no-mock", action="store_false", dest="mock",
                       help="Use real LLM providers")
    p_run.set_defaults(func=cmd_run)

    # export
    p_export = subparsers.add_parser("export", help="Export state to JSON")
    p_export.add_argument("profile", help="Profile key")
    p_export.add_argument("--output", "-o", help="Output file path")
    p_export.set_defaults(func=cmd_export)

    # input
    p_input = subparsers.add_parser("input", help="Send input to a profile")
    p_input.add_argument("profile", help="Profile key")
    p_input.add_argument("text", help="Input text")
    p_input.set_defaults(func=cmd_input)

    # import
    p_import = subparsers.add_parser("import", help="Import state from JSON file")
    p_import.add_argument("profile", help="Profile key to import into")
    p_import.add_argument("file", help="JSON file to import")
    p_import.set_defaults(func=cmd_import)

    # clone
    p_clone = subparsers.add_parser("clone", help="Clone a profile")
    p_clone.add_argument("source", help="Source profile key")
    p_clone.add_argument("target", help="Target profile key")
    p_clone.add_argument("--latest-only", "-l", action="store_true",
                         help="Only copy latest state, not history")
    p_clone.set_defaults(func=cmd_clone)

    # viz
    p_viz = subparsers.add_parser("viz", help="Visualize profile state")
    p_viz.add_argument("profile", help="Profile key")
    p_viz.add_argument("view", nargs="?", default="graph",
                       choices=["graph", "constitution", "goals", "beliefs", "affect", "report"],
                       help="Visualization to show (default: graph)")
    p_viz.add_argument("--dimension", "-D", default="valence",
                       choices=["valence", "arousal", "tension"],
                       help="Dimension for affect timeline (default: valence)")
    p_viz.add_argument("--limit", "-n", type=int, default=20,
                       help="Number of entries for timeline (default: 20)")
    p_viz.set_defaults(func=cmd_viz)

    # query
    p_query = subparsers.add_parser("query", help="Query profile state")
    p_query.add_argument("profile", help="Profile key")
    p_query.add_argument("query_name", help="Query to run (values, affect, goals, etc.)")
    p_query.add_argument("--action", "-a", help="Action to check (for 'check' query)")
    p_query.add_argument("--node", help="Node name (for 'history' query)")
    p_query.add_argument("--value", "-v", help="Value name (for 'has-value' query)")
    p_query.add_argument("--limit", "-n", type=int, default=5,
                         help="Number of entries (default: 5)")
    p_query.set_defaults(func=cmd_query)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        args.func(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
