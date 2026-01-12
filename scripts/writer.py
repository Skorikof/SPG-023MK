# -*- coding: utf-8 -*-
from PySide6.QtCore import QTimer, QThreadPool, QObject, Signal
import modbus_tk.defines as cst

from scripts.logger import my_logger
from scripts.my_thread.thread_writer import WriterThread


class WriterSignals(QObject):
    check_buffer = Signal(str, str)


class Writer:
    def __init__(self, client):
        self.logger = my_logger.get_logger(__name__)
        self.signals = WriterSignals()

        self.client = client
        self.threadpool = QThreadPool()
        self.timer_writer = None
        self.list_write = []
        self.query_write = False
        self.writer_flag_init = False

        self._init_timer_writer()

    def _init_timer_writer(self):
        self.timer_writer = QTimer()
        self.timer_writer.setInterval(50)
        self.timer_writer.timeout.connect(self._control_write)

    def _control_write(self):
        try:
            if not self.query_write:
                if self.list_write:
                    obj_wr = self.list_write[0]
                    self.query_write = True

                    self.threadpool.start(obj_wr)

        except Exception as e:
            self.logger.error(e)

    def timer_writer_start(self):
        self.timer_writer.start()

    def timer_writer_stop(self):
        self.timer_writer.stop()

    def _init_writer(self, tag, values=None, reg_write=None, freq_command=None, command=None):
        try:
            writer = WriterThread(client=self.client,
                                  cst=cst,
                                  tag=tag,
                                  values=values,
                                  reg_write=reg_write,
                                  freq_command=freq_command,
                                  command=command)

            if not self.writer_flag_init:
                writer.signals.thread_err.connect(self._log_error_write_thread)
                writer.signals.write_result.connect(self._result_write)
                self.writer_flag_init = True

            return writer

        except Exception as e:
            self.logger.error(e)

    def _log_error_write_thread(self, txt_log):
        self.logger.error(txt_log)

    def _result_write(self, response):
        try:
            if self.query_write:
                self.logger.debug(f'Write result --> {response[1]}, {response[0]}, '
                              f'addr={hex(response[2])}, val={response[3]}, '
                              f'com={response[4]}')
                
                self.list_write.pop(0)
                if response[1] == 'FC':
                    pass
                
                elif response[1] == 'reg':
                    if response[4] == 'buffer_on' or response[4] == 'buffer_off':
                        self._pars_result_write_force(response[0], response[4])

                else:
                    pass
                
                self.query_write = False

        except Exception as e:
            self.logger.error(e)

    def _pars_result_write_force(self, res, command):
        self.signals.check_buffer.emit(res, command)

    def write_out(self, tag, values=None, reg_write=None, freq_command=None, command=None):
        try:
            self.list_write.append(self._init_writer(tag, values, reg_write, freq_command, command))
            if reg_write:
                reg_write = hex(reg_write)
            self.logger.debug(f'Write queny append --> addr={reg_write}, val={values}, '
                              f'freq_command={freq_command}, com={command}')

        except Exception as e:
            self.logger.error(e)
