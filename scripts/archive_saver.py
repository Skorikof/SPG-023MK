# -*- coding: utf-8 -*-
from PySide6.QtCore import QTimer, QThreadPool

from scripts.logger import my_logger
from scripts.my_thread.writer_archive import WriterArchive


class WriterArch:
    def __init__(self):
        self.logger = my_logger.get_logger(__name__)

        self.threadpool = QThreadPool()
        self.timer_writer_arch = None
        self.list_write_arch = []
        self.query_write_arch = False
        self.writer_arch_flag_init = False

        self._init_timer_writer_arch()

    def _init_timer_writer_arch(self):
        self.timer_writer_arch = QTimer()
        self.timer_writer_arch.setInterval(200)
        self.timer_writer_arch.timeout.connect(self._control_write_arch)

    def _control_write_arch(self):
        try:
            if not self.query_write_arch:
                if self.list_write_arch:
                    obj_wr = self.list_write_arch[0]
                    self.query_write_arch = True

                    self.threadpool.start(obj_wr)

        except Exception as e:
            self.logger.error(e)

    def timer_writer_arch_start(self):
        self.timer_writer_arch.start()

    def timer_writer_arch_stop(self):
        self.timer_writer_arch.stop()

    def _init_writer(self, tag, data=None):
        try:
            writer_arch = WriterArchive(tag=tag,
                                        data = data)

            if not self.writer_arch_flag_init:
                writer_arch.signals.thread_err.connect(self._log_error_write_arch_thread)
                writer_arch.signals.write_archive.connect(self._result_write_arch)
                self.writer_arch_flag_init = True

            return writer_arch

        except Exception as e:
            self.logger.error(e)

    def _log_error_write_arch_thread(self, txt_log):
        self.logger.error(txt_log)
        self._result_write_arch()
        
    def _result_write_arch(self):
        try:
            if self.query_write_arch:
                self.query_write_arch = False
                self.list_write_arch.pop(0)
                
            if not self.list_write_arch:
                self.timer_writer_arch_stop()

        except Exception as e:
            self.logger.error(e)

    def write_arch_out(self, tag, data=None):
        try:
            self.list_write_arch.append(self._init_writer(tag, data))

        except Exception as e:
            self.logger.error(e)
