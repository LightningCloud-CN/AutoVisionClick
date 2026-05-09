"""Template library management panel."""
import os
import customtkinter as ctk
from autovision.gui.styles import (
    styled_label, styled_button, BG_PANEL, BG_CARD, FONT_FAMILY,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, ACCENT_GREEN, ACCENT_RED,
)


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
            width=70, height=24, font=(FONT_FAMILY, 10),
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

        styled_label(card, f"🖼 {name}", size=10, color=TEXT_PRIMARY).pack(
            side="left", padx=8, pady=6)

        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="right", padx=4)
        styled_button(
            info_frame, "Del", color=ACCENT_RED,
            width=35, height=22, font=(FONT_FAMILY, 9),
            command=lambda n=name: self._delete(n),
        ).pack(side="right", padx=2)
        styled_button(
            info_frame, "Use", color=ACCENT_GREEN,
            width=35, height=22, font=(FONT_FAMILY, 9),
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
