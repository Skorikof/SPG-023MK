# -*- coding: utf-8 -*-
import time
import statistics
import modbus_tk.defines as cst
from PySide6.QtCore import QObject, QThreadPool, Signal, QTimer

from logger import my_logger
from test_obj import OperatorSchema
from my_thread.thread_reader import Reader
from settings.settings import PrgSettings
from my_parser.parser import ParserSPG023MK
from calc_data.data_calculation import CalcData
from writer.writer import Writer
from archive_saver import WriterArch
from connect.client import Client
from freq_control.freq_control import FreqControl


class ModelSignals(QObject):
    stbar_msg = Signal(str)
    read_start = Signal()
    start_test = Signal()
    stop_test = Signal()
    read_stop = Signal()
    read_exit = Signal()

    win_set_update = Signal()
    full_cycle_count = Signal(str)
    update_data_graph = Signal()
    test_launch = Signal(bool)
    save_koef_force = Signal(str)

    connect_ctrl = Signal()
    read_finish = Signal()


class Model:
    def __init__(self):
        self.signals = ModelSignals()
        self.threadpool = QThreadPool()

        self.logger = my_logger.get_logger(__name__)
        self.fc = FreqControl()
        self.parser = ParserSPG023MK()
        self.calc_data = CalcData()
        self.client = Client()

        self._init_varibles()
        self._init_flags()

        self._start_param_model()

    def _init_varibles(self):
        self.operator = OperatorSchema(name='', rank='')
        self.state_dict = {}
        self.switch_dict = {}

        self.reader = None
        self.writer = None
        self.serial_number = ''
        self.amort = None
        self.buffer_state = ['null', 'null']

        self.force_list = []
        self.move_list = []
        self.force = []
        self.move = []
        self.temper_graph = []
        self.temper_recoil_graph = []
        self.temper_comp_graph = []

        self.force_koef = PrgSettings().force_koef
        self.force_clear = 0
        self.force_correct = 0
        self.force_koef_offset = 0
        self.force_offset = 0

        self.counter = 0
        self.move_now = 0
        self.move_traverse = 0
        self.hod_measure = 0
        self.min_point = 0
        self.max_point = 0
        self.start_direction = False
        self.current_direction = False

        self.force_alarm = 0
        self.temper_first = 0
        self.temper_second = 0
        self.temper_max = 0
        self.temper_now = 0

        self.koef_force_list = []
        self.timer_add_koef = None
        self.timer_calc_koef = None

        self.finish_temper = PrgSettings().finish_temper
        self.timer_yellow = None
        self.time_push_yellow = None

        self.state_list = [0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        self.static_push_force = 0
        self.dynamic_push_force = 0
        self.max_recoil = 0
        self.max_comp = 0

        self.speed_test = 0
        self.speed_cascade = []
        self.power_amort = 0
        self.freq_piston = 0

    def _init_flags(self):
        self.flag_push_force = False
        self.lbl_push_force = ''
        self.min_pos = False
        self.max_pos = False
        self.gear_referent = False
        self.traverse_referent = False

        self.flag_fill_graph = False
        self.type_test = 'hand'
        self.flag_test = False
        self.flag_test_lunch = False
        self.yellow_rattle = False
        self.flag_repeat = False
        self.flag_search_hod = False

        self.alarm_tag = ''
        self.flag_alarm = False


    def _start_param_model(self):
        self.client.connect_client()
        # FIXME таймер жёлтой кнопки
        # self._init_timer_yellow_btn()

        if self.client.flag_connect:
            self.writer = Writer(self.client.client)
            # self.logger.debug('Writer is initialized')
            self.writer.timer_writer_start()
            # self.logger.debug('Timer Writer started')

            self._init_signals()
            self._init_reader()
            # self.logger.debug('Reader is initialized and started')

            self.save_arch = WriterArch()
            self.save_arch.timer_writer_arch_start()
            # self.logger.debug('Writer Archive is initialized and timer started')
            
            self._stand_initialisation()

        else:
            self.status_bar_msg(f'Нет подключения к контроллеру')
            self.logger.warning(f'Нет подключения к контроллеру')
            
    def _stand_initialisation(self):
        try:
            self.fc_control(**{'tag':'max', 'adr':1, 'freq':120})

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_stand_initialisation - {e}')

    def status_bar_msg(self, txt_bar):
        self.signals.stbar_msg.emit(txt_bar)

    def log_error_thread(self, txt_log):
        self.logger.error(txt_log)
        self.status_bar_msg(txt_log)

    def _init_signals(self):
        self.writer.signals.check_buffer.connect(self.check_buffer_state)

    def check_buffer_state(self, res, state):
        self.buffer_state = [res, state]

    def _init_reader(self):
        self.reader = Reader(self.client.client, cst)
        self.reader.signals.thread_err.connect(self.log_error_thread)
        self.reader.signals.read_result.connect(self._reader_result)
        self.signals.read_start.connect(self.reader.start_read)
        self.signals.start_test.connect(self.reader.start_test)
        self.signals.read_stop.connect(self.reader.stop_read)
        self.signals.stop_test.connect(self.reader.stop_test)
        self.signals.read_exit.connect(self.reader.exit_read)
        self.threadpool.start(self.reader)
        self.reader_start()

    def reader_start(self):
        self.signals.read_start.emit()
        self.status_bar_msg(f'Чтение контроллера запущено')

    def reader_start_test(self):
        self.signals.start_test.emit()
        self.status_bar_msg(f'Чтение буффура контроллера запущено')

    def reader_stop(self):
        self.signals.read_stop.emit()
        self.status_bar_msg(f'Чтение контроллера остановлено')

    def reader_stop_test(self):
        self.signals.stop_test.emit()
        self.status_bar_msg(f'Чтение буффера контроллера остановлено')

    def reader_exit(self):
        self.signals.read_exit.emit()

    def _update_switch_dict(self, data):
        try:
            self.switch_dict = {**self.switch_dict, **data}

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_update_switch_dict - {e}')

    def _update_state_dict(self, data):
        try:
            self.state_dict = {**self.state_dict, **data}

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_update_state_dict - {e}')

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
            self.write_bit_force_cycle(0)
            self.timer_add_koef.stop()
            self.timer_calc_koef.stop()

            if self.koef_force_list:
                self.force_koef_offset = round(statistics.fmean(self.koef_force_list), 1)
                self.koef_force_list.clear()
                self.signals.save_koef_force.emit('done')

            else:
                self.signals.save_koef_force.emit('bad')

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_calc_and_save_force_koef - {e}')

    def cancel_koef_force(self):
        try:
            self.force_koef_offset = 0

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/cancel_koef_force - {e}')

    def _reader_result(self, response, tag):
        try:
            if tag == 'buffer':
                self._pars_buffer_result(response)

            if tag == 'reg':
                self._pars_regs_result(response.get('regs'))

            # FIXME при включении проскакивает шум с жёлтой кнопки и отрубается испытание
            # if self.flag_test_launch is True:
            #     if not self.timer_yellow.isActive():
            #         self.timer_yellow.start()
            #     else:
            #         pass

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_reader_result - {e}')

    def _pars_regs_result(self, res):
        try:
            if not res:
                pass
            else:
                self.force_clear = self.parser.magnitude_effort(res[0], res[1])
                self.force_correct = round(self.force_clear * self.force_koef, 1)
                self.force_offset = round(self.force_correct - self.force_koef_offset, 1)

                self.move_now = self.parser.movement_amount(res[2])
                self.move_traverse = round(0.5 * self.parser.movement_amount(res[6]), 1)

                self.counter = self.parser.counter_time(res[4])
                self.force_alarm = self.parser.emergency_force(res[10], res[11])

                self.temper_first = self.parser.temperature_value(res[7], res[8])
                self.temper_second = self.parser.temperature_value(res[12], res[13])
                if self.temper_first > self.temper_second:
                    temp = self.temper_first
                else:
                    temp = self.temper_second
                if temp > self.temper_max:
                    self.temper_max = temp

                self._update_switch_dict(self.parser.switch_state(res[5]))
                self._change_state_list(res[3])

                if self.type_test == 'hand':
                    self.signals.win_set_update.emit()

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_pars_regs_result - {e}')

    def _pars_buffer_result(self, response):
        try:
            data = self.parser.discard_left_data(response)

            if data is None:
                self.logger.debug('Response from buffer controller is None')
                pass  # Пришла пустая посылка

            else:
                self.force_clear = data.get('force')[-1]
                self.force_correct = round(self.force_clear * self.force_koef, 1)
                self.force_offset = round(self.force_correct - self.force_koef_offset, 1)
                self.force_buf = [x * self.force_koef - self.force_koef_offset for x in data.get('force')]

                self.move_now = data.get('move')[-1]
                self.move_buf = data.get('move')

                self.counter = data.get('count')[-1]

                self.temper_max = self.calc_data.check_temperature(data.get('temper'), self.temper_max)
                self.temper_now = data.get('temper')[-1]

                self._change_state_list(data.get('state')[-1])

                if self.type_test == 'hand':
                    self.signals.win_set_update.emit()
                else:
                    self._pars_response_on_circle(self.force_buf, self.move_buf)

        except Exception as e:
            if str(e) == 'list index out of range':
                pass
            else:
                self.logger.error(e)
                self.status_bar_msg(f'ERROR in model/_pars_buffer_result - {e}')

    def _change_state_list(self, reg):
        try:
            temp = bin(reg)[2:].zfill(16)
            bits = ''.join(reversed(temp))
            self.state_list = [int(x) for x in bits]

            self._update_state_dict(self.parser.register_state(reg))

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_change_state_list - {e}')

    def _init_timer_yellow_btn(self):
        try:
            self.timer_yellow = QTimer()
            self.timer_yellow.setInterval(1000)
            self.timer_yellow.timeout.connect(self.yellow_btn_click)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_init_timer_yellow_btn - {e}')

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
            self.status_bar_msg(f'ERROR in model/_yellow_btn_click - {e}')

    def reset_current_circle(self):
        try:
            self.min_pos = False
            self.max_pos = False
            self.start_direction = False
            self.current_direction = False

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/reset_current_circle - {e}')

    def _find_start_direction(self, move):
        try:
            if move[0] < move[-1]:
                direction = 'up'

            elif move[0] > move[-1]:
                direction = 'down'

            else:
                direction = False

            if direction:
                self.start_direction = direction
                self.current_direction = direction
                self.logger.debug(f'Start direction --> {direction}')

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_find_start_direction - {e}')

    def _find_direction_and_point(self, move):
        try:
            if self.current_direction == 'up':
                max_point = max(move)
                if max_point > move[-1]:
                    if not -1 < max_point < 1:
                        self.max_point = max_point
                        self.max_pos = True
                        self.current_direction = 'down'
                        self.logger.debug(f'Max point --> {max_point}')

            elif self.current_direction == 'down':
                min_point = min(move)
                if min_point < move[-1]:
                    if not -1 < min_point < 1:
                        self.min_point = min_point
                        self.min_pos = True
                        self.current_direction = 'up'
                        self.logger.debug(f'Min point --> {min_point}')

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_find_direction_and_point - {e}')
            
    def _add_data_in_graph(self, force, move):
        try:
            self.force_list.extend(force)
            self.move_list.extend(move)
            
        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_add_data_in_graph - {e}')
            
    def clear_data_in_graph(self):
        self.force_list = []
        self.move_list = []
        
    def clear_data_in_circle_graph(self):
        self.force = []
        self.move = []

    def clear_data_in_temper_graph(self):
        self.temper_graph = []
        self.temper_recoil_graph = []
        self.temper_comp_graph = []

    def _check_full_circle(self):
        try:
            if self.gear_referent is False:
                self.clear_data_in_graph()

                self.reset_current_circle()

                self.gear_referent = True
                self.logger.debug('Gear referent is True')

            else:
                self._full_circle_done()

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_check_full_circle - {e}')
            
    def _calc_dynamic_push_force(self):
        try:
            force_min = self.force[self.move.index(min(self.move))]
            
            force_max = self.force[self.move.index(max(self.move))]
            
            force_mid = (force_min + force_max) / 2
            
            self.dynamic_push_force = round((force_mid - self.static_push_force) / 2 + self.static_push_force, 2)
            
        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_calc_dynamic_push_force - {e}')

    def _choice_push_force(self):
        try:
            if self.flag_push_force:
                self._calc_dynamic_push_force()
                return self.dynamic_push_force

            else:
                self.dynamic_push_force = 0
                return self.static_push_force

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_choice_push_force - {e}')

    def _full_circle_done(self):
        try:
            self.logger.debug('Full circle is done')
            if self.flag_fill_graph:
                offset_p = self.calc_data.offset_move_by_hod(self.amort, self.min_point)
                
                self.force = [round(x * (-1), 2) for x in self.force_list]
                self.move = [round(x + offset_p, 2) for x in self.move_list]

                self.clear_data_in_graph()

                max_recoil, max_comp = self.calc_data.middle_min_and_max_force(self.force)
                self.logger.debug(f'Clear recoil --> {max_recoil}, clear comp --> {max_comp}')
                
                push_force = self._choice_push_force()
                self.max_recoil = round(max_recoil + push_force, 1)
                self.max_comp = round(max_comp + push_force, 1)
                self.logger.debug(f'Correct recoil --> {self.max_recoil}, correct comp --> {self.max_comp}')

                self.power_amort = self.calc_data.power_amort(self.force, self.move)
                self.freq_piston = self.calc_data.freq_piston_amort(self.speed_test, self.amort.hod)
                
                self.logger.debug('Full circle response parsing is done')

                self.signals.update_data_graph.emit()

            self.signals.full_cycle_count.emit('+1')

            self.min_pos = False
            self.max_pos = False

        except Exception as e:
            self.clear_data_in_graph()
            self.min_pos = False
            self.max_pos = False

            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_full_circle_done - {e}')

    def _pars_response_on_circle(self, force, move):
        try:
            if self.start_direction is False:
                self._find_start_direction(move)

            else:
                if self.flag_fill_graph:
                    self._add_data_in_graph(force, move)

                if self.min_pos and self.max_pos and min(move) <= self.min_point <= max(move):
                    hod = round(abs(self.min_point) + abs(self.max_point), 1)
                    if self.flag_search_hod is False:
                        if hod > 30:
                            self._check_full_circle()
                        else:
                            self.min_pos = False
                            self.max_pos = False

                    else:
                        self._check_full_circle()

                else:
                    self._find_direction_and_point(move)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_pars_response_on_circle - {e}')

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
            self.status_bar_msg(f'ERROR in model/_write_reg_state - {e}')

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
            self.status_bar_msg(f'ERROR in model/write_bit_force_cycle - {e}')

    def write_bit_red_light(self, value):
        try:
            bit = self.state_dict.get('red_light', 0)
            if int(bit) != value:
                self._write_reg_state(1, value)
        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/write_bit_red_light - {e}')

    def write_bit_green_light(self, value):
        try:
            bit = self.state_dict.get('green_light', 0)
            if int(bit) != value:
                self._write_reg_state(2, value)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/write_bit_green_light - {e}')

    def write_bit_unblock_control(self):
        try:
            self._write_reg_state(3, 1)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/write_bit_unblock_control - {e}')

    def write_bit_emergency_force(self):
        try:
            self._write_reg_state(4, 1)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/write_bit_emergency_force - {e}')

    def write_bit_select_temper(self, value):
        try:
            bit = self.state_dict.get('select_temper', 0)
            if int(bit) != value:
                self._write_reg_state(6, value)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/write_bit_select_temper - {e}')

    def write_emergency_force(self, value):
        try:
            arr = self.calc_data.emergency_force(value)

            self.writer.write_out('reg', values=arr, reg_write=0x200a)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/write_emergency_force - {e}')
            
    def fc_control(self, tag: str, adr: int, speed: float=None, freq: int=None, hod: int=None):
        try:
            if self.state_dict.get('lost_control'):
                self.write_bit_unblock_control()

            if self.state_dict.get('excess_force'):
                self.write_bit_emergency_force()
                
            if hod is None:
                if self.amort is None:
                    hod = 120
                else:
                    hod = self.amort.hod
                
            values = self.fc.freq_command(tag, adr, speed, freq, hod)
            self.writer.write_out('FC', freq_command=values)
            
        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/fc_control - {e}')

    def lamp_all_switch_on(self):
        """Включение всех индикаторов"""
        try:
            if not self.state_dict.get('green_light'):
                self.write_bit_green_light(1)
            if not self.state_dict.get('red_light'):
                self.write_bit_red_light(1)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/lamp_all_switch_on - {e}')

    def lamp_all_switch_off(self):
        """Выключение всех индикаторов"""
        try:
            if self.state_dict.get('green_light'):
                self.write_bit_green_light(0)
            if self.state_dict.get('red_light'):
                self.write_bit_red_light(0)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/lamp_all_switch_off - {e}')

    def lamp_green_switch_on(self):
        """Выключение зелёного индикатора"""
        try:
            if not self.state_dict.get('green_light'):
                self.write_bit_green_light(1)
            if self.state_dict.get('red_light'):
                self.write_bit_red_light(0)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/lamp_green_switch_on - {e}')

    def lamp_red_switch_on(self):
        """Выключение красного индикатора"""
        try:
            if self.state_dict.get('green_light'):
                self.write_bit_green_light(0)
            if not self.state_dict.get('red_light'):
                self.write_bit_red_light(1)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/lamp_red_switch_on - {e}')
            
    def write_data_in_archive(self, tag, data=None):
        try:
            self.save_arch.write_arch_out(tag, data)
            
        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/write_data_in_archive - {e}')
            
    def save_data_in_archive(self):
        try:
            data_dict = {'move_graph': self.move[:],
                         'force_graph': self.force[:],
                         'temper_graph': self.temper_graph[:],
                         'temper_recoil_graph': self.temper_recoil_graph[:],
                         'temper_comp_graph': self.temper_comp_graph[:],
                         'type_test': self.type_test,
                         'speed': self.speed_test,
                         'operator_name': self.operator.name,
                         'operator_rank': self.operator.rank,
                         'serial': self.serial_number,
                         'amort': self.amort,
                         'flag_push_force': int(self.flag_push_force),
                         'static_push_force': self.static_push_force,
                         'dynamic_push_force': self.dynamic_push_force,
                         'max_temperature': self.temper_max}
            
            self.clear_data_in_circle_graph()
            
            self.write_data_in_archive('data', data_dict)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/save_data_in_archive - {e}')
            
    def write_end_test_in_archive(self):
        try:
            self.write_data_in_archive('end_test')

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/write_end_test_in_archive - {e}')
