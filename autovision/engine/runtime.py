"""Multi-script runtime manager."""
from __future__ import annotations
from enum import Enum
from autovision.model.project import Project
from autovision.model.script import Script
from autovision.engine.script_runner import ScriptRunner, ScriptState
from autovision.engine.hotkeys import HotkeyManager
from autovision.config import MAX_CONCURRENT_SCRIPTS


class RuntimeState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"


class Runtime:
    def __init__(self, project: Project, capture_service, matcher_service):
        self.project = project
        self._capture = capture_service
        self._matcher = matcher_service
        self._runners: dict[str, ScriptRunner] = {}
        self.state = RuntimeState.IDLE
        self.hotkeys = HotkeyManager()
        self._setup_hotkeys()

    def _setup_hotkeys(self):
        hk = self.project.global_hotkeys
        if hk.get("start_all"):
            self.hotkeys.register(hk["start_all"], self.start_all)
        if hk.get("stop_all"):
            self.hotkeys.register(hk["stop_all"], self.stop_all)
        if hk.get("pause"):
            self.hotkeys.register(hk["pause"], self.toggle_pause)
        if hk.get("emergency"):
            self.hotkeys.register(hk["emergency"], self.emergency_stop)

    def start_all(self):
        self.hotkeys.start()
        enabled = [s for s in self.project.scripts if s.enabled]
        for i, script in enumerate(enabled):
            if i >= MAX_CONCURRENT_SCRIPTS:
                break
            runner = ScriptRunner(script, self._capture, self._matcher)
            self._runners[script.name] = runner
            runner.start()
        self.state = RuntimeState.RUNNING

    def stop_all(self):
        for runner in self._runners.values():
            runner.stop()
        self._runners.clear()
        self.hotkeys.stop()
        self.state = RuntimeState.STOPPED

    def pause_all(self):
        for runner in self._runners.values():
            runner.pause()
        self.state = RuntimeState.PAUSED

    def resume_all(self):
        for runner in self._runners.values():
            runner.resume()
        self.state = RuntimeState.RUNNING

    def toggle_pause(self):
        if self.state == RuntimeState.RUNNING:
            self.pause_all()
        elif self.state == RuntimeState.PAUSED:
            self.resume_all()

    def emergency_stop(self):
        for runner in self._runners.values():
            runner.stop()
        self._runners.clear()
        self.hotkeys.stop()
        self.state = RuntimeState.STOPPED

    def get_runner(self, name: str) -> ScriptRunner | None:
        return self._runners.get(name)

    def get_all_runners(self) -> list[ScriptRunner]:
        return list(self._runners.values())

    def start_single(self, name: str):
        script = self.project.get_script(name)
        if script is None or name in self._runners:
            return
        runner = ScriptRunner(script, self._capture, self._matcher)
        self._runners[name] = runner
        runner.start()

    def stop_single(self, name: str):
        runner = self._runners.pop(name, None)
        if runner:
            runner.stop()
