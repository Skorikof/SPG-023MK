import statistics
from PySide6.QtCore import QObject, Signal

from scripts.logger import my_logger


class StepsSignal(QObject):
    stage_from_logic = Signal(str)
    next_stage_from_logic = Signal(str)
    conv_result_lamp = Signal(str, str)


class Steps:
    # Speed configuration: {hod_range: {speed_tag: speed_value}}
    SPEED_CONFIG = {
        (100, float('inf')): {'slow': 0.03, 'medium': 0.1, 'fast': 0.2},
        (50, 100): {'slow': 0.02, 'medium': 0.06, 'fast': 0.1},
        (0, 50): {'slow': 0.01, 'medium': 0.03, 'fast': 0.03},
    }

    def __init__(self, model):
        self.logger = my_logger.get_logger(__name__)
        self.model = model
        self.signals = StepsSignal()

        self.flag_freq_1_step = False
        self.flag_freq_2_step = False
        self.count_wait_point = 0

    def stage_control_alarm_state(self):
        """Check for alarm conditions and return alarm tag or None."""
        try:
            alarm_checks = [
                ('lost_control', self.model.reg_data.state.lost_control),
                ('excess_force', self.model.reg_data.state.excess_force),
                ('safety_fence', self.model.reg_data.state.safety_fence),
            ]
            
            for alarm_tag, is_triggered in alarm_checks:
                if is_triggered:
                    return alarm_tag
            
            if self.model.data_test.type_test != 'temper':
                if self.model.data_test.max_temperature >= self.model.data_test.amort.max_temper:
                    return 'excess_temperature'
            
            return None

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in Steps/stage_control_alarm_state - {e}')
            
    def _definition_speed_by_hod(self, tag: str) -> float:
        """Get speed based on hod value and speed tag."""
        try:
            # Get hod value (default 120 if None)
            hod = self.model.data_test.amort.hod if self.model.data_test.amort else 120
            
            # Find matching range and get speed
            for (min_hod, max_hod), speeds in self.SPEED_CONFIG.items():
                if min_hod < hod <= max_hod:
                    return speeds.get(tag, 0.03)
            
            return 0.03  # Safe default

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in Steps/_definition_speed_by_hod - {e}')
            return 0.03  # Safe default on error

    def step_search_hod_gear(self):
        try:
            self.signals.stage_from_logic.emit('wait')
            self.signals.next_stage_from_logic.emit('search_hod')

            self.model.reset_current_circle()
            self.model.alarm_tag = ''
            self.model.flag_alarm = False
            self.model.flag_search_hod = True

            speed = self._definition_speed_by_hod('medium')
            self.model.fc_control(**{'tag': 'speed', 'adr': 1, 'speed': speed})
            self.signals.stage_from_logic.emit('wait_buffer')
            self.model.write_bit_force_cycle(1)

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in Steps/step_search_hod_gear - {e}')

    def stage_search_hod(self, count_cycle):
        try:
            if count_cycle >= 1:
                self.model.hod_measure = round(abs(self.model.min_point) + abs(self.model.max_point), 1)
                return True

            else:
                return False

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in Steps/stage_search_hod - {e}')

    def step_move_gear_set_pos(self):
        try:
            self.signals.stage_from_logic.emit('wait')
            self.signals.next_stage_from_logic.emit('pos_set_gear')

            self.model.reset_current_circle()
            self.model.alarm_tag = ''
            self.model.flag_alarm = False

            speed = self._definition_speed_by_hod('slow')
            self.model.fc_control(**{'tag': 'speed', 'adr': 1, 'speed': speed})
            self.signals.stage_from_logic.emit('wait_buffer')
            self.model.write_bit_force_cycle(1)

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in Steps/step_move_gear_set_pos - {e}')

    def stage_pos_set_gear(self):
        try:
            if self.model.gear_referent:
                if self.model.max_pos:
                    if abs(14 - self.model.reg_data.pos) < 5:
                        self.model.fc_control(**{'tag': 'stop', 'adr': 1})
                        self.model.reader_stop_test()
                        # self.model.flag_bufer = False
                        # self.model.clear_data_in_graph()
                        # self.model.timer_pars_circle_stop()
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
            self.model.fc_control(**{'tag': 'stop', 'adr': 1})

            self.signals.stage_from_logic.emit('stop_gear_end_test')

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in Steps/step_stop_gear_end_test - {e}')

    def stage_stop_gear_end_test(self):
        try:
            # if abs(self.model.move_list[-1] - self.model.move_list[-10]) < 0.1:
            if statistics.stdev(self.model.move_buf) < 0.1: # Перемещение перестало изменятьсяs
                self.count_wait_point += 1

            else:
                self.count_wait_point = 0

            if self.count_wait_point > 20:
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
            # self.model.flag_bufer = False
            # self.model.clear_data_in_graph()
            # self.model.timer_pars_circle_stop()

            self.model.write_bit_force_cycle(0)

            speed = self._definition_speed_by_hod('slow')
            self.model.fc_control(**{'tag': 'speed', 'adr': 1, 'speed': speed})
            self.model.fc_control(**{'tag': 'up', 'adr': 1})

            self.signals.stage_from_logic.emit('stop_gear_min_pos')

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in Steps/step_stop_gear_min_pos - {e}')

    def stage_stop_gear_min_pos(self):
        try:
            if self.model.reg_data.pos < self.model.min_point + 1:
                self.model.fc_control(**{'tag': 'stop', 'adr': 1})

                self.signals.stage_from_logic.emit('wait')

                self.model.clear_data_in_graph()

                self.model.reset_current_circle()
                
                if self.model.flag_test:
                    self.model.flag_test = False

                return True

            return False

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in Steps/stage_stop_gear_min_pos - {e}')

    def step_test_move_cycle(self):
        """Проверочный ход"""
        try:
            speed = self._definition_speed_by_hod('medium')
            self.model.fc_control(**{'tag': 'speed', 'adr': 1, 'speed': speed})
            self.model.write_bit_force_cycle(1)

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in Steps/step_test_move_cycle - {e}')

    def step_pumping_before_test(self):
        """Прокачка на скорости 0.2 3 оборота перед запуском теста"""
        try:
            speed = self._definition_speed_by_hod('fast')
            self.model.fc_control(**{'tag': 'speed', 'adr': 1, 'speed': speed})

            self.signals.stage_from_logic.emit('pumping')

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in Steps/step_pumping_before_test - {e}')

    def step_traverse_referent_point(self):
        """Подъём траверсы до концевика для определения референтной точки"""
        try:
            self.model.fc_control(**{'tag':'speed', 'adr':2, 'freq':30})
            self.signals.stage_from_logic.emit('traverse_referent')
            self.model.fc_control(**{'tag': 'up', 'adr': 2})

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in Steps/step_traverse_referent_point - {e}')

    def stage_traverse_referent(self):
        try:
            if self.model.reg_data.state.referent is True:
                self.model.fc_control(**{'tag': 'stop', 'adr': 2})

                self.model.traverse_referent = True
                self.model.init_timer_koef_force()

                return True
            return False

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in Steps/stage_traverse_referent - {e}')

    def step_move_traverse_out_alarm(self, pos):
        try:
            tag = 'down'
            self.flag_freq_1_step = False
            self.flag_freq_2_step = False
            self.model.fc_control(**{'tag': 'speed', 'adr': 2, 'freq': 30})
            if pos == 'up':
                tag = 'down'
            elif pos == 'down':
                tag = 'up'
            self.model.fc_control(**{'tag': tag, 'adr': 2})

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in steps/step_move_traverse_out_alarm - {e}')

    def step_traverse_move_position(self, set_point):
        """Непосредственно включение и перемещение траверсы"""
        try:
            val = abs(set_point - self.model.move_traverse)
            if val > 0.3:
                if val <= 10:
                    freq = 5
                elif 10 < val < 20:
                    freq = 15
                else:
                    freq = 30
                    
                self.flag_freq_1_step = False
                self.flag_freq_2_step = False
                self.model.fc_control(**{'tag': 'speed', 'adr': 2, 'freq': freq})
                pos_trav = self.model.move_traverse

                if pos_trav > set_point:
                    tag = 'up'
                else:
                    tag = 'down'
                self.model.fc_control(**{'tag': tag, 'adr': 2})

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in steps/step_traverse_move_position - {e}')

    def step_control_traverse_move(self, point) -> bool:  # Функция отслеживания траверсы, при достижении точки останов
        try:
            if 8 < abs(point - self.model.move_traverse) <= 15:
                if not self.flag_freq_1_step:
                    self.model.fc_control(**{'tag': 'speed', 'adr': 2, 'freq': 15})
                    self.flag_freq_1_step = True

            if 2 < abs(point - self.model.move_traverse) <= 8:
                if not self.flag_freq_2_step:
                    self.model.fc_control(**{'tag': 'speed', 'adr': 2, 'freq': 5})
                    self.flag_freq_2_step = True

            if abs(point - self.model.move_traverse) <= 0.3:
                self.model.fc_control(**{'tag': 'stop', 'adr': 2})
                # print(f'Остановился -- {self.model.move_traverse}')
                return True

            return False

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in steps/control_traverse_move - {e}')

    def step_result_conveyor_test(self, step):
        """Включение индикаторов, зелёный - в допусках, красный - нет"""
        try:
            amort = self.model.data_test.amort
            min_comp, max_comp = 0, 2000
            min_recoil, max_recoil = 0, 2000

            if step == 'one':
                min_comp, max_comp = amort.min_comp, amort.max_comp
                min_recoil, max_recoil = amort.min_recoil, amort.max_recoil

            elif step == 'two':
                min_comp, max_comp = amort.min_comp_2, amort.max_comp_2
                min_recoil, max_recoil = amort.min_recoil_2, amort.max_recoil_2

            if min_comp < self.model.max_comp < max_comp and min_recoil < self.model.max_recoil < max_recoil:
                self.model.lamp_green_switch_on()
                self.signals.conv_result_lamp.emit(step, 'green')

            else:
                self.model.lamp_red_switch_on()
                self.signals.conv_result_lamp.emit(step, 'red')

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in Steps/step_result_conveyor_test - {e}')
