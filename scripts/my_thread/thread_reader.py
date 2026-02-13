# -*- coding: utf-8 -*-
import time
from PySide6.QtCore import QObject, QRunnable, Signal, Slot

from config import config


class Signals(QObject):
    thread_err = Signal(str)
    read_result = Signal(dict, str)


class ReaderThread(QRunnable):
    PAUSE_REG = config.pause_reg
    PAUSE_BUF = config.pause_buf
    signals = Signals()

    def __init__(self, client):
        super(ReaderThread, self).__init__()
        self.client = client

        self.read_tag: str = 'reg'

        self.reg_buffer: int = 0x4000
        self.buffer_count: int = 20

        self.flag_start_test: bool = False
        self.current_rec: int = -1
        
        # self._last_move: None | int = None
        # self.flag_add_data: bool = False
        # self.flag_send_res: bool = False

        self.result: dict[str, tuple | list[int]] = {}

        self.cycle: bool = True
        self.is_run: bool = False

    @Slot()
    def run(self):
        while self.cycle:
            if not self.is_run:
                time.sleep(0.001)
                continue
            
            if self.read_tag == 'reg':
                try:
                    rr = self.client.read_holding_registers(0x2000, count=14, device_id=1)
                    if rr.isError():
                        self.signals.thread_err.emit(str(rr))
                        
                    else:
                        result = {'regs': rr.registers}
                        self.signals.read_result.emit(result, self.read_tag)
                        
                    time.sleep(self.PAUSE_REG)

                except Exception as e:
                    self.thread_err.emit(f'ERROR in thread reader reg - {e}')

            elif self.read_tag == 'buffer':
                try:
                    self.result = {'count': [],
                                    'force_big': [],
                                    'force_low': [],
                                    'move': [],
                                    'state': [],
                                    'temper': []}
                    
                    rr = self.client.read_holding_registers(self.reg_buffer,
                                                            count=self.buffer_count * 6,
                                                            device_id=1)
                    
                    if rr.isError():
                        self.signals.thread_err.emit(str(rr))
                        
                    else:
                        if len(rr.registers) == self.buffer_count * 6:  # 120
                            for i in range(0, self.buffer_count):  # 20
                                flag_add = False
                                ind = 6 * i
                                if self.flag_start_test:
                                    flag_add = True
                                    self.flag_start_test = False
                                else:
                                    if abs(rr.registers[ind] - self.current_rec) < 2 or abs(rr.registers[ind] - self.current_rec) > 65530:
                                        flag_add = True

                                if flag_add:
                                    # if rr[ind] is not None and rr[ind] != 0:
                                    self.current_rec = rr.registers[ind]
                                    self.reg_buffer += 6
                                    
                                    # if self._last_move is None:
                                    #     self._last_move = rr.registers[ind + 3]
                                    #     self.flag_add_data = True
                                        
                                    # else:
                                    #     if self._last_move != rr.registers[ind + 3]:
                                    #         self.flag_add_data = True
                                            
                                    # if self.flag_add_data:
                                    self.result['count'].append(rr.registers[ind])
                                    self.result['force_big'].append(rr.registers[ind+1])
                                    self.result['force_low'].append(rr.registers[ind+2])
                                    self.result['move'].append(rr.registers[ind+3])
                                    self.result['state'].append(rr.registers[ind + 4])
                                    self.result['temper'].append(rr.registers[ind + 5])
                                        
                                        # self.flag_send_res = True
                                        # self.flag_add_data = True

                                else:
                                    # txt = (f'addr: {self.reg_buffer} num rec: {self.current_rec} read rec: {rr.registers[ind]}\n')
                                    # self.signals.thread_err.emit(txt)
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
                                    
                            # if self.flag_send_res:
                            self.signals.read_result.emit(self.result, self.read_tag)
                                # self.flag_send_res = False       
                        
                    # time.sleep(self.PAUSE_BUF)

                except Exception as e:
                    self.signals.thread_err.emit(f'ERROR in thread reader buffer - {e}')

    @Slot()
    def start_test(self):
        self.reg_buffer = 0x4000
        # self._last_move = None
        # self.flag_add_data = False
        # self.flag_send_res = False
        self.flag_start_test = True
        self.read_tag = 'buffer'

    @Slot()
    def stop_test(self):
        self.read_tag = 'reg'

    @Slot()
    def start_read(self):
        self.read_tag = 'reg'
        self.is_run = True

    @Slot()
    def stop_read(self):
        self.read_tag = 'reg'
        self.is_run = False

    @Slot()
    def exit_read(self):
        self.cycle = False
