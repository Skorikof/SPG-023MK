import os
from datetime import datetime
from PySide6.QtCore import QObject, QRunnable, Signal, Slot


class Signals(QObject):
    thread_err = Signal(str)
    write_archive = Signal(str)
    

class WriterArchive(QRunnable):
    signals = Signals()
    
    def __init__(self, tag=None, data=None):
        super(WriterArchive, self).__init__()
        self.tag = tag
        self.data = data
        
    @Slot()
    def run(self):
        try:
            if self.tag:
                nam_f = f'{datetime.now().day:02}.{datetime.now().month:02}.{datetime.now().year}.csv'
                self._check_exist_file(nam_f)
                
                if self.tag == 'data':
                    self._save_test_in_archive(nam_f, self.data)
                elif self.tag == 'end_test':
                    self._write_end_test_in_archive(nam_f)
            else:
                pass
            
        except Exception as e:
            self.signals.thread_err.emit(f'ERROR in thread writer_archive --> {e}')
            
    def _check_exist_file(self, nam_f):
        try:
            path_file = 'archive/' + nam_f
            if not os.path.isfile(path_file):
                self._create_file(nam_f)
            
        except Exception as e:
            self.signals.thread_err.emit(f'ERROR in thread writer_archive/_check_exist_file --> {e}')
            
    def _create_file(self, nam_f):
        try:
            with open('archive/' + nam_f, 'a', encoding='utf-8') as file_arch:
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
            
        except Exception as e:
            self.signals.thread_err.emit(f'ERROR in thread writer_archive/_create_file --> {e}')
            
    def _save_test_in_archive(self, nam_f, obj):
        try:
            time_t = datetime.now().strftime('%H:%M:%S')
            with open('archive/' + nam_f, 'a', encoding='utf-8') as file_arch:
                write_name = (f'{time_t};'
                              f'{obj["operator_name"]};'
                              f'{obj["operator_rank"]};'
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
            
            self.signals.write_archive.emit(self.tag)
            self.tag = None

        except Exception as e:
            self.signals.thread_err.emit(f'ERROR in thread writer_archive/_save_test_in_archive --> {e}')

    def _change_data_for_save(self, data: list):
        try:
            data = str(data)
            data = data[1:-1]
            data = data.replace(' ', '')
            data = data.replace(',', ';')
            data = data.replace('.', ',')

            return data

        except Exception as e:
            self.signals.thread_err.emit(f'ERROR in thread writer_archive/_change_data_for_save --> {e}')

    def _write_end_test_in_archive(self, nam_f):
        try:
            with open('archive/' + nam_f, 'a', encoding='utf-8') as file_arch:
                str_t = f'end_test;\n'
                file_arch.write(str_t)
                
            self.signals.write_archive.emit(self.tag)
            self.tag = None

        except Exception as e:
            self.signals.thread_err.emit(f'ERROR in thread writer_archive/_write_end_test_in_archive --> {e}')
    