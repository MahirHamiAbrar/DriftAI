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
    # run_audio_recorder_app()

    from driftai.ui.chat_widget import run_test_chat_widget
    # run_test_chat_widget()

    from driftai.experimentals.audio_visualizer import run_visualizer_app
    # run_visualizer_app()
    
    from driftai.experimentals.audio_visualizer_file import run_audio_visualizer_file
    # run_audio_visualizer_file()

    from driftai.ui.audio_visualizer_widget import test_run_widget
    # test_run_widget()

    from driftai.experimentals.test_recorder_app import run_test_recorder_app
    # run_test_recorder_app()

    from driftai.ui import test_run_audio_input_widget
    test_run_audio_input_widget()
