import os
import wave
import pyaudio
import threading

from datetime import datetime
from pydub import AudioSegment
from driftai.config import RecorderConfig


class AudioRecorder:
    def __init__(self, chunk_duration=2, output_dir="recordings") -> None:
        """
        Initialize the audio recorder.
        
        Args:
            chunk_duration (int): Duration of each audio chunk in seconds.
            output_dir (str): Directory to save the audio chunks.
        """
        self.chunk_duration = chunk_duration
        self.output_dir = output_dir
        self.is_recording = False
        self.audio_thread = None
        self.stop_event = threading.Event()
        
        # Audio parameters
        self.format = pyaudio.paInt16
        self.channels = 2
        self.rate = 44100
        self.chunk_size = 1024
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def _record_audio(self) -> None:
        """Background thread function that records audio in chunks."""
        p = pyaudio.PyAudio()
        stream = p.open(format=self.format,
                        channels=self.channels,
                        rate=self.rate,
                        input=True,
                        frames_per_buffer=self.chunk_size)
        
        print("Recording started...")
        
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
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                wave_filename = os.path.join(self.output_dir, f"chunk_{timestamp}.wav")
                mp3_filename = os.path.join(self.output_dir, f"chunk_{timestamp}.mp3")
                
                # Save as WAV first
                wf = wave.open(wave_filename, 'wb')
                wf.setnchannels(self.channels)
                wf.setsampwidth(p.get_sample_size(self.format))
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(frames))
                wf.close()
                
                # Convert to MP3 using pydub
                audio = AudioSegment.from_wav(wave_filename)
                audio.export(mp3_filename, format="mp3")
                
                # Remove the temporary WAV file
                os.remove(wave_filename)
                
                print(f"Saved chunk: {mp3_filename}")
        
        # Clean up
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("Recording stopped.")
    
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

def main() -> None:
    chunk_duration = 5
    try:
        user_duration = input("Enter chunk duration in seconds (default is 2): ")
        if user_duration.strip():
            chunk_duration = float(user_duration)
    except ValueError:
        print("Invalid input. Using default 2 seconds.")
    
    recorder = AudioRecorder(chunk_duration=chunk_duration)
    recorder.start_recording()
    
    print(f"Audio recording has started in the background with {chunk_duration} second chunks.")
    print("Type 'stop' to stop recording.")
    
    try:
        while True:
            user_input = input("> ").strip().lower()
            if user_input == "stop":
                print("Stopping the recording...")
                recorder.stop_recording()
                break
            elif user_input == "help":
                print("Commands available:")
                print("  stop - Stop recording and exit")
                print("  help - Show this help message")
            else:
                print(f"Unknown command: {user_input}. Type 'help' for available commands.")
    except KeyboardInterrupt:
        print("\nInterrupted by user. Stopping recording...")
        recorder.stop_recording()
    
    print("Program exited.")

if __name__ == "__main__":
    main()