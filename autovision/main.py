"""Entry point for AutoVision."""
import sys
from autovision.gui.main_window import MainWindow
from autovision.app import AppController


def main():
    app = AppController()
    window = MainWindow(app_controller=app)
    app.set_window(window)
    window.mainloop()


if __name__ == "__main__":
    main()
