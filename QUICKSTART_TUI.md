# Self-Model TUI Quick Start Guide

## Installation

```bash
cd /Users/jacob/fun/self-model

# Install with uv (recommended)
uv pip install -e .

# Or with pip
pip install -e .
```

This will install Textual and all other dependencies.

## First Run

### Option 1: Use the Demo Script (Recommended)

```bash
python demo_tui.py
```

This will:
1. Create a demo profile (`demo-heavy-v1`) if it doesn't exist
2. Launch the TUI automatically
3. Show you a working dashboard with sample data

### Option 2: Create Your Own Profile

```bash
# Bootstrap a new profile
python main.py bootstrap myname-heavy-v1

# Launch TUI
python main.py tui myname-heavy-v1

# Or just run with no args to auto-select
python main.py
```

## What You'll See

When you launch the TUI, you'll see:

1. **Header** - Shows profile name and system status
2. **Affect Gauge** - Real-time emotional state (valence, arousal, tension)
3. **Context Panel** - Current task and environment
4. **Goal List** - Active goals with priorities and progress
5. **Event Stream** - Live feed of system events
6. **Stats Panel** - System metrics (ticks, uptime, etc.)
7. **Footer** - Available key bindings

## Essential Key Bindings

| Key | Action |
|-----|--------|
| `q` | Quit |
| `r` | Refresh data |
| `c` | View full constitution |
| `g` | View full goal hierarchy |
| `i` | Enter input mode (send messages) |
| `d` | Toggle dark mode |
| `Esc` | Go back (from sub-screens) |

## Try These Actions

1. **Refresh the dashboard**: Press `r`
   - Watch the data update
   - See the refresh event in the stream

2. **View your constitution**: Press `c`
   - See all your values and weights
   - Review terminal goals
   - Check non-negotiables
   - Press `Esc` to go back

3. **View goals hierarchy**: Press `g`
   - See all active goals
   - Check progress and priorities
   - View current plan
   - Press `Esc` to go back

4. **Send input**: Press `i`
   - Type a message (e.g., "Working on a new feature")
   - Press `Enter` to submit
   - See it appear in the event stream

5. **Toggle dark mode**: Press `d`
   - Switch between light and dark themes

## Understanding the Display

### Affect Gauge
```
Valence  [       │████████] +0.45
```
- Centered bar: positive (right) or negative (left)
- Green = positive, Red = negative
- Value range: -1.0 to +1.0

### Goal Status Icons
- ● Green = Active
- ○ Yellow = Paused
- ⊘ Red = Blocked
- ✓ Green = Completed
- ✗ Gray = Abandoned

### Progress Bars
```
[████████░░] 80%
```
- Filled (█) = completed
- Empty (░) = remaining

### Priority Bars
```
[▓▓▓▓▓░░░░░] 0.85
```
- High priority = more bars
- Range: 0.0 to 1.0

## Navigation

The TUI has three main screens:

1. **Dashboard** (default)
   - Press `c` → Constitution
   - Press `g` → Goals

2. **Constitution**
   - Press `Esc` or `q` → Back to Dashboard
   - Use `↑` `↓` to scroll

3. **Goals**
   - Press `Esc` or `q` → Back to Dashboard
   - Use `↑` `↓` to scroll

## Troubleshooting

### "No profiles found"
```bash
# Create one first
python main.py bootstrap myname-heavy-v1
```

### "Module not found: textual"
```bash
# Install dependencies
uv pip install -e .
# or
pip install -e .
```

### TUI looks weird/misaligned
- Make sure terminal is at least 80 columns wide
- Use a modern terminal (iTerm2, Windows Terminal, etc.)
- Try toggling dark mode with `d`

### No data showing
- Make sure you bootstrapped a profile first
- Check that the profile has some state:
```bash
python main.py status myname-heavy-v1
```

## Next Steps

### Customize Your Profile

Edit your constitution:
```bash
# Export current state
python main.py export myname-heavy-v1 -o state.json

# Edit state.json
# ...

# Re-bootstrap with custom constitution
python main.py bootstrap myname-custom-v1 --constitution state.json
```

### Run the Orchestrator

For live updates (future enhancement):
```bash
# In one terminal
python main.py run myname-heavy-v1

# In another terminal
python main.py tui myname-heavy-v1
```

### Use the REPL

For interactive exploration:
```bash
python main.py repl myname-heavy-v1
```

## Tips

1. **Start with the demo**: `python demo_tui.py` is the fastest way to see it working

2. **Check the status first**: Before launching TUI, verify your profile:
   ```bash
   python main.py status myname-heavy-v1
   ```

3. **Use keyboard shortcuts**: Learn `c`, `g`, `i`, `r` for quick navigation

4. **Watch the event stream**: It shows what's happening in real-time

5. **Resize your terminal**: The TUI is responsive and adapts to size

## Learning More

- **TUI Documentation**: `src/selfmodel/tui/README.md`
- **Implementation Details**: `TUI_IMPLEMENTATION.md`
- **Visual Preview**: `src/selfmodel/tui/VISUAL_PREVIEW.md`
- **Main README**: `README.md` (self-model system overview)

## Common Workflows

### Daily Check-in
```bash
# Launch TUI
python main.py

# Check affect (valence, arousal, tension)
# Review active goals
# See recent events
```

### Goal Review
```bash
# Launch TUI
python main.py

# Press 'g' for full goal view
# Review priorities and progress
# Check for conflicts
```

### Constitution Review
```bash
# Launch TUI
python main.py

# Press 'c' for constitution
# Review values and weights
# Check alignment
```

### Send Input
```bash
# Launch TUI
python main.py

# Press 'i' for input mode
# Type: "Working on project X"
# Press Enter
# Watch event stream for processing
```

## Getting Help

If something doesn't work:
1. Check this guide
2. Read `TUI_IMPLEMENTATION.md` for technical details
3. Try the demo script: `python demo_tui.py`
4. Check that you're using Python 3.11+
5. Verify Textual is installed: `python -c "import textual"`

## Enjoy!

The TUI makes it easy to monitor and interact with your self-model system. Explore, experiment, and customize to fit your workflow.
