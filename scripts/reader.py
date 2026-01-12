import modbus_tk.defines as cst
from PySide6.QtCore import QThreadPool, QObject, Signal

from scripts.logger import my_logger
from scripts.my_thread.thread_reader import ReaderThread


class ReaderSignals(QObject):
    start = Signal()
    start_test = Signal()
    stop_test = Signal()
    stop = Signal()
    exit = Signal()
    result = Signal(dict, str)
    error = Signal(str)
    

class Reader:
    def __init__(self):
        self.signals = ReaderSignals()
        self.threadpool = QThreadPool()
        self.logger = my_logger.get_logger(__name__)

    def init_reader(self, client):
        self.reader = ReaderThread(client, cst)
        self.reader.signals.thread_err.connect(self._log_error_thread)
        self.reader.signals.read_result.connect(self._reader_result)
        self.signals.start.connect(self.reader.start_read)
        self.signals.start_test.connect(self.reader.start_test)
        self.signals.stop.connect(self.reader.stop_read)
        self.signals.stop_test.connect(self.reader.stop_test)
        self.signals.exit.connect(self.reader.exit_read)
        self.threadpool.start(self.reader)

    def reader_start(self):
        self.signals.start.emit()

    def reader_start_test(self):
        self.signals.start_test.emit()

    def reader_stop(self):
        self.signals.stop.emit()

    def reader_stop_test(self):
        self.signals.stop_test.emit()

    def reader_exit(self):
        self.signals.exit.emit()
        
    def _log_error_thread(self, txt_log):
        self.signals.error.emit(txt_log)
    
    def _reader_result(self, res, tag):
        self.signals.result.emit(res, tag)
    