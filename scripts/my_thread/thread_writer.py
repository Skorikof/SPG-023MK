import time
from PySide6.QtCore import QObject, QRunnable, Signal, Slot

from config import config


class Signals(QObject):
    thread_err = Signal(str)
    write_result = Signal(tuple)


class WriterThread(QRunnable):
    signals = Signals()
    PAUSE_WRITE = config.pause_write

    def __init__(self, client, tag, values, reg_write, freq_command, command):
        super(WriterThread, self).__init__()
        self.client = client
        self.tag = tag
        self.values = values
        self.reg_write = reg_write
        self.freq_command = freq_command
        self.command = command

        self.number_attempts = 0
        self.max_attempts = 5

    @Slot()
    def run(self):
        if self.tag == 'reg':
            try:
                succes = False
                while self.number_attempts < self.max_attempts:
                    try:
                        rw = self.client.write_registers(self.reg_write,
                                                        self.values,
                                                        device_id=1)
                        
                        if not rw.isError():
                            success = True
                            break
                        
                        self.number_attempts += 1
                        time.sleep(self.PAUSE_WRITE)
                        
                    except Exception:
                        pass
                        
                flag = 'OK!' if success else 'ERROR!'

                self.signals.write_result.emit((flag, self.tag,
                                                self.reg_write,
                                                self.values, self.command))

            except Exception as e:
                self.signals.thread_err.emit(f'ERROR in thread_writer reg --> {e}')

        if self.tag == 'FC':
            try:
                if not self._wait_drive_ready():
                    raise Exception("Drive busy timeout")

                if not self._write_retry(0x2060, [8]):
                    raise Exception("Length write failed")

                if not self._wait_drive_ready():
                    raise Exception("Drive busy timeout 2")

                if not self._write_retry(0x2061, self.freq_command):
                    raise Exception("Command write failed")

                self.signals.write_result.emit((
                    'OK!',
                    self.tag,
                    0x2061,
                    self.freq_command,
                    self.command
                ))

            except Exception as e:
                self.signals.write_result.emit((
                    'ERROR!',
                    self.tag,
                    0x2061,
                    self.freq_command,
                    self.command
                ))

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
            
    def _wait_drive_ready(self):
        try:
            attempts = 0
            while attempts < self.max_attempts:
                time.sleep(0.02)
                try:
                    rr = self.client.read_holding_registers(
                        0x2003, count=1, device_id=1
                    )
                    if not rr.isError() and len(rr.registers) == 1:
                        bits = self._dec_to_bin_str(rr.registers[0])
                        if bits[11] == 0:
                            return True

                except Exception:
                    pass

                attempts += 1
            return False
        
        except Exception as e:
            self.signals.thread_err.emit(f'ERROR in thread_writer/_wait_drive_ready --> {e}')

    def _write_retry(self, reg, values):
        try:
            attempts = 0
            while attempts < self.max_attempts:
                time.sleep(0.02)
                try:
                    rw = self.client.write_registers(
                        reg, values, device_id=1
                    )
                    if not rw.isError():
                        return True

                except Exception:
                    pass

                attempts += 1
            return False
        except Exception as e:
            self.signals.thread_err.emit(f'ERROR in thread_writer/_write_retry --> {e}')
