from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.uic.load_ui import loadUi

from driftai.utils import get_ui_xml_path
from .thread_recorder import ThreadAudioRecorder
from .visualizer_widget import AudioVisualizerWidget


class AudioInputWidget(QWidget):
    record_btn: QPushButton
    audio_visualizer_widget: QWidget

    def __init__(
        self,
        parent: QWidget | QMainWindow = None,
        activate: bool = True
    ) -> None:
        super().__init__(parent)

        # audio recorder that will run parallaly on different thread
        self._recorder = ThreadAudioRecorder()
        self._recorder.update_visualizer.connect(self.update_visualizer)

        # load and setup the UI first
        self.setup_ui()

        # start the audio recorder
        self._recorder.start()
    
    def activate(self) -> None:
        self._recorder.start()
    
    def setup_ui(self) -> None:
        # load the XML-UI created using the Qt6-designer
        self.ui_xml_path = get_ui_xml_path('audio_input_widget_ui.ui')
        self.ui = loadUi(self.ui_xml_path, self)
        
        visualizer_layout = QVBoxLayout()
        self.audio_visualizer_widget.setLayout(visualizer_layout)

        # Visualizer
        self._visualizer = AudioVisualizerWidget(chunk_size=1024)
        visualizer_layout.addWidget(self._visualizer)

        self.record_btn.clicked.connect(self.toggle_recording)
    
    def update_visualizer(self, data) -> None:
        self._visualizer.set_data(data)
    
    def toggle_recording(self):
        if self._recorder.toggle_recording():
            # stopped recording
            self.record_btn.setText("Click to Speak")
            self._visualizer.set_recording_state(False)
            self.record_btn.setStyleSheet('')

            # save the recording
            self._recorder.save_recording()
        else:
            # started recording
            self.record_btn.setText("Stop Recording")
            self.record_btn.setStyleSheet('background-color: rgba(255, 150, 0, 50); color: rgb(255, 150, 0);')
            self._visualizer.set_recording_state(True)
    
    def closeEvent(self, event) -> None:
        self.hide()
        self._recorder.stop()
        self._recorder.wait()
        event.accept()


def test_run_audio_input_widget() -> None:
    import sys

    app = QApplication(sys.argv)
    widget = AudioInputWidget()
    widget.show()
    sys.exit(app.exec())