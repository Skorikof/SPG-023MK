# -*- coding: utf-8 -*-
from PySide6.QtCore import QTimer, QObject, Signal

from scripts.logger import my_logger
from scripts.data_calculation import CalcData
from scripts.controller.steps_logic import Steps
from scripts.controller.alarm_steps import AlarmSteps
from scripts.controller.steps_tests import StepTests


class ControlSignals(QObject):
    control_msg = Signal(str)
    conv_win_test = Signal()
    lab_win_test = Signal()
    lab_test_stop = Signal()
    conv_test_stop = Signal()
    cancel_test = Signal()
    search_hod_msg = Signal()
    reset_ui = Signal()


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
            self.last_max_temper = -100

            self._init_signals()
            # self._init_timer_test()

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

    def _alarm_traverse_position(self, pos):
        self.signals.control_msg.emit(f'alarm_traverse_{pos}')

    def change_stage_controller(self, stage: str):
        self.stage = stage
        self.logger.debug(f'Stage --> {stage}')

    def change_next_stage_controller(self, stage: str):
        self.next_stage = stage
        self.logger.debug(f'Next Stage --> {stage}')

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
            type_test = self.model.data_test.type_test
            self.alarm_steps.step_alarm_traverse_position()

            if self.model.flag_test:
                self._select_alarm_state(self.steps.stage_control_alarm_state())

            if self.stage == 'wait':
                pass

            elif self.stage == 'wait_buffer':
                if self.model.buffer_state[0] == 'OK!':
                    if self.model.buffer_state[1] == 'buffer_on':
                        self.model.buffer_state = ['null', 'null']
                        # self.model.flag_bufer = True
                        # self.model.timer_pars_circle_start()
                        self.model.reader_start_test()
                        self.model.fc_control(**{'tag': 'up', 'adr': 1})
                        self.stage = self.next_stage

                    elif self.model.buffer_state[1] == 'buffer_off':
                        pass

                elif self.model.buffer_state[0] == 'ERROR!':
                    self.model.buffer_state = ['null', 'null']
                    self.model.write_bit_force_cycle(1)

            elif self.stage == 'repeat_test':
                self.stage = 'wait'
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
                    self.model.fc_control(**{'tag': 'stop', 'adr': 2})
                    self.model.write_bit_red_light(0)
                    self.alarm_steps.flag_alarm_traverse = False
                    self.stage = 'wait'
                    self.model.alarm_tag = ''
                    self.model.flag_alarm = False

                    self.signals.reset_ui.emit()

            elif self.stage == 'search_hod':
                if self.steps.stage_search_hod(self.count_cycle):
                    self.stage = 'wait'
                    self.steps.step_stop_gear_end_test()

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
                    self.signals.control_msg.emit('yellow_btn')

            elif self.stage == 'start_point_amort':
                if self.steps.step_control_traverse_move(self.set_trav_point):
                    # self.model.reset_current_circle()
                    self.next_stage = 'test_move_cycle'
                    self.signals.control_msg.emit(f'move_detection')
                    self._full_cycle_update('0')
                    self.steps.step_test_move_cycle()
                    self.stage = 'wait_buffer'

            elif self.stage == 'test_move_cycle':
                if self.count_cycle >= 1:
                    self.signals.control_msg.emit('pumping')
                    self._full_cycle_update('0')
                    self.steps.step_pumping_before_test()

            elif self.stage == 'pumping':
                if self.count_cycle >= 3:
                    if type_test == 'conv':
                        self.signals.conv_win_test.emit()
                        self._test_on_two_speed(1)
                    else:
                        self.signals.lab_win_test.emit()
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
                    self.model.save_result_cycle()
                    if type_test == 'conv':
                        self.steps.step_result_conveyor_test('one')

                    self.model.write_end_test_in_archive()
                    self._test_on_two_speed(2)

            elif self.stage == 'test_speed_two':
                if self.count_cycle >= 5:
                    self.model.save_result_cycle()
                    if type_test == 'conv':
                        self.steps.step_result_conveyor_test('two')
                        
                    self.stage = 'wait'
                    self.model.flag_fill_graph = False
                    self.model.write_end_test_in_archive()
                    self.steps.step_stop_gear_end_test()

            elif self.stage == 'test_lab_hand_speed':
                if self.count_cycle >= 5:
                    self.model.save_result_cycle()
                    self.stage = 'wait'
                    self.model.flag_fill_graph = False
                    self.model.write_end_test_in_archive()
                    self.steps.step_stop_gear_end_test()

            elif self.stage == 'test_temper':
                if self.count_cycle >= 1:
                    if self.model.data_test.max_temperature != self.last_max_temper:
                        self.last_max_temper = self.model.data_test.max_temperature
                        if self.model.data_test.max_temperature <= self.model.data_test.finish_temperature:
                            self.model.temper_graph.append(self.model.data_test.max_temperature)
                            self.model.temper_recoil_graph.append(self.model.max_recoil)
                            self.model.temper_comp_graph.append(self.model.max_comp)
                            self._full_cycle_update('0')

                        else:
                            self.model.save_result_cycle()
                            self.model.flag_fill_graph = False
                            self.stage = 'wait'
                            self.model.write_end_test_in_archive()
                            self.steps.step_stop_gear_end_test()

                    else:
                        self._full_cycle_update('0')

            elif self.stage == 'test_lab_cascade':
                if self.count_cycle >= 5:
                    self.model.save_result_cycle()
                    if self.count_cascade < self.max_cascade:
                        self.model.fc_control(**{'tag': 'speed', 'adr': 1,
                                                 'speed':self.model.data_test.speed_list[self.count_cascade]})
                        self.model.data_test.speed_test = self.model.data_test.speed_list[self.count_cascade]

                        self.model.clear_data_in_graph()
                        self.model.flag_fill_graph = True
                        self.count_cascade += 1

                        self._full_cycle_update('0')

                    else:
                        self.stage = 'wait'
                        self.model.flag_fill_graph = False
                        self.count_cascade = 1
                        self.model.write_end_test_in_archive()
                        self.steps.step_stop_gear_end_test()


            elif self.stage == 'stop_gear_end_test':
                if self.steps.stage_stop_gear_end_test():
                    self.steps.step_stop_gear_min_pos()

            elif self.stage == 'stop_gear_min_pos':
                if self.steps.stage_stop_gear_min_pos():
                    if self.model.flag_search_hod:
                        self.model.flag_search_hod = False
                        self.signals.search_hod_msg.emit()

                    else:
                        if type_test == 'conv':
                            self.signals.conv_test_stop.emit()

                        else:
                            self.signals.lab_test_stop.emit()

            elif self.stage == 'stop_test':
                flag = self.steps.step_control_traverse_move(self.set_trav_point)
                if flag:
                    self.stage = 'wait'
                    if not self.model.flag_alarm:
                        self.signals.cancel_test.emit()

            else:
                pass

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/_update_stage_on_timer - {e}')

    def _select_alarm_state(self, tag):
        try:
            self.signals.control_msg.emit(tag)
            if tag == 'lost_control':
                self.alarm_steps.step_lost_control()

            elif tag == 'excess_force':
                self.alarm_steps.step_excess_force()

            elif tag == 'safety_fence':
                self.alarm_steps.step_safety_fence()

            elif tag == 'excess_temperature':
                self.steps.step_stop_gear_end_test()
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
        self.model.flag_test_launch = False
        self.model.flag_test = False

        self.model.lamp_all_switch_off()

        if self.model.client.flag_connect:
            self.model.fc_control(**{'tag': 'stop', 'adr': 1})
            self.model.fc_control(**{'tag': 'stop', 'adr': 2})
            self.model.reader_stop_test()
            # self.model.flag_bufer = False
            # self.model.clear_data_in_graph()
            # self.model.timer_pars_circle_stop()
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

                self.model.write_emergency_force(self.calc_data.excess_force(self.model.data_test.amort))

                if self.model.flag_repeat:
                    self.stage = 'wait_buffer'
                    self.next_stage = 'repeat_test'
                    self.model.write_bit_force_cycle(1)

                else:
                    if self.model.move_traverse < 10:
                        self.signals.control_msg.emit('traverse_referent')
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

            if self.model.gear_referent:
                self.steps.step_stop_gear_end_test()
            else:
                self.model.fc_control(**{'tag': 'stop', 'adr': 1})
                self.model.fc_control(**{'tag': 'stop', 'adr': 2})

                self.signals.cancel_test.emit()

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/stop_test_clicked - {e}')

    def search_hod_gear(self):
        try:
            self.signals.control_msg.emit(f'move_detection')
            self._full_cycle_update('0')
            self.steps.step_search_hod_gear()

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/search_hod_gear - {e}')

    def move_gear_set_pos(self):
        try:
            self.signals.control_msg.emit('gear_set_pos')
            self._full_cycle_update('0')
            self.steps.step_move_gear_set_pos()

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/move_gear_set_pos - {e}')

    def traverse_install_point(self, tag):
        """Позционирование траверсы"""
        try:
            stock_point = 760 # Константа, измереная высота у стенда
            hod = self.model.data_test.amort.hod
            len_min = self.model.data_test.amort.min_length
            len_max = self.model.data_test.amort.max_length
            mid_point = (len_max - len_min) / 2
            adapter = self.model.data_test.amort.adapter_len

            if tag == 'install':
                install_point = round((stock_point + hod / 2) - len_max - adapter, 1)
                # print(f'Цель -- {install_point}')
                self.signals.control_msg.emit(f'pos_traverse')
                # if self.model.move_traverse < install_point:
                #     install_point -= 1
                    
                if abs(abs(self.model.move_traverse) - abs(install_point)) < 0.5:
                    self.signals.control_msg.emit('yellow_btn')

                else:
                    self.stage = 'install_amort'
                    self.set_trav_point = install_point
                    self.steps.step_traverse_move_position(install_point)

            elif tag == 'start_test':
                start_point = int(stock_point - len_max - adapter + mid_point)
                self.signals.control_msg.emit(f'pos_traverse')
                self.stage = 'start_point_amort'
                self.set_trav_point = start_point
                self.steps.step_traverse_move_position(start_point)

            elif tag == 'stop_test':
                if not self.model.flag_alarm:
                    self.signals.control_msg.emit(f'pos_traverse')

                end_point = int((stock_point + hod / 2) - len_max - adapter)

                self.stage = 'stop_test'
                self.set_trav_point = end_point
                self.steps.step_traverse_move_position(end_point)

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/traverse_install_point - {e}')

    def _test_on_two_speed(self, ind):
        try:
            # if self.model.type_test == 'conv':
            #     self.signals.conv_win_test.emit()
            # elif self.model.type_test == 'lab':
            #     self.signals.lab_win_test.emit()
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
        first = self.model.reg_data.first_t
        second = self.model.reg_data.second_t
        if self.model.data_test.type_test == 'temper':
            finish_temp = self.model.data_test.finish_temperature
        else:
            finish_temp = self.model.data_test.amort.max_temper

        if first < finish_temp and second < finish_temp:
            return True

        else:
            self.signals.control_msg.emit('excess_temperature')
            return False

    def _test_temper(self):
        try:
            self.signals.lab_win_test.emit()
            self.last_max_temper = -100
            self.steps_tests.step_test_temper()
            self._full_cycle_update('0')

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/_test_temper - {e}')

    def _test_lab_cascade(self):
        try:
            self.signals.lab_win_test.emit()
            self.count_cascade = 1
            self.max_cascade = len(self.model.data_test.speed_list)

            self.steps_tests.step_test_lab_cascade(self.model.data_test.speed_list)
            self._full_cycle_update('0')

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/_test_lab_cascade - {e}')
