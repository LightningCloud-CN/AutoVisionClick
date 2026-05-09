"""Keyboard and mouse input simulation via pydirectinput."""
import time
import pydirectinput

pydirectinput.FAILSAFE = True
pydirectinput.PAUSE = 0.01


_key_map = {
    "enter": 0x0D, "return": 0x0D, "space": 0x20, "tab": 0x09,
    "escape": 0x1B, "esc": 0x1B, "backspace": 0x08,
    "shift": 0x10, "ctrl": 0x11, "alt": 0x12,
    "up": 0x26, "down": 0x28, "left": 0x25, "right": 0x27,
    "insert": 0x2D, "delete": 0x2E, "home": 0x24, "end": 0x23,
    "pageup": 0x21, "pagedown": 0x22,
    "f1": 0x70, "f2": 0x71, "f3": 0x72, "f4": 0x73,
    "f5": 0x74, "f6": 0x75, "f7": 0x76, "f8": 0x77,
    "f9": 0x78, "f10": 0x79, "f11": 0x7A, "f12": 0x7B,
}


def key_name_to_vk(name: str) -> int:
    name = name.lower().strip()
    if name in _key_map:
        return _key_map[name]
    if len(name) == 1 and name.isalnum():
        return ord(name.upper())
    return 0


class InputSim:
    @staticmethod
    def click(x: int, y: int, button: str = "left"):
        pydirectinput.moveTo(x, y)
        time.sleep(0.02)
        pydirectinput.click(button=button)

    @staticmethod
    def press_key(key: str):
        pydirectinput.press(key)

    @staticmethod
    def type_text(text: str):
        pydirectinput.typewrite(text, interval=0.02)

    @staticmethod
    def scroll(amount: int, x: int | None = None, y: int | None = None):
        if x is not None and y is not None:
            pydirectinput.moveTo(x, y)
            time.sleep(0.01)
        pydirectinput.scroll(amount)

    @staticmethod
    def move_to(x: int, y: int):
        pydirectinput.moveTo(x, y)

    @staticmethod
    def drag(from_x: int, from_y: int, to_x: int, to_y: int, button: str = "left"):
        pydirectinput.moveTo(from_x, from_y)
        pydirectinput.mouseDown(button=button)
        time.sleep(0.02)
        pydirectinput.moveTo(to_x, to_y)
        time.sleep(0.02)
        pydirectinput.mouseUp(button=button)

    @staticmethod
    def key_down(key: str):
        pydirectinput.keyDown(key)

    @staticmethod
    def key_up(key: str):
        pydirectinput.keyUp(key)
