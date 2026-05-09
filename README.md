# AutoVisionClick 🎯

> Automated screen recognition scripting tool based on Python + OpenCV — with a modern web UI.

> 基于 Python + OpenCV 的自动化屏幕识别脚本工具 — 配备现代化 Web 界面。

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue" alt="Python">
  <img src="https://img.shields.io/badge/flask-3.0+-green" alt="Flask">
  <img src="https://img.shields.io/badge/opencv-4.8+-red" alt="OpenCV">
  <img src="https://img.shields.io/badge/license-MIT-purple" alt="License">
</p>

---

## 📖 English / 中文

- [English](#english)
- [中文](#中文)

---

## English

### What is AutoVisionClick?

AutoVisionClick is a desktop automation tool that watches your screen for specific images (templates) and performs actions when they appear. Built primarily for game automation but useful for any repetitive visual task.

**Core features:**
- Screen region / full-screen template matching via OpenCV
- Modular visual scripting: triggers → conditions → loops → actions
- Modern glass-morphism web UI (Flask + SocketIO)
- Real-time dashboard with live log streaming
- Screen region capture tool for creating templates
- Coordinate picker (click anywhere on screen to capture)
- Quick-start wizard for beginners
- Global hotkey control (Ctrl+Shift+F5~F8)
- Project-based folder storage (JSON + images)

### Installation

#### Method 1: Download Packaged Release (Recommended)

No Python required. Just download and run.

1. Go to [Releases](https://github.com/LightningCloud-CN/AutoVisionClick/releases)
2. Download the latest `AutoVisionClick-vX.X.X.zip`
3. Extract to any folder
4. Double-click `AutoVisionClick.exe`

The browser opens automatically at `http://127.0.0.1:5000`.

#### Method 2: Run from Source (Developers)

Requires Python 3.10+.

```bash
git clone https://github.com/LightningCloud-CN/AutoVisionClick.git
cd AutoVisionClick
pip install -r requirements.txt
python -m autovision.main
```

#### Method 3: Build from Source

```bash
git clone https://github.com/LightningCloud-CN/AutoVisionClick.git
cd AutoVisionClick
pip install -r requirements.txt
pip install pyinstaller
pyinstaller AutoVisionClick.spec
# Output: dist/AutoVisionClick.exe
```

### How It Works

```
┌─────────────┐    ┌──────────────┐    ┌──────────────┐
│  Capture    │───▶│  Matcher     │───▶│  Action      │
│  (mss)      │    │  (OpenCV)    │    │  Executor    │
│  screenshot │    │  template    │    │  click/key   │
│  window/area│    │  matching    │    │  wait/scroll │
└─────────────┘    └──────────────┘    └──────────────┘
                          │
                          ▼
                   ┌──────────────┐
                   │  Script      │
                   │  Runner      │
                   │  (per thread)│
                   └──────────────┘
```

**Script structure** — every script is a tree of modules:

| Category | Chinese | Modules |
|----------|---------|---------|
| Trigger | 触发器 | Image Found, Image Lost, Script Start, Hotkey, Timer, Variable Change |
| Action | 动作 | Click Center, Click Coordinate, Press Key, Type Text, Wait, Set Variable, Scroll, Drag |
| Condition | 条件 | If Visible, If Variable, If Elapsed, If Pixel Color, Random Chance |
| Loop | 循环 | While Visible, Repeat N, Until Condition, For Each Match, Forever |
| Group | 分组 | Subroutine, Import |

### Project Structure

```
AutoVisionClick/
├── autovision/
│   ├── main.py                 # Entry point
│   ├── app.py                  # App controller
│   ├── config.py               # Settings
│   ├── engine/                 # Core engines
│   │   ├── capture.py          # Screen capture (mss + Win32)
│   │   ├── matcher.py          # OpenCV template matching
│   │   ├── input_sim.py        # Keyboard/mouse simulation
│   │   ├── action_executor.py  # Execute action nodes
│   │   ├── script_runner.py    # Per-script thread
│   │   ├── runtime.py          # Multi-script manager
│   │   └── hotkeys.py          # Global hotkey hooks
│   ├── model/                  # Data models
│   │   ├── module_types.py     # 26 module type definitions
│   │   ├── script.py           # Script tree node model
│   │   ├── variable_store.py   # Per-script variables
│   │   └── project.py          # Project load/save
│   ├── web/                    # Modern web UI
│   │   ├── server.py           # Flask + SocketIO server
│   │   ├── api.py              # REST API (30+ endpoints)
│   │   └── static/             # Frontend (HTML/CSS/JS)
│   ├── gui/                    # tkinter overlay tools (kept)
│   │   ├── template_capture.py # Screen region capture
│   │   └── coordinate_picker.py# Click-to-pick coordinates
│   └── resources/              # Starter templates
├── tests/                      # Unit tests (36 tests)
└── docs/                       # Design docs
```

### Hotkeys

| Default | Action |
|---------|--------|
| Ctrl+Shift+F5 | Start all scripts |
| Ctrl+Shift+F6 | Stop all scripts |
| Ctrl+Shift+F7 | Pause / Resume |
| Ctrl+Shift+F8 | Emergency kill |

### Tech Stack

| Layer | Tech |
|-------|------|
| Language | Python 3.10+ |
| Screen capture | mss + Win32 API |
| Template matching | OpenCV (`cv2.matchTemplate`) |
| Input simulation | PyDirectInput |
| Web backend | Flask + Flask-SocketIO |
| Frontend | Vanilla HTML/CSS/JS (glass morphism) |
| Hotkeys | pynput |

---

## 中文

### 什么是 AutoVisionClick？

AutoVisionClick 是一款桌面自动化工具。它实时监控屏幕上是否出现指定的图像（模板），一旦匹配成功，就执行你预设的动作链。主要用于游戏自动化，也适用于任何重复性的视觉识别任务。

**核心功能：**
- 基于 OpenCV 的屏幕区域 / 全屏模板匹配
- 模块化可视化脚本编辑：触发器 → 条件 → 循环 → 动作
- 现代化玻璃拟态 Web 界面 (Flask + SocketIO)
- 实时运行面板 + 事件日志流式推送
- 屏幕区域截图工具（拖拽选取并保存为模板）
- 坐标拾取器（在屏幕任意位置点击捕获坐标 + RGB 值）
- 新手快速向导（3 步生成脚本）
- 全局热键控制 (Ctrl+Shift+F5~F8)
- 基于项目文件夹的存储 (JSON + 图片)

### 安装方式

#### 方式一：下载打包版（推荐）

无需安装 Python，下载即用。

1. 前往 [Releases](https://github.com/LightningCloud-CN/AutoVisionClick/releases) 页面
2. 下载最新版 `AutoVisionClick-vX.X.X.zip`
3. 解压到任意目录
4. 双击 `AutoVisionClick.exe`

浏览器自动打开 `http://127.0.0.1:5000`。

#### 方式二：源码运行（开发者）

需要 Python 3.10+。

```bash
git clone https://github.com/LightningCloud-CN/AutoVisionClick.git
cd AutoVisionClick
pip install -r requirements.txt
python -m autovision.main
```

#### 方式三：自行打包

```bash
git clone https://github.com/LightningCloud-CN/AutoVisionClick.git
cd AutoVisionClick
pip install -r requirements.txt
pip install pyinstaller
pyinstaller AutoVisionClick.spec
# 输出文件: dist/AutoVisionClick.exe
```

### 工作原理

```
┌──────────┐    ┌──────────┐    ┌──────────┐
│ 截图引擎  │───▶│ 匹配引擎  │───▶│ 动作执行  │
│ (mss)    │    │ (OpenCV) │    │ 点击/按键 │
│ 屏幕/窗口 │    │ 模板匹配  │    │ 等待/滚轮 │
└──────────┘    └──────────┘    └──────────┘
                      │
                      ▼
               ┌──────────┐
               │ 脚本运行器│
               │ (每线程)  │
               └──────────┘
```

**脚本结构** — 每个脚本都是一棵模块树：

| 类别 | 模块 |
|------|------|
| 触发器 | 图像出现、图像消失、脚本启动、热键按下、定时器、变量变化 |
| 动作 | 点击图像中心、点击坐标、按键、输入文本、等待、设置变量、滚轮、拖拽 |
| 条件 | 如果图像可见、如果变量、如果时间到达、如果像素颜色、随机概率 |
| 循环 | 当图像可见时循环、重复N次、直到条件满足、对每个匹配、无限循环 |
| 分组 | 子程序、导入 |

### 使用流程

1. **新建项目** → 选择保存目录
2. **截取模板** → 点击「截图」按钮，在屏幕上拖拽选择目标图像区域
3. **创建脚本** → 点击「+ 新建」，命名脚本
4. **添加模块** → 从模块面板选择模块类型，拖入脚本树
5. **配置属性** → 选中节点，在右侧属性面板设置参数
6. **运行** → 点击「运行」按钮，实时查看仪表板和日志
7. **停止** → 点击「停止」或按热键

### 热键

| 默认热键 | 功能 |
|---------|------|
| Ctrl+Shift+F5 | 启动全部脚本 |
| Ctrl+Shift+F6 | 停止全部脚本 |
| Ctrl+Shift+F7 | 暂停 / 恢复 |
| Ctrl+Shift+F8 | 紧急停止 |

### 技术栈

| 层级 | 技术 |
|------|------|
| 语言 | Python 3.10+ |
| 屏幕截图 | mss + Win32 API |
| 模板匹配 | OpenCV (`cv2.matchTemplate`) |
| 输入模拟 | PyDirectInput |
| Web 后端 | Flask + Flask-SocketIO |
| 前端 | 原生 HTML/CSS/JS (玻璃拟态风格) |
| 全局热键 | pynput |

### 项目结构

```
AutoVisionClick/
├── autovision/
│   ├── main.py                 # 入口
│   ├── app.py                  # 应用控制器
│   ├── engine/                 # 核心引擎 (截图/匹配/输入/运行)
│   ├── model/                  # 数据模型 (模块类型/脚本树/变量/项目)
│   ├── web/                    # Web UI (Flask服务端 + 前端页面)
│   ├── gui/                    # tkinter 覆盖层工具 (截图/取坐标)
│   └── resources/              # 示例模板
├── tests/                      # 单元测试 (36 个)
└── docs/                       # 设计文档
```

### License

MIT
