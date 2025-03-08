import os
import pygame
import librosa
import numpy as np

from pygame import mixer
from driftai.ui.opengl_3d_visualizer_widget import OpenGL3DVisualizerWidget

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import (
    QPushButton, QWidget, QLabel, QSlider, QComboBox, 
    QVBoxLayout, QHBoxLayout, QFileDialog
)


class AudioVisualizerWidget3D(QWidget):
    def __init__(self) -> None:
        super().__init__()
        
        # Initialize pygame mixer
        pygame.init()
        mixer.init()
        
        # Create central widget and layout
        main_layout = QVBoxLayout(self)
        
        # Create OpenGL widget for visualization
        self.gl_widget = OpenGL3DVisualizerWidget(self)
        self.gl_widget.setMaximumSize(350, 180)
        main_layout.addWidget(self.gl_widget)
        
        # Create control panel
        control_layout = QHBoxLayout()
        
        # Play/Pause button
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.toggle_playback)
        control_layout.addWidget(self.play_button)
        
        # Open file button
        open_button = QPushButton("Open File")
        open_button.clicked.connect(self.open_file)
        control_layout.addWidget(open_button)
        
        # Color mode selector
        color_label = QLabel("Color Theme:")
        control_layout.addWidget(color_label)
        
        self.color_mode_combo = QComboBox()
        self.color_mode_combo.addItems(["Rainbow", "Spectrum", "Fire", "Ocean", "Candy"])
        self.color_mode_combo.currentTextChanged.connect(self.change_color_mode)
        control_layout.addWidget(self.color_mode_combo)
        
        # Volume slider
        volume_label = QLabel("Volume:")
        control_layout.addWidget(volume_label)
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(70)
        self.volume_slider.valueChanged.connect(self.change_volume)
        control_layout.addWidget(self.volume_slider)
        
        # Now playing label
        self.playing_label = QLabel("No file loaded")
        control_layout.addWidget(self.playing_label)
        
        main_layout.addLayout(control_layout)
        
        # Initialize variables
        self.current_file = None
        self.playing = False
        self.audio_data = None
        self.sample_rate = None
        
        # Set up timer for updating visualization
        self.timer = QTimer(self)
        self.timer.setInterval(25)  # Update every 25ms for smoother animation
        self.timer.timeout.connect(self.update_visualization)
        
        # Initialize volume
        self.change_volume(70)
    
    def change_color_mode(self, mode):
        self.gl_widget.set_color_mode(mode.lower())
    
    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Audio File", "", "Audio Files (*.mp3 *.wav)"
        )
        
        if file_path:
            # Stop current playback if any
            if self.playing:
                self.toggle_playback()
            
            # Load audio file
            self.current_file = file_path
            self.playing_label.setText(os.path.basename(file_path))
            
            # Load audio data for visualization
            self.audio_data, self.sample_rate = librosa.load(file_path, sr=None)
            
            # Prepare the audio for playback
            mixer.music.load(file_path)
            
            # Start playback
            self.toggle_playback()
    
    def toggle_playback(self):
        if not self.current_file:
            return
        
        if self.playing:
            mixer.music.pause()
            self.play_button.setText("Play")
            self.timer.stop()
        else:
            mixer.music.play()
            self.play_button.setText("Pause")
            self.timer.start()
        
        self.playing = not self.playing
    
    def change_volume(self, value):
        volume = value / 100.0
        mixer.music.set_volume(volume)
    
    def update_visualization(self):
        if not self.playing or self.audio_data is None:
            return
        
        # Get current playback position
        pos = mixer.music.get_pos() / 1000.0  # Convert to seconds
        
        # Sometimes get_pos returns -1, handle this case
        if pos < 0:
            return
        
        # Calculate frame index
        frame_index = int(pos * self.sample_rate)
        
        # Make sure we don't go out of bounds
        if frame_index >= len(self.audio_data):
            return
        
        # Get a window of audio data
        window_size = 1024
        if frame_index + window_size > len(self.audio_data):
            window = self.audio_data[frame_index:]
        else:
            window = self.audio_data[frame_index:frame_index + window_size]
        
        # FFT for frequency domain visualization
        spectrum = np.fft.fft(window)
        magnitude = np.abs(spectrum[:window_size//2])
        
        # Apply log scaling for better visualization
        magnitude = np.log10(magnitude + 1)
        
        # Normalize magnitude for better visualization
        magnitude = magnitude / np.max(magnitude) if np.max(magnitude) > 0 else magnitude
        
        # Downsample for smoother visualization
        spectrum_data = self.downsample(magnitude, 64)
        waveform_data = self.downsample(window, 128)
        
        # Update OpenGL widget with new data
        self.gl_widget.update_data(spectrum_data, waveform_data)
    
    def downsample(self, data, target_size):
        """Downsample the data to target_size using average pooling"""
        if len(data) <= target_size:
            return data
        
        result = np.zeros(target_size)
        ratio = len(data) / target_size
        
        for i in range(target_size):
            start = int(i * ratio)
            end = int((i + 1) * ratio)
            result[i] = np.mean(data[start:end])
        
        return result


def test_run_widget():
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    widget = AudioVisualizerWidget3D()
    widget.show()
    sys.exit(app.exec())
