import sys
import logging
from enum import Enum
from driftai.config import LoggerConfig

# generate log file name
_logger_config = LoggerConfig()


class LogFormatters(Enum):
    RegularFormatter = 0
    DetailedFormatter = 1


def init_logger(
    formatter: LogFormatters = LogFormatters.DetailedFormatter,
    log_level = logging.INFO
) -> None:
    """ Two options for formatter: 
        0 = 'regular', 
        1 = 'detailed' 
    """
    global _logger_config
    
    logging.basicConfig(
        level=log_level,
        format=(
            _logger_config.REGULAR_FORMATTER
            if formatter == LogFormatters.RegularFormatter
            else _logger_config.DETAILED_FORMATTER
        ),
        datefmt=_logger_config.DATE_TIME_FORMAT,
        handlers=[
            logging.FileHandler(_logger_config.getLogFileName()),
            logging.StreamHandler(sys.stdout)
        ]
    )

    if (_logger_config.LOG_FILE_CREATE_MESSAGE):
        logging.info(_logger_config.LOG_FILE_CREATE_MESSAGE)
    
    logging.info("*** SESSION STARTED ***")
