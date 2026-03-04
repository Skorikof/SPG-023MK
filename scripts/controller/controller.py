# -*- coding: utf-8 -*-
from PySide6.QtCore import QTimer, QObject, Signal, Slot

from scripts.logger import my_logger
from scripts.data_calculation import CalcData
from .alarm_steps import AlarmSteps
from .stages import Stage
from .test_flow import TestFlow
from .traverse_service import TraverseService


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
            self.model = model
            self.signals = ControlSignals()
            
            self.alarm_steps = AlarmSteps(model)
            self.calc_data = CalcData()
            self.test_flow = TestFlow(model)
            self.trav_serv = TraverseService(model)

            self._init_variables()
            self._init_flags()
            self._init_stage_handlers()
            self._init_signals()
            self._init_timer_test()

        except Exception as e:
            self.logger.error(e)
            
    def _init_variables(self):
        self.stage = Stage.WAIT
        self.next_stage = Stage.WAIT
        self.timer_process = None
        self.set_trav_point = 0
        self.count_cascade = 1
        self.max_cascade = 0
        self.last_max_temper = -100
        
    def _init_flags(self):
        self.flag_alarm_traverse = True
        self.flag_collect_done = False
        
    def _init_stage_handlers(self):
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
            Stage.TEST_PROGRAM: self._stage_testing_prog,
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
            Stage.TEST_PROGRAM: self._enter_testing_prog,
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
            Stage.TEST_PROGRAM: self._exit_testing_prog,
        }

    def _init_signals(self):
        try:
            self.model.signals.test_launch.connect(self._yellow_btn_push)

            self.alarm_steps.signals.stage_from_alarm.connect(self.set_stage)
            self.alarm_steps.signals.alarm_traverse.connect(self._alarm_traverse_position)
            
            self.test_flow.signals.set_stage.connect(self.set_stage)
            self.test_flow.signals.set_next_stage.connect(self.set_next_stage)
            
            self.trav_serv.signals.set_stage.connect(self.set_stage)
            self.trav_serv.signals.control_msg.connect(self._signal_control_msg)

        except Exception as e:
            self.logger.error(e)
            
    def _init_timer_test(self):
        self.timer_process = QTimer()
        self.timer_process.setInterval(100)
        self.timer_process.timeout.connect(self._update_stage_on_timer)
        self.timer_process.start()

    @Slot(str)
    def _signal_control_msg(self, text):
        self.signals.control_msg.emit(text)

    def _alarm_traverse_position(self, pos):
        self.signals.control_msg.emit(f'alarm_traverse_{pos}')
        
    @Slot(object)
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

    def _on_enter_stage(self, stage: Stage):
        handler = self._enter_handlers.get(stage)
        if handler:
            handler()
            
    def _on_exit_stage(self, stage):
        handler = self._exit_handlers.get(stage)
        if handler:
            handler()

    def set_next_stage(self, stage):
        self.logger.debug(f'Next stage {self.next_stage} -> {stage}')
        self.next_stage = stage
            
    def _update_stage_on_timer(self):
        try:
            self.alarm_steps.step_alarm_traverse_position()

            if self.model.flag_test:
                self._select_alarm_state(
                    self.alarm_steps.control_alarm_state()
                )

            handler = self._stage_handlers.get(self.stage)
            
            if handler is None:
                self.logger.error(f'No handler for stage {self.stage}')
                return
            
            handler()

        except Exception as e:
            self.logger.error(e)

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
                self.test_flow.stop_gear_end_test()
                self.alarm_steps.step_excess_temperature()
            else:
                pass

        except Exception as e:
            self.logger.error(e)

    def work_interrupted_operator(self):
        self.set_stage(Stage.WAIT)
        self.model.flag_test_launch = False
        self.model.flag_test = False

        self.model.lamp_all_switch_off()

        if self.model.client.client_connect:
            self.model.fc_control(**{'tag': 'stop', 'adr': 1})
            self.model.fc_control(**{'tag': 'stop', 'adr': 2})
            self.model.reader_stop_test()
            self.model.write_bit_force_cycle(0)
            
    # FIXME При втором испытании он сразу падает сюда в else и останавливает испытание, соответственно пока отключена кнопка
    def step_yellow_btn_push(self):
        try:
            if self.model.flag_test is False:
                if self.model.state_dict.get('green_light') or self.model.state_dict.get('red_light'):
                    self.model.lamp_all_switch_off()
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

    def _yellow_btn_push(self, state: bool):
        """Обработка нажатия жёлтой кнопки, запускает она испытание или останавливает"""
        try:
            if state:
                tag = self.step_yellow_btn_push()
                if tag == 'start':
                    self.trav_serv.traverse_install_point('start_test')

                elif tag == 'stop':
                    self.stop_test_clicked()

        except Exception as e:
            self.logger.error(e)

    # FIXME Пока закоммичено в тестовом режиме
    def start_test_clicked(self):
        """
        Точка входа в испытание, определение референтной точки траверсы, если известна,
        то сразу запуск позиционирования для установки амортизатора
        """
        try:
            self._test_program()
            # if self.model.check_max_temper_test():
            #     self.step_start_test()

            #     self.model.write_emergency_force(self.calc_data.excess_force(self.model.data_test.amort))

            #     if self.model.flag_repeat:
            #         self.set_stage(Stage.WAIT_BUFFER)
            #         self.set_next_stage(Stage.REPEAT_TEST)

            #     else:
            #         if self.model.move_traverse < 10:
            #             self.trav_serv.step_traverse_referent_point()

            #         else:
            #             self.trav_serv.traverse_install_point('install')

            # else:
            #     self.signals.control_msg.emit('excess_temperature')
            #     self.step_stop_test()

        except Exception as e:
            self.logger.error(e)
        
    def step_start_test(self):
        try:
            if self.model.state_dict.get('excess_force', False) is True:
                self.model.write_bit_emergency_force()

            if self.model.state_dict.get('lost_control', False) is True:
                self.model.write_bit_unblock_control()

            self.model.lamp_all_switch_off()

            self.model.data_test.max_temperature = 0
            self.model.flag_test_launch = True
            self.model.alarm_tag = ''
            self.model.flag_alarm = False

        except Exception as e:
            self.logger.error(e)

    def stop_test_clicked(self):
        """
        Завершение теста, если определена референтная точка коленвала, то остановка в нижней точке,
        иначе моментальная остановка
        """
        try:
            self.step_stop_test()
            self.test_flow.stop_gear_end_test()

        except Exception as e:
            self.logger.error(e)
            
    def step_stop_test(self):
        try:
            self.model.flag_test_launch = False
            self.model.flag_test = False

        except Exception as e:
            self.logger.error(e)

    def search_hod(self):
        """Блок определения хода шатуна"""
        self.test_flow.search_hod()
        
    # FIXME Пока не реализован
    def move_gear_set_pos(self):
        """Блок доворота шатуна для регулировки хода"""
        self.test_flow.move_gear_set_pos()

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
        """Блок ожидания включения записи в буфер и переключение на следующий шаг"""
        if self.model.buffer_state[0] == 'OK!':
            if self.model.buffer_state[1] == 'buffer_on':
                self.model.buffer_state = ['null', 'null']
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
            self.test_flow.test_lab_hand_speed()
        elif type_test == 'temper':
            self.test_flow.test_temper()
        elif type_test == 'lab_cascade':
            self.test_flow.test_lab_cascade()
        else:
            self.test_flow.test_on_two_speed(1)

    def _exit_repeat_test(self):
        pass

    def _enter_alarm_traverse(self):
        pass

    def _stage_alarm_traverse(self):
        if self.trav_serv.step_control_traverse_move(self.set_trav_point):
            self.model.fc_control(**{'tag': 'stop', 'adr': 2})
            self.model.write_bit_red_light(0)
            self.alarm_steps.flag_alarm_traverse = False
            self.set_stage(Stage.WAIT)
            self.model.alarm_tag = ''
            self.model.flag_alarm = False
            self.signals.reset_ui.emit()

    def _exit_alarm_traverse(self):
        pass

    # FIXME Пока не реализован
    def _enter_pos_set_gear(self):
        self.signals.control_msg.emit('gear_set_pos')

    def _stage_pos_set_gear(self):
        if self.model.gear_referent:
            if self.model.max_pos:
                if abs(14 - self.model.move_now) < 5:
                    self.model.fc_control(**{'tag': 'stop', 'adr': 1})
                    self.model.reader_stop_test()
                    self.model.write_bit_force_cycle(0)
                    self.model.min_pos = False
                    self.model.max_pos = False
                    self.set_stage(Stage.WAIT)
                    self.signals.reset_ui.emit()

    def _exit_pos_set_gear(self):
        pass

    def _enter_traverse_referent(self):
        self.signals.control_msg.emit('traverse_referent')

    def _stage_traverse_referent(self):
        if self.trav_serv.stage_traverse_referent():
            self.set_stage(Stage.WAIT)
            self.trav_serv.traverse_install_point('install')

    def _exit_traverse_referent(self):
        pass

    def _enter_install_amort(self):
        self.signals.control_msg.emit('pos_traverse')

    def _stage_install_amort(self):
        if self.trav_serv.step_control_traverse_move(self.set_trav_point):
            self.set_stage(Stage.WAIT)
            self.signals.control_msg.emit('yellow_btn')

    def _exit_install_amort(self):
        pass

    def _enter_stop_test(self):
        if not self.model.flag_alarm:
            self.signals.control_msg.emit(f'pos_traverse')

    def _stage_stop_test(self):
        if self.trav_serv.step_control_traverse_move(self.set_trav_point):
            self.set_stage(Stage.WAIT)
            if not self.model.flag_alarm:
                self.signals.cancel_test.emit()

    def _exit_stop_test(self):
        pass

    def _enter_search_hod(self):
        self.signals.control_msg.emit(f'move_detection')
        self.model.start_find_stroke()

    def _stage_search_hod(self):
        if self.model.is_collect_done():
            self.test_flow.stop_gear_end_test()

    def _exit_search_hod(self):
        self.model.stop_collect()
        
    def _enter_start_point_amort(self):
        self.signals.control_msg.emit(f'pos_traverse')

    def _stage_start_point_amort(self):
        if self.trav_serv.step_control_traverse_move(self.set_trav_point):
            self.test_flow.test_move_cycle()

    def _exit_start_point_amort(self):
        pass
        
    def _enter_test_move_cycle(self):
        self.signals.control_msg.emit(f'move_detection')
        self.model.start_collect(with_data=False)
        
    def _stage_test_move_cycle(self):
        if self.model.is_collect_done():
            self.test_flow.pumping()

    def _exit_test_move_cycle(self):
        self.model.stop_collect()
        
    def _enter_pumping(self):
        self.signals.control_msg.emit('pumping')
        self.model.start_collect(with_data=False)

    def _stage_pumping(self):
        type_test = self.model.data_test.type_test
        if self.model.is_collect_done():
            if type_test == 'conv':
                self.signals.conv_win_test.emit()
                self.test_flow.test_on_two_speed(1)
            else:
                self.signals.lab_win_test.emit()
                if type_test == 'lab_hand':
                    self.test_flow.test_lab_hand_speed()
                elif type_test == 'temper':
                    self.test_flow.test_temper()
                elif type_test == 'lab_cascade':
                    self.test_flow.test_lab_cascade()
                else:
                    self.test_flow.test_on_two_speed(1)

    def _exit_pumping(self):
        self.model.stop_collect()
        
    def _enter_test_speed_one(self):
        self.model.start_collect(with_data=True)

    def _stage_test_speed_one(self):
        if self.model.is_collect_done():
            type_test = self.model.data_test.type_test
            # self.model.save_result_cycle() # FIXME
            if type_test == 'conv':
                self.model.step_result_conveyor_test('one')
            self.model.write_end_test_in_archive()
            self.test_flow.test_on_two_speed(2)

    def _exit_test_speed_one(self):
        self.model.stop_collect()
        
    def _enter_test_speed_two(self):
        self.model.start_collect(with_data=True)

    def _stage_test_speed_two(self):
        if self.model.is_collect_done():
            type_test = self.model.data_test.type_test
            # self.model.save_result_cycle() # FIXME
            if type_test == 'conv':
                self.model.step_result_conveyor_test('two')
            self.set_stage(Stage.WAIT)
            self.model.write_end_test_in_archive()
            self.test_flow.stop_gear_end_test()

    def _exit_test_speed_two(self):
        self.model.stop_collect()
        
    def _enter_test_lab_hand_speed(self):
        self.signals.lab_win_test.emit()
        self.model.start_collect(with_data=True)

    def _stage_test_lab_hand_speed(self):
        if self.model.is_collect_done():
            # self.model.save_result_cycle() # FIXME
            self.set_stage(Stage.WAIT)
            self.model.write_end_test_in_archive()
            self.test_flow.stop_gear_end_test()

    def _exit_test_lab_hand_speed(self):
        self.model.stop_collect()
        
    def _enter_test_lab_cascade(self):
        self.signals.lab_win_test.emit()
        self.model.start_collect(with_data=True)

    def _stage_test_lab_cascade(self):
        if self.model.is_collect_done():
            # self.model.save_result_cycle() # FIXME
            if self.count_cascade < self.max_cascade:
                speed = self.model.data_test.speed_list[self.count_cascade]
                self.model.data_test.speed_test = speed
                self.model.fc_control(**{'tag': 'speed', 'adr': 1, 'speed': speed})
                self.model.start_collect(with_data=True)
                self.count_cascade += 1
            else:
                self.set_stage(Stage.WAIT)
                self.count_cascade = 1
                self.model.write_end_test_in_archive()
                self.test_flow.stop_gear_end_test()

    def _exit_test_lab_cascade(self):
        self.model.stop_collect()
        
    # FIXME Испытание пока со старой реализацией, переделать
    def _enter_test_temper(self):
        self.last_max_temper = -100
        self.signals.lab_win_test.emit()
        self.model.start_collect_inf_cycle()

    def _stage_test_temper(self):
        if self.model.is_collect_done():
            if self.model.data_test.max_temperature != self.last_max_temper:
                self.last_max_temper = self.model.data_test.max_temperature
                if self.model.data_test.max_temperature <= self.model.data_test.finish_temperature:
                    self.model.temper_graph.append(self.model.data_test.max_temperature)
                    self.model.temper_recoil_graph.append(self.model.max_recoil)
                    self.model.temper_comp_graph.append(self.model.max_comp)
                else:
                    # self.model.save_result_cycle() # FIXME
                    self.set_stage(Stage.WAIT)
                    self.model.write_end_test_in_archive()
                    self.test_flow.stop_gear_end_test()

    def _exit_test_temper(self):
        self.model.stop_cycle_collection()
        self.model.stop_collect()

    def _enter_stop_gear_end_test(self):
        self.flag_collect_done = False
        self.model.reader_start_test()

    def _stage_stop_gear_end_test(self):
        if self.model.is_motor_stopped():
            self.test_flow.stop_gear_min_pos()

    def _exit_stop_gear_end_test(self):
        self.model.stop_collect()
        self.test_flow.transition_via_buffer(Stage.STOP_GEAR_MIN_POS)
        
    def _enter_stop_gear_min_pos(self):
        self.model.start_nmt_poition()

    def _stage_stop_gear_min_pos(self):
        if self.model.get_nmt_info():
            info = self.model.get_nmt_info()
            tag = 'down'
            if info['direction_to_nmt'] > 0:
                tag = 'down'
            else:
                tag = 'up'
            
            speed = self.calc_data.definition_speed_by_hod('slow')
            self.model.fc_control(**{'tag': 'speed', 'adr': 1, 'speed': speed})
            self.model.fc_control(**{'tag': tag, 'adr': 1})
            
            if self.model.is_nmt_reached():
                self.model.fc_control(**{'tag': 'stop', 'adr': 1})

                self.set_stage(Stage.WAIT)
                if self.model.flag_test:
                    self.model.flag_test = False
            
                type_test = self.model.data_test.type_test
                if self.model.flag_search_hod:
                    self.model.flag_search_hod = False
                    self.signals.search_hod_msg.emit()
                else:
                    if type_test == 'conv':
                        self.signals.conv_test_stop.emit()
                    else:
                        self.signals.lab_test_stop.emit()

    def _exit_stop_gear_min_pos(self):
        self.model.stop_collect()
    
    #--------- testing ---------#
    def _test_program(self):
        self.test_flow.transition_via_buffer(Stage.TEST_PROGRAM)

    def _enter_testing_prog(self):
        print('enter test stage')
        self.model.start_collect(with_data=True)
        print('enter stage buffer start')
        self.signals.lab_win_test.emit()

    def _stage_testing_prog(self):
        if self.model.is_collect_done():
            print('Congratelations! 3 cycles is done')
            self.set_stage(Stage.WAIT)

    def _exit_testing_prog(self):
        print('exit test stage')
        self.model.stop_collect()
        print('exit stage off sensor')
