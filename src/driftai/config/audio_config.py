import pyaudio
from driftai.config import (
    get_config,
    get_config_data_subpath
)


class RecorderConfig:

    SAMPLING_FORMATS: dict = {
        "i8": pyaudio.paInt8,
        "i16": pyaudio.paInt16,
        "i24": pyaudio.paInt24,
        "i32": pyaudio.paInt32,
        "f32": pyaudio.paFloat32
    }

    def __init__(self) -> None:
        self._config: dict = {}
        self.load_config()

    def load_config(self) -> dict:
        # Recording parameter configuration
        self._config = get_config()['audio']['recorder']

        # Audio parameters (extracted from config file)
        self.channels: int = int(self._config.get('channels', 2))
        self.rate: int = int(self._config.get('rate', 44100))
        self.chunk_size: int = int(self._config.get('chunk_size', 1024))
        self.sampling_format = self.SAMPLING_FORMATS[self._config.get(
            'sampling_format',
            'i32'
        )]
        self.recording_format: str = self._config.get('recording_format', 'wav')
        self.chunk_duration: int = int(self._config.get('chunk_duration', 2))

        self.available_sampling_formats: list = self._config.get(
            'available_sampling_formats',
            []
        )

        self.available_recording_formats: list = self._config.get(
            'available_recording_formats',
            []
        )

        self.output_dir = get_config_data_subpath(
            keys=['audio', 'recorder', 'output_dir']
        )
