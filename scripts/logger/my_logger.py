import os
import logging
from datetime import datetime

from config import config


_log_format = "%(asctime)s - [%(levelname)s] - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
_date_log = str(datetime.now().day).zfill(2) + '_' + str(datetime.now().month).zfill(2) + \
            '_' + str(datetime.now().year)
_path_logs = 'logs'

_log_level = config.log_level

    
def get_handler():
    handler = logging.FileHandler(f'{_path_logs}/{_date_log}.log', encoding='utf-8')
    handler.setLevel(_log_level)
    handler.setFormatter(logging.Formatter(_log_format))
    return handler

def get_logger(name):
    directory = _path_logs
    os.makedirs(directory, exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(_log_level)
    logger.addHandler(get_handler())
    logger.propagate = False

    return logger
