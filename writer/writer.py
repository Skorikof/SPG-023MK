# -*- coding: utf-8 -*-
from PySide6.QtCore import QTimer, QThreadPool, QObject, Signal
import modbus_tk.defines as cst

from logger import my_logger
from my_thread.my_threads import WriterThread


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
                writer.signals.thread_log.connect(self._log_info_write_thread)
                writer.signals.thread_err.connect(self._log_error_write_thread)
                writer.signals.write_result.connect(self._result_write)
                self.writer_flag_init = True

            return writer

        except Exception as e:
            self.logger.error(e)

    def _log_info_write_thread(self, txt_log):
        self.logger.info(txt_log)

    def _log_error_write_thread(self, txt_log):
        self.logger.error(txt_log)

    def _result_write(self, response):
        try:
            res = response[0]
            tag = response[1]
            # addr = response[2]
            # value = response[3]
            command = response[4]
            if self.query_write:
                self.query_write = False
                self.list_write.pop(0)
                if tag == 'FC':
                    self.logger.debug(f'FC command write --> {res}')
                
                else:
                    if command == 'buffer_on' or command == 'buffer_off':
                        self._pars_result_write_force(res, command)

                # if res == 'OK!':
                #     pass

        except Exception as e:
            self.logger.error(e)

    def _pars_result_write_force(self, res, command):
        self.signals.check_buffer.emit(res, command)

    def write_out(self, tag, values=None, reg_write=None, freq_command=None, command=None):
        try:
            self.list_write.append(self._init_writer(tag, values, reg_write, freq_command, command))

        except Exception as e:
            self.logger.error(e)
