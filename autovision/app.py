"""Application controller - wires engines and GUI together."""
import os
from autovision.engine.capture import Capture
from autovision.engine.matcher import Matcher
from autovision.engine.runtime import Runtime, RuntimeState
from autovision.model.project import Project


class AppController:
    def __init__(self):
        self.capture = Capture()
        self.matcher = Matcher()
        self.project: Project | None = None
        self.project_dir: str | None = None
        self.runtime: Runtime | None = None
        self._window = None
        self._last_picked_coord = None

    def set_window(self, window):
        self._window = window
        window.after(100, self._on_window_ready)

    def _on_window_ready(self):
        if self._window:
            self._window.add_toolbar_buttons()

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

    def start_all(self):
        if self.project:
            self.runtime = Runtime(self.project, self.capture, self.matcher)
            self.runtime.start_all()
            self._open_dashboard()

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

    def _open_dashboard(self):
        if self._window:
            from autovision.gui.dashboard import Dashboard
            Dashboard(self._window, app_controller=self)

    def open_template_library(self):
        if self._window:
            from autovision.gui.template_library import TemplateLibrary
            lib = TemplateLibrary(self._window, app_controller=self)
            lib.refresh()

    def open_wizard(self):
        if self._window and self.project:
            from autovision.gui.wizard import Wizard
            Wizard(self._window, app_controller=self)

    def start_template_capture(self):
        from autovision.gui.template_capture import TemplateCapture
        tc = TemplateCapture(self)
        tc.start_capture()

    def start_coordinate_picker(self):
        from autovision.gui.coordinate_picker import CoordinatePicker
        def on_coord(x, y, rgb):
            self._last_picked_coord = (x, y, rgb)
        cp = CoordinatePicker(on_coord)
        cp.start()

    def handle_menu(self, action: str):
        handlers = {
            "start_all": self.start_all,
            "stop_all": self.stop_all,
            "toggle_pause": self.toggle_pause,
            "capture_template": self.start_template_capture,
            "template_library": self.open_template_library,
            "pick_coordinate": self.start_coordinate_picker,
            "wizard": self.open_wizard,
            "new_project": self._handle_new_project,
            "open_project": self._handle_open_project,
            "save_project": self.save_project,
        }
        handler = handlers.get(action)
        if handler:
            handler()

    def _handle_new_project(self):
        from tkinter import filedialog, simpledialog
        name = simpledialog.askstring("新建项目", "请输入项目名称:", parent=self._window)
        if name:
            directory = filedialog.askdirectory(title="选择项目保存位置", parent=self._window)
            if directory:
                proj_dir = os.path.join(directory, name)
                self.new_project(name, proj_dir)
                self.save_project()

    def _handle_open_project(self):
        from tkinter import filedialog
        directory = filedialog.askdirectory(title="打开项目文件夹", parent=self._window)
        if directory:
            try:
                self.load_project(directory)
            except FileNotFoundError:
                from tkinter import messagebox
                messagebox.showerror("错误", f"在 {directory} 中未找到 project.json")

    def shutdown(self):
        self.emergency_stop()
