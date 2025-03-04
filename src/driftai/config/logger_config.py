import os
import sys
import logging
import datetime

from driftai.utils import (
    read_json_file,
    get_internal_path
)
from driftai.config import get_config_data_subpath


class LoggerConfig:
    
    DATE_FORMAT = "%d-%m-%Y"
    TIME_FORMAT = "%H:%M:%S"
    DATE_TIME_FORMAT = DATE_FORMAT + ':' + TIME_FORMAT
    LOG_FOLDER_NAME = get_config_data_subpath(
        keys=['logging', 'log_dir']
    )
    
    LOG_FILE_CREATE_MESSAGE = None
    
    REGULAR_FORMATTER = '%(asctime)s:%(msecs)03d    ' \
        '[%(levelname)-6s] [%(filename)s:%(lineno)d]: %(message)s'
    
    DETAILED_FORMATTER = '%(asctime)s:%(msecs)03d    ' \
        '[%(levelname)-6s] [%(filename)s:%(module)s:%(funcName)s:%(lineno)d]: %(message)s'

    def __init__(self) -> None:
        pass

    def getLogFileName(self) -> str:
        # use "DD MM YYYY" format   
        date = datetime.date.today().strftime(self.DATE_FORMAT)
        fp = os.path.join(self.LOG_FOLDER_NAME, f"{date}.log")

        if not os.path.exists(fp):
            with open(fp, 'w') as file:
                file.write("")
            
            self.LOG_FILE_CREATE_MESSAGE = "LOG FILE GENERATED"
        
        return fp
