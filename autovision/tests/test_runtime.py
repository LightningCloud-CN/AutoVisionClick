"""Tests for runtime manager."""
import time
import numpy as np
from autovision.engine.runtime import Runtime, RuntimeState
from autovision.model.project import Project
from autovision.model.script import Script, ScriptNode


class FakeCapture:
    def window(self, title, method):
        return np.zeros((100, 100, 3), dtype=np.uint8)
    def full_screen(self):
        return np.zeros((100, 100, 3), dtype=np.uint8)
    def list_windows(self):
        return ["Test Window"]


class FakeMatcher:
    def find(self, template, scene, confidence, method=None):
        return []
    def find_multiple(self, templates, scene, confidence):
        return {}


def test_runtime_start_stop():
    proj = Project(name="Test")
    root = ScriptNode(type="trigger", subtype="script_start")
    root.add_child(ScriptNode(type="action", subtype="set_var",
                              config={"name": "x", "value": 42}))
    proj.add_script(Script(name="TestScript", root=root, tick_ms=50))

    rt = Runtime(proj, FakeCapture(), FakeMatcher())
    assert rt.state == RuntimeState.IDLE

    rt.start_all()
    assert rt.state == RuntimeState.RUNNING
    time.sleep(0.2)
    runner = rt.get_runner("TestScript")
    assert runner is not None
    assert runner.store.get("x") == 42
    rt.stop_all()
    assert rt.state == RuntimeState.STOPPED


def test_runtime_pause_resume():
    proj = Project(name="Test")
    proj.add_script(Script(name="S", root=ScriptNode(
        type="trigger", subtype="script_start"), tick_ms=50))

    rt = Runtime(proj, FakeCapture(), FakeMatcher())
    rt.start_all()
    time.sleep(0.05)
    rt.pause_all()
    assert rt.state == RuntimeState.PAUSED
    rt.resume_all()
    assert rt.state == RuntimeState.RUNNING
    rt.stop_all()


def test_runtime_emergency_stop():
    proj = Project(name="Test")
    proj.add_script(Script(name="S", root=ScriptNode(
        type="trigger", subtype="script_start"), tick_ms=50))

    rt = Runtime(proj, FakeCapture(), FakeMatcher())
    rt.start_all()
    time.sleep(0.05)
    rt.emergency_stop()
    assert rt.state == RuntimeState.STOPPED
