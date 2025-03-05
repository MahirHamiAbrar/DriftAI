import logging
from driftai.utils.logger import (
    init_logger,
    LogFormatters
)

# initialize the logging system
init_logger(formatter=LogFormatters.DetailedFormatter)

from driftai.tests import *

# from driftai.config.audio_config import AudioConfig


def main() -> None:
    # test_config_subpath()
    # test_logger()
    # test_recorder()

    # from driftai.ui.mic_input_ui import run_main_app
    # run_main_app()

    test_floating_window()
