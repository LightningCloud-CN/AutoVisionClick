# AutoVision Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python + CustomTkinter + OpenCV screen recognition automation tool with a hybrid tree/flow visual logic editor.

**Architecture:** Four engines — Capture (mss), Match (OpenCV), Logic Runtime (threaded per-script), GUI (CustomTkinter). Project-based folder storage with JSON scripts + PNG templates. Hybrid editor: left script list, center tree editor with module palette, right properties + mini flow, bottom event log.

**Tech Stack:** Python 3.10+, CustomTkinter, mss, OpenCV, pydirectinput, pynput, Pillow

---

## File Structure

```
autovision/
├── main.py                       # Entry point
├── app.py                        # App controller, wires engines↔GUI
├── config.py                     # Settings, constants, defaults
├── engine/
│   ├── __init__.py
│   ├── capture.py                # mss screen/window capture
│   ├── matcher.py                # OpenCV template matching
│   ├── input_sim.py              # Keyboard/mouse simulation
│   ├── action_executor.py        # Executes action nodes
│   ├── script_runner.py          # Per-script match-loop thread
│   ├── runtime.py                # Multi-script manager + hotkeys
│   └── hotkeys.py                # pynput global hotkey hooks
├── model/
│   ├── __init__.py
│   ├── module_types.py           # Module type enum + metadata
│   ├── script.py                 # Script tree node model
│   ├── variable_store.py         # Per-script variable scope
│   └── project.py                # Project load/save
├── gui/
│   ├── __init__.py
│   ├── styles.py                 # Theme, colors, fonts
│   ├── main_window.py            # Main window shell + layout
│   ├── script_list.py            # Left panel: script list
│   ├── module_palette.py         # Drag-from palette
│   ├── script_editor.py          # Center: tree editor
│   ├── properties_panel.py       # Right: properties form
│   ├── mini_flow.py              # Mini flowchart preview
│   ├── event_log.py              # Bottom: color-coded log
│   ├── template_library.py       # Template management panel
│   ├── dashboard.py              # Live running dashboard
│   ├── wizard.py                 # Beginner quick-start wizard
│   ├── window_selector.py        # Window picker dialog
│   ├── template_capture.py       # Screen region capture tool
│   └── coordinate_picker.py      # Click-to-pick coordinates
├── resources/
│   └── starter_templates/        # Built-in example scripts
└── tests/
    ├── __init__.py
    ├── test_module_types.py
    ├── test_script.py
    ├── test_variable_store.py
    ├── test_project.py
    ├── test_capture.py
    ├── test_matcher.py
    ├── test_input_sim.py
    ├── test_action_executor.py
    ├── test_script_runner.py
    └── test_runtime.py
```

---

## Foundation

### Task 1: Project scaffold and dependencies

**Files:**
- Create: `autovision/__init__.py`
- Create: `autovision/config.py`
- Create: `requirements.txt`
- Create: `autovision/engine/__init__.py`
- Create: `autovision/model/__init__.py`
- Create: `autovision/gui/__init__.py`
- Create: `autovision/resources/__init__.py`
- Create: `autovision/tests/__init__.py`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p autovision/engine autovision/model autovision/gui autovision/resources/starter_templates autovision/tests
```

- [ ] **Step 2: Write requirements.txt**

```txt
customtkinter>=5.2.0
opencv-python>=4.8.0
mss>=9.0.0
pydirectinput>=1.0.4
pynput>=1.7.6
Pillow>=10.0.0
```

- [ ] **Step 3: Write config.py**

```python
"""AutoVision configuration and constants."""

APP_NAME = "AutoVision"
APP_VERSION = "1.0.0"

# Match engine defaults
DEFAULT_CONFIDENCE = 0.85
DEFAULT_MATCH_METHOD = "TM_CCOEFF_NORMED"
DEFAULT_TICK_MS = 500
MAX_CONCURRENT_SCRIPTS = 8

# Hotkey defaults
HK_START_ALL = "<ctrl>+<shift>+F5"
HK_STOP_ALL = "<ctrl>+<shift>+F6"
HK_PAUSE = "<ctrl>+<shift>+F7"
HK_EMERGENCY = "<ctrl>+<shift>+F8"

# GUI defaults
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
THEME = "dark"
COLOR_SCHEME = "dark-blue"

# Capture
SCREENSHOT_FORMAT = "PNG"
TEMPLATE_DIR = "images"
SCRIPT_DIR = "scripts"
LOG_DIR = "logs"
PROJECT_FILENAME = "project.json"

# Validation
MIN_CONFIDENCE_WARN = 0.7
MIN_WAIT_WARN_MS = 100
```

- [ ] **Step 4: Install dependencies**

```bash
pip install -r requirements.txt
```

- [ ] **Step 5: Verify imports**

```bash
python -c "import customtkinter; import cv2; import mss; import pydirectinput; import pynput; print('All imports OK')"
```

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "feat: project scaffold, dependencies, and config"
```

### Task 2: Module type definitions

**Files:**
- Create: `autovision/model/module_types.py`
- Create: `autovision/tests/test_module_types.py`

- [ ] **Step 1: Write the failing test**

```python
"""Tests for module type definitions."""
import pytest
from autovision.model.module_types import ModuleCategory, MODULE_REGISTRY, ModuleDef


def test_module_categories():
    assert ModuleCategory.TRIGGER.value == "trigger"
    assert ModuleCategory.ACTION.value == "action"
    assert ModuleCategory.CONDITION.value == "condition"
    assert ModuleCategory.LOOP.value == "loop"
    assert ModuleCategory.GROUP.value == "group"


def test_registry_has_all_categories():
    cats = {m.category for m in MODULE_REGISTRY}
    assert ModuleCategory.TRIGGER in cats
    assert ModuleCategory.ACTION in cats
    assert ModuleCategory.CONDITION in cats
    assert ModuleCategory.LOOP in cats
    assert ModuleCategory.GROUP in cats


def test_every_module_has_required_fields():
    for mod in MODULE_REGISTRY:
        assert mod.subtype, f"{mod} missing subtype"
        assert mod.label, f"{mod} missing label"
        assert mod.category in ModuleCategory


def test_get_by_subtype():
    m = ModuleDef.get("image_found")
    assert m is not None
    assert m.category == ModuleCategory.TRIGGER
    assert ModuleDef.get("nonexistent") is None


def test_get_by_category():
    triggers = ModuleDef.get_by_category(ModuleCategory.TRIGGER)
    assert len(triggers) >= 3
    assert all(m.category == ModuleCategory.TRIGGER for m in triggers)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd autovision && python -m pytest tests/test_module_types.py -v
```
Expected: FAIL - module not found

- [ ] **Step 3: Write module_types.py**

```python
"""Module type definitions - the palette of available script building blocks."""
from enum import Enum
from dataclasses import dataclass, field


class ModuleCategory(Enum):
    TRIGGER = "trigger"
    ACTION = "action"
    CONDITION = "condition"
    LOOP = "loop"
    GROUP = "group"


@dataclass(frozen=True)
class ModuleDef:
    subtype: str
    category: ModuleCategory
    label: str
    icon: str = ""
    description: str = ""
    config_schema: dict = field(default_factory=dict)

    @classmethod
    def get(cls, subtype: str):
        for m in MODULE_REGISTRY:
            if m.subtype == subtype:
                return m
        return None

    @classmethod
    def get_by_category(cls, category: ModuleCategory) -> list:
        return [m for m in MODULE_REGISTRY if m.category == category]


MODULE_REGISTRY = [
    # Triggers
    ModuleDef("image_found", ModuleCategory.TRIGGER, "Image Found", "🔍",
              "Fires when a template image is found on screen",
              {"template": "", "confidence": 0.85, "region": "full"}),
    ModuleDef("image_lost", ModuleCategory.TRIGGER, "Image Lost", "👁",
              "Fires when a previously visible template disappears",
              {"template": "", "timeout_ms": 5000}),
    ModuleDef("script_start", ModuleCategory.TRIGGER, "Script Start", "▶",
              "Fires immediately when the script starts"),
    ModuleDef("hotkey", ModuleCategory.TRIGGER, "Hotkey Press", "⌨",
              "Fires when a specific hotkey is pressed",
              {"key_combo": ""}),
    ModuleDef("timer", ModuleCategory.TRIGGER, "Timer", "⏱",
              "Fires repeatedly at a set interval",
              {"interval_ms": 1000}),
    ModuleDef("var_change", ModuleCategory.TRIGGER, "Variable Change", "📊",
              "Fires when a variable's value changes",
              {"variable": ""}),

    # Actions
    ModuleDef("click_center", ModuleCategory.ACTION, "Click Center", "🖱",
              "Click the center of a matched image",
              {"button": "left", "offset_x": 0, "offset_y": 0}),
    ModuleDef("click_coord", ModuleCategory.ACTION, "Click Coordinate", "🎯",
              "Click a specific screen coordinate",
              {"x": 0, "y": 0, "button": "left"}),
    ModuleDef("press_key", ModuleCategory.ACTION, "Press Key", "⌨",
              "Press and release a keyboard key",
              {"key": ""}),
    ModuleDef("type_text", ModuleCategory.ACTION, "Type Text", "📝",
              "Type a string of text",
              {"text": ""}),
    ModuleDef("wait", ModuleCategory.ACTION, "Wait", "⏳",
              "Pause execution for a duration",
              {"duration_ms": 500}),
    ModuleDef("set_var", ModuleCategory.ACTION, "Set Variable", "📊",
              "Set a variable to a value",
              {"name": "", "value": ""}),
    ModuleDef("scroll", ModuleCategory.ACTION, "Scroll", "↕",
              "Scroll the mouse wheel",
              {"amount": 1, "x": 0, "y": 0}),
    ModuleDef("drag", ModuleCategory.ACTION, "Drag", "↗",
              "Click and drag from one point to another",
              {"from_x": 0, "from_y": 0, "to_x": 0, "to_y": 0}),

    # Conditions
    ModuleDef("if_visible", ModuleCategory.CONDITION, "If Visible", "👁",
              "Check if a template is visible on screen",
              {"template": "", "confidence": 0.85}),
    ModuleDef("if_variable", ModuleCategory.CONDITION, "If Variable", "🔢",
              "Check a variable against a value",
              {"variable": "", "operator": "eq", "value": ""}),
    ModuleDef("if_elapsed", ModuleCategory.CONDITION, "If Time Elapsed", "⏰",
              "Check if a timer has elapsed",
              {"timer_name": "", "duration_ms": 0}),
    ModuleDef("if_pixel", ModuleCategory.CONDITION, "If Pixel Color", "🎨",
              "Check if a pixel at coordinates has a specific color",
              {"x": 0, "y": 0, "color": "#000000", "tolerance": 10}),
    ModuleDef("random", ModuleCategory.CONDITION, "Random Chance", "🎲",
              "Randomly take this branch with given probability",
              {"percent": 50}),

    # Loops
    ModuleDef("while_visible", ModuleCategory.LOOP, "While Visible", "🔄",
              "Repeat while a template is visible",
              {"template": "", "max_iterations": 0, "delay_ms": 100}),
    ModuleDef("repeat", ModuleCategory.LOOP, "Repeat N Times", "🔁",
              "Repeat a fixed number of times",
              {"count": 1, "delay_ms": 0}),
    ModuleDef("until_condition", ModuleCategory.LOOP, "Until Condition", "⏳",
              "Repeat until a condition is true",
              {"delay_ms": 100}),
    ModuleDef("for_each_match", ModuleCategory.LOOP, "For Each Match", "🔍",
              "Run once for each match found",
              {"template": "", "confidence": 0.85}),
    ModuleDef("forever", ModuleCategory.LOOP, "Forever", "∞",
              "Repeat indefinitely",
              {"delay_ms": 100}),

    # Groups
    ModuleDef("subroutine", ModuleCategory.GROUP, "Subroutine", "📦",
              "A named reusable block of modules",
              {"name": ""}),
    ModuleDef("import_block", ModuleCategory.GROUP, "Import", "📥",
              "Import a block from the library",
              {"source": ""}),
]
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd autovision && python -m pytest tests/test_module_types.py -v
```
Expected: PASS (5 tests)

- [ ] **Step 5: Commit**

```bash
git add autovision/model/module_types.py autovision/tests/test_module_types.py
git commit -m "feat: add module type definitions and registry"
```

### Task 3: Script node model

**Files:**
- Create: `autovision/model/script.py`
- Create: `autovision/tests/test_script.py`

- [ ] **Step 1: Write the failing test**

```python
"""Tests for the script node model."""
import json
from autovision.model.script import ScriptNode, Script


def test_create_leaf_node():
    node = ScriptNode(type="action", subtype="click_center",
                      config={"button": "left", "offset_x": 0, "offset_y": 0})
    assert node.type == "action"
    assert node.subtype == "click_center"
    assert node.children == []


def test_add_child_and_parent_link():
    parent = ScriptNode(type="trigger", subtype="image_found")
    child = ScriptNode(type="action", subtype="click_center")
    parent.add_child(child)
    assert len(parent.children) == 1
    assert child.parent is parent


def test_to_dict_and_from_dict_deep():
    root = ScriptNode(type="trigger", subtype="image_found",
                      config={"template": "btn.png", "confidence": 0.85})
    root.add_child(ScriptNode(type="action", subtype="click_center"))
    loop = ScriptNode(type="loop", subtype="while_visible",
                      config={"template": "btn.png"})
    loop.add_child(ScriptNode(type="action", subtype="wait",
                              config={"duration_ms": 500}))
    root.add_child(loop)

    d = root.to_dict()
    restored = ScriptNode.from_dict(d)

    assert restored.subtype == "image_found"
    assert len(restored.children) == 2
    assert restored.children[1].subtype == "while_visible"
    assert len(restored.children[1].children) == 1


def test_script_wrapper():
    script = Script(
        name="Auto Heal",
        enabled=True,
        hotkey="<ctrl>+<shift>+1",
        window_title="Game",
        tick_ms=500,
        root=ScriptNode(type="trigger", subtype="image_found",
                        config={"template": "low_hp.png"})
    )
    d = script.to_dict()
    restored = Script.from_dict(d)
    assert restored.name == "Auto Heal"
    assert restored.root.subtype == "image_found"

def test_validate_errors():
    root = ScriptNode(type="trigger", subtype="image_found", config={})
    errors = root.validate()
    assert len(errors) > 0

    valid = ScriptNode(type="trigger", subtype="image_found",
                       config={"template": "btn.png", "confidence": 0.85})
    assert valid.validate() == []
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd autovision && python -m pytest tests/test_script.py -v
```
Expected: FAIL - module not found

