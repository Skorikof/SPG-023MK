# -*- coding: utf-8 -*-
"""
Имена файлов архива и логов: ГГГГ-ММ-ДД (сортируются по дате в любом файловом менеджере).
Старый формат ДД.ММ.ГГГГ (архив) и ДД_ММ_ГГГГ (логи) переименовывается при запуске;
в интерфейсе дата по-прежнему показывается как ДД.ММ.ГГГГ.
"""
import re
from datetime import date, datetime
from pathlib import Path

FILE_DATE_FORMAT = '%Y-%m-%d'
DISPLAY_DATE_FORMAT = '%d.%m.%Y'

_OLD_ARCHIVE_RX = re.compile(r'^(\d{2})\.(\d{2})\.(\d{4})$')
_OLD_LOG_RX = re.compile(r'^(\d{2})_(\d{2})_(\d{4})$')
_NEW_RX = re.compile(r'^(\d{4})-(\d{2})-(\d{2})$')


def file_stem(d: date | datetime) -> str:
    return d.strftime(FILE_DATE_FORMAT)


def display(d: date) -> str:
    return d.strftime(DISPLAY_DATE_FORMAT)


def is_new_format(stem: str) -> bool:
    return bool(_NEW_RX.match(stem))


def parse_stem(stem: str) -> date | None:
    """Дата из имени файла в новом или старом формате, None - не дата"""
    try:
        if m := _NEW_RX.match(stem):
            return date(int(m[1]), int(m[2]), int(m[3]))
        if m := (_OLD_ARCHIVE_RX.match(stem) or _OLD_LOG_RX.match(stem)):
            return date(int(m[3]), int(m[2]), int(m[1]))
    except ValueError:
        pass
    return None


def rename_old_files(directory: Path, suffix: str, logger=None) -> None:
    """Переименовывает файлы со старым форматом даты в ГГГГ-ММ-ДД"""
    if not directory.exists():
        return
    for path in directory.glob(f'*{suffix}'):
        if _NEW_RX.match(path.stem):
            continue
        d = parse_stem(path.stem)
        if d is None:
            continue
        target = path.with_name(file_stem(d) + suffix)
        try:
            if target.exists():
                # оба файла за одну дату (например, запускали старую версию) - не сливаем,
                # читалка архива покажет их как одну дату
                if logger:
                    logger.warning(f'{path.name} не переименован: уже есть {target.name}')
                continue
            path.rename(target)
            if logger:
                logger.info(f'{path.name} переименован в {target.name}')
        except PermissionError:
            if logger:
                logger.warning(f'{path.name} занят, переименование при следующем запуске')
        except Exception as e:
            if logger:
                logger.error(f'Ошибка переименования {path.name}: {e}')
