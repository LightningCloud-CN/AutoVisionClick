"""Right panel: properties editor for selected module."""
import customtkinter as ctk
from autovision.gui.styles import (
    styled_label, styled_button, BG_INPUT, FONT_FAMILY,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, ACCENT_GREEN,
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
                row, fg_color=BG_INPUT, border_color="#30363d",
                font=(FONT_FAMILY, 10), height=28,
            )
            entry.pack(fill="x", pady=(1, 4))
            current = node.config.get(key, default)
            entry.insert(0, str(current))
            entry.bind("<FocusOut>", lambda e, k=key, ent=entry: self._save(k, ent.get()))
            entry.bind("<Return>", lambda e, k=key, ent=entry: self._save(k, ent.get()))
            self._inputs[key] = entry

        if node.subtype == "click_coord":
            styled_button(
                self._content, "Pick Coordinates", color=ACCENT_GREEN,
                height=28, font=(FONT_FAMILY, 10),
                command=self._on_pick,
            ).pack(fill="x", pady=(8, 0))

    def _on_pick(self):
        if self._on_pick_coord:
            self._on_pick_coord()

    def _save(self, key: str, value: str):
        if self._node is None:
            return
        mod_def = ModuleDef.get(self._node.subtype)
        if mod_def:
            default = mod_def.config_schema.get(key)
            if isinstance(default, (int, float)):
                try:
                    value = type(default)(value)
                except ValueError:
                    value = default
            self._node.config[key] = value
        if self._on_modified:
            self._on_modified()
