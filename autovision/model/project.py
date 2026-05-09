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
