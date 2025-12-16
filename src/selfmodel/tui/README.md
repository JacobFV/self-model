# Self-Model TUI

A beautiful terminal user interface for the self-model system, built with [Textual](https://textual.textualize.io/).

## Features

### Dashboard (Main Screen)
- **Affect Gauge**: Real-time visualization of valence, arousal, and tension
- **Goal List**: Active goals with priorities and progress bars
- **Event Stream**: Live feed of system events
- **Context Panel**: Current task, location, and time pressure
- **Stats Panel**: System metrics (ticks, uptime, LLM calls)

### Constitution View
- Complete view of values with weights
- Terminal goals
- Non-negotiables and taboos
- Identity claims
- Decision principles

### Goals View
- Full goal hierarchy
- Terminal goals from constitution
- Active goals with status, priority, and progress
- Current plan with steps
- Goal conflicts

## Usage

### Launch TUI

```bash
# No args - will auto-select profile or list available profiles
selfmodel

# Explicit profile
selfmodel tui demo-heavy-v1

# With custom state directory
selfmodel tui demo-heavy-v1 -d /path/to/state
```

### Key Bindings

| Key | Action |
|-----|--------|
| `q` | Quit application |
| `r` | Refresh dashboard |
| `c` | View constitution |
| `g` | View goals hierarchy |
| `i` | Enter input mode |
| `/` | Command palette (TODO) |
| `d` | Toggle dark mode |
| `Tab` | Cycle focus |
| `Esc` | Go back / Cancel |

### Input Mode

Press `i` to enter input mode and send messages to the system:
1. Type your message
2. Press `Enter` to send
3. The input will appear in the event stream

## Widgets

### AffectGauge
Displays affect dimensions as horizontal bars:
- **Valence**: Centered bar (-1 to +1), green for positive, red for negative
- **Arousal**: Left-to-right bar (0 to 1), color-coded by intensity
- **Tension**: Left-to-right bar (0 to 1), color-coded by intensity

### GoalList
Shows active goals with:
- Status icon (● active, ○ paused, ⊘ blocked, ✓ completed, ✗ abandoned)
- Progress bar (0-100%)
- Priority bar (0-1 scale)
- Horizon indicator (→ immediate, ↠ session, ↣ daily, ⇢ weekly, ⟿ long-term)
- Value alignment (which value the goal serves)

### EventStream
Live stream of system events:
- Color-coded by type (errors red, updates green, ticks yellow)
- Shows timestamp, source, and message
- Auto-scrolls to show most recent events

### StatsPanel
System statistics:
- Instant loop ticks
- Session loop ticks
- Inputs processed
- LLM calls made
- Uptime

### ContextPanel
Current context information:
- Active task
- Location
- Social setting
- Time pressure (bar)
- Interruptions count

### ConstitutionPanel
Constitution summary:
- Top 5 values with weight bars
- Terminal goals (up to 3)
- Non-negotiables (up to 3)

## Architecture

```
src/selfmodel/tui/
├── __init__.py          # Package exports
├── app.py               # Main Textual App
├── widgets/             # Custom widgets
│   ├── affect_gauge.py
│   ├── goal_list.py
│   ├── event_stream.py
│   ├── stats_panel.py
│   ├── constitution_panel.py
│   └── context_panel.py
└── screens/             # Screen views
    ├── dashboard.py     # Main dashboard
    ├── constitution.py  # Full constitution view
    └── goals.py         # Full goals hierarchy
```

## Future Enhancements

- [ ] Command palette with fuzzy search
- [ ] Profile selector screen
- [ ] Affect timeline chart (text-based sparklines)
- [ ] Belief map visualization
- [ ] Interactive goal editing
- [ ] LLM usage breakdown
- [ ] Real-time orchestrator integration
- [ ] Background task monitoring
- [ ] Export/import from TUI
- [ ] Settings screen
- [ ] Theme customization
- [ ] Keyboard shortcuts help screen

## Development

The TUI uses Textual's reactive framework. Widgets automatically refresh when data changes.

To test the TUI:
```bash
# Create a demo profile
python demo_tui.py

# Or manually
python main.py bootstrap demo-heavy-v1
python main.py tui demo-heavy-v1
```

## Textual Features Used

- **Screens**: For different views (Dashboard, Constitution, Goals)
- **Widgets**: Custom widgets for domain-specific visualization
- **CSS**: For layout and styling
- **Bindings**: Keyboard shortcuts
- **Reactive**: Auto-refreshing data
- **Rich markup**: For colored, styled text

## Performance

The dashboard auto-refreshes every 1 second. This is configurable in `DashboardScreen.on_mount()`.

For production use with the orchestrator running, consider:
- Reducing refresh rate for lower CPU usage
- Using event-driven updates instead of polling
- Implementing lazy loading for large histories
