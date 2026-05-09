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
        for key, default in schema.items():
            val = self.config.get(key, default)
            if val == "" or val is None:
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
