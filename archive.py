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
            nam_f = str(datetime.now().day).zfill(2) + '.' + str(datetime.now().month).zfill(2) + \
                    '.' + str(datetime.now().year) + '.csv'
            time_t = datetime.now().strftime('%H:%M:%S')
            with open('archive/' + nam_f, 'a', encoding='cp1251') as file_arch:
                file_arch.write('Испытание; ' + '\n')
                file_arch.write('Время;' + time_t + '\n')
                file_arch.write('Оператор;' + str(obj.rank + ' ' + obj.operator) + '\n')
                file_arch.write('Серийный номер;' + str(obj.serial_number) + '\n')
                file_arch.write('Наименование;' + obj.name + '\n')
                file_arch.write('Максимальная длина;' + str(obj.max_len) + '\n')
                file_arch.write('Минимальная длина;' + str(obj.min_len) + '\n')
                file_arch.write('Скорость;' + str(obj.speed) + '\n')
                file_arch.write('Мин усилие сжатия;' + str(obj.min_comp) + '\n')
                file_arch.write('Макс усилие сжатия;' + str(obj.max_comp) + '\n')
                file_arch.write('Мин усилие отбоя;' + str(obj.min_recoil) + '\n')
                file_arch.write('Макс усилие отбоя;' + str(obj.max_recoil) + '\n')
                file_arch.write('Выталкивающая сила;' + str(obj.push_force) + '\n')
                file_arch.write('Макс температура;' + str(obj.temper) + '\n')
                file_arch.write('Усилие;Перемещение' + '\n')
                for i in range(len(obj.move_list)):
                    val_f = str(obj.force_list[i])
                    val_m = str(obj.move_list[i]).replace('.', ',')
                    file_arch.write(val_m + ';' + val_f + '\n')

        except Exception as e:
            print('{}'.format(e))

    #FIXME
    def save_test_in_archive_new(self):
        try:
            flag_add_title = True
            nam_f = f'{datetime.now().day:02}.{datetime.now().month:02}.{datetime.now().year}.csv'
            time_t = datetime.now().strftime('%H:%M:%S')
            path_file = 'archive/' + nam_f
            if os.path.isfile(path_file):
                flag_add_title = False

            with open('archive/' + nam_f, 'a') as file_arch:
                if flag_add_title:
                    str_t = (f'Время;ФИО оператора;Должность;Название гасителя;Серийный номер;'
                             f'Длина в сжатом состоянии, мм;Длина в разжатом состоянии, мм;'
                             f'Мин усилие отбоя, кгс;Макс усилие отбоя, кгс;Мин усилие сжатия, кгс;'
                             f'Макс усилие сжатия, кгс;Выталкивающая сила, кгс;Макс температура, °С')


        except Exception as e:
            print(f'Exception in archive - {e}')