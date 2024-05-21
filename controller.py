import os
import time
from PyQt5.QtCore import QTimer, QObject, pyqtSignal


class ControlSignals(QObject):
    control_msg = pyqtSignal(str)
    traverse_referent = pyqtSignal()
    traverse_position = pyqtSignal()
    wait_yellow_btn = pyqtSignal()
    test_move_cycle = pyqtSignal()


class Controller:
    def __init__(self, model):
        try:
            self.response = {}
            self.amort = None
            self.timer_process = None

            self.signals = ControlSignals()
            self.model = model

            self.model.start_param()
            self.check_directory()
            self.init_signals()

        except Exception as e:
            self.model.log_error(f'ERROR in controller/__init__ - {e}')

    def check_directory(self):
        current_dir = os.getcwd()
        os.chdir(current_dir)
        if not os.path.exists('archive'):
            os.mkdir('archive')
        if not os.path.exists('log'):
            os.mkdir('log')

    def init_signals(self):
        try:
            self.model.signals.read_finish.connect(self.update_data)

        except Exception as e:
            self.model.log_error(f'ERROR in controller/init_signals - {e}')

    def update_data(self, response):
        try:
            self.response = response

        except Exception as e:
            self.model.log_error(f'ERROR in controller/update_data - {e}')

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
            if self.response.get('lost_control') == 1:
                self.lost_control()
            if self.response.get('excess_force') == 1:
                self.excess_force()
            if self.response.get('safety_fence') == 1:
                self.safety_fence()
            if self.response.get('alarm_highest_position') == 1:
                self.alarm_traverse_position('up')
            if self.response.get('alarm_lowest_position') == 1:
                self.alarm_traverse_position('down')
            # if self.response.get('test_launch') == 1:
            #     self.yellow_btn_push()

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
            self.stop_test_clicked()

    # def yellow_btn_push(self):
    #     if test == 'stop':
    #         test == 'start'
    #     elif test == 'start':
    #         test == 'stop'

    def current_amort(self):
        try:
            self.amort = self.response.get('amort')

        except Exception as e:
            self.model.log_error(f'ERROR in controller/current_amort - {e}')

    def start_test_clicked(self):
        try:
            self.model.write_bit_unblock_control()
            time.sleep(0.1)
            self.check_traverse_position()

            # self.start_test()

        except Exception as e:
            self.model.log_error(f'ERROR in controller/start_test_clicked - {e}')

    def stop_test_clicked(self):
        try:
            len_max = self.amort.max_length
            bracket = self.response.get('bracket_height')
            stock_point = len_max + bracket

            self.traverse_move_position(stock_point)

        except Exception as e:
            self.model.log_error(f'ERROR in controller/stop_test_clicked - {e}')

    def check_traverse_position(self):
        try:
            hod = self.amort.hod
            len_min = self.amort.min_length
            len_max = self.amort.max_length
            midpoint = (len_max - len_min)
            bracket = self.response.get('bracket_height')
            test_point = bracket + len_min + midpoint + hod / 2

            if not self.response['traverse_referent']:
                self.signals.traverse_referent.emit()
                self.traverse_referent_point()

            # if not self.response['traverse_position']:
            #     self.signals.traverse_position.emit()
            #     set_point = len_max + bracket
            #     self.traverse_move_position(set_point)
            #
            # if test_point != self.response['traverse_position']:
            #     self.traverse_move_position(test_point)
            #
            # if test_point == self.response['traverse_position']:
            #     self.signals.wait_yellow_btn.emit()

        except Exception as e:
            self.model.log_error(f'ERROR in controller/check_traverse_position - {e}')

    def traverse_move_position(self, set_point):
        """Позционирование траверсы для установки амортизатора"""
        try:
            self.model.set_regs['adr_freq'] = 2
            self.model.set_regs['frequency'] = 1000
            if self.response['traverse_move'] > set_point:
                self.model.motor_down()
            else:
                self.model.motor_up()

            pos_trav = self.response.get('traverse_move')
            while set_point != (pos_trav - 2) or set_point != (pos_trav + 2):
                pos_trav = self.response.get('traverse_move')
                print(f'Позиция траверсы --> {pos_trav}')
                time.sleep(0.1)

            self.model.motor_stop()
            self.model.set_regs['traverse_position'] = True

        except Exception as e:
            self.model.log_error(f'ERROR in controller/traverse_move_position - {e}')

    def traverse_referent_point(self):
        """Подъём траверсы до концевика для определения референтной точки"""
        try:
            self.model.set_regs['traverse_position'] = False
            self.model.set_regs['adr_freq'] = 2
            self.model.set_regs['frequency'] = 1000
            self.model.write_frequency()
            self.model.motor_up()
            time.sleep(0.1)
            control = self.response.get('highest_position')
            while control != '1':
                print(f'Состояние верхнего концевика --> {self.response["highest_position"]}')
                print(f'Перемещение траверсы --> {self.response.get("traverse_move")}')
                control = self.response.get('highest_position')
                time.sleep(0.1)

            self.model.motor_stop()
            time.sleep(0.2)
            self.model.set_regs['traverse_referent'] = True
            self.model.set_regs['traverse_referent_point'] = self.response.get('traverse_move')

        except Exception as e:
            self.model.log_error(f'ERROR in controller/traverse_referent_point - {e}')

    def test_move_cycle(self):
        """Проверочный ход"""
        try:
            self.signals.test_move_cycle.emit()
            self.model.set_regs['force_alarm'] = 30
            self.model.write_emergency_force()
            time.sleep(0.1)

            self.model.set_regs['frequency'] = self.model.calculate_freq(0.01)
            self.model.set_regs['adr_freq'] = 1
            self.model.write_frequency()
            time.sleep(0.1)

            self.model.set_state['full_cycle'] = False
            self.model.motor_up()

            control = self.response.get('full_cycle')
            while not control:
                control = self.response.get('full_cycle')
                time.sleep(0.1)

            self.model.motor_stop()

            return True

        except Exception as e:
            self.model.log_error(f'ERROR in controller/test_move_cycle - {e}')

    def start_test(self):
        try:
            self.model.set_regs['force_alarm'] = 2000
            self.model.write_emergency_force()
            time.sleep(0.1)

            temp = self.response.get('type_test')
            if temp == 'lab':
                self.start_laboratory_test()

            elif temp == 'conv':
                self.start_conveyor_test()

            else:
                pass

        except Exception as e:
            self.model.log_error(f'ERROR in controller/start_test - {e}')

    def start_laboratory_test(self):
        try:
            speed = self.amort.speed_one
            self.model.set_regs['frequency'] = self.model.calculate_freq(speed)
            self.model.set_regs['adr_freq'] = 1
            self.model.write_frequency()
            time.sleep(0.1)

            self.model.set_state['full_cycle'] = False
            self.model.motor_up()

        except Exception as e:
            self.model.log_error(f'ERROR in controller/start_laboratory_test - {e}')

    def start_conveyor_test(self):
        try:
            pass

        except Exception as e:
            self.model.log_error(f'ERROR in controller/start_conveyor_test - {e}')

    # def stop_gear_min_pos(self):
    #     try:
    #
    #
    #     except Exception as e:
    #         self.model.log_error(f'ERROR in controller/stop_gear_min_pos - {e}')