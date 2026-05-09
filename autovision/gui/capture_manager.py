"""Manages screen capture requests from Flask thread to tkinter main thread."""
import queue
import threading

_capture_queue = queue.Queue()
_tk_root = None


def init(root):
    """Call from main thread with tkinter root."""
    global _tk_root
    _tk_root = root
    _poll_queue()


def _poll_queue():
    """Check for capture requests, re-schedule via tkinter after()."""
    global _tk_root
    try:
        while True:
            func = _capture_queue.get_nowait()
            func()
    except queue.Empty:
        pass
    if _tk_root:
        _tk_root.after(100, _poll_queue)


def request_capture(app_controller, sid, socketio):
    """Called from Flask thread. Schedules capture on main thread."""
    def do_capture():
        import tkinter as tk
        from autovision.gui.template_capture import TemplateCapture

        result = {}

        def on_saved(name, width, height, filepath):
            result['name'] = name
            result['width'] = width
            result['height'] = height
            result['filepath'] = filepath
            if sid:
                socketio.emit('template_captured', result, room=sid)

        def on_cancelled():
            pass

        tc = TemplateCapture(app_controller, on_saved=on_saved, on_cancelled=on_cancelled)
        tc.start_capture(root=_tk_root)

    _capture_queue.put(do_capture)


def request_coordinate(sid, socketio):
    """Called from Flask thread. Schedules coordinate picker on main thread."""
    def do_pick():
        from autovision.gui.coordinate_picker import CoordinatePicker

        def on_picked(x, y, rgb):
            socketio.emit('coordinate_picked', {
                'x': x, 'y': y,
                'rgb': list(rgb) if rgb else [0, 0, 0],
            }, room=sid)

        def on_cancelled():
            pass

        cp = CoordinatePicker(on_picked, on_cancelled=on_cancelled)
        cp.start(root=_tk_root)

    _capture_queue.put(do_pick)
