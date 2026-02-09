import time
from PySide6.QtCore import QObject, QRunnable, Signal, Slot


class Signals(QObject):
    thread_err = Signal(str)
    write_result = Signal(tuple)


class WriterThread(QRunnable):
    signals = Signals()

    def __init__(self, client, tag, values, reg_write, freq_command, command):
        super(WriterThread, self).__init__()
        self.client = client
        # self.cst = cst
        self.tag = tag
        self.values = values
        self.reg_write = reg_write
        self.freq_command = freq_command
        self.command = command

        self.number_attempts = 0
        self.max_attempts = 5
        self.cond = True
        self.flag_next = False

    @Slot()
    def run(self):
        if self.tag == 'reg':
            try:
                while self.number_attempts <= self.max_attempts:
                    # rw = self.client.execute(1, self.cst.WRITE_MULTIPLE_REGISTERS,
                    #                          self.reg_write, output_value=tuple(self.values))
                    rw = self.client.write_registers(self.reg_write,
                                                     self.values,
                                                     device_id=1)
                    if not rw.isError:
                        self.number_attempts = 10
                        self.signals.write_result.emit(('OK!', self.tag,
                                                        self.reg_write,
                                                        self.values, self.command))
                    
                    else:
                        self.number_attempts += 1
                        time.sleep(0.02)

                if not self.number_attempts == 10:
                    self.signals.write_result.emit(('ERROR!', self.tag,
                                                    self.reg_write, self.values,
                                                    self.command))

            except Exception as e:
                self.signals.thread_err.emit(f'ERROR in thread_writer reg --> {e}')

        if self.tag == 'FC':
            try:
                while self.cond:  # Проверяем бит занятости ПЧ
                    time.sleep(0.02)
                    rr = self.client.read_holding_registers(0x2003, count=1, device_id=1)
                    if not rr.isError:
                        if len(rr.registers) == 1:
                            bits_list = self._dec_to_bin_str(rr.registers[0])
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
                        rw = self.client.write_registers(0x2060, [8], device_id=1)
                        if rw.isError:
                            self.flag_next = True
                            self.number_attempts = 10
                        else:
                            self.number_attempts += 1
                            if self.number_attempts >= self.max_attempts:
                                self.flag_next = False

                if self.flag_next:  # Проверяем бит занятости ПЧ
                    self.flag_next = False
                    self.cond = True
                    self.number_attempts = 0
                    while self.cond:
                        time.sleep(0.02)
                        rr = self.client.read_holding_registers(0x2003, count=1, device_id=1)
                    if not rr.isError:
                        if len(rr.registers) == 1:
                            bits_list = self._dec_to_bin_str(rr.registers[0])
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
                        rw = self.client.write_registers(0x2061, self.freq_command, device_id=1)
                        if not rw.isError:
                            self.number_attempts = 10
                            self.flag_next = True
                        else:
                            self.number_attempts += 1
                            if self.number_attempts >= self.max_attempts:
                                self.signals.write_result.emit(('ERROR!', self.tag,
                                                                0x2061, self.freq_command,
                                                                self.command))

                if self.flag_next:
                    self.signals.write_result.emit(('OK!', self.tag, 0x2061,
                                                    self.freq_command, self.command))

            except Exception as e:
                self.signals.thread_err.emit(f'ERROR in thread_writer FC --> {e}')

    def _dec_to_bin_str(self, val_d):
        try:
            bin_str = bin(val_d)
            bin_str = bin_str[2:]
            bin_str = bin_str.zfill(16)
            bin_str = ''.join(reversed(bin_str))
            return [int(x) for x in bin_str]

        except Exception as e:
            self.signals.thread_err.emit(f'ERROR in thread_writer/_dec_to_bin_str - {e}')
