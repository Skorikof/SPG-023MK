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
        self.serial_number = ''
        self.specif_damp = []
        self.conclusion = ''
        self.graph = []
        self.resistance = ''


class ReadArchive:
    def __init__(self):
        self.files_dir = None
        self.files_arr = []
        self.files_name_arr = []
        self.files_name_sort = []
        self.count_files = 0

        self.struct = None
        self.count_tests = None
        self.index_archive = None
        self.glob_arr = None

        self.init_arch()

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
                        self.struct.tests[self.count_tests].specif_damp.append(temp_val[1][:-1])

                    if self.glob_arr[i].find('Максимальная длина') >= 0:
                        flag_data_grf = False
                        temp_val = self.glob_arr[i].split(';')
                        self.struct.tests[self.count_tests].specif_damp.append(temp_val[1][:-1])

                    if self.glob_arr[i].find('Минимальная длина') >= 0:
                        flag_data_grf = False
                        temp_val = self.glob_arr[i].split(';')
                        self.struct.tests[self.count_tests].specif_damp.append(temp_val[1][:-1])

                    if self.glob_arr[i].find('Кронштейн') >= 0:
                        flag_data_grf = False
                        temp_val = self.glob_arr[i].split(';')
                        self.struct.tests[self.count_tests].specif_damp.append(temp_val[1][:-1])

                    if self.glob_arr[i].find('Скорость') >= 0:
                        flag_data_grf = False
                        temp_val = self.glob_arr[i].split(';')
                        self.struct.tests[self.count_tests].specif_damp.append(temp_val[1][:-1])

                    if self.glob_arr[i].find('Угол') >= 0:
                        flag_data_grf = False
                        temp_val = self.glob_arr[i].split(';')
                        self.struct.tests[self.count_tests].specif_damp.append(temp_val[1][:-1])

                    if self.glob_arr[i].find('Мин усилие сжатия') >= 0:
                        flag_data_grf = False
                        temp_val = self.glob_arr[i].split(';')
                        self.struct.tests[self.count_tests].specif_damp.append(temp_val[1][:-1])

                    if self.glob_arr[i].find('Макс усилие сжатия') >= 0:
                        flag_data_grf = False
                        temp_val = self.glob_arr[i].split(';')
                        self.struct.tests[self.count_tests].specif_damp.append(temp_val[1][:-1])

                    if self.glob_arr[i].find('Мин усилие отбоя') >= 0:
                        flag_data_grf = False
                        temp_val = self.glob_arr[i].split(';')
                        self.struct.tests[self.count_tests].specif_damp.append(temp_val[1][:-1])

                    if self.glob_arr[i].find('Макс усилие отбоя') >= 0:
                        flag_data_grf = False
                        temp_val = self.glob_arr[i].split(';')
                        self.struct.tests[self.count_tests].specif_damp.append(temp_val[1][:-1])

                    if self.glob_arr[i].find('Макс температура') >= 0:
                        flag_data_grf = False
                        temp_val = self.glob_arr[i].split(';')
                        self.struct.tests[self.count_tests].specif_damp.append(temp_val[1][:-1])

                    if self.glob_arr[i].find('Сопротивление') >= 0:
                        flag_data_grf = False
                        temp_val = self.glob_arr[i].split(';')
                        self.struct.tests[self.count_tests].resistance = temp_val[1][:-1]

                    if self.glob_arr[i].find('Усилие') >= 0:
                        flag_data_grf = False

                    if flag_data_grf:
                        self.struct.tests[self.count_tests].graph.append(self.glob_arr[i][:-1])

        except Exception as e:
            print(str(e))
