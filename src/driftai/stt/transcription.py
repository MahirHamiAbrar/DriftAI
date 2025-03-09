import whisper
import logging

from torch import Tensor
from numpy import ndarray

from typing import List, Literal
from driftai.config import STTConfig


class WhisperTranscriptor(STTConfig):
    
    @staticmethod
    def get_available_models() -> List[str]:
        return whisper.available_models()

    def __init__(self) -> None:
        STTConfig.__init__(self)

        # 'True' when the model is being loaded
        self._model_loaded: bool = False

        # model set to None
        self._model: whisper.Whisper = None
    
    def is_model_loaded(self) -> bool:
        return self._model_loaded
    
    def load_model(self) -> None:
        # load the model
        self._model = whisper.load_model(
            name = self.model_name,
            device = self.device,
            download_root = self.download_root,
            in_memory = self.preload_in_memory
        )

        # set status to True
        self._model_loaded = True
    
    def transcribe(
        self,
        audio: str | ndarray | Tensor,
        initial_prompt: str | None = None
    ) -> dict[str, str | list] | Literal[-1]:
        
        # return if model not already loaded
        if not self._model_loaded:
            logging.error('please load the model first')
            return -1
        
        # transcribe the result
        result = self._model.transcribe(
            audio=audio,
            verbose=self.verbose,
            temperature=self.temperature,
            initial_prompt=initial_prompt,
            word_timestamps=self.word_timestamps,
            clip_timestamps=self.clip_timestamps
        )

        return result


def test_transcriptor() -> None:
    transcriptor = WhisperTranscriptor()
    print(WhisperTranscriptor.get_available_models())

# test_transcriptor()
