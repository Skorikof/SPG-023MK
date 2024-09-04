# -*- coding: utf-8 -*-
import os.path
from pathlib import Path
from datetime import datetime


class FileArchive:
    def __init__(self):
        self.tests = []


class TestArchive:
    def __init__(self):
        self.test_id = ''
        self.time = ''
        self.data_arch = ''
        self.operator = ''
        self.rank = ''
        self.name = ''
        self.serial_number = ''
        self.min_len = ''
        self.max_len = ''
        self.min_comp = ''
        self.max_comp = ''
        self.min_recoil = ''
        self.max_recoil = ''
        self.push_force = ''
        self.speed = ''
        self.temper = ''
        self.graph = []
        self.move_list = []
        self.force_list = []


class ReadArchive:
    def __init__(self):
        self.files_dir = None
        self.files_arr = []
        self.files_name_arr = []
        self.files_name_sort = []
        self.count_files = 0

        self.struct = None
        self.count_tests = -1
        self.index_archive = None
        self.glob_arr = None

    def init_arch(self):
        try:
            source_dir = Path('archive/')
            self.files_dir = source_dir.glob('*.csv')

            for i in self.files_dir:
                self.count_files += 1
                self.files_arr.append(i)
                self.files_name_arr.append(i.stem)
                self.files_name_sort.append(i.stem)

            """сортировка списка файлов по дате"""
            self.files_name_sort.sort(key=lambda date: datetime.strptime(date, "%d.%m.%Y"), reverse=True)

        except Exception as e:
            print(str(e))

    def select_file(self, data):
        try:
            self.struct = FileArchive()
            self.count_tests = -1

            self.index_archive = self.files_name_arr.index(data)

            with open(self.files_arr[self.index_archive]) as f:
                self.glob_arr = f.readlines()
                for i in range(len(self.glob_arr)):
                    flag_data_grf = True
                    if self.glob_arr[i].find('Испытание') >= 0:
                        self.count_tests += 1
                        flag_data_grf = False
                        self.struct.tests.append(TestArchive())
                        temp_val = self.glob_arr[i].split(';')
                        self.struct.tests[self.count_tests].test_id = temp_val[1][:-1]

                    if self.glob_arr[i].find('Время') >= 0:
                        flag_data_grf = False
                        temp_val = self.glob_arr[i].split(';')
                        self.struct.tests[self.count_tests].time = temp_val[1][:-1]
                        self.struct.tests[self.count_tests].date_arch = data

                    if self.glob_arr[i].find('Оператор') >= 0:
                        flag_data_grf = False
                        temp_val = self.glob_arr[i].split(';')
                        self.struct.tests[self.count_tests].operator = temp_val[1][:-1]

                    if self.glob_arr[i].find('Серийный номер') >= 0:
                        flag_data_grf = False
                        temp_val = self.glob_arr[i].split(';')
                        self.struct.tests[self.count_tests].serial_number = temp_val[1][:-1]

                    if self.glob_arr[i].find('Наименование') >= 0:
                        flag_data_grf = False
                        temp_val = self.glob_arr[i].split(';')
                        self.struct.tests[self.count_tests].name = temp_val[1][:-1]

                    if self.glob_arr[i].find('Тип испытания') >= 0:
                        flag_data_grf = False
                        temp_val = self.glob_arr[i].split(';')
                        self.struct.tests[self.count_tests].type_test = temp_val[1][:-1]

                    if self.glob_arr[i].find('Максимальная длина') >= 0:
                        flag_data_grf = False
                        temp_val = self.glob_arr[i].split(';')
                        self.struct.tests[self.count_tests].max_len = temp_val[1][:-1]

                    if self.glob_arr[i].find('Минимальная длина') >= 0:
                        flag_data_grf = False
                        temp_val = self.glob_arr[i].split(';')
                        self.struct.tests[self.count_tests].min_len = temp_val[1][:-1]

                    if self.glob_arr[i].find('Скорость') >= 0:
                        flag_data_grf = False
                        temp_val = self.glob_arr[i].split(';')
                        self.struct.tests[self.count_tests].speed = temp_val[1][:-1]

                    if self.glob_arr[i].find('Мин усилие сжатия') >= 0:
                        flag_data_grf = False
                        temp_val = self.glob_arr[i].split(';')
                        self.struct.tests[self.count_tests].min_comp = temp_val[1][:-1]

                    if self.glob_arr[i].find('Макс усилие сжатия') >= 0:
                        flag_data_grf = False
                        temp_val = self.glob_arr[i].split(';')
                        self.struct.tests[self.count_tests].max_comp = temp_val[1][:-1]

                    if self.glob_arr[i].find('Мин усилие отбоя') >= 0:
                        flag_data_grf = False
                        temp_val = self.glob_arr[i].split(';')
                        self.struct.tests[self.count_tests].min_recoil = temp_val[1][:-1]

                    if self.glob_arr[i].find('Макс усилие отбоя') >= 0:
                        flag_data_grf = False
                        temp_val = self.glob_arr[i].split(';')
                        self.struct.tests[self.count_tests].max_recoil = temp_val[1][:-1]

                    if self.glob_arr[i].find('Выталкивающая сила') >= 0:
                        flag_data_grf = False
                        temp_val = self.glob_arr[i].split(';')
                        self.struct.tests[self.count_tests].push_force = temp_val[1][:-1]

                    if self.glob_arr[i].find('Макс температура') >= 0:
                        flag_data_grf = False
                        temp_val = self.glob_arr[i].split(';')
                        self.struct.tests[self.count_tests].temper = temp_val[1][:-1]

                    if self.glob_arr[i].find('Усилие') >= 0:
                        flag_data_grf = False

                    if flag_data_grf:
                        self.struct.tests[self.count_tests].graph.append(self.glob_arr[i][:-1])

        except Exception as e:
            print(str(e))

    def save_test_in_archive(self, obj):
        try:
            flag_add_title = True
            nam_f = f'{datetime.now().day:02}.{datetime.now().month:02}.{datetime.now().year}.csv'
            time_t = datetime.now().strftime('%H:%M:%S')
            path_file = 'archive/' + nam_f
            if os.path.isfile(path_file):
                flag_add_title = False

            with open('archive/' + nam_f, 'a') as file_arch:
                if flag_add_title:
                    str_t = (f'Время;'
                             f'ФИО оператора;'
                             f'Должность;'
                             f'Тип испытания;'
                             f'Название гасителя;'
                             f'Серийный номер;'
                             f'Длина в сжатом состоянии, мм;'
                             f'Длина в разжатом состоянии, мм;'
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
                             f'Выталкивающая сила, кгс;'
                             f'Макс температура, °С;'
                             f'Скорость испытания, м/с;'
                             f'Перемещение, мм/Усилие, кгс')
                    file_arch.write(str_t + '\n')

                write_name = (f'{time_t};'
                              f'{obj["operator"]["name"]};'
                              f'{obj["operator"]["rank"]};'
                              f'{obj["type_test"]};'
                              f'{obj["amort"].name};'
                              f'{obj["serial"]};')

                write_str = (f'{obj["amort"].min_length};'
                             f'{obj["amort"].max_length};'
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
                             f'{obj["push_force"]};'
                             f'{obj["max_temperature"]};')

                write_str = write_str.replace('.', '.')

                if obj['type_test'] == 'lab':
                    speed = str(obj['speed']).replace('.', ',')
                    move = self._change_data_for_save(obj['move_graph'])
                    force = self._change_data_for_save(obj['force_graph'])

                    write_data = (f'{speed};{move};\n'
                                  f';;;;;;;;;;;;;;;;;;;;;;{force};\n')

                    file_arch.write(write_name + write_str + write_data)

                elif obj['type_test'] == 'lab_cascade':
                    write_data = ''

                    for key, value in obj['cascade_graph'].items():
                        speed = str(value.speed).replace('.', ',')
                        move = self._change_data_for_save(value.move)
                        force = self._change_data_for_save(value.force)

                        if key == 1:
                            write_data = write_data + (f'{speed};{move};\n'
                                                       f';;;;;;;;;;;;;;;;;;;;;;{force};\n')

                        else:
                            write_data = write_data + (f';;;;;;;;;;;;;;;;;;;;;{speed};{move};\n'
                                                       f';;;;;;;;;;;;;;;;;;;;;;{force};\n')

                    file_arch.write(write_name + write_str + write_data)

        except Exception as e:
            print(f'Exception in archive - {e}')

    def _change_data_for_save(self, data: list):
        try:
            data = str(data)
            data = data[1:-1]
            data = data.replace(' ', '')
            data = data.replace(',', ';')
            data = data.replace('.', ',')

            return data

        except Exception as e:
            print(f'Exception in archive/_change_data_for_save - {e}')
