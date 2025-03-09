import whisper  

device = "cuda" 
audio_file = "/WindowsDrive/DriftResearch/lib/python3.10/mhabrar_research/DriftAI/tts_test/kokoro_1.wav"
audio_file = "/WindowsDrive/DriftResearch/lib/python3.10/mhabrar_research/DriftAI/stt_test/topgun_maverick.mp3"

model = whisper.load_model(
    # name="large-v3",
    name="turbo",
    device=device,
    download_root="/WindowsDrive/LLM/Whisper"
)  # Change to "medium" or "large" if needed

result = model.transcribe(
    audio=audio_file,
    temperature=0.8,
    word_timestamps=True
)  

print(result)


class WhisperTranscriptor:
    def __init__(self) -> None:
        pass
