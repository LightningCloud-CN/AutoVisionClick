"""AutoVision configuration and constants."""

APP_NAME = "AutoVision"
APP_VERSION = "1.0.0"

# Match engine defaults
DEFAULT_CONFIDENCE = 0.85
DEFAULT_MATCH_METHOD = "TM_CCOEFF_NORMED"
DEFAULT_TICK_MS = 500
MAX_CONCURRENT_SCRIPTS = 8

# Hotkey defaults
HK_START_ALL = "<ctrl>+<shift>+F5"
HK_STOP_ALL = "<ctrl>+<shift>+F6"
HK_PAUSE = "<ctrl>+<shift>+F7"
HK_EMERGENCY = "<ctrl>+<shift>+F8"

# GUI defaults
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
THEME = "dark"
COLOR_SCHEME = "dark-blue"

# Capture
SCREENSHOT_FORMAT = "PNG"
TEMPLATE_DIR = "images"
SCRIPT_DIR = "scripts"
LOG_DIR = "logs"
PROJECT_FILENAME = "project.json"

# Validation
MIN_CONFIDENCE_WARN = 0.7
MIN_WAIT_WARN_MS = 100
