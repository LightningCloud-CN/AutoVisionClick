"""Screen capture using mss and window enumeration."""
from __future__ import annotations
import ctypes
from ctypes import wintypes
import numpy as np
import mss
import cv2

user32 = ctypes.windll.user32


class Capture:
    def __init__(self):
        self._sct = mss.MSS()

    def full_screen(self) -> np.ndarray:
        monitor = self._sct.monitors[1]
        img = np.array(self._sct.grab(monitor))
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    def region(self, left: int, top: int, width: int, height: int) -> np.ndarray:
        monitor = {"left": left, "top": top, "width": width, "height": height}
        img = np.array(self._sct.grab(monitor))
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    def window(self, title: str, method: str = "partial") -> np.ndarray | None:
        hwnd = self._find_window(title, method)
        if hwnd == 0:
            return None

        rect = wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        if rect.left == rect.right or rect.top == rect.bottom:
            return None

        return self.region(
            rect.left, rect.top,
            rect.right - rect.left,
            rect.bottom - rect.top,
        )

    def _find_window(self, title: str, method: str) -> int:
        windows = self._enum_visible_windows()
        if method == "exact":
            for hwnd, wtitle in windows:
                if wtitle == title:
                    return hwnd
        elif method == "regex":
            import re
            for hwnd, wtitle in windows:
                if re.search(title, wtitle):
                    return hwnd
        else:
            title_lower = title.lower()
            for hwnd, wtitle in windows:
                if title_lower in wtitle.lower():
                    return hwnd
        return 0

    def list_windows(self) -> list[str]:
        return sorted(wtitle for _, wtitle in self._enum_visible_windows())

    @staticmethod
    def _enum_visible_windows() -> list[tuple[int, str]]:
        results = []

        def enum_callback(hwnd, _):
            if user32.IsWindowVisible(hwnd):
                text = ctypes.create_unicode_buffer(260)
                user32.GetWindowTextW(hwnd, text, 260)
                if text.value:
                    results.append((hwnd, text.value))
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        user32.EnumWindows(WNDENUMPROC(enum_callback), 0)
        return results
