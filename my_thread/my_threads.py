# -*- coding: utf-8 -*-
import time
# import os
from struct import pack, unpack
from datetime import datetime
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot


# base_dir = os.path.dirname(__file__)
base_dir = 'c:/System'


class Signals(QObject):
    thread_log = pyqtSignal(str)
    thread_err = pyqtSignal(str)
    read_result = pyqtSignal(dict, str)
    write_result = pyqtSignal(str, str, int, object)


class LogWriter(QRunnable):
    def __init__(self, mode, obj_name, msg):
        super(LogWriter, self).__init__()
        try:
            _date_log = None
            if mode == 'info':
                _date_log = str(datetime.now().day).zfill(2) + '_' + str(datetime.now().month).zfill(2) + \
                    '_' + str(datetime.now().year)
            if mode == 'error':
                _date_log = 'errors'

            _path_logs = base_dir + '/log'
            self.filename = _path_logs + '/' + _date_log + '.log'
            self.msg = msg
            self.nam_f = obj_name[0]
            self.nam_m = obj_name[1]
            self.num_line = obj_name[2]

        except Exception as e:
            print(str(e))

    @pyqtSlot()
    def run(self):
        try:
            with open(self.filename, 'a') as file:
                time_msg = str(datetime.now())[:-3]
                temp = f'{time_msg} - [{self.nam_f}].{self.nam_m}[{self.num_line}] - {self.msg}\n'
                file.write(temp)

        except Exception as err:
            print(f'ERROR in thread LogWriter - {err}')


class Writer(QRunnable):
    signals = Signals()

    def __init__(self, client, cst, tag, values, reg_write, freq_command):
        super(Writer, self).__init__()
        self.client = client
        self.cst = cst
        self.tag = tag
        self.values = values
        self.dev_id = 1
        self.reg_write = reg_write
        self.reg_state = 0x2003
        self.len_msg = 8
        self.reg_len_freq = 0x2060
        self.reg_freq_buffer = 0x2061
        self.freq_command = freq_command
        self.number_attempts = 0
        self.max_attempts = 5
        self.cond = True
        self.flag_next = False

    @pyqtSlot()
    def run(self):
        try:
            if self.tag == 'reg':
                while self.number_attempts <= self.max_attempts:
                    try:
                        rw = self.client.execute(self.dev_id, self.cst.WRITE_MULTIPLE_REGISTERS,
                                                 self.reg_write, output_value=tuple(self.values))
                        self.signals.write_result.emit('OK!', self.tag, self.reg_write, self.values)
                        self.number_attempts = 10

                    except Exception as e:
                        self.signals.write_result.emit('ERROR!', self.tag, self.reg_write, self.values)
                        self.number_attempts += 1
                        time.sleep(0.02)

                if not self.number_attempts == 10:
                    self.signals.write_result.emit('ERROR!', self.tag, self.reg_write, self.values)

            if self.tag == 'FC':
                while self.cond:  # Проверяем бит занятости ПЧ
                    time.sleep(0.02)
                    rr = self.client.execute(self.dev_id, self.cst.READ_HOLDING_REGISTERS, self.reg_state, 1)
                    if len(rr) == 1:
                        val_reg = rr[0]
                        bits_list = self._dec_to_bin_str(val_reg)
                        if bits_list[11] == 0:
                            self.flag_next = True
                            self.cond = False
                    else:
                        self.number_attempts += 1
                        if self.number_attempts >= self.max_attempts:
                            # self.signals.thread_err.emit(f'ERROR write - {rw}')
                            # self.signals.write_finish.emit(False)
                            print('ERROR WRITE!!!')
                            self.flag_next = False
                            self.cond = False

                if self.flag_next:  # Записываем длину команды
                    self.flag_next = False
                    self.number_attempts = 0
                    while self.number_attempts < self.max_attempts:
                        time.sleep(0.02)
                        arr = []
                        arr.append(self.len_msg)
                        try:
                            rq = self.client.execute(self.dev_id, self.cst.WRITE_MULTIPLE_REGISTERS,
                                                     self.reg_len_freq, output_value=tuple(arr))
                            self.flag_next = True
                            self.number_attempts = 10

                        except Exception as e:
                            self.number_attempts += 1
                            if self.number_attempts >= self.max_attempts:
                                # self.signals.thread_err.emit(f'ERROR write - {rq}')
                                # self.signals.write_finish.emit(False)
                                print('ERROR WRITE')

                if self.flag_next:  # Проверяем бит занятости ПЧ
                    self.flag_next = False
                    self.cond = True
                    self.number_attempts = 0
                    while self.cond:
                        time.sleep(0.02)
                        rr = self.client.execute(self.dev_id, self.cst.READ_HOLDING_REGISTERS, self.reg_state, 1)
                        if len(rr) == 1:
                            val_reg = rr[0]
                            bits_list = self._dec_to_bin_str(val_reg)
                            if bits_list[11] == 0:
                                self.flag_next = True
                                self.cond = False
                        else:
                            self.number_attempts += 1
                            if self.number_attempts >= self.max_attempts:
                                # self.signals.thread_err.emit(f'ERROR write - {rw}')
                                # self.signals.write_finish.emit(False)
                                print('ERROR WRITE!!!')
                                self.flag_next = False
                                self.cond = False

                if self.flag_next:  # Записываем команду для ПЧ
                    self.flag_next = False
                    self.number_attempts = 0
                    while self.number_attempts < self.max_attempts:
                        time.sleep(0.02)
                        try:
                            rq = self.client.execute(self.dev_id, self.cst.WRITE_MULTIPLE_REGISTERS,
                                                     self.reg_freq_buffer, output_value=tuple(self.freq_command))
                            self.number_attempts = 10
                            self.flag_next = True

                        except Exception as e:
                            # self.signals.thread_err.emit(f'ERROR write - {rq}')
                            # self.signals.write_finish.emit(False)
                            self.number_attempts += 1
                            if self.number_attempts >= self.max_attempts:
                                print('ERROR WRITE')

                if self.flag_next:
                    self.signals.write_result.emit('OK!', self.tag, self.reg_freq_buffer, self.freq_command)

        except Exception as e:
            self.signals.thread_err.emit(f'ERROR in thread Writer - {e}')

    def _dec_to_bin_str(self, val_d):
        try:
            bin_str = bin(val_d)
            bin_str = bin_str[2:]
            bin_str = bin_str.zfill(16)
            bin_str = ''.join(reversed(bin_str))
            bin_list = []
            for i in bin_str:
                bin_list.append(int(i))
            return bin_list

        except Exception as e:
            self.signals.thread_err.emit(f'ERROR in thread Writer/_dec_to_bin_str - {e}')


