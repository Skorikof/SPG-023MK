import os
import logging
from datetime import datetime
from configparser import ConfigParser


_log_format = "%(asctime)s - [%(levelname)s] - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
_date_log = str(datetime.now().day).zfill(2) + '_' + str(datetime.now().month).zfill(2) + \
            '_' + str(datetime.now().year)
_path_logs = 'logs'


def convert_level(level: int):
    if level == 1:
        return logging.DEBUG
    elif level == 3:
        return logging.ERROR
    elif level == 4:
        return logging.WARNING
    else:
        return logging.INFO
    
def get_handler(level):
    handler = logging.FileHandler(f'{_path_logs}/{_date_log}.log', encoding='utf-8')
    handler.setLevel(convert_level(level))
    handler.setFormatter(logging.Formatter(_log_format))
    return handler

def get_logger(name):
    directory = _path_logs
    os.makedirs(directory, exist_ok=True)
    config = ConfigParser()
    config.read('settings.ini', encoding='utf-8')
    log_level = int(config['Settings']['LogLevel'])
    logger = logging.getLogger(name)
    logger.setLevel(convert_level(log_level))
    logger.addHandler(get_handler(log_level))
    logger.propagate = False

    return logger
