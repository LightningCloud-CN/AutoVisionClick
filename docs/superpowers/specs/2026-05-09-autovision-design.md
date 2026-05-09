# AutoVision — Automated Screen Recognition Tool

## Context

A Python + OpenCV desktop automation tool for game automation. Users define visual triggers (image templates) that, when matched on screen, execute configurable action chains. The GUI uses CustomTkinter with a dark theme. The core differentiator is a modular logic editor that makes full scripting accessible to beginners through a hybrid tree + flow-preview interface.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| GUI | CustomTkinter (dark theme) |
| Screen capture | mss + PIL/Pillow |
| Template matching | OpenCV (`cv2.matchTemplate`) |
| Input simulation | pydirectinput (keyboard + mouse) |
| Global hotkeys | pynput |
| Project format | JSON scripts + PNG templates in folder |

## Architecture — 4 Engines

### 1. Capture Engine
- **Window selection**: dropdown list of open windows, crosshair drag-to-select, or manual title/process name entry (partial match + regex toggle)
- **Template capture**: built-in screen region snapshot (freeze screen → drag selection → name + save) + file import (PNG/JPG/BMP with optional crop)
- **Coordinate picker**: activate pick mode → crosshair cursor → press Space anywhere to capture coordinates + RGB value → auto-fill into action config

### 2. Match Engine
- OpenCV template matching with configurable method (TM_CCOEFF default) and confidence threshold per trigger
- Multi-template parallel search within a single capture pass
- Match caching to avoid re-scanning static regions when multiple triggers target the same window
- Auto-throttles scan rate when match frequency is low

### 3. Logic Runtime
- Each script runs in its own match loop thread (max 8 concurrent, configurable)
- Shared resource lock for input actions to prevent conflicting clicks/keys
- Per-script variable store (auto-generated: `$match_x`, `$match_y`, `$loop_count`; user-defined supported)
- Per-script isolation — one script crash does not affect others

### 4. GUI (CustomTkinter)
- Main window: script list (left), script tree editor (center), properties panel + mini flow preview (right), event log (bottom)
- Standalone template library panel
- Live dashboard when scripts are running (status, performance, log)

## Logic Module System

### Module Types

**Trigger** (starts a script branch):
- Image Found, Image Lost, Script Start, Hotkey Press, Timer (every N ms), Variable Change

**Action** (does something):
- Click (center of match), Click (coordinate), Press Key, Type Text, Wait (ms), Set Variable, Scroll, Drag

**Condition** (branches execution):
- If Image Visible, If Variable, If Time Elapsed, If Pixel Color, Random Chance

**Loop** (repeats children):
- While Visible, Repeat N times, Until Condition, For Each Match, Forever

**Group** (organizes):
- Named subroutine, reusable block, import from library, collapsible in editor

### Editor Design (Hybrid: List + Flow Preview)
- Left panel: tree list of scripts and their module hierarchy (collapsible, drag-reorderable)
- Center: module palette (drag into tree) + script tree with inline property display
- Right: properties panel for selected module + mini flowchart preview (vertical flow of connected nodes)

## Capture Workflows

### Window Selection
Dropdown list (auto-refreshed), crosshair drag overlay, or manual title entry.

### Template Image
Screen region snapshot tool: freeze screen → drag region → preview + name → saved to `project/images/`. Also import from file with optional crop.

### Coordinate Picker
In any action property panel, a "Pick" button activates pick mode. Tool minimizes, crosshair cursor appears. Press Space to capture coordinates + RGB. Press Esc to cancel. Works while scripts are running for quick calibration.

## Project Structure

```
my_project/
├── project.json          # window target, global settings
├── scripts/
│   ├── auto_accept.json  # one file per script
│   └── heal_check.json
├── images/
│   ├── accept.png
│   └── low_hp.png
└── logs/                 # per-session logs
```

### Script JSON Format
Recursive node tree. Each node has `type`, `subtype`, `config`, and optional `children` array. Triggers are root nodes. Conditions and loops wrap their children. Actions are leaf nodes.

## Runtime Controls

### Global Hotkeys (configurable)

| Default | Action |
|---------|--------|
| Ctrl+Shift+F5 | Start all enabled scripts |
| Ctrl+Shift+F6 | Stop all scripts |
| Ctrl+Shift+F7 | Pause / Resume |
| Ctrl+Shift+F8 | Emergency kill (release all hooks) |
| User-defined | Per-script start/stop |

Hotkeys work when the tool window is minimized.

### Live Dashboard
- Per-script status cards: state (running/paused/error), runtime, match count, last match time, thread health
- Performance panel: CPU usage, match rate, FPS, thread count, memory
- Color-coded event log with timestamps

## Beginner-Friendly Features

1. **Starter templates** — built-in example scripts users can load, inspect, and modify
2. **Quick-start wizard** — 3 questions ("Which image?", "What to do?", "How often?") generates a working script
3. **Inline validation** — red errors (blocks execution), yellow warnings (advisory); tooltips on every module

## Error Handling

| Scenario | Behavior | User sees |
|----------|----------|-----------|
| Window not found | Pause, retry every 2s, auto-resume | Warning with "waiting" status |
| Template match timeout | After N seconds, trigger optional fallback | Info log entry |
| Click/input blocked | Queue and retry when window is foreground | Warning |
| Invalid script JSON | Refuse to run, highlight broken nodes in editor | Error with node count |
| Emergency kill | Stop all threads, release hooks, save state | Red emergency banner |
| Engine crash | Per-script isolation — others unaffected | Error on specific script |

## Validation Rules

**Errors (blocks execution):** trigger with no template, action missing required field, loop with no exit condition, circular group references

**Warnings (advisory):** confidence < 0.7, wait < 100ms, forever loop with no delay, unused templates

## Verification

1. Build the main window shell with CustomTkinter — verify dark theme, layout panels, responsive resize
2. Implement window selection dropdown + crosshair overlay
3. Implement screen region capture (freeze + drag + save)
4. Implement coordinate picker (Space to capture)
5. Implement template matching engine with a single trigger → click action script
6. Implement the logic module tree editor (palette, drag, properties panel, mini flow)
7. Implement parallel script runtime with hotkey controls
8. Test with a real game window: capture a UI button template, run auto-click script, verify detection and clicking
9. Test error scenarios: window lost, emergency stop, invalid config
10. Test beginner wizard: generate a script from 3 questions and verify it runs
