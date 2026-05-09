"""Tests for script runner."""
import time
import numpy as np
from autovision.engine.script_runner import ScriptRunner, ScriptState
from autovision.model.script import Script, ScriptNode
from autovision.model.variable_store import VariableStore


class FakeCapture:
    def __init__(self, img=None):
        self.img = img if img is not None else np.zeros((100, 100, 3), dtype=np.uint8)
    def window(self, title, method):
        return self.img.copy()
    def full_screen(self):
        return self.img.copy()

class FakeMatcher:
    def find(self, template, scene, confidence, method=None):
        return []
    def find_multiple(self, templates, scene, confidence):
        return {}

def test_script_runner_lifecycle():
    root = ScriptNode(type="trigger", subtype="script_start")
    root.add_child(ScriptNode(type="action", subtype="set_var",
                              config={"name": "x", "value": 1}))
    script = Script(name="Test", root=root, tick_ms=50)
    runner = ScriptRunner(script, FakeCapture(), FakeMatcher())
    assert runner.state == ScriptState.IDLE

    runner.start()
    time.sleep(0.2)
    assert runner.store.get("x") == 1
    runner.stop()
    assert runner.state == ScriptState.STOPPED

def test_pause_resume():
    root = ScriptNode(type="trigger", subtype="script_start")
    script = Script(name="PauseTest", root=root, tick_ms=50)
    runner = ScriptRunner(script, FakeCapture(), FakeMatcher())
    runner.start()
    time.sleep(0.05)
    runner.pause()
    assert runner.state == ScriptState.PAUSED
    runner.resume()
    assert runner.state == ScriptState.RUNNING
    runner.stop()
