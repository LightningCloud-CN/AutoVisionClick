"""Per-script match-loop thread."""
from __future__ import annotations
import time
import threading
import cv2
import numpy as np
from enum import Enum
from autovision.model.script import Script, ScriptNode
from autovision.model.variable_store import VariableStore
from autovision.engine.action_executor import ActionExecutor


class ScriptState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


class ScriptRunner:
    def __init__(self, script: Script, capture_service, matcher_service):
        self.script = script
        self._capture = capture_service
        self._matcher = matcher_service
        self.store = VariableStore()
        self.state = ScriptState.IDLE
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._pause_event.set()
        self._match_count = 0
        self._last_match_time: float | None = None
        self._start_time: float | None = None
        self._error: str | None = None
        self.log: list[tuple[float, str, str]] = []

    def start(self):
        if self.state == ScriptState.RUNNING:
            return
        self._stop_event.clear()
        self._pause_event.set()
        self.state = ScriptState.RUNNING
        self._start_time = time.time()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        self._pause_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3)
        self.state = ScriptState.STOPPED

    def pause(self):
        self._pause_event.clear()
        self.state = ScriptState.PAUSED

    def resume(self):
        self._pause_event.set()
        self.state = ScriptState.RUNNING

    def runtime_seconds(self) -> float:
        if self._start_time is None:
            return 0
        return time.time() - self._start_time

    def _loop(self):
        try:
            while not self._stop_event.is_set():
                self._pause_event.wait()
                self._tick()
                time.sleep(self.script.tick_ms / 1000.0)
        except Exception as e:
            self.state = ScriptState.ERROR
            self._error = str(e)
            self._log("ERROR", f"Script crashed: {e}")

    def _tick(self):
        if self.script.root is None:
            return
        scene = None
        if self.script.window_title:
            scene = self._capture.window(self.script.window_title,
                                         self.script.window_method)
        if scene is None:
            scene = self._capture.full_screen()
        self._process_node(self.script.root, scene)

    def _process_node(self, node: ScriptNode, scene):
        if node.type == "trigger":
            self._handle_trigger(node, scene)
        elif node.type == "action":
            executor = ActionExecutor()
            executor.execute(node, self.store)
        elif node.type == "condition":
            executor = ActionExecutor(capture_service=self._capture,
                                      matcher_service=self._matcher)
            if executor.evaluate_condition(node, self.store):
                for child in node.children:
                    self._process_node(child, scene)
        elif node.type == "loop":
            self._handle_loop(node, scene)

    def _handle_trigger(self, node: ScriptNode, scene):
        subtype = node.subtype
        if subtype == "script_start":
            if self._match_count == 0:
                for child in node.children:
                    self._process_node(child, scene)
            return
        if subtype == "image_found":
            template = self._load_template(node.config.get("template", ""))
            if template is not None:
                matches = self._matcher.find(
                    template, scene,
                    confidence=node.config.get("confidence", 0.85),
                )
                for match in matches:
                    self._match_count += 1
                    self._last_match_time = time.time()
                    self._log("INFO",
                              f"Match: {node.config['template']} at ({match.x},{match.y}) "
                              f"conf={match.confidence:.2f}")
                    executor = ActionExecutor(match_context=match)
                    for child in node.children:
                        executor.execute(child, self.store)
        elif subtype == "timer":
            for child in node.children:
                self._process_node(child, scene)

    def _handle_loop(self, node: ScriptNode, scene):
        subtype = node.subtype
        max_iter = int(node.config.get("max_iterations", 0)) or 999999
        count = 0
        while count < max_iter and not self._stop_event.is_set():
            self._pause_event.wait()
            if subtype == "while_visible":
                template = self._load_template(node.config.get("template", ""))
                if template is not None:
                    matches = self._matcher.find(
                        template, scene,
                        confidence=node.config.get("confidence", 0.85),
                    )
                    if not matches:
                        break
            for child in node.children:
                self._process_node(child, scene)
            count += 1
            self.store.set_loop_count(count)
            delay = int(node.config.get("delay_ms", 100)) / 1000.0
            if delay > 0:
                time.sleep(delay)

    def _load_template(self, name: str) -> np.ndarray | None:
        if not name:
            return None
        try:
            import os
            if os.path.exists(name):
                return cv2.imread(name)
        except Exception:
            pass
        return None

    def _log(self, level: str, message: str):
        self.log.append((time.time(), level, message))
        if len(self.log) > 1000:
            self.log = self.log[-500:]
