"""Main application window."""
import customtkinter as ctk
from autovision.gui.styles import apply_theme, BG_DARK
from autovision.config import APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT


class MainWindow(ctk.CTk):
    def __init__(self, app_controller=None):
        super().__init__()
        apply_theme()
        self._app = app_controller

        self.title(f"{APP_NAME}")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.configure(fg_color=BG_DARK)
        self.minsize(900, 600)

        self.grid_columnconfigure(0, weight=0, minsize=200)
        self.grid_columnconfigure(1, weight=3)
        self.grid_columnconfigure(2, weight=1, minsize=220)
        self.grid_rowconfigure(0, weight=3)
        self.grid_rowconfigure(1, weight=1, minsize=120)

        self.left_frame = None
        self.center_frame = None
        self.right_frame = None
        self.bottom_frame = None

        self._create_shell()
        self._create_menu()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _create_shell(self):
        from autovision.gui.styles import styled_frame, styled_label, BG_PANEL

        self.left_frame = styled_frame(self)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(4, 2), pady=4)

        self.center_frame = styled_frame(self)
        self.center_frame.grid(row=0, column=1, sticky="nsew", padx=2, pady=4)

        self.right_frame = styled_frame(self)
        self.right_frame.grid(row=0, column=2, sticky="nsew", padx=(2, 4), pady=4)

        self.bottom_frame = styled_frame(self)
        self.bottom_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=4, pady=(2, 4))

        self.toolbar = ctk.CTkFrame(self.center_frame, fg_color="transparent", height=36)
        self.toolbar.pack(fill="x", padx=6, pady=(6, 2))

    def add_toolbar_buttons(self):
        from autovision.gui.styles import styled_button, FONT_FAMILY
        from autovision.gui.styles import ACCENT_GREEN, ACCENT_RED, ACCENT_BLUE, ACCENT_YELLOW

        styled_button(
            self.toolbar, "Run", color=ACCENT_GREEN,
            width=60, height=26, font=(FONT_FAMILY, 10),
            command=self._menu("start_all"),
        ).pack(side="left", padx=2)

        styled_button(
            self.toolbar, "Stop", color=ACCENT_RED,
            width=60, height=26, font=(FONT_FAMILY, 10),
            command=self._menu("stop_all"),
        ).pack(side="left", padx=2)

        styled_button(
            self.toolbar, "Pause", color=ACCENT_YELLOW,
            width=60, height=26, font=(FONT_FAMILY, 10),
            command=self._menu("toggle_pause"),
        ).pack(side="left", padx=2)

        ctk.CTkFrame(self.toolbar, fg_color="#30363d", width=1, height=20).pack(
            side="left", padx=6)

        styled_button(
            self.toolbar, "Capture", color="#30363d",
            width=70, height=26, font=(FONT_FAMILY, 10),
            command=self._menu("capture_template"),
        ).pack(side="left", padx=2)

        styled_button(
            self.toolbar, "Pick", color="#30363d",
            width=60, height=26, font=(FONT_FAMILY, 10),
            command=self._menu("pick_coordinate"),
        ).pack(side="left", padx=2)

        styled_button(
            self.toolbar, "Wizard", color=ACCENT_BLUE,
            width=70, height=26, font=(FONT_FAMILY, 10),
            command=self._menu("wizard"),
        ).pack(side="left", padx=2)

    def _create_menu(self):
        from tkinter import Menu
        menubar = Menu(self, bg="#161b22", fg="#e6edf3", activebackground="#1f2937",
                       activeforeground="#00ccff")
        file_menu = Menu(menubar, tearoff=0, bg="#161b22", fg="#e6edf3")
        file_menu.add_command(label="New Project", command=self._menu("new_project"))
        file_menu.add_command(label="Open Project", command=self._menu("open_project"))
        file_menu.add_command(label="Save Project", command=self._menu("save_project"))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_close)
        menubar.add_cascade(label="File", menu=file_menu)

        run_menu = Menu(menubar, tearoff=0, bg="#161b22", fg="#e6edf3")
        run_menu.add_command(label="Start All", command=self._menu("start_all"))
        run_menu.add_command(label="Stop All", command=self._menu("stop_all"))
        run_menu.add_command(label="Pause/Resume", command=self._menu("toggle_pause"))
        menubar.add_cascade(label="Run", menu=run_menu)

        tools_menu = Menu(menubar, tearoff=0, bg="#161b22", fg="#e6edf3")
        tools_menu.add_command(label="Capture Template", command=self._menu("capture_template"))
        tools_menu.add_command(label="Template Library", command=self._menu("template_library"))
        tools_menu.add_command(label="Pick Coordinate", command=self._menu("pick_coordinate"))
        tools_menu.add_command(label="Quick Start Wizard", command=self._menu("wizard"))
        menubar.add_cascade(label="Tools", menu=tools_menu)

        self.config(menu=menubar)

    def _menu(self, action: str):
        def handler():
            if self._app:
                self._app.handle_menu(action)
        return handler

    def _on_close(self):
        if self._app:
            self._app.shutdown()
        self.destroy()
