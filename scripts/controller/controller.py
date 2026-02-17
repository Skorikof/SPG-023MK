# -*- coding: utf-8 -*-
from PySide6.QtCore import QTimer, QObject, Signal, Slot

from config import config
from scripts.logger import my_logger
from scripts.data_calculation import CalcData
from scripts.controller.stages import Stage
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

            self._init_variables()
            self._init_flags()
            self._init_signals()
            self._init_timer_test()

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/__init__ - {e}')
            
    def _init_variables(self):
        self.stage = Stage.WAIT
        self.next_stage = Stage.WAIT
        
        self.timer_process = None
        self._stage_handlers = {
            Stage.WAIT: self._stage_wait,
            Stage.WAIT_BUFFER: self._stage_wait_buffer,
            Stage.REPEAT_TEST: self._stage_repeat_test,
            Stage.ALARM_TRAVERSE: self._stage_alarm_traverse,
            Stage.SEARCH_HOD: self._stage_search_hod,
            Stage.PUMPING: self._stage_pumping,
            Stage.POS_SET_GEAR: self._stage_pos_set_gear,
            Stage.TRAVERSE_REFERENT: self._stage_traverse_referent,
            Stage.INSTALL_AMORT: self._stage_install_amort,
            Stage.START_POINT_AMORT: self._stage_start_point_amort,
            Stage.TEST_MOVE_CYCLE: self._stage_test_move_cycle,
            Stage.TEST_SPEED_ONE: self._stage_test_speed_one,
            Stage.TEST_SPEED_TWO: self._stage_test_speed_two,
            Stage.TEST_LAB_HAND_SPEED: self._stage_test_lab_hand_speed,
            Stage.TEST_TEMPER: self._stage_test_temper,
            Stage.TEST_LAB_CASCADE: self._stage_test_lab_cascade,
            Stage.STOP_GEAR_END_TEST: self._stage_stop_gear_end_test,
            Stage.STOP_GEAR_MIN_POS: self._stage_stop_gear_min_pos,
            Stage.STOP_TEST: self._stage_stop_test,
        }
        
        self._enter_handlers = {
            Stage.WAIT: self._enter_wait,
            Stage.WAIT_BUFFER: self._enter_wait_buffer,
            Stage.REPEAT_TEST: self._enter_repeat_test,
            Stage.ALARM_TRAVERSE: self._enter_alarm_traverse,
            Stage.SEARCH_HOD: self._enter_search_hod,
            Stage.PUMPING: self._enter_pumping,
            Stage.POS_SET_GEAR: self._enter_pos_set_gear,
            Stage.TRAVERSE_REFERENT: self._enter_traverse_referent,
            Stage.INSTALL_AMORT: self._enter_install_amort,
            Stage.START_POINT_AMORT: self._enter_start_point_amort,
            Stage.TEST_MOVE_CYCLE: self._enter_test_move_cycle,
            Stage.TEST_SPEED_ONE: self._enter_test_speed_one,
            Stage.TEST_SPEED_TWO: self._enter_test_speed_two,
            Stage.TEST_LAB_HAND_SPEED: self._enter_test_lab_hand_speed,
            Stage.TEST_TEMPER: self._enter_test_temper,
            Stage.TEST_LAB_CASCADE: self._enter_test_lab_cascade,
            Stage.STOP_GEAR_END_TEST: self._enter_stop_gear_end_test,
            Stage.STOP_GEAR_MIN_POS: self._enter_stop_gear_min_pos,
            Stage.STOP_TEST: self._enter_stop_test,
        }
        
        self._exit_handlers = {
            Stage.WAIT: self._exit_wait,
            Stage.WAIT_BUFFER: self._exit_wait_buffer,
            Stage.REPEAT_TEST: self._exit_repeat_test,
            Stage.ALARM_TRAVERSE: self._exit_alarm_traverse,
            Stage.SEARCH_HOD: self._exit_search_hod,
            Stage.PUMPING: self._exit_pumping,
            Stage.POS_SET_GEAR: self._exit_pos_set_gear,
            Stage.TRAVERSE_REFERENT: self._exit_traverse_referent,
            Stage.INSTALL_AMORT: self._exit_install_amort,
            Stage.START_POINT_AMORT: self._exit_start_point_amort,
            Stage.TEST_MOVE_CYCLE: self._exit_test_move_cycle,
            Stage.TEST_SPEED_ONE: self._exit_test_speed_one,
            Stage.TEST_SPEED_TWO: self._exit_test_speed_two,
            Stage.TEST_LAB_HAND_SPEED: self._exit_test_lab_hand_speed,
            Stage.TEST_TEMPER: self._exit_test_temper,
            Stage.TEST_LAB_CASCADE: self._exit_test_lab_cascade,
            Stage.STOP_GEAR_END_TEST: self._exit_stop_gear_end_test,
            Stage.STOP_GEAR_MIN_POS: self._exit_stop_gear_min_pos,
            Stage.STOP_TEST: self._exit_stop_test,
        }
        
        self.count_cycle = 0
        self.set_trav_point = 0
        self.count_cascade = 1
        self.max_cascade = 0
        self.last_max_temper = -100
        
    def _init_flags(self):
        self.flag_alarm_traverse = True
        self.flag_collect_done = False

    def _init_signals(self):
        try:
            self.model.signals.full_cycle_count.connect(self._full_cycle_update)
            self.model.signals.test_launch.connect(self._yellow_btn_push)

            self.alarm_steps.signals.stage_from_alarm.connect(self.set_stage)
            self.alarm_steps.signals.alarm_traverse.connect(self._alarm_traverse_position)

            self.steps.signals.stage_from_logic.connect(self.set_stage)
            self.steps.signals.next_stage_from_logic.connect(self.set_next_stage)

            self.steps_tests.signals.stage_from_tests.connect(self.set_stage)
            self.steps_tests.signals.next_stage_from_tests.connect(self.set_next_stage)

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/_init_signals - {e}')

    def _alarm_traverse_position(self, pos):
        self.signals.control_msg.emit(f'alarm_traverse_{pos}')
        
    def set_stage(self, new_stage: Stage):
        if new_stage == self.stage:
            return
        if new_stage not in self._stage_handlers:
            self.logger.error(f"Unknown stage {new_stage}")
            return
        old_stage = self.stage
        self._on_exit_stage(old_stage)
        self.logger.debug(f'Stage {old_stage} -> {new_stage}')
        self.stage = new_stage
        self._on_enter_stage(new_stage)

    def _on_exit_stage(self, stage):
        handler = self._exit_handlers.get(stage)
        if handler:
            handler()

    def _on_enter_stage(self, stage: Stage):
        handler = self._enter_handlers.get(stage)
        if handler:
            handler()

    def set_next_stage(self, stage):
        self.logger.debug(f'Next stage {self.next_stage} -> {stage}')
        self.next_stage = stage
    
    @Slot()
    def _collect_done(self):
        self.flag_collect_done = True

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

            if self.model.flag_test:
                self._select_alarm_state(
                    self.steps.stage_control_alarm_state()
                )

            handler = self._stage_handlers.get(self.stage)
            
            if handler is None:
                self.logger.error(f'No handler for stage {self.stage}')
                return
            
            handler()

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(
                f'ERROR in controller/_update_stage_on_timer - {e}'
            )

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
            self.set_stage(Stage.ALARM_TRAVERSE)
            self.steps.step_traverse_move_position(self.set_trav_point)

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/traverse_move_out_alarm - {e}')

    def work_interrupted_operator(self):
        self.set_stage(Stage.WAIT)
        self.model.flag_test_launch = False
        self.model.flag_test = False

        self.model.lamp_all_switch_off()

        if self.model.client.flag_connect:
            self.model.fc_control(**{'tag': 'stop', 'adr': 1})
            self.model.fc_control(**{'tag': 'stop', 'adr': 2})
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

                self.model.write_emergency_force(self.calc_data.excess_force(self.model.data_test.amort))

                if self.model.flag_repeat:
                    self.set_stage(Stage.WAIT_BUFFER)
                    self.set_next_stage(Stage.REPEAT_TEST)
                    self.model.write_bit_force_cycle(1)

                else:
                    if self.model.move_traverse < 10:
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
            self._full_cycle_update('0')
            self.steps.step_search_hod_gear()

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/search_hod_gear - {e}')

    def move_gear_set_pos(self):
        try:
            self._full_cycle_update('0')
            self.steps.step_move_gear_set_pos()

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/move_gear_set_pos - {e}')

    def traverse_install_point(self, tag):
        """Позционирование траверсы"""
        try:
            stock_point = config.const_traverse
            hod = self.model.data_test.amort.hod
            len_min = self.model.data_test.amort.min_length
            len_max = self.model.data_test.amort.max_length
            mid_point = (len_max - len_min) / 2
            adapter = self.model.data_test.amort.adapter_len
            if tag == 'install':
                install_point = round((stock_point + hod / 2) - len_max - adapter, 1)
                if abs(abs(self.model.move_traverse) - abs(install_point)) < 0.5:
                    self.signals.control_msg.emit('yellow_btn')
                else:
                    self.set_stage(Stage.INSTALL_AMORT)
                    self.set_trav_point = install_point
                    self.steps.step_traverse_move_position(install_point)
            elif tag == 'start_test':
                start_point = int(stock_point - len_max - adapter + mid_point)
                self.set_stage(Stage.START_POINT_AMORT)
                self.set_trav_point = start_point
                self.steps.step_traverse_move_position(start_point)
            elif tag == 'stop_test':
                end_point = int((stock_point + hod / 2) - len_max - adapter)
                self.set_stage(Stage.STOP_TEST)
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
        first = self.model.data_test.first_temperature
        second = self.model.data_test.second_temperature
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
            
    ##### STAGES #####
    def _enter_wait(self):
        pass

    def _stage_wait(self):
        pass

    def _exit_wait(self):
        pass

    def _enter_wait_buffer(self):
        pass

    def _stage_wait_buffer(self):
        if self.model.buffer_state[0] == 'OK!':
            if self.model.buffer_state[1] == 'buffer_on':
                self.model.buffer_state = ['null', 'null']
                self.model.reader_start_test()
                self.model.fc_control(tag='up', adr=1)
                self.set_stage(self.next_stage)
            elif self.model.buffer_state[1] == 'buffer_off':
                pass
        elif self.model.buffer_state[0] == 'ERROR!':
            self.model.buffer_state = ['null', 'null']
            self.model.write_bit_force_cycle(1)

    def _exit_wait_buffer(self):
        pass

    def _enter_repeat_test(self):
        pass

    def _stage_repeat_test(self):
        type_test = self.model.data_test.type_test
        self.set_stage(Stage.WAIT)
        if type_test == 'lab_hand':
            self._test_lab_hand_speed()
        elif type_test == 'temper':
            self._test_temper()
        elif type_test == 'lab_cascade':
            self._test_lab_cascade()
        else:
            self._test_on_two_speed(1)

    def _exit_repeat_test(self):
        pass

    def _enter_search_hod(self):
        self.signals.control_msg.emit(f'move_detection')

    def _stage_search_hod(self):
        if self.steps.stage_search_hod(self.count_cycle):
            self.set_stage(Stage.WAIT)
            self.steps.step_stop_gear_end_test()

    def _exit_search_hod(self):
        pass

    def _enter_pumping(self):
        pass

    def _stage_pumping(self):
        type_test = self.model.data_test.type_test
        if self.count_cycle < 3:
            return
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

    def _exit_pumping(self):
        pass

    def _enter_alarm_traverse(self):
        pass

    def _stage_alarm_traverse(self):
        if self.steps.step_control_traverse_move(self.set_trav_point):
            self.model.fc_control(**{'tag': 'stop', 'adr': 2})
            self.model.write_bit_red_light(0)
            self.alarm_steps.flag_alarm_traverse = False
            self.set_stage(Stage.WAIT)
            self.model.alarm_tag = ''
            self.model.flag_alarm = False
            self.signals.reset_ui.emit()

    def _exit_alarm_traverse(self):
        pass

    def _enter_pos_set_gear(self):
        self.signals.control_msg.emit('gear_set_pos')

    def _stage_pos_set_gear(self):
        if self.steps.stage_pos_set_gear():
            self.set_stage(Stage.WAIT)
            self.signals.reset_ui.emit()

    def _exit_pos_set_gear(self):
        pass

    def _enter_traverse_referent(self):
        self.signals.control_msg.emit('traverse_referent')

    def _stage_traverse_referent(self):
        if self.steps.stage_traverse_referent():
            self.set_stage(Stage.WAIT)
            self.traverse_install_point('install')

    def _exit_traverse_referent(self):
        pass

    def _enter_install_amort(self):
        self.signals.control_msg.emit('pos_traverse')

    def _stage_install_amort(self):
        if self.steps.step_control_traverse_move(self.set_trav_point):
            self.set_stage(Stage.WAIT)
            self.signals.control_msg.emit('yellow_btn')

    def _exit_install_amort(self):
        pass

    def _enter_start_point_amort(self):
        self.signals.control_msg.emit(f'pos_traverse')

    def _stage_start_point_amort(self):
        if self.steps.step_control_traverse_move(self.set_trav_point):
            self.set_next_stage(Stage.TEST_MOVE_CYCLE)
            self.signals.control_msg.emit(f'move_detection')
            self._full_cycle_update('0')
            self.steps.step_test_move_cycle()
            self.set_stage(Stage.WAIT_BUFFER)

    def _exit_start_point_amort(self):
        pass

    def _enter_test_move_cycle(self):
        pass

    def _stage_test_move_cycle(self):
        if 0 < self.count_cycle < 2:
            return
        self.signals.control_msg.emit('pumping')
        self._full_cycle_update('0')
        self.steps.step_pumping_before_test()

    def _exit_test_move_cycle(self):
        pass

    def _enter_test_speed_one(self):
        pass

    def _stage_test_speed_one(self):
        type_test = self.model.data_test.type_test
        if self.count_cycle < 5:
            return
        self.model.save_result_cycle()
        if type_test == 'conv':
            self.steps.step_result_conveyor_test('one')
        self.model.write_end_test_in_archive()
        self._test_on_two_speed(2)

    def _exit_test_speed_one(self):
        pass

    def _enter_test_speed_two(self):
        pass

    def _stage_test_speed_two(self):
        type_test = self.model.data_test.type_test
        if self.count_cycle < 5:
            return
        self.model.save_result_cycle()
        if type_test == 'conv':
            self.steps.step_result_conveyor_test('two')
        self.set_stage(Stage.WAIT)
        self.model.flag_fill_graph = False
        self.model.write_end_test_in_archive()
        self.steps.step_stop_gear_end_test()

    def _exit_test_speed_two(self):
        pass

    def _enter_test_lab_hand_speed(self):
        pass

    def _stage_test_lab_hand_speed(self):
        if self.count_cycle < 5:
            return
        self.model.save_result_cycle()
        self.set_stage(Stage.WAIT)
        self.model.flag_fill_graph = False
        self.model.write_end_test_in_archive()
        self.steps.step_stop_gear_end_test()

    def _exit_test_lab_hand_speed(self):
        pass

    def _enter_test_temper(self):
        self.last_max_temper = -100

    def _stage_test_temper(self):
        if 0 < self.count_cycle < 2:
            return
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
                self.set_stage(Stage.WAIT)
                self.model.write_end_test_in_archive()
                self.steps.step_stop_gear_end_test()
        else:
            self._full_cycle_update('0')

    def _exit_test_temper(self):
        pass

    def _enter_test_lab_cascade(self):
        pass

    def _stage_test_lab_cascade(self):
        if self.count_cycle < 5:
            return
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
            self.set_stage(Stage.WAIT)
            self.model.flag_fill_graph = False
            self.count_cascade = 1
            self.model.write_end_test_in_archive()
            self.steps.step_stop_gear_end_test()

    def _exit_test_lab_cascade(self):
        pass

    def _enter_stop_gear_end_test(self):
        pass

    def _stage_stop_gear_end_test(self):
        if self.steps.stage_stop_gear_end_test():
            self.steps.step_stop_gear_min_pos()

    def _exit_stop_gear_end_test(self):
        pass

    def _enter_stop_gear_min_pos(self):
        pass

    def _stage_stop_gear_min_pos(self):
        type_test = self.model.data_test.type_test
        if self.steps.stage_stop_gear_min_pos():
            if self.model.flag_search_hod:
                self.model.flag_search_hod = False
                self.signals.search_hod_msg.emit()
            else:
                if type_test == 'conv':
                    self.signals.conv_test_stop.emit()
                else:
                    self.signals.lab_test_stop.emit()

    def _exit_stop_gear_min_pos(self):
        pass

    def _enter_stop_test(self):
        if not self.model.flag_alarm:
                    self.signals.control_msg.emit(f'pos_traverse')

    def _stage_stop_test(self):
        flag = self.steps.step_control_traverse_move(self.set_trav_point)
        if flag:
            self.set_stage(Stage.WAIT)
            if not self.model.flag_alarm:
                self.signals.cancel_test.emit()

    def _exit_stop_test(self):
        pass
