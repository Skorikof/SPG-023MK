import time
import os
from datetime import datetime
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot


base_dir = os.path.dirname(__file__)


class Signals(QObject):
    thread_log = pyqtSignal(str)
    thread_err = pyqtSignal(str)
    read_result = pyqtSignal(tuple)
    write_finish = pyqtSignal(bool)


class LogWriter(QRunnable):
    def __init__(self, mode, obj_name, msg):
        super(LogWriter, self).__init__()
        try:
            _date_log = None
            if mode == 'info':
                _date_log = str(datetime.now().day).zfill(2) + '_' + str(datetime.now().month).zfill(2) + \
                    '_' + str(datetime.now().year)
            if mode == 'error':
                _date_log = 'errors'

            _path_logs = base_dir + '/log'
            self.filename = _path_logs + '/' + _date_log + '.log'
            self.msg = msg
            self.nam_f = obj_name[0]
            self.nam_m = obj_name[1]
            self.num_line = obj_name[2]

        except Exception as e:
            print(str(e))

    @pyqtSlot()
    def run(self):
        try:
            with open(self.filename, 'a') as file:
                temp_str = str(datetime.now())[:-3] + ' - [' + str(self.nam_f) + '].' + self.nam_m + \
                    '[' + str(self.num_line) + '] - ' + self.msg + '\n'
                file.write(temp_str)

        except Exception as err:
            print(str(err))


class Writer(QRunnable):
    signals = Signals()

    def __init__(self, **kwargs):
        super(Writer, self).__init__()
        self.client = kwargs.get('client')
        self.cst = kwargs.get('cst')
        self.values = kwargs.get('values')
        self.start_reg = kwargs.get('start_reg')
        self.dev_id = kwargs.get('dev_id')
        self.number_attempts = 0
        self.max_attempts = 5
        self.flag_write = False

    @pyqtSlot()
    def run(self):
        try:
            while self.number_attempts <= self.max_attempts:
                txt = 'Writer, start_adr -> {}, value -> {}, dev_id -> {}'.format(self.start_reg,
                                                                                  self.values,
                                                                                  self.dev_id)
                self.signals.thread_log.emit(txt)
                try:
                    rq = self.client.execute(self.dev_id, self.cst.WRITE_MULTIPLE_REGISTERS,
                                             self.start_reg, output_value=tuple(self.values))
                    time.sleep(0.1)
                    txt = 'Complite write value {} in reg -> {}, dev_id -> {}'.format(self.values,
                                                                                      self.start_reg,
                                                                                      self.dev_id)
                    self.signals.thread_log.emit(txt)
                    self.flag_write = True
                    self.number_attempts = self.max_attempts + 1
                    self.signals.write_finish.emit(True)

                except Exception as e:
                    txt = 'Attempts write: {}, value {} in reg -> {}, dev_id -> {}'.format(self.number_attempts,
                                                                                           self.values,
                                                                                           self.start_reg,
                                                                                           self.dev_id)
                    self.signals.thread_log.emit(txt)
                    self.number_attempts += 1
                    time.sleep(0.1)

            if not self.flag_write:
                txt = 'Unsuccessful write attempt value {} in reg -> {}, dev_id -> {}'.format(self.values,
                                                                                              self.start_reg,
                                                                                              self.dev_id)
                self.signals.thread_log.emit(txt)
                txt = 'ERROR format - {}'.format(rq)
                self.signals.thread_err.emit(txt)
                self.signals.write_finish.emit(False)

        except Exception as e:
            txt = 'ERROR in thread Writer - {}'.format(e)
            self.signals.thread_err.emit(txt)


class Reader(QRunnable):
    signals = Signals()

    def __init__(self, client, cst):
        super(Reader, self).__init__()
        self.cycle = True
        self.is_run = False
        self.client = client
        self.cst = cst
        self.start_reg = None
        self.count_reg = None
        self.dev_id = None

    @pyqtSlot()
    def run(self):
        while self.cycle:
            try:
                if not self.is_run:
                    time.sleep(0.001)
                else:
                    rr = self.client.execute(self.dev_id, self.cst.READ_HOLDING_REGISTERS,
                                             self.start_reg, self.count_reg)

                    self.signals.read_result.emit(rr)

                    time.sleep(0.01)

            except Exception as e:
                txt = 'ERROR in thread Reader - {}'.format(e)
                self.signals.thread_err.emit(txt)

    def start_read(self, request):
        self.dev_id = request.get('dev_id')
        self.start_reg = request.get('start_reg_read')
        self.count_reg = request.get('count_reg_read')
        self.is_run = True

    def stop_read(self):
        self.is_run = False

    def exit_read(self):
        self.cycle = False
