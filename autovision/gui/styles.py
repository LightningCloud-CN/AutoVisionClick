"""GUI theme, colors, and fonts."""
import customtkinter as ctk

# Color palette (dark theme)
BG_DARK = "#0d1117"
BG_PANEL = "#161b22"
BG_CARD = "#1a1a2e"
BG_INPUT = "#0f3460"
BORDER = "#30363d"

ACCENT_RED = "#e94560"
ACCENT_GREEN = "#00ff99"
ACCENT_BLUE = "#00ccff"
ACCENT_YELLOW = "#ffc107"
ACCENT_PURPLE = "#c792ea"

TEXT_PRIMARY = "#e6edf3"
TEXT_SECONDARY = "#8b949e"
TEXT_MUTED = "#484f58"

CATEGORY_COLORS = {
    "trigger": ACCENT_RED,
    "action": ACCENT_GREEN,
    "condition": ACCENT_YELLOW,
    "loop": ACCENT_BLUE,
    "group": TEXT_SECONDARY,
}

FONT_FAMILY = "Segoe UI"
FONT_MONO = "Cascadia Code"


def apply_theme():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")


def styled_frame(parent, **kwargs):
    return ctk.CTkFrame(
        parent,
        fg_color=BG_PANEL,
        border_color=BORDER,
        border_width=1,
        corner_radius=8,
        **kwargs,
    )


def styled_button(parent, text, color=ACCENT_BLUE, **kwargs):
    return ctk.CTkButton(
        parent,
        text=text,
        fg_color=color,
        hover_color=_darken(color, 0.15),
        corner_radius=6,
        font=(FONT_FAMILY, 12),
        **kwargs,
    )


def styled_label(parent, text, size=12, color=TEXT_PRIMARY, **kwargs):
    return ctk.CTkLabel(
        parent,
        text=text,
        text_color=color,
        font=(FONT_FAMILY, size),
        **kwargs,
    )


def _darken(hex_color: str, factor: float) -> str:
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r = max(0, int(r * (1 - factor)))
    g = max(0, int(g * (1 - factor)))
    b = max(0, int(b * (1 - factor)))
    return f"#{r:02x}{g:02x}{b:02x}"
