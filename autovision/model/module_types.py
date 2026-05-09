"""Module type definitions - the palette of available script building blocks."""
from enum import Enum
from dataclasses import dataclass, field


class ModuleCategory(Enum):
    TRIGGER = "trigger"
    ACTION = "action"
    CONDITION = "condition"
    LOOP = "loop"
    GROUP = "group"

    @property
    def display_name(self) -> str:
        names = {
            "trigger": "触发器",
            "action": "动作",
            "condition": "条件",
            "loop": "循环",
            "group": "分组",
        }
        return names.get(self.value, self.value)


@dataclass(frozen=True)
class ModuleDef:
    subtype: str
    category: ModuleCategory
    label: str
    icon: str = ""
    description: str = ""
    config_schema: dict = field(default_factory=dict)

    @classmethod
    def get(cls, subtype: str):
        for m in MODULE_REGISTRY:
            if m.subtype == subtype:
                return m
        return None

    @classmethod
    def get_by_category(cls, category: ModuleCategory) -> list:
        return [m for m in MODULE_REGISTRY if m.category == category]


MODULE_REGISTRY = [
    # 触发器
    ModuleDef("image_found", ModuleCategory.TRIGGER, "图像出现", "🔍",
              "当屏幕上发现指定模板图像时触发",
              {"template": "", "confidence": 0.85, "region": "full"}),
    ModuleDef("image_lost", ModuleCategory.TRIGGER, "图像消失", "👁",
              "当之前可见的模板图像从屏幕消失时触发",
              {"template": "", "timeout_ms": 5000}),
    ModuleDef("script_start", ModuleCategory.TRIGGER, "脚本启动", "▶",
              "脚本启动时立即触发"),
    ModuleDef("hotkey", ModuleCategory.TRIGGER, "热键按下", "⌨",
              "当指定热键被按下时触发",
              {"key_combo": ""}),
    ModuleDef("timer", ModuleCategory.TRIGGER, "定时器", "⏱",
              "按设定间隔重复触发",
              {"interval_ms": 1000}),
    ModuleDef("var_change", ModuleCategory.TRIGGER, "变量变化", "📊",
              "当指定变量的值发生变化时触发",
              {"variable": ""}),

    # 动作
    ModuleDef("click_center", ModuleCategory.ACTION, "点击图像中心", "🖱",
              "点击匹配到的图像中心位置",
              {"button": "left", "offset_x": 0, "offset_y": 0}),
    ModuleDef("click_coord", ModuleCategory.ACTION, "点击坐标", "🎯",
              "点击屏幕上指定的坐标位置",
              {"x": 0, "y": 0, "button": "left"}),
    ModuleDef("press_key", ModuleCategory.ACTION, "按键", "⌨",
              "按下并释放一个键盘按键",
              {"key": ""}),
    ModuleDef("type_text", ModuleCategory.ACTION, "输入文本", "📝",
              "输入一串文本字符",
              {"text": ""}),
    ModuleDef("wait", ModuleCategory.ACTION, "等待", "⏳",
              "暂停执行指定时长",
              {"duration_ms": 500}),
    ModuleDef("set_var", ModuleCategory.ACTION, "设置变量", "📊",
              "给变量设置一个值",
              {"name": "", "value": ""}),
    ModuleDef("scroll", ModuleCategory.ACTION, "滚轮", "↕",
              "滚动鼠标滚轮",
              {"amount": 1, "x": 0, "y": 0}),
    ModuleDef("drag", ModuleCategory.ACTION, "拖拽", "↗",
              "从一个点点击拖拽到另一个点",
              {"from_x": 0, "from_y": 0, "to_x": 0, "to_y": 0}),

    # 条件
    ModuleDef("if_visible", ModuleCategory.CONDITION, "如果图像可见", "👁",
              "检查模板图像是否在屏幕上可见",
              {"template": "", "confidence": 0.85}),
    ModuleDef("if_variable", ModuleCategory.CONDITION, "如果变量", "🔢",
              "检查变量与某个值的比较结果",
              {"variable": "", "operator": "eq", "value": ""}),
    ModuleDef("if_elapsed", ModuleCategory.CONDITION, "如果时间到达", "⏰",
              "检查计时器是否已到达指定时长",
              {"timer_name": "", "duration_ms": 0}),
    ModuleDef("if_pixel", ModuleCategory.CONDITION, "如果像素颜色", "🎨",
              "检查指定坐标的像素是否为特定颜色",
              {"x": 0, "y": 0, "color": "#000000", "tolerance": 10}),
    ModuleDef("random", ModuleCategory.CONDITION, "随机概率", "🎲",
              "以给定概率随机进入此分支",
              {"percent": 50}),

    # 循环
    ModuleDef("while_visible", ModuleCategory.LOOP, "当图像可见时循环", "🔄",
              "当模板图像在屏幕上可见时重复执行",
              {"template": "", "max_iterations": 0, "delay_ms": 100}),
    ModuleDef("repeat", ModuleCategory.LOOP, "重复N次", "🔁",
              "固定重复指定次数",
              {"count": 1, "delay_ms": 0}),
    ModuleDef("until_condition", ModuleCategory.LOOP, "直到条件满足", "⏳",
              "重复执行直到条件为真",
              {"delay_ms": 100}),
    ModuleDef("for_each_match", ModuleCategory.LOOP, "对每个匹配", "🔍",
              "对找到的每个匹配结果分别执行一次",
              {"template": "", "confidence": 0.85}),
    ModuleDef("forever", ModuleCategory.LOOP, "无限循环", "∞",
              "无限重复执行",
              {"delay_ms": 100}),

    # 分组
    ModuleDef("subroutine", ModuleCategory.GROUP, "子程序", "📦",
              "一个命名的可复用模块块",
              {"name": ""}),
    ModuleDef("import_block", ModuleCategory.GROUP, "导入", "📥",
              "从库中导入一个模块块",
              {"source": ""}),
]
