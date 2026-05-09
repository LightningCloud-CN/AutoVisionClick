"""Screen region capture tool for creating templates."""
import os
import cv2
import numpy as np
import customtkinter as ctk
import tkinter as tk
from autovision.gui.styles import (
    styled_label, styled_button, BG_PANEL, FONT_FAMILY,
    TEXT_SECONDARY, ACCENT_GREEN,
)


class TemplateCapture:
    def __init__(self, app_controller):
        self._app = app_controller
        self._start = None
        self._rect = None

    def start_capture(self):
        self._overlay = tk.Toplevel()
        self._overlay.attributes("-fullscreen", True)
        self._overlay.attributes("-alpha", 0.3)
        self._overlay.attributes("-topmost", True)
        self._overlay.configure(bg="black")

        self._canvas = tk.Canvas(self._overlay, bg="black", highlightthickness=0)
        self._canvas.pack(fill="both", expand=True)

        self._canvas.bind("<ButtonPress-1>", self._on_press)
        self._canvas.bind("<B1-Motion>", self._on_drag)
        self._canvas.bind("<ButtonRelease-1>", self._on_release)
        self._overlay.bind("<Escape>", lambda e: self._overlay.destroy())
        self._overlay.focus_force()

    def _on_press(self, event):
        self._start = (event.x, event.y)
        if self._rect:
            self._canvas.delete(self._rect)
        self._rect = None

    def _on_drag(self, event):
        if self._start:
            if self._rect:
                self._canvas.delete(self._rect)
            self._rect = self._canvas.create_rectangle(
                self._start[0], self._start[1], event.x, event.y,
                outline="#00ff99", width=2, dash=(4, 2),
            )

    def _on_release(self, event):
        if self._start is None:
            return
        x1, y1 = self._start
        x2, y2 = event.x, event.y
        if abs(x2 - x1) < 5 or abs(y2 - y1) < 5:
            self._overlay.destroy()
            return

        left, right = sorted([x1, x2])
        top, bottom = sorted([y1, y2])
        self._overlay.destroy()

        img = self._app.capture.region(left, top, right - left, bottom - top)
        self._save_template(img, left, top, right, bottom)

    def _save_template(self, img: np.ndarray, left, top, right, bottom):
        dialog = ctk.CTkToplevel()
        dialog.title("保存模板")
        dialog.geometry("350x250")
        dialog.configure(fg_color=BG_PANEL)

        styled_label(dialog, "保存模板", size=11, color=TEXT_SECONDARY).pack(pady=(10, 4))
        styled_label(dialog, f"区域大小: {right-left}x{bottom-top}",
                     size=9, color=TEXT_SECONDARY).pack()

        entry = ctk.CTkEntry(dialog, placeholder_text="输入模板名称...",
                             font=(FONT_FAMILY, 11), height=30)
        entry.pack(fill="x", padx=20, pady=(10, 4))
        entry.focus()

        def save():
            name = entry.get().strip()
            if not name:
                return
            if not self._app.project_dir:
                from tkinter import messagebox
                messagebox.showwarning("提示", "请先创建或打开一个项目。")
                dialog.destroy()
                return
            img_dir = os.path.join(self._app.project_dir, "images")
            os.makedirs(img_dir, exist_ok=True)
            path = os.path.join(img_dir, f"{name}.png")
            cv2.imwrite(path, img)
            dialog.destroy()

        styled_button(dialog, "保存", color=ACCENT_GREEN, command=save).pack(pady=(8, 4))
        dialog.bind("<Return>", lambda e: save())
