"""Entry point for AutoVision — tkinter in main thread, Flask in daemon thread."""
import tkinter as tk
import threading
import time
import webbrowser
from autovision.app import AppController
from autovision.web.server import create_app
from autovision.gui import capture_manager
from autovision import config


def main():
    app_controller = AppController()
    socketio, flask_app = create_app(app_controller)

    # Start dashboard push thread
    from autovision.web.server import _dashboard_push_thread
    push_thread = threading.Thread(
        target=_dashboard_push_thread,
        args=(socketio, app_controller),
        daemon=True,
    )
    push_thread.start()

    # Start Flask in a daemon thread
    def run_flask():
        try:
            socketio.run(flask_app,
                         host=config.SERVER_HOST,
                         port=config.SERVER_PORT,
                         allow_unsafe_werkzeug=True,
                         debug=False)
        except Exception:
            pass

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Open browser
    if config.AUTO_OPEN_BROWSER:
        def open_browser():
            time.sleep(1.0)
            webbrowser.open(f'http://{config.SERVER_HOST}:{config.SERVER_PORT}')
        threading.Thread(target=open_browser, daemon=True).start()

    print(f"AutoVision running at http://{config.SERVER_HOST}:{config.SERVER_PORT}")
    print("Close the browser tab to exit, or close this window")

    # tkinter main loop (main thread)
    root = tk.Tk()
    root.withdraw()
    root.title("AutoVision")

    # Initialize capture manager with the main-thread root
    capture_manager.init(root)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        app_controller.shutdown()
        import os
        os._exit(0)


if __name__ == "__main__":
    main()
