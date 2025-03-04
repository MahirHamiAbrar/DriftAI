import logging
from driftai.utils.logger import (
    init_logger,
    LogFormatters
)

# initialize the logging system
init_logger(formatter=LogFormatters.DetailedFormatter)

# from driftai.config.audio_config import AudioConfig

def config_subpath_test() -> None:
    from driftai.config import get_config_data_subpath
    path = get_config_data_subpath(['audio', 'recorder', 'output_dir'])
    print(f'{path = }')


def logger_test() -> None:
    logging.debug('this is an debug log')
    logging.info('this is an info log')
    logging.warning('this is an warning log')
    logging.error('this is an error log')
    
    try:
        n = 1 / 0
    except Exception as e:
        logging.exception(f"Exception: {e}")
    
    logging.critical('this is an critical log')


def main() -> None:
    # config_subpath_test()
    logger_test()
