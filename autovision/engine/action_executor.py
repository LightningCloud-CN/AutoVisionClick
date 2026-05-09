"""Executes action nodes and evaluates condition nodes."""
from __future__ import annotations
import time
import random
from autovision.model.variable_store import VariableStore
from autovision.model.script import ScriptNode
from autovision.engine.matcher import MatchResult
from autovision.engine.input_sim import InputSim


class ActionExecutor:
    def __init__(self, match_context: MatchResult | None = None,
                 capture_service=None, matcher_service=None):
        self._match = match_context
        self._capture = capture_service
        self._matcher = matcher_service
        self._input = InputSim()
        self._interrupted = False

    def interrupt(self):
        self._interrupted = True

    def execute(self, node: ScriptNode, store: VariableStore):
        if self._interrupted:
            return
        self._execute_one(node, store)

    def evaluate_condition(self, node: ScriptNode, store: VariableStore) -> bool:
        return self._eval_condition(node, store)

    def _execute_one(self, node: ScriptNode, store: VariableStore):
        subtype = node.subtype
        cfg = node.config

        if self._match:
            store.set_match(self._match.x, self._match.y)

        if subtype == "click_center" and self._match:
            cx, cy = self._match.center
            self._input.click(
                cx + int(cfg.get("offset_x", 0)),
                cy + int(cfg.get("offset_y", 0)),
                button=cfg.get("button", "left"),
            )
        elif subtype == "click_coord":
            self._input.click(
                int(cfg.get("x", 0)), int(cfg.get("y", 0)),
                button=cfg.get("button", "left"),
            )
        elif subtype == "press_key":
            self._input.press_key(cfg.get("key", ""))
        elif subtype == "type_text":
            self._input.type_text(str(cfg.get("text", "")))
        elif subtype == "wait":
            duration = int(cfg.get("duration_ms", 500)) / 1000.0
            time.sleep(duration)
        elif subtype == "set_var":
            store.set(cfg["name"], cfg["value"])
        elif subtype == "scroll":
            x = int(cfg.get("x", 0)) if cfg.get("x", 0) else None
            y = int(cfg.get("y", 0)) if cfg.get("y", 0) else None
            self._input.scroll(int(cfg.get("amount", 1)), x=x, y=y)
        elif subtype == "drag":
            self._input.drag(
                int(cfg["from_x"]), int(cfg["from_y"]),
                int(cfg["to_x"]), int(cfg["to_y"]),
            )

    def _eval_condition(self, node: ScriptNode, store: VariableStore) -> bool:
        cfg = node.config
        subtype = node.subtype
        if subtype == "if_variable":
            var = cfg["variable"]
            op = cfg.get("operator", "eq")
            val = cfg.get("value", "")
            current = store.get(var)
            if current is None:
                return False
            return self._compare(current, op, val)
        elif subtype == "random":
            return random.randint(1, 100) <= int(cfg.get("percent", 50))
        return False

    @staticmethod
    def _compare(current, op: str, target) -> bool:
        try:
            curr_num = float(current)
            tgt_num = float(target)
            if op == "eq":
                return curr_num == tgt_num
            if op == "neq":
                return curr_num != tgt_num
            if op == "lt":
                return curr_num < tgt_num
            if op == "lte":
                return curr_num <= tgt_num
            if op == "gt":
                return curr_num > tgt_num
            if op == "gte":
                return curr_num >= tgt_num
        except (ValueError, TypeError):
            if op == "eq":
                return str(current) == str(target)
            if op == "neq":
                return str(current) != str(target)
        return False
