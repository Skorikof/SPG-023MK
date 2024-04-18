import os
from PyQt5.QtCore import QTimer, QObject, pyqtSignal


class ControlSignals(QObject):
    control_msg = pyqtSignal(str)


class Controller:
    def __init__(self, model):
        try:
            self.timer_process = None
            self.values_time = []
            self.values_f = []
            self.values_move = []
            self.values_state = []
            self.time_proc = []

            self.signals = ControlSignals()
            self.model = model

            self.model.start_param()
            self.check_directory()
            self.init_signals()

        except Exception as e:
            self.model.save_log('error', str(e))

    def check_directory(self):
        current_dir = os.getcwd()
        os.chdir(current_dir)
        if not os.path.exists('archive'):
            os.mkdir('archive')
        if not os.path.exists('log'):
            os.mkdir('log')

    def init_signals(self):
        self.model.signals.read_result_buffer.connect(self.result_test)

    def result_test(self, result):
        try:
            self.values_time = result.get('count')
            self.values_f = result.get('force')
            self.values_move = result.get('move')
            self.values_state = result.get('state')
            self.time_proc = result.get('time')

            self.save_result_test()

        except Exception as e:
            txt_log = 'ERROR in controller/result_test - {}'.format(e)
            self.model.status_bar_msg(txt_log)
            self.model.save_log('error', str(e))

    def save_result_test(self):
        try:
            with open('testData.dat', 'w') as file_dat:
                for i in range(0, len(self.values_f)):
                    str_f = str(i) + ' Время: ' + str(self.values_time[i]) + \
                        ' Статус: ' + str(self.values_state[i]) + \
                        ' F = ' + str(self.values_f[i]) + \
                        ' H = ' + str(self.values_move[i]) + '\n'
                    file_dat.write(str_f)

                file_dat.write('=' * 50 + '\n')

        except Exception as e:
            txt_log = 'ERROR in controller/save_result_test - {}'.format(e)
            self.model.status_bar_msg(txt_log)
            self.model.save_log('error', str(e))

    def init_timer(self):
        try:
            self.timer_process = QTimer()
            self.timer_process.setInterval(50)
            self.timer_process.timeout.connect(self.control_process)
            self.timer_process.start()

        except Exception as e:
            txt_log = 'ERROR in controler/init_timer - {}'.format(e)
            self.model.status_bar_msg(txt_log)
            self.model.save_log('error', str(e))

    def control_process(self):
        try:
            if self.model.set_regs.get('lost_control') == '1':
                self.lost_control()
            if self.model.set_regs.get('excess_force') == '1':
                self.excess_force()
            if self.model.set_regs.get('safety_fence') == '1':
                self.safety_fence()
            if self.model.set_regs.get('alarm_highest_position') == '1':
                self.alarm_traverse_position('up')
            if self.model.set_regs.get('alarm_lowest_position') == '1':
                self.alarm_traverse_position('down')

        except Exception as e:
            txt_log = 'ERROR in controller/control_process - {}'.format(e)
            self.model.status_bar_msg(txt_log)
            self.model.save_log('error', str(e))

    def lost_control(self):
        self.signals.control_msg.emit('lost_control')

    def excess_force(self):
        self.signals.control_msg.emit('excess_force')

    def safety_fence(self):
        self.signals.control_msg.emit('safety_fence')

    def alarm_traverse_position(self, pos):
        txt = 'alarm_traverce_{}'.format(pos)
        self.signals.control_msg.emit(txt)

    def position_traverse(self):
        txt = 'pos_traverse'
        self.signals.control_msg.emit(txt)

    def move_detection(self):
        txt = 'move_detection'
        self.signals.control_msg.emit(txt)

    def work_interrupted_operator(self):
        client = self.model.set_connect.get('client')
        if client:
            self.model.set_regs['adr_freq'] = 1
            self.model.motor_stop()
            self.model.set_regs['adr_freq'] = 2
            self.model.motor_stop()
