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
            self.speed = 0
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
                archive_str = f.readlines()
                for i in archive_str:
                    archive_list = i.split(';')

                    if archive_list[0] == 'Время':
                        continue

                    else:
                        self._pars_str_archive(archive_list)

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
                self.temper[self.ind_temp].temper_graph = self._add_data_on_list_graph(archive_list[24:-1])
                
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
                if self.flag_new_cascade:
                    self.flag_new_cascade = False
                    self.cascade.append(CascTest())
                    self._fill_obj_archive_data(self.cascade[self.ind_casc], archive_list[:24])
                    self.cascade[self.ind_casc].speed_list.append(self.speed)
            
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
            self.speed = float(data[23].replace(',', '.'))

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

# class FileArchive:
#     def __init__(self):
#         self.tests = []
#         self.conv = []
#         self.cascade = {}
#         self.temper = []


# class TestArchive:
#     def __init__(self):
#         self.index = -1
#         self.time_test = ''
#         self.operator_name = ''
#         self.operator_rank = ''
#         self.type_test = ''
#         self.serial_number = ''
#         self.flag_push_force = ''
#         self.static_push_force = ''
#         self.dynamic_push_force = ''
#         self.speed = ''
#         self.move_list = []
#         self.force_list = []
#         self.temper_list = []
#         self.temper_force_list = []

#         self.amort = DataAmort()


# class TestCascade:
#     def __init__(self):
#         self.cascade = {}


# class ReadArchive:
#     def __init__(self):
#         self.logger = my_logger.get_logger(__name__)
#         self.files_dir = None
#         self.files_arr = []
#         self.files_name_arr = []
#         self.files_name_sort = []
#         self.count_files = 0
#         self.cascade_list = []

#         self.struct = None
#         self.type_graph = None
#         self.ind_test = -1
#         self.ind_test_conv = -1
#         self.ind_casc = 0
#         self.ind_temp = -1
#         self.index_archive = None
#         self.glob_arr = None

#     def init_arch(self):
#         try:
#             self.files_arr = []
#             self.files_name_arr = []
#             self.files_name_sort = []
#             self.count_files = 0

#             source_dir = Path('archive/')
#             self.files_dir = source_dir.glob('*.csv')

#             for i in self.files_dir:
#                 self.count_files += 1
#                 self.files_arr.append(i)
#                 self.files_name_arr.append(i.stem)
#                 self.files_name_sort.append(i.stem)

#             """сортировка списка файлов по дате"""
#             self.files_name_sort.sort(key=lambda date: datetime.strptime(date, "%d.%m.%Y"), reverse=True)

#         except Exception as e:
#             self.logger.error(e)

#     def select_file(self, data):
#         try:
#             self.ind_test = -1
#             self.ind_test_conv = -1
#             self.ind_casc = 1
#             self.ind_temp = -1
#             self.cascade_list = []
#             self.struct = FileArchive()

#             self.index_archive = self.files_name_arr.index(data)

#             with open(self.files_arr[self.index_archive], encoding='utf-8') as f:
#                 archive_str = f.readlines()
#                 for i in archive_str:
#                     archive_list = i.split(';')

#                     if archive_list[0] == 'Время':
#                         continue

#                     else:
#                         self._pars_str_archive(archive_list)

#         except Exception as e:
#             self.logger.error(e)

#     def _pars_str_archive(self, archive_list):
#         try:
#             if archive_list[0] == 'end_test':
#                 if self.type_graph == 'lab_cascade':
#                     self.struct.cascade[self.ind_casc] = self.cascade_list[:]
#                     self.ind_casc += 1
#                     self.cascade_list = []

#             else:
#                 if not archive_list[0] == '*':
#                     self.type_graph = archive_list[3]

#                     if self.type_graph == 'temper':
#                         self.ind_temp += 1
#                         self.struct.temper.append(TestArchive())
#                         self._fill_obj_archive_data(self.struct.temper[self.ind_temp], archive_list)

