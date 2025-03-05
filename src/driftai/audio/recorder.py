import os
import wave
import logging
import pyaudio
import threading

from datetime import datetime
from pydub import AudioSegment
from driftai.config import RecorderConfig


class AudioRecorder(RecorderConfig):
    def __init__(
        self,
        chunk_duration: int = None
    ) -> None:
        """
        Initialize the audio recorder.
        
        Args:
            chunk_duration (int): Duration of each audio chunk in seconds.
        """
        RecorderConfig.__init__(self)

        if chunk_duration:
            self.chunk_duration = chunk_duration

        # thread variables
        self.is_recording = False
        self.audio_thread = None
        self.stop_event = threading.Event()
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def _record_audio(self) -> None:
        """Background thread function that records audio in chunks."""
        p = pyaudio.PyAudio()
        stream = p.open(format=self.sampling_format,
                        channels=self.channels,
                        rate=self.rate,
                        input=True,
                        frames_per_buffer=self.chunk_size)
        
        logging.info("Recording started...")
        
        while not self.stop_event.is_set():
            frames = []
            # Calculate how many chunks we need to record for our chunk_duration
            for _ in range(0, int(self.rate / self.chunk_size * self.chunk_duration)):
                if self.stop_event.is_set():
                    break
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                frames.append(data)
            
            if len(frames) > 0 and not self.stop_event.is_set():
                # Save the recorded chunk
                timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
                wave_filename = os.path.join(self.output_dir, f"chunk_{timestamp}.wav")
                mp3_filename = os.path.join(self.output_dir, f"chunk_{timestamp}.mp3")
                
                # Save as WAV first
                with wave.open(wave_filename, 'wb') as wf:
                    wf.setnchannels(self.channels)
                    wf.setsampwidth(p.get_sample_size(self.sampling_format))
                    wf.setframerate(self.rate)
                    wf.writeframes(b''.join(frames))
                
                # Convert to MP3 using pydub
                audio = AudioSegment.from_wav(wave_filename)
                audio.export(mp3_filename, format="mp3")
                
                # Remove the temporary WAV file
                os.remove(wave_filename)
                
                logging.info(f"Saved chunk: {mp3_filename}")
        
        # Clean up
        stream.stop_stream()
        stream.close()
        p.terminate()
        logging.info("Recording stopped.")
    
    def start_recording(self) -> bool:
        """Start recording audio in a separate thread."""
        if not self.is_recording:
            self.stop_event.clear()
            self.is_recording = True
            self.audio_thread = threading.Thread(target=self._record_audio)
            self.audio_thread.daemon = True
            self.audio_thread.start()
            return True
        return False
    
    def stop_recording(self) -> bool:
        """Stop the audio recording thread."""
        if self.is_recording:
            self.stop_event.set()
            if self.audio_thread:
                self.audio_thread.join(timeout=3.0)  # Wait for thread to finish
            self.is_recording = False
            return True
        return False
    
    def set_chunk_duration(self, duration) -> bool:
        """Set the duration of each audio chunk in seconds."""
        if not self.is_recording:
            self.chunk_duration = duration
            return True
        return False
