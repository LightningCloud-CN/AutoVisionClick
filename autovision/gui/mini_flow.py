"""Mini flowchart preview panel."""
import customtkinter as ctk
from autovision.gui.styles import (
    styled_label, BG_CARD, TEXT_SECONDARY, CATEGORY_COLORS, FONT_FAMILY,
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
            styled_label(self, "未选择模块", size=9,
                         color=TEXT_SECONDARY).pack(pady=20)
            return

        styled_label(self, "流程预览", size=9, color=TEXT_SECONDARY).pack(
            anchor="w", padx=6, pady=(6, 4))
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
