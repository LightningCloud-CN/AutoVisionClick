"""Tests for action executor."""
import numpy as np
from autovision.engine.action_executor import ActionExecutor
from autovision.model.script import ScriptNode
from autovision.model.variable_store import VariableStore
from autovision.engine.matcher import MatchResult

def test_execute_wait():
    node = ScriptNode(type="action", subtype="wait", config={"duration_ms": 10})
    store = VariableStore()
    executor = ActionExecutor()
    import time
    start = time.time()
    executor.execute(node, store)
    elapsed = time.time() - start
    assert elapsed >= 0.01

def test_execute_set_var():
    node = ScriptNode(type="action", subtype="set_var",
                      config={"name": "flag", "value": "hello"})
    store = VariableStore()
    executor = ActionExecutor()
    executor.execute(node, store)
    assert store.get("flag") == "hello"

def test_execute_with_match_context():
    match = MatchResult(x=100, y=200, width=30, height=40, confidence=0.95)
    node = ScriptNode(type="action", subtype="click_center",
                      config={"button": "left", "offset_x": 0, "offset_y": 0})
    store = VariableStore()
    executor = ActionExecutor(match_context=match)
    executor.execute(node, store)
    assert store.get("$match_x") == 100
    assert store.get("$match_y") == 200

def test_evaluate_condition_if_variable():
    node = ScriptNode(type="condition", subtype="if_variable",
                      config={"variable": "hp", "operator": "lt", "value": "50"})
    store = VariableStore()
    store.set("hp", 30)
    executor = ActionExecutor()
    assert executor.evaluate_condition(node, store) is True
    store.set("hp", 80)
    assert executor.evaluate_condition(node, store) is False
