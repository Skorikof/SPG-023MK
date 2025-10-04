import time
from PySide6.QtCore import QObject, QRunnable, Signal, Slot


class Signals(QObject):
    thread_err = Signal(str)
    write_result = Signal(list)


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

    @Slot()
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
                self.signals.thread_err.emit(f'ERROR in thread_writer reg --> {e}')

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
