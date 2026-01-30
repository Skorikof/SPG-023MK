# -*- coding: utf-8 -*-
from dataclasses import dataclass
from PySide6.QtCore import QTimer, QObject, Signal

from scripts.logger import my_logger
from scripts.data_calculation import CalcData
from scripts.controller.steps_logic import Steps
from scripts.controller.alarm_steps import AlarmSteps
from scripts.controller.steps_tests import StepTests


@dataclass
class ControllerState:
    """Encapsulates controller runtime state."""
    stage: str = 'wait'
    next_stage: str = 'wait'
    flag_alarm_traverse: bool = True
    count_cycle: int = 0
    set_trav_point: int = 0
    count_cascade: int = 1
    max_cascade: int = 0
    last_max_temper: float = -100.0
    
    def reset(self):
        """Reset state to initial values."""
        self.stage = 'wait'
        self.next_stage = 'wait'
        self.flag_alarm_traverse = True
        self.count_cycle = 0
        self.set_trav_point = 0
        self.count_cascade = 1
        self.max_cascade = 0
        self.last_max_temper = -100.0


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

            self.state = ControllerState()
            self.timer_process = None

            self._init_signals()
            self._init_stage_handlers()
            self._init_timer_test()

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/__init__ - {e}')

    def _init_signals(self):
        """Initialize signal connections."""
        try:
            # Model signals
            signal_connections = [
                (self.model.signals.full_cycle_count, self._full_cycle_update),
                (self.model.signals.test_launch, self._yellow_btn_push),
            ]
            
            # Alarm steps signals
            signal_connections.extend([
                (self.alarm_steps.signals.stage_from_alarm, self.change_stage_controller),
                (self.alarm_steps.signals.alarm_traverse, self._alarm_traverse_position),
            ])
            
            # Steps logic signals
            signal_connections.extend([
                (self.steps.signals.stage_from_logic, self.change_stage_controller),
                (self.steps.signals.next_stage_from_logic, self.change_next_stage_controller),
            ])
            
            # Steps tests signals
            signal_connections.extend([
                (self.steps_tests.signals.stage_from_tests, self.change_stage_controller),
                (self.steps_tests.signals.next_stage_from_tests, self.change_next_stage_controller),
            ])
            
            # Connect all signals
            for signal, slot in signal_connections:
                signal.connect(slot)

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/_init_signals - {e}')
            
    def _init_stage_handlers(self):
        """Initialize stage handlers mapping."""
        self.stage_handlers = {
            'wait': self._handle_wait,
            'wait_buffer': self._handle_wait_buffer,
            'repeat_test': self._handle_repeat_test,
            'alarm_traverse': self._handle_alarm_traverse,
            'search_hod': self._handle_search_hod,
            'pos_set_gear': self._handle_pos_set_gear,
            'traverse_referent': self._handle_traverse_referent,
            'install_amort': self._handle_install_amort,
            'start_point_amort': self._handle_start_point_amort,
            'test_move_cycle': self._handle_test_move_cycle,
            'pumping': self._handle_pumping,
            'test_speed_one': self._handle_test_speed_one,
            'test_speed_two': self._handle_test_speed_two,
            'test_lab_hand_speed': self._handle_test_lab_hand_speed,
            'test_temper': self._handle_test_temper,
            'test_lab_cascade': self._handle_test_lab_cascade,
            'stop_gear_end_test': self._handle_stop_gear_end_test,
            'stop_gear_min_pos': self._handle_stop_gear_min_pos,
            'stop_test': self._handle_stop_test,
        }
        
        # Alarm state handlers
        self.alarm_handlers = {
            'lost_control': self._handle_alarm_lost_control,
            'excess_force': self._handle_alarm_excess_force,
            'safety_fence': self._handle_alarm_safety_fence,
            'excess_temperature': self._handle_alarm_excess_temperature,
        }

    def _alarm_traverse_position(self, pos):
        self.signals.control_msg.emit(f'alarm_traverse_{pos}')

    def change_stage_controller(self, stage: str):
        self.state.stage = stage
        self.logger.debug(f'Stage --> {stage}')

    def change_next_stage_controller(self, stage: str):
        self.state.next_stage = stage
        self.logger.debug(f'Next Stage --> {stage}')

    def _full_cycle_update(self, command: str):
        try:
            if command == '+1':
                self.state.count_cycle += 1
            else:
                self.state.count_cycle = int(command)

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
                self._select_alarm_state(self.steps.stage_control_alarm_state())
                
            # Get handler for current stage and execute it
            handler = self.stage_handlers.get(self.state.stage)
            if handler:
                handler()

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/_update_stage_on_timer - {e}')

    def _select_alarm_state(self, tag):
        try:
            self.signals.control_msg.emit(tag)
            handler = self.alarm_handlers.get(tag)
            if handler:
                handler()

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/_select_alarm_state - {e}')
            
    def _handle_alarm_lost_control(self):
        """Handle 'lost_control' alarm."""
        self.alarm_steps.step_lost_control()

    def _handle_alarm_excess_force(self):
        """Handle 'excess_force' alarm."""
        self.alarm_steps.step_excess_force()

    def _handle_alarm_safety_fence(self):
        """Handle 'safety_fence' alarm."""
        self.alarm_steps.step_safety_fence()

    def _handle_alarm_excess_temperature(self):
        """Handle 'excess_temperature' alarm."""
        self.steps.step_stop_gear_end_test()
        self.alarm_steps.step_excess_temperature()

    def traverse_move_out_alarm(self, pos):
        try:
            if pos == 'up':
                self.state.set_trav_point = 20
            elif pos == 'down':
                self.state.set_trav_point = 550

            self.state.stage = 'alarm_traverse'
            self.steps.step_traverse_move_position(self.state.set_trav_point)

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/traverse_move_out_alarm - {e}')

    def work_interrupted_operator(self):
        self.state.stage = 'wait'
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

                self.model.write_emergency_force(self.calc_data.excess_force(self.model.amort))

                if self.model.flag_repeat:
                    self.state.stage = 'wait_buffer'
                    self.state.next_stage = 'repeat_test'
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
            hod = self.model.amort.hod
            len_min = self.model.amort.min_length
            len_max = self.model.amort.max_length
            mid_point = (len_max - len_min) / 2
            adapter = self.model.amort.adapter_len

            if tag == 'install':
                install_point = round((stock_point + hod / 2) - len_max - adapter, 1)
                self.signals.control_msg.emit(f'pos_traverse')
                if abs(abs(self.model.move_traverse) - abs(install_point)) < 0.5:
                    self.signals.control_msg.emit('yellow_btn')

                else:
                    self.state.stage = 'install_amort'
                    self.state.set_trav_point = install_point
                    self.steps.step_traverse_move_position(install_point)

            elif tag == 'start_test':
                start_point = int(stock_point - len_max - adapter + mid_point)
                self.signals.control_msg.emit(f'pos_traverse')
                self.state.stage = 'start_point_amort'
                self.state.set_trav_point = start_point
                self.steps.step_traverse_move_position(start_point)

            elif tag == 'stop_test':
                if not self.model.flag_alarm:
                    self.signals.control_msg.emit(f'pos_traverse')

                end_point = int((stock_point + hod / 2) - len_max - adapter)

                self.state.stage = 'stop_test'
                self.state.set_trav_point = end_point
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
        if self.model.type_test == 'temper':
            finish_temp = self.model.finish_temper
        else:
            finish_temp = self.model.amort.max_temper

        if self.model.temper_first < finish_temp and self.model.temper_second < finish_temp:
            return True

        else:
            self.signals.control_msg.emit('excess_temperature')
            return False

    def _test_temper(self):
        try:
            self.signals.lab_win_test.emit()
            self.state.last_max_temper = -100
            self.steps_tests.step_test_temper()
            self._full_cycle_update('0')

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/_test_temper - {e}')

    def _test_lab_cascade(self):
        try:
            self.signals.lab_win_test.emit()
            self.state.count_cascade = 1
            self.state.max_cascade = len(self.model.speed_cascade)

            self.steps_tests.step_test_lab_cascade(self.model.speed_cascade)
            self._full_cycle_update('0')

        except Exception as e:
            self.logger.error(e)
            self.model.status_bar_msg(f'ERROR in controller/_test_lab_cascade - {e}')

    def _handle_wait(self):
            """Handle 'wait' stage - no action needed."""
            pass

    def _handle_wait_buffer(self):
        """Handle 'wait_buffer' stage - wait for buffer confirmation."""
        if self.model.buffer_state[0] == 'OK!':
            if self.model.buffer_state[1] == 'buffer_on':
                self.model.buffer_state = ['null', 'null']
                self.model.reader_start_test()
                self.model.fc_control(**{'tag': 'up', 'adr': 1})
                self.state.stage = self.state.next_stage
            elif self.model.buffer_state[1] == 'buffer_off':
                pass
        elif self.model.buffer_state[0] == 'ERROR!':
            self.model.buffer_state = ['null', 'null']
            self.model.write_bit_force_cycle(1)

    def _handle_repeat_test(self):
        """Handle 'repeat_test' stage - repeat test based on type."""
        self.state.stage = 'wait'
        type_test = self.model.data_test.type_test
        
        if type_test == 'lab_hand':
            self._test_lab_hand_speed()
        elif type_test == 'temper':
            self._test_temper()
        elif type_test == 'lab_cascade':
            self._test_lab_cascade()
        else:
            self._test_on_two_speed(1)

    def _handle_alarm_traverse(self):
        """Handle 'alarm_traverse' stage - traverse to alarm position."""
        if self.steps.step_control_traverse_move(self.state.set_trav_point):
            self.model.fc_control(**{'tag': 'stop', 'adr': 2})
            self.model.write_bit_red_light(0)
            self.alarm_steps.flag_alarm_traverse = False
            self.state.stage = 'wait'
            self.model.alarm_tag = ''
            self.model.flag_alarm = False
            self.signals.reset_ui.emit()

    def _handle_search_hod(self):
        """Handle 'search_hod' stage - search for gear stroke."""
        if self.steps.stage_search_hod(self.state.count_cycle):
            self.state.stage = 'wait'
            self.steps.step_stop_gear_end_test()

    def _handle_pos_set_gear(self):
        """Handle 'pos_set_gear' stage - set gear position."""
        if self.steps.stage_pos_set_gear():
            self.state.stage = 'wait'
            self.signals.reset_ui.emit()

    def _handle_traverse_referent(self):
        """Handle 'traverse_referent' stage - find traverse reference point."""
        if self.steps.stage_traverse_referent():
            self.state.stage = 'wait'
            self.traverse_install_point('install')

    def _handle_install_amort(self):
        """Handle 'install_amort' stage - move traverse to install position."""
        if self.steps.step_control_traverse_move(self.state.set_trav_point):
            self.state.stage = 'wait'
            self.signals.control_msg.emit('yellow_btn')

    def _handle_start_point_amort(self):
        """Handle 'start_point_amort' stage - move to start position and begin test."""
        if self.steps.step_control_traverse_move(self.state.set_trav_point):
            self.state.next_stage = 'test_move_cycle'
            self.signals.control_msg.emit('move_detection')
            self._full_cycle_update('0')
            self.steps.step_test_move_cycle()
            self.state.stage = 'wait_buffer'

    def _handle_test_move_cycle(self):
        """Handle 'test_move_cycle' stage - wait for one cycle then start pumping."""
        if self.state.count_cycle >= 1:
            self.signals.control_msg.emit('pumping')
            self._full_cycle_update('0')
            self.steps.step_pumping_before_test()

    def _handle_pumping(self):
        """Handle 'pumping' stage - pump for 3 cycles then start actual test."""
        if self.state.count_cycle >= 3:
            type_test = self.model.data_test.type_test
            
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

    def _handle_test_speed_one(self):
        """Handle 'test_speed_one' stage - first speed test."""
        if self.state.count_cycle >= 5:
            type_test = self.model.data_test.type_test
            if type_test == 'conv':
                self.steps.step_result_conveyor_test('one')
            
            self.model.write_end_test_in_archive()
            self._test_on_two_speed(2)

    def _handle_test_speed_two(self):
        """Handle 'test_speed_two' stage - second speed test."""
        if self.state.count_cycle >= 5:
            type_test = self.model.data_test.type_test
            if type_test == 'conv':
                self.steps.step_result_conveyor_test('two')
            
            self.model.write_end_test_in_archive()
            self.state.stage = 'wait'
            self.model.flag_fill_graph = False
            self.steps.step_stop_gear_end_test()

    def _handle_test_lab_hand_speed(self):
        """Handle 'test_lab_hand_speed' stage - lab hand speed test."""
        if self.state.count_cycle >= 5:
            self.state.stage = 'wait'
            self.model.flag_fill_graph = False
            self.model.write_end_test_in_archive()
            self.steps.step_stop_gear_end_test()

    def _handle_test_temper(self):
        """Handle 'test_temper' stage - temperature test."""
        if self.state.count_cycle >= 1:
            if self.model.data_test.max_temperature != self.state.last_max_temper:
                self.state.last_max_temper = self.model.data_test.max_temperature
                
                if self.model.data_test.max_temperature <= self.model.data_test.finish_temperature:
                    self.model.temper_graph.append(self.model.data_test.max_temperature)
                    self.model.temper_recoil_graph.append(self.model.max_recoil)
                    self.model.temper_comp_graph.append(self.model.max_comp)
                    self._full_cycle_update('0')
                else:
                    self.model.flag_fill_graph = False
                    self.state.stage = 'wait'
                    self.model.write_end_test_in_archive()
                    self.steps.step_stop_gear_end_test()
            else:
                self._full_cycle_update('0')

    def _handle_test_lab_cascade(self):
        """Handle 'test_lab_cascade' stage - cascade speed test."""
        if self.state.count_cycle >= 5:
            self.model.save_result_cycle()
            
            if self.state.count_cascade < self.state.max_cascade:
                speed_value = self.model.data_test.speed_list[self.state.count_cascade]
                self.model.fc_control(**{'tag': 'speed', 'adr': 1, 'speed': speed_value})
                self.model.data_test.speed_test = speed_value
                
                self.model.clear_data_in_graph()
                self.model.flag_fill_graph = True
                self.state.count_cascade += 1
                self._full_cycle_update('0')
            else:
                self.state.stage = 'wait'
                self.model.flag_fill_graph = False
                self.state.count_cascade = 1
                self.model.write_end_test_in_archive()
                self.steps.step_stop_gear_end_test()

    def _handle_stop_gear_end_test(self):
        """Handle 'stop_gear_end_test' stage - stop gear at end of test."""
        if self.steps.stage_stop_gear_end_test():
            self.steps.step_stop_gear_min_pos()

    def _handle_stop_gear_min_pos(self):
        """Handle 'stop_gear_min_pos' stage - gear stopped at minimum position."""
        if self.steps.stage_stop_gear_min_pos():
            if self.model.flag_search_hod:
                self.model.flag_search_hod = False
                self.signals.search_hod_msg.emit()
            else:
                type_test = self.model.data_test.type_test
                if type_test == 'conv':
                    self.signals.conv_test_stop.emit()
                else:
                    self.signals.lab_test_stop.emit()

    def _handle_stop_test(self):
        """Handle 'stop_test' stage - test stopping."""
        flag = self.steps.step_control_traverse_move(self.state.set_trav_point)
        if flag:
            self.state.stage = 'wait'
            if not self.model.flag_alarm:
                self.signals.cancel_test.emit()
