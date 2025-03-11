import whisper
import logging

from enum import Enum
from torch import Tensor
from numpy import ndarray

from typing import List, Literal
from driftai.config import STTConfig


class JobStatus(Enum):
    JobQueued = 200

    ModelNotLoaded = 0
    ModelLoading = 1
    ModelLoaded = 2

    TranscriptionProcessing = 10
    TranscriptionComplete = 11


class AudioTranscriptor(STTConfig):
    
    @staticmethod
    def get_available_models() -> List[str]:
        return whisper.available_models()

    def __init__(self) -> None:
        STTConfig.__init__(self)

        # 'True' when the model is being loaded
        self._model_status = JobStatus.ModelNotLoaded

        # model set to None
        self._model: whisper.Whisper = None
    
    def get_model_status(self) -> JobStatus:
        return self._model_status
    
    def load_model(self) -> None:
        """ NOTE: Loading may take some good amount of time depending on the hardware and model size. """

        self._model_status = JobStatus.ModelLoading

        # load the model
        self._model = whisper.load_model(
            name = self.model_name,
            device = self.device,
            download_root = self.download_root,
            in_memory = self.preload_in_memory
        )

        # set status to True
        self._model_status = JobStatus.ModelLoaded
    
    def unload_model(self) -> None:
        self._model = None
        self._model_status = JobStatus.ModelNotLoaded
    
    def transcribe(
        self,
        audio: str | ndarray | Tensor,
        initial_prompt: str | None = None
    ) -> dict[str, str | list] | Literal[-1]:
        
        # return if model not already loaded
        if self._model_status == JobStatus.ModelNotLoaded:
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
    transcriptor = AudioTranscriptor()
    transcriptor.load_model()
    print(AudioTranscriptor.get_available_models())
    result = transcriptor.transcribe('audio.mp3')
    print(result)

# test_transcriptor()
