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
        self._ep_server_status: str = urljoin(self._base_url, '/stt/server_status/')
        self._ep_model_load: str = urljoin(self._base_url, '/stt/load_model/')
        self._ep_model_status: str = urljoin(self._base_url, '/stt/model_status/')
        self._ep_model_unload: str = urljoin(self._base_url, '/stt/unload_model/')
        self._ep_transcribe: str = urljoin(self._base_url, '/stt/transcribe/')
        self._ep_transcription_status: str = urljoin(self._base_url, '/stt/transcription_status/')
        self._ep_server_shutdown: str = urljoin(self._base_url, '/stt/shutdown_server/')
    
    def get_server_url(self) -> str:
        return self._base_url
    
    def is_server_running(self) -> bool:
        try:
            res = requests.get(self._ep_server_status)
        except requests.exceptions.ConnectionError:
            return False
        return True
    
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
    
    def shutdown_server(self) -> None:
        res = requests.post(self._ep_server_shutdown)
        return res.json()
    
    def transcribe(self, audio_file_path: str)-> dict[str, Any]:
        res = requests.post(
            self._ep_transcribe,
            json = {
                "audio_file": audio_file_path
            }
        )

        return res.json()
    
    def get_transcription_status(self, job_id: str) -> dict[str, Any]:
        res = requests.get(urljoin(self._ep_transcription_status, str(job_id)))

        try:
            res = res.json()
        except Exception as e:
            print(f"Error: {e}")
        
        return res


def test_client() -> None:
    client = STTClient()

    is_server_alive = client.is_server_running()
    print(f"{is_server_alive = }")
    
    # quit if server is not running
    if not is_server_alive:
        return
    
    res = client.load_model()
    sts = res['status']
    sts_cnged = True

    while sts != 2:

        if res['status'] != sts:
            sts_cnged = True
            sts = res['status']
        
        if sts_cnged:
            if sts == 0:
                print('model not loaded')
            elif sts == 1:
                print('model loading...')
            
            sts_cnged = False
        
        res = client.get_model_status()
    
    print('model loaded.')

    audio_file = input('Enter Audio File Path (mp3 or wav): ')

    res = client.transcribe(audio_file)
    sts = res['status']
    sts_cnged = True

    print(f'processing audio...\n{res = }')
    while sts != 11:
        res = client.get_transcription_status(res['job_id'])
        sts = res['status']
    
    print('PROCESSING COMPLETE')

    print(f"\n\n{res = }")

    print('\n\nUnloading Model...')
    client.unload_model()

# test_client()
