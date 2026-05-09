"""Tests for template matcher."""
import numpy as np
import cv2
from autovision.engine.matcher import Matcher, MatchResult

TEMPLATE = np.ones((20, 20), dtype=np.uint8) * 200
TEMPLATE[5:15, 5:15] = 255

def test_matcher_init():
    m = Matcher()
    assert m.default_confidence == 0.85
    assert m.default_method == cv2.TM_CCOEFF_NORMED

def test_find_template_in_image():
    scene = (np.random.default_rng(42).random((200, 200)) * 30).astype(np.uint8)
    scene[60:80, 100:120] = 200
    scene[65:75, 105:115] = 255
    m = Matcher()
    results = m.find(TEMPLATE, scene, confidence=0.7)
    assert len(results) > 0
    assert results[0].confidence >= 0.7
    assert abs(results[0].x - 100) <= 5
    assert abs(results[0].y - 60) <= 5

def test_no_match():
    scene = (np.random.default_rng(99).random((200, 200)) * 60).astype(np.uint8)
    m = Matcher()
    results = m.find(TEMPLATE, scene, confidence=0.95)
    assert len(results) == 0

def test_match_result_center():
    r = MatchResult(x=100, y=200, width=30, height=40, confidence=0.92)
    cx, cy = r.center
    assert cx == 115
    assert cy == 220
