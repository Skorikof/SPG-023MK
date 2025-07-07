# -*- coding: utf-8 -*-
import os.path
from pathlib import Path
from datetime import datetime

from logger import my_logger
from amorts import DataAmort


class BaseTest:
    def __init__(self):
        self.amort = DataAmort()
        self.index = -1
        self.time_test = ''
        self.operator_name = ''
        self.operator_rank = ''
        self.type_test = ''
        self.serial_number = ''
        self.flag_push_force = ''
        self.static_push_force = ''
        self.dynamic_push_force = ''
        self.speed = ''


class LabTest(BaseTest):
    def __init__(self):
        super().__init__()
        self.move_list = []
        self.force_list = []
        
        
class ConvTest(BaseTest):
    def __init__(self):
        super().__init__()
        self.move_list = []
        self.force_list = []
        
        
class TempTest(BaseTest):
    def __init__(self):
        super().__init__()
        self.temper_list = []
        self.recoil_list = []
        self.comp_list = []
        
        
class CascTest(BaseTest):
    def __init__(self):
        super().__init__()
        self.recoil_list = []
        self.comp_list = []
        self.speed_list = []


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
            self.type_test = ''
            self.ind_lab = -1
            self.ind_conv = -1
            self.ind_temp = -1
            self.ind_casc = 0
            self.lab = []
            self.conv = []
            self.temper = []
            self.cascade = []
            self.flag_new_cascade = True
        
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
                    self.ind_casc += 1
                    self.flag_new_cascade = True

            else:
                if not archive_list[0] == '*':
                    self._pars_first_data(archive_list)
                            
                elif archive_list[0] == '*':
                    self._pars_second_data(archive_list[24:-1])

        except Exception as e:
            self.logger.error(e)
            
    def _pars_first_data(self, archive_list):
        try:
            self.type_test = archive_list[3]
            if self.type_test == 'temper':
                self.ind_temp += 1
                self.temper.append(TempTest())
                self._fill_obj_archive_data(self.temper[self.ind_temp], archive_list[:24])
                self.temper[self.ind_temp].temper_list = self._add_data_on_list_graph(archive_list[24:-1])
                
            elif self.type_test == 'lab':
                self.ind_lab += 1
                self.lab.append(LabTest())
                self._fill_obj_archive_data(self.lab[self.ind_lab], archive_list[:24])
                self.lab[self.ind_lab].move_list = self._add_data_on_list_graph(archive_list[24:-1])

            elif self.type_test == 'conv':
                self.ind_conv += 1
                self.conv.append(ConvTest())
                self._fill_obj_archive_data(self.conv[self.ind_conv], archive_list[:24])
                self.conv[self.ind_conv].move_list = self._add_data_on_list_graph(archive_list[24:-1])
                
            elif self.type_test == 'lab_cascade':
                self.ind_lab += 1
                self.lab.append(LabTest())
                self._fill_obj_archive_data(self.lab[self.ind_lab], archive_list[:24])
                self.lab[self.ind_lab].move_list = self._add_data_on_list_graph(archive_list[24:-1])
                
                if self.flag_new_cascade:
                    self.flag_new_cascade = False
                    self.cascade.append(CascTest())
                    self._fill_obj_archive_data(self.cascade[self.ind_casc], archive_list[:24])
                speed = float(archive_list[23].replace(',', '.'))
                self.cascade[self.ind_casc].speed_list.append(speed)
            
        except Exception as e:
            self.logger.error(e)
            
    def _pars_second_data(self, archive_list):
        try:
            if self.type_test == 'temper':
                        recoil, comp = self._add_data_temper_graph(archive_list)
                        self.temper[self.ind_temp].recoil_list = recoil
                        self.temper[self.ind_temp].comp_list = comp
                        
            elif self.type_test == 'lab':
                self.lab[self.ind_lab].force_list = self._add_data_on_list_graph(archive_list)

            elif self.type_test == 'conv':
                self.conv[self.ind_conv].force_list = self._add_data_on_list_graph(archive_list)

            elif self.type_test == 'lab_cascade':
                self.lab[self.ind_lab].force_list = self._add_data_on_list_graph(archive_list)
                force_list = self._add_data_on_list_graph(archive_list)
                self.cascade[self.ind_casc].recoil_list.append(max(force_list))
                self.cascade[self.ind_casc].comp_list.append(abs(min(force_list)))
            
        except Exception as e:
            self.logger.error(e)

    def _fill_obj_archive_data(self, obj, data):
        try:
            obj.time_test = data[0]
            obj.operator_name = data[1]
            obj.operator_rank = data[2]
            obj.type_test = data[3]
            obj.amort.name = data[4]
            obj.serial_number = data[5]
            obj.amort.min_length = data[6].replace(',', '.')
            obj.amort.max_length = data[7].replace(',', '.')
            obj.amort.hod = data[8]
            obj.amort.speed_one = data[9].replace(',', '.')
            obj.amort.min_recoil = data[10].replace(',', '.')
            obj.amort.max_recoil = data[11].replace(',', '.')
            obj.amort.min_comp = data[12].replace(',', '.')
            obj.amort.max_comp = data[13].replace(',', '.')
            obj.amort.speed_two = data[14].replace(',', '.')
            obj.amort.min_recoil_2 = data[15].replace(',', '.')
            obj.amort.max_recoil_2 = data[16].replace(',', '.')
            obj.amort.min_comp_2 = data[17].replace(',', '.')
            obj.amort.max_comp_2 = data[18].replace(',', '.')
            obj.flag_push_force = data[19]
            obj.static_push_force = data[20].replace(',', '.')
            obj.dynamic_push_force = data[21].replace(',', '.')
            obj.amort.max_temper = data[22].replace(',', '.')
            obj.speed = data[23].replace(',', '.')

        except Exception as e:
            self.logger.error(e)

    def _add_data_on_list_graph(self, data_list):
        try:
            return [float(x.replace(',', '.')) for x in data_list]

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
