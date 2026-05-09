"""Module palette - drag source for available modules."""
import customtkinter as ctk
from autovision.gui.styles import (
    BG_CARD, FONT_FAMILY, TEXT_SECONDARY, CATEGORY_COLORS,
)
from autovision.model.module_types import ModuleCategory, MODULE_REGISTRY, ModuleDef


class ModulePalette(ctk.CTkScrollableFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", label_text="模块面板",
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
            text=category.display_name,
            text_color=color,
            font=(FONT_FAMILY, 9, "bold"),
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
            font=(FONT_FAMILY, 10),
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
