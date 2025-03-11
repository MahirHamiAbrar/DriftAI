import sys
import json
import time
import requests
from pathlib import Path
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QUrl, QPropertyAnimation, 
    QEasingCurve, QSize, pyqtProperty, QTimer
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QPushButton, QTextEdit, QLabel, QFileDialog, QWidget,
    QProgressBar, QMessageBox, QFrame, QSizePolicy, QSpacerItem,
    QGraphicsOpacityEffect, QStackedWidget
)
from PyQt6.QtGui import (
    QDesktopServices, QColor, QPalette, QFont, 
    QFontDatabase, QIcon, QPixmap
)

# Modern dark theme colors
class Theme:
    # Main colors
    PRIMARY = "#6366F1"      # Indigo
    SECONDARY = "#4F46E5"    # Darker indigo
    BACKGROUND = "#1E1E2E"   # Dark background
    SURFACE = "#2A2A3C"      # Slightly lighter surface
    ERROR = "#EF4444"        # Red
    SUCCESS = "#10B981"      # Green
    WARNING = "#F59E0B"      # Amber
    INFO = "#3B82F6"         # Blue
    
    # Text colors
    TEXT_PRIMARY = "#FFFFFF"
    TEXT_SECONDARY = "#A0A0B0"
    
    # Border and divider
    BORDER = "#383850"
    
    # Button states
    BUTTON_HOVER = "#4F46E5"
    BUTTON_PRESSED = "#4338CA"
    BUTTON_DISABLED = "#4B5563"

class AnimatedProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._animation = QPropertyAnimation(self, b"value")
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.setDuration(800)
        
    def setAnimatedValue(self, value):
        self._animation.stop()
        self._animation.setStartValue(self.value())
        self._animation.setEndValue(value)
        self._animation.start()

class PulsatingButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._effect)
        self._effect.setOpacity(1.0)
        
        self._animation = QPropertyAnimation(self._effect, b"opacity")
        self._animation.setDuration(1200)
        self._animation.setStartValue(1.0)
        self._animation.setEndValue(0.7)
        self._animation.setLoopCount(-1)  # Infinite loop
        self._animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
    def startPulsating(self):
        self._animation.start()
        
    def stopPulsating(self):
        self._animation.stop()
        self._effect.setOpacity(1.0)

class StyledFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"""
            StyledFrame {{
                background-color: {Theme.SURFACE};
                border-radius: 8px;
                border: 1px solid {Theme.BORDER};
            }}
        """)
        self.setContentsMargins(16, 16, 16, 16)

class ModelLoaderThread(QThread):
    update_signal = pyqtSignal(int)
    
    def __init__(self, server_url):
        super().__init__()
        self.server_url = server_url
        
    def run(self):
        try:
            response = requests.post(f"{self.server_url}/stt/load_model")
            if response.status_code == 200:
                while True:
                    status_response = requests.get(f"{self.server_url}/stt/model_status")
                    status_data = status_response.json()
                    current_status = status_data.get("status", 0)
                    self.update_signal.emit(current_status)
                    
                    if current_status == 2:  # Model is loaded
                        break
                    time.sleep(1)
        except Exception as e:
            print(f"Error in model loading thread: {e}")
            self.update_signal.emit(-1)  # Signal error

