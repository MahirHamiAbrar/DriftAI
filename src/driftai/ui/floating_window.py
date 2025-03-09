import sys
import logging

from PyQt6.QtGui import (
    QIcon,
    QPixmap
)
from PyQt6.QtCore import (
    Qt,
    QRect,
    QSize,
    QPropertyAnimation
)
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QWidget,
    QPushButton,
    QMainWindow,
    QApplication
)
from PyQt6.uic.load_ui import loadUi
from driftai.utils import (
    get_ui_xml_path,
    get_ui_icon_path
)

from driftai.ui.audio_input_widget import AudioInputWidget


class FloatingWindow(QMainWindow):

    # window widgets declaration for intellisense suggestions
    quit_btn: QPushButton
    chat_btn: QPushButton
    speak_btn: QPushButton

    container_widget: QWidget
    inner_container_widget: QWidget
    audio_input_container_widget: QWidget

    def __init__(self, app: QApplication) -> None:
        QMainWindow.__init__(self)

        # QApplication object
        self.app = app

        # Window size
        self.window_width = 250
        self.window_height = 52

        # screen position padding
        self.screen_pad_x = 40
        self.screen_pad_y = 10

        # is the window expanded
        self._is_expanded = False
        self._expansion_offset = 200
        self._expansion_anim_duration = 300

        # setup and launch the UI
        self.setup_ui()
    
    def setup_ui(self) -> None:

        # load the XML-UI created using the Qt6-designer
        self.ui_xml_path = get_ui_xml_path('floating_window_ui.ui')
        self.ui = loadUi(self.ui_xml_path, self)

        # set window flags and attributes
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # create a layout in `audio_input_container_widget`
        self.input_container_layout = QHBoxLayout()
        self.audio_input_container_widget.setLayout(
            self.input_container_layout
        )

        # audio visualizer widget
        self._audio_in_widget = AudioInputWidget(
            parent=self.audio_input_container_widget,
            activate=False
        )
        self.input_container_layout.addWidget(
            self._audio_in_widget
        )

        # set window minimum height and width
        # self.setMinimumSize(self.window_width, self.window_height)

        self.inner_container_widget.setMaximumHeight(self.window_height)

        # define button click events
        self.quit_btn.clicked.connect(self._exit_application)
        self.speak_btn.clicked.connect(self._expand_or_collapse)

        self.audio_input_container_widget.hide()

        # set button icons
        self._set_button_icons()

        # calculate the screen appearance position
        self._launch_ui_with_animation()

        # create an info-log on startup
        logging.info("Floating Window Launched")
    
    def _set_button_icons(self) -> None:
        logging.debug('Setting button icons of floating window')

        # quit button icon
        self._quit_icon = QPixmap(get_ui_icon_path('shutdown-icon.png'))
        self.quit_btn.setText("")
        self.quit_btn.setIcon(QIcon(self._quit_icon))
        self.quit_btn.setIconSize(QSize(64, 64))
    
    def _set_button_widths(self) -> None:
        logging.debug('Setting floating window button sizes')
        
        w40 = int(self.window_width * 0.42)
        w20 = int(self.window_width * 0.16)
        btn_h = int((self.window_height - 10) * 0.80)

        self.quit_btn.setMinimumSize(w20, btn_h)
        self.quit_btn.setMaximumSize(w20, btn_h)

        self.chat_btn.setMinimumSize(w40, btn_h)
        self.speak_btn.setMinimumSize(w40, btn_h)
    
    def _launch_ui_with_animation(self) -> None:
        logging.debug('starting animation of floating window')

        # Get screen geometry
        screen_geometry = QApplication.primaryScreen().geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        
        # Set initial position (bottom-right side of the screen)
        self.pos_x = int(screen_width - self.window_width - self.screen_pad_x)
        self.pos_y = int(screen_height - self.window_height - self.screen_pad_y)
        self.setGeometry(self.pos_x, self.pos_y, self.window_width, self.window_height)

        # Animation setup
        self._animation = QPropertyAnimation(self, b"size")
        self._animation.setDuration(500)
        self._animation.setStartValue(QSize(0, self.window_height))
        self._animation.setEndValue(QSize(self.window_width, self.window_height))
        self._animation.start()

        self._animation.finished.connect(self._set_button_widths)
    
    def _exit_application(self) -> None:
        # create an info-log before quitting
        logging.info('Closing the floating window and quitting application')

        self.close()        # close window
        self.app.exit()     # and quit application
    
    def _expand_or_collapse(self) -> None:
        start_rect = self.geometry()
        
        if self._is_expanded:
            end_rect = QRect(
                start_rect.x(), 
                start_rect.y() + self._expansion_offset, 
                start_rect.width(), 
                start_rect.height() - self._expansion_offset
            )
        else:
            end_rect = QRect(
                start_rect.x(), 
                start_rect.y() - self._expansion_offset, 
                start_rect.width(), 
                start_rect.height() + self._expansion_offset
            )
            # hide the inner container widget for smoother animation 
            self.inner_container_widget.hide()
            self._audio_in_widget.hide()

        # animate the window
        self._window_animation = QPropertyAnimation(self, b"geometry")
        self._window_animation.setDuration(self._expansion_anim_duration)
        self._window_animation.setStartValue(start_rect)
        self._window_animation.setEndValue(end_rect)
        self._window_animation.start()

        # unhide the inner container widget after animation is finished
        self._window_animation.finished.connect(
            self._on_window_extended
        )
        
        # alter the expanded status
        self._is_expanded = not self._is_expanded
    
    def _on_window_extended(self) -> None:
        if self._is_expanded:
            self.inner_container_widget.show()
            self.audio_input_container_widget.show()
            self._audio_in_widget.show()
            self._audio_in_widget.activate()
        else:
            # self._audio_in_widget.deactivate()
            self._audio_in_widget.hide()
            self.audio_input_container_widget.hide()
            self.inner_container_widget.show()
        
    
def test_run_floating_window():
    app = QApplication(sys.argv)
    window = FloatingWindow(app)
    window.show()
    sys.exit(
        app.exec()
    )
