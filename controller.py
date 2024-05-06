import os
from PyQt5.QtCore import QTimer, QObject, pyqtSignal


class ControlSignals(QObject):
    control_msg = pyqtSignal(str)


class Controller:
    def __init__(self, model):
        try:
            self.timer_process = None
            # self.values_time = []
            # self.values_f = []
            # self.values_move = []
            # self.values_state = []
            # self.time_proc = []
            # self.val_1 = []
            # self.val_2 = []
            # self.val_3 = []
            # self.val_4 = []
            # self.val_5 = []
            self.count_msg = 0
            self.count_err = 0

            self.signals = ControlSignals()
            self.model = model

            self.model.start_param()
            self.check_directory()

        except Exception as e:
            self.model.log_error(f'ERROR in controller/__init__ - {e}')

    def check_directory(self):
        current_dir = os.getcwd()
        os.chdir(current_dir)
        if not os.path.exists('archive'):
            os.mkdir('archive')
        if not os.path.exists('log'):
            os.mkdir('log')

    # def result_test(self, result):
    #     try:
    #         # self.val_1 = result.get('1')
    #         # self.val_2 = result.get('2')
    #         # self.val_3 = result.get('3')
    #         # self.val_4 = result.get('4')
    #         # self.val_5 = result.get('5')
    #
    #         # self.values_time = result.get('count')
    #         # self.values_f = result.get('force')
    #         # self.values_move = result.get('move')
    #         # self.values_state = result.get('state')
    #         # self.time_proc = result.get('time')
    #         #
    #         # self.save_result_test()
    #
    #     except Exception as e:
    #         txt_log = 'ERROR in controller/result_test - {}'.format(e)
    #         self.model.status_bar_msg(txt_log)
    #         self.model.save_log('error', str(e))
    #
    #
    # def print_result_test(self, res):
    #     try:
    #         for i in range(0, len(res.get('count'))):
    #             self.count_msg += 1
    #             if res.get('force')[i] == -100000.0:
    #                 self.count_err += 1
    #
    #             print(f'{str(i)} Счётчик: {str(res.get("count")[i])} '
    #                   f'Статус: {str(res.get("state")[i])} '
    #                   f'УСИЛИЕ: {str(res.get("force")[i])} '
    #                   f'ПЕРЕМЕЩЕНИЕ: {str(res.get("move")[i])}')
    #
    #             print(f'Count error in force sensor = {self.count_err} in all msg = {self.count_msg}')
    #
    #         # with open('testData.dat', 'w') as file_dat:
    #         #     for i in range(0, len(self.val_1)):
    #         #         str_f = str(i) + ' Время: ' + str(self.values_time[i]) + \
    #         #             ' Статус: ' + str(self.values_state[i]) + \
    #         #             ' УСИЛИЕ = ' + str(self.values_f[i]) + \
    #         #             ' ПЕРЕМЕШЕНИЕ = ' + str(self.values_move[i]) + '\n'
    #
    #                 # str_f = str(i) + ' Время: ' + str(self.val_1[i]) + \
    #                 #     ' Усилие старш: ' + str(self.val_2[i]) + \
    #                 #     ' Усилие младш: ' + str(self.val_3[i]) + \
    #                 #     ' Перемещение: ' + str(self.val_4[i]) + \
    #                 #     ' Статус: ' + str(self.val_5[i]) + '\n'
    #             #     file_dat.write(str_f)
    #             #
    #             # file_dat.write('=' * 50 + '\n')
    #
    #     except Exception as e:
    #         txt_log = 'ERROR in controller/save_result_test - {}'.format(e)
    #         self.model.status_bar_msg(txt_log)
    #         self.model.save_log('error', str(e))

    def init_timer(self):
        try:
            self.timer_process = QTimer()
            self.timer_process.setInterval(50)
            self.timer_process.timeout.connect(self.control_process)
            self.timer_process.start()

        except Exception as e:
            self.model.log_error(f'ERROR in controller/init_timer - {e}')

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
            self.model.log_error(f'ERROR in controller/control_process - {e}')

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
