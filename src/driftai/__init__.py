import logging
from driftai.utils.logger import (
    init_logger,
    LogFormatters
)

# initialize the logging system
init_logger(
    formatter=LogFormatters.DetailedFormatter,
    log_level=logging.DEBUG
)

from driftai.tests import *
from driftai.ui import run_audio_recorder_app

# from driftai.config.audio_config import AudioConfig


def main() -> None:
    # test_config_subpath()
    # test_logger()
    # test_recorder()

    # from driftai.ui.mic_input_ui import run_main_app
    # run_main_app()

    # test_run_floating_window()
    run_audio_recorder_app()
