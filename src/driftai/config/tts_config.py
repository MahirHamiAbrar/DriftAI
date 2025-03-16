from driftai.config import (
    get_config,
    get_config_data_subpath
)


class TTSConfig:

    def __init__(self) -> None:
        self._config: dict = {}
        self.load_config()

    def load_config(self) -> dict:
        # Recording parameter configuration
        self._config = get_config()['audio']['tts']

        # config for loading the model
        self.hf_home: str = get_config_data_subpath(
            keys=['audio', 'tts', 'hf_home']
        )
        self.model_name: str = self._config.get("model_name", "hexgrad/Kokoro-82M")
        
        # server host & port
        self.host: str = self._config.get('host', 'http://127.0.0.1')
        self.port: int = self._config.get('port', 9000)
