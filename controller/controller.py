# -*- coding: utf-8 -*-
from PyQt5.QtCore import QTimer, QObject, pyqtSignal

from logger import my_logger
from calc_data.data_calculation import CalcData
from controller.steps_logic import Steps
from controller.alarm_steps import AlarmSteps
from controller.steps_tests import StepTests


class ControlSignals(QObject):
    control_msg = pyqtSignal(str)
    traverse_referent_msg = pyqtSignal()
    wait_yellow_btn = pyqtSignal()
    conv_win_test = pyqtSignal()
    lab_win_test = pyqtSignal()
    lab_test_stop = pyqtSignal()
    lab_save_result = pyqtSignal(str)
    cancel_test = pyqtSignal()
    end_test = pyqtSignal()
    search_hod_msg = pyqtSignal()
    reset_ui = pyqtSignal()


class Controller:
    def __init__(self, model):
        try:
            self.logger = my_logger.get_logger(__name__)
            self.signals = ControlSignals()
            self.model = model
            self.steps = Steps(model)
            self.alarm_steps = AlarmSteps(model)
            self.steps_tests = StepTests(model)
            self.calc_data = CalcData()

            self.stage = 'wait'
            self.next_stage = 'wait'
            self.timer_process = None
            self.flag_alarm_traverse = True
            self.count_cycle = 0
            self.set_trav_point = 0
            self.count_cascade = 1
            self.max_cascade = 0

            self._init_signals()
            self._init_timer_test()

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/__init__ - {e}')

    def _init_signals(self):
        try:
            self.model.signals.full_cycle_count.connect(self._full_cycle_update)
            self.model.signals.test_launch.connect(self._yellow_btn_push)

            self.alarm_steps.signals.stage_from_alarm.connect(self.change_stage_controller)
            self.alarm_steps.signals.alarm_traverse.connect(self._alarm_traverse_position)

            self.steps.signals.stage_from_logic.connect(self.change_stage_controller)
            self.steps.signals.next_stage_from_logic.connect(self.change_next_stage_controller)

            self.steps_tests.signals.stage_from_tests.connect(self.change_stage_controller)
            self.steps_tests.signals.next_stage_from_tests.connect(self.change_next_stage_controller)

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/_init_signals - {e}')

    def _position_traverse(self):
        self.signals.control_msg.emit(f'pos_traverse')

    def _alarm_traverse_position(self, pos):
        self.signals.control_msg.emit(f'alarm_traverse_{pos}')

    def _move_detection(self):
        self.signals.control_msg.emit(f'move_detection')

    def _gear_set_pos(self):
        self.signals.control_msg.emit('gear_set_pos')

    def _pumping_msg(self):
        self.signals.control_msg.emit(f'pumping')

    def change_stage_controller(self, stage: str):
        self.stage = stage

    def change_next_stage_controller(self, stage: str):
        self.next_stage = stage

    def _full_cycle_update(self, command: str):
        try:
            if command == '+1':
                self.count_cycle += 1
            else:
                self.count_cycle = int(command)

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/_full_cycle_update - {e}')

    def _init_timer_test(self):
        try:
            self.timer_process = QTimer()
            self.timer_process.setInterval(100)
            self.timer_process.timeout.connect(self._update_stage_on_timer)
            self.timer_process.start()

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/init_timer - {e}')

    def _update_stage_on_timer(self):
        try:
            self.alarm_steps.step_alarm_traverse_position()

            if self.model.set_regs.get('test_flag', False):
                self._select_alarm_state(self.steps.stage_control_alarm_state())

            if self.stage == 'wait':
                pass

            elif self.stage == 'wait_buffer':
                if self.model.set_regs['buffer_state'][0] == 'OK!':
                    if self.model.set_regs['buffer_state'][1] == 'buffer_on':
                        self.model.set_regs['buffer_state'] = ['null', 'null']
                        self.model.reader_start_test()
                        self.model.motor_up(1)
                        self.stage = self.next_stage

                    elif self.model.set_regs['buffer_state'][1] == 'buffer_off':
                        pass
                        # Ну и в данном случае мы чтото делаем
                elif self.model.set_regs['buffer_state'][0] == 'ERROR!':
                    self.model.set_regs['buffer_state'] = ['null', 'null']
                    self.model.write_bit_force_cycle(1)

            elif self.stage == 'repeat_test':
                self.stage = 'wait'
                type_test = self.model.set_regs.get('type_test')
                if type_test == 'lab_hand':
                    self._test_lab_hand_speed()
                elif type_test == 'temper':
                    self._test_temper()
                elif type_test == 'lab_cascade':
                    self._test_lab_cascade()
                else:
                    self._test_on_two_speed(1)

            elif self.stage == 'alarm_traverse':
                if self.steps.step_control_traverse_move(self.set_trav_point):
                    self.model.motor_stop(2)
                    self.model.write_bit_red_light(0)
                    self.alarm_steps.flag_alarm_traverse = False
                    self.stage = 'wait'
                    command = {'alarm_flag': False,
                               'alarm_tag': '',
                               }
                    self.model.update_main_dict(command)
                    self.signals.reset_ui.emit()

            elif self.stage == 'search_hod':
                if self.steps.stage_search_hod(self.count_cycle):
                    self.stage = 'wait'
                    self.steps.step_stop_gear_min_pos()

            elif self.stage == 'pos_set_gear':
                if self.steps.stage_pos_set_gear():
                    self.stage = 'wait'
                    self.signals.reset_ui.emit()

            elif self.stage == 'traverse_referent':
                if self.steps.stage_traverse_referent():
                    self.stage = 'wait'
                    self.traverse_install_point('install')

            elif self.stage == 'install_amort':
                if self.steps.step_control_traverse_move(self.set_trav_point):
                    self.stage = 'wait'
                    self.signals.wait_yellow_btn.emit()

            elif self.stage == 'start_point_amort':
                if self.steps.step_control_traverse_move(self.set_trav_point):
                    self.next_stage = 'test_move_cycle'
                    self._move_detection()
                    self._full_cycle_update('0')
                    self.steps.step_test_move_cycle()
                    self.stage = 'wait_buffer'

            elif self.stage == 'test_move_cycle':
                if self.count_cycle >= 1:
                    self._pumping_msg()
                    self._full_cycle_update('0')
                    self.steps.step_pumping_before_test()

            elif self.stage == 'pumping':
                if self.count_cycle >= 3:
                    type_test = self.model.set_regs.get('type_test')
                    if type_test == 'lab_hand':
                        self._test_lab_hand_speed()
                    elif type_test == 'temper':
                        self._test_temper()
                    elif type_test == 'lab_cascade':
                        self._test_lab_cascade()
                    else:
                        self._test_on_two_speed(1)

            elif self.stage == 'test_speed_one':
                if self.count_cycle >= 5:
                    type_test = self.model.set_regs.get('type_test')
                    if type_test == 'conv':
                        self.steps.step_result_conveyor_test('one')

                    elif type_test == 'lab':
                        self.signals.lab_save_result.emit('end')

                    self._test_on_two_speed(2)

            elif self.stage == 'test_speed_two':
                if self.count_cycle >= 5:
                    type_test = self.model.set_regs.get('type_test')
                    if type_test == 'conv':
                        self.steps.step_result_conveyor_test('two')

                    elif type_test == 'lab':
                        self.signals.lab_save_result.emit('end')

                    self.stage = 'wait'
                    self.model.set_regs['fill_graph'] = False
                    self.steps.step_stop_gear_end_test()

            elif self.stage == 'test_lab_hand_speed':
                if self.count_cycle >= 5:
                    self.stage = 'wait'
                    self.model.set_regs['fill_graph'] = False
                    self.signals.lab_save_result.emit('end')
                    self.steps.step_stop_gear_end_test()

            elif self.stage == 'test_temper':
                if self.count_cycle >= 1:
                    max_temper = self.model.set_regs.get('max_temperature', None)
                    if max_temper <= self.model.set_regs.get('finish_temper', 80):
                        max_recoil = self.model.set_regs.get('max_recoil', None)
                        max_comp = self.model.set_regs.get('max_comp', None)
                        if max_temper is not None and max_recoil is not None and max_comp is not None:
                            force = f'{max_recoil}|{max_comp}'
                            self.steps_tests.step_fill_temper_graph(max_temper, force)

                        self._full_cycle_update('0')

                    else:
                        self.stage = 'wait'
                        self.model.set_regs['fill_graph'] = False
                        self.signals.lab_save_result.emit('end')
                        self.steps.step_stop_gear_end_test()

            elif self.stage == 'test_lab_cascade':
                if self.count_cycle >= 5:
                    self.signals.lab_save_result.emit('cont')
                    if self.count_cascade < self.max_cascade:
                        speed = self.model.set_regs.get('speed_cascade')[self.count_cascade]
                        self.model.write_speed_motor(1, speed=speed)
                        command = {'speed': speed,
                                   'force_accum_list': [],
                                   'move_accum_list': [],
                                   'fill_graph': True,
                                   }
                        self.model.update_main_dict(command)

                        self.count_cascade += 1

                        self._full_cycle_update('0')

                    else:
                        self.stage = 'wait'
                        self.model.set_regs['fill_graph'] = False
                        self.count_cascade = 1
                        self.signals.end_test.emit()
                        self.steps.step_stop_gear_end_test()

            elif self.stage == 'stop_gear_end_test':
                if self.steps.stage_stop_gear_end_test():
                    self.steps.step_stop_gear_min_pos()

            elif self.stage == 'stop_gear_min_pos':
                if self.steps.stage_stop_gear_min_pos():
                    if self.model.set_regs.get('search_hod', False):
                        self.model.set_regs['search_hod'] = False
                        self.signals.search_hod_msg.emit()

                    else:
                        if self.model.set_regs.get('type_test') == 'conv':
                            if self.model.set_regs.get('test_launch', False) is True:
                                self.traverse_install_point('install')
                            else:
                                self.traverse_install_point('stop_test')

                        else:
                            self.signals.lab_test_stop.emit()

            elif self.stage == 'stop_test':
                flag = self.steps.step_control_traverse_move(self.set_trav_point)
                if flag:
                    self.stage = 'wait'
                    if not self.model.set_regs.get('alarm_flag', False):
                        self.signals.cancel_test.emit()

            else:
                pass

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/_update_stage_on_timer - {e}')

    def _select_alarm_state(self, tag):
        try:
            if tag == 'lost_control':
                self.signals.control_msg.emit('lost_control')
                self.alarm_steps.step_lost_control()

            elif tag == 'excess_force':
                self.signals.control_msg.emit('excess_force')
                self.alarm_steps.step_excess_force()

            elif tag == 'safety_fence':
                self.signals.control_msg.emit('safety_fence')
                self.alarm_steps.step_safety_fence()

            elif tag == 'excess_temperature':
                self.steps.step_stop_gear_end_test()
                self.signals.control_msg.emit('excess_temperature')
                self.alarm_steps.step_excess_temperature()
            else:
                pass

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/_select_alarm_state - {e}')

    def traverse_move_out_alarm(self, pos):
        try:
            if pos == 'up':
                self.set_trav_point = 20
            elif pos == 'down':
                self.set_trav_point = 550

            self.stage = 'alarm_traverse'
            self.steps.step_traverse_move_position(self.set_trav_point)

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/traverse_move_out_alarm - {e}')

    def work_interrupted_operator(self):
        self.stage = 'wait'
        command = {'test_launch': False,
                   'test_flag': False}
        self.model.update_main_dict(command)

        self.model.lamp_all_switch_off()

        if self.model.client.set_dict['connect']:
            self.model.motor_stop(1)
            self.model.motor_stop(2)
            self.model.reader_stop_test()
            self.model.write_bit_force_cycle(0)

    def _yellow_btn_push(self, state: bool):
        """Обработка нажатия жёлтой кнопки, запускает она испытание или останавливает"""
        try:
            if state:
                tag = self.steps_tests.step_yellow_btn_push()
                if tag == 'start':
                    self.traverse_install_point('start_test')

                elif tag == 'stop':
                    self.stop_test_clicked()

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/_yellow_btn_push - {e}')

    def start_test_clicked(self):
        """
        Точка входа в испытание, определение референтной точки траверсы, если известна,
        то сразу запуск позиционирования для установки амортизатора
        """
        try:
            if self._check_max_temper_test():
                self.steps_tests.step_start_test()

                amort = self.model.set_regs.get('amort')
                self.model.write_emergency_force(self.calc_data.excess_force(amort))

                if self.model.set_regs.get('repeat', False):
                    self.stage = 'wait_buffer'
                    self.next_stage = 'repeat_test'
                    self.model.write_bit_force_cycle(1)

                else:
                    if self.model.set_regs.get('traverse_move', 0) < 10:
                        self.signals.traverse_referent_msg.emit()
                        self.steps.step_traverse_referent_point()

                    else:
                        self.traverse_install_point('install')

            else:
                self.steps_tests.step_stop_test()

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/start_test_clicked - {e}')

    def stop_test_clicked(self):
        """
        Завершение теста, если определена референтная точка коленвала, то остановка в нижней точке,
        иначе моментальная остановка
        """
        try:
            self.steps_tests.step_stop_test()

            if self.model.set_regs.get('gear_referent', False):
                self.steps.step_stop_gear_end_test()
            else:
                self.model.motor_stop(1)
                self.model.motor_stop(2)

                self.signals.cancel_test.emit()

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/stop_test_clicked - {e}')

    def search_hod_gear(self):
        try:
            self._move_detection()
            self._full_cycle_update('0')
            self.steps.step_search_hod_gear()

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/search_hod_gear - {e}')

    def move_gear_set_pos(self):
        try:
            self._gear_set_pos()
            self._full_cycle_update('0')
            self.steps.step_move_gear_set_pos()

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/move_gear_set_pos - {e}')

    def traverse_install_point(self, tag):
        """Позционирование траверсы"""
        try:
            amort = self.model.set_regs.get('amort')
            stock_point = self.model.set_regs.get('traverse_stock', 756)
            hod = amort.hod
            len_min = amort.min_length
            len_max = amort.max_length
            mid_point = (len_max - len_min) / 2
            adapter = amort.adapter_len

            if tag == 'install':
                install_point = int((stock_point + hod / 2) - len_max - adapter + 1)
                self._position_traverse()
                pos_trav = float(self.model.set_regs.get('traverse_move'))
                if abs(pos_trav - install_point) < 1:
                    self.signals.wait_yellow_btn.emit()

                else:
                    self.stage = 'install_amort'
                    self.set_trav_point = install_point
                    self.steps.step_traverse_move_position(install_point)

            elif tag == 'start_test':
                start_point = int(stock_point - len_max - adapter + mid_point)
                self._position_traverse()
                self.stage = 'start_point_amort'
                self.set_trav_point = start_point
                self.steps.step_traverse_move_position(start_point)

            elif tag == 'stop_test':
                if not self.model.set_regs.get('alarm_flag', False):
                    self._position_traverse()

                end_point = int((stock_point + hod / 2) - len_max - adapter + 1)

                self.stage = 'stop_test'
                self.set_trav_point = end_point
                self.steps.step_traverse_move_position(end_point)

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/traverse_install_point - {e}')

    def _test_on_two_speed(self, ind):
        try:
            type_test = self.model.set_regs.get('type_test')
            if type_test == 'conv':
                self.signals.conv_win_test.emit()
            elif type_test == 'lab':
                self.signals.lab_win_test.emit()

            self.steps_tests.step_test_on_two_speed(ind)
            self._full_cycle_update('0')

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/_test_on_two_speed - {e}')

    def _test_lab_hand_speed(self):
        try:
            self.signals.lab_win_test.emit()
            self.steps_tests.step_test_lab_hand_speed()
            self._full_cycle_update('0')

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/_test_lab_hand_speed - {e}')

    def _check_max_temper_test(self):
        if self.model.set_regs.get('type_test', 'hand') == 'temper':
            temp_f = self.model.set_regs.get('temper_first', 0)
            temp_s = self.model.set_regs.get('temper_second', 0)
            temp_b = self.model.set_regs.get('temperature', 0)
            finish_temp = self.model.set_regs.get('finish_temper', 80)
            if temp_f < finish_temp and temp_s < finish_temp and temp_b < finish_temp:
                return True

            else:
                self.signals.control_msg.emit('excess_temperature')
                return False

    def _test_temper(self):
        try:
            self.signals.lab_win_test.emit()
            self.steps_tests.step_test_temper()
            self._full_cycle_update('0')

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/_test_temper - {e}')

    def _test_lab_cascade(self):
        try:
            self.signals.lab_win_test.emit()
            speed_list = self.model.set_regs.get('speed_cascade')
            self.count_cascade = 1
            self.max_cascade = len(speed_list)

            self.steps_tests.step_test_lab_cascade(speed_list)
            self._full_cycle_update('0')

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/_test_lab_cascade - {e}')
