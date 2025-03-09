import numpy as np
from enum import Enum
from PyQt6.QtWidgets import QMainWindow, QWidget
from PyQt6.QtGui import (
    QPen, QFont, QBrush, QColor, QPainter, QLinearGradient, QPainterPath
)
from PyQt6.QtCore import Qt, QRectF


class AudioVisualizerType(Enum):
    Linear = 0
    Sinusoidal = 1


class AudioVisualizerWidget(QWidget):
    def __init__(self, chunk_size: int, parent: QWidget | QMainWindow=None) -> None:
        super().__init__(parent)

        self.audio_chunk_size = chunk_size

        self.setMinimumHeight(70)
        self.setStyleSheet('border-radius: 10px;')

        self.is_recording = False
        self.audio_data = np.zeros(self.audio_chunk_size)
        self.visualizer_type = AudioVisualizerType.Linear

        # self.set_data(np.random)
        
    def set_data(self, data) -> None:
        self.audio_data = data
        self.update()
        
    def set_recording_state(self, is_recording) -> None:
        self.is_recording = is_recording
        self.update()
        
    def set_visualizer_type(self, visualizer_type) -> None:
        self.visualizer_type = visualizer_type
        self.update()
    
    def draw_round_rect(self, event, width, height):
        # Create the painter
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Create the path
        path = QPainterPath()
        # Set painter colors to given values.
        pen = QPen(QColor(41, 41, 43), 2.0)
        painter.setPen(pen)
        brush = QBrush(QColor(20, 20, 30))
        painter.setBrush(brush)

        self.bordersize = 8.0
        self.border_radius = 15

        rect = QRectF(event.rect())
        # Slighly shrink dimensions to account for bordersize.
        # rect.adjust(self.bordersize/2, self.bordersize/2, -self.bordersize/2, -self.bordersize/2)

        # Add the rect to path.
        path.addRoundedRect(rect, self.border_radius, self.border_radius)
        painter.setClipPath(path)

        # Fill shape, draw the border and center the text.
        painter.fillPath(path, painter.brush())
        painter.strokePath(path, painter.pen())
        # painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, 'self.text()')
        
    def paintEvent(self, event) -> None:
        self.draw_round_rect(event, self.width(), self.height())

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        # Background
        # painter.fillRect(0, 0, width, height, QColor(20, 20, 30))
        
        if len(self.audio_data) == 0:
            return
            
        # Create gradient based on recording state
        if self.is_recording:
            # Bluish theme when recording
            gradient = QLinearGradient(0, 0, 0, height)
            gradient.setColorAt(0, QColor(0, 200, 255, 180))
            gradient.setColorAt(1, QColor(0, 100, 200, 180))
        else:
            # Orange theme when not recording
            gradient = QLinearGradient(0, 0, 0, height)
            gradient.setColorAt(0, QColor(255, 150, 0, 180))
            gradient.setColorAt(1, QColor(200, 70, 0, 180))
        
        pen = QPen(QBrush(gradient), 2)
        painter.setPen(pen)
        
        # Normalize audio data for visualization
        normalized_data = self.audio_data / 32768.0  # Normalize to [-1, 1]
        
        if self.visualizer_type == AudioVisualizerType.Linear:
            # Linear visualization
            points_per_pixel = len(normalized_data) / width
            pixel_values = []
            
            for i in range(width):
                start = int(i * points_per_pixel)
                end = int((i + 1) * points_per_pixel)
                if start >= len(normalized_data):
                    start = len(normalized_data) - 1
                if end >= len(normalized_data):
                    end = len(normalized_data) - 1
                    
                if start == end:
                    val = abs(normalized_data[start])
                else:
                    val = np.max(np.abs(normalized_data[start:end]))
                pixel_values.append(val)
            
            for i in range(width):
                amp = pixel_values[i] * height/2
                painter.drawLine(i, int(height/2 - amp), i, int(height/2 + amp))
        
        elif self.visualizer_type == AudioVisualizerType.Sinusoidal:
            # Sinusoidal visualization
            points = []
            points_per_pixel = len(normalized_data) / width
            
            for i in range(width):
                idx = int(i * points_per_pixel)
                if idx >= len(normalized_data):
                    idx = len(normalized_data) - 1
                
                # Scale the amplitude
                amp = normalized_data[idx] * height/2
                points.append((i, int(height/2 - amp)))
            
            for i in range(1, len(points)):
                painter.drawLine(points[i-1][0], points[i-1][1], points[i][0], points[i][1])
        
        # Draw label
        if self.is_recording:
            painter.setFont(QFont("Arial", 10))
            painter.setPen(QColor(0, 200, 255))
            painter.drawText(10, 20, "RECORDING...")
        else:
            painter.setFont(QFont("Arial", 10))
            painter.setPen(QColor(255, 150, 0))
            painter.drawText(10, 20, "STANDBY")
