# -*- coding: utf-8 -*-
import time
from PySide6.QtCore import QObject, QRunnable, Signal, Slot

from config import config
from scripts.buffer_dump import dump, slot
from scripts.modbus.registers import (
    REG_STATE_BLOCK,
    REG_STATE_BLOCK_COUNT,
    REG_BUFFER_START,
    REG_BUFFER_RECORD_REGS,
    REG_BUFFER_RECORDS_PER_READ,
    REG_BUFFER_TOTAL_REGS,
)


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

        self.reg_buffer: int = REG_BUFFER_START
        self.buffer_count: int = REG_BUFFER_RECORDS_PER_READ

        self.flag_start_test: bool = False
        self.current_rec: int = -1

        self.result: dict[str, tuple | list[int]] = {}

        self.cycle: bool = True
        self.is_run: bool = False

        # запись в файл диагностики (BUFFER_DUMP): до какого момента писать все записи
        # чтения (мс файла), последняя запись, на которой остановилось чтение, и сколько
        # пустых чтений подряд на ней
        self._verbose_until: float | None = None
        self._dump_last_rej = None
        self._dump_idle_reads = 0

    @Slot()
    def run(self):
        while self.cycle:
            if not self.is_run:
                time.sleep(0.001)
                continue
            
            if self.read_tag == 'reg':
                try:
                    rr = self.client.read_holding_registers(REG_STATE_BLOCK,
                                                            count=REG_STATE_BLOCK_COUNT,
                                                            device_id=1)
                    if rr.isError():
                        self.signals.thread_err.emit(str(rr))
                        
                    else:
                        result = {'regs': rr.registers}
                        self.signals.read_result.emit(result, self.read_tag)
                        
                    # time.sleep(self.PAUSE_REG)

                except Exception as e:
                    self.signals.thread_err.emit(f'ERROR in thread reader reg - {e}')

            elif self.read_tag == 'buffer':
                try:
                    self.result = {'count': [],
                                   'force_big': [],
                                   'force_low': [],
                                   'move': [],
                                   'state': [],
                                   'temper': []}
                    
                    addr_start = self.reg_buffer
                    count_read = self.buffer_count
                    rr = self.client.read_holding_registers(self.reg_buffer,
                                                            count=self.buffer_count * REG_BUFFER_RECORD_REGS,
                                                            device_id=1)

                    if rr.isError():
                        self.signals.thread_err.emit(str(rr))
                        if dump.is_open:
                            dump.line('RDERR', dump.now_ms(), slot(addr_start), str(rr))

                    else:
                        if len(rr.registers) == self.buffer_count * REG_BUFFER_RECORD_REGS:
                            taken = 0   # для записи в файл: сколько записей принято подряд
                            for i in range(0, self.buffer_count):
                                flag_add = False
                                ind = REG_BUFFER_RECORD_REGS * i
                                if self.flag_start_test:
                                    flag_add = True
                                    self.flag_start_test = False
                                else:
                                    if abs(rr.registers[ind] - self.current_rec) == 1 or abs(rr.registers[ind] - self.current_rec) > 65530:
                                        flag_add = True

                                if flag_add:
                                    taken += 1
                                    self.current_rec = rr.registers[ind]
                                    self.reg_buffer += REG_BUFFER_RECORD_REGS

                                    if rr.registers[ind] != 0:
                                        self.result['count'].append(rr.registers[ind])
                                        self.result['force_big'].append(rr.registers[ind+1])
                                        self.result['force_low'].append(rr.registers[ind+2])
                                        self.result['move'].append(rr.registers[ind+3])
                                        self.result['state'].append(rr.registers[ind + 4])
                                        self.result['temper'].append(rr.registers[ind + 5])

                                else:
                                    # txt = (f'addr: {self.reg_buffer} num rec: {self.current_rec} read rec: {rr.registers[ind]}\n')
                                    # self.signals.thread_err.emit(txt)
                                    break

                            if dump.is_open:
                                self._dump_read(addr_start, count_read, rr.registers, taken)

                            delta_r = REG_BUFFER_START + REG_BUFFER_TOTAL_REGS - self.reg_buffer

                            if delta_r <= 0:
                                if delta_r < 0:
                                    self.signals.thread_err.emit('Выход за пределы буфера')
                                self.buffer_count = REG_BUFFER_RECORDS_PER_READ
                                self.reg_buffer = REG_BUFFER_START
                            else:
                                if delta_r >= REG_BUFFER_RECORD_REGS * self.buffer_count:
                                    self.buffer_count = REG_BUFFER_RECORDS_PER_READ

                                else:
                                    self.buffer_count = int(delta_r / REG_BUFFER_RECORD_REGS)
                                    
                            if self.result.get('count'):
                                self.signals.read_result.emit(self.result, self.read_tag)
                        
                    # time.sleep(self.PAUSE_BUF)

                except Exception as e:
                    self.signals.thread_err.emit(f'ERROR in thread reader buffer - {e}')

    def _dump_read(self, addr_start: int, count: int, regs: list[int], taken: int):
        """
        Запись чтения буфера в файл диагностики (BUFFER_DUMP). В первые VERBOSE_WINDOW с
        после начала чтения буфера - все записи чтения, дальше - принятые записи и сводка
        чтения; подряд идущие пустые чтения (упёрлись в ту же запись) сворачиваются в счётчик
        """
        t = dump.now_ms()
        base = slot(addr_start)
        n = REG_BUFFER_RECORD_REGS
        if self._verbose_until is None:
            self._verbose_until = t + dump.VERBOSE_WINDOW * 1000
            dump.event('reader_first_read', base, f'record_no={regs[0]}')

        rej_no = regs[n * taken] if taken < count else ''
        rej_move = regs[n * taken + 3] if taken < count else ''
        if taken == 0 and rej_no == self._dump_last_rej and t >= self._verbose_until:
            self._dump_idle_reads += 1
            return

        lines = []
        if t < self._verbose_until:
            for i in range(count):
                mark = 'A' if i < taken else ('R' if i == taken else '-')
                rec = ';'.join(map(str, regs[n * i:n * i + n]))
                lines.append(f'RAW;{t:.1f};{base + i};{rec};{mark}')
        else:
            for i in range(taken):
                if regs[n * i] != 0:
                    rec = ';'.join(map(str, regs[n * i:n * i + n]))
                    lines.append(f'REC;{t:.1f};{base + i};{rec}')
        first = regs[0] if taken else ''
        last = regs[n * (taken - 1)] if taken else ''
        lines.append(f'RD;{t:.1f};{base};{count};{taken};{first};{last};{rej_no};{rej_move};'
                     f'{self._dump_idle_reads}')
        dump.block(lines)
        self._dump_last_rej = rej_no
        self._dump_idle_reads = 0

    @Slot()
    def start_test(self):
        self.reg_buffer = REG_BUFFER_START
        self.flag_start_test = True
        self._verbose_until = None
        self._dump_last_rej = None
        self._dump_idle_reads = 0
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
