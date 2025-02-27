from functools import reduce
from PyQt5.QtCore import pyqtSignal, QObject

from logger import my_logger


class StepsSignal(QObject):
    stage_from_logic = pyqtSignal(str)
    next_stage_from_logic = pyqtSignal(str)


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
                if self.model.set_regs.get('max_temperature', 0) >= self.model.set_regs.get('amort').max_temper:
                    tag = 'excess_temperature'

            if self.model.set_regs.get('lost_control', False) is True:
                tag = 'lost_control'
            if self.model.set_regs.get('excess_force', False) is True:
                tag = 'excess_force'
            if self.model.set_regs.get('safety_fence', False) is True:
                tag = 'safety_fence'

            return tag

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in Steps/stage_control_alarm_state - {e}')

    def step_search_hod_gear(self):
        try:
            hod = self.model.set_regs.get('hod', 120)
            if hod > 100:
                speed = 0.1
            elif 50 < hod <= 100:
                speed = 0.06
            else:
                speed = 0.03

            self.signals.stage_from_logic.emit('wait')
            self.signals.next_stage_from_logic.emit('search_hod')
            command = {'search_hod': True,
                       'alarm_flag': False,
                       'alarm_tag': '',
                       'start_direction': False,
                       'min_pos': False,
                       'max_pos': False,
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
                min_point = self.model.set_regs.get('min_point', 0)
                max_point = self.model.set_regs.get('max_point', 0)
                hod = round(abs(min_point) + abs(max_point), 1)

                self.model.set_regs['hod_measure'] = hod

                return True

            else:
                return False

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in Steps/stage_search_hod - {e}')

    def step_move_gear_set_pos(self):
        try:
            hod = self.model.set_regs.get('hod', 120)
            if hod > 100:
                speed = 0.03
            elif 50 < hod <= 100:
                speed = 0.02
            else:
                speed = 0.01

            self.signals.stage_from_logic.emit('wait')
            self.signals.next_stage_from_logic.emit('pos_set_gear')
            command = {'alarm_flag': False,
                       'alarm_tag': '',
                       'start_direction': False,
                       'min_pos': False,
                       'max_pos': False,
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
            if self.model.set_regs.get('gear_referent', False):
                if self.model.set_regs.get('max_pos', False):
                    if abs(14 - self.model.set_regs.get('move', 200)) < 5:
                        self.model.motor_stop(1)
                        self.model.reader_stop_test()
                        self.model.write_bit_force_cycle(0)
                        self.model.set_regs['max_pos'] = False

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
            move_list = self.model.set_regs.get('move_list')
            stop_point = reduce(lambda x, y: round(abs(abs(x) - abs(y)), 3), move_list)

            if stop_point < 0.2 or stop_point == abs(move_list[0]):  # Перемещение перестало изменяться
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

            hod = self.model.set_regs.get('hod', 120)
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
            if self.model.set_regs.get('move') < self.model.main_min_point + 2:
                self.model.motor_stop(1)

                self.signals.stage_from_logic.emit('wait')
                command = {'force_accum_list': [],
                           'move_accum_list': [],
                           'start_direction': False,
                           'min_pos': False,
                           'max_pos': False,
                           'test_flag': False,
                           }

                self.model.update_main_dict(command)

                return True

            return False

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in Steps/stage_stop_gear_min_pos - {e}')

    def step_test_move_cycle(self):
        """Проверочный ход"""
        try:
            hod = self.model.set_regs.get('hod', 120)
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
            hod = self.model.set_regs.get('hod', 120)
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
            if self.model.set_regs.get('highest_position', False) is True:
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
            pos_trav = self.model.set_regs.get('traverse_move')

            if pos_trav > set_point:
                self.model.motor_up(2)
            else:
                self.model.motor_down(2)

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in steps/step_traverse_move_position - {e}')

    def step_control_traverse_move(self, point) -> bool:  # Функция отслеживания траверсы, при достижении точки останов
        try:
            if 5 < abs(point - self.model.set_regs.get('traverse_move')) <= 10:
                if not self.flag_freq_1_step:
                    self.model.write_speed_motor(2, freq=20)
                    self.flag_freq_1_step = True

            if 1 < abs(point - float(self.model.set_regs.get('traverse_move'))) <= 5:
                if not self.flag_freq_2_step:
                    self.model.write_speed_motor(2, freq=15)
                    self.flag_freq_2_step = True

            if abs(point - self.model.set_regs.get('traverse_move')) <= 0.5:
                self.model.motor_stop(2)
                return True

            return False

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in steps/control_traverse_move - {e}')

    def step_result_conveyor_test(self, step):
        """Включение индикаторов, зелёный - в допусках, красный - нет"""
        try:
            comp = self.model.set_regs.get('max_comp', 0)
            recoil = self.model.set_regs.get('max_recoil', 0)
            amort = self.model.set_regs.get('amort')
            min_comp, max_comp = 0, 2000
            min_recoil, max_recoil = 0, 2000

            if step == 'one':
                min_comp, max_comp = amort.min_comp, amort.max_comp
                min_recoil, max_recoil = amort.min_recoil, amort.max_recoil

            elif step == 'two':
                min_comp, max_comp = amort.min_comp_2, amort.max_comp_2
                min_recoil, max_recoil = amort.min_recoil_2, amort.max_recoil_2

            if min_comp < comp < max_comp and min_recoil < recoil < max_recoil:
                self.model.lamp_green_switch_on()

            else:
                self.model.lamp_red_switch_on()

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in Steps/step_result_conveyor_test - {e}')
