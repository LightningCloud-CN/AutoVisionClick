"""OpenCV template matching engine."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import cv2
from autovision.config import DEFAULT_CONFIDENCE, DEFAULT_MATCH_METHOD


@dataclass
class MatchResult:
    x: int
    y: int
    width: int
    height: int
    confidence: float

    @property
    def center(self) -> tuple[int, int]:
        return (self.x + self.width // 2, self.y + self.height // 2)


METHOD_MAP = {
    "TM_CCOEFF": cv2.TM_CCOEFF,
    "TM_CCOEFF_NORMED": cv2.TM_CCOEFF_NORMED,
    "TM_CCORR": cv2.TM_CCORR,
    "TM_CCORR_NORMED": cv2.TM_CCORR_NORMED,
    "TM_SQDIFF": cv2.TM_SQDIFF,
    "TM_SQDIFF_NORMED": cv2.TM_SQDIFF_NORMED,
}


class Matcher:
    def __init__(self, default_confidence: float = DEFAULT_CONFIDENCE,
                 default_method: str = DEFAULT_MATCH_METHOD):
        self.default_confidence = default_confidence
        self.default_method = METHOD_MAP.get(default_method, cv2.TM_CCOEFF_NORMED)

    def find(self, template: np.ndarray, scene: np.ndarray,
             confidence: float | None = None,
             method: int | None = None) -> list[MatchResult]:
        if confidence is None:
            confidence = self.default_confidence
        if method is None:
            method = self.default_method

        tmpl = self._to_gray(template)
        scn = self._to_gray(scene)

        t_h, t_w = tmpl.shape[:2]
        if t_h > scn.shape[0] or t_w > scn.shape[1]:
            return []

        result = cv2.matchTemplate(scn, tmpl, method)
        locations = self._find_peaks(result, confidence, method)

        return [
            MatchResult(x=loc[0], y=loc[1], width=t_w, height=t_h,
                        confidence=float(result[loc[1], loc[0]]))
            for loc in locations
        ]

    def find_multiple(self, templates: dict[str, np.ndarray], scene: np.ndarray,
                      confidence: float | None = None) -> dict[str, list[MatchResult]]:
        return {
            name: self.find(tmpl, scene, confidence)
            for name, tmpl in templates.items()
        }

    @staticmethod
    def _to_gray(img: np.ndarray) -> np.ndarray:
        if len(img.shape) == 2:
            return img
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    def _find_peaks(self, result: np.ndarray, confidence: float,
                    method: int) -> list[tuple[int, int]]:
        if method in (cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED):
            threshold = 1.0 - confidence
            locs = np.where(result <= threshold)
        else:
            locs = np.where(result >= confidence)

        if len(locs[0]) == 0:
            return []

        coords = list(zip(locs[1], locs[0]))
        coords.sort(key=lambda c: result[c[1], c[0]], reverse=True)

        kept = []
        for x, y in coords:
            too_close = False
            for kx, ky in kept:
                if abs(x - kx) < 10 and abs(y - ky) < 10:
                    too_close = True
                    break
            if not too_close:
                kept.append((x, y))
        return kept[:50]
