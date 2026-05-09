"""REST API blueprint for AutoVision web UI."""
from flask import Blueprint, request, jsonify, current_app, send_file
from autovision.model.script import Script, ScriptNode
from autovision.model.module_types import ModuleDef

api_bp = Blueprint('api', __name__)


def _ctrl():
    return current_app.config['APP_CONTROLLER']


def _sio():
    return current_app.config['SOCKETIO']


def _resolve_path(root, path):
    """Resolve a node path [0,1,2] to (node, parent)."""
    if not path:
        return root, None
    node = root
    parent = None
    for idx in path[:-1]:
        parent = node
        node = node.children[idx]
    if len(path) > 0:
        parent = node
        node = node.children[path[-1]]
    return node, parent


# ═══════════ PROJECT ═══════════

@api_bp.route('/project/new', methods=['POST'])
def project_new():
    data = request.get_json()
    name = data.get('name', 'Untitled')
    directory = data.get('directory', '')
    if not directory:
        return jsonify({'success': False, 'error': 'No directory provided'}), 400
    _ctrl().new_project(name, directory)
    _ctrl().save_project()
    return jsonify({'success': True, **(_ctrl().get_project_state() or {})})


@api_bp.route('/project/open', methods=['POST'])
def project_open():
    data = request.get_json()
    directory = data.get('directory', '')
    if not directory:
        return jsonify({'success': False, 'error': 'No directory provided'}), 400
    try:
        _ctrl().load_project(directory)
    except FileNotFoundError:
        return jsonify({'success': False, 'error': 'project.json not found'}), 404
    return jsonify({'success': True, **(_ctrl().get_project_state() or {})})


@api_bp.route('/project/save', methods=['POST'])
def project_save():
    _ctrl().save_project()
    return jsonify({'success': True})


@api_bp.route('/project/state', methods=['GET'])
def project_state():
    state = _ctrl().get_project_state()
    if state is None:
        return jsonify({'success': False, 'error': 'No project open'}), 404
    return jsonify({'success': True, **state})


# ═══════════ RUNTIME ═══════════

@api_bp.route('/runtime/start', methods=['POST'])
def runtime_start():
    _ctrl().start_all()
    return jsonify({'success': True})


@api_bp.route('/runtime/stop', methods=['POST'])
def runtime_stop():
    _ctrl().stop_all()
    return jsonify({'success': True})


@api_bp.route('/runtime/pause', methods=['POST'])
def runtime_pause():
    _ctrl().toggle_pause()
    return jsonify({'success': True})


@api_bp.route('/runtime/emergency', methods=['POST'])
def runtime_emergency():
    _ctrl().emergency_stop()
    return jsonify({'success': True})


@api_bp.route('/runtime/start_single', methods=['POST'])
def runtime_start_single():
    name = request.get_json().get('name', '')
    _ctrl().start_single(name)
    return jsonify({'success': True})


@api_bp.route('/runtime/stop_single', methods=['POST'])
def runtime_stop_single():
    name = request.get_json().get('name', '')
    _ctrl().stop_single(name)
    return jsonify({'success': True})


# ═══════════ SCRIPTS ═══════════

@api_bp.route('/scripts', methods=['GET'])
def scripts_list():
    return jsonify({'scripts': _ctrl().get_script_names()})


@api_bp.route('/script/create', methods=['POST'])
def script_create():
    name = request.get_json().get('name', 'New Script')
    _ctrl().create_script(name)
    return jsonify({'success': True, 'name': name})


@api_bp.route('/script/<name>', methods=['DELETE'])
def script_delete(name):
    _ctrl().delete_script(name)
    return jsonify({'success': True})


@api_bp.route('/script/<name>', methods=['GET'])
def script_get(name):
    s = _ctrl().get_script(name)
    if s is None:
        return jsonify({'success': False, 'error': 'Script not found'}), 404
    return jsonify({'success': True, 'script': s.to_dict()})


@api_bp.route('/script/<name>', methods=['PUT'])
def script_update(name):
    s = _ctrl().get_script(name)
    if s is None:
        return jsonify({'success': False, 'error': 'Script not found'}), 404
    data = request.get_json()
    for key in ('name', 'enabled', 'hotkey', 'window_title', 'window_method', 'tick_ms'):
        if key in data:
            setattr(s, key, data[key])
    return jsonify({'success': True, 'script': s.to_dict()})


@api_bp.route('/script/<name>/node', methods=['POST'])
def script_add_node(name):
    s = _ctrl().get_script(name)
    if s is None:
        return jsonify({'success': False, 'error': 'Script not found'}), 404
    data = request.get_json()
    parent_path = data.get('parent_path', [])
    subtype = data.get('subtype', '')

    mod = ModuleDef.get(subtype)
    if mod is None:
        return jsonify({'success': False, 'error': f'Unknown module: {subtype}'}), 400

    cfg = {k: v for k, v in mod.config_schema.items()}
    node = ScriptNode(type=mod.category.value, subtype=subtype, config=cfg)

    if s.root is None:
        s.root = node
    else:
        parent, _ = _resolve_path(s.root, parent_path)
        parent.add_child(node)

    return jsonify({'success': True, 'script': s.to_dict()})


