import logging
from datetime import datetime
import os

_log_format = "%(asctime)s - [%(levelname)s] - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
_date_log = str(datetime.now().day).zfill(2) + '_' + str(datetime.now().month).zfill(2) + \
            '_' + str(datetime.now().year)
_path_logs = 'logs'


def get_warn_handler():
    warn_handler = logging.FileHandler(f'{_path_logs}/{_date_log}.log', encoding='utf-8')
    warn_handler.setLevel(logging.WARNING)
    warn_handler.setFormatter(logging.Formatter(_log_format))
    return warn_handler


def get_err_handler():
    err_handler = logging.FileHandler(f'{_path_logs}/{_date_log}.log', encoding='utf-8')
    err_handler.setLevel(logging.ERROR)
    err_handler.setFormatter(logging.Formatter(_log_format))
    return err_handler


def get_info_handler():
    info_handler = logging.FileHandler(f'{_path_logs}/{_date_log}.log', encoding='utf-8')
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(logging.Formatter(_log_format))
    return info_handler

def get_debug_handler():
    info_handler = logging.FileHandler(f'{_path_logs}/{_date_log}.log', encoding='utf-8')
    info_handler.setLevel(logging.DEBUG)
    info_handler.setFormatter(logging.Formatter(_log_format))
    return info_handler


def get_handler():
    info_handler = logging.FileHandler(f'{_path_logs}/{_date_log}.log', encoding='utf-8')
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(logging.Formatter(_log_format))
    return info_handler


def get_logger(name):
    directory = _path_logs
    os.makedirs(directory, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(get_handler())
    # logger.addHandler(get_debug_handler())
    # logger.addHandler(get_info_handler())
    # logger.addHandler(get_err_handler())
    # logger.addHandler(get_warn_handler())
    logger.propagate = False

    return logger
