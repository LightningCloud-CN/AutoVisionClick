"""Center panel: script tree editor."""
import customtkinter as ctk
from autovision.gui.styles import (
    styled_label, FONT_FAMILY, TEXT_PRIMARY, TEXT_SECONDARY, CATEGORY_COLORS,
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
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=6, pady=(6, 2))
        styled_label(header, "脚本编辑器", size=10, color=TEXT_SECONDARY).pack(side="left")

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
        cfg = {k: v for k, v in mod.config_schema.items()}
        node = ScriptNode(type=mod.category.value, subtype=mod.subtype, config=cfg)
        if parent is None:
            self._script.root = node
        else:
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
                arr = node.parent.children
                arr[idx], arr[idx - 1] = arr[idx - 1], arr[idx]
                self._refresh_tree()

    def move_down(self):
        node = self._selected_node
        if node and node.parent:
            idx = node.parent.children.index(node)
            if idx < len(node.parent.children) - 1:
                arr = node.parent.children
                arr[idx], arr[idx + 1] = arr[idx + 1], arr[idx]
                self._refresh_tree()

    def _refresh_tree(self):
        for w in self._tree_frame.winfo_children():
            w.destroy()
        if self._script and self._script.root:
            self._render_node(self._script.root, depth=0)

    def _render_node(self, node: ScriptNode, depth: int):
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
            summary = ", ".join(
                f"{k}={v}" for k, v in list(node.config.items())[:2])
            text += f"  -  {summary}"

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