@api_bp.route('/script/<name>/node', methods=['DELETE'])
def script_delete_node(name):
    s = _ctrl().get_script(name)
    if s is None:
        return jsonify({'success': False, 'error': 'Script not found'}), 404
    path = request.get_json().get('node_path', [])
    if not path:
        s.root = None
    else:
        node, parent = _resolve_path(s.root, path)
        parent.remove_child(node)
    return jsonify({'success': True, 'script': s.to_dict()})


@api_bp.route('/script/<name>/node/move', methods=['PUT'])
def script_move_node(name):
    s = _ctrl().get_script(name)
    if s is None:
        return jsonify({'success': False, 'error': 'Script not found'}), 404
    data = request.get_json()
    path = data.get('node_path', [])
    direction = data.get('direction', 'up')
    node, parent = _resolve_path(s.root, path)
    if parent is None:
        return jsonify({'success': False, 'error': 'Cannot move root'}), 400
    idx = parent.children.index(node)
    new_idx = idx - 1 if direction == 'up' else idx + 1
    if 0 <= new_idx < len(parent.children):
        parent.children[idx], parent.children[new_idx] = \
            parent.children[new_idx], parent.children[idx]
    return jsonify({'success': True, 'script': s.to_dict()})


@api_bp.route('/script/<name>/node/config', methods=['PUT'])
def script_update_node_config(name):
    s = _ctrl().get_script(name)
    if s is None:
        return jsonify({'success': False, 'error': 'Script not found'}), 404
    data = request.get_json()
    path = data.get('node_path', [])
    key = data.get('key', '')
    value = data.get('value', '')

    node, _ = _resolve_path(s.root, path)

    mod = ModuleDef.get(node.subtype)
    if mod and key in mod.config_schema:
        default = mod.config_schema[key]
        if isinstance(default, (int, float)):
            try:
                value = type(default)(value)
            except (ValueError, TypeError):
                value = default
    node.config[key] = value
    return jsonify({'success': True, 'script': s.to_dict()})


# ═══════════ TEMPLATES ═══════════

@api_bp.route('/templates', methods=['GET'])
def templates_list():
    return jsonify({'templates': _ctrl().list_templates()})


@api_bp.route('/templates/<name>', methods=['GET'])
def template_serve(name):
    path = _ctrl().template_path(name)
    if path is None:
        return jsonify({'success': False, 'error': 'Template not found'}), 404
    return send_file(path)


@api_bp.route('/templates/<name>', methods=['DELETE'])
def template_delete(name):
    _ctrl().delete_template(name)
    return jsonify({'success': True})


@api_bp.route('/templates/upload', methods=['POST'])
def template_upload():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No filename'}), 400
    import os, tempfile
    tmp = os.path.join(tempfile.gettempdir(), file.filename)
    file.save(tmp)
    _ctrl().import_template(tmp, file.filename)
    os.remove(tmp)
    return jsonify({'success': True, 'name': file.filename})


# ═══════════ TOOLS ═══════════

@api_bp.route('/tools/list_windows', methods=['GET'])
def tools_list_windows():
    return jsonify({'windows': _ctrl().list_windows()})


@api_bp.route('/tools/capture_template', methods=['POST'])
def tools_capture_template():
    import threading
    sid = request.args.get('sid', '')

    def run():
        import tkinter as tk
        result = {}
        done = threading.Event()

        def on_saved(name, width, height, filepath):
            result['name'] = name
            result['width'] = width
            result['height'] = height
            result['filepath'] = filepath
            done.set()

        root = tk.Tk()
        root.withdraw()
        try:
            _ctrl().start_template_capture(on_saved=on_saved)
            root.mainloop()
        except Exception:
            pass
        done.wait(timeout=120)
        if result and sid:
            _sio().emit('template_captured', result, room=sid)

    threading.Thread(target=run, daemon=True).start()
    return jsonify({'success': True, 'message': 'Capture started'})


@api_bp.route('/tools/pick_coordinate', methods=['POST'])
def tools_pick_coordinate():
    import threading
    sid = request.args.get('sid', '')

    def run():
        import tkinter as tk
        result = {}
        done = threading.Event()

        def on_picked(x, y, rgb):
            result['x'] = x
            result['y'] = y
            result['rgb'] = list(rgb) if rgb else [0, 0, 0]
            done.set()

        root = tk.Tk()
        root.withdraw()
        try:
            _ctrl().start_coordinate_picker(on_picked=on_picked)
            root.mainloop()
        except Exception:
            pass
        done.wait(timeout=30)
        if result and sid:
            _sio().emit('coordinate_picked', result, room=sid)

    threading.Thread(target=run, daemon=True).start()
    return jsonify({'success': True, 'message': 'Picker started'})


# ═══════════ META ═══════════

@api_bp.route('/modules', methods=['GET'])
def modules_list():
    return jsonify({'modules': _ctrl().get_module_registry()})


@api_bp.route('/wizard/generate', methods=['POST'])
def wizard_generate():
    data = request.get_json()
    name = _ctrl().wizard_generate(data)
    return jsonify({'success': True, 'name': name})


@api_bp.route('/validate-path', methods=['POST'])
def validate_path():
    import os
    path = request.get_json().get('path', '')
    exists = os.path.isdir(path)
    return jsonify({'exists': exists, 'path': path})
