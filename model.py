# -*- coding: utf-8 -*-
import inspect
import time
import crcmod
import serial
import modbus_tk.defines as cst
import modbus_tk.modbus_rtu as modbus_rtu
from struct import pack, unpack
from PyQt5.QtCore import QObject, QThreadPool, pyqtSignal, QTimer

from logger import my_logger
from my_thread.my_threads import LogWriter, Writer, Reader
from settings import PrgSettings
from my_obj.data_calculation import CalcData


class WinSignals(QObject):
    connect_ctrl = pyqtSignal()
    stbar_msg = pyqtSignal(str)
    read_start = pyqtSignal()
    start_test = pyqtSignal()
    stop_test = pyqtSignal()
    read_stop = pyqtSignal()
    read_exit = pyqtSignal()
    read_finish = pyqtSignal(dict)
    full_cycle_count = pyqtSignal()
    update_data_graph = pyqtSignal()
    test_launch = pyqtSignal(bool)
    save_koef_force = pyqtSignal()


class Model:
    def __init__(self):
        self.signals = WinSignals()
        self.set_dict = PrgSettings().settings
        self.threadpool = QThreadPool()

        self.logger = my_logger.get_logger(__name__)

        self.client = None
        self.log_writer = None
        self.set_regs = {}
        self.reader = None
        self.writer_flag_init = False
        self.flag_write = False
        self.time_response = None
        self.timer_add_koef = None
        self.koef_force_list = []
        self.timer_calc_koef = None
        self.timer_yellow = None
        self.time_push_yellow = None
        self.yellow_rattle = False
        self.main_min_point = 100
        self.min_point = 0
        self.max_point = 0
        self.reg_state = None
        self.reg_switch = None

        self._start_param_model()

    def _start_param_model(self):
        self._init_connect()
        self._init_timer_yellow_btn()
        start_state = PrgSettings().state
        self.update_main_dict(start_state)

        if self.client:
            self._init_timer_writer()
            self._init_reader()
            self.write_bit_force_cycle(1)

        else:
            self.status_bar_msg(f'Нет подключения к контроллеру')
            self.logger.warning(f'Нет подключения к контроллеру')

    def _save_log(self, mode_s, msg_s):
        try:
            current_frame = inspect.currentframe()
            caller_frame = current_frame.f_back
            num_line = caller_frame.f_lineno
            code_obj = caller_frame.f_code
            code_obj_name = code_obj.co_name
            temp_str = code_obj.co_filename
            temp_d = temp_str.split('/')
            nam_f = temp_d[len(temp_d) - 1]

            self.log_writer = LogWriter(mode_s, (nam_f, code_obj_name, num_line), msg_s)
            self.threadpool.start(self.log_writer)

        except Exception as e:
            print(str(e))

    def status_bar_msg(self, txt_bar):
        self.signals.stbar_msg.emit(txt_bar)

    # FIXME
    def log_error(self, txt_log):
        self.status_bar_msg(txt_log)
        self._save_log('error', txt_log)

    def log_info(self, txt_log):
        self.status_bar_msg(txt_log)
        self._save_log('info', txt_log)

    def _init_connect(self):
        try:
            self.client = modbus_rtu.RtuMaster(serial.Serial(port=self.set_dict.get('con_set')['COM'],
                                                             baudrate=self.set_dict.get('con_set')['baudrate'],
                                                             bytesize=self.set_dict.get('con_set')['bytesize'],
                                                             parity=self.set_dict.get('con_set')['parity'],
                                                             stopbits=self.set_dict.get('con_set')['stopbits'],
                                                             timeout=0.000001))

            self.client.set_timeout(1.0)
            self.client.set_verbose(True)
            self.client.open()
            self.set_dict['con_set']['connect'] = True
            self.status_bar_msg(f'Контроллер подключен')

        except Exception as e:
            self.client = None
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_init_connect - {e}')

    def disconnect_client(self):
        if self.client:
            self.client.close()
            self.set_dict['con_set']['connect'] = False
            self.status_bar_msg(f'Контроллер отключен')

    def _init_reader(self):
        self.reader = Reader(self.client, cst)
        self.reader.signals.thread_log.connect(self.log_info)
        self.reader.signals.thread_err.connect(self.log_error)
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
        self.koef_force_list.append(self.set_regs.get('force_real', 0))

    def _calc_and_save_force_koef(self):
        try:
            self.timer_add_koef.stop()
            self.timer_calc_koef.stop()
            self.set_regs['force_refresh'] = round(sum(self.koef_force_list) / len(self.koef_force_list), 1)
            self.signals.save_koef_force.emit()

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_calc_and_save_force_koef - {e}')

    def cancel_koef_force(self):
        try:
            self.set_regs['force_refresh'] = 0

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/cancel_koef_force - {e}')

    def correct_force(self, force):
        try:
            refresh = self.set_regs.get('force_refresh', 0)
            koef = self.set_regs.get('force_koef', 1)
            return round((force - refresh) * koef, 1)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/correct_force - {e}')

    def reset_min_point(self):
        self.main_min_point = 100

    def _reader_result(self, response, tag):
        try:
            if tag == 'buffer':
                self._pars_buffer_result(response)

            if tag == 'reg':
                self._pars_regs_result(response.get('regs'))

            if self.set_regs.get('test_launch', False) is True:
                if not self.timer_yellow.isActive():
                    self.timer_yellow.start()
                else:
                    pass

            self.time_response = time.monotonic()

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_reader_result - {e}')

    def _pars_buffer_result(self, response):
        try:
            # print(f'Count --> {response.get("count")}')
            # print(f'Force --> {response.get("force")}')
            # print(f'Move --> {response.get("move")}')
            # print(f'State --> {response.get("state")}')
            # print(f'Temper --> {response.get("temper")}')
            # print(f'{"=" * 100}')

            force_list = []
            move_list = []

            for count, force in enumerate(response.get('force', [-100000])):
                if force != -100000:
                    force_list.append(response.get('force')[count])
                    move_list.append(response.get('move')[count])

            if not force_list:
                pass # Пришла пустая посылка

            else:
                command = {'force_real': force_list[-1],
                           'force': self.correct_force(force_list[-1]),
                           'move': move_list[-1],
                           'force_list': [self.correct_force(x) for x in force_list],
                           'move_list': move_list[:],
                           'temp_list': response.get('temper')[:],
                           'count': response.get('count', [-32000])[-1],
                           }

                self.update_main_dict(command)

                state = response.get('state')[-1]
                self._register_state(state)

                self._check_temperature(self.set_regs['temp_list'])

                self.signals.read_finish.emit(self.set_regs)

                self._pars_response_on_circle(self.set_regs.get('force_list'), self.set_regs.get('move_list'))

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_pars_buffer_result - {e}')

    def _pars_regs_result(self, res):
        try:
            if not res:
                pass
            else:
                force = self._magnitude_effort(res[0], res[1])
                command = {
                    'force_real': force,
                    'force': self.correct_force(force),
                    'move': self._movement_amount(res[2]),
                    'count': self._counter_time(res[4]),
                    'traverse_move': round(0.5 * self._movement_amount(res[6]), 1),
                    'temper_first': self._temperature_value(res[7], res[8]),
                    'force_alarm': self._emergency_force(res[10], res[11]),
                    'temper_second': self._temperature_value(res[12], res[13]),
                }

                self.update_main_dict(command)

                self._register_state(res[3])
                self._switch_state(res[5])

                self.signals.read_finish.emit(self.set_regs)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_pars_regs_result - {e}')

    def _init_timer_yellow_btn(self):
        try:
            self.timer_yellow = QTimer()
            self.timer_yellow.setInterval(200)
            self.timer_yellow.timeout.connect(self.yellow_btn_click)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_init_timer_yellow_btn - {e}')

    def yellow_btn_click(self):
        try:
            if self.set_regs.get('yellow_btn', True) is False:
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

            command = {'start_direction': direction,
                       'current_direction': direction}
            self.update_main_dict(command)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_find_start_direction - {e}')

    def _find_direction_and_point(self, move):
        try:
            direction = self.set_regs.get('current_direction')
            if direction == 'up':
                if max(move) > move[-1]:
                    if not -1 < max(move) < 1:
                        self.max_point = max(move)
                        command = {'max_point': self.max_point,
                                   'max_pos': True,
                                   'current_direction': 'down',
                                   }

                        self.update_main_dict(command)

            elif direction == 'down':
                if min(move) < move[-1]:
                    if not -1 < min(move) < 1:
                        self.min_point = min(move)
                        command = {'min_point': self.min_point,
                                   'min_pos': True,
                                   'current_direction': 'up',
                                   }

                        self.update_main_dict(command)
                        if self.min_point < self.main_min_point:
                            self.main_min_point = self.min_point

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_find_direction_and_point - {e}')

    def _add_data_in_list_graph(self, force, move):
        try:
            self.set_regs['force_accum_list'].extend(force)
            self.set_regs['move_accum_list'].extend(move)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_add_data_in_list_graph - {e}')

    def _check_full_circle(self):
        try:
            if self.set_regs.get('gear_referent', False) is False:
                command = {'force_accum_list': [],
                           'move_accum_list': [],
                           'force_graph': [],
                           'move_real_list': [],
                           'start_direction': False,
                           'min_pos': False,
                           'max_pos': False,
                           'gear_referent': True}

                self.update_main_dict(command)

            else:
                self._full_circle_done()

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_check_full_circle - {e}')

    def _calc_dynamic_push_force(self):
        try:
            static_push_force = self.set_regs.get('static_push_force', 0)

            min_index = self.set_regs.get('move_accum_list').index(self.min_point)
            force_min = abs(self.set_regs.get('force_accum_list')[min_index])

            max_index = self.set_regs.get('move_accum_list').index(self.max_point)
            force_max = abs(self.set_regs.get('force_accum_list')[max_index])

            push_force_mid = round((force_min + force_max) / 2, 1)
            self.set_regs['dynamic_push_force'] = round((push_force_mid - static_push_force) / 2 + static_push_force, 2)

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
                amort = self.set_regs.get('amort')

                move_list = self.set_regs.get('move_accum_list')[:]
                force_list = self.set_regs.get('force_accum_list')[:]

                max_recoil, max_comp = CalcData().middle_min_and_max_force(force_list)

                offset_p = CalcData().offset_move_by_hod(amort, self.min_point)

                command = {'max_comp': round(max_comp - push_force, 2),
                           'max_recoil': round(max_recoil + push_force, 2),
                           'force_graph': list(map(lambda x: round(x * (-1), 1), force_list)),
                           'move_real_list': move_list[:],
                           'move_graph': list(map(lambda x: round(x + offset_p, 1), move_list)),
                           'power': CalcData().power_amort(move_list, force_list),
                           'freq_piston': CalcData().freq_piston_amort(speed, amort),
                           'force_accum_list': [],
                           'move_accum_list': [],
                           }

                self.update_main_dict(command)

                self.signals.update_data_graph.emit()

            self.signals.full_cycle_count.emit()

            command = {'min_pos': False,
                       'max_pos': False,
                       }

            self.update_main_dict(command)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_full_circle_done - {e}')

    def _pars_response_on_circle(self, force: list, move: list):
        try:
            if not self.set_regs.get('start_direction', False):
                self._find_start_direction(move)

            else:
                if self.set_regs.get('fill_graph', False):
                    self._add_data_in_list_graph(force, move)

                if (self.set_regs.get('min_pos', False) and self.set_regs.get('max_pos', False) and
                        min(move) <= self.min_point <= max(move)):
                    hod = round(abs(self.min_point) + abs(self.max_point), 1)
                    hod_dif = self.set_regs.get('hod', 120)
                    if self.set_regs.get('search_hod') is False:
                        if hod > hod_dif - 5:
                            self._check_full_circle()
                        else:
                            command = {'min_pos': False,
                                       'max_pos': False,
                                       }

                            self.update_main_dict(command)

                    else:
                        self._check_full_circle()

                else:
                    self._find_direction_and_point(move)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_pars_response_on_circle - {e}')

    def _init_timer_writer(self):
        self.timer_writer = QTimer()
        self.timer_writer.setInterval(50)
        self.timer_writer.timeout.connect(self._control_write)
        self.timer_writer.start()

    def _control_write(self):
        try:
            if not self.set_regs.get('query_write', False):
                if self.set_regs.get('list_write', []):
                    obj_wr = self.set_regs.get('list_write')[0]
                    self.set_regs['query_write'] = True

                    self.threadpool.start(obj_wr)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_control_write - {e}')

    def _result_write(self, res, tag, addr, value):
        try:
            if self.set_regs.get('query_write', False):
                self.set_regs['query_write'] = False
                self.set_regs['list_write'].pop(0)

                if res == 'OK!':
                    pass
                    # if tag == 'reg':
                    #     self._pars_result_reg_write(addr, value[0])
                    #
                    # elif tag == 'FC':
                    #     if not self.set_regs.get('repeat_command'):
                    #         self.set_regs['fc_ready'] = True
                    #     else:
                    #         self.set_regs['repeat_command'] = False

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_result_write - {e}')

    def _pars_result_reg_write(self, addr, value):
        if addr == 8195:  # Регистр состояния 0х2003
            temp = bin(value)[2:].zfill(16)
            bits = ''.join(reversed(temp))
            self._switch_read_buffer(bool(int(bits[0])))

    def _switch_read_buffer(self, flag):
        try:
            if flag:
                if not self.set_regs.get('flag_bit_force', False):
                    self.set_regs['flag_bit_force'] = True

            else:
                if self.set_regs.get('flag_bit_force', True):
                    self.set_regs['flag_bit_force'] = False

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_switch_read_buffer - {e}')

    def write_out(self, tag, values=None, reg_write=None, freq_command=None):
        try:
            self.set_regs['list_write'].append(self._init_writer(tag, values, reg_write, freq_command))

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/write_out - {e}')

    def _init_writer(self, tag, values=None, reg_write=None, freq_command=None):
        try:
            writer = Writer(client=self.client,
                            cst=cst,
                            tag=tag,
                            values=values,
                            reg_write=reg_write,
                            freq_command=freq_command)

            writer.signals.thread_log.connect(self.log_info)
            writer.signals.thread_err.connect(self.log_error)
            writer.signals.write_result.connect(self._result_write)

            return writer

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_init_writer - {e}')

    def _write_reg_state(self, bit, value):
        try:
            temp_list = [0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            com_list = self.set_regs.get('list_state', temp_list)[:]
            com_list[bit] = value

            res = 0
            values = []

            for i in range(16):
                res = res + com_list[i] * 2 ** i

            values.append(res)

            self.write_out('reg', values, 0x2003)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_write_reg_state - {e}')

    def write_bit_force_cycle(self, value):
        try:
            bit = self.set_regs.get('cycle_force', 0)
            if int(bit) != value:
                self._write_reg_state(0, value)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/write_bit_force_cycle - {e}')

    def write_bit_red_light(self, value):
        try:
            bit = self.set_regs.get('red_light', 0)
            if int(bit) != value:
                self._write_reg_state(1, value)
        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/write_bit_red_light - {e}')

    def write_bit_green_light(self, value):
        try:
            bit = self.set_regs.get('green_light', 0)
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
            bit = self.set_regs.get('select_temper', 0)
            if int(bit) != value:
                self._write_reg_state(6, value)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/write_bit_select_temper - {e}')

    def write_emergency_force(self, value):
        try:
            arr = []
            val = pack('>f', value)
            for i in range(0, 4, 2):
                arr.append(int((hex(val[i])[2:] + hex(val[i + 1])[2:]), 16))

            self.write_out('reg', arr, 0x200a)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/write_emergency_force - {e}')

    def _motor_command(self, command):
        try:
            if self.set_regs.get('lost_control'):
                self.write_bit_unblock_control()

            if self.set_regs.get('excess_force'):
                self.write_bit_emergency_force()

            command = command + self._calc_crc(command)
            values = self._calc_values_write(command)

            self.write_out('FC', freq_command=values)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_motor_command - {e}')

    def write_max_frequency(self, adr_freq, freq):
        try:
            freq = freq * 100
            freq_hex = hex(freq)[2:].zfill(4)
            freq_hex = f'0{adr_freq}06010B{freq_hex}'
            self._motor_command(freq_hex)
            print('max freq rewrite')

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/write_frequency - {e}')

    def write_frequency(self, adr_freq, freq):
        try:
            freq_hex = hex(freq)[2:].zfill(4)
            freq_hex = f'0{adr_freq}06010D{freq_hex}'
            self._motor_command(freq_hex)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/write_frequency - {e}')

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

    def _calc_crc(self, data):
        try:
            byte_data = bytes.fromhex(data)
            crc16 = crcmod.mkCrcFun(0x18005, initCrc=0xFFFF, rev=True, xorOut=0x0000)
            crc_str = hex(crc16(byte_data))[2:].zfill(4)
            crc_str = crc_str[2:] + crc_str[:2]

            return crc_str

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_calc_crc - {e}')

    def _calc_values_write(self, data):
        try:
            val_regs = []
            for i in range(0, len(data), 4):
                temp = data[i:i + 4]
                temp_byte = bytearray.fromhex(temp)
                temp_val = int.from_bytes(temp_byte, 'big')
                val_regs.append(temp_val)

            return val_regs

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_calc_values_write - {e}')

    def _check_temperature(self, temp_list: list):
        try:
            self.set_regs['temperature'] = temp_list[-1]

            if max(temp_list) > self.set_regs.get('max_temperature', 0):
                self.set_regs['max_temperature'] = max(temp_list)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/find_max_temperature - {e}')

    #FIXME
    def _magnitude_effort(self, low_reg, big_reg):
        """Текущая величина усилия"""
        try:
            val_temp = round(unpack('f', pack('<HH', big_reg, low_reg))[0], 1)

            return val_temp

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_magnitude_effort - {e}')

    def _movement_amount(self, data) -> float:
        """Текущая величина перемещения штока аммортизатора или траверсы"""
        try:
            result = round(-0.1 * (int.from_bytes(pack('>H', data), 'big', signed=True)), 1)

            return result

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_movement_amount - {e}')

    def _register_state(self, reg):
        """Регистр состояния 0х2003"""
        try:
            if self.reg_state != reg:
                self.reg_state = reg
                temp = bin(reg)[2:].zfill(16)
                bits = ''.join(reversed(temp))

                command = {'list_state': [int(x) for x in bits],
                           'cycle_force': bool(int(bits[0])),
                           'red_light': bool(int(bits[1])),
                           'green_light': bool(int(bits[2])),
                           'lost_control': bool(int(bits[3])),
                           'excess_force': bool(int(bits[4])),
                           'select_temper': int(bits[6]),
                           'safety_fence': bool(int(bits[8])),
                           'traverse_block': bool(int(bits[9])),
                           'state_freq': bool(int(bits[11])),
                           'state_force': bool(int(bits[12])),
                           'yellow_btn': bool(int(bits[13]))
                           }

                self.update_main_dict(command)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_register_state - {e}')

    def _counter_time(self, register):
        """Регистр счётчика времени"""
        try:
            return register

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_counter_time - {e}')

    def _switch_state(self, reg):
        """Регистр состояния входов модуля МВ110-224.16ДН"""
        try:
            if self.reg_switch != reg:
                self.reg_switch = reg
                temp = bin(reg)[2:].zfill(16)
                bits = ''.join(reversed(temp))

                command = {'traverse_block_left': bool(int(bits[1])),
                           'traverse_block_right': bool(int(bits[2])),
                           'alarm_highest_position': bool(int(bits[8])),
                           'alarm_lowest_position': bool(int(bits[9])),
                           'highest_position': bool(int(bits[12])),
                           'lowest_position': bool(int(bits[13]))}

                self.update_main_dict(command)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_switch_state - {e}')

    def _temperature_value(self, low_reg, big_reg):
        """Величина температуры с модуля МВ-110-224-2А"""
        try:
            val_temp = round(unpack('f', pack('<HH', big_reg, low_reg))[0], 1)

            return val_temp

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_temperature_value - {e}')

    def _emergency_force(self, low_reg, big_reg):
        """Аварийное усилие"""
        try:
            val_temp = unpack('f', pack('<HH', big_reg, low_reg))[0]

            return val_temp

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_emergency_force - {e}')

    def calculate_freq(self, speed):
        """Пересчёт скорости в частоту для записи в частотник"""
        try:
            koef = round((2 * 17.99) / (2 * 3.1415 * 0.98), 5)
            hod = self.set_regs.get('hod', 120) / 1000
            radius = hod / 2
            freq = int(100 * (koef * speed) / radius)

            return freq

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/calculate_freq - {e}')
