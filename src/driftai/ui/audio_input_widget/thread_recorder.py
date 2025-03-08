import os
import wave
import time
import pyaudio
import datetime
import numpy as np

from driftai.config import RecorderConfig

from PyQt6.QtCore import pyqtSignal, QThread
from PyQt6.QtWidgets import QWidget, QMainWindow


class ThreadAudioRecorder(QThread, RecorderConfig):
    update_visualizer = pyqtSignal(np.ndarray)
    
    def __init__(
            self,
            parent: QWidget | QMainWindow = None,
            audio_config: dict = None,
        ) -> None:

        QThread.__init__(self, parent)
        RecorderConfig.__init__(self)

        super().__init__(parent)

        self.p = pyaudio.PyAudio()
        
        self.frames = []
        self.stream = None
        self.is_running = True
        self.is_recording = False
        self.visualizer_active = True
    
    def set_audio_config(self, config: dict) -> None:
        self._config = config
        
    def run(self) -> None:
        self.stream = self.p.open(
            format=self.sampling_format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        while self.is_running:
            data = self.stream.read(
                self.chunk_size,
                exception_on_overflow=False
            )
            audio_data = np.frombuffer(data, dtype=np.int16)
            
            if self.visualizer_active:
                self.update_visualizer.emit(audio_data)
            
            if self.is_recording:
                self.frames.append(data)
            
            time.sleep(0.001)  # Small delay to prevent CPU overuse
    
    def toggle_recording(self) -> bool:
        self.is_recording = not self.is_recording
        if not self.is_recording and self.frames:
            return True
        return False
    
    def save_recording(self) -> bool:
        if not self.frames:
            return False
        
        timestamp = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        filename = os.path.join(self.output_dir, f"chunk_{timestamp}.wav")
            
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(
                self.p.get_sample_size(self.sampling_format)
            )
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.frames))
        
        self.frames = []
        return True
    
    def clear_recording(self) -> None:
        self.frames = []
    
    def set_visualizer_active(self, active) -> None:
        self.visualizer_active = active
    
    def stop(self) -> None:
        self.is_running = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()