#                         temp_list = self._add_data_on_list_graph(archive_list[24:-1])
#                         self.struct.temper[self.ind_temp].temper_graph = temp_list[:]

#                     elif self.type_graph == 'conv':
#                         self.ind_test_conv += 1
#                         self.struct.conv.append(TestArchive())
#                         self._fill_obj_archive_data(self.struct.conv[self.ind_test_conv], archive_list)
#                         temp_list = self._add_data_on_list_graph(archive_list[24:-1])
#                         self.struct.conv[self.ind_test_conv].move_list = temp_list[:]

#                     else:
#                         self.ind_test += 1
#                         self.struct.tests.append(TestArchive())

#                         self._fill_obj_archive_data(self.struct.tests[self.ind_test], archive_list)

#                         temp_list = self._add_data_on_list_graph(archive_list[24:-1])

#                         self.struct.tests[self.ind_test].move_list = temp_list[:]

#                 elif archive_list[0] == '*':
#                     if self.type_graph == 'temper':
#                         self.struct.temper[self.ind_temp].temper_force_graph = archive_list[24:-1]

#                     elif self.type_graph == 'conv':
#                         temp_list = self._add_data_on_list_graph(archive_list[24:-1])
#                         self.struct.conv[self.ind_test_conv].force_list = temp_list[:]

#                     else:
#                         temp_list = self._add_data_on_list_graph(archive_list[24:-1])

#                         self.struct.tests[self.ind_test].force_list = temp_list[:]

#                         if self.struct.tests[self.ind_test].type_test == 'lab_cascade':
#                             self.cascade_list.append(self.struct.tests[self.ind_test])

#         except Exception as e:
#             self.logger.error(e)

#     def _fill_obj_archive_data(self, obj, data):
#         try:
#             obj.time_test = data[0]
#             obj.operator_name = data[1]
#             obj.operator_rank = data[2]
#             obj.type_test = data[3]
#             obj.amort.name = data[4]
#             obj.serial_number = data[5]
#             obj.amort.min_length = data[6].replace(',', '.')
#             obj.amort.max_length = data[7].replace(',', '.')
#             obj.amort.hod = data[8]
#             obj.amort.speed_one = data[9].replace(',', '.')
#             obj.amort.min_recoil = data[10].replace(',', '.')
#             obj.amort.max_recoil = data[11].replace(',', '.')
#             obj.amort.min_comp = data[12].replace(',', '.')
#             obj.amort.max_comp = data[13].replace(',', '.')
#             obj.amort.speed_two = data[14].replace(',', '.')
#             obj.amort.min_recoil_2 = data[15].replace(',', '.')
#             obj.amort.max_recoil_2 = data[16].replace(',', '.')
#             obj.amort.min_comp_2 = data[17].replace(',', '.')
#             obj.amort.max_comp_2 = data[18].replace(',', '.')
#             obj.flag_push_force = data[19]
#             obj.static_push_force = data[20].replace(',', '.')
#             obj.dynamic_push_force = data[21].replace(',', '.')
#             obj.amort.max_temper = data[22].replace(',', '.')
#             obj.speed = data[23].replace(',', '.')

#         except Exception as e:
#             self.logger.error(e)

#     def _add_data_on_list_graph(self, data_list):
#         try:
#             return [float(x.replace(',', '.')) for x in data_list]

#         except Exception as e:
#             self.logger.error(e)


