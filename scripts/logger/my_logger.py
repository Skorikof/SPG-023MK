# -*- coding: utf-8 -*-
import os
import logging
from datetime import datetime
from pathlib import Path
from config import config
from scripts import archive_names


_log_format = "%(asctime)s - [%(levelname)s] - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
_date_log = archive_names.file_stem(datetime.now())     # ГГГГ-ММ-ДД
_path_logs = 'logs'

# старые логи ДД_ММ_ГГГГ.log -> ГГГГ-ММ-ДД.log (один раз, при первом импорте)
archive_names.rename_old_files(Path(_path_logs), '.log')

    
def get_handler():
    handler = logging.FileHandler(f'{_path_logs}/{_date_log}.log', encoding='utf-8')
    handler.setLevel(config.log_level)
    handler.setFormatter(logging.Formatter(_log_format))
    return handler

def get_logger(name):
    directory = _path_logs
    os.makedirs(directory, exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(config.log_level)
    # get_logger вызывается в конструкторах (CalcData, ReadArchive... создаются многократно):
    # без проверки каждый вызов добавлял обработчик, и строка писалась в лог N раз
    if not logger.handlers:
        logger.addHandler(get_handler())
    logger.propagate = False

    return logger
