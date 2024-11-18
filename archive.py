# -*- coding: utf-8 -*-
import os.path
import random
from pathlib import Path
from datetime import datetime
from amorts import DataAmort


class FileArchive:
    def __init__(self):
        self.tests = []


class TestArchive:
    def __init__(self):
        self.time_test = ''
        self.operator_name = ''
        self.operator_rank = ''
        self.type_test = ''
        self.serial_number = ''
        self.flag_push_force = ''
        self.static_push_force = ''
        self.dynamic_push_force = ''
        self.speed = ''
        self.move_list = []
        self.force_list = []
        self.temper_list = []

        self.amort = DataAmort()


class TestCascade:
    def __init__(self):
        self.cascade = {}


class ReadArchive:
    def __init__(self):
        self.files_dir = None
        self.files_arr = []
        self.files_name_arr = []
        self.files_name_sort = []
        self.count_files = 0
        self.cascade_list = []

        self.struct = None
        self.struct_cascade = TestCascade()
        self.struct_temper = None
        self.ind_test = -1
        self.ind_casc = 0
        self.ind_temp = -1
        self.index_archive = None
        self.glob_arr = None

    def init_arch(self):
        try:
            self.files_arr = []
            self.files_name_arr = []
            self.files_name_sort = []
            self.count_files = 0

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
            self.ind_test = -1
            self.ind_casc = 1
            self.ind_temp = -1
            self.cascade_list = []
            self.struct = FileArchive()
            self.struct_temper = FileArchive()

            self.index_archive = self.files_name_arr.index(data)

            with open(self.files_arr[self.index_archive]) as f:
                archive_str = f.readlines()
                for i in archive_str:
                    archive_list = i.split(';')

                    if archive_list[0] == 'Время':
                        continue

                    else:
                        self._pars_str_archive(archive_list)

        except Exception as e:
            print(f'Exception in archive/select_file - {e}')

    # FIXME
    def _pars_str_archive(self, archive_list):
        try:
            if not archive_list[0] == '*' and not archive_list[0] == 'end_test':
                if archive_list[3] == 'temper':
                    self.ind_temp += 1
                    self.struct_temper.tests.append()

                else:
                    self.ind_test += 1
                    self.struct.tests.append(TestArchive())

                    self._fill_obj_archive_data(self.struct.tests[self.ind_test], archive_list)

                    temp_list = self._add_data_on_list_graph(archive_list[24:-1])

                    self.struct.tests[self.ind_test].move_list = temp_list[:]

            elif archive_list[0] == '*':
                temp_list = self._add_data_on_list_graph(archive_list[24:-1])

                self.struct.tests[self.ind_test].force_list = temp_list[:]

            if self.struct.tests[self.ind_test].type_test == 'lab_cascade':
                self.cascade_list.append(self.struct.tests[self.ind_test])

            if archive_list[0] == 'end_test':
                if self.struct.tests[self.ind_test].type_test == 'lab_cascade':
                    self.struct_cascade.cascade[self.ind_casc] = self.cascade_list[:]
                    self.ind_casc += 1
                    self.cascade_list = []

        except Exception as e:
            print(f'Exception in archive/_pars_str_archihve - {e}')

    # FIXME
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
            print(f'Exception in archive/_fill_obj_archihve_data - {e}')

    def _add_data_on_list_graph(self, data_list):
        try:
            return [float(x.replace(',', '.')) for x in data_list]

        except Exception as e:
            print(f'Exception in archive/_add_data_on_list_graph - {e}')

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
                    data = self._change_data_for_save(obj['temper_graph'])

                else:
                    data = self._change_data_for_save(obj['move_graph'])

                force = self._change_data_for_save(obj['force_graph'])

                write_data = (f'{speed};{data};\n'
                              f'*;;;;;;;;;;;;;;;;;;;;;;;;{force};\n')

                file_arch.write(write_name + write_str + write_data)

        except Exception as e:
            print(f'Exception in archive/save_test_in_archive - {e}')

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

    def write_end_test_in_archive(self):
        try:
            nam_f = f'{datetime.now().day:02}.{datetime.now().month:02}.{datetime.now().year}.csv'

            with open('archive/' + nam_f, 'a') as file_arch:
                str_t = f'end_test;\n'
                file_arch.write(str_t)

        except Exception as e:
            print(f'Exception in archive/_write_end_test_in_archive - {e}')
