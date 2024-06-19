import os
import time
from PyQt5.QtCore import QTimer, QObject, pyqtSignal


class ControlSignals(QObject):
    control_msg = pyqtSignal(str)
    traverse_referent = pyqtSignal()
    traverse_position = pyqtSignal()
    wait_yellow_btn = pyqtSignal()
    test_move_cycle = pyqtSignal()
    conv_win_test = pyqtSignal()
    conv_test_cancel = pyqtSignal()
    conv_lamp = pyqtSignal(str)
    lab_win_test = pyqtSignal()
    lab_test_cancel = pyqtSignal()
    cancel_test = pyqtSignal()


class Controller:
    def __init__(self, model):
        try:
            self.response = {}
            self.amort = None
            self.timer_process = None
            self.count_cycle = 0
            self.flag_alarm = False

            self.signals = ControlSignals()
            self.model = model
            self.model.start_param_model()
            self.model.set_regs['stage'] = 'wait'

            self.check_directory()
            self.init_signals()
            self.init_timer()

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
            self.model.signals.full_cycle.connect(self.update_full_cycle)
            self.model.signals.test_launch.connect(self.yellow_btn_push)

        except Exception as e:
            self.model.log_error(f'ERROR in controller/init_signals - {e}')

    def update_data_ctrl(self, response):
        try:

            self.response = {**self.response, **response}

        except Exception as e:
            self.model.log_error(f'ERROR in controller/update_data - {e}')

    def update_full_cycle(self):
        try:
            self.count_cycle += 1

        except Exception as e:
            self.model.log_error(f'ERROR in controller/update_full_cycle - {e}')

    def init_timer(self):
        try:
            self.timer_process = QTimer()
            self.timer_process.setInterval(50)
            self.timer_process.timeout.connect(self.update_stage_on_timer)
            self.timer_process.start()

        except Exception as e:
            self.model.log_error(f'ERROR in controller/init_timer - {e}')

    def update_stage_on_timer(self):
        try:
            # self.control_alarm_traverse_position()

            stage = self.response.get('stage')
            type_test = self.response.get('type_test')
            flag_test = self.response.get('test_flag')
            flag_alarm = self.response.get('alarm_stage')

            # if flag_test:
            #     self.control_alarm_state()

            if stage == 'wait':
                pass

            elif stage == 'traverse_referent':
                high_switch = self.response.get('highest_position')

                if high_switch == 1:
                    self.model.motor_stop()
                    self.model.set_regs['traverse_referent'] = True
                    self.model.set_regs['stage'] = 'wait'
                    time.sleep(0.2)
                    self.traverse_install_point()

            elif stage == 'install_amort':
                control_point = float(self.response.get('traverse_point'))
                pos_trav = float(self.response.get('traverse_move'))

                if 0.6 < abs(control_point - pos_trav) <= 5:
                    self.write_speed_motor(2, freq=15)

                if abs(control_point - pos_trav) <= 0.6:
                    self.model.motor_stop()
                    self.model.set_regs['traverse_position'] = True
                    self.model.set_regs['stage'] = 'wait'
                    time.sleep(0.2)
                    self.signals.wait_yellow_btn.emit()
                    
            elif stage == 'start_point_amort':
                control_point = float(self.response.get('traverse_point'))
                pos_trav = float(self.response.get('traverse_move'))

                if 0.6 < abs(control_point - pos_trav) <= 5:
                    self.write_speed_motor(2, freq=15)

                if abs(control_point - pos_trav) <= 0.6:
                    self.model.motor_stop()
                    self.model.set_regs['traverse_position'] = True
                    time.sleep(0.2)
                    self.test_move_cycle()

            elif stage == 'test_move_cycle':
                exc_force = self.response.get('excess_force')
                if self.count_cycle >= 1:
                    self.change_excess_force(2000)

                    if type_test == 'lab':
                        self.laboratory_test_speed()

                    elif type_test == 'conv':
                        self.conv_test_speed(1)

                if exc_force == 1:
                    self.excess_force()
                    self.model.set_regs['stage'] = 'wait'

            elif stage == 'test_speed_one':
                if self.count_cycle == 3:
                    self.conv_test_speed(2)

            elif stage == 'test_speed_two':
                if self.count_cycle == 3:
                    self.result_conveyor_test()
                    self.model.set_regs['stage'] = 'wait'
                    self.stop_gear_min_pos()

            elif stage == 'stop_gear_min_pos':
                point = float(self.response.get('min_point'))
                move = float(self.response.get('move'))
                if move <= point + 1:
                    self.model.motor_stop()
                    time.sleep(0.5)
                    flag = self.response.get('test_launch')
                    if flag:
                        self.traverse_install_point()
                    else:
                        self.traverse_end_point()

            elif stage == 'end_test':
                control_point = float(self.response.get('traverse_point'))
                pos_trav = float(self.response.get('traverse_move'))

                if 0.6 < abs(control_point - pos_trav) <= 5:
                    self.write_speed_motor(2, freq=15)

                if abs(control_point - pos_trav) <= 0.6:
                    self.model.motor_stop()
                    self.model.set_regs['traverse_position'] = True
                    self.model.set_regs['stage'] = 'wait'
                    if not flag_alarm:
                        self.signals.cancel_test.emit()

        except Exception as e:
            self.model.log_error(f'ERROR in controller/update_stage_on_timer - {e}')

    # FIXME Как отследить дребезг/помехи в аварийных сигналах?
    def rattle_alarm_signal(self, state):
        try:
            pass

        except Exception as e:
            self.model.log_error(f'ERROR in controller/rattle_alarm_signal - {e}')

    def control_alarm_traverse_position(self):
        try:

            if self.response.get('alarm_highest_position') == 0:
                self.alarm_traverse_position('up')
            if self.response.get('alarm_lowest_position') == 0:
                self.alarm_traverse_position('down')

        except Exception as e:
            self.model.log_error(f'ERROR in controller/control_alarm_traverse_position - {e}')

    def control_alarm_state(self):
        try:
            if self.response.get('lost_control') == 1:
                self.lost_control()
            if self.response.get('excess_force') == 1:
                self.excess_force()
            if self.response.get('safety_fence') == 1:
                self.safety_fence()

            self.check_max_temperature()

        except Exception as e:
            self.model.log_error(f'ERROR in controller/control_alarm_state - {e}')

    def check_max_temperature(self):
        if self.response.get('max_temper') >= self.amort.max_temper:
            self.excess_temperature()

    def lost_control(self):
        print('lost control!')
        # self.stop_gear_now()
        # self.lamp_red_switch_on()
        # self.model.set_regs['stage'] = 'wait'
        # self.model.set_regs['alarm_stage'] = True
        # self.model.set_regs['test_launch'] = False
        # self.model.set_regs['test_flag'] = False
        # self.model.log_error(f'lost control')
        # self.signals.control_msg.emit('lost_control')

    def excess_force(self):
        print('excess force')
        # self.stop_gear_now()
        # self.lamp_red_switch_on()
        # self.model.set_regs['stage'] = 'wait'
        # self.model.set_regs['alarm_stage'] = True
        # self.model.set_regs['test_launch'] = False
        # self.model.set_regs['test_flag'] = False
        # self.model.log_error(f'excess force')
        # self.signals.control_msg.emit('excess_force')

    def excess_temperature(self):
        self.stop_gear_min_pos()
        self.lamp_red_switch_on()
        self.model.set_regs['alarm_stage'] = True
        self.model.set_regs['test_launch'] = False
        self.model.log_error(f'excess temperature')
        self.signals.control_msg.emit('excess_temperature')

    def safety_fence(self):
        print('safety fence')
        # self.stop_gear_min_pos()
        # self.lamp_red_switch_on()
        # self.model.set_regs['alarm_stage'] = True
        # self.model.set_regs['test_launch'] = False
        # self.model.log_error(f'safety fence')
        # self.signals.control_msg.emit('safety_fence')

    def alarm_traverse_position(self, pos):
        self.stop_gear_now()
        self.lamp_red_switch_on()
        self.model.set_regs['stage'] = 'wait'
        self.model.set_regs['alarm_stage'] = True
        self.model.set_regs['test_launch'] = False
        self.model.set_regs['test_flag'] = False
        txt = 'alarm_traverse_{}'.format(pos)
        self.model.log_error(f'alarm traverse {pos}')
        self.signals.control_msg.emit(txt)

    def position_traverse(self):
        txt = 'pos_traverse'
        self.signals.control_msg.emit(txt)

    def move_detection(self):
        txt = 'move_detection'
        self.signals.control_msg.emit(txt)

    def work_interrupted_operator(self):
        self.model.set_regs['test_launch'] = False
        self.model.set_regs['test_flag'] = False
        self.model.set_regs['stage'] = 'wait'
        self.lamp_all_switch_off()
        if self.model.client:
            self.stop_gear_now()
            self.model.reader_stop_test()

    def yellow_btn_push(self):
        """Обработка нажатия жёлтой кнопки, запускает она испытание или останавливает"""
        try:
            flag = self.model.set_regs.get('test_flag')
            if not flag:
                self.lamp_all_switch_off()
                self.traverse_start_test_point()
                self.model.set_regs['test_flag'] = True

            else:
                self.model.set_regs['test_flag'] = False
                self.stop_test_clicked()

        except Exception as e:
            self.model.log_error(f'ERROR in controller/yellow_btn_push - {e}')

    def current_amort(self):
        try:
            self.amort = self.response.get('amort')

        except Exception as e:
            self.model.log_error(f'ERROR in controller/current_amort - {e}')

    def write_speed_motor(self, adr: int, speed: float = None, freq: int = None):
        """
        Запись скорости вращения двигателя, если задана скорость, то она пересчитывается в частоту,
        частота записывается напрямую
        """
        try:
            if not freq:
                self.model.set_regs['frequency'] = self.model.calculate_freq(speed)
            elif not speed:
                self.model.set_regs['frequency'] = 100 * freq

            self.model.set_regs['adr_freq'] = adr
            self.model.write_frequency()
            time.sleep(0.2)

        except Exception as e:
            self.model.log_error(f'ERROR in controller/write_speed_motor - {e}')

    def start_test_clicked(self):
        """
        Точка входа в испытание, определение референтной траверсы, если известна,
        то сразу запуск позиционирования для установки амортизатора
        """
        try:
            self.model.set_regs['max_temperature'] = 0
            self.model.set_regs['alarm_stage'] = False
            self.model.set_regs['test_launch'] = True
            # trav_ref = self.response.get('traverse_referent')
            # if not trav_ref:
            #     self.traverse_referent_point()
            #
            # else:
            self.traverse_install_point()

            # temp = self.response.get('type_test')
            # if temp == 'lab':
            #     self.start_laboratory_test()
            #
            # elif temp == 'conv':
            #     self.start_conveyor_test()
            #
            # else:
            #     pass

        except Exception as e:
            self.model.log_error(f'ERROR in controller/start_test_clicked - {e}')

    def stop_test_clicked(self):
        """
        Завершение теста, если определена референтная коленвала, то остановка в нижней точке,
        иначе моментальная остановка
        """
        try:
            self.model.set_regs['stage'] = 'wait'
            self.model.set_regs['test_launch'] = False

            self.change_excess_force(2000)

            flag = self.response.get('gear_referent')
            if flag:
                self.stop_gear_min_pos()
            else:
                self.stop_gear_now()
                self.signals.cancel_test.emit()

        except Exception as e:
            self.model.log_error(f'ERROR in controller/stop_test_clicked - {e}')

    def convert_adapter(self, ind):
        """Перевод номера адаптера в его длинну"""
        try:
            if ind == 1:
                return 20

            else:
                return 0

        except Exception as e:
            self.model.log_error(f'ERROR in controller/convert_adapter - {e}')

    def traverse_move_position(self, set_point):
        """Непосредственно включение и перемещение траверсы"""
        try:
            self.write_speed_motor(2, freq=25)

            pos_trav = self.response.get('traverse_move')
            self.model.set_regs['traverse_position'] = False
            self.model.set_regs['traverse_point'] = set_point

            self.model.write_bit_unblock_control()
            time.sleep(0.1)

            if pos_trav > set_point:
                self.model.motor_up()
            else:
                self.model.motor_down()

        except Exception as e:
            self.model.log_error(f'ERROR in controller/traverse_move_position - {e}')

    def traverse_referent_point(self):
        """Подъём траверсы до концевика для определения референтной точки"""
        try:
            self.signals.traverse_referent.emit()
            self.model.set_regs['traverse_position'] = False
            self.write_speed_motor(2, freq=25)
            self.model.set_regs['stage'] = 'traverse_referent'
            self.model.motor_up()

        except Exception as e:
            self.model.log_error(f'ERROR in controller/traverse_referent_point - {e}')

    def traverse_install_point(self):
        """Позционирование траверсы для установки амортизатора"""
        try:
            self.position_traverse()
            stock_point = self.response.get('traverse_stock')
            hod = self.amort.hod
            len_max = self.amort.max_length
            adapter = self.convert_adapter(self.amort.adapter)
            install_point = (stock_point + hod / 2) - len_max - adapter + 2

            pos_trav = float(self.response.get('traverse_move'))
            if abs(pos_trav - install_point) < 2:
                self.signals.wait_yellow_btn.emit()

            else:
                self.model.set_regs['stage'] = 'install_amort'
                self.traverse_move_position(install_point)

        except Exception as e:
            self.model.log_error(f'ERROR in controller/traverse_install_point - {e}')

    def traverse_start_test_point(self):
        """Позиционирование траверсы для начала испытания"""
        try:
            self.position_traverse()
            stock_point = int(self.response.get('traverse_stock'))
            len_max = self.amort.max_length
            len_min = self.amort.min_length
            mid_point = (len_max - len_min) / 2
            adapter = self.convert_adapter(self.amort.adapter)
            start_point = stock_point - len_max - adapter + mid_point

            self.model.set_regs['stage'] = 'start_point_amort'
            self.traverse_move_position(start_point)

        except Exception as e:
            self.model.log_error(f'ERROR in controller/traverse_start_test_point - {e}')

    def traverse_end_point(self):
        """Подъём траверсы в исходное состояние и завершение испытания"""
        try:
            self.position_traverse()
            stock_point = self.response.get('traverse_stock')
            hod = self.amort.hod
            len_max = self.amort.max_length
            adapter = self.convert_adapter(self.amort.adapter)
            end_point = (stock_point + hod / 2) - len_max - adapter + 2

            self.model.set_regs['stage'] = 'end_test'
            self.traverse_move_position(end_point)

        except Exception as e:
            self.model.log_error(f'ERROR in controller/traverse_end_point - {e}')

    def test_move_cycle(self):
        """Проверочный ход"""
        try:
            self.move_detection()

            self.change_excess_force(30)

            self.model.write_bit_force_cycle(1)
            time.sleep(0.2)

            self.write_speed_motor(1, speed=0.05)

            self.model.set_regs['stage'] = 'test_move_cycle'
            self.count_cycle = 0
            self.model.set_regs['start_pos'] = False
            self.model.set_regs['start_direction'] = False
            self.model.set_regs['min_pos'] = False
            self.model.set_regs['max_pos'] = False

            self.model.reader_start_test()
            time.sleep(0.5)
            self.model.motor_up()

        except Exception as e:
            self.model.log_error(f'ERROR in controller/test_move_cycle - {e}')

    def change_excess_force(self, force):
        """Запись аварийного усилия и отключение бита блокировки"""
        try:
            self.model.set_regs['force_alarm'] = force
            self.model.write_emergency_force()
            time.sleep(0.2)

            self.model.write_bit_unblock_control()
            time.sleep(0.2)

        except Exception as e:
            self.model.log_error(f'ERROR in controller/change_excess_force - {e}')

    def conv_test_speed(self, ind):
        """Сигнал на окно конвейерного испытания, разгон до скорости индекса(1 или 2)"""
        try:
            self.signals.conv_win_test.emit()

            if ind == 1:
                self.write_speed_motor(1, speed=self.amort.speed_one)
                self.model.set_regs['stage'] = 'test_speed_one'
                self.model.motor_up()

            elif ind == 2:
                self.write_speed_motor(1, speed=self.amort.speed_two)
                self.model.set_regs['stage'] = 'test_speed_two'

            self.count_cycle = 0

        except Exception as e:
            self.model.log_error(f'ERROR in controller/conv_test - {e}')

    def laboratory_test_speed(self):
        """Сигнал на окно лабораторного испытания, разгон до заданной скорости"""
        try:
            self.signals.lab_win_test.emit()

            speed = self.amort.speed_one
            self.write_speed_motor(1, speed=speed)

            self.model.motor_up()

        except Exception as e:
            self.model.log_error(f'ERROR in controller/start_laboratory_test - {e}')

    def result_conveyor_test(self):
        """Включение индикаторов, зелёный - в допусках, красный - нет"""
        try:
            comp_max = self.response.get('max_comp')
            recoil_max = self.response.get('max_recoil')

            if self.amort.min_comp < comp_max < self.amort.max_comp and \
                    self.amort.min_recoil < recoil_max < self.amort.max_recoil:
                self.lamp_green_switch_on()

            else:
                self.lamp_red_switch_on()

        except Exception as e:
            self.model.log_error(f'ERROR in controller/result_conveyor_test - {e}')

    def stop_gear_min_pos(self):
        """Снижение скорости и остановка привода в нижней точке"""
        try:
            self.model.reader_stop_test()
            time.sleep(0.5)

            self.write_speed_motor(1, speed=0.05)

            self.model.set_regs['test_flag'] = False
            self.model.set_regs['stage'] = 'stop_gear_min_pos'

        except Exception as e:
            self.model.log_error(f'ERROR in controller/stop_gear_min_pos - {e}')

    def stop_gear_now(self):
        """Останов всех двигателей сейчас"""
        try:
            self.model.set_regs['adr_freq'] = 1
            self.model.motor_stop()
            time.sleep(0.1)
            self.model.set_regs['adr_freq'] = 2
            self.model.motor_stop()
            time.sleep(0.1)

        except Exception as e:
            self.model.log_error(f'ERROR in controller/stop_gear_now - {e}')

    def lamp_all_switch_on(self):
        """Включение всех индикаторов"""
        try:
            self.model.write_bit_green_light(1)
            time.sleep(0.1)
            self.model.write_bit_red_light(1)
            time.sleep(0.1)
            self.signals.conv_lamp.emit('all_on')

        except Exception as e:
            self.model.log_error(f'ERROR in controller/lamp_all_switch_on - {e}')

    def lamp_all_switch_off(self):
        """Выключение всех индикаторов"""
        try:
            self.model.write_bit_green_light(0)
            time.sleep(0.1)
            self.model.write_bit_red_light(0)
            time.sleep(0.1)
            self.signals.conv_lamp.emit('all_off')

        except Exception as e:
            self.model.log_error(f'ERROR in controller/lamp_all_switch_off - {e}')

    def lamp_green_switch_on(self):
        """Включение зелёного индикатора"""
        try:
            self.model.write_bit_green_light(1)
            time.sleep(0.1)
            self.model.write_bit_red_light(0)
            time.sleep(0.1)
            self.signals.conv_lamp.emit('green_on')

        except Exception as e:
            self.model.log_error(f'ERROR in controller/lamp_green_switch_on - {e}')

    def lamp_red_switch_on(self):
        """Включение красного индикатора"""
        try:
            self.model.write_bit_green_light(0)
            time.sleep(0.1)
            self.model.write_bit_red_light(1)
            time.sleep(0.1)
            self.signals.conv_lamp.emit('red_on')

        except Exception as e:
            self.model.log_error(f'ERROR in controller/lamp_red_switch_on - {e}')
