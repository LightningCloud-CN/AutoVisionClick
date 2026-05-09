"""Tests for project model."""
from autovision.model.project import Project
from autovision.model.script import Script, ScriptNode


def _dummy_script(name="Dummy Script"):
    root = ScriptNode(type="trigger", subtype="image_found",
                      config={"template": "btn.png", "confidence": 0.85})
    root.add_child(ScriptNode(type="action", subtype="click_center"))
    return Script(name=name, root=root)


def test_create_project():
    proj = Project(name="Test Project")
    assert proj.name == "Test Project"
    assert proj.scripts == []
    assert proj.global_hotkeys["start_all"] != ""


def test_add_remove_script():
    proj = Project(name="Test")
    proj.add_script(_dummy_script())
    assert len(proj.scripts) == 1
    proj.remove_script("Dummy Script")
    assert len(proj.scripts) == 0


def test_save_and_load(tmp_path):
    img_dir = tmp_path / "images"
    img_dir.mkdir()
    (tmp_path / "scripts").mkdir()
    (tmp_path / "logs").mkdir()

    proj = Project(name="Test", window_title="MyGame")
    proj.add_script(_dummy_script())
    proj.save(str(tmp_path))

    assert (tmp_path / "project.json").exists()
    loaded = Project.load(str(tmp_path))
    assert loaded.name == "Test"
    assert loaded.window_title == "MyGame"
    assert len(loaded.scripts) == 1


def test_list_templates(tmp_path):
    (tmp_path / "images").mkdir(parents=True)
    (tmp_path / "scripts").mkdir()
    (tmp_path / "logs").mkdir()
    (tmp_path / "images" / "a.png").touch()

    proj = Project(name="T")
    proj.save(str(tmp_path))
    templates = proj.list_templates(str(tmp_path))
    assert len(templates) == 1
    assert "a.png" in templates[0]
