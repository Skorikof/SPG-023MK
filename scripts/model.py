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
from scripts.modbus.client import Client
from scripts.freq_ctrl.freq_control import FreqControl

from scripts.controller.cycle_collector import CycleCollector, PhaseState, Mode


class ModelSignals(QObject):
    stbar_msg = Signal(str)

    test_launch = Signal(bool)
    save_koef_force = Signal(str)
    
    connect_ctrl = Signal()
    read_finish = Signal()
    
    collect_done = Signal(bool)
    win_set_update = Signal(str)
    update_lab_graph = Signal(object)
    update_conv_graph = Signal(object)
    update_temper_graph = Signal(object)
    
    conv_result_lamp = Signal(str, str)


class Model:
    def __init__(self):
        self._init_variables()
        self._init_flags()

        self._start_param_model()

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
        
        # self.list_lab_result = []

    def _init_flags(self):
        self.lbl_push_force = ''

        self.flag_test = False
        self.flag_test_launch = False
        self.yellow_rattle = False
        self.flag_repeat = False
        self.flag_search_hod = False

        self.alarm_tag = ''
        self.flag_alarm = False
        self.flag_non_buffer = False

        self.flag_collect_done = False
        self.flag_collect_error = False
        
    def _init_signals(self):
        self.reader.signals.result.connect(self._reader_result)
        self.reader.signals.error.connect(self.log_error_thread)
        self.writer.signals.check_buffer.connect(self.check_buffer_state)

    def _start_param_model(self):
        try:
            self.init_timer_clear_statusbar()
            self.client.connect_client()
            # FIXME таймер жёлтой кнопки
            # self._init_timer_yellow_btn()

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
                
        except Exception as e:
            self.logger.error(e)

    def status_bar_msg(self, txt_bar):
        self.signals.stbar_msg.emit(txt_bar)
        self.timer_clear_statusbar.start()
        
    def clear_status_bar(self):
        self.signals.stbar_msg.emit(' ')
        self.timer_clear_statusbar.stop()

    def log_error_thread(self, txt_log):
        self.logger.error(txt_log)
        self.status_bar_msg(txt_log)

    def check_buffer_state(self, res, state):
        self.buffer_state = [res, state]

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
        
    def _update_switch_dict(self, data):
        try:
            if data is not None:
                self.switch_dict.update(data)

        except Exception as e:
            self.logger.error(e)

    def _update_state_dict(self, data):
        try:
            if data is not None:
                self.state_dict.update(data)

        except Exception as e:
            self.logger.error(e)
            
    def init_timer_clear_statusbar(self):
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

    def _calc_and_save_force_koef(self):
        try:
            self.timer_add_koef.stop()
            self.timer_calc_koef.stop()
            self.write_bit_force_cycle(0)

            if self.koef_force_list:
                self.force_koef_offset = round(statistics.fmean(self.koef_force_list), 1)
                self.koef_force_list.clear()
                self.signals.save_koef_force.emit('done')

            else:
                self.signals.save_koef_force.emit('bad')

        except Exception as e:
            self.logger.error(e)

    def cancel_koef_force(self):
        try:
            self.force_koef_offset = 0

        except Exception as e:
            self.logger.error(e)
            
    def _init_timer_yellow_btn(self):
        try:
            self.timer_yellow = QTimer()
            self.timer_yellow.setInterval(1000)
            self.timer_yellow.timeout.connect(self.yellow_btn_click)

        except Exception as e:
            self.logger.error(e)

    def yellow_btn_click(self):
        try:
            if self.state_dict.get('yellow_btn', True) is False:
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

        except Exception as e:
            self.logger.error(e)

    def _reader_result(self, response, tag):
        try:
            if tag == 'reg':
                self._pars_regs_result(response.get('regs'))
            else:
                self._pars_buffer_result(response)

            # FIXME при включении проскакивает шум с жёлтой кнопки и отрубается испытание
            # if self.flag_test_launch is True:
            #     if not self.timer_yellow.isActive():
            #         self.timer_yellow.start()
            #     else:
            #         pass

        except Exception as e:
            self.logger.error(e)

    def _pars_regs_result(self, res):
        try:
            if not res:
                pass
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

                self.data_test.first_temperature = result.get('first_t')
                self.data_test.second_temperature = result.get('second_t')
                
                self.data_test.temperature = max(
                    self.data_test.first_temperature,
                    self.data_test.second_temperature
                )

                self.data_test.max_temperature = max(
                    self.data_test.max_temperature,
                    self.data_test.temperature
                )

                # FIXME Пока отключено, так как у макета нет концевиков траверсы
                # self._update_switch_dict(result.get('switch'))
                self._update_state_dict(result.get('state'))
                self.state_list = result.get('state_list')

                if self.data_test.type_test == 'hand':
                    self.signals.win_set_update.emit('reg')

        except Exception as e:
            self.logger.error(e)

    # FIXME Тестирую чтение буфера
    def _pars_buffer_result(self, res):
        try:
            data = self.parser.pars_response_from_buffer(res)
            if data is None:
                if not self.flag_non_buffer:
                    self.flag_non_buffer = True
                    self.logger.debug('Response from force sensor is None')
            else:
                self.flag_non_buffer = False
                if self.data_test.type_test == 'hand':
                    self._send_data_in_set_win(data)
                else:
                    state = self.collector.add_stream_dict(data)
                    if state == PhaseState.DONE and not self.flag_collect_done:
                        self.flag_collect_done = True
                        self.signals.collect_done.emit(True)
                        if Mode.STROKE_ONLY:
                            cycles = self.collector.get_cycles()
                            self.min_point, self.max_point, self.stroke = cycles[0]
                        elif Mode.COLLECT:
                            cycles = self.collector.get_cycles()
                            avg = self.calc_data.average_cycles(cycles) # возвращает список с 2 массивами - pos, force
                            self._pars_result_avarage_cycles(avg)
                    elif state == PhaseState.ERROR and not self.flag_collect_error:
                        self.flag_collect_error = True
                        txt = 'Error in collector/add_stream_dict'
                        self.logger.error(txt)

        except Exception as e:
            self.logger.error(e)
                
    def run_collector_without_data(self, count_det: int=1):
        try:
            self.flag_collect_done = False
            self.flag_collect_error = False
            self.collector.load_program([
                (Mode.DETECT_ONLY, count_det),
            ])
            
        except Exception as e:
            self.logger.error(e)
            
    def run_collector_with_data(self, count_det: int=1, count_col: int=1):
        try:
            self.flag_collect_done = False
            self.flag_collect_error = False
            self.collector.load_program([
                (Mode.DETECT_ONLY, count_det),
                (Mode.COLLECT, count_col),
            ])
            
        except Exception as e:
            self.logger.error(e)
            
    def run_collector_find_stroke(self, count_str: int=1):
        try:
            self.min_point = 0
            self.max_point = 0
            self.stroke = 0
            self.flag_collect_done = False
            self.flag_collect_error = False
            self.collector.load_program([
                (Mode.STROKE_ONLY, count_str),
            ])

        except Exception as e:
            self.logger.error(e)
            
    def run_collector_find_nmt(self):
        try:
            self.flag_collect_done = False
            self.flag_collect_error = False
            self.collector.load_program([
                (Mode.NMT_CAPTURE, 1),      # 1 оборот для захвата НМТ на скорости
                (Mode.NMT_FINAL, 1),        # Режим доворота до НМТ
            ])

        except Exception as e:
            self.logger.error(e)

    def _send_data_in_set_win(self, data):
        try:
            self.force_clear = data.get('force')[-1]
            self.force_correct = round(self.force_clear * config.force_koef, 1)
            self.force_offset = round(self.force_correct - self.force_koef_offset, 1)

            self.move_now = data.get('move')[-1]
            self.counter = data.get('count')[-1]
            self.state_list = data.get('state_list')
            self._update_state_dict(data.get('state'))

            self.signals.win_set_update.emit('buf')
            
        except Exception as e:
            self.logger.error(e)

    def _pars_result_avarage_cycles(self, avg):
        if self.data_test.type_test == 'conv':
            self._pars_relust_conv_test(avg)
        
        elif self.data_test.type_test == 'temper':
            self._pars_result_temper_test(avg)
            
        else:
            self._pars_result_lab_test(avg)
            
    def _pars_result_lab_test(self, avg):
        self.signals.update_lab_graph.emit(avg)
            
    def _pars_relust_conv_test(self, avg):
        self.signals.update_conv_graph.emit(avg)
        
    def _pars_result_temper_test(self, avg):
        self.signals.update_temper_graph.emit(avg)
        
    def _write_reg_state(self, bit, value, command=None):
        try:
            com_list = self.state_list[:]
            com_list[bit] = value

            res = 0

            for i in range(16):
                res = res + com_list[i] * 2 ** i

            self.writer.write_out('reg',
                                  values=[res],
                                  reg_write=0x2003,
                                  command=command)

        except Exception as e:
            self.logger.error(e)

    def write_bit_force_cycle(self, value):
        try:
            self.buffer_state = ['null', 'null']
            if value == 1:
                command = 'buffer_on'
            else:
                command = 'buffer_off'

            self._write_reg_state(0, value, command)

        except Exception as e:
            self.logger.error(e)

    def write_bit_red_light(self, value):
        try:
            bit = self.state_dict.get('red_light', 0)
            if int(bit) != value:
                self._write_reg_state(1, value, command='red_light')
        except Exception as e:
            self.logger.error(e)

    def write_bit_green_light(self, value):
        try:
            bit = self.state_dict.get('green_light', 0)
            if int(bit) != value:
                self._write_reg_state(2, value, command='green_light')

        except Exception as e:
            self.logger.error(e)

    def write_bit_unblock_control(self):
        try:
            self._write_reg_state(3, 1, command='unblock_control')

        except Exception as e:
            self.logger.error(e)

    def write_bit_emergency_force(self):
        try:
            self._write_reg_state(4, 1, command='reset_emergency_force')

        except Exception as e:
            self.logger.error(e)

    def write_bit_select_temper(self, value):
        try:
            bit = self.state_dict.get('select_temper', 0)
            if int(bit) != value:
                self._write_reg_state(6, value, command='select_temper')

        except Exception as e:
            self.logger.error(e)

    def write_emergency_force(self, value):
        try:
            arr = self.calc_data.emergency_force(value)

            self.writer.write_out('reg', values=arr, reg_write=0x200a)

        except Exception as e:
            self.logger.error(e)
            
    def fc_control(self, tag: str, adr: int, speed: float = None, freq: int = None, hod: int = None):
        try:
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
            
        except Exception as e:
            self.logger.error(e)

    def lamp_all_switch_on(self):
        """Включение всех индикаторов"""
        try:
            self.write_bit_green_light(1)
            time.sleep(0.1)
            self.write_bit_red_light(1)

        except Exception as e:
            self.logger.error(e)

    def lamp_all_switch_off(self):
        """Выключение всех индикаторов"""
        try:
            self.write_bit_green_light(0)
            time.sleep(0.1)
            self.write_bit_red_light(0)

        except Exception as e:
            self.logger.error(e)

    def lamp_green_switch_on(self):
        """Включение зелёного индикатора"""
        try:
            self.write_bit_green_light(1)
            time.sleep(0.1)
            self.write_bit_red_light(0)

        except Exception as e:
            self.logger.error(e)

    def lamp_red_switch_on(self):
        """Включение красного индикатора"""
        try:
            self.write_bit_green_light(0)
            time.sleep(0.1)
            self.write_bit_red_light(1)

        except Exception as e:
            self.logger.error(e)
            
    def result_conveyor_test(self, step):
        """Включение индикаторов, зелёный - в допусках, красный - нет"""
        try:
            amort = self.data_test.amort
            min_comp, max_comp = 0, 2000
            min_recoil, max_recoil = 0, 2000

            if step == 'one':
                min_comp, max_comp = amort.min_comp, amort.max_comp
                min_recoil, max_recoil = amort.min_recoil, amort.max_recoil

            elif step == 'two':
                min_comp, max_comp = amort.min_comp_2, amort.max_comp_2
                min_recoil, max_recoil = amort.min_recoil_2, amort.max_recoil_2

            if min_comp < self.max_comp < max_comp and min_recoil < self.max_recoil < max_recoil:
                self.lamp_green_switch_on()
                self.signals.conv_result_lamp.emit(step, 'green')

            else:
                self.lamp_red_switch_on()
                self.signals.conv_result_lamp.emit(step, 'red')

        except Exception as e:
            self.logger.error(e)
            
    def save_result_cycle(self):
        try:
            pass
            # if not self.move or not self.force:
            #     pass
            # else:
            #     type_test = self.data_test.type_test
            #     if type_test == 'lab' or type_test == 'lab_cascade' or type_test == 'conv':
            #         data_dict = {'speed': self.data_test.speed_test,
            #                      'move': self.move[:],
            #                      'force': self.force[:]}

            #         self.list_lab_result.append(data_dict)
                        
            #     self.save_data_in_archive()
                    
        except Exception as e:
            self.logger.error(e)
            
    def write_data_in_archive(self, tag, data=None):
        try:
            self.save_arch.write_arch_out(tag, data)
            
        except Exception as e:
            self.logger.error(e)
            
    def save_data_in_archive(self):
        try:
            pass
            # data_dict = {'move_graph': self.move[:],
            #              'force_graph': self.force[:],
            #              'temper_graph': self.temper_graph[:],
            #              'temper_recoil_graph': self.temper_recoil_graph[:],
            #              'temper_comp_graph': self.temper_comp_graph[:],
            #              'type_test': self.data_test.type_test,
            #              'speed': self.data_test.speed_test,
            #              'operator_name': self.data_test.operator.name,
            #              'operator_rank': self.data_test.operator.rank,
            #              'serial': self.data_test.serial,
            #              'amort': self.data_test.amort,
            #              'flag_push_force': int(self.data_test.flag_push_force),
            #              'static_push_force': self.data_test.static_push_force,
            #              'dynamic_push_force': self.dynamic_push_force,
            #              'max_temperature': self.data_test.max_temperature}
            
            # self.write_data_in_archive('data', data_dict)

        except Exception as e:
            self.logger.error(e)
            
    def write_end_test_in_archive(self):
        try:
            pass
            # self.write_data_in_archive('end_test')

        except Exception as e:
            self.logger.error(e)
