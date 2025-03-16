from kokoro import KPipeline
from driftai.config import TTSConfig


class SpeechEngine(TTSConfig):
    def __init__(self) -> None:
        TTSConfig.__init__(self)

        self._kokoro_model = KPipeline(
            lang_code='a'
        )


def test_speech_engine():
    engine = SpeechEngine()
