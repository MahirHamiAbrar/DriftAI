from driftai.models.text2speech import SpeechEngine

def test_speech_engine(text: str, live_play: bool = True, save_audio: bool = True):
    engine = SpeechEngine()
    engine.generate_speech(
        text,
        live_play=live_play, 
        save_audio=save_audio
    )