"""Tests for variable store."""
from autovision.model.variable_store import VariableStore

def test_set_and_get():
    store = VariableStore()
    store.set("count", 5)
    assert store.get("count") == 5
    assert store.get("nonexistent") is None
    assert store.get("nonexistent", default=0) == 0

def test_match_variables():
    store = VariableStore()
    store.set_match(845, 420)
    assert store.get("$match_x") == 845
    assert store.get("$match_y") == 420

def test_increment_and_delete():
    store = VariableStore()
    store.set("count", 0)
    assert store.inc("count") == 1
    store.delete("count")
    assert not store.exists("count")

def test_list_all():
    store = VariableStore()
    store.set("a", 1)
    store.set_match(10, 20)
    names = {v["name"] for v in store.list_all()}
    assert "a" in names
    assert "$match_x" in names
