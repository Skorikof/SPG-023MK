from functools import reduce

from logger import my_logger


class Steps:
    def __init__(self, model):
        self.logger = my_logger.get_logger(__name__)
        self.model = model

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

    def stage_search_hod(self, count_cycle):
        try:
            if count_cycle >= 1:
                self.model.motor_stop(1)
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

    def stage_stop_gear_end_test(self):
        try:
            move_list = self.model.set_regs.get('move_list')
            stop_point = reduce(lambda x, y: round(abs(abs(x) - abs(y)), 3), move_list)

            if stop_point < 0.2 or stop_point == move_list[0]:  # Перемещение перестало изменяться
                self.count_wait_point += 1

            else:
                self.count_wait_point = 0

            if self.count_wait_point > 3:
                self.count_wait_point = 0
                self.model.set_regs['stage'] = 'wait'
                return True
            return False

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in steps/stop_gear_end_test - {e}')

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
            self.model.write_speed_motor(2, freq=10)
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
            self.model.write_speed_motor(2, freq=20)
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
                    self.model.write_speed_motor(2, freq=15)
                    self.flag_freq_1_step = True

            if 1 < abs(point - float(self.model.set_regs.get('traverse_move'))) <= 5:
                if not self.flag_freq_2_step:
                    self.model.write_speed_motor(2, freq=10)
                    self.flag_freq_2_step = True

            if abs(point - self.model.set_regs.get('traverse_move')) <= 1:
                self.model.motor_stop(2)
                return True

            return False

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in steps/control_traverse_move - {e}')
