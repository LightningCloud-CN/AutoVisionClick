"""Entry point for AutoVision — web-based UI."""
from autovision.app import AppController
from autovision.web.server import create_app, start_server


def main():
    app_controller = AppController()
    socketio, flask_app = create_app(app_controller)
    start_server(socketio, flask_app, app_controller)


if __name__ == "__main__":
    main()
