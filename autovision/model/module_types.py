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
