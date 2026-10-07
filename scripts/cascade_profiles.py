# -*- coding: utf-8 -*-
import configparser
from pathlib import Path
from dataclasses import dataclass, field

from scripts.logger import my_logger


@dataclass
class CascadeProfile:
    """Профиль каскадного испытания: подпись кнопки и список скоростей, м/с"""
    name: str
    speeds: list[float] = field(default_factory=list)


class CascadeProfiles:
    """
    Типовые наборы скоростей для каскадного испытания из cascade.ini (рядом с exe).
    Формат секции:
        [Profile1]
        name = Профиль 1
        speeds = 0.05; 0.1; 0.15
    Скорости разделяются ';', дробная часть - через точку или запятую.
    """
    SECTION_PREFIX = 'Profile'
    CONFIG_FILE = Path('cascade.ini')
    COUNT = 4
    # Содержимое файла, которым он пересоздаётся при отсутствии (случайно удалили)
    DEFAULT_CONTENT = """\
; Профили каскадного испытания: кнопки «Профиль 1..4» заполняют таблицу скоростей.
; name   - подпись на кнопке (если не задана - «Профиль N»)
; speeds - скорости в м/с через ';' (не больше 30), дробная часть через точку или запятую.
; Скорости вне допустимого диапазона для хода амортизатора пропускаются с предупреждением.
; Файл перечитывается при каждом нажатии кнопки, перезапуск программы не нужен.
; Если файл удалить, программа создаст его заново со случайными значениями.

[Profile1]
name = Профиль 1
speeds = 0.05; 0.1; 0.15; 0.2; 0.25; 0.3

[Profile2]
name = Профиль 2
speeds = 0.05; 0.1; 0.2; 0.3; 0.4; 0.5; 0.6

[Profile3]
name = Профиль 3
speeds = 0.026; 0.052; 0.105; 0.131; 0.209; 0.262; 0.314; 0.393; 0.524

[Profile4]
name = Профиль 4
speeds = 0.02; 0.05; 0.08; 0.1; 0.13; 0.16; 0.2; 0.25; 0.3; 0.35; 0.4; 0.45; 0.5; 0.55; 0.6
"""

    def __init__(self):
        self.logger = my_logger.get_logger(__name__)
        self.profiles: dict[int, CascadeProfile] = {}

    def update_list(self) -> None:
        """Перечитывает файл, чтобы правки применялись без перезапуска программы"""
        self.profiles.clear()
        if not self.CONFIG_FILE.exists():
            self._create_default_file()
            if not self.CONFIG_FILE.exists():
                return

        config = configparser.ConfigParser()
        try:
            config.read(self.CONFIG_FILE, encoding='utf-8')
        except Exception as e:
            self.logger.error(f'Ошибка при загрузке профилей каскада: {e}')
            return

        for num in range(1, self.COUNT + 1):
            section = f'{self.SECTION_PREFIX}{num}'
            if not config.has_section(section):
                continue
            name = config.get(section, 'name', fallback='').strip() or f'Профиль {num}'
            raw = config.get(section, 'speeds', fallback='')
            speeds = []
            for item in raw.split(';'):
                item = item.strip().replace(',', '.')
                if not item:
                    continue
                try:
                    speeds.append(float(item))
                except ValueError:
                    self.logger.warning(f'{section}: некорректная скорость "{item}" пропущена')
            self.profiles[num] = CascadeProfile(name=name, speeds=speeds)

    def _create_default_file(self) -> None:
        try:
            self.CONFIG_FILE.write_text(self.DEFAULT_CONTENT, encoding='utf-8')
            self.logger.warning(f'Не найден файл профилей каскада, создан заново '
                                f'со значениями по умолчанию: {self.CONFIG_FILE.resolve()}')
        except Exception as e:
            self.logger.error(f'Не удалось создать файл профилей каскада {self.CONFIG_FILE}: {e}')

    def get_profile(self, num: int) -> CascadeProfile | None:
        return self.profiles.get(num)
