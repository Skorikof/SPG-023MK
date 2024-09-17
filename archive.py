# -*- coding: utf-8 -*-
import os.path
from pathlib import Path
from datetime import datetime
from amorts import DataAmort
from my_obj.graph_lab_cascade import DataGraphCascade


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
        self.push_force = ''
        self.speed = ''
        self.move_list = []
        self.force_list = []

        self.amort = DataAmort()

        self.cascade = {}


class ReadArchive:
    def __init__(self):
        self.files_dir = None
        self.files_arr = []
        self.files_name_arr = []
        self.files_name_sort = []
        self.count_files = 0

        self.struct = None
        self.ind_test = -1
        self.ind_casc = 0
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
            self.ind_test = -1
            self.ind_casc = 0
            self.struct = FileArchive()

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

    def _pars_str_archive(self, archive_list):
        try:
            if not archive_list[0] == '*':
                self.ind_test += 1
                self.struct.tests.append(TestArchive())

                self.struct.tests[self.ind_test].time_test = archive_list[0]
                self.struct.tests[self.ind_test].operator_name = archive_list[1]
                self.struct.tests[self.ind_test].operator_rank = archive_list[2]
                self.struct.tests[self.ind_test].amort.name = archive_list[3]
                self.struct.tests[self.ind_test].serial_number = archive_list[4]
                self.struct.tests[self.ind_test].amort.min_length = archive_list[5].replace(',', '.')
                self.struct.tests[self.ind_test].amort.max_length = archive_list[6].replace(',', '.')
                self.struct.tests[self.ind_test].amort.hod = archive_list[7]
                self.struct.tests[self.ind_test].amort.speed_one = archive_list[8].replace(',', '.')
                self.struct.tests[self.ind_test].amort.min_recoil = archive_list[9].replace(',', '.')
                self.struct.tests[self.ind_test].amort.max_recoil = archive_list[10].replace(',', '.')
                self.struct.tests[self.ind_test].amort.min_comp = archive_list[11].replace(',', '.')
                self.struct.tests[self.ind_test].amort.max_comp = archive_list[12].replace(',', '.')
                self.struct.tests[self.ind_test].amort.speed_two = archive_list[13].replace(',', '.')
                self.struct.tests[self.ind_test].amort.min_recoil_2 = archive_list[14].replace(',', '.')
                self.struct.tests[self.ind_test].amort.max_recoil_2 = archive_list[15].replace(',', '.')
                self.struct.tests[self.ind_test].amort.min_comp_2 = archive_list[16].replace(',', '.')
                self.struct.tests[self.ind_test].amort.max_comp_2 = archive_list[17].replace(',', '.')
                self.struct.tests[self.ind_test].flag_push_force = archive_list[18]
                self.struct.tests[self.ind_test].push_force = archive_list[19].replace(',', '.')
                self.struct.tests[self.ind_test].amort.max_temper = archive_list[20].replace(',', '.')

                self.struct.tests[self.ind_test].speed = archive_list[21].replace(',', '.')

                temp_list = self._add_data_on_list_graph(archive_list[22:-1])

                self.struct.tests[self.ind_test].move_list = temp_list[:]

            elif archive_list[0] == '*':
                temp_list = self._add_data_on_list_graph(archive_list[22:-1])

                self.struct.tests[self.ind_test].force_list = temp_list[:]

        except Exception as e:
            print(f'Exception in archive/_pars_str_archihve - {e}')

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
                             f'Выталкивающая сила, кгс;'
                             f'Макс температура, °С;'
                             f'Скорость испытания, м/с;'
                             f'Перемещение, мм/Усилие, кгс')
                    file_arch.write(str_t + '\n')

                write_name = (f'{time_t};'
                              f'{obj["operator"]["name"]};'
                              f'{obj["operator"]["rank"]};'
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
                             f'{obj["push_force"]};'
                             f'{obj["max_temperature"]};')

                write_str = write_str.replace('.', ',')

                speed = str(obj['speed']).replace('.', ',')
                move = self._change_data_for_save(obj['move_graph'])
                force = self._change_data_for_save(obj['force_graph'])

                write_data = (f'{speed};{move};\n'
                              f'*;;;;;;;;;;;;;;;;;;;;;;{force};\n')

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