class TranscriptionThread(QThread):
    update_signal = pyqtSignal(dict)
    
    def __init__(self, server_url, audio_file):
        super().__init__()
        self.server_url = server_url
        self.audio_file = audio_file
        self.job_id = None
        
    def run(self):
        try:
            payload = {"audio_file": self.audio_file}
            response = requests.post(f"{self.server_url}/stt/transcribe/", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.job_id = data.get("job_id")
                self.update_signal.emit(data)
                
                while True:
                    status_response = requests.get(f"{self.server_url}/stt/transcription_status/{self.job_id}")
                    status_data = status_response.json()
                    self.update_signal.emit(status_data)
                    
                    if status_data.get("status") == 11:  # Transcription complete
                        break
                    time.sleep(1)
        except Exception as e:
            print(f"Error in transcription thread: {e}")
            self.update_signal.emit({"error": str(e)})

class WhisperClientApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.server_url = "http://127.0.0.1:8000"
        self.selected_file = None
        self.model_loaded = False
        
        # Setup UI
        self.applyFonts()
        self.setupUI()
        self.applyStyles()
        
        # Initialize animation properties
        self.setupAnimations()
        
    def applyFonts(self):
        # Modern font setup
        QFontDatabase.addApplicationFont(":/fonts/Inter-Regular.ttf")
        QFontDatabase.addApplicationFont(":/fonts/Inter-Bold.ttf")
        
        self.app_font = QFont("Inter", 10)
        self.app_font_bold = QFont("Inter", 10, QFont.Weight.Bold)
        self.heading_font = QFont("Inter", 14, QFont.Weight.Bold)
        QApplication.setFont(self.app_font)
        
    def setupUI(self):
        self.setWindowTitle("Whisper Transcription Client")
        self.setGeometry(100, 100, 900, 700)
        
        # Central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(24, 24, 24, 24)
        self.setCentralWidget(central_widget)
        
        # Header section
        header_frame = StyledFrame()
        header_layout = QVBoxLayout(header_frame)
        
        app_title = QLabel("Whisper Transcription Client")
        app_title.setFont(self.heading_font)
        header_layout.addWidget(app_title)
        
        self.status_label = QLabel("Status: Model not loaded")
        self.status_label.setStyleSheet(f"color: {Theme.TEXT_SECONDARY};")
        header_layout.addWidget(self.status_label)
        
        main_layout.addWidget(header_frame)
        
        # Model loading section
        model_frame = StyledFrame()
        model_layout = QVBoxLayout(model_frame)
        
        model_header = QHBoxLayout()
        model_title = QLabel("Model Status")
        model_title.setFont(self.app_font_bold)
        
        self.load_model_btn = PulsatingButton("Load Model")
        self.load_model_btn.clicked.connect(self.load_model)
        self.load_model_btn.startPulsating()
        
        model_header.addWidget(model_title)
        model_header.addStretch()
        model_header.addWidget(self.load_model_btn)
        model_layout.addLayout(model_header)
        
        # Progress bar with animation
        self.progress_bar = AnimatedProgressBar()
        self.progress_bar.setRange(0, 2)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%v/2 - %p%")
        model_layout.addWidget(self.progress_bar)
        
        main_layout.addWidget(model_frame)
        
        # File selection section
        file_frame = StyledFrame()
        file_layout = QVBoxLayout(file_frame)
        
        file_header = QHBoxLayout()
        file_title = QLabel("Audio File")
        file_title.setFont(self.app_font_bold)
        
        self.browse_btn = QPushButton("Browse Audio")
        self.browse_btn.clicked.connect(self.browse_file)
        self.browse_btn.setEnabled(False)
        
        file_header.addWidget(file_title)
        file_header.addStretch()
        file_header.addWidget(self.browse_btn)
        file_layout.addLayout(file_header)
        
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; padding: 8px;")
        file_layout.addWidget(self.file_label)
        
        main_layout.addWidget(file_frame)
        
        # Transcription section
        transcription_frame = StyledFrame()
        transcription_layout = QVBoxLayout(transcription_frame)
        
        transcription_header = QHBoxLayout()
        transcription_title = QLabel("Transcription")
        transcription_title.setFont(self.app_font_bold)
        
        self.transcribe_btn = QPushButton("Transcribe Audio")
        self.transcribe_btn.clicked.connect(self.transcribe_audio)
        self.transcribe_btn.setEnabled(False)
        
        transcription_header.addWidget(transcription_title)
        transcription_header.addStretch()
        transcription_header.addWidget(self.transcribe_btn)
        transcription_layout.addLayout(transcription_header)
        
        # Results section
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMinimumHeight(250)
        transcription_layout.addWidget(self.results_text)
        
        main_layout.addWidget(transcription_frame)
        
        # Status bar for additional info
        self.statusBar().showMessage("Ready")
        
    def applyStyles(self):
        # Apply theme colors to the whole application
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {Theme.BACKGROUND};
                color: {Theme.TEXT_PRIMARY};
            }}
            
            QPushButton {{
                background-color: {Theme.PRIMARY};
                color: {Theme.TEXT_PRIMARY};
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: bold;
            }}
            
            QPushButton:hover {{
                background-color: {Theme.BUTTON_HOVER};
            }}
            
            QPushButton:pressed {{
                background-color: {Theme.BUTTON_PRESSED};
            }}
            
            QPushButton:disabled {{
                background-color: {Theme.BUTTON_DISABLED};
                color: {Theme.TEXT_SECONDARY};
            }}
            
            QProgressBar {{
                border: none;
                border-radius: 4px;
                background-color: {Theme.BORDER};
                text-align: center;
                height: 10px;
                margin: 8px 0;
            }}
            
            QProgressBar::chunk {{
                background-color: {Theme.SUCCESS};
                border-radius: 4px;
            }}
            
            QTextEdit {{
                background-color: {Theme.SURFACE};
                border: 1px solid {Theme.BORDER};
                border-radius: 6px;
                padding: 10px;
                selection-background-color: {Theme.PRIMARY};
            }}
            
            QStatusBar {{
                background-color: {Theme.SURFACE};
                color: {Theme.TEXT_SECONDARY};
            }}
            
            QLabel {{
                color: {Theme.TEXT_PRIMARY};
            }}
        """)
        
    def setupAnimations(self):
        # Create opacity effects for widgets to animate them
        self.file_opacity = QGraphicsOpacityEffect(self.file_label)
        self.file_label.setGraphicsEffect(self.file_opacity)
        
        self.results_opacity = QGraphicsOpacityEffect(self.results_text)
        self.results_text.setGraphicsEffect(self.results_opacity)
        
    def fadeIn(self, widget):
        opacity_effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(opacity_effect)
        
        self.fade_animation = QPropertyAnimation(opacity_effect, b"opacity")
        self.fade_animation.setDuration(500)
        self.fade_animation.setStartValue(0)
        self.fade_animation.setEndValue(1)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.fade_animation.start()
    
    def closeEvent(self, event):
        if self.model_loaded:
            reply = QMessageBox.question(
                self, 'Confirm Exit',
                "Do you want to exit? The model will be unloaded.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Show unloading message
                self.statusBar().showMessage("Unloading model...")
                
                try:
                    requests.post(f"{self.server_url}/stt/unload_model/")
                    self.statusBar().showMessage("Model unloaded successfully")
                    QTimer.singleShot(500, lambda: event.accept())
                except Exception as e:
                    print(f"Error unloading model: {e}")
                    self.statusBar().showMessage(f"Error: {str(e)}")
                    event.accept()
            else:
                event.ignore()
        else:
            event.accept()
    
    def load_model(self):
        self.load_model_btn.setEnabled(False)
        self.load_model_btn.stopPulsating()
        self.status_label.setText("Status: Requesting model load...")
        self.statusBar().showMessage("Connecting to server...")
        
        # Create and start the loader thread
        self.loader_thread = ModelLoaderThread(self.server_url)
        self.loader_thread.update_signal.connect(self.update_model_status)
        self.loader_thread.start()
    
    def update_model_status(self, status):
        if status == -1:
            self.status_label.setText("Status: Error loading model")
            self.statusBar().showMessage("Connection error. Please check server status.")
            self.load_model_btn.setEnabled(True)
            self.load_model_btn.startPulsating()
            return
            
        self.progress_bar.setAnimatedValue(status)
        
        status_text = {
            0: "Model not loaded",
            1: "Model loading...",
            2: "Model loaded and ready"
        }.get(status, "Unknown status")
        
        self.status_label.setText(f"Status: {status_text}")
        self.statusBar().showMessage(f"Model status: {status_text}")
        
        if status == 2:
            self.model_loaded = True
            self.load_model_btn.setEnabled(False)
            self.browse_btn.setEnabled(True)
            
            # Animate the transition
            QTimer.singleShot(300, lambda: self.fadeIn(self.browse_btn))
            
            # Enable transcribe button if a file is already selected
            if self.selected_file:
                self.transcribe_btn.setEnabled(True)
    
    def browse_file(self):
        file_dialog = QFileDialog()
        file_dialog.setWindowTitle("Select Audio File")
        file_dialog.setNameFilter("Audio Files (*.mp3 *.wav)")
        file_dialog.setViewMode(QFileDialog.ViewMode.List)
        
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            self.selected_file = file_path
            
            # Show only the file name, not the full path
            file_name = Path(file_path).name
            self.file_label.setText(f"Selected: {file_name}")
            
            # Animate the file label
            self.fadeIn(self.file_label)
            
            # Enable transcribe button if model is loaded
            if self.model_loaded:
                self.transcribe_btn.setEnabled(True)
                self.fadeIn(self.transcribe_btn)
    
    def transcribe_audio(self):
        if not self.selected_file:
            QMessageBox.warning(self, "Warning", "Please select an audio file first.")
            return
        
        self.transcribe_btn.setEnabled(False)
        self.results_text.clear()
        self.results_text.setText("Starting transcription...")
        self.statusBar().showMessage("Preparing transcription request...")
        
        # Extract just the filename from the path
        file_name = Path(self.selected_file).name
        
        # Create and start the transcription thread
        self.transcription_thread = TranscriptionThread(self.server_url, file_name)
        self.transcription_thread.update_signal.connect(self.update_transcription_status)
        self.transcription_thread.start()
    
    def update_transcription_status(self, data):
        if "error" in data:
            self.results_text.setHtml(f"<span style='color:{Theme.ERROR}'>Error: {data['error']}</span>")
            self.transcribe_btn.setEnabled(True)
            self.statusBar().showMessage("Transcription failed")
            return
            
        job_id = data.get("job_id", "Unknown")
        status = data.get("status")
        audio_file = data.get("audio_file", "Unknown")
        result = data.get("result")
        
        status_text = {
            10: "Processing",
            11: "Complete"
        }.get(status, "Unknown")
        
        status_html = f"""
            <h3 style='color:{Theme.TEXT_PRIMARY}'>Transcription Status</h3>
            <p><b>Job ID:</b> {job_id}</p>
            <p><b>Status:</b> <span style='color:{Theme.SUCCESS if status == 11 else Theme.INFO}'>{status_text}</span></p>
            <p><b>Audio File:</b> {audio_file}</p>
        """
        
        if status == 10:
            status_html += "<p><b>Progress:</b> Transcribing audio... please wait</p>"
            self.statusBar().showMessage(f"Transcription in progress: {audio_file}")
        
        self.results_text.setHtml(status_html)
        
        if status == 11 and result:
            self.statusBar().showMessage("Transcription complete!")
            
            # Add a small delay for visual effect
            QTimer.singleShot(300, lambda: self.display_results(result))
                
    def display_results(self, result):
        # Get current HTML content
        current_html = self.results_text.toHtml()
        
        # Add the result with nice formatting
        result_html = current_html + "<h3 style='color:{0}; margin-top:20px;'>Transcription Result:</h3>".format(Theme.SUCCESS)
        
        if isinstance(result, dict):
            # Format the dictionary as pretty JSON with syntax highlighting
            formatted_json = json.dumps(result, indent=2)
            result_html += "<pre style='background-color:{0}; padding:10px; border-radius:4px; overflow:auto'>".format(Theme.SURFACE)
            
            # Simple syntax highlighting for JSON
            for line in formatted_json.split('\n'):
                # Highlight keys
                if ":" in line:
                    key_part = line.split(':', 1)[0]
                    val_part = line.split(':', 1)[1]
                    line = f"<span style='color:#F59E0B'>{key_part}</span>:{val_part}"
                result_html += line + "<br>"
            
            result_html += "</pre>"
        else:
            result_html += f"<pre>{str(result)}</pre>"
        
        self.results_text.setHtml(result_html)
        self.fadeIn(self.results_text)
        self.transcribe_btn.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WhisperClientApp()
    window.show()
    sys.exit(app.exec())