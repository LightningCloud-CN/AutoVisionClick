"""Left sidebar: script list panel."""
import customtkinter as ctk
from autovision.gui.styles import (
    styled_label, styled_button, BG_CARD, FONT_FAMILY,
    ACCENT_RED, ACCENT_GREEN,
    TEXT_PRIMARY, TEXT_SECONDARY,
)


class ScriptListPanel(ctk.CTkScrollableFrame):
    def __init__(self, parent, app_controller=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self._app = app_controller
        self._on_select = None
        self._on_add = None
        self._build_ui()

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=6, pady=(6, 4))
        styled_label(header, "SCRIPTS", size=10, color=TEXT_SECONDARY).pack(side="left")
        styled_button(
            header, "+ New", color=ACCENT_GREEN,
            width=50, height=22, font=(FONT_FAMILY, 10),
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
