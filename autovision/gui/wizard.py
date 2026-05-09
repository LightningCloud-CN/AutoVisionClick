"""Quick-start wizard for beginners."""
import customtkinter as ctk
from autovision.gui.styles import (
    styled_label, styled_button, BG_PANEL, FONT_FAMILY,
    TEXT_PRIMARY, TEXT_SECONDARY, ACCENT_GREEN, ACCENT_BLUE,
)
from autovision.model.script import Script, ScriptNode


class Wizard(ctk.CTkToplevel):
    def __init__(self, parent, app_controller=None):
        super().__init__(parent)
        self._app = app_controller
        self.title("快速向导")
        self.geometry("450x380")
        self.configure(fg_color=BG_PANEL)
        self._step = 0
        self._template_var = ctk.StringVar(value="")
        self._action_var = ctk.StringVar(value="click")
        self._loop_var = ctk.StringVar(value="always")
        self._build()

    def _build(self):
        self._content = ctk.CTkFrame(self, fg_color="transparent")
        self._content.pack(fill="both", expand=True, padx=20, pady=20)
        self._show_step()

    def _show_step(self):
        for w in self._content.winfo_children():
            w.destroy()

        if self._step == 0:
            styled_label(self._content, "第一步：选择触发图像",
                         size=14, color=TEXT_PRIMARY).pack(pady=(0, 8))
            styled_label(self._content,
                         "选择一个项目中的模板图像作为触发条件。",
                         size=10, color=TEXT_SECONDARY).pack(pady=(0, 12))

            if self._app and self._app.project and self._app.project_dir:
                templates = self._app.project.list_templates(self._app.project_dir)
                if templates:
                    self._template_var = ctk.StringVar(value=templates[0])
                    for t in templates:
                        ctk.CTkRadioButton(
                            self._content, text=t,
                            variable=self._template_var, value=t,
                        ).pack(anchor="w", padx=10, pady=2)
                else:
                    styled_label(self._content,
                                 "暂无模板，请先在模板库中添加。",
                                 size=10, color=TEXT_SECONDARY).pack()
            else:
                styled_label(self._content, "请先创建或打开一个项目。",
                             size=10, color=TEXT_SECONDARY).pack()

        elif self._step == 1:
            styled_label(self._content, "第二步：选择执行动作",
                         size=14, color=TEXT_PRIMARY).pack(pady=(0, 8))

            self._action_var = ctk.StringVar(value="click")
            for val, label in [
                ("click", "🖱  点击图像中心"),
                ("key", "⌨  按下键盘按键"),
                ("click_coord", "🎯  点击固定坐标"),
            ]:
                ctk.CTkRadioButton(
                    self._content, text=label,
                    variable=self._action_var, value=val,
                ).pack(anchor="w", padx=10, pady=4)

            self._key_entry = ctk.CTkEntry(
                self._content, placeholder_text="按键名称 (例如: f1, enter)...",
                font=(FONT_FAMILY, 10), height=28,
            )
            self._key_entry.pack(fill="x", padx=10, pady=(8, 0))

        elif self._step == 2:
            styled_label(self._content, "第三步：设置运行方式",
                         size=14, color=TEXT_PRIMARY).pack(pady=(0, 8))

            self._loop_var = ctk.StringVar(value="always")
            ctk.CTkRadioButton(self._content,
                               text="持续检测（图像可见时循环执行）",
                               variable=self._loop_var,
                               value="always").pack(anchor="w", padx=10, pady=4)
            ctk.CTkRadioButton(self._content,
                               text="仅执行一次",
                               variable=self._loop_var,
                               value="once").pack(anchor="w", padx=10, pady=4)

            styled_label(self._content, "检测间隔 (毫秒):",
                         size=10, color=TEXT_SECONDARY).pack(
                anchor="w", padx=10, pady=(12, 2))
            self._interval_entry = ctk.CTkEntry(
                self._content, font=(FONT_FAMILY, 10), height=28,
            )
            self._interval_entry.insert(0, "500")
            self._interval_entry.pack(fill="x", padx=10)

        nav = ctk.CTkFrame(self._content, fg_color="transparent")
        nav.pack(side="bottom", fill="x", pady=(16, 0))

        if self._step > 0:
            styled_button(nav, "上一步", color="#30363d",
                          command=self._prev).pack(side="left")
        if self._step < 2:
            styled_button(nav, "下一步", color=ACCENT_BLUE,
                          command=self._next).pack(side="right")
        else:
            styled_button(nav, "生成脚本", color=ACCENT_GREEN,
                          command=self._finish).pack(side="right")

    def _next(self):
        self._step += 1
        self._show_step()

    def _prev(self):
        self._step -= 1
        self._show_step()

    def _finish(self):
        if not self._app or not self._app.project:
            self.destroy()
            return

        name = f"向导脚本 {len(self._app.project.scripts) + 1}"
        root = ScriptNode(
            type="trigger", subtype="image_found",
            config={"template": self._template_var.get(), "confidence": 0.85})

        action_type = self._action_var.get()
        if action_type == "click":
            root.add_child(ScriptNode(type="action", subtype="click_center"))
        elif action_type == "key":
            key_val = self._key_entry.get() if hasattr(self, '_key_entry') else "f1"
            root.add_child(ScriptNode(type="action", subtype="press_key",
                                      config={"key": key_val}))
        elif action_type == "click_coord":
            root.add_child(ScriptNode(type="action", subtype="click_coord",
                                      config={"x": 0, "y": 0}))

        if self._loop_var.get() == "always":
            loop = ScriptNode(type="loop", subtype="while_visible",
                              config={"template": root.config.get("template", ""),
                                      "delay_ms": 100})
            loop.add_child(ScriptNode(type="action", subtype="wait",
                                      config={"duration_ms": 500}))
            root.add_child(loop)

        tick = int(self._interval_entry.get()) if hasattr(self, '_interval_entry') else 500
        script = Script(name=name, root=root, tick_ms=tick)
        self._app.project.add_script(script)
        self.destroy()
