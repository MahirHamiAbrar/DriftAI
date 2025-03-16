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
    
    def generate_speech(self, text: str) -> Generator:
        gen = self._kokoro_pipeline(
            text=text,
            voice=self.voice,
            speed=self.speed,
            split_pattern=r'{}'.format(self.split_pattern)
        )

        for (gs, ps, audio) in gen:
            sd.play(audio, 24000)
