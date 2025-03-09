from typing import List
from driftai.config import get_config


class STTConfig:

    def __init__(self) -> None:
        self._config: dict = {}
        self.load_config()

    def load_config(self) -> dict:
        # Recording parameter configuration
        self._config = get_config()['audio']['stt']

        # config for loading the model
        self.model_name: str = self._config.get('model', 'small')
        self.device: str = self._config.get('device', 'cpu')
        self.default_download_root: str = self._config.get('default_download_root')
        self.download_root: str = self._config.get('download_root', self.default_download_root)
        self.preload_in_memory: bool = self._config.get('preload_in_memory', False)

        # config for transcription
        self.verbose: bool | None = self._config.get('verbose', None)
        self.temperature: float = self._config.get('temperature', 0.7)
        self.word_timestamps: bool = self._config.get('word_timestamps', True)
        self.clip_timestamps: str | List[float] = self._config.get('clip_timestamps', "0")
