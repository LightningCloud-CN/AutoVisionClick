"""Coordinate picker - click on screen to capture coordinates."""
import tkinter as tk
import mss


class CoordinatePicker:
    def __init__(self, callback):
        self._callback = callback
        self._result = None

    def start(self):
        self._overlay = tk.Toplevel()
        self._overlay.attributes("-fullscreen", True)
        self._overlay.attributes("-alpha", 0.15)
        self._overlay.attributes("-topmost", True)
        self._overlay.configure(bg="black", cursor="crosshair")

        self._overlay.bind("<KeyPress-space>", self._on_capture)
        self._overlay.bind("<Escape>", lambda e: self._overlay.destroy())
        self._overlay.bind("<Button-1>", self._on_capture)

        self._info = tk.Label(
            self._overlay,
            text="按空格键或点击鼠标捕获坐标 | 按ESC取消",
            bg="#161b22", fg="#00ccff",
            font=("Microsoft YaHei", 10), padx=10, pady=4,
        )
        self._info.place(relx=0.5, rely=0.02, anchor="n")
        self._overlay.focus_force()
        self._overlay.lift()

    def _on_capture(self, event):
        if hasattr(event, 'x'):
            x, y = event.x_root, event.y_root
        else:
            x, y = 0, 0
        try:
            sct = mss.MSS()
            monitor = {"left": x, "top": y, "width": 1, "height": 1}
            img = sct.grab(monitor)
            r, g, b = img.pixel(0, 0)
        except Exception:
            r, g, b = 0, 0, 0

        self._overlay.destroy()
        if self._callback:
            self._callback(x, y, (r, g, b))
