# -*- coding: utf-8 -*-
import time
from PySide6.QtCore import QObject, QRunnable, Signal, Slot


class Signals(QObject):
    thread_err = Signal(str)
    read_result = Signal(str, tuple)


class ReaderThread(QRunnable):
    signals = Signals()

    def __init__(self, client, cst):
        super(ReaderThread, self).__init__()
        self.client = client
        self.cst = cst

        self.read_tag = 'reg'
        self.reg_buffer = 0x4000
        self.buffer_count = 20

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
                        rr = self.client.execute(1, self.cst.READ_HOLDING_REGISTERS, 0x2000, 14)
                        self.signals.read_result.emit(self.read_tag, rr)

                    except Exception as e:
                        self.signals.thread_err.emit(f'ERROR in thread reader reg - {e}')

                elif self.read_tag == 'buffer':
                    try:
                        rr = self.client.execute(1, self.cst.READ_HOLDING_REGISTERS,
                                                 self.reg_buffer, self.buffer_count * 6)
                        
                        self.signals.read_result.emit(self.read_tag, rr)
                        
                        self.reg_buffer += 6
                        
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

                    except Exception as e:
                        self.signals.thread_err.emit(f'ERROR in thread reader buffer - {e}')

    def start_test(self):
        self.reg_buffer = 0x4000
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
