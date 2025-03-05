import sys
import signal
from PyQt6.QtWidgets import QApplication, QMainWindow, QSystemTrayIcon, QMenu, QWidget
from PyQt6.QtGui import QIcon, QAction, QKeySequence, QShortcut
from PyQt6.QtCore import Qt, QObject, QEvent

class GlobalShortcutFilter(QObject):
    def __init__(self, toggle_callback):
        super().__init__()
        self.toggle_callback = toggle_callback
        self.super_pressed = False
        self.d_pressed = False

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            # Check for Super (Meta) key
            if event.key() == Qt.Key.Key_Super_L or event.key() == Qt.Key.Key_Super_R:
                self.super_pressed = True
                print('super pressed')
            
            # Check for D key
            if event.key() == Qt.Key.Key_D:
                self.d_pressed = True
                print('key-D pressed')
            
            # Trigger if both Super and D are pressed
            if self.super_pressed and self.d_pressed:
                self.toggle_callback()
                return True

        elif event.type() == QEvent.Type.KeyRelease:
            # Reset key states on release
            if event.key() == Qt.Key.Key_Super_L or event.key() == Qt.Key.Key_Super_R:
                self.super_pressed = False
            
            if event.key() == Qt.Key.Key_D:
                self.d_pressed = False

        return super().eventFilter(obj, event)

class SystemTrayApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Set up the main window
        self.setWindowTitle("Hidden System Tray App")
        self.setGeometry(100, 100, 400, 300)
        
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon.fromTheme("computer"))  # Default system icon
        
        # Create tray icon context menu
        tray_menu = QMenu()
        
        # Add actions to the tray menu
        show_action = QAction("Show Window", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # Initially hide the window
        self.hide()
        
        # Set up global shortcut filter
        self.setup_global_shortcut()
        
    def setup_global_shortcut(self):
        # Create a global shortcut filter
        self.shortcut_filter = GlobalShortcutFilter(self.toggle_window)
        
        # Install the event filter on the application
        QApplication.instance().installEventFilter(self.shortcut_filter)
        
    def toggle_window(self):
        # Toggle window visibility
        if self.isHidden():
            self.show()
            self.activateWindow()
        else:
            self.hide()

def run_main_app():
    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    app = QApplication(sys.argv)
    
    # Ensure the app continues running even when main window is hidden
    app.setQuitOnLastWindowClosed(False)
    
    window = SystemTrayApp()
    
    sys.exit(app.exec())
