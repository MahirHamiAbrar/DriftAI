import os
import time
import soundfile as sf
import sounddevice as sd
from typing import Generator
from .kokoro import KPipeline
from driftai.config import TTSConfig


class SpeechEngine(TTSConfig):
    def __init__(self) -> None:
        TTSConfig.__init__(self)

        # kokoro pipeline instance
        self._kokoro_pipeline = KPipeline(
            lang_code=self.lang_code,
            cache_dir=self.cache_dir,
            local_dir=self.local_dir
        )
    
    def generate_speech(self, text: str, live_play: bool = True, save_audio: bool = True) -> Generator:
        gen = self._kokoro_pipeline(
            text=text,
            voice=self.voice,
            speed=self.speed,
            split_pattern=r'{}'.format(self.split_pattern)
        )

        fname = str(time.time())

        for i, (gs, ps, audio) in enumerate(gen):
            fp = os.path.join(self.output_dir, f'{fname}_{i}.wav')

            if save_audio:
                sf.write(fp, audio, self.output_sample_rate)
            
            if live_play:
                sd.play(audio.numpy(), self.output_sample_rate)
                sd.wait()
