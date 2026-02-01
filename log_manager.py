import logging 
import re
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

LOG_FOLDER = Path(__file__).with_name("logs")
LOG_FOLDER.mkdir(exist_ok=True)

class CustomTimedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, filename, log_folder, **kwargs):
        super().__init__(filename, **kwargs)
        self.log_folder = log_folder

    def rotation_filename(self, dest):
        # Extract the date from the default dest name
        date_suffix = dest.split('.')[-1]
        # Use the date to create the desired filename format
        return f'{self.log_folder}/{date_suffix}.log'


def setup_logger(name):
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        return logger
    
    logger.setLevel(logging.INFO)

    log_filename = f'{LOG_FOLDER}/current.log'
    file_handler = CustomTimedRotatingFileHandler(log_filename, LOG_FOLDER, when="midnight", interval=1, backupCount=0)
    file_handler.suffix = "%Y_%m_%d"
    file_handler.extMatch = re.compile(r"^\d{4}_\d{2}_\d{2}\.log$")

    # New console handler
    console_handler = logging.StreamHandler()

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)  # Use the same formatter for the console handler

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)  # Add the console handler to the logger

    logger.propagate = False

    return logger