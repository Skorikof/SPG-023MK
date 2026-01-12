# -*- coding: utf-8 -*-
import configparser
from pydantic import BaseModel

from scripts.logger import my_logger


class StructAmort(object):
    def __init__(self):
        self.amorts = []
        

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
    def __init__(self):
        self.logger = my_logger.get_logger(__name__)
        self.names = []
        self.current_index = -1
        self.struct = StructAmort()
        self.config = configparser.ConfigParser()

    def _convert_adapter(self, name: str):
        """Перевод номера адаптера в его длинну"""
        try:
            if name == '069' or name == '069-01':
                return 25

            elif name == '069-02' or name == '069-03' or name == '069-04':
                return 34

            elif name == '072':
                return 41

            else:
                return 0

        except Exception as e:
            self.logger.error(e)

    def update_amort_list(self):
        try:
            self.names = []
            self.struct.amorts.clear()
            self.config.read("amorts.ini", encoding='utf-8')
            ind = -1
            for section in self.config.sections():
                try:
                    ind += 1
                    data = {}
                    
                    for key in self.config[section]:
                        val = self.config.get(section, key)
                        if key == 'name':
                            data[key] = val
                            self.names.append(val)
                        elif key == 'hod':
                            data[key] = int(val)
                        elif key == 'adapter':
                            data[key] = val
                            data['adapter_len'] = self._convert_adapter(val)
                        else:
                            data[key] = float(val)
                            
                    self.struct.amorts.append(ArchiveSchema(**data))

                except Exception as e:
                    self.logger.error(e)
                    
        except Exception as e:
            self.logger.error(e)

    def delete_amort(self, index_del):
        try:
            self.struct.amorts.pop(index_del)
            self._write_struct_in_file()

        except Exception as e:
            self.logger.error(e)

    def add_amort(self, obj):
        try:
            max_rec = len(self.struct.amorts)
            nam_section = 'Amort' + str(max_rec)
            self.config.add_section(nam_section)
            
            for key, value in obj.items():
                if key == 'tag':
                    pass
                else:
                    self.config.set(nam_section, key, str(value))

            with open('amorts.ini', 'w', encoding='utf-8') as configfile:
                self.config.write(configfile)

        except Exception as e:
            self.logger.error(e)

    def change_amort(self, ind, obj):
        try:
            self.struct.amorts[ind] = ArchiveSchema(**obj)
            self._write_struct_in_file()

        except Exception as e:
            self.logger.error(e)

    def _write_struct_in_file(self):
        try:
            self.config.clear()

            for i in range(len(self.struct.amorts)):
                nam_section = 'Amort' + str(i)
                self.config.add_section(nam_section)
                
                data = self.struct.amorts[i].dict()
                
                for key, val in data.items():
                    self.config.set(nam_section, key, str(val))

            with open('amorts.ini', "w", encoding='utf-8') as configfile:
                self.config.write(configfile)

        except Exception as e:
            self.logger.error(e)
