import pyaudio
from driftai.utils import (
    read_json_file,
    get_internal_path
)
# from driftai.config import get_config


class RecorderConfig:

    CONFIG_FILE_PATH: str = get_internal_path('data/config.json', check_exist=True)
    SAMPLING_FORMATS: dict = {
        "i8": pyaudio.paInt8,
        "i16": pyaudio.paInt16,
        "i24": pyaudio.paInt24,
        "i32": pyaudio.paInt32,
        "f32": pyaudio.paFloat32
    }

    def __init__(self) -> None:
        self._config: dict = self.load_config()

    def load_config(self) -> dict:
        _file_data: dict = read_json_file(self.CONFIG_FILE_PATH)
        return _file_data['audio']['recorder']
    
    def reload_config(self) -> None:
        self._config = self.load_config()
