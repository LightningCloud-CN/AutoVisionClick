"""Tests for the script node model."""
import json
from autovision.model.script import ScriptNode, Script


def test_create_leaf_node():
    node = ScriptNode(type="action", subtype="click_center",
                      config={"button": "left", "offset_x": 0, "offset_y": 0})
    assert node.type == "action"
    assert node.subtype == "click_center"
    assert node.children == []


def test_add_child_and_parent_link():
    parent = ScriptNode(type="trigger", subtype="image_found")
    child = ScriptNode(type="action", subtype="click_center")
    parent.add_child(child)
    assert len(parent.children) == 1
    assert child.parent is parent


def test_to_dict_and_from_dict_deep():
    root = ScriptNode(type="trigger", subtype="image_found",
                      config={"template": "btn.png", "confidence": 0.85})
    root.add_child(ScriptNode(type="action", subtype="click_center"))
    loop = ScriptNode(type="loop", subtype="while_visible",
                      config={"template": "btn.png"})
    loop.add_child(ScriptNode(type="action", subtype="wait",
                              config={"duration_ms": 500}))
    root.add_child(loop)

    d = root.to_dict()
    restored = ScriptNode.from_dict(d)

    assert restored.subtype == "image_found"
    assert len(restored.children) == 2
    assert restored.children[1].subtype == "while_visible"
    assert len(restored.children[1].children) == 1


def test_script_wrapper():
    script = Script(
        name="Auto Heal",
        enabled=True,
        hotkey="<ctrl>+<shift>+1",
        window_title="Game",
        tick_ms=500,
        root=ScriptNode(type="trigger", subtype="image_found",
                        config={"template": "low_hp.png"})
    )
    d = script.to_dict()
    restored = Script.from_dict(d)
    assert restored.name == "Auto Heal"
    assert restored.root.subtype == "image_found"


def test_validate_errors():
    root = ScriptNode(type="trigger", subtype="image_found", config={})
    errors = root.validate()
    assert len(errors) > 0

    valid = ScriptNode(type="trigger", subtype="image_found",
                       config={"template": "btn.png", "confidence": 0.85})
    assert valid.validate() == []
