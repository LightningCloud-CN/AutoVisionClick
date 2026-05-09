"""Global hotkey manager using pynput."""
from __future__ import annotations
from pynput import keyboard


class HotkeyManager:
    def __init__(self):
        self._listener: keyboard.Listener | None = None
        self._actions: dict[str, callable] = {}
        self._pressed = set()
        self._running = False

    def register(self, combo: str, action: callable):
        self._actions[combo] = action

    def unregister(self, combo: str):
        self._actions.pop(combo, None)

    def start(self):
        if self._running:
            return
        self._listener = keyboard.Listener(
            on_press=self._on_press, on_release=self._on_release)
        self._listener.start()
        self._running = True

    def stop(self):
        self._running = False
        if self._listener:
            self._listener.stop()
            self._listener = None

    def _on_press(self, key):
        try:
            self._pressed.add(self._key_name(key))
        except Exception:
            return
        self._check_combos()

    def _on_release(self, key):
        try:
            self._pressed.discard(self._key_name(key))
        except Exception:
            pass

    def _check_combos(self):
        for combo, action in self._actions.items():
            parts = [p.strip().lower().replace("+", "") for p in combo.split("+")]
            required = set()
            for p in parts:
                p = p.strip()
                if p == "ctrl":
                    required.add("ctrl")
                elif p == "shift":
                    required.add("shift")
                elif p == "alt":
                    required.add("alt")
                else:
                    required.add(p.lower())
            if required and required == self._pressed:
                action()

    @staticmethod
    def _key_name(key) -> str:
        if hasattr(key, "name"):
            return key.name
        if hasattr(key, "char") and key.char:
            return key.char.lower()
        return str(key).lower()