- [ ] **Step 3: Write script.py**

```python
"""Script node model - recursive tree structure for visual scripts."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable
from autovision.model.module_types import ModuleDef


@dataclass
class ScriptNode:
    type: str
    subtype: str
    config: dict = field(default_factory=dict)
    children: list[ScriptNode] = field(default_factory=list)
    parent: ScriptNode | None = field(default=None, repr=False)

    def add_child(self, child: ScriptNode) -> ScriptNode:
        child.parent = self
        self.children.append(child)
        return self

    def remove_child(self, child: ScriptNode):
        child.parent = None
        self.children.remove(child)

    def insert_child(self, index: int, child: ScriptNode) -> ScriptNode:
        child.parent = self
        self.children.insert(index, child)
        return self

    def find(self, predicate: Callable[[ScriptNode], bool]) -> ScriptNode | None:
        if predicate(self):
            return self
        for child in self.children:
            result = child.find(predicate)
            if result is not None:
                return result
        return None

    def find_all(self, predicate: Callable[[ScriptNode], bool]) -> list[ScriptNode]:
        results = []
        if predicate(self):
            results.append(self)
        for child in self.children:
            results.extend(child.find_all(predicate))
        return results

    def validate(self) -> list[str]:
        errors = []
        mod_def = ModuleDef.get(self.subtype)
        if mod_def is None:
            return [f"Unknown module subtype: {self.subtype}"]
        schema = mod_def.config_schema
        for key in schema:
            if key not in self.config or self.config[key] == "":
                errors.append(f"Missing required config: {key}")
        for child in self.children:
            errors.extend(child.validate())
        return errors

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "subtype": self.subtype,
            "config": self.config,
            "children": [c.to_dict() for c in self.children],
        }

    @classmethod
    def from_dict(cls, data: dict) -> ScriptNode:
        node = cls(
            type=data["type"],
            subtype=data["subtype"],
            config=data.get("config", {}),
        )
        for child_data in data.get("children", []):
            node.add_child(cls.from_dict(child_data))
        return node


@dataclass
class Script:
    name: str
    enabled: bool = True
    hotkey: str = ""
    window_title: str = ""
    window_method: str = "partial"
    tick_ms: int = 500
    root: ScriptNode | None = None

    def to_dict(self) -> dict:
        result = {
            "name": self.name,
            "enabled": self.enabled,
            "hotkey": self.hotkey,
            "window_title": self.window_title,
            "window_method": self.window_method,
            "tick_ms": self.tick_ms,
        }
        if self.root:
            result["root"] = self.root.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: dict) -> Script:
        script = cls(
            name=data["name"],
            enabled=data.get("enabled", True),
            hotkey=data.get("hotkey", ""),
            window_title=data.get("window_title", ""),
            window_method=data.get("window_method", "partial"),
            tick_ms=data.get("tick_ms", 500),
        )
        if "root" in data and data["root"]:
            script.root = ScriptNode.from_dict(data["root"])
        return script
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd autovision && python -m pytest tests/test_script.py -v
```
Expected: PASS (5 tests)

- [ ] **Step 5: Commit**

```bash
git add autovision/model/script.py autovision/tests/test_script.py
git commit -m "feat: add script node model with recursive tree and validation"
```

### Task 4: Variable store

**Files:**
- Create: `autovision/model/variable_store.py`
- Create: `autovision/tests/test_variable_store.py`

- [ ] **Step 1: Write the failing test**

```python
"""Tests for variable store."""
from autovision.model.variable_store import VariableStore

def test_set_and_get():
    store = VariableStore()
    store.set("count", 5)
    assert store.get("count") == 5
    assert store.get("nonexistent") is None
    assert store.get("nonexistent", default=0) == 0

def test_match_variables():
    store = VariableStore()
    store.set_match(845, 420)
    assert store.get("$match_x") == 845
    assert store.get("$match_y") == 420

def test_increment_and_delete():
    store = VariableStore()
    store.set("count", 0)
    assert store.inc("count") == 1
    store.delete("count")
    assert not store.exists("count")

def test_list_all():
    store = VariableStore()
    store.set("a", 1)
    store.set_match(10, 20)
    names = {v["name"] for v in store.list_all()}
    assert "a" in names
    assert "$match_x" in names
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd autovision && python -m pytest tests/test_variable_store.py -v
```
Expected: FAIL - module not found

- [ ] **Step 3: Write variable_store.py**

```python
"""Per-script variable store with auto-generated match variables."""
from threading import Lock


class VariableStore:
    def __init__(self):
        self._data: dict[str, object] = {}
        self._lock = Lock()

    def set(self, name: str, value: object):
        with self._lock:
            self._data[name] = value

    def get(self, name: str, default: object = None) -> object:
        with self._lock:
            return self._data.get(name, default)

    def exists(self, name: str) -> bool:
        with self._lock:
            return name in self._data

    def delete(self, name: str):
        with self._lock:
            self._data.pop(name, None)

    def inc(self, name: str, amount: int = 1) -> int:
        with self._lock:
            current = self._data.get(name, 0)
            if not isinstance(current, (int, float)):
                current = 0
            current += amount
            self._data[name] = current
            return current

    def set_match(self, x: int, y: int):
        self.set("$match_x", x)
        self.set("$match_y", y)

    def set_loop_count(self, count: int):
        self.set("$loop_count", count)

    def clear(self):
        with self._lock:
            self._data.clear()

    def list_all(self) -> list[dict]:
        with self._lock:
            return [{"name": k, "value": v} for k, v in self._data.items()]
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd autovision && python -m pytest tests/test_variable_store.py -v
```
Expected: PASS (4 tests)

- [ ] **Step 5: Commit**

```bash
git add autovision/model/variable_store.py autovision/tests/test_variable_store.py
git commit -m "feat: add variable store with thread-safe auto variables"
```

### Task 5: Project model

**Files:**
- Create: `autovision/model/project.py`
- Create: `autovision/tests/test_project.py`

- [ ] **Step 1: Write the failing test**

```python
"""Tests for project model."""
from autovision.model.project import Project
from autovision.model.script import Script, ScriptNode


def _dummy_script(name="Dummy Script"):
    root = ScriptNode(type="trigger", subtype="image_found",
                      config={"template": "btn.png", "confidence": 0.85})
    root.add_child(ScriptNode(type="action", subtype="click_center"))
    return Script(name=name, root=root)


def test_create_project():
    proj = Project(name="Test Project")
    assert proj.name == "Test Project"
    assert proj.scripts == []
    assert proj.global_hotkeys["start_all"] != ""


def test_add_remove_script():
    proj = Project(name="Test")
    proj.add_script(_dummy_script())
    assert len(proj.scripts) == 1
    proj.remove_script("Dummy Script")
    assert len(proj.scripts) == 0


def test_save_and_load(tmp_path):
    img_dir = tmp_path / "images"
    img_dir.mkdir()
    (tmp_path / "scripts").mkdir()
    (tmp_path / "logs").mkdir()

    proj = Project(name="Test", window_title="MyGame")
    proj.add_script(_dummy_script())
    proj.save(str(tmp_path))

    assert (tmp_path / "project.json").exists()
    loaded = Project.load(str(tmp_path))
    assert loaded.name == "Test"
    assert loaded.window_title == "MyGame"
    assert len(loaded.scripts) == 1


def test_list_templates(tmp_path):
    (tmp_path / "images").mkdir(parents=True)
    (tmp_path / "scripts").mkdir()
    (tmp_path / "logs").mkdir()
    (tmp_path / "images" / "a.png").touch()

    proj = Project(name="T")
    proj.save(str(tmp_path))
    templates = proj.list_templates(str(tmp_path))
    assert len(templates) == 1
    assert "a.png" in templates[0]
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd autovision && python -m pytest tests/test_project.py -v
```
Expected: FAIL - module not found

- [ ] **Step 3: Write project.py**

```python
"""Project model - load/save project folders."""
from __future__ import annotations
import json
import os
from dataclasses import dataclass, field
from autovision.model.script import Script
from autovision.config import (
    PROJECT_FILENAME, TEMPLATE_DIR,
    HK_START_ALL, HK_STOP_ALL, HK_PAUSE, HK_EMERGENCY,
)


@dataclass
class Project:
    name: str
    window_title: str = ""
    window_method: str = "partial"
    scripts: list[Script] = field(default_factory=list)
    global_hotkeys: dict = field(default_factory=lambda: {
        "start_all": HK_START_ALL,
        "stop_all": HK_STOP_ALL,
        "pause": HK_PAUSE,
        "emergency": HK_EMERGENCY,
    })

    def add_script(self, script: Script):
        self.scripts.append(script)

    def remove_script(self, name: str):
        self.scripts = [s for s in self.scripts if s.name != name]

    def get_script(self, name: str) -> Script | None:
        for s in self.scripts:
            if s.name == name:
                return s
        return None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "window_title": self.window_title,
            "window_method": self.window_method,
            "global_hotkeys": self.global_hotkeys,
            "scripts": [s.to_dict() for s in self.scripts],
        }

    @classmethod
    def from_dict(cls, data: dict) -> Project:
        proj = cls(
            name=data.get("name", "Untitled"),
            window_title=data.get("window_title", ""),
            window_method=data.get("window_method", "partial"),
        )
        if "global_hotkeys" in data:
            proj.global_hotkeys.update(data["global_hotkeys"])
        for script_data in data.get("scripts", []):
            proj.add_script(Script.from_dict(script_data))
        return proj

    def save(self, directory: str):
        os.makedirs(directory, exist_ok=True)
        filepath = os.path.join(directory, PROJECT_FILENAME)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, directory: str) -> Project:
        filepath = os.path.join(directory, PROJECT_FILENAME)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Project file not found: {filepath}")
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def list_templates(self, directory: str) -> list[str]:
        img_dir = os.path.join(directory, TEMPLATE_DIR)
        if not os.path.isdir(img_dir):
            return []
        return sorted(
            f for f in os.listdir(img_dir)
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp"))
        )
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd autovision && python -m pytest tests/test_project.py -v
```
Expected: PASS (4 tests)

- [ ] **Step 5: Commit**

```bash
git add autovision/model/project.py autovision/tests/test_project.py
git commit -m "feat: add project model with save/load and template listing"
```

---

## Engine

### Task 6: Screen capture engine

**Files:**
- Create: `autovision/engine/capture.py`
- Create: `autovision/tests/test_capture.py`

- [ ] **Step 1: Write the failing test**

```python
"""Tests for screen capture engine."""
import numpy as np
from autovision.engine.capture import Capture

def test_capture_full_screen():
    cap = Capture()
    img = cap.full_screen()
    assert img is not None
    assert isinstance(img, np.ndarray)
    assert len(img.shape) == 3  # color image
    assert img.shape[2] == 3  # RGB/BGR

def test_list_windows():
    cap = Capture()
    windows = cap.list_windows()
    assert len(windows) > 0
    assert all(isinstance(w, str) for w in windows)
    assert any(len(w) > 0 for w in windows)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd autovision && python -m pytest tests/test_capture.py -v
```
Expected: FAIL - module not found

- [ ] **Step 3: Write capture.py**

```python
"""Screen capture using mss and window enumeration."""
from __future__ import annotations
import numpy as np
import mss
import cv2


class Capture:
    def __init__(self):
        self._sct = mss.mss()

    def full_screen(self) -> np.ndarray:
        monitor = self._sct.monitors[1]
        img = np.array(self._sct.grab(monitor))
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    def region(self, left: int, top: int, width: int, height: int) -> np.ndarray:
        monitor = {"left": left, "top": top, "width": width, "height": height}
        img = np.array(self._sct.grab(monitor))
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    def window(self, title: str, method: str = "partial") -> np.ndarray | None:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        hwnd = self._find_window(title, method)
        if hwnd == 0:
            return None

        rect = wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        if rect.left == rect.right or rect.top == rect.bottom:
            return None

        return self.region(
            rect.left, rect.top,
            rect.right - rect.left,
            rect.bottom - rect.top,
        )

    def _find_window(self, title: str, method: str) -> int:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        windows = []

        def enum_callback(hwnd, _):
            if user32.IsWindowVisible(hwnd):
                text = ctypes.create_unicode_buffer(260)
                user32.GetWindowTextW(hwnd, text, 260)
                if text.value:
                    windows.append((hwnd, text.value))
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        user32.EnumWindows(WNDENUMPROC(enum_callback), 0)

        if method == "exact":
            for hwnd, wtitle in windows:
                if wtitle == title:
                    return hwnd
        elif method == "regex":
            import re
            for hwnd, wtitle in windows:
                if re.search(title, wtitle):
                    return hwnd
        else:  # partial
            title_lower = title.lower()
            for hwnd, wtitle in windows:
                if title_lower in wtitle.lower():
                    return hwnd
        return 0

    def list_windows(self) -> list[str]:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        results = []

        def enum_callback(hwnd, _):
            if user32.IsWindowVisible(hwnd):
                text = ctypes.create_unicode_buffer(260)
                user32.GetWindowTextW(hwnd, text, 260)
                if text.value:
                    results.append(text.value)
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        user32.EnumWindows(WNDENUMPROC(enum_callback), 0)
        return sorted(results)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd autovision && python -m pytest tests/test_capture.py -v
```
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add autovision/engine/capture.py autovision/tests/test_capture.py
git commit -m "feat: add screen capture engine with window enumeration"
```

### Task 7: Template matcher

**Files:**
- Create: `autovision/engine/matcher.py`
- Create: `autovision/tests/test_matcher.py`

- [ ] **Step 1: Write the failing test**

```python
"""Tests for template matcher."""
import numpy as np
import cv2
from autovision.engine.matcher import Matcher, MatchResult

