"""Application controller — wires engines and web API together."""
import os
from autovision.engine.capture import Capture
from autovision.engine.matcher import Matcher
from autovision.engine.runtime import Runtime
from autovision.model.project import Project
from autovision.model.module_types import MODULE_REGISTRY, ModuleDef, ModuleCategory


class AppController:
    def __init__(self):
        self.capture = Capture()
        self.matcher = Matcher()
        self.project: Project | None = None
        self.project_dir: str | None = None
        self.runtime: Runtime | None = None
        self._last_picked_coord = None

    # ── project ──────────────────────────────────────────────

    def new_project(self, name: str, directory: str):
        self.project = Project(name=name)
        self.project_dir = directory
        os.makedirs(directory, exist_ok=True)
        os.makedirs(os.path.join(directory, "images"), exist_ok=True)
        os.makedirs(os.path.join(directory, "scripts"), exist_ok=True)
        os.makedirs(os.path.join(directory, "logs"), exist_ok=True)

    def load_project(self, directory: str):
        self.project = Project.load(directory)
        self.project_dir = directory

    def save_project(self):
        if self.project and self.project_dir:
            self.project.save(self.project_dir)

    def get_project_state(self) -> dict | None:
        if not self.project:
            return None
        return {
            'name': self.project.name,
            'window_title': self.project.window_title,
            'window_method': self.project.window_method,
            'scripts': [s.to_dict() for s in self.project.scripts],
            'templates': self.list_templates(),
            'project_dir': self.project_dir,
        }

    # ── runtime ──────────────────────────────────────────────

    def start_all(self):
        if self.project:
            self.runtime = Runtime(self.project, self.capture, self.matcher)
            self.runtime.start_all()

    def stop_all(self):
        if self.runtime:
            self.runtime.stop_all()
            self.runtime = None

    def toggle_pause(self):
        if self.runtime:
            self.runtime.toggle_pause()

    def emergency_stop(self):
        if self.runtime:
            self.runtime.emergency_stop()
            self.runtime = None

    def get_runtime(self):
        return self.runtime

    def start_single(self, name: str):
        if self.runtime:
            self.runtime.start_single(name)

    def stop_single(self, name: str):
        if self.runtime:
            self.runtime.stop_single(name)

    # ── scripts ──────────────────────────────────────────────

    def create_script(self, name: str):
        from autovision.model.script import Script
        script = Script(name=name)
        self.project.add_script(script)

    def delete_script(self, name: str):
        self.project.remove_script(name)

    def get_script(self, name: str):
        return self.project.get_script(name)

    def get_script_names(self) -> list[str]:
        if not self.project:
            return []
        return [s.name for s in self.project.scripts]

    # ── templates ────────────────────────────────────────────

    def list_templates(self) -> list[str]:
        if not self.project or not self.project_dir:
            return []
        return self.project.list_templates(self.project_dir)

    def delete_template(self, name: str):
        if self.project_dir:
            path = os.path.join(self.project_dir, "images", name)
            if os.path.exists(path):
                os.remove(path)

    def import_template(self, file_path: str, name: str | None = None):
        import shutil
        if not self.project_dir:
            return
        img_dir = os.path.join(self.project_dir, "images")
        os.makedirs(img_dir, exist_ok=True)
        dest_name = name if name else os.path.basename(file_path)
        shutil.copy(file_path, os.path.join(img_dir, dest_name))

    def template_path(self, name: str) -> str | None:
        if not self.project_dir:
            return None
        path = os.path.join(self.project_dir, "images", name)
        if os.path.exists(path):
            return path
        return None

    # ── modules ──────────────────────────────────────────────

    def get_module_registry(self) -> list[dict]:
        return [
            {
                'subtype': m.subtype,
                'category': m.category.value,
                'label': m.label,
                'icon': m.icon,
                'description': m.description,
                'config_schema': m.config_schema,
            }
            for m in MODULE_REGISTRY
        ]

    # ── tools ────────────────────────────────────────────────

    def list_windows(self) -> list[str]:
        return self.capture.list_windows()

    def start_template_capture(self, on_saved=None):
        from autovision.gui.template_capture import TemplateCapture
        self._capture_on_saved = on_saved
        tc = TemplateCapture(self, on_saved=on_saved)
        tc.start_capture()

    def start_coordinate_picker(self, on_picked=None):
        from autovision.gui.coordinate_picker import CoordinatePicker
        cp = CoordinatePicker(on_picked)
        cp.start()

    # ── wizard ───────────────────────────────────────────────

    def wizard_generate(self, data: dict) -> str:
        from autovision.model.script import Script, ScriptNode
        name = data.get('name', f'向导脚本 {len(self.project.scripts) + 1}')
        template = data.get('template', '')
        action_type = data.get('action_type', 'click')
        action_config = data.get('action_config', {})
        loop_mode = data.get('loop_mode', 'always')
        tick_ms = int(data.get('tick_ms', 500))

        root = ScriptNode(
            type='trigger', subtype='image_found',
            config={'template': template, 'confidence': 0.85})

        if action_type == 'click':
            root.add_child(ScriptNode(type='action', subtype='click_center'))
        elif action_type == 'key':
            root.add_child(ScriptNode(type='action', subtype='press_key',
                                       config=action_config))
        elif action_type == 'click_coord':
            root.add_child(ScriptNode(type='action', subtype='click_coord',
                                       config=action_config))

        if loop_mode == 'always':
            loop = ScriptNode(type='loop', subtype='while_visible',
                              config={'template': template, 'delay_ms': 100})
            loop.add_child(ScriptNode(type='action', subtype='wait',
                                       config={'duration_ms': 500}))
            root.add_child(loop)

        script = Script(name=name, root=root, tick_ms=tick_ms)
        self.project.add_script(script)
        return name

    # ── shutdown ─────────────────────────────────────────────

    def shutdown(self):
        self.emergency_stop()
