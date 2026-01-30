from PySide6.QtCore import QObject, Signal

from scripts.logger import my_logger


class StepTestsSignals(QObject):
    stage_from_tests = Signal(str)
    next_stage_from_tests = Signal(str)


class StepTests:
    def __init__(self, model):
        self.logger = my_logger.get_logger(__name__)
        self.model = model
        self.signals = StepTestsSignals()

    # FIXME При втором испытании он сразу падает сюда в else и останавливает испытание
    def step_yellow_btn_push(self):
        try:
            if self.model.flag_test is False:
                if self.model.state_dict.get('green_light') or self.model.state_dict.get('red_light'):
                    self.model.lamp_all_switch_off()

                self.model.clear_data_in_graph()
                self.model.clear_data_in_circle_graph()

                self.model.reset_current_circle()
                self.model.flag_test = True
                self.model.alarm_tag = ''
                self.model.flag_alarm = False

                if self.model.state_dict.get('lost_control'):
                    self.model.write_bit_unblock_control()

                if self.model.state_dict.get('excess_force'):
                    self.model.write_bit_emergency_force()

                return 'start'

            else:
                self.model.flag_test = False
                return 'stop'

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in steps_tests/step_yellow_btn_push - {e}')

    def step_start_test(self):
        try:
            if self.model.state_dict.get('excess_force', False) is True:
                self.model.write_bit_emergency_force()

            if self.model.state_dict.get('lost_control', False) is True:
                self.model.write_bit_unblock_control()

            self.model.lamp_all_switch_off()

            self.model.data_test.max_temperature = 0

            self.model.reset_current_circle()
            self.model.flag_test_launch = True
            self.model.alarm_tag = ''
            self.model.flag_alarm = False

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in steps_tests/step_start_test - {e}')

    def step_stop_test(self):
        try:
            self.signals.stage_from_tests.emit('wait')

            self.model.clear_data_in_graph()

            self.model.reset_current_circle()
            self.model.flag_test_launch = False
            self.model.flag_test = False
            self.model.flag_fill_graph = False

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in steps_tests/step_stop_test - {e}')

    def step_test_on_two_speed(self, ind: int):
        try:
            if ind == 1:
                self.model.fc_control(**{'tag': 'speed', 'adr': 1,
                                         'speed': self.model.data_test.amort.speed_one})
                self.signals.stage_from_tests.emit('test_speed_one')
                self.model.clear_data_in_graph()
                self.model.data_test.speed_test = self.model.data_test.amort.speed_one

                self.model.flag_fill_graph = True

            elif ind == 2:
                self.signals.stage_from_tests.emit('test_speed_two')
                self.model.data_test.speed_test = self.model.data_test.amort.speed_two
                self.model.fc_control(**{'tag': 'speed', 'adr': 1,
                                         'speed': self.model.data_test.amort.speed_two})

            if self.model.flag_repeat:
                self.model.flag_repeat = False
                self.model.fc_control(**{'tag': 'up', 'adr': 1})

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in steps_tests/step_test_on_two_speed - {e}')

    def step_test_lab_hand_speed(self):
        try:
            self.model.fc_control(**{'tag': 'speed', 'adr': 1,
                                     'speed': self.model.data_test.speed_test})
            self.signals.stage_from_tests.emit('test_lab_hand_speed')
            self.model.clear_data_in_graph()
            self.model.flag_fill_graph = True

            if self.model.flag_repeat:
                self.model.flag_repeat = False
                self.model.fc_control(**{'tag': 'up', 'adr': 1})

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in steps_tests/step_test_lab_hand_speed - {e}')

    def step_test_lab_cascade(self, speed_list: list):
        try:
            self.model.fc_control(**{'tag': 'speed', 'adr': 1,
                                     'speed': speed_list[0]})
            self.signals.stage_from_tests.emit('test_lab_cascade')

            self.model.clear_data_in_graph()
            self.model.data_test.speed_test = speed_list[0]
            self.model.flag_fill_graph = True

            if self.model.flag_repeat:
                self.model.flag_repeat = False
                self.model.fc_control(**{'tag': 'up', 'adr': 1})

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in steps_tests/step_test_lab_cascade - {e}')

    def step_test_temper(self):
        try:
            self.model.fc_control(**{'tag': 'speed', 'adr': 1,
                                     'speed': self.model.data_test.speed_test})
            self.signals.stage_from_tests.emit('test_temper')

            self.model.clear_data_in_graph()
            self.model.clear_data_in_temper_graph()
            self.model.flag_fill_graph = True

            if self.model.flag_repeat:
                self.model.flag_repeat = False
                self.model.fc_control(**{'tag': 'up', 'adr': 1})

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in steps_tests/step_test_temper - {e}')