TEMPLATE = np.ones((20, 20, 3), dtype=np.uint8) * 255

def test_matcher_init():
    m = Matcher()
    assert m.default_confidence == 0.85
    assert m.default_method == cv2.TM_CCOEFF_NORMED

def test_find_template_in_image():
    scene = np.zeros((200, 200, 3), dtype=np.uint8)
    scene[80:100, 80:100] = 255  # white square matching template

    m = Matcher()
    results = m.find(TEMPLATE, scene, confidence=0.9)
    assert len(results) > 0
    assert results[0].confidence >= 0.9
    assert abs(results[0].x - 90) <= 2
    assert abs(results[0].y - 90) <= 2

def test_no_match():
    scene = np.zeros((200, 200, 3), dtype=np.uint8)
    m = Matcher()
    results = m.find(TEMPLATE, scene, confidence=0.9)
    assert len(results) == 0

def test_match_result_center():
    r = MatchResult(x=100, y=200, width=30, height=40, confidence=0.92)
    cx, cy = r.center
    assert cx == 115
    assert cy == 220
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd autovision && python -m pytest tests/test_matcher.py -v
```
Expected: FAIL - module not found

- [ ] **Step 3: Write matcher.py**

```python
"""OpenCV template matching engine."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import cv2
from autovision.config import DEFAULT_CONFIDENCE, DEFAULT_MATCH_METHOD


@dataclass
class MatchResult:
    x: int
    y: int
    width: int
    height: int
    confidence: float

    @property
    def center(self) -> tuple[int, int]:
        return (self.x + self.width // 2, self.y + self.height // 2)


METHOD_MAP = {
    "TM_CCOEFF": cv2.TM_CCOEFF,
    "TM_CCOEFF_NORMED": cv2.TM_CCOEFF_NORMED,
    "TM_CCORR": cv2.TM_CCORR,
    "TM_CCORR_NORMED": cv2.TM_CCORR_NORMED,
    "TM_SQDIFF": cv2.TM_SQDIFF,
    "TM_SQDIFF_NORMED": cv2.TM_SQDIFF_NORMED,
}


class Matcher:
    def __init__(self, default_confidence: float = DEFAULT_CONFIDENCE,
                 default_method: str = DEFAULT_MATCH_METHOD):
        self.default_confidence = default_confidence
        self.default_method = METHOD_MAP.get(default_method, cv2.TM_CCOEFF_NORMED)

    def find(self, template: np.ndarray, scene: np.ndarray,
             confidence: float | None = None,
             method: int | None = None) -> list[MatchResult]:
        if confidence is None:
            confidence = self.default_confidence
        if method is None:
            method = self.default_method

        t_h, t_w = template.shape[:2]
        if t_h > scene.shape[0] or t_w > scene.shape[1]:
            return []

        result = cv2.matchTemplate(scene, template, method)
        locations = self._find_peaks(result, confidence, method)

        return [
            MatchResult(x=loc[0], y=loc[1], width=t_w, height=t_h,
                        confidence=float(result[loc[1], loc[0]]))
            for loc in locations
        ]

    def find_multiple(self, templates: dict[str, np.ndarray], scene: np.ndarray,
                      confidence: float | None = None) -> dict[str, list[MatchResult]]:
        return {
            name: self.find(tmpl, scene, confidence)
            for name, tmpl in templates.items()
        }

    def _find_peaks(self, result: np.ndarray, confidence: float,
                    method: int) -> list[tuple[int, int]]:
        if method in (cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED):
            threshold = 1.0 - confidence
            locs = np.where(result <= threshold)
        else:
            locs = np.where(result >= confidence)

        if len(locs[0]) == 0:
            return []

        # Non-maximum suppression
        coords = list(zip(locs[1], locs[0]))
        coords.sort(key=lambda c: result[c[1], c[0]], reverse=True)

        kept = []
        for x, y in coords:
            too_close = False
            for kx, ky in kept:
                if abs(x - kx) < 10 and abs(y - ky) < 10:
                    too_close = True
                    break
            if not too_close:
                kept.append((x, y))
        return kept[:50]  # Max 50 results
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd autovision && python -m pytest tests/test_matcher.py -v
```
Expected: PASS (4 tests)

- [ ] **Step 5: Commit**

```bash
git add autovision/engine/matcher.py autovision/tests/test_matcher.py
git commit -m "feat: add OpenCV template matcher with peak detection"
```

### Task 8: Input simulator

**Files:**
- Create: `autovision/engine/input_sim.py`
- Create: `autovision/tests/test_input_sim.py`

- [ ] **Step 1: Write the failing test**

```python
"""Tests for input simulator (unit tests - no actual input)."""
from autovision.engine.input_sim import InputSim, key_name_to_vk

def test_key_name_to_vk_common():
    assert key_name_to_vk("enter") == 0x0D
    assert key_name_to_vk("space") == 0x20
    assert key_name_to_vk("a") == 0x41
    assert key_name_to_vk("f1") == 0x70

def test_key_name_to_vk_unknown():
    assert key_name_to_vk("zzzz") == 0

def test_input_sim_has_methods():
    sim = InputSim()
    assert hasattr(sim, "click")
    assert hasattr(sim, "press_key")
    assert hasattr(sim, "type_text")
    assert hasattr(sim, "scroll")
    assert hasattr(sim, "move_to")
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd autovision && python -m pytest tests/test_input_sim.py -v
```
Expected: FAIL - module not found

- [ ] **Step 3: Write input_sim.py**

```python
"""Keyboard and mouse input simulation via pydirectinput."""
import time
import pydirectinput

pydirectinput.FAILSAFE = True
pydirectinput.PAUSE = 0.01


_key_map = {
    "enter": 0x0D, "return": 0x0D, "space": 0x20, "tab": 0x09,
    "escape": 0x1B, "esc": 0x1B, "backspace": 0x08,
    "shift": 0x10, "ctrl": 0x11, "alt": 0x12,
    "up": 0x26, "down": 0x28, "left": 0x25, "right": 0x27,
    "insert": 0x2D, "delete": 0x2E, "home": 0x24, "end": 0x23,
    "pageup": 0x21, "pagedown": 0x22,
    "f1": 0x70, "f2": 0x71, "f3": 0x72, "f4": 0x73,
    "f5": 0x74, "f6": 0x75, "f7": 0x76, "f8": 0x77,
    "f9": 0x78, "f10": 0x79, "f11": 0x7A, "f12": 0x7B,
}


def key_name_to_vk(name: str) -> int:
    name = name.lower().strip()
    if name in _key_map:
        return _key_map[name]
    if len(name) == 1 and name.isalnum():
        return ord(name.upper())
    return 0


class InputSim:
    @staticmethod
    def click(x: int, y: int, button: str = "left"):
        pydirectinput.moveTo(x, y)
        time.sleep(0.02)
        pydirectinput.click(button=button)

    @staticmethod
    def press_key(key: str):
        pydirectinput.press(key)

    @staticmethod
    def type_text(text: str):
        pydirectinput.typewrite(text, interval=0.02)

    @staticmethod
    def scroll(amount: int, x: int | None = None, y: int | None = None):
        if x is not None and y is not None:
            pydirectinput.moveTo(x, y)
            time.sleep(0.01)
        pydirectinput.scroll(amount)

    @staticmethod
    def move_to(x: int, y: int):
        pydirectinput.moveTo(x, y)

    @staticmethod
    def drag(from_x: int, from_y: int, to_x: int, to_y: int, button: str = "left"):
        pydirectinput.moveTo(from_x, from_y)
        pydirectinput.mouseDown(button=button)
        time.sleep(0.02)
        pydirectinput.moveTo(to_x, to_y)
        time.sleep(0.02)
        pydirectinput.mouseUp(button=button)

    @staticmethod
    def key_down(key: str):
        pydirectinput.keyDown(key)

    @staticmethod
    def key_up(key: str):
        pydirectinput.keyUp(key)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd autovision && python -m pytest tests/test_input_sim.py -v
```
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add autovision/engine/input_sim.py autovision/tests/test_input_sim.py
git commit -m "feat: add input simulator with keyboard and mouse control"
```

### Task 9: Action executor

**Files:**
- Create: `autovision/engine/action_executor.py`
- Create: `autovision/tests/test_action_executor.py`

- [ ] **Step 1: Write the failing test**

```python
"""Tests for action executor."""
import numpy as np
from autovision.engine.action_executor import ActionExecutor
from autovision.model.script import ScriptNode
from autovision.model.variable_store import VariableStore
from autovision.engine.matcher import MatchResult

def test_execute_wait():
    node = ScriptNode(type="action", subtype="wait", config={"duration_ms": 10})
    store = VariableStore()
    executor = ActionExecutor()
    import time
    start = time.time()
    executor.execute(node, store)
    elapsed = time.time() - start
    assert elapsed >= 0.01

def test_execute_set_var():
    node = ScriptNode(type="action", subtype="set_var",
                      config={"name": "flag", "value": "hello"})
    store = VariableStore()
    executor = ActionExecutor()
    executor.execute(node, store)
    assert store.get("flag") == "hello"

def test_execute_with_match_context():
    match = MatchResult(x=100, y=200, width=30, height=40, confidence=0.95)
    node = ScriptNode(type="action", subtype="click_center",
                      config={"button": "left", "offset_x": 0, "offset_y": 0})
    store = VariableStore()
    executor = ActionExecutor(match_context=match)
    executor.execute(node, store)
    assert store.get("$match_x") == 100
    assert store.get("$match_y") == 200

def test_evaluate_condition_if_variable():
    node = ScriptNode(type="condition", subtype="if_variable",
                      config={"variable": "hp", "operator": "lt", "value": "50"})
    store = VariableStore()
    store.set("hp", 30)
    executor = ActionExecutor()
    assert executor.evaluate_condition(node, store) is True

    store.set("hp", 80)
    assert executor.evaluate_condition(node, store) is False
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd autovision && python -m pytest tests/test_action_executor.py -v
```
Expected: FAIL - module not found

- [ ] **Step 3: Write action_executor.py**

```python
"""Executes action nodes and evaluates condition nodes."""
from __future__ import annotations
import time
import random
from autovision.model.variable_store import VariableStore
from autovision.model.script import ScriptNode
from autovision.engine.matcher import MatchResult
from autovision.engine.input_sim import InputSim


class ActionExecutor:
    def __init__(self, match_context: MatchResult | None = None,
                 capture_service=None, matcher_service=None):
        self._match = match_context
        self._capture = capture_service
        self._matcher = matcher_service
        self._input = InputSim()
        self._interrupted = False

    def interrupt(self):
        self._interrupted = True

    def execute(self, node: ScriptNode, store: VariableStore):
        if self._interrupted:
            return
        self._execute_one(node, store)

    def evaluate_condition(self, node: ScriptNode, store: VariableStore) -> bool:
        return self._eval_condition(node, store)

    def _execute_one(self, node: ScriptNode, store: VariableStore):
        subtype = node.subtype
        cfg = node.config

        # Update match variables if we have context
        if self._match:
            store.set_match(self._match.x, self._match.y)

        if subtype == "click_center" and self._match:
            cx, cy = self._match.center
            self._input.click(
                cx + int(cfg.get("offset_x", 0)),
                cy + int(cfg.get("offset_y", 0)),
                button=cfg.get("button", "left"),
            )
        elif subtype == "click_coord":
            self._input.click(
                int(cfg.get("x", 0)), int(cfg.get("y", 0)),
                button=cfg.get("button", "left"),
            )
        elif subtype == "press_key":
            self._input.press_key(cfg.get("key", ""))
        elif subtype == "type_text":
            self._input.type_text(str(cfg.get("text", "")))
        elif subtype == "wait":
            duration = int(cfg.get("duration_ms", 500)) / 1000.0
            time.sleep(duration)
        elif subtype == "set_var":
            store.set(cfg["name"], cfg["value"])
        elif subtype == "scroll":
            self._input.scroll(
                int(cfg.get("amount", 1)),
                x=int(cfg.get("x", 0)) if cfg.get("x") != 0 else None,
                y=int(cfg.get("y", 0)) if cfg.get("y") != 0 else None,
            )
        elif subtype == "drag":
            self._input.drag(
                int(cfg["from_x"]), int(cfg["from_y"]),
                int(cfg["to_x"]), int(cfg["to_y"]),
            )

    def _eval_condition(self, node: ScriptNode, store: VariableStore) -> bool:
        cfg = node.config
        subtype = node.subtype

        if subtype == "if_variable":
            var = cfg["variable"]
            op = cfg.get("operator", "eq")
            val = cfg.get("value", "")
            current = store.get(var)
            if current is None:
                return False
            return self._compare(current, op, val)
        elif subtype == "random":
            return random.randint(1, 100) <= int(cfg.get("percent", 50))
        elif subtype == "if_visible":
            if not self._capture or not self._matcher:
                return False
            # Template matching needed - handled by script runner
            return False
        return False

    @staticmethod
    def _compare(current, op: str, target) -> bool:
        try:
            curr_num = float(current)
            tgt_num = float(target)
            if op == "eq":
                return curr_num == tgt_num
            if op == "neq":
                return curr_num != tgt_num
            if op == "lt":
                return curr_num < tgt_num
            if op == "lte":
                return curr_num <= tgt_num
            if op == "gt":
                return curr_num > tgt_num
            if op == "gte":
                return curr_num >= tgt_num
        except (ValueError, TypeError):
            if op == "eq":
                return str(current) == str(target)
            if op == "neq":
                return str(current) != str(target)
        return False
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd autovision && python -m pytest tests/test_action_executor.py -v
```
Expected: PASS (4 tests)

- [ ] **Step 5: Commit**

```bash
git add autovision/engine/action_executor.py autovision/tests/test_action_executor.py
git commit -m "feat: add action executor with condition evaluation"
```

### Task 10: Script runner (per-script thread)

**Files:**
- Create: `autovision/engine/script_runner.py`
- Create: `autovision/tests/test_script_runner.py`

- [ ] **Step 1: Write the failing test**

```python
"""Tests for script runner."""
import time
import numpy as np
import cv2
from autovision.engine.script_runner import ScriptRunner, ScriptState
from autovision.model.script import Script, ScriptNode
from autovision.model.variable_store import VariableStore

TEMPLATE = np.ones((20, 20, 3), dtype=np.uint8) * 255

def _make_scene():
    scene = np.zeros((200, 200, 3), dtype=np.uint8)
    scene[80:100, 80:100] = 255
    return scene

class FakeCapture:
    def __init__(self, img):
        self.img = img
    def window(self, title, method):
        return self.img.copy()
    def full_screen(self):
        return self.img.copy()

class FakeMatcher:
    def find(self, template, scene, confidence, method=None):
        return []  # no match
    def find_multiple(self, templates, scene, confidence):
        return {}

def test_script_runner_lifecycle():
    root = ScriptNode(type="trigger", subtype="script_start")
    root.add_child(ScriptNode(type="action", subtype="set_var",
                              config={"name": "x", "value": 1}))
    script = Script(name="Test", root=root, tick_ms=100)

    cap = FakeCapture(_make_scene())
    matcher = FakeMatcher()
    runner = ScriptRunner(script, cap, matcher)
    assert runner.state == ScriptState.IDLE

    runner.start()
    time.sleep(0.3)
    assert runner.store.get("x") == 1
    runner.stop()
    assert runner.state == ScriptState.STOPPED

def test_pause_resume():
    root = ScriptNode(type="trigger", subtype="script_start")
    script = Script(name="PauseTest", root=root, tick_ms=100)

    runner = ScriptRunner(script, FakeCapture(_make_scene()), FakeMatcher())
    runner.start()
    time.sleep(0.1)
    runner.pause()
    assert runner.state == ScriptState.PAUSED
    runner.resume()
    assert runner.state == ScriptState.RUNNING
    runner.stop()
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd autovision && python -m pytest tests/test_script_runner.py -v
```
Expected: FAIL - module not found

- [ ] **Step 3: Write script_runner.py**

```python
"""Per-script match-loop thread."""
from __future__ import annotations
import time
import threading
from enum import Enum
from autovision.model.script import Script, ScriptNode
from autovision.model.variable_store import VariableStore
from autovision.engine.action_executor import ActionExecutor
from autovision.engine.matcher import MatchResult


class ScriptState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


class ScriptRunner:
    def __init__(self, script: Script, capture_service, matcher_service):
        self.script = script
        self._capture = capture_service
        self._matcher = matcher_service
        self.store = VariableStore()
        self.state = ScriptState.IDLE
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._pause_event.set()
        self._match_count = 0
        self._last_match_time: float | None = None
        self._start_time: float | None = None
        self._error: str | None = None
        self.log: list[tuple[float, str, str]] = []  # (timestamp, level, message)

    def start(self):
        if self.state == ScriptState.RUNNING:
            return
        self._stop_event.clear()
        self._pause_event.set()
        self.state = ScriptState.RUNNING
        self._start_time = time.time()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        self._pause_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3)
        self.state = ScriptState.STOPPED

    def pause(self):
        self._pause_event.clear()
        self.state = ScriptState.PAUSED

    def resume(self):
        self._pause_event.set()
        self.state = ScriptState.RUNNING

    def runtime_seconds(self) -> float:
        if self._start_time is None:
            return 0
        return time.time() - self._start_time

    def _loop(self):
        try:
            while not self._stop_event.is_set():
                self._pause_event.wait()
                self._tick()
                time.sleep(self.script.tick_ms / 1000.0)
        except Exception as e:
            self.state = ScriptState.ERROR
            self._error = str(e)
            self._log("ERROR", f"Script crashed: {e}")

    def _tick(self):
        if self.script.root is None:
            return

        # Capture target window
        scene = None
        if self.script.window_title:
            scene = self._capture.window(self.script.window_title,
                                         self.script.window_method)
        if scene is None:
            scene = self._capture.full_screen()

        # Process each trigger in root
        self._process_node(self.script.root, scene)

    def _process_node(self, node: ScriptNode, scene):
        if node.type == "trigger":
            self._handle_trigger(node, scene)
        elif node.type == "action":
            executor = ActionExecutor()
            executor.execute(node, self.store)
        elif node.type == "condition":
            executor = ActionExecutor(capture_service=self._capture,
                                      matcher_service=self._matcher)
            if executor.evaluate_condition(node, self.store):
                for child in node.children:
                    self._process_node(child, scene)
        elif node.type == "loop":
            self._handle_loop(node, scene)

    def _handle_trigger(self, node: ScriptNode, scene):
        subtype = node.subtype
        if subtype == "script_start":
            if self._match_count == 0:
                self._execute_children(node, scene)
            return

        if subtype == "image_found":
            template = self._load_template(node.config["template"])
            if template is not None:
                matches = self._matcher.find(
                    template, scene,
                    confidence=node.config.get("confidence", 0.85),
                )
                for match in matches:
                    self._match_count += 1
                    self._last_match_time = time.time()
                    self._log("INFO",
                              f"Match: {node.config['template']} at ({match.x},{match.y}) "
                              f"conf={match.confidence:.2f}")
                    executor = ActionExecutor(match_context=match)
                    for child in node.children:
                        executor.execute(child, self.store)
        elif subtype == "timer":
            # Simple: fire children every interval
            self._execute_children(node, scene)

    def _handle_loop(self, node: ScriptNode, scene):
        subtype = node.subtype
        max_iter = int(node.config.get("max_iterations", 0)) or 999999
        count = 0

        while count < max_iter and not self._stop_event.is_set():
            self._pause_event.wait()
            if subtype == "while_visible":
                template = self._load_template(node.config.get("template", ""))
                if template is not None:
                    matches = self._matcher.find(template, scene,
                                                 confidence=node.config.get("confidence", 0.85))
                    if not matches:
                        break
            for child in node.children:
                self._process_node(child, scene)
            count += 1
            self.store.set_loop_count(count)
            delay = int(node.config.get("delay_ms", 100)) / 1000.0
            if delay > 0:
                time.sleep(delay)

    def _execute_children(self, node: ScriptNode, scene):
        executor = ActionExecutor()
        for child in node.children:
            executor.execute(child, self.store)

    def _load_template(self, name: str):
        import os
        if not name:
            return None
        # Try project images dir first, then templates in script config
        import cv2
        import numpy as np
        try:
            return cv2.imread(name)
        except Exception:
            return np.zeros((10, 10, 3), dtype=np.uint8)

    def _log(self, level: str, message: str):
        self.log.append((time.time(), level, message))
        if len(self.log) > 1000:
            self.log = self.log[-500:]
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd autovision && python -m pytest tests/test_script_runner.py -v
```
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add autovision/engine/script_runner.py autovision/tests/test_script_runner.py
git commit -m "feat: add per-script runner thread with match loop"
```

### Task 11: Runtime manager + hotkeys

**Files:**
- Create: `autovision/engine/hotkeys.py`
- Create: `autovision/engine/runtime.py`
- Create: `autovision/tests/test_runtime.py`

- [ ] **Step 1: Write the test**

```python
"""Tests for runtime manager."""
import time
import numpy as np
from autovision.engine.runtime import Runtime, RuntimeState
from autovision.engine.script_runner import ScriptState
from autovision.model.project import Project
from autovision.model.script import Script, ScriptNode

class FakeCapture:
    def window(self, title, method):
        return np.zeros((100, 100, 3), dtype=np.uint8)
    def full_screen(self):
        return np.zeros((100, 100, 3), dtype=np.uint8)
    def list_windows(self):
        return ["Test Window"]

class FakeMatcher:
    def find(self, template, scene, confidence, method=None):
        return []
    def find_multiple(self, templates, scene, confidence):
        return {}

def test_runtime_start_stop():
    proj = Project(name="Test")
    root = ScriptNode(type="trigger", subtype="script_start")
    root.add_child(ScriptNode(type="action", subtype="set_var",
                              config={"name": "x", "value": 42}))
    proj.add_script(Script(name="TestScript", root=root, tick_ms=100))

    rt = Runtime(proj, FakeCapture(), FakeMatcher())
    assert rt.state == RuntimeState.IDLE

    rt.start_all()
    assert rt.state == RuntimeState.RUNNING
    time.sleep(0.3)
    runner = rt.get_runner("TestScript")
    assert runner is not None
    assert runner.store.get("x") == 42
    rt.stop_all()
    assert rt.state == RuntimeState.STOPPED

def test_runtime_pause_resume():
    proj = Project(name="Test")
    proj.add_script(Script(name="S", root=ScriptNode(type="trigger", subtype="script_start"), tick_ms=100))

    rt = Runtime(proj, FakeCapture(), FakeMatcher())
    rt.start_all()
    time.sleep(0.1)
    rt.pause_all()
    assert rt.state == RuntimeState.PAUSED
    rt.resume_all()
    assert rt.state == RuntimeState.RUNNING
    rt.stop_all()

def test_runtime_emergency_stop():
    proj = Project(name="Test")
    proj.add_script(Script(name="S", root=ScriptNode(type="trigger", subtype="script_start"), tick_ms=100))

    rt = Runtime(proj, FakeCapture(), FakeMatcher())
    rt.start_all()
    time.sleep(0.1)
    rt.emergency_stop()
    assert rt.state == RuntimeState.STOPPED
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd autovision && python -m pytest tests/test_runtime.py -v
```
Expected: FAIL - module not found

- [ ] **Step 3: Write hotkeys.py**

```python
"""Global hotkey manager using pynput."""
from __future__ import annotations
from pynput import keyboard


class HotkeyManager:
    def __init__(self):
        self._listener: keyboard.Listener | None = None
        self._actions: dict[str, callable] = {}
        self._pressed = set()
        self._running = False

    def register(self, combo: str, action: callable):
        self._actions[combo] = action

    def unregister(self, combo: str):
        self._actions.pop(combo, None)

    def start(self):
        if self._running:
            return
        self._listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
        self._listener.start()
        self._running = True

    def stop(self):
        self._running = False
        if self._listener:
            self._listener.stop()
            self._listener = None

    def _on_press(self, key):
        try:
            self._pressed.add(self._key_name(key))
        except Exception:
            return
        self._check_combos()

    def _on_release(self, key):
        try:
            self._pressed.discard(self._key_name(key))
        except Exception:
            pass

    def _check_combos(self):
        for combo, action in self._actions.items():
            parts = [p.strip().lower().replace("+", "") for p in combo.split("+")]
            required = set()
            for p in parts:
                p = p.strip()
                if p == "ctrl":
                    required.add("ctrl")
                elif p == "shift":
                    required.add("shift")
                elif p == "alt":
                    required.add("alt")
                else:
                    required.add(p.lower())
            if required and required == self._pressed:
                action()

    @staticmethod
    def _key_name(key) -> str:
        if hasattr(key, "name"):
            return key.name
        if hasattr(key, "char") and key.char:
            return key.char.lower()
        return str(key).lower()
```

- [ ] **Step 4: Write runtime.py**

```python
"""Multi-script runtime manager."""
from __future__ import annotations
from enum import Enum
from autovision.model.project import Project
from autovision.model.script import Script
from autovision.engine.script_runner import ScriptRunner, ScriptState
from autovision.engine.hotkeys import HotkeyManager
from autovision.config import MAX_CONCURRENT_SCRIPTS


class RuntimeState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"


class Runtime:
    def __init__(self, project: Project, capture_service, matcher_service):
        self.project = project
        self._capture = capture_service
        self._matcher = matcher_service
        self._runners: dict[str, ScriptRunner] = {}
        self.state = RuntimeState.IDLE
        self.hotkeys = HotkeyManager()
        self._setup_hotkeys()

    def _setup_hotkeys(self):
        hk = self.project.global_hotkeys
        if hk.get("start_all"):
            self.hotkeys.register(hk["start_all"], self.start_all)
        if hk.get("stop_all"):
            self.hotkeys.register(hk["stop_all"], self.stop_all)
        if hk.get("pause"):
            self.hotkeys.register(hk["pause"], self.toggle_pause)
        if hk.get("emergency"):
            self.hotkeys.register(hk["emergency"], self.emergency_stop)

    def start_all(self):
        self.hotkeys.start()
        enabled = [s for s in self.project.scripts if s.enabled]
        for i, script in enumerate(enabled):
            if i >= MAX_CONCURRENT_SCRIPTS:
                break
            runner = ScriptRunner(script, self._capture, self._matcher)
            self._runners[script.name] = runner
            runner.start()
        self.state = RuntimeState.RUNNING

    def stop_all(self):
        for runner in self._runners.values():
            runner.stop()
        self._runners.clear()
        self.hotkeys.stop()
        self.state = RuntimeState.STOPPED

    def pause_all(self):
        for runner in self._runners.values():
            runner.pause()
        self.state = RuntimeState.PAUSED

    def resume_all(self):
        for runner in self._runners.values():
            runner.resume()
        self.state = RuntimeState.RUNNING

    def toggle_pause(self):
        if self.state == RuntimeState.RUNNING:
            self.pause_all()
        elif self.state == RuntimeState.PAUSED:
            self.resume_all()

    def emergency_stop(self):
        for runner in self._runners.values():
            runner.stop()
        self._runners.clear()
        self.hotkeys.stop()
        self.state = RuntimeState.STOPPED

    def get_runner(self, name: str) -> ScriptRunner | None:
        return self._runners.get(name)

    def get_all_runners(self) -> list[ScriptRunner]:
        return list(self._runners.values())

    def start_single(self, name: str):
        script = self.project.get_script(name)
        if script is None or name in self._runners:
            return
        runner = ScriptRunner(script, self._capture, self._matcher)
        self._runners[name] = runner
        runner.start()

    def stop_single(self, name: str):
        runner = self._runners.pop(name, None)
        if runner:
            runner.stop()
```

- [ ] **Step 5: Run test to verify it passes**

```bash
cd autovision && python -m pytest tests/test_runtime.py -v
```
Expected: PASS (3 tests)

- [ ] **Step 6: Commit**

```bash
git add autovision/engine/hotkeys.py autovision/engine/runtime.py autovision/tests/test_runtime.py
git commit -m "feat: add runtime manager with global hotkey support"
```

---

## GUI

### Task 12: GUI styles

**Files:**
- Create: `autovision/gui/styles.py`

- [ ] **Step 1: Write styles.py**

```python
"""GUI theme, colors, and fonts."""
import customtkinter as ctk

# Color palette (dark theme)
BG_DARK = "#0d1117"
BG_PANEL = "#161b22"
BG_CARD = "#1a1a2e"
BG_INPUT = "#0f3460"
BORDER = "#30363d"

ACCENT_RED = "#e94560"
ACCENT_GREEN = "#00ff99"
ACCENT_BLUE = "#00ccff"
ACCENT_YELLOW = "#ffc107"
ACCENT_PURPLE = "#c792ea"

TEXT_PRIMARY = "#e6edf3"
TEXT_SECONDARY = "#8b949e"
TEXT_MUTED = "#484f58"

CATEGORY_COLORS = {
    "trigger": ACCENT_RED,
    "action": ACCENT_GREEN,
    "condition": ACCENT_YELLOW,
    "loop": ACCENT_BLUE,
    "group": TEXT_SECONDARY,
}

FONT_FAMILY = "Segoe UI"
FONT_MONO = "Cascadia Code"


def apply_theme():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")


def styled_frame(parent, **kwargs):
    return ctk.CTkFrame(
        parent,
        fg_color=BG_PANEL,
        border_color=BORDER,
        border_width=1,
        corner_radius=8,
        **kwargs,
    )


def styled_button(parent, text, color=ACCENT_BLUE, **kwargs):
    return ctk.CTkButton(
        parent,
        text=text,
        fg_color=color,
        hover_color=_darken(color, 0.15),
        corner_radius=6,
        font=(FONT_FAMILY, 12),
        **kwargs,
    )


def styled_label(parent, text, size=12, color=TEXT_PRIMARY, **kwargs):
    return ctk.CTkLabel(
        parent,
        text=text,
        text_color=color,
        font=(FONT_FAMILY, size),
        **kwargs,
    )


def _darken(hex_color: str, factor: float) -> str:
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r = max(0, int(r * (1 - factor)))
    g = max(0, int(g * (1 - factor)))
    b = max(0, int(b * (1 - factor)))
    return f"#{r:02x}{g:02x}{b:02x}"
```

- [ ] **Step 2: Commit**

```bash
git add autovision/gui/styles.py && git commit -m "feat: add GUI styles, theme, and color palette"
```

### Task 13: Main window shell

**Files:**
- Create: `autovision/gui/main_window.py`
- Create: `autovision/main.py`
- Create: `autovision/app.py`

- [ ] **Step 1: Write main_window.py**

```python
"""Main application window."""
import customtkinter as ctk
from autovision.gui.styles import apply_theme, BG_DARK
from autovision.config import APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT


class MainWindow(ctk.CTk):
    def __init__(self, app_controller=None):
        super().__init__()
        apply_theme()
        self._app = app_controller

        self.title(f"⚡ {APP_NAME}")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.configure(fg_color=BG_DARK)
        self.minsize(900, 600)

        # Grid layout
        self.grid_columnconfigure(0, weight=0, minsize=200)  # left sidebar
        self.grid_columnconfigure(1, weight=3)  # center editor
        self.grid_columnconfigure(2, weight=1, minsize=220)  # right panel
        self.grid_rowconfigure(0, weight=3)  # main content
        self.grid_rowconfigure(1, weight=1, minsize=120)  # bottom log

        self.left_frame = None
        self.center_frame = None
        self.right_frame = None
        self.bottom_frame = None

        # Placeholder frames - populated by app controller
        self._create_shell()

        # Menu bar
        self._create_menu()

        # Bind close
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _create_shell(self):
        from autovision.gui.styles import styled_frame, styled_label, BG_PANEL

        self.left_frame = styled_frame(self)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(4, 2), pady=4)

        self.center_frame = styled_frame(self)
        self.center_frame.grid(row=0, column=1, sticky="nsew", padx=2, pady=4)

        self.right_frame = styled_frame(self)
        self.right_frame.grid(row=0, column=2, sticky="nsew", padx=(2, 4), pady=4)

        self.bottom_frame = styled_frame(self)
        self.bottom_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=4, pady=(2, 4))

        # Toolbar on center frame top
        self.toolbar = ctk.CTkFrame(self.center_frame, fg_color="transparent", height=36)
        self.toolbar.pack(fill="x", padx=6, pady=(6, 2))

    def _create_menu(self):
        from tkinter import Menu
        menubar = Menu(self, bg="#161b22", fg="#e6edf3", activebackground="#1f2937",
                       activeforeground="#00ccff")
        file_menu = Menu(menubar, tearoff=0, bg="#161b22", fg="#e6edf3")
        file_menu.add_command(label="New Project", command=self._menu("new_project"))
        file_menu.add_command(label="Open Project", command=self._menu("open_project"))
        file_menu.add_command(label="Save Project", command=self._menu("save_project"))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_close)
        menubar.add_cascade(label="File", menu=file_menu)

        run_menu = Menu(menubar, tearoff=0, bg="#161b22", fg="#e6edf3")
        run_menu.add_command(label="Start All", command=self._menu("start_all"))
        run_menu.add_command(label="Stop All", command=self._menu("stop_all"))
        run_menu.add_command(label="Pause/Resume", command=self._menu("toggle_pause"))
        menubar.add_cascade(label="Run", menu=run_menu)

        tools_menu = Menu(menubar, tearoff=0, bg="#161b22", fg="#e6edf3")
        tools_menu.add_command(label="Capture Template", command=self._menu("capture_template"))
        tools_menu.add_command(label="Template Library", command=self._menu("template_library"))
        tools_menu.add_command(label="Pick Coordinate", command=self._menu("pick_coordinate"))
        tools_menu.add_command(label="Quick Start Wizard", command=self._menu("wizard"))
        menubar.add_cascade(label="Tools", menu=tools_menu)

        self.config(menu=menubar)

    def _menu(self, action: str):
        def handler():
            if self._app:
                self._app.handle_menu(action)
        return handler

    def _on_close(self):
        if self._app:
            self._app.shutdown()
        self.destroy()
```

- [ ] **Step 2: Write app.py**

```python
"""Application controller - wires engines and GUI together."""
from autovision.engine.capture import Capture
from autovision.engine.matcher import Matcher
from autovision.engine.runtime import Runtime, RuntimeState
from autovision.model.project import Project


class AppController:
    def __init__(self):
        self.capture = Capture()
        self.matcher = Matcher()
        self.project: Project | None = None
        self.project_dir: str | None = None
        self.runtime: Runtime | None = None
        self._window = None

    def set_window(self, window):
        self._window = window

    def new_project(self, name: str):
        self.project = Project(name=name)

    def load_project(self, directory: str):
        self.project = Project.load(directory)
        self.project_dir = directory

    def save_project(self):
        if self.project and self.project_dir:
            self.project.save(self.project_dir)

    def start_all(self):
        if self.project:
            self.runtime = Runtime(self.project, self.capture, self.matcher)
            self.runtime.start_all()

    def stop_all(self):
        if self.runtime:
            self.runtime.stop_all()
            self.runtime = None

    def toggle_pause(self):
        if self.runtime:
            self.runtime.toggle_pause()

    def emergency_stop(self):
        if self.runtime:
            self.runtime.emergency_stop()
            self.runtime = None

    def get_runtime(self) -> Runtime | None:
        return self.runtime

    def handle_menu(self, action: str):
        handlers = {
            "start_all": self.start_all,
            "stop_all": self.stop_all,
            "toggle_pause": self.toggle_pause,
        }
        handler = handlers.get(action)
        if handler:
            handler()

    def shutdown(self):
        self.emergency_stop()
```

- [ ] **Step 3: Write main.py**

```python
"""Entry point for AutoVision."""
import sys
from autovision.gui.main_window import MainWindow
from autovision.app import AppController


def main():
    app = AppController()
    window = MainWindow(app_controller=app)
    app.set_window(window)
    window.mainloop()


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Verify it launches (smoke test)**

```bash
python -c "from autovision.gui.main_window import MainWindow; from autovision.app import AppController; print('GUI imports OK')"
```

- [ ] **Step 5: Commit**

```bash
git add autovision/gui/styles.py autovision/gui/main_window.py autovision/app.py autovision/main.py
git commit -m "feat: add main window shell and app controller"
```

### Task 14: Script list + module palette panels

**Files:**
- Create: `autovision/gui/script_list.py`
- Create: `autovision/gui/module_palette.py`

- [ ] **Step 1: Write script_list.py**

```python
"""Left sidebar: script list panel."""
import customtkinter as ctk
from autovision.gui.styles import (
    styled_frame, styled_label, styled_button,
    BG_PANEL, BG_CARD, ACCENT_RED, ACCENT_GREEN,
    TEXT_PRIMARY, TEXT_SECONDARY,
)


class ScriptListPanel(ctk.CTkScrollableFrame):
    def __init__(self, parent, app_controller=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self._app = app_controller
        self._scripts: list[dict] = []
        self._on_select = None
        self._on_add = None
        self._build_ui()

    def _build_ui(self):
        from autovision.gui.styles import FONT_FAMILY

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=6, pady=(6, 4))
        styled_label(header, "SCRIPTS", size=10, color=TEXT_SECONDARY).pack(side="left")
        styled_button(
            header, "+ New", color=ACCENT_GREEN,
            width=50, height=22,
            font=(FONT_FAMILY, 10),
            command=self._on_add_click,
        ).pack(side="right")

        self._list_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._list_frame.pack(fill="both", expand=True, padx=4)

    def _on_add_click(self):
        if self._on_add:
            self._on_add()

    def set_on_select(self, callback):
        self._on_select = callback

    def set_on_add(self, callback):
        self._on_add = callback

    def refresh(self, scripts: list):
        for w in self._list_frame.winfo_children():
            w.destroy()
        self._scripts = scripts
        from autovision.gui.styles import FONT_FAMILY, BG_CARD
        for i, s in enumerate(scripts):
            color = ACCENT_RED if s.get("errors") else TEXT_PRIMARY
            btn = ctk.CTkButton(
                self._list_frame,
                text=f"  {s['name']}",
                fg_color=BG_CARD if i % 2 == 0 else "transparent",
                hover_color="#1f2937",
                text_color=color,
                font=(FONT_FAMILY, 11),
                anchor="w",
                corner_radius=0,
                command=lambda n=s['name']: self._select(n),
            )
            btn.pack(fill="x", padx=2, pady=0)

    def _select(self, name: str):
        if self._on_select:
            self._on_select(name)
```

- [ ] **Step 2: Write module_palette.py**

```python
"""Module palette - drag source for available modules."""
import customtkinter as ctk
from autovision.gui.styles import (
    styled_frame, styled_label,
    BG_PANEL, BG_CARD, TEXT_SECONDARY, CATEGORY_COLORS,
)
from autovision.model.module_types import ModuleCategory, MODULE_REGISTRY, ModuleDef


class ModulePalette(ctk.CTkScrollableFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", label_text="MODULE PALETTE",
                         label_fg_color=TEXT_SECONDARY, **kwargs)
        self._on_add_module = None
        self._build()

    def _build(self):
        for category in ModuleCategory:
            modules = ModuleDef.get_by_category(category)
            if not modules:
                continue
            self._add_category_header(category)
            for mod in modules:
                self._add_module_button(mod)

    def _add_category_header(self, category: ModuleCategory):
        color = CATEGORY_COLORS.get(category.value, TEXT_SECONDARY)
        label = ctk.CTkLabel(
            self,
            text=f"{category.value.upper()}",
            text_color=color,
            font=("Segoe UI", 9, "bold"),
        )
        label.pack(fill="x", padx=8, pady=(8, 2))

    def _add_module_button(self, mod: ModuleDef):
        color = CATEGORY_COLORS.get(mod.category.value, TEXT_SECONDARY)
        btn = ctk.CTkButton(
            self,
            text=f"  {mod.icon}  {mod.label}",
            fg_color=BG_CARD,
            hover_color="#1f2937",
            text_color=color,
            font=("Segoe UI", 10),
            anchor="w",
            corner_radius=4,
            height=28,
            command=lambda m=mod: self._on_click(m),
        )
        btn.pack(fill="x", padx=6, pady=1)

    def set_on_add_module(self, callback):
        self._on_add_module = callback

    def _on_click(self, mod: ModuleDef):
        if self._on_add_module:
            self._on_add_module(mod)
```

- [ ] **Step 3: Commit**

```bash
git add autovision/gui/script_list.py autovision/gui/module_palette.py
git commit -m "feat: add script list and module palette panels"
```

### Task 15: Script tree editor

**Files:**
- Create: `autovision/gui/script_editor.py`

- [ ] **Step 1: Write script_editor.py**

```python
"""Center panel: script tree editor."""
import customtkinter as ctk
from autovision.gui.styles import (
    styled_frame, styled_label, styled_button,
    BG_PANEL, BG_CARD, BG_INPUT, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    ACCENT_RED, ACCENT_GREEN, ACCENT_BLUE, CATEGORY_COLORS,
)
from autovision.model.script import Script, ScriptNode
from autovision.model.module_types import ModuleDef


class ScriptEditor(ctk.CTkFrame):
    def __init__(self, parent, app_controller=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self._app = app_controller
        self._script: Script | None = None
        self._selected_node: ScriptNode | None = None
        self._on_node_select = None
        self._on_script_modified = None
        self._tree_frame = None
        self._build()

    def _build(self):
        from autovision.gui.styles import FONT_FAMILY

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=6, pady=(6, 2))
        styled_label(header, "SCRIPT EDITOR", size=10, color=TEXT_SECONDARY).pack(side="left")

        self._script_name_label = styled_label(header, "", size=11, color=TEXT_PRIMARY)
        self._script_name_label.pack(side="left", padx=16)

        self._tree_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._tree_frame.pack(fill="both", expand=True, padx=4, pady=4)

    def set_on_node_select(self, callback):
        self._on_node_select = callback

    def set_on_script_modified(self, callback):
        self._on_script_modified = callback

    def load_script(self, script: Script):
        self._script = script
        self._script_name_label.configure(text=script.name)
        self._refresh_tree()

    def get_selected(self) -> ScriptNode | None:
        return self._selected_node

    def add_module(self, mod: ModuleDef, parent: ScriptNode | None = None):
        if self._script is None:
            return
        if parent is None:
            parent = self._script.root
        if parent is None:
            node = ScriptNode(type=mod.category.value, subtype=mod.subtype,
                              config={k: v for k, v in mod.config_schema.items()})
            self._script.root = node
        else:
            node = ScriptNode(type=mod.category.value, subtype=mod.subtype,
                              config={k: v for k, v in mod.config_schema.items()})
            parent.add_child(node)
        self._refresh_tree()
        if self._on_script_modified:
            self._on_script_modified()

    def remove_selected(self):
        if self._selected_node and self._selected_node.parent:
            self._selected_node.parent.remove_child(self._selected_node)
            self._selected_node = None
            self._refresh_tree()
            if self._on_script_modified:
                self._on_script_modified()

    def move_up(self):
        node = self._selected_node
        if node and node.parent:
            idx = node.parent.children.index(node)
            if idx > 0:
                node.parent.children[idx], node.parent.children[idx - 1] = \
                    node.parent.children[idx - 1], node.parent.children[idx]
                self._refresh_tree()

    def move_down(self):
        node = self._selected_node
        if node and node.parent:
            idx = node.parent.children.index(node)
            if idx < len(node.parent.children) - 1:
                node.parent.children[idx], node.parent.children[idx + 1] = \
                    node.parent.children[idx + 1], node.parent.children[idx]
                self._refresh_tree()

    def _refresh_tree(self):
        for w in self._tree_frame.winfo_children():
            w.destroy()
        if self._script and self._script.root:
            self._render_node(self._script.root, depth=0)

    def _render_node(self, node: ScriptNode, depth: int):
        from autovision.gui.styles import FONT_FAMILY

        mod = ModuleDef.get(node.subtype)
        icon = mod.icon if mod else "?"
        label = mod.label if mod else node.subtype
        color = CATEGORY_COLORS.get(node.type, TEXT_PRIMARY)

        is_selected = node is self._selected_node
        bg = "#1f2937" if is_selected else "transparent"

        row = ctk.CTkFrame(self._tree_frame, fg_color=bg, height=28)
        row.pack(fill="x", padx=(depth * 16, 2), pady=0)
        row.bind("<Button-1>", lambda e, n=node: self._select_node(n))

        padding = "    " * depth
        text = f"{padding}{icon}  {label}"
        if node.config:
            summary = ", ".join(f"{k}={v}" for k, v in list(node.config.items())[:2])
            text += f"  •  {summary}"

        lbl = styled_label(row, text, size=10, color=color)
        lbl.pack(side="left", padx=4)
        lbl.bind("<Button-1>", lambda e, n=node: self._select_node(n))

        for child in node.children:
            self._render_node(child, depth + 1)

    def _select_node(self, node: ScriptNode):
        self._selected_node = node
        self._refresh_tree()
        if self._on_node_select:
            self._on_node_select(node)
```

- [ ] **Step 2: Commit**

```bash
git add autovision/gui/script_editor.py && git commit -m "feat: add script tree editor"
```

### Task 16: Properties panel + mini flow preview

**Files:**
- Create: `autovision/gui/properties_panel.py`
- Create: `autovision/gui/mini_flow.py`

- [ ] **Step 1: Write properties_panel.py**

```python
"""Right panel: properties editor for selected module."""
import customtkinter as ctk
from autovision.gui.styles import (
    styled_frame, styled_label, styled_button,
    BG_PANEL, BG_CARD, BG_INPUT, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    ACCENT_GREEN,
)
from autovision.model.script import ScriptNode
from autovision.model.module_types import ModuleDef


class PropertiesPanel(ctk.CTkScrollableFrame):
    def __init__(self, parent, app_controller=None, **kwargs):
        super().__init__(parent, fg_color="transparent", label_text="PROPERTIES",
                         label_fg_color=TEXT_SECONDARY, **kwargs)
        self._app = app_controller
        self._node: ScriptNode | None = None
        self._inputs: dict[str, ctk.CTkEntry] = {}
        self._on_pick_coord = None
        self._on_modified = None
        self._build_placeholder()

    def _build_placeholder(self):
        self._content = ctk.CTkFrame(self, fg_color="transparent")
        self._content.pack(fill="both", expand=True, padx=6, pady=6)
        styled_label(self._content, "Select a module\nto edit properties",
                     size=10, color=TEXT_MUTED).pack(pady=20)

    def set_on_pick_coord(self, callback):
        self._on_pick_coord = callback

    def set_on_modified(self, callback):
        self._on_modified = callback

    def load_node(self, node: ScriptNode | None):
        for w in self._content.winfo_children():
            w.destroy()
        self._inputs.clear()
        self._node = node

        if node is None:
            styled_label(self._content, "Select a module\nto edit properties",
                         size=10, color=TEXT_MUTED).pack(pady=20)
            return

        mod = ModuleDef.get(node.subtype)
        if mod is None:
            styled_label(self._content, f"Unknown: {node.subtype}",
                         size=10, color=TEXT_MUTED).pack(pady=20)
            return

        styled_label(self._content, f"{mod.icon} {mod.label}",
                     size=12, color=TEXT_PRIMARY).pack(anchor="w", pady=(0, 2))
        styled_label(self._content, mod.description, size=9,
                     color=TEXT_SECONDARY).pack(anchor="w", pady=(0, 8))

        for key, default in mod.config_schema.items():
            row = ctk.CTkFrame(self._content, fg_color="transparent")
            row.pack(fill="x", pady=2)
            styled_label(row, key, size=10, color=TEXT_SECONDARY).pack(anchor="w")

            entry = ctk.CTkEntry(
                row,
                fg_color=BG_INPUT,
                border_color="#30363d",
                font=("Segoe UI", 10),
                height=28,
            )
            entry.pack(fill="x", pady=(1, 4))
            current = node.config.get(key, default)
            entry.insert(0, str(current))
            entry.bind("<FocusOut>", lambda e, k=key, ent=entry: self._save_field(k, ent.get()))
            entry.bind("<Return>", lambda e, k=key, ent=entry: self._save_field(k, ent.get()))
            self._inputs[key] = entry

        # Coordinate picker button for click_coord
        if node.subtype == "click_coord":
            styled_button(
                self._content, "📍 Pick Coordinates", color=ACCENT_GREEN,
                height=28, font=("Segoe UI", 10),
                command=self._on_pick,
            ).pack(fill="x", pady=(8, 0))

    def _on_pick(self):
        if self._on_pick_coord:
            self._on_pick_coord()

    def _save_field(self, key: str, value: str):
        if self._node is None:
            return
        schema = ModuleDef.get(self._node.subtype)
        if schema:
            default = schema.config_schema.get(key)
            if isinstance(default, (int, float)):
                try:
                    value = type(default)(value)
                except ValueError:
                    value = default
            self._node.config[key] = value
        if self._on_modified:
            self._on_modified()
```

- [ ] **Step 2: Write mini_flow.py**

```python
"""Mini flowchart preview panel."""
import customtkinter as ctk
from autovision.gui.styles import (
    styled_frame, styled_label,
    BG_CARD, TEXT_SECONDARY, CATEGORY_COLORS,
)
from autovision.model.script import ScriptNode
from autovision.model.module_types import ModuleDef


class MiniFlowPreview(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", height=160, **kwargs)
        self.pack_propagate(False)

    def render(self, node: ScriptNode | None):
        for w in self.winfo_children():
            w.destroy()
        if node is None:
            styled_label(self, "No module selected", size=9,
                         color=TEXT_SECONDARY).pack(pady=20)
            return

        styled_label(self, "FLOW PREVIEW", size=9, color=TEXT_SECONDARY).pack(
            anchor="w", padx=6, pady=(6, 4))

        # Show the node and its children as a vertical flow
        self._render_flow_node(node)

    def _render_flow_node(self, node: ScriptNode):
        mod = ModuleDef.get(node.subtype)
        label = mod.label if mod else node.subtype
        color = CATEGORY_COLORS.get(node.type, TEXT_SECONDARY)

        row = ctk.CTkFrame(self, fg_color=BG_CARD, height=22, corner_radius=4)
        row.pack(fill="x", padx=8, pady=2)

        styled_label(row, f" {mod.icon if mod else '•'} {label}",
                     size=9, color=color).pack(side="left", padx=4)

        if node.children:
            sep = ctk.CTkFrame(self, fg_color=TEXT_SECONDARY, width=1, height=10)
            sep.pack()
            for child in node.children:
                self._render_flow_node(child)
```

- [ ] **Step 3: Commit**

```bash
git add autovision/gui/properties_panel.py autovision/gui/mini_flow.py
git commit -m "feat: add properties panel and mini flow preview"
```

### Task 17: Event log

**Files:**
- Create: `autovision/gui/event_log.py`

- [ ] **Step 1: Write event_log.py**

```python
"""Bottom panel: event log viewer."""
import customtkinter as ctk
from autovision.gui.styles import (
    styled_frame, styled_label, styled_button,
    BG_PANEL, BG_CARD, TEXT_PRIMARY, TEXT_SECONDARY,
    ACCENT_RED, ACCENT_GREEN, ACCENT_YELLOW, ACCENT_BLUE,
)


LEVEL_COLORS = {
    "INFO": ACCENT_GREEN,
    "WARN": ACCENT_YELLOW,
    "ERROR": ACCENT_RED,
    "DEBUG": ACCENT_BLUE,
}


class EventLog(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self._entries: list[tuple[str, str, str]] = []  # (timestamp, level, message)
        self._build()

    def _build(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=6, pady=(6, 2))

        styled_label(header, "EVENT LOG", size=10, color=TEXT_SECONDARY).pack(side="left")
        clear_btn = styled_button(
            header, "Clear", color="#30363d",
            width=50, height=20, font=("Segoe UI", 9),
            command=self.clear,
        )
        clear_btn.pack(side="right")

        self._log_frame = ctk.CTkScrollableFrame(self, fg_color=BG_CARD, height=100)
        self._log_frame.pack(fill="both", expand=True, padx=6, pady=(2, 6))

    def add(self, level: str, message: str):
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self._entries.append((timestamp, level, message))
        if len(self._entries) > 500:
            self._entries = self._entries[-250:]
        self._append_line(timestamp, level, message)

    def _append_line(self, timestamp: str, level: str, message: str):
        color = LEVEL_COLORS.get(level, TEXT_SECONDARY)
        line = f"[{timestamp}] {level:5s} {message}"
        lbl = styled_label(self._log_frame, line, size=9, color=color)
        lbl.pack(anchor="w", padx=4, pady=0)
        # Auto-scroll to bottom
        self._log_frame._parent_canvas.yview_moveto(1.0)

    def add_from_runner(self, runner_log: list):
        for ts, level, msg in runner_log:
            from datetime import datetime
            timestamp = datetime.fromtimestamp(ts).strftime("%H:%M:%S")
            if (timestamp, level, msg) not in self._entries:
                self._entries.append((timestamp, level, msg))
                self._append_line(timestamp, level, msg)

    def clear(self):
        self._entries.clear()
        for w in self._log_frame.winfo_children():
            w.destroy()
```

- [ ] **Step 2: Commit**

```bash
git add autovision/gui/event_log.py && git commit -m "feat: add event log panel"
```

### Task 18: Template library

**Files:**
- Create: `autovision/gui/template_library.py`

- [ ] **Step 1: Write template_library.py**

```python
"""Template library management panel."""
import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
from autovision.gui.styles import (
    styled_frame, styled_label, styled_button,
    BG_PANEL, BG_CARD, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    ACCENT_GREEN, ACCENT_RED,
)
from autovision.model.project import Project


class TemplateLibrary(ctk.CTkToplevel):
    def __init__(self, parent, app_controller=None):
        super().__init__(parent)
        self._app = app_controller
        self.title("Template Library")
        self.geometry("500x500")
        self.configure(fg_color=BG_PANEL)
        self._on_select = None
        self._build()

    def _build(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(10, 6))
        styled_label(header, "TEMPLATE LIBRARY", size=11, color=TEXT_SECONDARY).pack(side="left")
        styled_button(
            header, "+ Import", color=ACCENT_GREEN,
            width=70, height=24, font=("Segoe UI", 10),
            command=self._import_file,
        ).pack(side="right")

        self._grid = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._grid.pack(fill="both", expand=True, padx=10, pady=6)

        self._info = styled_label(self, "", size=9, color=TEXT_MUTED)
        self._info.pack(padx=10, pady=(0, 10))

    def set_on_select(self, callback):
        self._on_select = callback

    def refresh(self):
        for w in self._grid.winfo_children():
            w.destroy()
        if self._app and self._app.project and self._app.project_dir:
            templates = self._app.project.list_templates(self._app.project_dir)
            self._info.configure(text=f"{len(templates)} templates in project")
            for name in templates:
                self._add_card(name)
        else:
            self._info.configure(text="No project open")

    def _add_card(self, name: str):
        card = ctk.CTkFrame(self._grid, fg_color=BG_CARD, corner_radius=6)
        card.pack(fill="x", padx=2, pady=2)

        path = os.path.join(self._app.project_dir, "images", name)
        styled_label(card, f"🖼 {name}", size=10, color=TEXT_PRIMARY).pack(
            side="left", padx=8, pady=6)

        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="right", padx=4)
        styled_button(
            info_frame, "Del", color=ACCENT_RED,
            width=35, height=22, font=("Segoe UI", 9),
            command=lambda n=name: self._delete(n),
        ).pack(side="right", padx=2)
        styled_button(
            info_frame, "Use", color=ACCENT_GREEN,
            width=35, height=22, font=("Segoe UI", 9),
            command=lambda n=name: self._select(n),
        ).pack(side="right", padx=2)

    def _select(self, name: str):
        if self._on_select:
            self._on_select(name)
        self.destroy()

    def _delete(self, name: str):
        if self._app and self._app.project_dir:
            path = os.path.join(self._app.project_dir, "images", name)
            if os.path.exists(path):
                os.remove(path)
            self.refresh()

    def _import_file(self):
        from tkinter import filedialog
        files = filedialog.askopenfilenames(
            title="Import Template Images",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp"), ("All", "*.*")],
        )
        if files and self._app and self._app.project_dir:
            img_dir = os.path.join(self._app.project_dir, "images")
            os.makedirs(img_dir, exist_ok=True)
            import shutil
            for f in files:
                shutil.copy(f, os.path.join(img_dir, os.path.basename(f)))
            self.refresh()
```

- [ ] **Step 2: Commit**

```bash
git add autovision/gui/template_library.py && git commit -m "feat: add template library panel"
```

### Task 19: Window selector, template capture, coordinate picker

**Files:**
- Create: `autovision/gui/window_selector.py`
- Create: `autovision/gui/template_capture.py`
- Create: `autovision/gui/coordinate_picker.py`

- [ ] **Step 1: Write window_selector.py**

```python
"""Window selection dialog."""
import customtkinter as ctk
from autovision.gui.styles import (
    styled_frame, styled_label, styled_button,
    BG_PANEL, BG_CARD, BG_INPUT, TEXT_PRIMARY, TEXT_SECONDARY,
    ACCENT_GREEN, ACCENT_BLUE,
)


class WindowSelector(ctk.CTkToplevel):
    def __init__(self, parent, app_controller=None):
        super().__init__(parent)
        self._app = app_controller
        self.title("Select Target Window")
        self.geometry("400x400")
        self.configure(fg_color=BG_PANEL)
        self.result = None
        self._build()

    def _build(self):
        styled_label(self, "SELECT TARGET WINDOW", size=11,
                     color=TEXT_SECONDARY).pack(pady=(10, 4))

        # Tab-like buttons for method
        tab_frame = ctk.CTkFrame(self, fg_color="transparent")
        tab_frame.pack(fill="x", padx=10, pady=4)

        self._method = ctk.StringVar(value="list")
        ctk.CTkRadioButton(tab_frame, text="List", variable=self._method,
                           value="list", command=self._show_list).pack(side="left", padx=4)
        ctk.CTkRadioButton(tab_frame, text="Manual", variable=self._method,
                           value="manual", command=self._show_manual).pack(side="left", padx=4)

        self._list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._manual_frame = ctk.CTkFrame(self, fg_color="transparent")

        self._manual_entry = ctk.CTkEntry(
            self._manual_frame,
            fg_color=BG_INPUT,
            placeholder_text="Enter window title or process name...",
            font=("Segoe UI", 10),
            height=30,
        )
        self._manual_entry.pack(fill="x", padx=10, pady=4)

        method_var = ctk.StringVar(value="partial")
        for text, val in [("Partial match", "partial"), ("Exact match", "exact"), ("Regex", "regex")]:
            ctk.CTkRadioButton(self._manual_frame, text=text, variable=method_var,
                               value=val).pack(anchor="w", padx=20, pady=1)

        self._show_list()
        self._populate_list()

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=(8, 10))
        styled_button(btn_frame, "Select", color=ACCENT_GREEN,
                      command=self._on_select).pack(side="right", padx=4)
        styled_button(btn_frame, "Cancel", color="#30363d",
                      command=self.destroy).pack(side="right", padx=4)

    def _show_list(self):
        self._manual_frame.pack_forget()
        self._list_frame.pack(fill="both", expand=True, padx=10, pady=4)

    def _show_manual(self):
        self._list_frame.pack_forget()
        self._manual_frame.pack(fill="both", expand=True, padx=10, pady=4)

    def _populate_list(self):
        if self._app:
            windows = self._app.capture.list_windows()
            for w in windows:
                btn = ctk.CTkButton(
                    self._list_frame,
                    text=w[:60],
                    fg_color="transparent",
                    hover_color="#1f2937",
                    font=("Segoe UI", 10),
                    anchor="w",
                    command=lambda title=w: self._select_from_list(title),
                )
                btn.pack(fill="x", pady=0)

    def _select_from_list(self, title: str):
        self._manual_entry.delete(0, "end")
        self._manual_entry.insert(0, title)

    def _on_select(self):
        title = self._manual_entry.get().strip()
        if title:
            self.result = (title, self._method.get())
        self.destroy()
```

- [ ] **Step 2: Write template_capture.py**

```python
"""Screen region capture tool for creating templates."""
import customtkinter as ctk
import tkinter as tk
from PIL import Image
import numpy as np
import os
from autovision.gui.styles import (
    styled_label, styled_button, styled_frame,
    BG_PANEL, TEXT_SECONDARY, ACCENT_GREEN, ACCENT_RED,
)


class TemplateCapture:
    def __init__(self, app_controller):
        self._app = app_controller
        self._start = None
        self._rect = None

    def start_capture(self):
        """Launch a full-screen overlay to select a region."""
        self._overlay = tk.Toplevel()
        self._overlay.attributes("-fullscreen", True)
        self._overlay.attributes("-alpha", 0.3)
        self._overlay.attributes("-topmost", True)
        self._overlay.configure(bg="black")

        self._canvas = tk.Canvas(self._overlay, bg="black", highlightthickness=0)
        self._canvas.pack(fill="both", expand=True)

        self._canvas.bind("<ButtonPress-1>", self._on_press)
        self._canvas.bind("<B1-Motion>", self._on_drag)
        self._canvas.bind("<ButtonRelease-1>", self._on_release)
        self._overlay.bind("<Escape>", lambda e: self._overlay.destroy())

        self._overlay.focus_force()

    def _on_press(self, event):
        self._start = (event.x, event.y)
        if self._rect:
            self._canvas.delete(self._rect)
        self._rect = None

    def _on_drag(self, event):
        if self._start:
            if self._rect:
                self._canvas.delete(self._rect)
            self._rect = self._canvas.create_rectangle(
                self._start[0], self._start[1], event.x, event.y,
                outline="#00ff99", width=2, dash=(4, 2),
            )

    def _on_release(self, event):
        if self._start is None:
            return
        x1, y1 = self._start
        x2, y2 = event.x, event.y
        if abs(x2 - x1) < 5 or abs(y2 - y1) < 5:
            self._overlay.destroy()
            return

        left, right = sorted([x1, x2])
        top, bottom = sorted([y1, y2])

        self._overlay.destroy()

        # Capture and save
        img = self._app.capture.region(left, top, right - left, bottom - top)
        self._save_template(img, left, top, right, bottom)

    def _save_template(self, img: np.ndarray, left, top, right, bottom):
        import cv2

        # Show preview + name dialog
        dialog = ctk.CTkToplevel()
        dialog.title("Save Template")
        dialog.geometry("350x250")
        dialog.configure(fg_color=BG_PANEL)

        styled_label(dialog, "SAVE TEMPLATE", size=11, color=TEXT_SECONDARY).pack(pady=(10, 4))
        styled_label(dialog, f"Region: {right-left}x{bottom-top}",
                     size=9, color=TEXT_SECONDARY).pack()

        entry = ctk.CTkEntry(dialog, placeholder_text="Template name...",
                             font=("Segoe UI", 11), height=30)
        entry.pack(fill="x", padx=20, pady=(10, 4))
        entry.focus()

        def save():
            name = entry.get().strip()
            if not name:
                return
            if not self._app.project_dir:
                from tkinter import messagebox
                messagebox.showwarning("No Project", "Open or create a project first.")
                dialog.destroy()
                return
            img_dir = os.path.join(self._app.project_dir, "images")
            os.makedirs(img_dir, exist_ok=True)
            path = os.path.join(img_dir, f"{name}.png")
            cv2.imwrite(path, img)
            dialog.destroy()

        styled_button(dialog, "Save", color=ACCENT_GREEN,
                      command=save).pack(pady=(8, 4))
        dialog.bind("<Return>", lambda e: save())
```

- [ ] **Step 3: Write coordinate_picker.py**

```python
"""Coordinate picker - click on screen to capture coordinates."""
import tkinter as tk
from autovision.gui.styles import ACCENT_GREEN, ACCENT_RED


class CoordinatePicker:
    def __init__(self, callback):
        self._callback = callback
        self._result = None

    def start(self):
        import mss
        import numpy as np

        self._overlay = tk.Toplevel()
        self._overlay.attributes("-fullscreen", True)
        self._overlay.attributes("-alpha", 0.15)
        self._overlay.attributes("-topmost", True)
        self._overlay.configure(bg="black", cursor="crosshair")

        self._overlay.bind("<KeyPress-space>", self._on_capture)
        self._overlay.bind("<Escape>", lambda e: self._overlay.destroy())
        self._overlay.bind("<Button-1>", self._on_capture)

        # Floating info label
        self._info = tk.Label(
            self._overlay, text="Press SPACE or click to capture | ESC to cancel",
            bg="#161b22", fg="#00ccff", font=("Segoe UI", 10),
            padx=10, pady=4,
        )
        self._info.place(relx=0.5, rely=0.02, anchor="n")

        self._overlay.focus_force()
        self._overlay.lift()

    def _on_capture(self, event):
        x, y = event.x, event.y if hasattr(event, "x") else self._overlay.winfo_pointerxy()

        # Get RGB at this position
        try:
            import mss
            sct = mss.mss()
            monitor = {"left": x, "top": y, "width": 1, "height": 1}
            img = sct.grab(monitor)
            r, g, b = img.pixel(0, 0)
        except Exception:
            r, g, b = 0, 0, 0

        self._overlay.destroy()
        if self._callback:
            self._callback(x, y, (r, g, b))
```

- [ ] **Step 4: Commit**

```bash
git add autovision/gui/window_selector.py autovision/gui/template_capture.py autovision/gui/coordinate_picker.py
git commit -m "feat: add window selector, template capture, and coordinate picker"
```

### Task 20: Dashboard + Wizard + Integration

**Files:**
- Create: `autovision/gui/dashboard.py`
- Create: `autovision/gui/wizard.py`
- Modify: `autovision/gui/main_window.py` - wire all panels
- Modify: `autovision/app.py` - connect GUI to app controller

- [ ] **Step 1: Write dashboard.py**

```python
"""Live running dashboard."""
import customtkinter as ctk
from autovision.gui.styles import (
    styled_frame, styled_label, styled_button,
    BG_PANEL, BG_CARD, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    ACCENT_RED, ACCENT_GREEN, ACCENT_YELLOW, ACCENT_BLUE,
)
from autovision.engine.script_runner import ScriptState

STATE_COLORS = {
    ScriptState.RUNNING: ACCENT_GREEN,
    ScriptState.PAUSED: ACCENT_YELLOW,
    ScriptState.STOPPED: ACCENT_RED,
    ScriptState.ERROR: ACCENT_RED,
    ScriptState.IDLE: TEXT_MUTED,
}


class Dashboard(ctk.CTkToplevel):
    def __init__(self, parent, app_controller=None):
        super().__init__(parent)
        self._app = app_controller
        self.title("Live Dashboard")
        self.geometry("500x400")
        self.configure(fg_color=BG_PANEL)
        self._cards_frame = None
        self._perf_frame = None
        self._build()

    def _build(self):
        styled_label(self, "LIVE DASHBOARD", size=11, color=TEXT_SECONDARY).pack(pady=(10, 4))

        self._cards_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._cards_frame.pack(fill="both", expand=True, padx=10, pady=4)

        self._perf_frame = ctk.CTkFrame(self, fg_color=BG_CARD, height=60)
        self._perf_frame.pack(fill="x", padx=10, pady=(4, 10))
        self._perf_label = styled_label(self._perf_frame, "No scripts running",
                                        size=10, color=TEXT_MUTED)
        self._perf_label.pack(padx=10, pady=10)

    def refresh(self):
        for w in self._cards_frame.winfo_children():
            w.destroy()

        rt = self._app.get_runtime() if self._app else None
        if rt is None:
            self._perf_label.configure(text="No scripts running")
            return

        runners = rt.get_all_runners()
        running = sum(1 for r in runners if r.state == ScriptState.RUNNING)
        self._perf_label.configure(
            text=f"Scripts: {running}/{len(runners)} | Threads: {len(runners)}/8"
        )

        for runner in runners:
            color = STATE_COLORS.get(runner.state, TEXT_MUTED)
            card = ctk.CTkFrame(self._cards_frame, fg_color=BG_CARD, corner_radius=6)
            card.pack(fill="x", padx=2, pady=2)

            styled_label(card, f"{runner.script.name}",
                         size=11, color=color).pack(anchor="w", padx=8, pady=(6, 1))
            styled_label(
                card,
                f"State: {runner.state.value} | Matches: {runner._match_count} | "
                f"Runtime: {runner.runtime_seconds():.0f}s",
                size=9, color=TEXT_SECONDARY,
            ).pack(anchor="w", padx=8, pady=(0, 6))
```

- [ ] **Step 2: Write wizard.py**

```python
"""Quick-start wizard for beginners."""
import customtkinter as ctk
from autovision.gui.styles import (
    styled_frame, styled_label, styled_button,
    BG_PANEL, BG_CARD, TEXT_PRIMARY, TEXT_SECONDARY,
    ACCENT_GREEN, ACCENT_BLUE,
)
from autovision.model.script import Script, ScriptNode


class Wizard(ctk.CTkToplevel):
    def __init__(self, parent, app_controller=None):
        super().__init__(parent)
        self._app = app_controller
        self.title("Quick Start Wizard")
        self.geometry("450x350")
        self.configure(fg_color=BG_PANEL)
        self._step = 0
        self._answers = {}
        self._build()

    def _build(self):
        self._content = ctk.CTkFrame(self, fg_color="transparent")
        self._content.pack(fill="both", expand=True, padx=20, pady=20)
        self._show_step()

    def _show_step(self):
        for w in self._content.winfo_children():
            w.destroy()

        if self._step == 0:
            styled_label(self._content, "Step 1: Which image should trigger this script?",
                         size=13, color=TEXT_PRIMARY).pack(pady=(0, 8))
            styled_label(self._content, "Select a template image from your project, or create one first.",
                         size=10, color=TEXT_SECONDARY).pack(pady=(0, 12))

            if self._app and self._app.project and self._app.project_dir:
                templates = self._app.project.list_templates(self._app.project_dir)
                if templates:
                    self._template_var = ctk.StringVar(value=templates[0])
                    for t in templates:
                        ctk.CTkRadioButton(
                            self._content, text=t, variable=self._template_var, value=t,
                        ).pack(anchor="w", padx=10, pady=2)
                else:
                    styled_label(self._content, "No templates found. Add one from the Template Library.",
                                 size=10, color=TEXT_SECONDARY).pack()
            else:
                styled_label(self._content, "Open or create a project first.", size=10,
                             color=TEXT_SECONDARY).pack()

        elif self._step == 1:
            styled_label(self._content, "Step 2: What should happen?",
                         size=13, color=TEXT_PRIMARY).pack(pady=(0, 8))

            self._action_var = ctk.StringVar(value="click")
            for val, label in [
                ("click", "🖱  Click the image center"),
                ("key", "⌨  Press a keyboard key"),
                ("click_coord", "🎯  Click a fixed coordinate"),
            ]:
                ctk.CTkRadioButton(
                    self._content, text=label, variable=self._action_var, value=val,
                ).pack(anchor="w", padx=10, pady=4)

            if self._action_var.get() == "key":
                self._key_entry = ctk.CTkEntry(
                    self._content, placeholder_text="Key name (e.g., f1, enter)...",
                    font=("Segoe UI", 10), height=28,
                )
                self._key_entry.pack(fill="x", padx=10, pady=(8, 0))

        elif self._step == 2:
            styled_label(self._content, "Step 3: How often should it check?",
                         size=13, color=TEXT_PRIMARY).pack(pady=(0, 8))

            self._loop_var = ctk.StringVar(value="always")
            ctk.CTkRadioButton(self._content, text="Keep checking (loop while visible)",
                               variable=self._loop_var, value="always").pack(anchor="w", padx=10, pady=4)
            ctk.CTkRadioButton(self._content, text="Just once (fire and stop)",
                               variable=self._loop_var, value="once").pack(anchor="w", padx=10, pady=4)

            styled_label(self._content, "Check interval (ms):",
                         size=10, color=TEXT_SECONDARY).pack(anchor="w", padx=10, pady=(12, 2))
            self._interval_entry = ctk.CTkEntry(
                self._content, font=("Segoe UI", 10), height=28,
            )
            self._interval_entry.insert(0, "500")
            self._interval_entry.pack(fill="x", padx=10)

        # Navigation
        nav = ctk.CTkFrame(self._content, fg_color="transparent")
        nav.pack(side="bottom", fill="x", pady=(16, 0))

        if self._step > 0:
            styled_button(nav, "Back", color="#30363d",
                          command=self._prev).pack(side="left")
        if self._step < 2:
            styled_button(nav, "Next", color=ACCENT_BLUE,
                          command=self._next).pack(side="right")
        else:
            styled_button(nav, "Generate Script", color=ACCENT_GREEN,
                          command=self._finish).pack(side="right")

    def _next(self):
        self._step += 1
        self._show_step()

    def _prev(self):
        self._step -= 1
        self._show_step()

    def _finish(self):
        name = f"Wizard Script {len(self._app.project.scripts) + 1}" if self._app and self._app.project else "Wizard Script"
        root = ScriptNode(type="trigger", subtype="image_found",
                          config={"template": getattr(self, "_template_var", ctk.StringVar(value="")).get(),
                                  "confidence": 0.85})

        action_type = getattr(self, "_action_var", ctk.StringVar(value="click")).get()
        if action_type == "click":
            root.add_child(ScriptNode(type="action", subtype="click_center"))
        elif action_type == "key":
            key = getattr(self, "_key_entry", None)
            key_val = key.get() if key else "f1"
            root.add_child(ScriptNode(type="action", subtype="press_key",
                                      config={"key": key_val}))
        elif action_type == "click_coord":
            root.add_child(ScriptNode(type="action", subtype="click_coord",
                                      config={"x": 0, "y": 0}))

        loop_mode = getattr(self, "_loop_var", ctk.StringVar(value="always")).get()
        if loop_mode == "always":
            loop = ScriptNode(type="loop", subtype="while_visible",
                              config={"template": root.config.get("template", ""),
                                      "delay_ms": 100})
            loop.add_child(ScriptNode(type="action", subtype="wait",
                                      config={"duration_ms": 500}))
            root.add_child(loop)

        tick = int(getattr(self, "_interval_entry", None).get() if hasattr(self, "_interval_entry") else "500")
        script = Script(name=name, root=root, tick_ms=tick)
        self._app.project.add_script(script)
        self.destroy()
```

- [ ] **Step 3: Wire together in main_window.py — add toolbar buttons**

Modify `autovision/gui/main_window.py` `_create_shell` method — add toolbar buttons after the toolbar pack:

```python
    def add_toolbar_buttons(self):
        from autovision.gui.styles import styled_button, FONT_FAMILY, ACCENT_GREEN, ACCENT_RED, ACCENT_BLUE, ACCENT_YELLOW

        self._run_btn = styled_button(
            self.toolbar, "▶ Run", color=ACCENT_GREEN,
            width=60, height=26, font=(FONT_FAMILY, 10),
            command=self._menu("start_all"),
        )
        self._run_btn.pack(side="left", padx=2)

        self._stop_btn = styled_button(
            self.toolbar, "⏹ Stop", color=ACCENT_RED,
            width=60, height=26, font=(FONT_FAMILY, 10),
            command=self._menu("stop_all"),
        )
        self._stop_btn.pack(side="left", padx=2)

        self._pause_btn = styled_button(
            self.toolbar, "⏸ Pause", color=ACCENT_YELLOW,
            width=60, height=26, font=(FONT_FAMILY, 10),
            command=self._menu("toggle_pause"),
        )
        self._pause_btn.pack(side="left", padx=2)

        ctk.CTkFrame(self.toolbar, fg_color="#30363d", width=1, height=20).pack(
            side="left", padx=6)

        styled_button(
            self.toolbar, "📸 Capture", color="#30363d",
            width=70, height=26, font=(FONT_FAMILY, 10),
            command=self._menu("capture_template"),
        ).pack(side="left", padx=2)

        styled_button(
            self.toolbar, "📍 Pick", color="#30363d",
            width=60, height=26, font=(FONT_FAMILY, 10),
            command=self._menu("pick_coordinate"),
        ).pack(side="left", padx=2)

        styled_button(
            self.toolbar, "🧙 Wizard", color=ACCENT_BLUE,
            width=70, height=26, font=(FONT_FAMILY, 10),
            command=self._menu("wizard"),
        ).pack(side="left", padx=2)
```

- [ ] **Step 4: Update app.py to use project_dir for save and handle all menu actions**

```python
"""Application controller - wires engines and GUI together."""
from autovision.engine.capture import Capture
from autovision.engine.matcher import Matcher
from autovision.engine.runtime import Runtime, RuntimeState
from autovision.model.project import Project
from autovision.gui.template_capture import TemplateCapture
from autovision.gui.coordinate_picker import CoordinatePicker
from autovision.gui.template_library import TemplateLibrary
from autovision.gui.wizard import Wizard
from autovision.gui.dashboard import Dashboard
import os


class AppController:
    def __init__(self):
        self.capture = Capture()
        self.matcher = Matcher()
        self.project: Project | None = None
        self.project_dir: str | None = None
        self.runtime: Runtime | None = None
        self._window = None
        self._last_picked_coord = None

    def set_window(self, window):
        self._window = window
        window.after(100, self._on_window_ready)

    def _on_window_ready(self):
        if self._window:
            self._window.add_toolbar_buttons()

    def new_project(self, name: str, directory: str):
        self.project = Project(name=name)
        self.project_dir = directory
        os.makedirs(directory, exist_ok=True)
        os.makedirs(os.path.join(directory, "images"), exist_ok=True)
        os.makedirs(os.path.join(directory, "scripts"), exist_ok=True)
        os.makedirs(os.path.join(directory, "logs"), exist_ok=True)

    def load_project(self, directory: str):
        self.project = Project.load(directory)
        self.project_dir = directory

    def save_project(self):
        if self.project and self.project_dir:
            self.project.save(self.project_dir)

    def start_all(self):
        if self.project:
            self.runtime = Runtime(self.project, self.capture, self.matcher)
            self.runtime.start_all()
            self._open_dashboard()

    def stop_all(self):
        if self.runtime:
            self.runtime.stop_all()
            self.runtime = None

    def toggle_pause(self):
        if self.runtime:
            self.runtime.toggle_pause()

    def emergency_stop(self):
        if self.runtime:
            self.runtime.emergency_stop()
            self.runtime = None

    def get_runtime(self):
        return self.runtime

    def _open_dashboard(self):
        if self._window:
            Dashboard(self._window, app_controller=self)

    def open_template_library(self):
        if self._window:
            lib = TemplateLibrary(self._window, app_controller=self)
            lib.refresh()

    def open_wizard(self):
        if self._window and self.project:
            Wizard(self._window, app_controller=self)

    def start_template_capture(self):
        tc = TemplateCapture(self)
        tc.start_capture()

    def start_coordinate_picker(self):
        def on_coord(x, y, rgb):
            self._last_picked_coord = (x, y, rgb)
        cp = CoordinatePicker(on_coord)
        cp.start()

    def handle_menu(self, action: str):
        handlers = {
            "start_all": self.start_all,
            "stop_all": self.stop_all,
            "toggle_pause": self.toggle_pause,
            "capture_template": self.start_template_capture,
            "template_library": self.open_template_library,
            "pick_coordinate": self.start_coordinate_picker,
            "wizard": self.open_wizard,
            "new_project": self._handle_new_project,
            "open_project": self._handle_open_project,
            "save_project": self.save_project,
        }
        handler = handlers.get(action)
        if handler:
            handler()

    def _handle_new_project(self):
        from tkinter import filedialog, simpledialog
        name = simpledialog.askstring("New Project", "Project name:", parent=self._window)
        if name:
            directory = filedialog.askdirectory(title="Select project folder", parent=self._window)
            if directory:
                proj_dir = os.path.join(directory, name)
                self.new_project(name, proj_dir)
                self.save_project()

    def _handle_open_project(self):
        from tkinter import filedialog
        directory = filedialog.askdirectory(title="Open project folder", parent=self._window)
        if directory:
            try:
                self.load_project(directory)
            except FileNotFoundError:
                from tkinter import messagebox
                messagebox.showerror("Error", f"No project.json found in {directory}")

    def shutdown(self):
        self.emergency_stop()
```

- [ ] **Step 5: Update main.py entry point**

```python
"""Entry point for AutoVision."""
import sys
from autovision.gui.main_window import MainWindow
from autovision.app import AppController


def main():
    app = AppController()
    window = MainWindow(app_controller=app)
    app.set_window(window)
    window.mainloop()


if __name__ == "__main__":
    main()
```

- [ ] **Step 6: Commit**

```bash
git add autovision/gui/dashboard.py autovision/gui/wizard.py autovision/gui/main_window.py autovision/app.py autovision/main.py
git commit -m "feat: add dashboard, wizard, and full GUI integration"
```

---

## Polish

### Task 21: Starter templates

**Files:**
- Create: `autovision/resources/starter_templates/auto_click.json`
- Create: `autovision/resources/starter_templates/heal_check.json`

- [ ] **Step 1: Write auto_click.json**

```json
{
  "name": "Auto Click (Example)",
  "enabled": true,
  "hotkey": "",
  "window_title": "",
  "window_method": "partial",
  "tick_ms": 500,
  "root": {
    "type": "trigger",
    "subtype": "image_found",
    "config": {
      "template": "your_button.png",
      "confidence": 0.85
    },
    "children": [
      {
        "type": "action",
        "subtype": "click_center",
        "config": {
          "button": "left",
          "offset_x": 0,
          "offset_y": 0
        }
      },
      {
        "type": "loop",
        "subtype": "while_visible",
        "config": {
          "template": "your_button.png",
          "max_iterations": 0,
          "delay_ms": 100
        },
        "children": [
          {
            "type": "action",
            "subtype": "wait",
            "config": {
              "duration_ms": 500
            }
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 2: Write heal_check.json**

```json
{
  "name": "Heal Check (Example)",
  "enabled": true,
  "hotkey": "",
  "window_title": "",
  "window_method": "partial",
  "tick_ms": 2000,
  "root": {
    "type": "trigger",
    "subtype": "image_found",
    "config": {
      "template": "low_hp.png",
      "confidence": 0.8
    },
    "children": [
      {
        "type": "action",
        "subtype": "press_key",
        "config": {
          "key": "f1"
        }
      },
      {
        "type": "action",
        "subtype": "wait",
        "config": {
          "duration_ms": 1500
        }
      }
    ]
  }
}
```

- [ ] **Step 3: Commit**

```bash
git add autovision/resources/starter_templates/ && git commit -m "feat: add starter template scripts"
```

---

## Verification

Verification checklist (manual, since GUI and capture tools require a desktop):

1. `python -m pytest autovision/tests/ -v` — all unit tests pass
2. `python -m autovision.main` — GUI launches with dark theme, all panels visible
3. Create a new project → project.json and folders created
4. Capture a template image from screen → saved to project/images/
5. Use coordinate picker (Space to capture) → coordinates displayed
6. Create a script via wizard (3 questions) → script appears in tree
7. Add modules from palette to script tree → tree updates, properties editable
8. Run script → dashboard shows status, event log populates
9. Global hotkeys work (Ctrl+Shift+F5/F6/F7/F8)
10. Emergency stop kills all threads and releases hooks

