# -*- coding: utf-8 -*-
import configparser
from pydantic import BaseModel

from scripts.logger import my_logger


class StructAmort:
    """Контейнер для хранения данных амортизаторов"""
    def __init__(self):
        self.amorts: list['ArchiveSchema'] = []
        

class AmortSchema(BaseModel):
    name: str
    min_length: float
    max_length: float
    hod: int
    speed_one: float
    speed_two: float
    min_comp: float
    min_comp_2: float
    max_comp: float
    max_comp_2: float
    min_recoil: float
    min_recoil_2: float
    max_recoil: float
    max_recoil_2: float
    max_temper: float

    
class ArchiveSchema(AmortSchema):
    adapter: str
    adapter_len: int


class Amort:
    # Соответствие номеров адаптеров их длинам
    ADAPTER_LENGTHS: dict[str, int] = {
        '069': 25,
        '069-01': 25,
        '069-02': 34,
        '069-03': 34,
        '069-04': 34,
        '072': 41,
    }
    
    CONFIG_FILE = 'amorts.ini'
    
    def __init__(self):
        self.logger = my_logger.get_logger(__name__)
        self.names: list[str] = []
        self.current_index: int = -1
        self.struct = StructAmort()
        self.config = configparser.ConfigParser()

    def _convert_adapter(self, name: str) -> int:
        """Перевод номера адаптера в его длинну"""
        try:
            return self.ADAPTER_LENGTHS.get(name, 0)
        except Exception as e:
            self.logger.error(f"Error converting adapter '{name}': {e}")
            return 0

    def _parse_config_value(self, key: str, value: str):
        """Преобразование значения конфига в нужный тип"""
        if key == 'hod':
            return int(value)
        elif key in ('name', 'adapter'):
            return value
        else:
            return float(value)

    def update_amort_list(self) -> None:
        """Загрузка списка амортизаторов из конфига"""
        try:
            self.names.clear()
            self.struct.amorts.clear()
            self.config.read(self.CONFIG_FILE, encoding='utf-8')
            
            for section in self.config.sections():
                try:
                    data = self._parse_section(section)
                    if data:
                        self.struct.amorts.append(ArchiveSchema(**data))
                except Exception as e:
                    self.logger.error(f"Error parsing section {section}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error reading config file '{self.CONFIG_FILE}': {e}")

    def _parse_section(self, section: str) -> dict | None:
        """Парсинг одной секции конфига"""
        data = {}
        
        for key in self.config[section]:
            val = self.config.get(section, key)
            
            if key == 'name':
                data[key] = val
                self.names.append(val)
            elif key == 'adapter':
                data[key] = val
                data['adapter_len'] = self._convert_adapter(val)
            else:
                data[key] = self._parse_config_value(key, val)
        
        return data if data else None

    def delete_amort(self, index_del: int) -> None:
        """Удаление амортизатора по индексу"""
        try:
            if 0 <= index_del < len(self.struct.amorts):
                self.struct.amorts.pop(index_del)
                self._write_struct_in_file()
            else:
                self.logger.warning(f"Invalid index for deletion: {index_del}")
        except Exception as e:
            self.logger.error(f"Error deleting amort at index {index_del}: {e}")

    def add_amort(self, obj: dict) -> None:
        """Добавление нового амортизатора"""
        try:
            nam_section = f'Amort{len(self.struct.amorts)}'
            self.config.add_section(nam_section)
            
            for key, value in obj.items():
                if key != 'tag':
                    self.config.set(nam_section, key, str(value))

            self._save_config()

        except Exception as e:
            self.logger.error(f"Error adding amort: {e}")

    def change_amort(self, ind: int, obj: dict) -> None:
        """Изменение данных амортизатора по индексу"""
        try:
            if 0 <= ind < len(self.struct.amorts):
                self.struct.amorts[ind] = ArchiveSchema(**obj)
                self._write_struct_in_file()
            else:
                self.logger.warning(f"Invalid index for change: {ind}")
        except Exception as e:
            self.logger.error(f"Error changing amort at index {ind}: {e}")

    def _save_config(self) -> None:
        """Сохранение конфига в файл"""
        try:
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as configfile:
                self.config.write(configfile)
        except Exception as e:
            self.logger.error(f"Error saving config to '{self.CONFIG_FILE}': {e}")

    def _write_struct_in_file(self) -> None:
        """Перезапись всей структуры амортизаторов в файл"""
        try:
            self.config.clear()

            for i, amort in enumerate(self.struct.amorts):
                nam_section = f'Amort{i}'
                self.config.add_section(nam_section)
                
                data = amort.dict()
                
                for key, val in data.items():
                    self.config.set(nam_section, key, str(val))

            self._save_config()

        except Exception as e:
            self.logger.error(f"Error writing struct to file: {e}")