class SaveArchive:
    def __init__(self):
        self.logger = my_logger.get_logger(__name__)

    def save_test_in_archive(self, obj):
        try:
            flag_add_title = True
            nam_f = f'{datetime.now().day:02}.{datetime.now().month:02}.{datetime.now().year}.csv'
            time_t = datetime.now().strftime('%H:%M:%S')
            path_file = 'archive/' + nam_f
            if os.path.isfile(path_file):
                flag_add_title = False

            with open('archive/' + nam_f, 'a', encoding='utf-8') as file_arch:
                if flag_add_title:
                    str_t = (f'Время;'
                             f'ФИО оператора;'
                             f'Должность;'
                             f'Тип испытания;'
                             f'Название гасителя;'
                             f'Серийный номер;'
                             f'Длина в сжатом состоянии, мм;'
                             f'Длина в разжатом состоянии, мм;'
                             f'Ход испытания, мм;'
                             f'1-я скорость исытания, м/с;'
                             f'Мин усилие отбоя, кгс;'
                             f'Макс усилие отбоя, кгс;'
                             f'Мин усилие сжатия, кгс;'
                             f'Макс усилие сжатия, кгс;'
                             f'2-я скорость испытания, м/с;'
                             f'Мин усилие отбоя, кгс;'
                             f'Макс усилие отбоя, кгс;'
                             f'Мин усилие сжатия, кгс;'
                             f'Макс усилие сжатия, кгс;'
                             f'Флаг выталкивающей силы;'
                             f'Выталкивающая сила статичная, кгс;'
                             f'Выталкивающая сила динамическая, кгс;'
                             f'Макс температура, °С;'
                             f'Скорость испытания, м/с;'
                             f'Перемещение, мм(Температура, ℃)/Усилие, кгс')
                    file_arch.write(str_t + '\n')

                write_name = (f'{time_t};'
                              f'{obj["operator"]["name"]};'
                              f'{obj["operator"]["rank"]};'
                              f'{obj["type_test"]};'
                              f'{obj["amort"].name};'
                              f'{obj["serial"]};')

                write_str = (f'{obj["amort"].min_length};'
                             f'{obj["amort"].max_length};'
                             f'{obj["amort"].hod};'
                             f'{obj["amort"].speed_one};'
                             f'{obj["amort"].min_recoil};'
                             f'{obj["amort"].max_recoil};'
                             f'{obj["amort"].min_comp};'
                             f'{obj["amort"].max_comp};'
                             f'{obj["amort"].speed_two};'
                             f'{obj["amort"].min_recoil_2};'
                             f'{obj["amort"].max_recoil_2};'
                             f'{obj["amort"].min_comp_2};'
                             f'{obj["amort"].max_comp_2};'
                             f'{obj["flag_push_force"]};'
                             f'{obj["static_push_force"]};'
                             f'{obj["dynamic_push_force"]};'
                             f'{obj["max_temperature"]};')

                write_str = write_str.replace('.', ',')

                speed = str(obj['speed']).replace('.', ',')

                if obj['type_test'] == 'temper':
                    data_first = self._change_data_for_save(obj['temper_graph'])
                    temper_force = []
                    for i in range(len(obj['temper_graph'])):
                        temper_force.append(f'{obj["temper_recoil_graph"][i]}|{obj["temper_comp_graph"][i]}')
                    data_second = self._change_data_for_save(temper_force)

                else:
                    data_first = self._change_data_for_save(obj['move_graph'])
                    data_second = self._change_data_for_save(obj['force_graph'])

                write_data = (f'{speed};{data_first};\n'
                              f'*;;;;;;;;;;;;;;;;;;;;;;;;{data_second};\n')

                file_arch.write(write_name + write_str + write_data)

        except Exception as e:
            self.logger.error(e)

    def _change_data_for_save(self, data: list):
        try:
            data = str(data)
            data = data[1:-1]
            data = data.replace(' ', '')
            data = data.replace(',', ';')
            data = data.replace('.', ',')

            return data

        except Exception as e:
            self.logger.error(e)

    def write_end_test_in_archive(self):
        try:
            nam_f = f'{datetime.now().day:02}.{datetime.now().month:02}.{datetime.now().year}.csv'

            with open('archive/' + nam_f, 'a', encoding='utf-8') as file_arch:
                str_t = f'end_test;\n'
                file_arch.write(str_t)

        except Exception as e:
            self.logger.error(e)
