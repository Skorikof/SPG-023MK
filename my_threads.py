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

    def __init__(self, client, cst, **kwargs):
        super(Writer, self).__init__()
        self.client = client
        self.cst = cst
        self.tag = kwargs.get('write_tag')
        self.values = kwargs.get('write_values')
        self.start_reg = kwargs.get('reg_write')
        self.dev_id = kwargs.get('dev_id')
        self.reg_write = kwargs.get('reg_write')
        self.reg_state = kwargs.get('reg_state')
        self.len_msg = kwargs.get('len_freq_msg')
        self.reg_len_freq = kwargs.get('reg_len_freq')
        self.reg_freq_buffer = kwargs.get('reg_freq_buffer')
        self.freq_command = kwargs.get('freq_command')
        self.number_attempts = 0
        self.max_attempts = 5
        self.cond = True
        self.flag_next = False
        self.flag_write = False

    @pyqtSlot()
    def run(self):
        try:
            if self.tag == 'reg':
                while self.number_attempts <= self.max_attempts:
                    txt = 'Writer, start_adr -> {}, value -> {}, dev_id -> {}'.format(self.reg_write,
                                                                                      self.values,
                                                                                      self.dev_id)
                    self.signals.thread_log.emit(txt)
                    try:
                        rw = self.client.execute(self.dev_id, self.cst.WRITE_MULTIPLE_REGISTERS,
                                                 self.reg_write, output_value=tuple(self.values))
                        txt = 'Complite write value {} in reg -> {}, dev_id -> {}'.format(self.values,
                                                                                          self.reg_state,
                                                                                          self.dev_id)
                        self.signals.thread_log.emit(txt)
                        self.flag_write = True
                        self.number_attempts = self.max_attempts + 1
                        self.signals.write_finish.emit(True)

                    except Exception as e:
                        txt = 'Attempts write: {}, value {} in reg -> {}, dev_id -> {}'.format(self.number_attempts,
                                                                                               self.values,
                                                                                               self.reg_write,
                                                                                               self.dev_id)
                        self.signals.thread_log.emit(txt)
                        self.number_attempts += 1
                        time.sleep(0.02)

                if not self.flag_write:
                    txt = 'Unsuccessful write attempt value {} in reg -> {}, dev_id -> {}'.format(self.values,
                                                                                                  self.reg_write,
                                                                                                  self.dev_id)
                    self.signals.thread_log.emit(txt)
                    txt = 'ERROR format - {}'.format(rw)
                    self.signals.thread_err.emit(txt)
                    self.signals.write_finish.emit(False)

            if self.tag == 'FC':
                while self.cond:
                    time.sleep(0.02)
                    rr = self.client.execute(self.dev_id, self.cst.READ_HOLDING_REGISTERS, self.reg_state, 1)
                    if len(rr) == 1:
                        val_reg = rr[0]
                        bits_list = self.dec_to_bin_str(val_reg)
                        if bits_list[11] == 0:
                            self.flag_next = True
                            self.cond = False
                    else:
                        self.number_attempts += 1
                        if self.number_attempts == self.max_attempts:
                            txt = 'ERROR write - {}'.format(rw)
                            self.signals.thread_err.emit(txt)
                            self.signals.write_finish.emit(False)

                if self.flag_next:
                    self.flag_next = False
                    self.number_attempts = 0
                    while self.number_attempts < self.max_attempts:
                        time.sleep(0.02)
                        arr = []
                        arr.append(self.len_msg)
                        try:
                            rq = self.client.execute(self.dev_id, self.cst.WRITE_MULTIPLE_REGISTERS,
                                                     self.reg_len_freq, output_value=tuple(arr))
                            self.flag_next = True
                            self.number_attempts = 10

                        except Exception as e:
                            txt = 'ERROR write - {}'.format(rq)
                            self.signals.thread_err.emit(txt)
                            self.signals.write_finish.emit(False)

                if self.flag_next:
                    self.flag_next = False
                    self.cond = True
                    self.number_attempts = 0
                    while self.cond:
                        time.sleep(0.02)
                        rr = self.client.execute(self.dev_id, self.cst.READ_HOLDING_REGISTERS, self.reg_state, 1)
                        if len(rr) == 1:
                            val_reg = rr[0]
                            bits_list = self.dec_to_bin_str(val_reg)
                            if bits_list[11] == 0:
                                self.flag_next = True
                                self.cond = False
                        else:
                            self.number_attempts += 1
                            if self.number_attempts == self.max_attempts:
                                txt = 'ERROR write - {}'.format(rw)
                                self.signals.thread_err.emit(txt)
                                self.signals.write_finish.emit(False)

                if self.flag_next:
                    self.flag_next = False
                    self.number_attempts = 0
                    while self.number_attempts < self.max_attempts:
                        time.sleep(0.02)
                        try:
                            rq = self.client.execute(self.dev_id, self.cst.WRITE_MULTIPLE_REGISTERS,
                                                     self.reg_freq_buffer, output_value=tuple(self.freq_command))
                            self.number_attempts = self.max_attempts
                            self.flag_next = True
                        except Exception as e:
                            txt = 'ERROR write - {}'.format(rq)
                            self.signals.thread_err.emit(txt)
                            self.signals.write_finish.emit(False)

                if self.flag_next:
                    self.signals.write_finish.emit(True)

        except Exception as e:
            txt = 'ERROR in thread Writer - {}'.format(e)
            self.signals.thread_err.emit(txt)

    def dec_to_bin_str(self, val_d):
        try:
            bin_str = bin(val_d)
            bin_str = bin_str[2:]
            bin_str = bin_str.zfill(16)
            bin_str = ''.join(reversed(bin_str))
            bin_list = []
            for i in bin_str:
                bin_list.append(int(i))
            return bin_list

        except Exception as e:
            txt = 'ERROR in thread Writer/dec_to_bin_str - {}'.format(e)
            self.signals.thread_err.emit(txt)


class Reader(QRunnable):
    signals = Signals()

    def __init__(self):
        super(Reader, self).__init__()
        self.cycle = True
        self.is_run = False
        self.client = None
        self.cst = None
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

    def start_read(self, client, cst, request):
        self.client = client
        self.cst = cst
        self.dev_id = request.get('dev_id')
        self.start_reg = request.get('reg_read')
        self.count_reg = request.get('read_count')
        self.is_run = True

    def stop_read(self):
        self.is_run = False

    def exit_read(self):
        self.cycle = False
