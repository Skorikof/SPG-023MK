# -*- coding: utf-8 -*-
import configparser
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

from scripts.logger import my_logger


@dataclass
class Operator:
    """Оператор с именем и рангом"""
    name: str
    rank: str


class Operators:
    SECTION_PREFIX = 'Operator'
    CONFIG_FILE = Path('operators.ini')
    
    def __init__(self):
        self.logger = my_logger.get_logger(__name__)
        self.operators: list[Operator] = []
        self.config = configparser.ConfigParser()
        self.current_index = -1

    def update_list(self) -> None:
        """Загружает операторов из конфига"""
        try:
            self.operators.clear()
            self.config.read(self.CONFIG_FILE, encoding='utf-8')
            
            for section in self.config.sections():
                try:
                    name = self.config.get(section, 'name', fallback='')
                    rank = self.config.get(section, 'rank', fallback='')
                    
                    if name:  # Пропускаем пустые записи
                        self.operators.append(Operator(name=name, rank=rank))
                except Exception as e:
                    self.logger.error(f"Ошибка чтения раздела {section}: {e}")

        except Exception as e:
            self.logger.error(f"Ошибка при загрузке операторов: {e}")

    def _save_config(self) -> None:
        """Сохраняет операторов в конфиг"""
        try:
            self.config.clear()
            
            for i, operator in enumerate(self.operators):
                section_name = f'{self.SECTION_PREFIX}{i}'
                self.config.add_section(section_name)
                self.config.set(section_name, 'name', operator.name)
                self.config.set(section_name, 'rank', operator.rank)
            
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as configfile:
                self.config.write(configfile)
                
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении конфига: {e}")

    def delete_operator(self, index: int) -> bool:
        """Удаляет оператора по индексу. Возвращает True если успешно"""
        try:
            if 0 <= index < len(self.operators):
                self.operators.pop(index)
                self._save_config()
                return True
            else:
                self.logger.warning(f"Невалидный индекс: {index}")
                return False
        except Exception as e:
            self.logger.error(f"Ошибка при удалении оператора: {e}")
            return False

    def add_operator(self, name: str, rank: str) -> bool:
        """Добавляет нового оператора. Возвращает True если успешно"""
        try:
            if not name.strip():
                self.logger.warning("Имя оператора не может быть пустым")
                return False
                
            operator = Operator(name=name.strip(), rank=rank.strip())
            self.operators.append(operator)
            self._save_config()
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка при добавлении оператора: {e}")
            return False

    def get_names(self):
        """Возвращает список имен операторов"""
        return [op.name for op in self.operators]

    def get_ranks(self):
        """Возвращает список рангов операторов"""
        return [op.rank for op in self.operators]

    def get_operator(self, index: int) -> Optional[Operator]:
        """Возвращает оператора по индексу"""
        if 0 <= index < len(self.operators):
            return self.operators[index]
        return None
