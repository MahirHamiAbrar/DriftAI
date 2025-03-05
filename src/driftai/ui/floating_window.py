import sys
from PyQt6.QtCore import QPropertyAnimation
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.uic.load_ui import loadUi

from driftai.utils import (
    get_ui_xml_path,
    get_ui_icon_path
)

class Animator:
    @staticmethod
    def animate(
        target,
        property_name,
        duration,
        start_value,
        end_value,
        easing_curve=QEasingCurve.Type.Linear
    ) -> QPropertyAnimation:

        animation = QPropertyAnimation(target, property_name.encode())
        animation.setDuration(duration)
        animation.setStartValue(start_value)
        animation.setEndValue(end_value)
        animation.setEasingCurve(easing_curve)
        animation.start()
        
        return animation

class FloatingWindow(QMainWindow):

    # window widgets declaration for intellisense suggestions
    quit_btn: QPushButton
    chat_btn: QPushButton
    speak_btn: QPushButton
    container_widget: QWidget

    def __init__(self, app: QApplication) -> None:
        QMainWindow.__init__(self)

        # QApplication object
        self.app = app

        # Window size
        self.window_width = 250
        self.window_height = 50

        # screen position padding
        self.screen_pad_x = 40
        self.screen_pad_y = 10

        # load the XML-UI created using the Qt6-designer
        self.ui_xml_path = get_ui_xml_path('floating_window_ui.ui')
        self.ui = loadUi(self.ui_xml_path, self)

        # set window flags and attributes
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # define button click events
        self.quit_btn.clicked.connect(self._exit_application)

        # set button icons
        self._set_button_icons()

        # calculate the screen appearance position
        self._appear_with_animation()
    
    def _set_button_icons(self) -> None:

        # quit button icon
        self._quit_icon = QPixmap(get_ui_icon_path('shutdown-icon.png'))
        self.quit_btn.setText("")
        self.quit_btn.setIcon(QIcon(self._quit_icon))
        self.quit_btn.setIconSize(QSize(64, 64))
    
    def _appear_with_animation(self) -> None:
        # Get screen geometry
        screen_geometry = QApplication.primaryScreen().geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        
        # Set initial position (bottom-right side of the screen)
        pos_x = int(screen_width - self.window_width - self.screen_pad_x)
        pos_y = int(screen_height - self.window_height - self.screen_pad_y)
        self.setGeometry(pos_x, pos_y, self.window_width, self.window_height)

        # Animation setup
        self._animation = QPropertyAnimation(self, b"size")
        self._animation.setDuration(500)
        self._animation.setStartValue(QSize(0, self.window_height))
        self._animation.setEndValue(QSize(self.window_width, self.window_height))
        self._animation.start()

        self._animation.finished.connect(self._set_button_widths)
    
    def _set_button_widths(self) -> None:
        w40 = int(self.window_width * 0.42)
        w20 = int(self.window_width * 0.16)
        btn_h = int((self.window_height - 10) * 0.80)

        self.quit_btn.setMinimumSize(w20, btn_h)
        self.quit_btn.setMaximumSize(w20, btn_h)

        self.chat_btn.setMinimumSize(w40, btn_h)
        self.speak_btn.setMinimumSize(w40, btn_h)
    
    def _exit_application(self) -> None:
        self.close()
        self.app.exit()
        
    
def test_floating_window():
    app = QApplication(sys.argv)
    window = FloatingWindow(app)
    window.show()
    sys.exit(
        app.exec()
    )