class Reader(QRunnable):
    signals = Signals()

    def __init__(self, client, cst):
        super(Reader, self).__init__()
        self.client = client
        self.cst = cst

        self.read_tag = ''

        self.dev_id = 1
        self.start_reg = 0x2000
        self.count_reg = 14

        self.reg_buffer = 0x4000
        self.buffer_count = 20
        self.buffer_all = 18000

        self.flag_start_test = False
        self.num_rec = 0
        self.current_rec = -1
        self.count_rec = 0

        self.result = {}

        self.cycle = True
        self.is_run = False

    @pyqtSlot()
    def run(self):
        while self.cycle:
            try:
                if not self.is_run:
                    time.sleep(0.001)
                else:
                    if self.read_tag == 'reg':
                        rr = self.client.execute(self.dev_id, self.cst.READ_HOLDING_REGISTERS,
                                                 self.start_reg, self.count_reg)

                        self.result['regs'] = rr

                        self.signals.read_result.emit(self.result, self.read_tag)

                    elif self.read_tag == 'buffer':

                        self.result = {'count': [], 'force': [], 'move': [], 'state': [], 'temper': []}

                        rr = self.client.execute(self.dev_id, self.cst.READ_HOLDING_REGISTERS,
                                                 self.reg_buffer, self.buffer_count * 6)

                        if len(rr) == self.buffer_count * 6:  # 120
                            for i in range(0, self.buffer_count):  # 20
                                flag_add = False
                                ind = 6 * i
                                if self.flag_start_test:
                                    flag_add = True
                                    self.flag_start_test = False
                                else:
                                    if abs(rr[ind] - self.current_rec) < 2 or abs(rr[ind] - self.current_rec) > 65530:
                                        flag_add = True

                                if flag_add:
                                    self.current_rec = rr[ind]
                                    self.reg_buffer += 6
                                    self.num_rec += 1
                                    self.count_rec += 1

                                    self.result['count'].append(rr[ind])

                                    force = round(unpack('f', pack('<HH', rr[ind + 2], rr[ind + 1]))[0], 1)
                                    self.result['force'].append(force)

                                    move = round(-0.1 * (int.from_bytes(pack('>H', rr[ind + 3]), 'big', signed=True))
                                                 , 1)
                                    self.result['move'].append(move)

                                    self.result['state'].append(rr[ind + 4])
                                    self.result['temper'].append(round(rr[ind + 5] * 0.01, 1))

                                else:
                                    # print(f'addr: {self.reg_buffer} num rec: {self.current_rec} read rec: {rr[ind]}\n')
                                    break

                            delta_r = 16384 + self.buffer_all - self.reg_buffer

                            if delta_r <= 0:
                                if delta_r < 0:
                                    self.signals.thread_err.emit('Выход за пределы буфера')
                                self.num_rec = 0
                                self.buffer_count = 20
                                self.reg_buffer = 0x4000
                            else:
                                if delta_r >= 6 * self.buffer_count:
                                    self.buffer_count = 20

                                else:
                                    self.buffer_count = int(delta_r / 6)

                            self.signals.read_result.emit(self.result, self.read_tag)

                        else:
                            self.signals.thread_err.emit(str(rr))

            except Exception as e:
                self.signals.thread_err.emit(f'ERROR in thread Reader - {e}')

    def start_test(self):
        self.num_rec = 0
        self.count_rec = 0
        self.result = {'count': [], 'force': [], 'move': [], 'state': [], 'temper': []}
        self.flag_start_test = True
        self.read_tag = 'buffer'

    def stop_test(self):
        self.read_tag = 'reg'

    def start_read(self):
        self.read_tag = 'reg'
        self.is_run = True

    def stop_read(self):
        self.read_tag = 'reg'
        self.is_run = False

    def exit_read(self):
        self.cycle = False
