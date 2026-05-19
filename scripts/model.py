# -*- coding: utf-8 -*-
import time
import statistics
from PySide6.QtCore import QObject, Signal, QTimer

from config import config
from scripts.logger import my_logger
from scripts.test_obj import DataTest
from scripts.parser.parser import ParserSPG023MK
from scripts.data_calculation import CalcData
from scripts.reader import Reader
from scripts.writer import Writer
from scripts.archive_saver import WriterArch
from scripts.controller.stages import Stage, TypeTest
from scripts.modbus.client import Client
from scripts.freq_ctrl.freq_control import FreqControl

from scripts.controller.cycle_collector import CycleCollector, PhaseState, Mode


class ModelSignals(QObject):
    stbar_msg = Signal(str)

    test_launch = Signal(bool)
    save_koef_force = Signal(str)
    
    connect_ctrl = Signal()
    read_finish = Signal()
    
    win_set_update = Signal(str)
    update_lab_graph = Signal(object)
    update_conv_graph = Signal(object)
    update_temper_graph = Signal(object)
    
    conv_result_lamp = Signal(str, str)
    set_stage = Signal(object)
    set_next_stage = Signal(object)


class Model:
    def __init__(self):
        self._init_variables()
        self._init_flags()

        self._start_param_model()

    def _tune_cycle_collector_for_speed(self):
        """Tune CycleCollector parameters for current speed/stroke.
        At high speeds with short stroke, the half-cycle time can drop below the
        fixed gate (default 0.2s) and the collector starts missing turns, which
        looks like doubled loops on the force-displacement graph.
        """
        try:
            amort = self.data_test.amort
            hod = int(amort.hod) if amort and amort.hod else 120
            speed = float(self.data_test.speed_test) if self.data_test.speed_test else None
            if not speed or speed <= 0:
                return

            freq = self.calc_data.calc_freq_piston_amort(speed, hod)
            if not freq or freq <= 0:
                return

            half_cycle_s = 1.0 / (2.0 * float(freq))
            # Gate must be < real half-cycle; keep reasonable floor/ceiling.
            gate_s = max(0.03, min(0.2, 0.45 * half_cycle_s))
            # Convert time (seconds) to fraction of sample_rate
            sr = float(self.collector.sample_rate)
            if sr > 0:
                gate_fraction = gate_s / sr
                self.collector.min_halfcycle_fraction = gate_fraction

        except Exception as e:
            self.logger.error(e)

    def _init_variables(self):
        self.logger = my_logger.get_logger(__name__)
        self.signals = ModelSignals()
        self.client = Client()
        self.writer: Writer | None = None
        self.reader = Reader()
        self.fc = FreqControl()
        self.parser = ParserSPG023MK()
        self.calc_data = CalcData()
        self.collector = CycleCollector()
        self.data_test = DataTest()
        self.state_dict = {'cycle_force': False,
                           'red_light': False,
                           'green_light': False,
                           'lost_control': True,
                           'excess_force': False,
                           'select_temper': False,
                           'safety_fence': False,
                           'traverse_block': False,
                           'state_freq': False,
                           'state_force': False,
                           'yellow_btn': False,
                           }
        self.switch_dict = {'traverse_block_left': False,
                            'traverse_block_right': False,
                            'alarm_highest_position': True,
                            'alarm_lowest_position': True,
                            'highest_position': False,
                            'lowest_position': False,
                            }
        self.buffer_state = ['null', 'null']

        self.counter = 0
        self.move_now = 0
        self.move_traverse = 0
        self.force_clear = 0
        self.force_correct = 0
        self.force_koef_offset = 0
        self.koef_force_list = []
        self.force_offset = 0
        self.min_point = 0
        self.max_point = 0
        self.stroke = 0

        self.timer_clear_statusbar = None
        self.timer_add_koef = None
        self.timer_calc_koef = None
        self.timer_yellow = None
        self.time_push_yellow = None
        self.state_list = [0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        
        self.list_lab_result = []
        self.list_conv_result = []
        self.count_cascade = 0
        self.max_cascade = 0
        self.last_max_temper = -100

    def _init_flags(self):
        self.lbl_push_force = ''

        self.flag_test = False
        self.flag_test_launch = False
        self.yellow_rattle = False
        self.flag_repeat = False
        self.flag_search_hod = False
        self.flag_cascade_done = False

        self.alarm_tag = ''
        self.flag_alarm = False
        self.flag_non_buffer = False

        self.flag_collect_done = False
        self.flag_collect_error = False
        self.flag_nmt_reached = False
        self.flag_mid_reached = False
        
    def _init_signals(self):
        self.reader.signals.result.connect(self._reader_result)
        self.writer.signals.check_buffer.connect(self.check_buffer_state)
        
    def log_exceptions(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                args[0].logger.error(
                    f'ERROR in {func.__name__}: {e}'
                )
        return wrapper

    @log_exceptions
    def _start_param_model(self):
        self._init_timer_clear_statusbar()
        self.client.connect_client()
        self._init_timer_yellow_btn()

        if self.client.flag_connect:
            self.writer = Writer(self.client.client)
            self.writer.timer_writer_start()

            self.reader.init_reader(self.client.client)
            self._init_signals()
            self.reader_start()

            self.save_arch = WriterArch()
            self.save_arch.timer_writer_arch_start()

        else:
            self.status_bar_msg(f'Нет подключения к контроллеру')
            self.logger.warning(f'Нет подключения к контроллеру')

    def status_bar_msg(self, txt_bar):
        self.signals.stbar_msg.emit(txt_bar)
        self.timer_clear_statusbar.start()
        
    def clear_status_bar(self):
        self.signals.stbar_msg.emit(' ')
        self.timer_clear_statusbar.stop()
        
    def set_type_test(self, type_test: TypeTest):
        self.data_test.type_test = type_test
        
    def get_type_test(self) -> TypeTest:
        return self.data_test.type_test
        
    def set_amort(self, amort):
        self.data_test.amort = amort
        
    def set_speed_test(self, speed: float):
        self.data_test.speed_test = speed
        
    def get_speed_test(self) -> float:
        return self.data_test.speed_test
    
    def get_state_cycle_force(self) -> bool:
        return self.state_dict.get('cycle_force', False)

    def check_buffer_state(self, res, state):
        self.buffer_state = [res, state]
        
    def get_buffer_state(self):
        res = self.buffer_state[0]
        state = self.buffer_state[1]
        return res, state
    
    def reset_buffer_state(self):
        self.buffer_state = ['null', 'null']
        
    def reset_cascade_speed(self):
        self.flag_cascade_done = False
        self.count_cascade = 0
        self.max_cascade = len(self.data_test.speed_list)

    def set_next_step_count_cascade(self):
        self.count_cascade += 1
        
    def get_flag_cascade_done(self):
        return self.flag_cascade_done
    
    def reset_last_max_temper(self):
        self.last_max_temper = -100

    def reader_start(self):
        self.reader.reader_start()
        self.status_bar_msg(f'Чтение контроллера запущено')

    def reader_start_test(self):
        self.reader.reader_start_test()
        self.status_bar_msg(f'Чтение буфера контроллера запущено')

    def reader_stop(self):
        self.reader.reader_stop()
        self.status_bar_msg(f'Чтение контроллера остановлено')

    def reader_stop_test(self):
        self.reader.reader_stop_test()
        self.status_bar_msg(f'Чтение буфера контроллера остановлено')

    def reader_exit(self):
        self.reader.reader_exit()
        
    @log_exceptions
    def _update_switch_dict(self, data):
        if data is not None:
            self.switch_dict.update(data)

    @log_exceptions
    def _update_state_dict(self, data):
        if data is not None:
            self.state_dict.update(data)
            
    def _init_timer_clear_statusbar(self):
        self.timer_clear_statusbar = QTimer()
        self.timer_clear_statusbar.setInterval(2000)
        self.timer_clear_statusbar.timeout.connect(self.clear_status_bar)

    def init_timer_koef_force(self):
        self.write_bit_force_cycle(1)
        self.timer_add_koef = QTimer()
        self.timer_add_koef.setInterval(50)
        self.timer_add_koef.timeout.connect(self._add_koef_force_in_list)
        self.timer_add_koef.start()

        self.timer_calc_koef = QTimer()
        self.timer_calc_koef.setInterval(1000)
        self.timer_calc_koef.timeout.connect(self._calc_and_save_force_koef)
        self.timer_calc_koef.start()

    def _add_koef_force_in_list(self):
        if self.force_clear != -100000.0:
            self.koef_force_list.append(self.force_correct)
        else:
            pass

    @log_exceptions
    def _calc_and_save_force_koef(self):
        self.timer_add_koef.stop()
        self.timer_calc_koef.stop()
        self.write_bit_force_cycle(0)

        if self.koef_force_list:
            self.force_koef_offset = round(statistics.fmean(self.koef_force_list), 1)
            self.koef_force_list.clear()
            self.signals.save_koef_force.emit('done')

        else:
            self.signals.save_koef_force.emit('bad')

    def cancel_koef_force(self):
        self.force_koef_offset = 0
            
    def _init_timer_yellow_btn(self):
        self.timer_yellow = QTimer()
        self.timer_yellow.setInterval(1000)
        self.timer_yellow.timeout.connect(self.yellow_btn_click)

    @log_exceptions
    def yellow_btn_click(self):
        if self.state_dict.get('yellow_btn', False) is True:
            if self.yellow_rattle is False:
                self.time_push_yellow = time.monotonic()
                self.signals.test_launch.emit(True)
                self.yellow_rattle = True
            else:
                time_signal = time.monotonic() - self.time_push_yellow
                if 2 < time_signal:
                    self.time_push_yellow = time.monotonic()
                    self.signals.test_launch.emit(True)
                    self.yellow_rattle = True
                else:
                    pass
        else:
            self.timer_yellow.stop()
            
    def check_max_temper_test(self):
        first = self.data_test.first_temperature
        second = self.data_test.second_temperature
        if self.get_type_test() == TypeTest.TEMPER:
            finish_temp = self.data_test.finish_temperature
        else:
            finish_temp = self.data_test.amort.max_temper
        if first < finish_temp and second < finish_temp:
            return True
        else:
            return False
        
    def is_collect_done(self):
        return self.flag_collect_done

    def stop_cycle_collection(self):
        self.collector.reset_active_collate()
        
    def is_motor_stopped(self):
        return self.collector.motor_stopped()
    
    def reset_nmt(self):
        """Сбросить сохранённую НМТ в коллекторе."""
        self.collector.clear_nmt()

    def is_nmt_reached(self):
        return self.flag_nmt_reached
    
    def is_mid_reached(self):
        return self.flag_mid_reached

    @log_exceptions
    def _reader_result(self, response, tag):
        if tag == 'reg':
            self._pars_regs_result(response.get('regs'))
        else:
            self._pars_buffer_result(response)

        if self.flag_test_launch is True:
            if not self.timer_yellow.isActive():
                self.timer_yellow.start()
            else:
                pass

    @log_exceptions
    def _pars_regs_result(self, res):
        if not res:
            return
        else:
            result = self.parser.pars_response_from_regs(res)
            
            if result.get('force', None) is not None:
                self.force_clear = result.get('force', 0)
                self.force_correct = round(self.force_clear * config.force_koef, 1)
                self.force_offset = round(self.force_correct - self.force_koef_offset, 1)

            self.move_now = result.get('move')
            self.move_traverse = result.get('traverse')
            self.counter = result.get('counter')
            self.data_test.force_alarm = result.get('force_a')

            self.data_test.first_temperature = round(result.get('first_t'), 1)
            self.data_test.second_temperature = round(result.get('second_t'), 1)
            
            self.data_test.temperature = max(
                self.data_test.first_temperature,
                self.data_test.second_temperature
            )

            self.data_test.max_temperature = max(
                self.data_test.max_temperature,
                self.data_test.temperature
            )

            self._update_switch_dict(result.get('switch'))
            self._update_state_dict(result.get('state'))
            self.state_list = result.get('state_list')

            if self.get_type_test() == TypeTest.SETTINGS:
                self.signals.win_set_update.emit('reg')

    @log_exceptions
    def _pars_buffer_result(self, res):
        data = self.parser.pars_response_from_buffer(res)
        if not data:
            if not self.flag_non_buffer:
                self.flag_non_buffer = True
                self.logger.debug('Response from force sensor is None')
        else:
            self.flag_non_buffer = False
            self.state_list = data.get('state_list')
            self._update_state_dict(data.get('state'))
            temperature = data.get('temper')
            self.data_test.temperature = temperature
            self.data_test.max_temperature = self.calc_data.check_temperature(temperature,
                                                                              self.data_test.max_temperature)
            if self.get_type_test() == TypeTest.SETTINGS:
                self._send_data_in_set_win(data)
            else:
                event_state = self.collector.add_stream_dict(data)
                if event_state == PhaseState.DONE and not self.flag_collect_done:
                    self._handle_program_done()
                elif event_state == PhaseState.ERROR and not self.flag_collect_error:
                    self.flag_collect_error = True
                    self.logger.error('Error in collector/add_stream_dict')

    def _handle_program_done(self):
        step = self.collector.get_last_completed_step()
        result = self.collector.get_last_step_result()
        if step is None:
            return
        mode, _ = step
        if mode == Mode.STROKE_ONLY:
            self.min_point, self.max_point, self.stroke = result[0]
        elif mode == Mode.COLLECT:
            avg = self.calc_data.average_cycles(result)
            self._pars_result_avarage_cycles(avg)
        elif mode == Mode.NMT_FINAL:
            self.flag_nmt_reached = True
        elif mode == Mode.MID_FINAL:
            self.flag_mid_reached = True
        self.flag_collect_done = True
        
    def start_collect(self, with_data: bool, *, count_det: int=2, count_col: int=1):
        self.flag_collect_done = False
        self.flag_collect_error = False
        self.flag_nmt_reached = False
        if with_data:
            self.collector.load_program([
            (Mode.DETECT_ONLY, count_det),
            (Mode.COLLECT, count_col),
            ], skip_accel=True)
        else:
            self.collector.load_program([(Mode.DETECT_ONLY, count_det)], skip_accel=True)
        
    def start_collect_inf_cycle(self):
        self.flag_collect_done = False
        self.flag_collect_error = False
        self.flag_nmt_reached = False
        self.collector.load_program([(Mode.COLLECT, None)], skip_accel=False)
        self.collector.set_cycle_callback(self._pars_result_inf_cycles)
        
    def start_collect_wait_stop(self):
        self.flag_collect_done = False
        self.flag_collect_error = False
        self.flag_nmt_reached = False
        self.collector.load_program([(Mode.WAIT_STOP, None)], skip_accel=True)
        
    def start_find_stroke(self, count_str: int=2):
        self.min_point = 0
        self.max_point = 0
        self.stroke = 0
        self.flag_collect_done = False
        self.flag_collect_error = False
        self.flag_nmt_reached = False
        self.reset_nmt()
        self.collector.load_program([(Mode.STROKE_ONLY, count_str)], skip_accel=True)
        
    def start_nmt_position(self, *, tolerance_mm: float = 1.0, confirm_points: int = 2):
        self.flag_collect_done = False
        self.flag_collect_error = False
        self.flag_nmt_reached = False
        self.collector.set_nmt_params(tolerance=tolerance_mm, confirm_points=confirm_points)
        self.collector.load_program([(Mode.NMT_FINAL, None)], skip_accel=True, preserve_nmt=True)

    def start_mid_position(self, *, tolerance_mm: float = 2.0, confirm_points: int = 2):
        self.flag_collect_done = False
        self.flag_collect_error = False
        self.flag_mid_reached = False
        self.collector.set_mid_params(tolerance=tolerance_mm, confirm_points=confirm_points)
        self.collector.load_program([(Mode.MID_FINAL, None)], skip_accel=True, preserve_nmt=True)
        
    def stop_collect(self):
        self.reader_stop_test()
        self.write_bit_force_cycle(0)

    @log_exceptions
    def _send_data_in_set_win(self, data):
        self.force_clear = data.get('force')[-1]
        self.force_correct = round(self.force_clear * config.force_koef, 1)
        self.force_offset = round(self.force_correct - self.force_koef_offset, 1)

        self.move_now = data.get('move')[-1]
        self.counter = data.get('count')[-1]
        self.data_test.first_temperature = self.data_test.temperature

        self.signals.win_set_update.emit('buf')
            
    def _pars_result_inf_cycles(self, result):
        if self.get_type_test() == TypeTest.TEMPER:
            self._pars_result_temper_test(result)

    def _pars_result_avarage_cycles(self, avg):
        if self.get_type_test() == TypeTest.CONV:
            self._pars_result_conv_test(avg)
        
        elif self.get_type_test() == TypeTest.TEMPER:
            pass
            
        else:
            self._pars_result_lab_test(avg)

    @log_exceptions
    def _calc_result_cycle(self, move, force):
        if self.get_type_test() == TypeTest.TEMPER:
            comp_clear, rec_clear = self.calc_data.middle_min_and_max_force(force)
        else:
            rec_clear, comp_clear = self.calc_data.middle_min_and_max_force(force)
        if self.data_test.flag_push_force:
            push_force = self.calc_data.calc_dynamic_push_force_array(move, force,
                                                                    self.data_test.static_push_force)
            self.data_test.dynamic_push_force = push_force
        else:
            push_force = self.data_test.static_push_force
            self.data_test.dynamic_push_force = 0
        
        self.data_test.max_recoil = abs(round(rec_clear + push_force, 2))
        self.data_test.max_comp = abs(round(comp_clear + push_force, 2))

        self.data_test.power_amort = self.calc_data.calc_power_amort_array(move, force)
        
        self.data_test.freq_piston = self.calc_data.calc_freq_piston_amort(self.get_speed_test(),
                                                                          self.data_test.amort.hod)
    
    @log_exceptions
    def _pars_result_lab_test(self, avg):
        self.data_test.move = avg[0]
        self.data_test.force = self.calc_data.correct_force_with_koef(avg[1],
                                                                      config.force_koef,
                                                                      self.force_koef_offset)
        data_dict = {'speed': self.get_speed_test(),
                     'move': self.data_test.move[:],
                     'force': self.data_test.force[:]}
        self.list_lab_result.append((data_dict))
        self._calc_result_cycle(self.data_test.move, self.data_test.force)

        self.signals.update_lab_graph.emit(avg)
    
    @log_exceptions
    def _pars_result_conv_test(self, avg):
        self.data_test.move = avg[0]
        self.data_test.force = self.calc_data.correct_force_with_koef(avg[1],
                                                                      config.force_koef,
                                                                      self.force_koef_offset)
        data_dict = {'speed': self.get_speed_test(),
                     'move': self.data_test.move[:],
                     'force': self.data_test.force[:]}
        self.list_conv_result.append((data_dict))
        self._calc_result_cycle(self.data_test.move, self.data_test.force)

        self.signals.update_conv_graph.emit(avg)
        
    @log_exceptions
    def _pars_result_temper_test(self, result):
        move = result[0]
        force = self.calc_data.correct_force_with_koef(result[1],
                                                       config.force_koef,
                                                       self.force_koef_offset)
        self._calc_result_cycle(move, force)
        
        t = round(float(self.data_test.max_temperature), 1)

        if self.data_test.temper_list and abs(t - self.data_test.temper_list[-1]) < 1e-9:
            # температура та же — обновляем последнюю точку
            self.data_test.recoil_list[-1] = self.data_test.max_recoil
            self.data_test.comp_list[-1] = self.data_test.max_comp
            self.data_test.temper_list[-1] = t
        else:
            # новая температура — добавляем точку
            self.data_test.recoil_list.append(self.data_test.max_recoil)
            self.data_test.comp_list.append(self.data_test.max_comp)
            self.data_test.temper_list.append(t)
            
        self.signals.update_temper_graph.emit((self.data_test.recoil_list,
                                               self.data_test.comp_list,
                                               self.data_test.temper_list))
        
    @log_exceptions
    def _write_reg_state(self, bit, value, command=None):
        com_list = self.state_list[:]
        com_list[bit] = value

        res = 0

        for i in range(16):
            res = res + com_list[i] * 2 ** i

        self.writer.write_out('reg',
                                values=[res],
                                reg_write=0x2003,
                                command=command)

    @log_exceptions
    def write_bit_force_cycle(self, value):
        self.reset_buffer_state()
        if value == 1:
            command = 'buffer_on'
        else:
            command = 'buffer_off'

        self._write_reg_state(0, value, command)

    @log_exceptions
    def write_bit_red_light(self, value):
        bit = self.state_dict.get('red_light', 0)
        if int(bit) != value:
            self._write_reg_state(1, value, command='red_light')

    @log_exceptions
    def write_bit_green_light(self, value):
        bit = self.state_dict.get('green_light', 0)
        if int(bit) != value:
            self._write_reg_state(2, value, command='green_light')

    @log_exceptions
    def write_bit_unblock_control(self):
        self._write_reg_state(3, 1, command='unblock_control')

    @log_exceptions
    def write_bit_emergency_force(self):
        self._write_reg_state(4, 1, command='reset_emergency_force')

    @log_exceptions
    def write_bit_select_temper(self, value):
        bit = self.state_dict.get('select_temper', 0)
        if int(bit) != value:
            self._write_reg_state(6, value, command='select_temper')

    @log_exceptions
    def write_emergency_force(self, value):
        arr = self.calc_data.emergency_force(value)
        self.writer.write_out('reg', values=arr, reg_write=0x200a)
    
    @log_exceptions
    def fc_control(self, tag: str, adr: int, speed: float = None, freq: int = None, hod: int = None):
        if self.state_dict.get('lost_control'):
            self.write_bit_unblock_control()

        if self.state_dict.get('excess_force'):
            self.write_bit_emergency_force()
            
        if hod is None:
            if self.data_test.amort is None:
                hod = 120
            else:
                hod = self.data_test.amort.hod
            
        values, comm = self.fc.freq_command(tag, adr, speed, freq, hod)
        self.writer.write_out('FC', freq_command=values, command=comm)

    @log_exceptions
    def lamp_all_switch_on(self):
        """Включение всех индикаторов"""
        self.write_bit_green_light(1)
        QTimer.singleShot(100, lambda: self.write_bit_red_light(1))

    @log_exceptions
    def lamp_all_switch_off(self):
        """Выключение всех индикаторов"""
        self.write_bit_green_light(0)
        QTimer.singleShot(100, lambda: self.write_bit_red_light(0))

    @log_exceptions
    def lamp_green_switch_on(self):
        """Включение зелёного индикатора"""
        self.write_bit_green_light(1)
        QTimer.singleShot(100, lambda: self.write_bit_red_light(0))

    @log_exceptions
    def lamp_red_switch_on(self):
        """Включение красного индикатора"""
        self.write_bit_green_light(0)
        QTimer.singleShot(100, lambda: self.write_bit_red_light(1))
            
    @log_exceptions
    def result_conveyor_test(self, step):
        """Включение индикаторов, зелёный - в допусках, красный - нет"""
        amort = self.data_test.amort
        min_comp, max_comp = 0, 2000
        min_recoil, max_recoil = 0, 2000
        if step == 'one':
            min_comp, max_comp = amort.min_comp, amort.max_comp
            min_recoil, max_recoil = amort.min_recoil, amort.max_recoil
        elif step == 'two':
            min_comp, max_comp = amort.min_comp_2, amort.max_comp_2
            min_recoil, max_recoil = amort.min_recoil_2, amort.max_recoil_2
            
        if min_comp < self.data_test.max_comp < max_comp and min_recoil < self.data_test.max_recoil < max_recoil:
            self.lamp_green_switch_on()
            self.signals.conv_result_lamp.emit(step, 'green')
        else:
            self.lamp_red_switch_on()
            self.signals.conv_result_lamp.emit(step, 'red')
            
    def work_interrupted_operator(self):
        self.signals.set_stage.emit(Stage.WAIT)
        self.lamp_all_switch_off()
        if self.client.flag_connect:
            self.fc_control(**{'tag': 'stop', 'adr': 1})
            self.fc_control(**{'tag': 'stop', 'adr': 2})
            self.stop_collect()
        self.flag_test_launch = False
        if self.flag_test:
            self.flag_test = False
            if self.get_type_test() == TypeTest.LAB_CASCADE:
                self.write_end_test_in_archive()
    
    @log_exceptions
    def flag_reset_start_test(self):
        if self.state_dict.get('excess_force', False) is True:
            self.write_bit_emergency_force()
        if self.state_dict.get('lost_control', False) is True:
            self.write_bit_unblock_control()
        self.lamp_all_switch_off()
        self.data_test.max_temperature = 0
        self.alarm_tag = ''
        self.flag_alarm = False
            
    def flag_reset_stop_test(self):
        self.flag_test_launch = False
        self.flag_test = False

    def write_emergency_force_start_test(self):
        self.write_emergency_force(self.calc_data.excess_force(self.data_test.amort))

    def transition_via_buffer(
        self,
        next_stage: Stage,
        *,
        speed=None,
        adr=1,
        force_cycle=True,
        extra_fc=None
    ):
        """
        Унифицированный переход через WAIT_BUFFER.
        Parameters
        ----------
        next_stage : Stage
            Куда перейти после buffer_on
        speed : int | None
            Если задан — отправим fc_control speed
        adr : int
            Адрес привода
        force_cycle : bool
            Нужно ли включать force_cycle
        extra_fc : dict | None
            Любая дополнительная команда fc_control
        """
        if speed is not None:
            self.fc_control(tag='speed', adr=adr, speed=speed)
        if extra_fc:
            self.fc_control(**extra_fc)
        if force_cycle:
            self.write_bit_force_cycle(1)

        self.signals.set_next_stage.emit(next_stage)
        self.signals.set_stage.emit(Stage.WAIT_BUFFER)
        
    def test_move_cycle(self):
        self.reset_nmt()
        self.start_collect(with_data=False, count_det=2)
        hod = self.data_test.amort.hod if self.data_test.amort else 120
        speed = self.calc_data.definition_speed_by_hod('slow', hod)
        self.transition_via_buffer(Stage.TEST_MOVE_CYCLE, speed=speed,
                                   extra_fc={'tag': 'up', 'adr': 1})
        
    def pumping(self):
        self.start_collect(with_data=False, count_det=3)
        hod = self.data_test.amort.hod if self.data_test.amort else 120
        speed = self.calc_data.definition_speed_by_hod('fast', hod)
        self.transition_via_buffer(Stage.PUMPING, speed=speed,
                                   extra_fc={'tag': 'up', 'adr': 1})
    
    def test_on_two_speed(self, ind: int):
        if ind == 1:
            self.start_collect(with_data=True, count_col=3)
            speed = self.data_test.amort.speed_one
            self.set_speed_test(speed)
            self._tune_cycle_collector_for_speed()
            self.transition_via_buffer(Stage.TEST_SPEED_ONE, speed=speed,
                                       extra_fc={'tag': 'up', 'adr': 1})

        elif ind == 2:
            self.start_collect(with_data=True, count_col=3)
            speed = self.data_test.amort.speed_two
            self.set_speed_test(speed)
            self._tune_cycle_collector_for_speed()
            self.transition_via_buffer(Stage.TEST_SPEED_TWO, speed=speed,
                                       extra_fc={'tag': 'up', 'adr': 1})
    
    def test_lab_hand_speed(self):
        self.start_collect(with_data=True, count_col=3)
        speed = self.get_speed_test()
        self._tune_cycle_collector_for_speed()
        self.transition_via_buffer(Stage.TEST_LAB_HAND_SPEED, speed=speed,
                                   extra_fc={'tag': 'up', 'adr': 1})
    
    def test_lab_cascade(self):
        if self.count_cascade < self.max_cascade:
            self.flag_cascade_done = False
            self.start_collect(with_data=True, count_col=3)
            speed = self.data_test.speed_list[self.count_cascade]
            self.set_speed_test(speed)  
            self._tune_cycle_collector_for_speed()
            self.transition_via_buffer(Stage.TEST_LAB_CASCADE, speed=speed,
                                       extra_fc={'tag': 'up', 'adr': 1})
        
        else:
            self.flag_cascade_done = True

    def test_temper(self):
        self.start_collect_inf_cycle()
        speed = self.get_speed_test()
        self._tune_cycle_collector_for_speed()
        self.transition_via_buffer(Stage.TEST_TEMPER, speed=speed,
                                   extra_fc={'tag': 'up', 'adr': 1})
    
    def check_finish_temper_test(self):
        if self.data_test.max_temperature != self.last_max_temper:
            self.last_max_temper = self.data_test.max_temperature
            if self.data_test.max_temperature <= self.data_test.finish_temperature:
                return False
            else:
                return True

    def stop_gear_end_test(self):
        self.start_collect_wait_stop()
        self.transition_via_buffer(Stage.STOP_GEAR_END_TEST, extra_fc={'tag': 'stop', 'adr': 1})

    def stop_gear_min_pos(self):
        self.start_nmt_position()
        hod = self.data_test.amort.hod if self.data_test.amort else 120
        speed = self.calc_data.definition_speed_by_hod('slow', hod)
        self.transition_via_buffer(Stage.STOP_GEAR_MIN_POS, speed=speed,
                                   extra_fc={'tag': 'up', 'adr': 1})
        
    def search_hod(self):
        self.alarm_tag = ''
        self.flag_alarm = False
        self.flag_search_hod = True
        
        self.start_find_stroke()
        hod = self.data_test.amort.hod if self.data_test.amort else 120
        speed = self.calc_data.definition_speed_by_hod('fast', hod)
        self.transition_via_buffer(Stage.SEARCH_HOD, speed=speed,
                                   extra_fc={'tag': 'up', 'adr': 1})
        
    def move_gear_set_pos(self):
        self.start_mid_position()
        hod = self.data_test.amort.hod if self.data_test.amort else 120
        speed = self.calc_data.definition_speed_by_hod('slow', hod)
        self.transition_via_buffer(Stage.POS_SET_GEAR, speed=speed,
                                   extra_fc={'tag': 'up', 'adr': 1})

    def write_data_in_archive(self, tag, data=None):
        self.save_arch.write_arch_out(tag, data)
        
    @log_exceptions
    def save_data_test_in_archive(self):
        type_test = self.get_type_test()
        data_dict = {'move_graph': list(self.data_test.move),
                     'force_graph': list(self.data_test.force),
                     'type_test': type_test.name.lower(),
                     'speed': self.get_speed_test(),
                     'operator_name': self.data_test.operator.name,
                     'operator_rank': self.data_test.operator.rank,
                     'serial': self.data_test.serial,
                     'amort': self.data_test.amort,
                     'flag_push_force': int(self.data_test.flag_push_force),
                     'static_push_force': self.data_test.static_push_force,
                     'dynamic_push_force': self.data_test.dynamic_push_force,
                     'max_temperature': self.data_test.max_temperature,
                    }
        self.write_data_in_archive('data', data_dict)
    
    @log_exceptions
    def save_temper_test_in_archive(self):
        data_dict = {'temper_graph': self.data_test.temper_list[:],
                     'temper_recoil_graph': self.data_test.recoil_list[:],
                     'temper_comp_graph': self.data_test.comp_list[:],
                     'type_test': 'temper',
                     'speed': self.get_speed_test(),
                     'operator_name': self.data_test.operator.name,
                     'operator_rank': self.data_test.operator.rank,
                     'serial': self.data_test.serial,
                     'amort': self.data_test.amort,
                     'flag_push_force': int(self.data_test.flag_push_force),
                     'static_push_force': self.data_test.static_push_force,
                     'dynamic_push_force': self.data_test.dynamic_push_force,
                     'max_temperature': self.data_test.max_temperature,
                    }
        self.write_data_in_archive('data', data_dict)

    def write_end_test_in_archive(self):
        self.write_data_in_archive('end_test')
