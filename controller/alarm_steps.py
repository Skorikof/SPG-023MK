from PyQt5.QtCore import QObject, pyqtSignal

from logger import my_logger


class AlarmSignals(QObject):
    stage_from_alarm = pyqtSignal(str)
    alarm_traverse = pyqtSignal(str)


class AlarmSteps:
    def __init__(self, model):
        self.logger = my_logger.get_logger(__name__)
        self.model = model
        self.signals = AlarmSignals()

        self.flag_alarm_traverse = False

        # self.time_start_wait = None
        # self.time_all_wait = None
        # self.time_tag_wait = None
        # self.time_lost_control = time.monotonic()
        # self.flag_lost_control = False
        # self.time_excess_force = time.monotonic()
        # self.flag_excess_force = False
        # self.time_safety_fence = time.monotonic()
        # self.flag_safety_fence = False

    def step_lost_control(self):
        try:
            self.signals.stage_from_alarm.emit('wait')
            command = {'alarm_flag': True,
                       'alarm_tag': 'lost_control',
                       'test_launch': False,
                       'test_flag': False}
            self.model.update_main_dict(command)

            self.model.reader_stop_test()

            self.model.write_bit_red_light(1)

            self.model.write_bit_force_cycle(0)

            self.logger.warning(f'lost control')
            self.model.status_bar_msg(f'lost control')
            # self.flag_lost_control = False

            # time_signal = time.monotonic()
            # if self.flag_lost_control is False:
            #     self.time_lost_control = time.monotonic()
            #     self.flag_lost_control = True
            #
            # elif 0.3 < abs(self.time_lost_control - time_signal) < 0.5:
            #     self.model.motor_stop(1)
            #     self.model.motor_stop(2)
            #
            #     # self.signals.stage_from_alarm.emit('wait')
            #     # self.model.set_regs['alarm_flag'] = True
            #     # self.model.set_regs['test_launch'] = False
            #     # self.model.set_regs['test_flag'] = False
            #
            #     command = {'alarm_flag': True,
            #                'test_launch': False,
            #                'test_flag': False}
            #     self.model.update_main_dict(command)
            #
            #     self.model.log_error(f'lost control')
            #     self.signals.control_msg.emit('lost_control')
            #     self.flag_lost_control = False
            #
            # elif abs(self.time_lost_control - time_signal) > 0.5:
            #     self.flag_lost_control = False

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in alarm_steps/step_lost_control - {e}')

    def step_excess_force(self):
        try:
            self.signals.stage_from_alarm.emit('wait')
            command = {'alarm_flag': True,
                       'alarm_tag': 'excess_force',
                       'test_launch': False,
                       'test_flag': False}
            self.model.update_main_dict(command)

            self.model.reader_stop_test()

            self.model.write_bit_red_light(1)

            self.model.write_bit_force_cycle(0)

            self.logger.warning(f'excess force')
            self.model.status_bar_msg(f'excess force')
            # self.flag_excess_force = False

            # time_signal = time.monotonic()
            # if self.flag_excess_force is False:
            #     self.time_excess_force = time.monotonic()
            #     self.flag_excess_force = True
            #
            # elif 0.3 < abs(self.time_excess_force - time_signal) < 0.5:
            #     self.model.motor_stop(1)
            #     self.model.motor_stop(2)
            #
            #     # self.model.set_regs['alarm_flag'] = True
            #     # self.model.set_regs['test_launch'] = False
            #     # self.model.set_regs['test_flag'] = False
            #
            #     self.signals.stage_from_alarm.emit('wait')
            #     command = {'alarm_flag': True,
            #                'test_launch': False,
            #                'test_flag': False}
            #     self.model.update_main_dict(command)
            #
            #     self.model.log_error(f'excess force')
            #     self.signals.control_msg.emit('excess_force')
            #     self.flag_excess_force = False
            #
            # elif abs(self.time_excess_force - time_signal) > 0.5:
            #     self.flag_excess_force = False

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in alarm_steps/step_excess_force - {e}')

    def step_excess_temperature(self):
        try:
            self.model.write_bit_red_light(1)

            command = {'alarm_flag': True,
                       'alarm_tag': 'excess_temperature',
                       'test_launch': False,
                       }
            self.model.update_main_dict(command)

            self.logger.warning(f'excess temperature')
            self.model.status_bar_msg(f'excess temperature')

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in alarm_steps/step_excess_temperature - {e}')

    def step_safety_fence(self):
        try:
            command = {'alarm_flag': True,
                       'alarm_tag': 'safety_fence',
                       'test_launch': False,
                       'test_flag': False,
                       }
            self.model.update_main_dict(command)

            self.model.motor_stop(1)
            self.model.motor_stop(2)
            self.model.write_bit_red_light(1)

            self.model.reader_stop_test()

            self.logger.warning(f'safety fence')
            self.model.status_bar_msg(f'safety fence')

            self.model.write_bit_force_cycle(0)

            # if self.flag_safety_fence is False:
            #     self.time_safety_fence = time.monotonic()
            #     self.flag_safety_fence = True
            #
            # # elif 0.1 < abs(self.time_safety_fence - time.monotonic()) < 1:
            # else:
            #
            #     command = {'alarm_flag': True,
            #                'test_launch': False}
            #     self.model.update_main_dict(command)
            #
            #     self._stop_gear_min_pos()
            #
            #     self.model.log_error(f'safety fence')
            #     self.signals.control_msg.emit('safety_fence')
            #     self.flag_safety_fence = False
            #
            # if abs(self.time_excess_force - time.monotonic()) > 2:
            #     self.flag_safety_fence = False

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in alarm_steps/step_safety_fence - {e}')

    def step_alarm_traverse_position(self):
        try:
            tag = 'null'
            if not self.model.set_regs.get('alarm_highest_position', False):
                tag = 'up'
            if not self.model.set_regs.get('alarm_lowest_position', False):
                tag = 'down'

            if tag != 'null':
                if not self.flag_alarm_traverse:
                    self.flag_alarm_traverse = True
                    self.model.write_bit_red_light(1)

                    command = {'alarm_flag': True,
                               'alarm_tag': f'alarm_traverse_{tag}',
                               'test_launch': False,
                               'test_flag': False}
                    self.model.update_main_dict(command)

                    self.model.reader_stop_test()

                    self.model.write_bit_force_cycle(0)

                    self.signals.alarm_traverse.emit(tag)

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in alarm_steps/step_alarm_traverse_position - {e}')
