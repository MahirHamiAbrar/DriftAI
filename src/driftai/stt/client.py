import requests
from typing import Any
from urllib.parse import urljoin
from driftai.config import STTConfig


class STTClient(STTConfig):
    def __init__(self, host: str=None, port: int=None) -> None:
        STTConfig.__init__(self)

        # change host to the specified host address
        if host:
            self.host = host
        
        # change port to the specified port
        if port:
            self.port = port
        
        # construct the base url
        self._base_url: str = f"{self.host}:{self.port}"
        
        # is the model loaded?
        self._model_loaded: bool = False

        # declare the endpoints
        self._ep_model_load: str = urljoin(self._base_url, '/stt/load_model/')
        self._ep_model_status: str = urljoin(self._base_url, '/stt/model_status/')
        self._ep_model_unload: str = urljoin(self._base_url, '/stt/unload_model/')
        self._ep_transcribe: str = urljoin(self._base_url, '/stt/transcribe/')
        self._ep_transcription_status: str = urljoin(self._base_url, '/stt/transcription_status/')
    
    def get_server_url(self) -> str:
        return self._url
    
    def is_model_loaded(self) -> bool:
        return self._model_loaded
    
    def load_model(self, force_load: bool=False) -> dict[str, int]:
        res = requests.post(self._ep_model_load)
        return res.json()
    
    def get_model_status(self) -> dict[str, int]:
        res = requests.get(self._ep_model_status)
        return res.json()
    
    def unload_model(self):
        res = requests.post(self._ep_model_unload)
        return res.json()
    
    def transcribe(self, audio_file_path: str)-> dict[str, Any]:
        res = requests.post(
            self._ep_transcribe,
            json = {
                "audio_file": audio_file_path
            }
        )

        return res.json()
    
    def get_transcription_status(self, job_id: str):
        res = requests.post(urljoin(self._ep_transcribe, str(job_id)))
        return res.json()


