"""Live running dashboard."""
import customtkinter as ctk
from autovision.gui.styles import (
    styled_label, BG_PANEL, BG_CARD, FONT_FAMILY,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    ACCENT_RED, ACCENT_GREEN, ACCENT_YELLOW, ACCENT_BLUE,
)
from autovision.engine.script_runner import ScriptState

STATE_COLORS = {
    ScriptState.RUNNING: ACCENT_GREEN,
    ScriptState.PAUSED: ACCENT_YELLOW,
    ScriptState.STOPPED: ACCENT_RED,
    ScriptState.ERROR: ACCENT_RED,
    ScriptState.IDLE: TEXT_MUTED,
}


class Dashboard(ctk.CTkToplevel):
    def __init__(self, parent, app_controller=None):
        super().__init__(parent)
        self._app = app_controller
        self.title("Live Dashboard")
        self.geometry("500x400")
        self.configure(fg_color=BG_PANEL)
        self._cards_frame = None
        self._build()

    def _build(self):
        styled_label(self, "LIVE DASHBOARD", size=11, color=TEXT_SECONDARY).pack(pady=(10, 4))

        self._cards_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._cards_frame.pack(fill="both", expand=True, padx=10, pady=4)

        self._perf_frame = ctk.CTkFrame(self, fg_color=BG_CARD, height=60)
        self._perf_frame.pack(fill="x", padx=10, pady=(4, 10))
        self._perf_label = styled_label(self._perf_frame, "No scripts running",
                                        size=10, color=TEXT_MUTED)
        self._perf_label.pack(padx=10, pady=10)

    def refresh(self):
        for w in self._cards_frame.winfo_children():
            w.destroy()

        rt = self._app.get_runtime() if self._app else None
        if rt is None:
            self._perf_label.configure(text="No scripts running")
            return

        runners = rt.get_all_runners()
        running = sum(1 for r in runners if r.state == ScriptState.RUNNING)
        self._perf_label.configure(
            text=f"Scripts: {running}/{len(runners)} | Threads: {len(runners)}/8"
        )

        for runner in runners:
            color = STATE_COLORS.get(runner.state, TEXT_MUTED)
            card = ctk.CTkFrame(self._cards_frame, fg_color=BG_CARD, corner_radius=6)
            card.pack(fill="x", padx=2, pady=2)

            styled_label(card, f"{runner.script.name}",
                         size=11, color=color).pack(anchor="w", padx=8, pady=(6, 1))
            styled_label(
                card,
                f"State: {runner.state.value} | Matches: {runner._match_count} | "
                f"Runtime: {runner.runtime_seconds():.0f}s",
                size=9, color=TEXT_SECONDARY,
            ).pack(anchor="w", padx=8, pady=(0, 6))
