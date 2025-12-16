# Self-Model TUI Visual Preview

This document shows what the TUI looks like in the terminal.

## Dashboard View

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Self-Model TUI                                    Profile: demo-heavy-v1     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ AFFECT STATE                   ┃  ┃ CURRENT CONTEXT                     ┃
┃                                ┃  ┃                                     ┃
┃   Valence  [       │████████] +0.45┃  Task: Building TUI for self-model  ┃
┃                                ┃  ┃                                     ┃
┃   Arousal  [███████░░░░░░░░░░] 0.35┃  Location: Home office              ┃
┃                                ┃  ┃  Setting: Solo work                 ┃
┃   Tension  [███░░░░░░░░░░░░░░] 0.20┃  Time Pressure: [██░░░░░░░░] 0.2   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ACTIVE GOALS                   ┃  ┃ EVENT STREAM                        ┃
┃                                ┃  ┃                                     ┃
┃ ● [████████░░] Implement TUI   ┃  ┃ 14:32:15 ↻ dashboard                ┃
┃    priority: ▓▓▓▓▓░░░░░ 0.85   ┃  ┃   Manual refresh triggered          ┃
┃    horizon: session            ┃  ┃ 14:32:10 • affect_core              ┃
┃    serves: Mastery             ┃  ┃   State updated                     ┃
┃                                ┃  ┃ 14:32:05 • user                     ┃
┃ ● [██████░░░░] Write docs      ┃  ┃   Input: Working on TUI             ┃
┃    priority: ▓▓▓▓░░░░░░ 0.65   ┃  ┃ 14:32:00 ⟳ instant_loop            ┃
┃    horizon: session            ┃  ┃   Tick #142                         ┃
┃    serves: Mastery             ┃  ┃ 14:31:55 ⟳ session_loop            ┃
┃                                ┃  ┃   Tick #28                          ┃
┃ ○ [░░░░░░░░░░] Take break      ┃  ┃ 14:31:50 ↻ goals_active            ┃
┃    priority: ▓▓░░░░░░░░ 0.30   ┃  ┃   Goals updated                     ┃
┃    horizon: immediate          ┃  ┃                                     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ SYSTEM STATS                                                               ┃
┃                                                                            ┃
┃ Instant Ticks:  142      Session Ticks: 28                                ┃
┃ Inputs:         5        LLM Calls:     12                                ┃
┃ Uptime:         3.2m                                                       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ q Quit  r Refresh  c Constitution  g Goals  i Input  / Command  d Dark    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

## Constitution View

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Self-Model TUI                                    Profile: demo-heavy-v1     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

═══════════════════════════════════════════════════════
                    CONSTITUTION
═══════════════════════════════════════════════════════

VALUES
───────────────────────────────────────────────────────

MASTERY      [██████████] 1.0
               The pursuit of excellence and deep understanding

AUTONOMY     [█████████░] 0.9
               Independence and self-direction

GROWTH       [████████░░] 0.8
               Continuous learning and development

INTEGRITY    [███████░░░] 0.7
               Honesty and alignment with values

CONNECTION   [██████░░░░] 0.6
               Meaningful relationships


TERMINAL GOALS
───────────────────────────────────────────────────────

  ★ Maximize learning and mastery across domains
  ★ Maintain autonomy and self-direction
  ★ Build systems that scale


NON-NEGOTIABLES
───────────────────────────────────────────────────────

  ⚠ Never compromise integrity for short-term gain
  ⚠ Never sacrifice growth for comfort
  ⚠ Never harm others intentionally


TABOOS
───────────────────────────────────────────────────────

  ✗ Deception or dishonesty
  ✗ Abandoning commitments
  ✗ Ignoring feedback


IDENTITY CLAIMS
───────────────────────────────────────────────────────

  • I am a continuous learner
  • I am autonomous and self-directed
  • I am systems-oriented


DECISION PRINCIPLES
───────────────────────────────────────────────────────

  1. When in doubt, choose growth over comfort
  2. Optimize for long-term value, not short-term ease
  3. Maintain consistency between values and actions

═══════════════════════════════════════════════════════

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Esc Back  q Quit  ↑↓ Scroll                                                ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

## Goals View

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Self-Model TUI                                    Profile: demo-heavy-v1     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

═══════════════════════════════════════════════════════
                   GOAL HIERARCHY
═══════════════════════════════════════════════════════

TERMINAL GOALS (from constitution)
───────────────────────────────────────────────────────

  ★ Maximize learning and mastery across domains
  ★ Maintain autonomy and self-direction
  ★ Build systems that scale

ACTIVE GOALS
───────────────────────────────────────────────────────

PRIMARY: Implement TUI for self-model system

● Implement TUI for self-model system
   Progress: [████████████████░░░░] 80%
   Priority: [████████░░] 0.85
   Horizon: session ↠
   Serves value: Mastery

● Write comprehensive documentation
   Progress: [████████░░░░░░░░░░░░] 40%
   Priority: [██████░░░░] 0.65
   Horizon: session ↠
   Serves value: Mastery

○ Take a break and rest
   Progress: [░░░░░░░░░░░░░░░░░░░░] 0%
   Priority: [███░░░░░░░] 0.30
   Horizon: immediate →
   Serves value: Growth

● Review and refactor code
   Progress: [░░░░░░░░░░░░░░░░░░░░] 0%
   Priority: [████░░░░░░] 0.45
   Horizon: daily ↣
   Serves value: Mastery


ACTIVE PLAN
───────────────────────────────────────────────────────

Goal: Implement TUI for self-model system

Steps:
  ✓ Create widget files
  ✓ Implement affect gauge
  ✓ Implement goal list
  → ● Test with demo profile
      Duration: 300s
  ○ Write documentation
  ○ Final review

═══════════════════════════════════════════════════════

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Esc Back  q Quit  ↑↓ Scroll                                                ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

## Input Mode (Dashboard)

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Self-Model TUI                                    Profile: demo-heavy-v1     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

[... dashboard widgets above ...]

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                                                                            ┃
┃ Enter message:                                                             ┃
┃                                                                            ┃
┃ █ I'm making great progress on the TUI                                    ┃
┃                                                                            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Enter Submit  Esc Cancel                                                   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

## Color Scheme

The TUI uses the following color coding:

### Affect Gauge
- **Positive valence**: Green bars (████)
- **Negative valence**: Red bars (████)
- **Low arousal/tension**: Green
- **Medium arousal/tension**: Yellow
- **High arousal/tension**: Red

### Goals
- **Active goal**: Green ●
- **Paused goal**: Yellow ○
- **Blocked goal**: Red ⊘
- **Completed goal**: Green ✓
- **Abandoned goal**: Dim ✗

### Events
- **Errors**: Red ✗
- **Updates**: Green ↻
- **Ticks**: Yellow ⟳
- **General**: Cyan •

### Borders
- **Primary**: Cyan borders
- **Accent**: Yellow/Gold for input/active elements

### Text
- **Headers**: Bold cyan
- **Labels**: Bold white
- **Values**: Normal white
- **Metadata**: Dim gray

## Responsive Layout

The TUI adapts to terminal size:
- Minimum width: 80 columns (recommended)
- Minimum height: 24 rows (recommended)
- Larger terminals show more content
- Smaller terminals auto-scroll

## Dark Mode

Toggle with `d` key:
- Default: Dark background, light text
- Light mode: Light background, dark text (Textual default themes)

## Accessibility

- All information available without color
- Status indicated by icons (●○⊘✓✗)
- Bar charts supplement numeric values
- Keyboard-only navigation
- Screen reader compatible (via Textual)
