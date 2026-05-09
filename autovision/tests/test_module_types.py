"""Tests for module type definitions."""
import pytest
from autovision.model.module_types import ModuleCategory, MODULE_REGISTRY, ModuleDef


def test_module_categories():
    assert ModuleCategory.TRIGGER.value == "trigger"
    assert ModuleCategory.ACTION.value == "action"
    assert ModuleCategory.CONDITION.value == "condition"
    assert ModuleCategory.LOOP.value == "loop"
    assert ModuleCategory.GROUP.value == "group"


def test_registry_has_all_categories():
    cats = {m.category for m in MODULE_REGISTRY}
    assert ModuleCategory.TRIGGER in cats
    assert ModuleCategory.ACTION in cats
    assert ModuleCategory.CONDITION in cats
    assert ModuleCategory.LOOP in cats
    assert ModuleCategory.GROUP in cats


def test_every_module_has_required_fields():
    for mod in MODULE_REGISTRY:
        assert mod.subtype, f"{mod} missing subtype"
        assert mod.label, f"{mod} missing label"
        assert mod.category in ModuleCategory


def test_get_by_subtype():
    m = ModuleDef.get("image_found")
    assert m is not None
    assert m.category == ModuleCategory.TRIGGER
    assert ModuleDef.get("nonexistent") is None


def test_get_by_category():
    triggers = ModuleDef.get_by_category(ModuleCategory.TRIGGER)
    assert len(triggers) >= 3
    assert all(m.category == ModuleCategory.TRIGGER for m in triggers)
