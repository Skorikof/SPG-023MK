# -*- coding: utf-8 -*-
import time
from PySide6.QtCore import QObject, QRunnable, Signal, Slot

from scripts.parser import ParserSPG023MK


class Signals(QObject):
    thread_err = Signal(str)
    read_result = Signal(dict, str)


class ReaderThread(QRunnable):
    signals = Signals()

    def __init__(self, client, cst):
        super(ReaderThread, self).__init__()
        self.client = client
        self.cst = cst

        self.parser = ParserSPG023MK()

        self.read_tag = ''

        self.reg_buffer = 0x4000
        self.buffer_count = 20

        self.flag_start_test = False
        self.current_rec = -1

        self.result = {}

        self.cycle = True
        self.is_run = False

    @Slot()
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
                                    # if abs(rr[ind] - self.current_rec) < 2 or abs(rr[ind] - self.current_rec) > 65530:
                                    flag_add = True

                                if flag_add:
                                    self.current_rec = rr[ind]
                                    self.reg_buffer += 6

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
        self.reg_buffer = 0x4000
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
