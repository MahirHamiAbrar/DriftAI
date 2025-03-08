from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from PyQt6.uic.load_ui import loadUi
from driftai.utils import (
    get_ui_xml_path,
    get_ui_icon_path
)
from driftai.ui import Animator


class ChatWidget(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)

        # hide the widget
        # self.hide()

        # load the XML-UI created using the Qt6-designer
        self.ui_xml_path = get_ui_xml_path('chat_ui.ui')
        self.ui = loadUi(self.ui_xml_path, self)

        # self._opacity_animator = Animator.animate(
        #     self,
        #     'opacity',
        #     1000,
        #     0.0,
        #     1.0
        # )

        self.b = QPushButton("Reduce", self, clicked=self.reduce)
        self.b.setStyleSheet("background: blue; color: yellow;")
        
        layout = QVBoxLayout(self)
        # layout.addWidget(self.label)
        layout.addWidget(self.b)

    def reduce(self):
        self.anim = QPropertyAnimation(self, b"opacity")
        self.anim.setDuration(3000)        
        self.anim.setLoopCount(3)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)        
        self.anim.start()
            
    def windowOpacity(self):
        return super().windowOpacity()    
    
    def setWindowOpacity(self, opacity):
        super().setWindowOpacity(opacity)    
    
    opacity = pyqtProperty(float, windowOpacity, setWindowOpacity)


def run_test_chat_widget() -> None:
    import sys

    app = QApplication(sys.argv)
    widget = ChatWidget()
    widget.show()
    sys.exit(app.exec())

