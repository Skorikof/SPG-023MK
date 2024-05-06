import time
import os
from struct import pack, unpack
from datetime import datetime
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot


base_dir = os.path.dirname(__file__)


class Signals(QObject):
    thread_log = pyqtSignal(str)
    thread_err = pyqtSignal(str)
    read_result = pyqtSignal(dict, str)
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
                temp = f'{datetime.now()[:-3]} - [{self.nam_f}].{self.nam_m}[{self.num_line}] - {self.msg}\n'
                file.write(temp)

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
                    self.signals.thread_log.emit(f'Writer, {self.reg_write=}, {self.values=}, {self.dev_id=}')
                    try:
                        rw = self.client.execute(self.dev_id, self.cst.WRITE_MULTIPLE_REGISTERS,
                                                 self.reg_write, output_value=tuple(self.values))
                        self.signals.thread_log.emit(f'Complite write {self.values=} in {self.reg_state=}')
                        self.flag_write = True
                        self.number_attempts = self.max_attempts + 1
                        self.signals.write_finish.emit(True)

                    except Exception as e:
                        self.signals.thread_log.emit(f'Attempts write: {self.number_attempts}, '
                                                     f'{self.values=} in {self.reg_write=}')
                        self.number_attempts += 1
                        time.sleep(0.02)

                if not self.flag_write:
                    self.signals.thread_log.emit(f'Unsuccessful write attempt {self.values=} in {self.reg_write=}')
                    self.signals.thread_err.emit(f'ERROR format - {rw}')
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
                            self.signals.thread_err.emit(f'ERROR write - {rw}')
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
                            self.signals.thread_err.emit(f'ERROR write - {rq}')
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
                                self.signals.thread_err.emit(f'ERROR write - {rw}')
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
                            self.signals.thread_err.emit(f'ERROR write - {rq}')
                            self.signals.write_finish.emit(False)

                if self.flag_next:
                    self.signals.write_finish.emit(True)

        except Exception as e:
            self.signals.thread_err.emit(f'ERROR in thread Writer - {e}')

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
            self.signals.thread_err.emit(f'ERROR in thread Writer/dec_to_bin_str - {e}')


class Reader(QRunnable):
    signals = Signals()

    def __init__(self):
        super(Reader, self).__init__()
        self.cycle = True
        self.is_run = False

        self.client = None
        self.cst = None

        self.read_tag = ''
        self.start_reg = None
        self.count_reg = None
        self.dev_id = None

        self.reg_buffer = None
        self.buffer_count = None
        self.time_start = 0
        self.flag_start_test = False
        self.flag_start_point = False
        self.num_rec = 0
        self.current_rec = -1
        self.count_rec = 0
        self.buffer_all = None
        self.result = {}
        self.values_time = []
        self.values_f = []
        self.values_move = []
        self.values_state = []
        self.time_proc = []

    @pyqtSlot()
    def run(self):
        while self.cycle:
            try:
                if not self.is_run:
                    time.sleep(0.001)
                else:
                    if self.read_tag == 'reg':
                        rr = self.client.execute(self.dev_id, self.cst.READ_HOLDING_REGISTERS,
                                                 self.start_reg, self.count_reg)

                        self.result['regs'] = rr

                        self.signals.read_result.emit(self.result, self.read_tag)

                    elif self.read_tag == 'buffer':
                        self.time_start = time.monotonic()
                        rr = self.client.execute(self.dev_id, self.cst.READ_HOLDING_REGISTERS,
                                                 self.reg_buffer, self.buffer_count * 5)

                        if len(rr) == self.buffer_count * 5:  # 100
                            for i in range(0, self.buffer_count):  # 20
                                flag_add = False
                                ind = 5 * i
                                if self.flag_start_test:
                                    flag_add = True
                                    self.flag_start_test = False
                                else:
                                    if abs(rr[ind] - self.current_rec) == 1:
                                        flag_add = True

                                if flag_add:
                                    self.current_rec = rr[ind]
                                    self.reg_buffer += 5
                                    self.num_rec += 1
                                    self.count_rec += 1

                                    self.values_time.append(rr[ind])
                                    temp = round(unpack('f', pack('<HH', rr[ind + 2], rr[ind + 1]))[0], 0)
                                    self.values_f.append(temp)

                                    temp = round(0.1 * (int.from_bytes(pack('>H', rr[ind + 3]), 'big', signed=True)), 1)
                                    self.values_move.append(temp)

                                    self.values_state.append(rr[ind + 4])

                                else:
                                    break

                            delta_r = 16384 + self.buffer_all - self.reg_buffer
                            if delta_r <= 0:
                                if delta_r < 0:
                                    print('Выход за пределы буфера')
                                self.buffer_count = 20
                                self.reg_buffer = 0x4000
                            else:
                                if delta_r >= 5 * self.buffer_count:
                                    self.buffer_count = 20
                                else:
                                    self.buffer_count = int(delta_r / 5)

                            self.time_proc.append(round(time.monotonic() - self.time_start, 6))

                            self.result['count'] = self.values_time
                            self.result['force'] = self.values_f
                            self.result['move'] = self.values_move
                            self.result['state'] = self.values_state
                            self.result['time'] = self.time_proc

                            self.signals.read_result.emit(self.result, self.read_tag)

                            time.sleep(0.001)

                        else:
                            self.signals.thread_err.emit(str(rr))

            except Exception as e:
                self.signals.thread_err.emit(f'ERROR in thread Reader - {e}')

    def start_test(self, request):
        self.reg_buffer = request.get('reg_buffer')
        self.buffer_count = request.get('buffer_count')
        self.buffer_all = request.get('buffer_all')

        self.values_time = []
        self.values_f = []
        self.values_move = []
        self.values_state = []

        self.time_proc = []

        self.num_rec = 0
        self.count_rec = 0
        self.result = {}
        self.flag_start_test = True
        self.flag_start_point = False
        self.read_tag = 'buffer'

    def stop_test(self):
        self.read_tag = 'reg'

    def start_read(self, client, cst, request):
        self.client = client
        self.cst = cst
        self.dev_id = request.get('dev_id')
        self.start_reg = request.get('reg_read')
        self.count_reg = request.get('read_count')
        self.read_tag = 'reg'

        self.is_run = True

    def stop_read(self):
        self.is_run = False

    def exit_read(self):
        self.cycle = False
