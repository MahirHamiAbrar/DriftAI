# from driftai.config.audio_config import AudioConfig
from driftai.config import get_config_data_subpath

def main() -> None:
    path = get_config_data_subpath(['audio', 'recorder', 'output_dir'])
    print(f'{path = }')
