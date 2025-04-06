# -*- coding: utf-8 -*-
import time
import statistics
import modbus_tk.defines as cst
import numpy as np
from PyQt5.QtCore import QObject, QThreadPool, pyqtSignal, QTimer

from logger import my_logger
from my_thread.my_threads import Reader
from settings.settings import PrgSettings
from my_parser.parser import ParserSPG023MK
from calc_data.data_calculation import CalcData
from writer.writer import Writer
from connect.client import Client


class ModelSignals(QObject):
    stbar_msg = pyqtSignal(str)
    read_start = pyqtSignal()
    start_test = pyqtSignal()
    stop_test = pyqtSignal()
    read_stop = pyqtSignal()
    read_exit = pyqtSignal()

    win_set_update = pyqtSignal()
    full_cycle_count = pyqtSignal(str)
    update_data_graph = pyqtSignal()
    test_launch = pyqtSignal(bool)
    save_koef_force = pyqtSignal(str)

    connect_ctrl = pyqtSignal()
    read_finish = pyqtSignal()


class Model:
    def __init__(self):
        self.signals = ModelSignals()
        self.threadpool = QThreadPool()

        self.logger = my_logger.get_logger(__name__)
        self.parser = ParserSPG023MK()
        self.calc_data = CalcData()
        self.client = Client()

        self._init_varibles()

        self._start_param_model()

    def _init_varibles(self):
        self.set_regs = {}
        self.state_dict = {}
        self.switch_dict = {}

        self.reader = None
        self.writer = None
        self.operator = {'name': '', 'rank': ''}
        self.amort = None
        self.buffer_state = ['null', 'null']

        self.force_graph = np.array([], 'float64')
        self.move_graph = np.array([], 'float64')

        self.force_koef = PrgSettings().force_koef
        self.force_clear = 0
        self.force_correct = 0
        self.force_koef_offset = 0
        self.force_offset = 0

        self.counter = 0
        self.move_now = 0
        self.move_traverse = 0

        self.hod_measure = 0
        self.min_pos = False
        self.min_point = 0
        self.max_pos = False
        self.max_point = 0
        self.start_direction = None
        self.current_direction = None

        self.gear_referent = False

        self.force_alarm = 0
        self.temper_first = 0
        self.temper_second = 0
        self.temper_max = 0

        self.timer_add_koef = None
        self.koef_force_list = []
        self.timer_calc_koef = None

        self.finish_temper = PrgSettings().finish_temper
        self.timer_yellow = None
        self.time_push_yellow = None
        self.yellow_rattle = False

        self.main_min_point = 100
        self.min_point = 0
        self.max_point = 0
        self.state_list = [0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def _start_param_model(self):
        self.client.connect_client()
        # FIXME таймер жёлтой кнопки
        # self._init_timer_yellow_btn()

        if self.client.flag_connect:
            self.writer = Writer(self.client.client)
            self.writer.timer_writer_start()

            self._init_signals()
            self._init_reader()

            self.write_bit_force_cycle(0)

            self.write_max_frequency(1, 120)

        else:
            self.status_bar_msg(f'Нет подключения к контроллеру')
            self.logger.warning(f'Нет подключения к контроллеру')

    def status_bar_msg(self, txt_bar):
        self.signals.stbar_msg.emit(txt_bar)

    def log_error_thread(self, txt_log):
        self.logger.error(txt_log)
        self.status_bar_msg(txt_log)

    def log_info_thread(self, txt_log):
        self.logger.info(txt_log)
        self.status_bar_msg(txt_log)

    def _init_signals(self):
        self.writer.signals.check_buffer.connect(self.check_buffer_state)

    def check_buffer_state(self, res, state):
        self.buffer_state = [res, state]

    def _init_reader(self):
        self.reader = Reader(self.client.client, cst)
        self.reader.signals.thread_log.connect(self.log_info_thread)
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

    def update_main_dict(self, data):
        try:
            self.set_regs = {**self.set_regs, **data}

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/update_main_dict - {e}')

    def init_timer_koef_force(self):
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

    def reset_min_point(self):
        self.main_min_point = 100

    def _reader_result(self, response, tag):
        try:
            if tag == 'buffer':
                self._pars_buffer_result(response)

            if tag == 'reg':
                self._pars_regs_result(response.get('regs'))

            # FIXME при включении проскакивает шум с жёлтой кнопки и отрубается испытание
            # if self.set_regs.get('test_launch', False) is True:
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

                self._update_switch_dict(self.parser.switch_state(res[5]))
                self._change_state_list(res[3])

                self._read_controller_finish()

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_pars_regs_result - {e}')

    def _pars_buffer_result(self, response):
        try:
            data = self.parser.discard_left_data(response)

            if data is None:
                pass  # Пришла пустая посылка

            else:
                self.counter = data.get('count')[-1]
                self.move_now = data.get('move')[-1]
                self.temper_max = self.calc_data.check_temperature(data.get('temper'), self.temper_max)

                self.force_array = (np.array(data.get('force')) * self.force_koef) - self.force_koef_offset
                self.move_array = np.array(data.get('move'))

                # self.temper_array = np.array(data.get('temper'))

                self._change_state_list(data.get('state')[-1])

                self._read_controller_finish()

                self._pars_response_on_circle(self.force_array, self.move_array)

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

    def _read_controller_finish(self):
        if self.set_regs.get('type_test', None) == 'hand':
            self.signals.win_set_update.emit()

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

    def _find_start_direction(self, move: list):
        try:
            if move[0] < move[-1]:
                direction = 'up'

            elif move[0] > move[-1]:
                direction = 'down'

            else:
                direction = False

            self.start_direction = direction
            self.current_direction = direction

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_find_start_direction - {e}')

    def _find_direction_and_point(self, move):
        try:
            if self.current_direction == 'up':
                if max(move) > move[-1]:
                    if not -1 < max(move) < 1:
                        self.max_point = max(move)
                        self.max_pos = True
                        self.current_direction = 'down'

            elif self.current_direction == 'down':
                if min(move) < move[-1]:
                    if not -1 < min(move) < 1:
                        self.min_point = min(move)
                        self.min_pos = True
                        self.current_direction = 'up'

                        if self.min_point < self.main_min_point:
                            self.main_min_point = self.min_point

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_find_direction_and_point - {e}')

    def _add_data_in_array_graph(self, force, move):
        try:
            self.force_graph = np.concatenate((self.force_graph, force))
            self.move_graph = np.concatenate((self.move_graph, move))

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_add_data_in_array_graph - {e}')

    def clear_data_in_array_graph(self):
        try:
            self.force_graph = np.array([], 'float64')
            self.move_graph = np.array([], 'float64')

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/clear_data_in_array_graph - {e}')

    def _check_full_circle(self):
        try:
            if self.gear_referent is False:

                self.clear_data_in_array_graph()

                self.min_pos = False
                self.max_pos = False
                self.start_direction = False
                self.gear_referent = True

                self.set_regs['force_graph'] = []

            else:
                self._full_circle_done()

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_check_full_circle - {e}')

    def _calc_dynamic_push_force(self):
        try:
            static_push_force = self.set_regs.get('static_push_force', 0)

            min_index = np.argmin(self.move_graph)
            force_min = abs(self.force_graph[min_index])

            max_index = np.argmax(self.move_graph)
            force_max = abs(self.force_graph[max_index])

            push_force_mid = (force_min + force_max) / 2
            self.set_regs['dynamic_push_force'] = np.round((push_force_mid - static_push_force) / 2 + static_push_force,
                                                           decimals=2)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_calc_dynamic_push_force - {e}')

    def _choice_push_force(self):
        try:
            if self.set_regs.get('flag_push_force', False):
                return self.set_regs.get('dynamic_push_force', 0)

            else:
                return self.set_regs.get('static_push_force', 0)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_choice_push_force - {e}')

    def _full_circle_done(self):
        try:
            if self.set_regs.get('fill_graph', False):
                self._calc_dynamic_push_force()
                push_force = self._choice_push_force()
                speed = self.set_regs.get('speed')

                move_list = list(self.move_graph)
                force_list = list(self.force_graph * (-1))

                max_recoil, max_comp = self.calc_data.middle_min_and_max_force(force_list)

                offset_p = self.calc_data.offset_move_by_hod(self.amort, self.min_point)

                self.clear_data_in_array_graph()

                command = {'max_comp': round(max_comp - push_force, 2),
                           'max_recoil': round(max_recoil + push_force, 2),
                           'force_graph': force_list[:],
                           'move_graph': list(map(lambda x: round(x + offset_p, 1), move_list)),
                           'power': self.calc_data.power_amort(move_list, force_list),
                           'freq_piston': self.calc_data.freq_piston_amort(speed, self.amort.hod),
                           }

                self.update_main_dict(command)

                self.signals.update_data_graph.emit()

            self.signals.full_cycle_count.emit('+1')

            self.min_pos = False
            self.max_pos = False

        except Exception as e:
            self.clear_data_in_array_graph()
            self.min_pos = False
            self.max_pos = False

            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_full_circle_done - {e}')

    def _pars_response_on_circle(self, force, move):
        try:
            if not self.start_direction:
                self._find_start_direction(move)

            else:
                if self.set_regs.get('fill_graph', False):
                    self._add_data_in_array_graph(force, move)

                if self.min_pos and self.max_pos and min(move) <= self.min_point <= max(move):
                    hod = round(abs(self.min_point) + abs(self.max_point), 1)
                    if self.set_regs.get('search_hod') is False:
                        if hod > 38:
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

    def _motor_command(self, command):
        try:
            if self.state_dict.get('lost_control'):
                self.write_bit_unblock_control()

            if self.state_dict.get('excess_force'):
                self.write_bit_emergency_force()

            command = command + self.calc_data.calc_crc(command)
            values = self.calc_data.values_freq_command(command)

            self.writer.write_out('FC', freq_command=values)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_motor_command - {e}')

    def write_max_frequency(self, adr_freq, freq):
        try:
            freq = freq * 100
            freq_hex = hex(freq)[2:].zfill(4)
            freq_hex = f'0{adr_freq}06010B{freq_hex}'
            self._motor_command(freq_hex)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/write_frequency - {e}')

    def write_speed_motor(self, adr: int, speed: float = None, freq: int = None, hod: int = None):
        """
        Запись скорости вращения двигателя, если задана скорость, то она пересчитывается в частоту,
        частота записывается напрямую
        """
        try:
            value = 0
            if not freq:
                if not hod:
                    if self.amort is None:
                        hod = 120
                    else:
                        hod = self.amort.hod
                value = self.calc_data.freq_from_speed(speed, hod)

            elif not speed:
                value = 100 * freq

            freq_hex = hex(value)[2:].zfill(4)
            freq_hex = f'0{adr}06010D{freq_hex}'
            self._motor_command(freq_hex)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/write_speed_motor - {e}')

    def motor_up(self, adr_freq):
        try:
            com_hex = f'0{adr_freq}0620000002'
            self._motor_command(com_hex)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/motor_up - {e}')

    def motor_down(self, adr_freq):
        try:
            com_hex = f'0{adr_freq}0620000001'
            self._motor_command(com_hex)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/motor_down - {e}')

    def motor_stop(self, adr_freq):
        try:
            com_hex = f'0{adr_freq}0620000003'
            self._motor_command(com_hex)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/motor_stop - {e}')

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
