import time
from PySide6.QtCore import QObject, QRunnable, Signal, Slot


class Signals(QObject):
    thread_err = Signal(str)
    write_result = Signal(tuple)


class WriterThread(QRunnable):
    signals = Signals()

    def __init__(self, client, cst, tag, values, reg_write, freq_command, command='reg'):
        super(WriterThread, self).__init__()
        self.client = client
        self.cst = cst
        self.tag = tag
        self.values = values
        self.reg_write = reg_write
        self.freq_command = tuple(freq_command)
        self.command = command

        self.number_attempts = 0
        self.max_attempts = 5

    @Slot()
    def run(self):
        if self.tag == 'reg':
            try:
                while self.number_attempts <= self.max_attempts:
                    try:
                        rw = self.client.execute(1, self.cst.WRITE_MULTIPLE_REGISTERS,
                                                 self.reg_write, output_value=tuple(self.values))
                        self.number_attempts = 10
                        self.signals.write_result.emit(('OK!', self.tag,
                                                        self.reg_write,
                                                        self.values, self.command,))

                    except:
                        self.number_attempts += 1
                        time.sleep(0.02)

                if not self.number_attempts == 10:
                    self.signals.write_result.emit(('ERROR!', self.tag,
                                                    self.reg_write, self.values,
                                                    self.command,))

            except Exception as e:
                self.signals.thread_err.emit(f'ERROR in thread_writer reg --> {e}')

        if self.tag == 'FC':
            try:
                res = 'ERROR!'
                if self._check_bit_employment():
                    if self._write_len_command_fc():
                        if self._check_bit_employment():
                            if self._write_command_fc(self.freq_command):
                                res = 'OK!'
                                
                self.signals.write_result.emit((res, self.tag, 0x2061,
                                                self.freq_command, self.command,))

            except Exception as e:
                self.signals.thread_err.emit(f'ERROR in thread_writer FC --> {e}')

    def _dec_to_bin_str(self, val_d):
        try:
            bin_str = bin(val_d)
            bin_str = bin_str[2:]
            bin_str = bin_str.zfill(16)
            bin_str = ''.join(reversed(bin_str))
            return bin_str

        except Exception as e:
            self.signals.thread_err.emit(f'ERROR in thread_writer/_dec_to_bin_str - {e}')

    def _check_bit_employment(self):
        """Проверяем бит занятости ПЧ"""
        try:
            flag = False
            attempts = 0
            while attempts < 5:
                time.sleep(0.02)
                rr = self.client.execute(1, self.cst.READ_HOLDING_REGISTERS, 0x2003, 1)
                if len(rr) == 1:
                    bits_list = self._dec_to_bin_str(rr[0])
                    if bits_list[11] == '0':
                        flag = True
                        attempts = 10
                else:
                    attempts += 1
                    
            if flag:
                pass
                # ПЧ свободен для приёма команд
            else:
                pass
                # ПЧ занят для приёма команд
                
            return flag
        
        except Exception as e:
            self.signals.thread_err.emit(f'ERROR in thread_writer/_check_bit_employment - {e}')

    def _write_len_command_fc(self):
        """Записываем длину команды"""
        try:
            flag = False
            attempts = 0
            while attempts < 5:
                time.sleep(0.02)
                try:
                    rq = self.client.execute(1, self.cst.WRITE_MULTIPLE_REGISTERS,
                                                0x2060, output_value=tuple([8]))
                    flag = True
                    attempts = 10

                except Exception as e:
                    attempts += 1
            
            if flag:
                pass
                # Команда в ПЧ прошла
            else:
                pass
                # Команда в ПЧ прошла
                
            return flag
            
        except Exception as e:
            self.signals.thread_err.emit(f'ERROR in thread_writer/_write_len_command_fc - {e}')
            
    def _write_command_fc(self, command):
        """Записываем команду для ПЧ"""
        try:
            flag = False
            attempts = 0
            while self.number_attempts < 5:
                time.sleep(0.02)
                try:
                    rq = self.client.execute(1, self.cst.WRITE_MULTIPLE_REGISTERS,
                                                0x2061, output_value=command)
                    flag = True
                    attempts = 10

                except Exception as e:
                    attempts += 1
                    
            if flag:
                # Команда в ПЧ прошла
                pass
            else:
                # Команда в ПЧ не прошла
                pass
            
            return flag
                
        except Exception as e:
            self.signals.thread_err.emit(f'ERROR in thread_writer/_write_command_fc - {e}')
