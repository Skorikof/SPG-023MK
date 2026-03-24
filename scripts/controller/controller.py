# -*- coding: utf-8 -*-
import time
from PySide6.QtCore import QTimer, QObject, Signal, Slot

from scripts.logger import my_logger
from scripts.model import Model
from scripts.data_calculation import CalcData
from .alarm_steps import AlarmSteps
from .stages import Stage, TypeTest
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
    def __init__(self, model: Model):
        self.logger = my_logger.get_logger(__name__)
        self.model = model
        self.signals = ControlSignals()
        
        self.alarm_steps = AlarmSteps(model)
        self.calc_data = CalcData()
        self.trav_serv = TraverseService(model)

        self._init_variables()
        self._init_flags()
        self._init_stage_handlers()
        self._init_signals()
        self._init_timer_test()
            
    def _init_variables(self):
        self.stage = Stage.WAIT
        self.next_stage = Stage.WAIT
        self.timer_process = None
        
    def _init_flags(self):
        self.flag_alarm_traverse = True
        
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

    def _init_signals(self):
        self.model.signals.test_launch.connect(self._yellow_btn_push)
        self.model.signals.set_stage.connect(self.set_stage)
        self.model.signals.set_next_stage.connect(self.set_next_stage)
        self.alarm_steps.signals.stage_from_alarm.connect(self.set_stage)
        self.alarm_steps.signals.alarm_traverse.connect(self._alarm_traverse_position)
        self.trav_serv.signals.set_stage.connect(self.set_stage)
        self.trav_serv.signals.control_msg.connect(self._signal_control_msg)
            
    def _init_timer_test(self):
        self.timer_process = QTimer()
        self.timer_process.setInterval(100)
        self.timer_process.timeout.connect(self._update_stage_on_timer)
        self.timer_process.start()
        
    def log_exceptions(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                args[0].logger.error(
                    f'ERROR in {func.__name__}: {e}'
                )
        return wrapper

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
    
    @log_exceptions     
    def _update_stage_on_timer(self):
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
            
    @log_exceptions
    def _select_alarm_state(self, tag):
        if not tag:
            return
        self.signals.control_msg.emit(tag)
        handlers = {
            'lost_control': self.alarm_steps.step_lost_control,
            'excess_force': self.alarm_steps.step_excess_force,
            'safety_fence': self.alarm_steps.step_safety_fence,
            'excess_temperature': self._handle_excess_temperature,
        }
        handler = handlers.get(tag)
        if handler:
            handler()
        else:
            self.logger.warning(f'Unknown alarm tag: {tag}')
            
    def _handle_excess_temperature(self):
        self.model.stop_gear_end_test()
        self.alarm_steps.step_excess_temperature()
            
    @log_exceptions 
    def _step_yellow_btn_push(self):
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

    @log_exceptions 
    def _yellow_btn_push(self, state: bool):
        """Обработка нажатия жёлтой кнопки, запускает она испытание или останавливает"""
        if state:
            tag = self._step_yellow_btn_push()
            if tag == 'start':
                self.trav_serv.traverse_install_point('start_test')
            elif tag == 'stop':
                self.stop_test_clicked()

    @log_exceptions
    def start_test_clicked(self):
        """
        Точка входа в испытание, определение референтной точки траверсы, если известна,
        то сразу запуск позиционирования для установки амортизатора
        """
        if self.model.check_max_temper_test():
            self.model.flag_reset_start_test()
            self.model.write_emergency_force_start_test()

            if self.model.flag_repeat:
                self.set_stage(Stage.REPEAT_TEST)

            else:
                if self.model.move_traverse < 10:
                    self.trav_serv.step_traverse_referent_point()

                else:
                    self.trav_serv.traverse_install_point('install')

        else:
            self.signals.control_msg.emit('excess_temperature')
            self.model.flag_reset_stop_test()

    @log_exceptions 
    def stop_test_clicked(self):
        """
        Завершение теста, если определена референтная точка коленвала, то остановка в нижней точке,
        иначе моментальная остановка
        """
        self.model.stop_collect()
        self.model.flag_reset_stop_test()
        self.set_stage(Stage.WAIT)
        self.model.stop_gear_end_test()

    def _dispatch_test_by_type(self):
        type_test = self.model.get_type_test()
        if type_test == TypeTest.CONV:
            self.signals.conv_win_test.emit()
            self.model.flag_test = True
            self.model.test_on_two_speed(1)
        else:
            self.signals.lab_win_test.emit()
            handlers = {
                TypeTest.LAB: lambda: self.model.test_on_two_speed(1),
                TypeTest.LAB_HAND: self.model.test_lab_hand_speed,
                TypeTest.LAB_CASCADE: self._start_cascade_test,
                TypeTest.TEMPER: self._start_temper_test,
            }
            handler = handlers.get(type_test)
            if handler is None:
                self.logger.warning(f'Unknown type test: {type_test.name.lower()}')
                handler = lambda: self.model.test_on_two_speed(1)

            self.model.flag_test = True
            handler()
        
    def _start_cascade_test(self):
        self.model.reset_cascade_speed()
        self.model.test_lab_cascade()
        
    def _start_temper_test(self):
        self.model.reset_last_max_temper()
        self.model.test_temper()

    ##### STAGES #####
    def _enter_wait(self):
        pass

    def _stage_wait(self):
        pass

    def _exit_wait(self):
        pass
    
    #==========

    def _enter_wait_buffer(self):
        self._wait_buf_t0 = time.monotonic()
        self._check_next_stage = False

    def _stage_wait_buffer(self):
        """Блок ожидания включения записи в буфер и переключение на следующий шаг"""
        if self._check_next_stage is True:
            return
        
        if self.model.get_state_cycle_force():
            self._check_next_stage = True
            self.model.reader_start_test()
            self.set_stage(self.next_stage)
            return
        
        timed_out = (time.monotonic() - self._wait_buf_t0) > 1
        res, state = self.model.get_buffer_state()
        if (res == 'ERROR!' and state == 'buffer_on') or timed_out:
            self._wait_buf_t0 = time.monotonic()
            self.model.write_bit_force_cycle(1)

    def _exit_wait_buffer(self):
        pass
    
    #==========

    def _enter_repeat_test(self):
        self.model.flag_repeat = False

    def _stage_repeat_test(self):
        self._dispatch_test_by_type()

    def _exit_repeat_test(self):
        pass
    
    #==========

    # FIXME Проверить этот момент
    def _enter_alarm_traverse(self):
        pass

    def _stage_alarm_traverse(self):
        if self.trav_serv.step_control_traverse_move():
            self.model.write_bit_red_light(0)
            self.alarm_steps.flag_alarm_traverse = False
            self.model.alarm_tag = ''
            self.model.flag_alarm = False
            self.set_stage(Stage.WAIT)

    def _exit_alarm_traverse(self):
        self.signals.reset_ui.emit()

    #==========

    def _enter_traverse_referent(self):
        self.signals.control_msg.emit('traverse_referent')

    def _stage_traverse_referent(self):
        if self.trav_serv.flag_traverse_referent():
            self.trav_serv.traverse_install_point('install')

    def _exit_traverse_referent(self):
        pass
    
    #==========

    def _enter_install_amort(self):
        self.signals.control_msg.emit('pos_traverse')

    def _stage_install_amort(self):
        if self.trav_serv.step_control_traverse_move():
            self.model.flag_test_launch = True
            self.signals.control_msg.emit('yellow_btn')

    def _exit_install_amort(self):
        pass
    
    #==========
    
    def _enter_start_point_amort(self):
        self.signals.control_msg.emit('pos_traverse')

    def _stage_start_point_amort(self):
        if self.trav_serv.step_control_traverse_move():
            self.model.test_move_cycle()

    def _exit_start_point_amort(self):
        pass
    
    #==========
    
    def _enter_test_move_cycle(self):
        self.signals.control_msg.emit('move_detection')
        
    def _stage_test_move_cycle(self):
        if self.model.is_collect_done():
            self.model.stop_collect()
            self.model.pumping()

    def _exit_test_move_cycle(self):
        pass
        
    #==========

    def _enter_pumping(self):
        self.signals.control_msg.emit('pumping')

    def _stage_pumping(self):
        if self.model.is_collect_done():
            self.model.stop_collect()
            self._dispatch_test_by_type()

    def _exit_pumping(self):
        pass
    
    #==========

    def _enter_test_speed_one(self):
        pass

    def _stage_test_speed_one(self):
        if self.model.is_collect_done():
            self.model.stop_collect()
            if self.model.get_type_test() == TypeTest.CONV:
                self.model.result_conveyor_test('one')
            self.model.save_data_test_in_archive()
            self.model.write_end_test_in_archive()
            self.model.test_on_two_speed(2)

    def _exit_test_speed_one(self):
        pass
    
    #==========
    
    def _enter_test_speed_two(self):
        pass

    def _stage_test_speed_two(self):
        if self.model.is_collect_done():
            self.model.stop_collect()
            if self.model.get_type_test() == TypeTest.CONV:
                self.model.result_conveyor_test('two')
            self.model.save_data_test_in_archive()
            self.model.write_end_test_in_archive()
            self.model.stop_gear_end_test()

    def _exit_test_speed_two(self):
        pass
    
    #==========
    
    def _enter_test_lab_hand_speed(self):
        pass

    def _stage_test_lab_hand_speed(self):
        if self.model.is_collect_done():
            self.model.stop_collect()
            self.model.save_data_test_in_archive()
            self.model.write_end_test_in_archive()
            self.model.stop_gear_end_test()

    def _exit_test_lab_hand_speed(self):
        pass
    
    #==========

    def _enter_test_lab_cascade(self):
        pass

    def _stage_test_lab_cascade(self):
        if self.model.is_collect_done():
            self.model.stop_collect()
            self.model.save_data_test_in_archive()
            self.model.set_next_step_count_cascade()
            self.model.test_lab_cascade()
            if self.model.get_flag_cascade_done():
                self.model.write_end_test_in_archive()
                self.model.stop_gear_end_test()

    def _exit_test_lab_cascade(self):
        pass
    
    #==========

    def _enter_test_temper(self):
        pass

    def _stage_test_temper(self):
        if self.model.check_finish_temper_test():
            self.model.save_temper_test_in_archive()
            self.model.stop_cycle_collection()
            self.model.stop_collect()
            self.model.write_end_test_in_archive()
            self.model.stop_gear_end_test()

    def _exit_test_temper(self):
        pass
    
    #==========

    def _enter_stop_gear_end_test(self):
        pass

    def _stage_stop_gear_end_test(self):
        if self.model.is_motor_stopped():
            self.model.stop_collect()
            self.model.stop_gear_min_pos()

    def _exit_stop_gear_end_test(self):
        pass

    #==========
    
    def _enter_stop_gear_min_pos(self):
        pass

    def _stage_stop_gear_min_pos(self):
        if self.model.is_nmt_reached():
            self.model.fc_control(**{'tag': 'stop', 'adr': 1})
            self.model.stop_collect()
            if self.model.flag_test:
                self.model.flag_test = False
            if self.model.flag_search_hod:
                self.model.flag_search_hod = False
                self.signals.search_hod_msg.emit()
            else:
                if self.model.get_type_test() == TypeTest.CONV:
                    self.signals.conv_test_stop.emit()
                else:
                    self.signals.lab_test_stop.emit()
            self.set_stage(Stage.WAIT)

    def _exit_stop_gear_min_pos(self):
        pass

    #==========

    def _enter_stop_test(self):
        if not self.model.flag_alarm:
            self.signals.control_msg.emit('pos_traverse')

    def _stage_stop_test(self):
        if self.trav_serv.step_control_traverse_move():
            if not self.model.flag_alarm:
                self.signals.cancel_test.emit()
            self.set_stage(Stage.WAIT)

    def _exit_stop_test(self):
        pass
    
    #==========

    def _enter_search_hod(self):
        self.signals.control_msg.emit('move_detection')

    def _stage_search_hod(self):
        if self.model.is_collect_done():
            self.model.stop_collect()
            self.model.stop_gear_end_test()

    def _exit_search_hod(self):
        pass
        
    #==========

    def _enter_pos_set_gear(self):
        self.signals.control_msg.emit('gear_set_pos')

    def _stage_pos_set_gear(self):
        if self.model.is_mid_reached():
            self.model.fc_control(**{'tag': 'stop', 'adr': 1})
            self.model.stop_collect()
            self.set_stage(Stage.WAIT)
            self.signals.reset_ui.emit()

    def _exit_pos_set_gear(self):
        pass

    #==========
