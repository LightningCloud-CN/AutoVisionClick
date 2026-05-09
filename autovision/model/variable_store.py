"""Per-script variable store with auto-generated match variables."""
from threading import Lock


class VariableStore:
    def __init__(self):
        self._data: dict[str, object] = {}
        self._lock = Lock()

    def set(self, name: str, value: object):
        with self._lock:
            self._data[name] = value

    def get(self, name: str, default: object = None) -> object:
        with self._lock:
            return self._data.get(name, default)

    def exists(self, name: str) -> bool:
        with self._lock:
            return name in self._data

    def delete(self, name: str):
        with self._lock:
            self._data.pop(name, None)

    def inc(self, name: str, amount: int = 1) -> int:
        with self._lock:
            current = self._data.get(name, 0)
            if not isinstance(current, (int, float)):
                current = 0
            current += amount
            self._data[name] = current
            return current

    def set_match(self, x: int, y: int):
        self.set("$match_x", x)
        self.set("$match_y", y)

    def set_loop_count(self, count: int):
        self.set("$loop_count", count)

    def clear(self):
        with self._lock:
            self._data.clear()

    def list_all(self) -> list[dict]:
        with self._lock:
            return [{"name": k, "value": v} for k, v in self._data.items()]
