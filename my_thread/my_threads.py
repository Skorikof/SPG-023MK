# -*- coding: utf-8 -*-
import time
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot

from my_parser.parser import ParserSPG023MK


class Signals(QObject):
    thread_log = pyqtSignal(str)
    thread_err = pyqtSignal(str)
    read_result = pyqtSignal(dict, str)
    write_result = pyqtSignal(list)


class WriterThread(QRunnable):
    signals = Signals()

    def __init__(self, client, cst, tag, values, reg_write, freq_command, command='reg'):
        super(WriterThread, self).__init__()
        self.client = client
        self.cst = cst
        self.tag = tag
        self.values = values
        self.reg_write = reg_write
        self.freq_command = freq_command
        self.command = command

        self.number_attempts = 0
        self.max_attempts = 5
        self.cond = True
        self.flag_next = False

    @pyqtSlot()
    def run(self):
        if self.tag == 'reg':
            try:
                while self.number_attempts <= self.max_attempts:
                    try:
                        rw = self.client.execute(1, self.cst.WRITE_MULTIPLE_REGISTERS,
                                                 self.reg_write, output_value=tuple(self.values))
                        self.number_attempts = 10
                        response = ['OK!', self.tag, self.reg_write, self.values, self.command]
                        self.signals.write_result.emit(response)

                    except:
                        self.number_attempts += 1
                        time.sleep(0.02)

                if not self.number_attempts == 10:
                    response = ['ERROR!', self.tag, self.reg_write, self.values, self.command]
                    self.signals.write_result.emit(response)

            except Exception as e:
                self.signals.thread_err.emit(f'ERROR in thread writer reg --> {e}')

        if self.tag == 'FC':
            try:
                while self.cond:  # Проверяем бит занятости ПЧ
                    time.sleep(0.02)
                    rr = self.client.execute(1, self.cst.READ_HOLDING_REGISTERS, 0x2003, 1)
                    if len(rr) == 1:
                        bits_list = self._dec_to_bin_str(rr[0])
                        if bits_list[11] == 0:
                            self.flag_next = True
                            self.cond = False
                    else:
                        self.number_attempts += 1
                        if self.number_attempts >= self.max_attempts:
                            self.flag_next = False
                            self.cond = False

                if self.flag_next:  # Записываем длину команды
                    self.flag_next = False
                    self.number_attempts = 0
                    while self.number_attempts < self.max_attempts:
                        time.sleep(0.02)
                        try:
                            rq = self.client.execute(1, self.cst.WRITE_MULTIPLE_REGISTERS,
                                                     0x2060, output_value=tuple([8]))
                            self.flag_next = True
                            self.number_attempts = 10

                        except Exception as e:
                            self.number_attempts += 1
                            if self.number_attempts >= self.max_attempts:
                                self.flag_next = False

                if self.flag_next:  # Проверяем бит занятости ПЧ
                    self.flag_next = False
                    self.cond = True
                    self.number_attempts = 0
                    while self.cond:
                        time.sleep(0.02)
                        rr = self.client.execute(1, self.cst.READ_HOLDING_REGISTERS, 0x2003, 1)
                        if len(rr) == 1:
                            bits_list = self._dec_to_bin_str(rr[0])
                            if bits_list[11] == 0:
                                self.flag_next = True
                                self.cond = False
                        else:
                            self.number_attempts += 1
                            if self.number_attempts >= self.max_attempts:
                                self.flag_next = False
                                self.cond = False

                if self.flag_next:  # Записываем команду для ПЧ
                    self.flag_next = False
                    self.number_attempts = 0
                    while self.number_attempts < self.max_attempts:
                        time.sleep(0.02)
                        try:
                            rq = self.client.execute(1, self.cst.WRITE_MULTIPLE_REGISTERS,
                                                     0x2061, output_value=tuple(self.freq_command))
                            self.number_attempts = 10
                            self.flag_next = True

                        except Exception as e:
                            self.number_attempts += 1
                            if self.number_attempts >= self.max_attempts:
                                response = ['ERROR!', self.tag, 0x2061, self.freq_command, self.command]
                                self.signals.write_result.emit(response)

                if self.flag_next:
                    response = ['OK!', self.tag, 0x2061, self.freq_command, self.command]
                    self.signals.write_result.emit(response)

            except Exception as e:
                self.signals.thread_err.emit(f'ERROR in thread writer FC --> {e}')

    def _dec_to_bin_str(self, val_d):
        try:
            bin_str = bin(val_d)
            bin_str = bin_str[2:]
            bin_str = bin_str.zfill(16)
            bin_str = ''.join(reversed(bin_str))
            return [int(x) for x in bin_str]

        except Exception as e:
            self.signals.thread_err.emit(f'ERROR in thread Writer/_dec_to_bin_str - {e}')


class Reader(QRunnable):
    signals = Signals()

    def __init__(self, client, cst):
        super(Reader, self).__init__()
        self.client = client
        self.cst = cst

        self.parser = ParserSPG023MK()

        self.read_tag = ''

        self.reg_buffer = 0x4000
        self.buffer_count = 20

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
            if not self.is_run:
                time.sleep(0.001)
            else:
                if self.read_tag == 'reg':
                    try:
                        self.result['regs'] = self.client.execute(1, self.cst.READ_HOLDING_REGISTERS, 0x2000, 14)

                        self.signals.read_result.emit(self.result, self.read_tag)

                    except Exception as e:
                        self.signals.thread_err.emit(f'ERROR in thread reader reg - {e}')

                elif self.read_tag == 'buffer':
                    try:
                        self.result = {'count': [],
                                       'force': [],
                                       'move': [],
                                       'state': [],
                                       'temper': []}

                        rr = self.client.execute(1, self.cst.READ_HOLDING_REGISTERS,
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
                                    self.result['force'].append(self.parser.magnitude_effort(rr[ind+1], rr[ind+2]))
                                    self.result['move'].append(self.parser.movement_amount(rr[ind+3]))
                                    self.result['state'].append(rr[ind + 4])
                                    self.result['temper'].append(round(rr[ind + 5] * 0.01, 1))

                                else:
                                    # print(f'addr: {self.reg_buffer} num rec: {self.current_rec} read rec: {rr[ind]}\n')
                                    break

                            delta_r = 16384 + 18000 - self.reg_buffer

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
                        self.signals.thread_err.emit(f'ERROR in thread reader buffer - {e}')

    def start_test(self):
        self.num_rec = 0
        self.count_rec = 0
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
