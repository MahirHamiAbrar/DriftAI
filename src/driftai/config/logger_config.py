import os
import sys
import logging
import datetime

from driftai.utils import (
    read_json_file,
    get_internal_path
)


class LoggerConfig:
    
    DATE_FORMAT = "%d-%m-%Y"
    
    LOG_FOLDER_NAME = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "logs"
    )
    
    LOG_FILE_CREATE_MESSAGE = None
    REGULAR_FORMATTER = '%(asctime)s,%(msecs)03d   %(levelname)-6s [%(filename)s:%(lineno)d]:%(message)s'
    DETAILED_FORMATTER = '%(asctime)s,%(msecs)03d   %(levelname)-6s [%(filename)s:%(module)s:%(funcName)s:%(lineno)d]:%(message)s'

    def __init__(self) -> None:
        pass




def __getLogFileName() -> str:
    global DATE_FORMAT, LOG_FOLDER_NAME, LOG_FILE_CREATE_MESSAGE
    
    date = datetime.date.today().strftime(DATE_FORMAT)    # use "DD MM YYYY" format
    fp = os.path.join(LOG_FOLDER_NAME, f"{date}.log")

    if not os.path.exists(fp):
        with open(fp, 'w') as file:
            file.write("")
        LOG_FILE_CREATE_MESSAGE = f"LOG FILE CREATED ON: {datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}"
    
    return fp


# generate log file name
__log_file_name: str = __getLogFileName()


def init_logger() -> None:
    global LOG_FILE_CREATE_MESSAGE
    
    logging.basicConfig(
        level=logging.INFO,
        format=DETAILED_FORMATTER,
        datefmt='%d-%m-%Y:%H:%M:%S',
        handlers=[
            logging.FileHandler(__log_file_name),
            logging.StreamHandler(sys.stdout)
        ]
    )

    if LOG_FILE_CREATE_MESSAGE:
        logging.info(LOG_FILE_CREATE_MESSAGE)
    logging.info("=="*20 + " SESSION STARTED " + "=="*20)
