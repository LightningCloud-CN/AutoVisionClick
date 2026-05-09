"""Tests for input simulator (unit tests - no actual input)."""
from autovision.engine.input_sim import InputSim, key_name_to_vk

def test_key_name_to_vk_common():
    assert key_name_to_vk("enter") == 0x0D
    assert key_name_to_vk("space") == 0x20
    assert key_name_to_vk("a") == 0x41
    assert key_name_to_vk("f1") == 0x70

def test_key_name_to_vk_unknown():
    assert key_name_to_vk("zzzz") == 0

def test_input_sim_has_methods():
    sim = InputSim()
    assert hasattr(sim, "click")
    assert hasattr(sim, "press_key")
    assert hasattr(sim, "type_text")
    assert hasattr(sim, "scroll")
    assert hasattr(sim, "move_to")
