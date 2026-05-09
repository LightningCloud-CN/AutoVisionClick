"""Screen region capture tool for creating templates."""
import os
import cv2
import numpy as np
import tkinter as tk
from tkinter import simpledialog, messagebox


class TemplateCapture:
    def __init__(self, app_controller, on_saved=None, on_cancelled=None):
        self._app = app_controller
        self._start = None
        self._rect = None
        self._on_saved = on_saved
        self._on_cancelled = on_cancelled
        self._overlay = None
        self._root = None

    def start_capture(self, root=None):
        self._root = root or tk.Tk()
        if not root:
            self._root.withdraw()

        self._overlay = tk.Toplevel(self._root)
        self._overlay.attributes("-fullscreen", True)
        self._overlay.attributes("-alpha", 0.3)
        self._overlay.attributes("-topmost", True)
        self._overlay.configure(bg="black")

        self._canvas = tk.Canvas(self._overlay, bg="black", highlightthickness=0)
        self._canvas.pack(fill="both", expand=True)

        self._canvas.bind("<ButtonPress-1>", self._on_press)
        self._canvas.bind("<B1-Motion>", self._on_drag)
        self._canvas.bind("<ButtonRelease-1>", self._on_release)
        self._overlay.bind("<Escape>", lambda e: self._cancel())
        self._overlay.protocol("WM_DELETE_WINDOW", self._cancel)
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
            return

        left, right = sorted([x1, x2])
        top, bottom = sorted([y1, y2])
        self._overlay.destroy()
        self._overlay = None

        img = self._app.capture.region(left, top, right - left, bottom - top)
        self._save_template(img, right - left, bottom - top)

    def _cancel(self):
        if self._overlay:
            self._overlay.destroy()
            self._overlay = None
        if self._on_cancelled:
            self._on_cancelled()

    def _save_template(self, img: np.ndarray, width: int, height: int):
        name = simpledialog.askstring(
            "保存模板",
            f"区域大小: {width}x{height}\n\n输入模板名称:",
            parent=self._root,
        )
        if not name:
            if self._on_cancelled:
                self._on_cancelled()
            return

        if not self._app.project_dir:
            messagebox.showwarning("提示", "请先创建或打开一个项目。", parent=self._root)
            if self._on_cancelled:
                self._on_cancelled()
            return

        img_dir = os.path.join(self._app.project_dir, "images")
        os.makedirs(img_dir, exist_ok=True)
        path = os.path.join(img_dir, f"{name}.png")
        cv2.imwrite(path, img)

        if self._on_saved:
            self._on_saved(name, width, height, path)
