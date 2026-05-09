"""Bottom panel: event log viewer."""
import customtkinter as ctk
from autovision.gui.styles import (
    styled_label, styled_button, BG_CARD, FONT_FAMILY,
    TEXT_SECONDARY, ACCENT_GREEN, ACCENT_YELLOW, ACCENT_RED, ACCENT_BLUE,
)

LEVEL_COLORS = {
    "INFO": ACCENT_GREEN,
    "WARN": ACCENT_YELLOW,
    "ERROR": ACCENT_RED,
    "DEBUG": ACCENT_BLUE,
}


class EventLog(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self._entries: list[tuple[str, str, str]] = []
        self._build()

    def _build(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=6, pady=(6, 2))

        styled_label(header, "事件日志", size=10, color=TEXT_SECONDARY).pack(side="left")
        styled_button(
            header, "清空", color="#30363d",
            width=50, height=20, font=(FONT_FAMILY, 9),
            command=self.clear,
        ).pack(side="right")

        self._log_frame = ctk.CTkScrollableFrame(self, fg_color=BG_CARD, height=100)
        self._log_frame.pack(fill="both", expand=True, padx=6, pady=(2, 6))

    def add(self, level: str, message: str):
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self._entries.append((timestamp, level, message))
        if len(self._entries) > 500:
            self._entries = self._entries[-250:]
        self._append_line(timestamp, level, message)

    def _append_line(self, timestamp: str, level: str, message: str):
        color = LEVEL_COLORS.get(level, TEXT_SECONDARY)
        line = f"[{timestamp}] {level:5s} {message}"
        lbl = styled_label(self._log_frame, line, size=9, color=color)
        lbl.pack(anchor="w", padx=4, pady=0)
        self._log_frame._parent_canvas.yview_moveto(1.0)

    def add_from_runner(self, runner_log: list):
        from datetime import datetime
        for ts, level, msg in runner_log:
            timestamp = datetime.fromtimestamp(ts).strftime("%H:%M:%S")
            if (timestamp, level, msg) not in self._entries:
                self._entries.append((timestamp, level, msg))
                self._append_line(timestamp, level, msg)

    def clear(self):
        self._entries.clear()
        for w in self._log_frame.winfo_children():
            w.destroy()
