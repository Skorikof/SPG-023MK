from PyQt5.QtCore import QObject, pyqtSignal

from logger import my_logger


class StepTestsSignals(QObject):
    stage_from_tests = pyqtSignal(str)
    next_stage_from_tests = pyqtSignal(str)


class StepTests:
    def __init__(self, model):
        self.logger = my_logger.get_logger(__name__)
        self.model = model
        self.signals = StepTestsSignals()

        self.temper_graph = []
        self.temper_force_graph = []

    # FIXME При втором испытании он сразу падает сюда в else и останавливает испытание
    def step_yellow_btn_push(self):
        try:
            if self.model.set_regs.get('test_flag', False) is False:
                if self.model.set_regs.get('green_light') or self.model.set_regs.get('red_light'):
                    self.model.lamp_all_switch_off()

                command = {'alarm_flag': False,
                           'alarm_tag': '',
                           'test_flag': True,
                           'force_accum_list': [],
                           'move_accum_list': [],
                           'force_graph': [],
                           'move_real_list': [],
                           'min_pos': False,
                           'max_pos': False,
                           'start_direction': False}
                self.model.update_main_dict(command)
                self.model.reset_min_point()

                if self.model.set_regs.get('lost_control'):
                    self.model.write_bit_unblock_control()

                if self.model.set_regs.get('excess_force'):
                    self.model.write_bit_emergency_force()

                return 'start'

            else:
                self.model.set_regs['test_flag'] = False
                return 'stop'

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in steps_tests/step_yellow_btn_push - {e}')

    def step_start_test(self):
        try:
            if self.model.set_regs.get('excess_force', False) is True:
                self.model.write_bit_emergency_force()

            if self.model.set_regs.get('lost_control', False) is True:
                self.model.write_bit_unblock_control()

            self.model.lamp_all_switch_off()

            command = {'test_launch': True,
                       'alarm_flag': False,
                       'alarm_tag': '',
                       # 'force_accum_list': [],
                       # 'move_accum_list': [],
                       # 'force_graph': [],
                       # 'move_real_list': [],
                       'max_temperature': 0,
                       'start_direction': False,
                       'min_pos': False,
                       'max_pos': False,
                       }

            self.model.update_main_dict(command)
            self.model.reset_min_point()

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in steps_tests/step_start_test - {e}')

    # def step_repeat_test(self):
    #     try:
    #         if self.model.set_regs.get('excess_force', False) is True:
    #             self.model.write_bit_emergency_force()
    #
    #         if self.model.set_regs.get('lost_control', False) is True:
    #             self.model.write_bit_unblock_control()
    #
    #         self.model.lamp_all_switch_off()
    #
    #         command = {'test_launch': True,
    #                    'alarm_flag': False,
    #                    'alarm_tag': '',
    #                    'force_accum_list': [],
    #                    'move_accum_list': [],
    #                    'force_graph': [],
    #                    'move_real_list': [],
    #                    'max_temperature': 0,
    #                    'start_direction': False,
    #                    'min_pos': False,
    #                    'max_pos': False,
    #                    'repeat': True,
    #                    }
    #
    #         self.model.update_main_dict(command)
    #         self.model.reset_min_point()
    #
    #         self.signals.stage_from_tests.emit('wait_buffer')
    #         self.signals.next_stage_from_tests.emit('repeat_test')
    #         self.model.write_bit_force_cycle(1)
    #
    #     except Exception as e:
    #         self.logger.error(e)
    #         self.model.status_bar_msg(f'ERROR in steps_tests/step_repeat_test - {e}')

    def step_stop_test(self):
        try:
            self.signals.stage_from_tests.emit('wait')
            command = {'test_launch': False,
                       'fill_graph': False,
                       'test_flag': False,
                       'force_accum_list': [],
                       'move_accum_list': [],
                       'start_direction': False,
                       'min_pos': False,
                       'max_pos': False,
                       }

            self.model.update_main_dict(command)

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in steps_tests/step_stop_test - {e}')

    def step_test_on_two_speed(self, ind: int):
        try:
            if ind == 1:
                speed_one = self.model.set_regs.get('amort').speed_one
                self.model.write_speed_motor(1, speed=speed_one)
                self.signals.stage_from_tests.emit('test_speed_one')
                command = {'speed': speed_one,
                           'force_accum_list': [],
                           'move_accum_list': [],
                           'fill_graph': True,
                           }
                self.model.update_main_dict(command)

            elif ind == 2:
                speed_two = self.model.set_regs.get('amort').speed_two
                self.signals.stage_from_tests.emit('test_speed_two')
                self.model.set_regs['speed'] = speed_two

                self.model.write_speed_motor(1, speed=speed_two)

            if self.model.set_regs.get('repeat', False):
                self.model.set_regs['repeat'] = False
                self.model.motor_up(1)

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in steps_tests/step_test_on_two_speed - {e}')

    def step_test_lab_hand_speed(self):
        try:
            speed = self.model.set_regs.get('speed')
            self.model.write_speed_motor(1, speed=speed)
            self.signals.stage_from_tests.emit('test_lab_hand_speed')
            command = {'force_accum_list': [],
                       'move_accum_list': [],
                       'fill_graph': True,
                       }
            self.model.update_main_dict(command)

            if self.model.set_regs.get('repeat', False):
                self.model.set_regs['repeat'] = False
                self.model.motor_up(1)

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in steps_tests/step_test_lab_hand_speed - {e}')

    def step_test_lab_cascade(self, speed_list: list):
        try:
            self.model.write_speed_motor(1, speed=speed_list[0])
            self.signals.stage_from_tests.emit('test_lab_cascade')
            command = {'speed': speed_list[0],
                       'force_accum_list': [],
                       'move_accum_list': [],
                       'fill_graph': True,
                       }
            self.model.update_main_dict(command)

            if self.model.set_regs.get('repeat', False):
                self.model.set_regs['repeat'] = False
                self.model.motor_up(1)

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in steps_tests/step_test_lab_cascade - {e}')

    def step_test_temper(self):
        try:
            speed = self.model.set_regs.get('speed')
            self.model.write_speed_motor(1, speed=speed)
            self.signals.stage_from_tests.emit('test_temper')
            self.temper_graph = []
            self.temper_force_graph = []

            command = {'force_accum_list': [],
                       'move_accum_list': [],
                       'temper_graph': [],
                       'temper_force_graph': [],
                       'fill_graph': True,
                       }
            self.model.update_main_dict(command)

            if self.model.set_regs.get('repeat', False):
                self.model.set_regs['repeat'] = False
                self.model.motor_up(1)

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in steps_tests/step_test_temper - {e}')

    def step_fill_temper_graph(self, temper, force):
        try:
            self.temper_graph.append(temper)
            self.temper_force_graph.append(force)

            self.model.set_regs['temper_graph'] = self.temper_graph[:]
            self.model.set_regs['temper_force_graph'] = self.temper_force_graph[:]

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in steps_tests/step_fill_temper_graph - {e}')

