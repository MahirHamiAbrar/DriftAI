import sys
import threading
from PyQt6.QtWidgets import QApplication, QMainWindow, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt
from pynput import keyboard

class HiddenWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Hidden System Tray Window")
        self.setGeometry(200, 200, 400, 300)

        # Keep window hidden initially
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.hide()

        # System Tray
        self.tray_icon = QSystemTrayIcon(QIcon("icon.png"), self)
        self.tray_icon.setToolTip("Hidden Tray App")

        # Create Tray Menu
        menu = QMenu()
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show_window)
        menu.addAction(show_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close_app)
        menu.addAction(exit_action)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

        # Start listening for Win + D in a separate thread
        self.start_hotkey_listener()

    def show_window(self):
        self.show()
        self.activateWindow()

    def hide_window(self):
        self.hide()

    def close_app(self):
        self.tray_icon.hide()
        self.close()

    def on_hotkey(self):
        if self.isVisible():
            self.hide_window()
        else:
            self.show_window()

    def start_hotkey_listener(self):
        def listen_hotkey():
            with keyboard.GlobalHotKeys({
                "<cmd>+d": self.on_hotkey,  # 'cmd' represents Win key in pynput
            }) as listener:
                listener.join()

        thread = threading.Thread(target=listen_hotkey, daemon=True)
        thread.start()

def run_main_app():
    app = QApplication(sys.argv)
    window = HiddenWindow()
    sys.exit(app.exec())
