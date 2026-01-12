from PySide6.QtCore import QObject, Signal

from scripts.logger import my_logger


class AlarmSignals(QObject):
    stage_from_alarm = Signal(str)
    alarm_traverse = Signal(str)


class AlarmSteps:
    def __init__(self, model):
        self.logger = my_logger.get_logger(__name__)
        self.model = model
        self.signals = AlarmSignals()

        self.flag_alarm_traverse = False

    def step_lost_control(self):
        try:
            self.signals.stage_from_alarm.emit('wait')
            self.model.flag_test_launch = False
            self.model.flag_test = False
            self.model.alarm_tag = 'lost_control'
            self.model.flag_alarm = True

            self.model.reader_stop_test()

            self.model.write_bit_red_light(1)

            self.model.write_bit_force_cycle(0)

            self.logger.warning(f'lost control')
            self.model.status_bar_msg(f'lost control')

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in alarm_steps/step_lost_control - {e}')

    def step_excess_force(self):
        try:
            self.signals.stage_from_alarm.emit('wait')
            self.model.flag_test_launch = False
            self.model.flag_test = False
            self.model.alarm_tag = 'excess_force'
            self.model.flag_alarm = True

            self.model.reader_stop_test()

            self.model.write_bit_red_light(1)

            self.model.write_bit_force_cycle(0)

            self.logger.warning(f'excess force')
            self.model.status_bar_msg(f'excess force')

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in alarm_steps/step_excess_force - {e}')

    def step_excess_temperature(self):
        try:
            self.model.write_bit_red_light(1)
            self.model.flag_test_launch = False
            self.model.alarm_tag = 'excess_temperature'
            self.model.flag_alarm = True

            self.logger.warning(f'excess temperature')
            self.model.status_bar_msg(f'excess temperature')

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in alarm_steps/step_excess_temperature - {e}')

    def step_safety_fence(self):
        try:
            self.model.flag_test_launch = False
            self.model.flag_test = False
            self.model.alarm_tag = 'safety_fence'
            self.model.flag_alarm = True

            self.model.fc_control(**{'tag': 'stop', 'adr': 1})
            self.model.fc_control(**{'tag': 'stop', 'adr': 2})
            
            self.model.write_bit_red_light(1)

            self.model.reader_stop_test()

            self.logger.warning(f'safety fence')
            self.model.status_bar_msg(f'safety fence')

            self.model.write_bit_force_cycle(0)

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in alarm_steps/step_safety_fence - {e}')

    def step_alarm_traverse_position(self):
        try:
            tag = 'null'
            if not self.model.switch_dict.get('alarm_highest_position', False):
                tag = 'up'
            if not self.model.switch_dict.get('alarm_lowest_position', False):
                tag = 'down'

            if tag != 'null':
                if not self.flag_alarm_traverse:
                    self.flag_alarm_traverse = True
                    self.model.write_bit_red_light(1)
                    self.model.flag_test_launch = False
                    self.model.flag_test = False
                    self.model.alarm_tag = f'alarm_traverse_{tag}'
                    self.model.flag_alarm = True

                    self.model.reader_stop_test()

                    self.model.write_bit_force_cycle(0)

                    self.signals.alarm_traverse.emit(tag)

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in alarm_steps/step_alarm_traverse_position - {e}')
