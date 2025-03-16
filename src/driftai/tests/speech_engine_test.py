from driftai.models.text2speech import SpeechEngine

def test_speech_engine(text: str):
    engine = SpeechEngine()
    engine.generate_speech(text)