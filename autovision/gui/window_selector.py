"""Window selection dialog."""
import customtkinter as ctk
from autovision.gui.styles import (
    styled_label, styled_button, BG_PANEL, BG_INPUT, FONT_FAMILY,
    TEXT_SECONDARY, ACCENT_GREEN,
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
            self._manual_frame, fg_color=BG_INPUT,
            placeholder_text="Enter window title...",
            font=(FONT_FAMILY, 10), height=30,
        )
        self._manual_entry.pack(fill="x", padx=10, pady=4)

        self._method_var = ctk.StringVar(value="partial")
        for text, val in [("Partial match", "partial"),
                          ("Exact match", "exact"),
                          ("Regex", "regex")]:
            ctk.CTkRadioButton(
                self._manual_frame, text=text, variable=self._method_var, value=val,
            ).pack(anchor="w", padx=20, pady=1)

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
                ctk.CTkButton(
                    self._list_frame, text=w[:60],
                    fg_color="transparent", hover_color="#1f2937",
                    font=(FONT_FAMILY, 10), anchor="w",
                    command=lambda title=w: self._select_from_list(title),
                ).pack(fill="x", pady=0)

    def _select_from_list(self, title: str):
        self._manual_entry.delete(0, "end")
        self._manual_entry.insert(0, title)
        self._method.set("manual")

    def _on_select(self):
        title = self._manual_entry.get().strip()
        if title:
            self.result = (title, self._method_var.get())
        self.destroy()
