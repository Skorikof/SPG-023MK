import numpy as np
from PyQt5.QtCore import pyqtSignal, QObject

from logger import my_logger


class StepsSignal(QObject):
    stage_from_logic = pyqtSignal(str)
    next_stage_from_logic = pyqtSignal(str)
    conv_result_lamp = pyqtSignal(str, str)


class Steps:
    def __init__(self, model):
        self.logger = my_logger.get_logger(__name__)
        self.model = model
        self.signals = StepsSignal()

        self.flag_freq_1_step = False
        self.flag_freq_2_step = False
        self.count_wait_point = 0

    def stage_control_alarm_state(self):
        try:
            tag = 'null'
            if not self.model.set_regs.get('type_test') == 'temper':
                if self.model.temper_max >= self.model.amort.max_temper:
                    tag = 'excess_temperature'

            if self.model.state_dict.get('lost_control', False) is True:
                tag = 'lost_control'
            if self.model.state_dict.get('excess_force', False) is True:
                tag = 'excess_force'
            if self.model.state_dict.get('safety_fence', False) is True:
                tag = 'safety_fence'

            return tag

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in Steps/stage_control_alarm_state - {e}')

    def step_search_hod_gear(self):
        try:
            if self.model.amort is None:
                hod = 120
            else:
                hod = self.model.amort.hod

            if hod > 100:
                speed = 0.1
            elif 50 < hod <= 100:
                speed = 0.06
            else:
                speed = 0.03

            self.signals.stage_from_logic.emit('wait')
            self.signals.next_stage_from_logic.emit('search_hod')

            self.model.reset_current_circle()

            command = {'search_hod': True,
                       'alarm_flag': False,
                       'alarm_tag': '',
                       }
            self.model.update_main_dict(command)

            self.model.write_speed_motor(1, speed=speed)
            self.signals.stage_from_logic.emit('wait_buffer')
            self.model.write_bit_force_cycle(1)

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in Steps/step_search_hod_gear - {e}')

    def stage_search_hod(self, count_cycle):
        try:
            if count_cycle >= 1:
                self.model.hod_measure = np.round(abs(self.model.min_point) + abs(self.model.max_point), decimals=2)

                return True

            else:
                return False

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in Steps/stage_search_hod - {e}')

    def step_move_gear_set_pos(self):
        try:
            if self.model.amort is None:
                hod = 120
            else:
                hod = self.model.amort.hod

            if hod > 100:
                speed = 0.03
            elif 50 < hod <= 100:
                speed = 0.02
            else:
                speed = 0.01

            self.signals.stage_from_logic.emit('wait')
            self.signals.next_stage_from_logic.emit('pos_set_gear')

            self.model.reset_current_circle()

            command = {'alarm_flag': False,
                       'alarm_tag': '',
                       }

            self.model.update_main_dict(command)
            self.model.write_speed_motor(1, speed=speed)
            self.signals.stage_from_logic.emit('wait_buffer')
            self.model.write_bit_force_cycle(1)

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in Steps/step_move_gear_set_pos - {e}')

    def stage_pos_set_gear(self):
        try:
            if self.model.gear_referent:
                if self.model.max_pos:
                    if abs(14 - self.model.move_now) < 5:
                        self.model.motor_stop(1)
                        self.model.reader_stop_test()
                        self.model.write_bit_force_cycle(0)
                        self.model.min_pos = False
                        self.model.max_pos = False

                        return True

            return False

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in Steps/stage_pos_set_gear - {e}')

    def step_stop_gear_end_test(self):
        """Остановка двигателя после испытания и перед исходным положением"""
        try:
            self.model.motor_stop(1)

            self.signals.stage_from_logic.emit('stop_gear_end_test')

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in Steps/step_stop_gear_end_test - {e}')

    def stage_stop_gear_end_test(self):
        try:
            if np.std(self.model.move_array) < 0.1:  # Перемещение перестало изменяться
                self.count_wait_point += 1

            else:
                self.count_wait_point = 0

            if self.count_wait_point > 5:
                self.signals.stage_from_logic.emit('wait')
                self.count_wait_point = 0
                return True
            return False

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in steps/stop_gear_end_test - {e}')

    def step_stop_gear_min_pos(self):
        """Снижение скорости и остановка привода в нижней точке"""
        try:
            self.model.reader_stop_test()

            self.model.write_bit_force_cycle(0)

            if self.model.amort is None:
                hod = 120
            else:
                hod = self.model.amort.hod

            if hod > 100:
                speed = 0.03
            elif 50 < hod <= 100:
                speed = 0.02
            else:
                speed = 0.01

            self.model.write_speed_motor(1, speed=speed)

            self.model.motor_up(1)

            self.signals.stage_from_logic.emit('stop_gear_min_pos')

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in Steps/step_stop_gear_min_pos - {e}')

    def stage_stop_gear_min_pos(self):
        try:
            if self.model.move_now < self.model.min_point + 2:
                self.model.motor_stop(1)

                self.signals.stage_from_logic.emit('wait')

                self.model.clear_data_in_array_graph()

                self.model.reset_current_circle()

                self.model.set_regs['test_flag'] = False

                return True

            return False

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in Steps/stage_stop_gear_min_pos - {e}')

    def step_test_move_cycle(self):
        """Проверочный ход"""
        try:
            if self.model.amort is None:
                hod = 120
            else:
                hod = self.model.amort.hod

            if hod > 100:
                speed = 0.06
            elif 50 < hod <= 100:
                speed = 0.03
            else:
                speed = 0.01
            self.model.write_speed_motor(1, speed=speed)
            self.model.write_bit_force_cycle(1)

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in Steps/step_test_move_cycle - {e}')

    def step_pumping_before_test(self):
        """Прокачка на скорости 0.2 3 оборота перед запуском теста"""
        try:
            if self.model.amort is None:
                hod = 120
            else:
                hod = self.model.amort.hod

            if hod >= 100:
                speed = 0.2
            elif 50 < hod <= 100:
                speed = 0.1
            else:
                speed = 0.03

            self.model.write_speed_motor(1, speed=speed)

            self.signals.stage_from_logic.emit('pumping')

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in Steps/step_pumping_before_test - {e}')

    def step_traverse_referent_point(self):
        """Подъём траверсы до концевика для определения референтной точки"""
        try:
            self.model.write_speed_motor(2, freq=30)
            self.signals.stage_from_logic.emit('traverse_referent')

            self.model.motor_up(2)

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in Steps/step_traverse_referent_point - {e}')

    def stage_traverse_referent(self):
        try:
            if self.model.switch_dict.get('highest_position', False) is True:
                self.model.motor_stop(2)

                self.model.set_regs['traverse_referent'] = True

                return True
            return False

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in Steps/stage_traverse_referent - {e}')

    def step_move_traverse_out_alarm(self, pos):
        try:
            self.flag_freq_1_step = False
            self.flag_freq_2_step = False
            self.model.write_speed_motor(2, freq=30)
            if pos == 'up':
                self.model.motor_down(2)

            elif pos == 'down':
                self.model.motor_up(2)

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in steps/step_move_traverse_out_alarm - {e}')

    def step_traverse_move_position(self, set_point):
        """Непосредственно включение и перемещение траверсы"""
        try:
            self.flag_freq_1_step = False
            self.flag_freq_2_step = False
            self.model.write_speed_motor(2, freq=30)
            pos_trav = self.model.move_traverse

            if pos_trav > set_point:
                self.model.motor_up(2)
            else:
                self.model.motor_down(2)

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in steps/step_traverse_move_position - {e}')

    def step_control_traverse_move(self, point) -> bool:  # Функция отслеживания траверсы, при достижении точки останов
        try:
            if 5 < abs(point - self.model.move_traverse) <= 10:
                if not self.flag_freq_1_step:
                    self.model.write_speed_motor(2, freq=20)
                    self.flag_freq_1_step = True

            if 1 < abs(point - self.model.move_traverse) <= 5:
                if not self.flag_freq_2_step:
                    self.model.write_speed_motor(2, freq=15)
                    self.flag_freq_2_step = True

            if abs(point - self.model.move_traverse) <= 0.5:
                self.model.motor_stop(2)
                return True

            return False

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in steps/control_traverse_move - {e}')

    def step_result_conveyor_test(self, step):
        """Включение индикаторов, зелёный - в допусках, красный - нет"""
        try:
            min_comp, max_comp = 0, 2000
            min_recoil, max_recoil = 0, 2000

            if step == 'one':
                min_comp, max_comp = self.model.amort.min_comp, self.model.amort.max_comp
                min_recoil, max_recoil = self.model.amort.min_recoil, self.model.amort.max_recoil

            elif step == 'two':
                min_comp, max_comp = self.model.amort.min_comp_2, self.model.amort.max_comp_2
                min_recoil, max_recoil = self.model.amort.min_recoil_2, self.model.amort.max_recoil_2

            if min_comp < self.model.max_comp < max_comp and min_recoil < self.model.max_recoil < max_recoil:
                self.model.lamp_green_switch_on()
                self.signals.conv_result_lamp.emit(step, 'green')

            else:
                self.model.lamp_red_switch_on()
                self.signals.conv_result_lamp.emit(step, 'red')

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in Steps/step_result_conveyor_test - {e}')
