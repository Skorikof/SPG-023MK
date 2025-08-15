# -*- coding: utf-8 -*-
from pathlib import Path
from datetime import datetime

from logger import my_logger
from amorts import AmortSchema


class BaseSchema(AmortSchema):
    time_test: str
    operator_name: str
    operator_rank: str
    type_test: str
    serial_number: str
    flag_push_force: str
    static_push_force: float
    dynamic_push_force: float
    speed: float

class LabSchema(BaseSchema):
    move_list: list
    force_list: list
    

class ConvSchema(BaseSchema):
    move_list: list
    force_list: list
    
    
class TempSchema(BaseSchema):
    temper_list: list
    recoil_list: list
    comp_list: list
    
    
class CascSchema(BaseSchema):
    recoil_list: list
    comp_list: list
    speed_list: list


class ReadArchive:
    def __init__(self):
        self.logger = my_logger.get_logger(__name__)

    def init_arch(self):
        try:
            self.files_arr = []
            self.files_name_arr = []
            self.files_name_sort = []

            source_dir = Path('archive/')
            self.files_dir = source_dir.glob('*.csv')

            for i in self.files_dir:
                self.files_arr.append(i)
                self.files_name_arr.append(i.stem)
                self.files_name_sort.append(i.stem)

            """сортировка списка файлов по дате"""
            self.files_name_sort.sort(key=lambda date: datetime.strptime(date, "%d.%m.%Y"), reverse=True)

        except Exception as e:
            self.logger.error(e)
            
    def select_file(self, data):
        try:
            self.data_one = {}
            self.data_two = {}
            self.type_test = ''
            self.lab = []
            self.conv = []
            self.temper = []
            self.cascade = []
            self.speed_list = []
            self.recoil_list = []
            self.comp_list = []
        
            self.index_archive = self.files_name_arr.index(data)

            with open(self.files_arr[self.index_archive], encoding='utf-8') as f:
                for data_list in self._read_line_in_archive(f):
                    self._pars_str_archive(data_list)

        except Exception as e:
            self.logger.error(e)
            
    def _read_line_in_archive(self, file):
        try:
            for line in file:
                data_list = line.split(';')
                if data_list[0] == 'Время':
                    continue
                else:
                    yield data_list
            
        except Exception as e:
            self.logger.error(e)
    
    def _pars_str_archive(self, archive_list):
        try:
            if archive_list[0] == 'end_test':
                if self.type_test == 'lab_cascade':
                    self._create_cascade_object()

            else:
                if archive_list[0] != '*':
                    self.data_one = self._pars_first_data(archive_list)
                            
                elif archive_list[0] == '*':
                    self.data_two = self._pars_second_data(archive_list[24:-1])
                    
            if self.data_one and self.data_two:
                self._create_object_archive(self.data_one, self.data_two)

        except Exception as e:
            self.logger.error(e)
            
    def _create_object_archive(self, data_one, data_two):
        try:
            data = {**data_one, **data_two}
            if self.type_test == 'lab_cascade':
                self.lab.append(LabSchema(**data))
                self.data_two = []
                
            else:
                if self.type_test == 'temper':
                    self.temper.append(TempSchema(**data))
                    
                elif self.type_test == 'lab':
                    self.lab.append(LabSchema(**data))
                    
                elif self.type_test == 'conv':
                    self.conv.append(ConvSchema(**data))
                self.data_one = {}
                self.data_two = {}

        except Exception as e:
            self.logger.error(e)
            
    def _create_cascade_object(self):
        try:
            self.data_one['speed_list'] = self.speed_list[:]
            self.data_one['recoil_list'] = self.recoil_list[:]
            self.data_one['comp_list'] = self.comp_list[:]
            
            self.cascade.append(CascSchema(**self.data_one))
            self.speed_list = []
            self.recoil_list = []
            self.comp_list = []
            self.data_one = {}
            
        except Exception as e:
            self.logger.error(e)
            
    def _pars_first_data(self, archive_list):
        try:
            key = 'move_list'
            data = self._fill_obj_archive_data(archive_list[:24])
            self.type_test = archive_list[3]
            if self.type_test == 'temper':
                key = 'temper_list'
                
            elif self.type_test == 'lab_cascade':
                self._add_data_cascade_graph(speed=float(archive_list[23].replace(',', '.')))
                
            data[key] = self._add_data_on_list_graph(archive_list[24:-1])
            
            return data
            
        except Exception as e:
            self.logger.error(e)
            
    def _pars_second_data(self, archive_list):
        try:
            data = {}
            if self.type_test == 'temper':
                data['recoil_list'], self.data['comp_list'] = self._add_data_temper_graph(archive_list)
                        
            elif self.type_test == 'lab' or self.type_test == 'conv':
                data['force_list'] = self._add_data_on_list_graph(archive_list)

            elif self.type_test == 'lab_cascade':
                force_list = self._add_data_on_list_graph(archive_list)
                data['force_list'] = force_list[:]
                self._add_data_cascade_graph(recoil=max(force_list), comp=min(force_list))
            
            return data
        
        except Exception as e:
            self.logger.error(e)

    def _fill_obj_archive_data(self, data):
        try:
            return {'time_test': data[0],
                    'operator_name': data[1],
                    'operator_rank': data[2],
                    'type_test': data[3],
                    'name': data[4],
                    'serial_number': data[5],
                    'min_length': float(data[6].replace(',', '.')),
                    'max_length': float(data[7].replace(',', '.')),
                    'hod': int(data[8]),
                    'speed_one': float(data[9].replace(',', '.')),
                    'min_recoil': float(data[10].replace(',', '.')),
                    'max_recoil': float(data[11].replace(',', '.')),
                    'min_comp': float(data[12].replace(',', '.')),
                    'max_comp': float(data[13].replace(',', '.')),
                    'speed_two': float(data[14].replace(',', '.')),
                    'min_recoil_2': float(data[15].replace(',', '.')),
                    'max_recoil_2': float(data[16].replace(',', '.')),
                    'min_comp_2': float(data[17].replace(',', '.')),
                    'max_comp_2': float(data[18].replace(',', '.')),
                    'flag_push_force': data[19],
                    'static_push_force': float(data[20].replace(',', '.')),
                    'dynamic_push_force': float(data[21].replace(',', '.')),
                    'max_temper': float(data[22].replace(',', '.')),
                    'speed': float(data[23].replace(',', '.'))
                    }

        except Exception as e:
            self.logger.error(e)

    def _add_data_on_list_graph(self, data_list):
        try:
            return [float(x.replace(',', '.')) for x in data_list]

        except Exception as e:
            self.logger.error(e)
            
    def _add_data_cascade_graph(self, speed=None, recoil=None, comp=None):
        try:
            if speed:
                self.speed_list.append(speed)
            if recoil:
                self.recoil_list.append(recoil)
            if comp:
                self.comp_list.append(comp)
                            
        except Exception as e:
            self.logger.error(e)
            
    def _add_data_temper_graph(self, data_list):
        try:
            recoil_list = []
            comp_list = []
            for value in data_list:
                value = value.strip('\'\"')
                value = value.replace(',', '.')
                value = value.split('|')
                recoil, comp = float(value[0]), float(value[1])
                recoil_list.append(recoil)
                comp_list.append(comp)
            
            return recoil_list, comp_list
                
        except Exception as e:
            self.logger.error(e)
