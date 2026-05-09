"""Flask + SocketIO web server for AutoVision."""
import time
import threading
import webbrowser
from flask import Flask, send_from_directory
from flask_socketio import SocketIO
from autovision import config


_subscribed_clients = set()


def create_app(app_controller):
    static_folder = _find_static_dir()
    flask_app = Flask(__name__, static_folder=static_folder, static_url_path='')
    flask_app.config['SECRET_KEY'] = 'autovision-secret'
    socketio = SocketIO(flask_app, cors_allowed_origins="*", async_mode='threading')

    flask_app.config['APP_CONTROLLER'] = app_controller
    flask_app.config['SOCKETIO'] = socketio

    from autovision.web.api import api_bp
    flask_app.register_blueprint(api_bp, url_prefix='/api')

    @flask_app.route('/')
    def index():
        return send_from_directory(static_folder, 'index.html')

    _register_socket_events(socketio, app_controller)

    return socketio, flask_app


def _find_static_dir():
    import os, sys
    # PyInstaller bundles files to sys._MEIPASS
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, 'static')


def _register_socket_events(socketio, app_controller):
    @socketio.on('connect')
    def on_connect():
        pass

    @socketio.on('disconnect')
    def on_disconnect():
        from flask import request
        _subscribed_clients.discard(request.sid)

    @socketio.on('subscribe_dashboard')
    def on_subscribe():
        from flask import request
        _subscribed_clients.add(request.sid)

    @socketio.on('unsubscribe_dashboard')
    def on_unsubscribe():
        from flask import request
        _subscribed_clients.discard(request.sid)


def _dashboard_push_thread(socketio, app_controller):
    last_log_idxs = {}
    while True:
        time.sleep(1)
        if not _subscribed_clients:
            continue
        rt = app_controller.get_runtime()
        if rt is None:
            socketio.emit('runtime_state', {'state': 'idle', 'runners': []})
            continue
        runners_data = []
        for runner in rt.get_all_runners():
            rdata = {
                'name': runner.script.name,
                'state': runner.state.value,
                'match_count': runner._match_count,
                'runtime_seconds': runner.runtime_seconds(),
                'error': runner._error,
            }
            runners_data.append(rdata)

            name = runner.script.name
            prev_idx = last_log_idxs.get(name, 0)
            new_entries = runner.log[prev_idx:]
            if new_entries:
                last_log_idxs[name] = len(runner.log)
                socketio.emit('runner_log', {
                    'script_name': name,
                    'entries': [{'ts': ts, 'level': lv, 'msg': msg}
                                for ts, lv, msg in new_entries],
                })
        socketio.emit('runtime_state', {
            'state': rt.state.value,
            'runners': runners_data,
        })


def start_server(socketio, flask_app, app_controller):
    push_thread = threading.Thread(
        target=_dashboard_push_thread,
        args=(socketio, app_controller),
        daemon=True,
    )
    push_thread.start()

    if config.AUTO_OPEN_BROWSER:
        def open_browser():
            time.sleep(1.0)
            webbrowser.open(f'http://{config.SERVER_HOST}:{config.SERVER_PORT}')
        threading.Thread(target=open_browser, daemon=True).start()

    try:
        socketio.run(flask_app,
                     host=config.SERVER_HOST,
                     port=config.SERVER_PORT,
                     allow_unsafe_werkzeug=True,
                     debug=False)
    except KeyboardInterrupt:
        pass
    finally:
        app_controller.shutdown()
