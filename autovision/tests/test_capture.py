"""Tests for screen capture engine."""
import numpy as np
from autovision.engine.capture import Capture

def test_capture_full_screen():
    cap = Capture()
    img = cap.full_screen()
    assert img is not None
    assert isinstance(img, np.ndarray)
    assert len(img.shape) == 3
    assert img.shape[2] == 3

def test_list_windows():
    cap = Capture()
    windows = cap.list_windows()
    assert len(windows) > 0
    assert all(isinstance(w, str) for w in windows)
    assert any(len(w) > 0 for w in windows)
