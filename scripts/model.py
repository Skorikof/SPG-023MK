# -*- coding: utf-8 -*-
import time
import statistics
from PySide6.QtCore import QObject, Signal, QTimer

from scripts.logger import my_logger
from scripts.test_obj import DataTest
from scripts.settings import PrgSettings
from scripts.parser import ParserSPG023MK
from scripts.data_calculation import CalcData
from scripts.reader import Reader
from scripts.writer import Writer
from scripts.archive_saver import WriterArch
from scripts.client import Client
from scripts.freq_control import FreqControl


class ModelSignals(QObject):
    stbar_msg = Signal(str)

    win_set_update = Signal()
    full_cycle_count = Signal(str)
    update_data_graph = Signal()
    test_launch = Signal(bool)
    save_koef_force = Signal(str)

    connect_ctrl = Signal()
    read_finish = Signal()


class Model:
    def __init__(self):
        self._init_variables()
        self._init_flags()

        self._start_param_model()

    def _init_variables(self):
        self.logger = my_logger.get_logger(__name__)
        self.signals = ModelSignals()
        self.client = Client()
        self.writer = None
        self.reader = Reader()
        self.fc = FreqControl()
        self.parser = ParserSPG023MK()
        self.calc_data = CalcData()

        self.data_test = DataTest()

        self.state_dict = {}
        self.switch_dict = {}
        
        self.buffer_state = ['null', 'null']
        
        self.force_koef = PrgSettings().force_koef
        self.force_clear = 0
        self.force_correct = 0
        self.force_koef_offset = 0
        self.force_offset = 0

        self.force_list = []
        self.move_list = []
        self.force = []
        self.move = []
        self.temper_graph = []
        self.temper_recoil_graph = []
        self.temper_comp_graph = []

        self.counter = 0
        self.move_now = 0
        self.move_traverse = 0
        self.hod_measure = 0
        self.min_point = 0
        self.max_point = 0
        self.start_direction = False
        self.current_direction = False

        self.koef_force_list = []
        self.timer_add_koef = None
        self.timer_calc_koef = None
        
        # self.timer_pars_circle = None

        self.timer_yellow = None
        self.time_push_yellow = None

        self.state_list = [0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        self.dynamic_push_force = 0
        self.max_recoil = 0
        self.max_comp = 0

        self.power_amort = 0
        self.freq_piston = 0
        
        self.list_lab_result = []

    def _init_flags(self):
        self.lbl_push_force = ''
        self.min_pos = False
        self.max_pos = False
        self.gear_referent = False
        self.traverse_referent = False

        # self.flag_bufer = False
        self.flag_fill_graph = False
        self.flag_test = False
        self.flag_test_lunch = False
        self.yellow_rattle = False
        self.flag_repeat = False
        self.flag_search_hod = False

        self.alarm_tag = ''
        self.flag_alarm = False
        
    def _init_signals(self):
        self.reader.signals.result.connect(self._reader_result)
        self.reader.signals.error.connect(self.log_error_thread)
        self.writer.signals.check_buffer.connect(self.check_buffer_state)
        
    # def _init_timer_pars_circle(self):
    #     self.timer_pars_circle = QTimer()
    #     self.timer_pars_circle.setInterval(300)
    #     self.timer_pars_circle.timeout.connect(self._pars_response_on_circle)

    def _start_param_model(self):
        self.client.connect_client()
        # FIXME таймер жёлтой кнопки
        # self._init_timer_yellow_btn()

        if self.client.flag_connect:
            self.writer = Writer(self.client.client)
            self.writer.timer_writer_start()

            self._init_signals()
            # self._init_timer_pars_circle()
            self.reader.init_reader(self.client.client)
            self.reader_start()

            # self.save_arch = WriterArch()
            # self.save_arch.timer_writer_arch_start()
            
            # self._stand_initialisation()

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
        
    # def timer_pars_circle_start(self):
    #     self.timer_pars_circle.start()
        
    # def timer_pars_circle_stop(self):
    #     self.timer_pars_circle.stop()
        
    def _update_switch_dict(self, data):
        try:
            if data is not None:
                self.switch_dict = {**self.switch_dict, **data}

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_update_switch_dict - {e}')

    def _update_state_dict(self, data):
        try:
            if data is not None:
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
            self.status_bar_msg(f'ERROR in model/_calc_and_save_force_koef - {e}')

    def cancel_koef_force(self):
        try:
            self.force_koef_offset = 0

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/cancel_koef_force - {e}')

    def _reader_result(self, tag, response):
        try:
            if tag == 'buffer':
                self._pars_buffer_result(response)

            if tag == 'reg':
                self._pars_regs_result(response)

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
                result = self.parser.pars_response_from_regs(res)
                
                if result.get('force', None) is not None:
                    self.force_clear = result.get('force', 0)
                    self.force_correct = round(self.force_clear * self.force_koef, 1)
                    self.force_offset = round(self.force_correct - self.force_koef_offset, 1)

                self.move_now = result.get('move')
                self.move_traverse = result.get('traverse')
                self.counter = result.get('counter')
                self.data_test.force_alarm = result.get('force_a')

                self.data_test.first_temperature = result.get('first_t')
                self.data_test.second_temperature = result.get('second_t')
                if self.data_test.first_temperature > self.data_test.second_temperature:
                    temp = self.data_test.first_temperature
                else:
                    temp = self.data_test.second_temperature
                self.data_test.temperature = temp
                if temp > self.data_test.max_temperature:
                    self.data_test.max_temperature = temp

                self._update_switch_dict(result.get('switch'))
                self._update_state_dict(result.get('state'))
                self.state_list = result.get('state_list')

                if self.data_test.type_test == 'hand':
                    self.signals.win_set_update.emit()
                    
                # if self.flag_bufer:
                #     self._add_data_in_graph(self.force_offset, self.move_now)
                #     # print(f'force_list ==> {self.force_list}')
                #     # print(f'move_list ==> {self.move_list}')
                #     # print(f'force_list ==> {len(self.force_list)}')
                #     # print(f'move_list ==> {len(self.move_list)}')

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_pars_regs_result - {e}')

    def _pars_buffer_result(self, res):
        try:
            data = self.parser.pars_response_from_buffer(res)

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

                self.data_test.max_temperature = self.calc_data.check_temperature(data.get('temper'),
                                                                                  self.data_test.max_temperature)
                self.data_test.temperature = data.get('temper')[-1]

                self.state_list = data.get('state_list')

                if self.data_test.type_test == 'hand':
                    self.signals.win_set_update.emit()
                else:
                    self._pars_response_on_circle(self.force_buf, self.move_buf)

        except Exception as e:
            if str(e) == 'list index out of range':
                pass
            else:
                self.logger.error(e)
                self.status_bar_msg(f'ERROR in model/_pars_buffer_result - {e}')
                
    def _add_data_in_graph(self, force, move):
        try:
            # if force > -50000:
                # self.force_list.append(force)
                # self.move_list.append(move)
            self.force_list.extend(force)
            self.move_list.extend(move)
            
        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_add_data_in_graph - {e}')
            
    def _add_terminator_in_graph(self):
        try:
            self.force_list.append('end')
            self.move_list.append('end')
            
        except Exception as e:
            self.logger.error(e)
            
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
            static = self.data_test.static_push_force
            self.dynamic_push_force = round((force_mid - static) / 2 + static, 2)
            
        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_calc_dynamic_push_force - {e}')

    def _choice_push_force(self):
        try:
            if self.data_test.flag_push_force:
                self._calc_dynamic_push_force()
                return self.dynamic_push_force

            else:
                self.dynamic_push_force = 0
                return self.data_test.static_push_force

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_choice_push_force - {e}')

    def _full_circle_done(self):
        try:
            self.logger.debug('Full circle is done')
            if self.flag_fill_graph:
                offset_p = self.calc_data.offset_move_by_hod(self.data_test.amort, self.min_point)
                
                self.force = [round(x * (-1), 2) for x in self.force_list]
                self.move = [round(x + offset_p, 2) for x in self.move_list]

                max_recoil, max_comp = self.calc_data.middle_min_and_max_force(self.force)
                # max_recoil = max(self.force)
                # max_comp = min(self.force)
                self.logger.debug(f'Clear recoil --> {max_recoil}, clear comp --> {max_comp}')
                
                push_force = self._choice_push_force()
                self.max_recoil = round(max_recoil + push_force, 1)
                self.max_comp = round(max_comp + push_force, 1)
                self.logger.debug(f'Correct recoil --> {self.max_recoil}, correct comp --> {self.max_comp}')

                self.power_amort = self.calc_data.power_amort(self.force, self.move)
                self.freq_piston = self.calc_data.freq_piston_amort(self.data_test.speed_test, self.data_test.amort.hod)
                
                self.logger.debug('Full circle response parsing is done')

                self.signals.update_data_graph.emit()
                
                self.clear_data_in_graph()

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
                self._write_reg_state(1, value, command='red_light')
        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/write_bit_red_light - {e}')

    def write_bit_green_light(self, value):
        try:
            bit = self.state_dict.get('green_light', 0)
            if int(bit) != value:
                self._write_reg_state(2, value, command='green_light')

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/write_bit_green_light - {e}')

    def write_bit_unblock_control(self):
        try:
            self._write_reg_state(3, 1, command='unblock_control')

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/write_bit_unblock_control - {e}')

    def write_bit_emergency_force(self):
        try:
            self._write_reg_state(4, 1, command='reset_emergency_force')

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/write_bit_emergency_force - {e}')

    def write_bit_select_temper(self, value):
        try:
            bit = self.state_dict.get('select_temper', 0)
            if int(bit) != value:
                self._write_reg_state(6, value, command='select_temper')

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
            self.status_bar_msg(f'ERROR in model/fc_control - {e}')

    def lamp_all_switch_on(self):
        """Включение всех индикаторов"""
        try:
            self.write_bit_green_light(1)
            self.write_bit_red_light(1)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/lamp_all_switch_on - {e}')

    def lamp_all_switch_off(self):
        """Выключение всех индикаторов"""
        try:
            self.write_bit_green_light(0)
            self.write_bit_red_light(0)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/lamp_all_switch_off - {e}')

    def lamp_green_switch_on(self):
        """Включение зелёного индикатора"""
        try:
            self.write_bit_green_light(1)
            self.write_bit_red_light(0)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/lamp_green_switch_on - {e}')

    def lamp_red_switch_on(self):
        """Включение красного индикатора"""
        try:
            self.write_bit_green_light(0)
            self.write_bit_red_light(1)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/lamp_red_switch_on - {e}')
            
    def save_result_cycle(self):
        try:
            if not self.move or not self.force:
                pass
            else:
                type_test = self.data_test.type_test
                if type_test == 'lab' or type_test == 'lab_cascade' or type_test == 'conv':
                    data_dict = {'speed': self.data_test.speed_test,
                                 'move': self.move[:],
                                 'force': self.force[:]}

                    self.list_lab_result.append(data_dict)
                        
                self.save_data_in_archive()
                    
        except Exception as e:
            self.logger.error(e)
            
    def write_data_in_archive(self, tag, data=None):
        try:
            self.save_arch = WriterArch()
            self.save_arch.timer_writer_arch_start()
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
                         'type_test': self.data_test.type_test,
                         'speed': self.data_test.speed_test,
                         'operator_name': self.data_test.operator.name,
                         'operator_rank': self.data_test.operator.rank,
                         'serial': self.data_test.serial,
                         'amort': self.data_test.amort,
                         'flag_push_force': int(self.data_test.flag_push_force),
                         'static_push_force': self.data_test.static_push_force,
                         'dynamic_push_force': self.dynamic_push_force,
                         'max_temperature': self.data_test.max_temperature}
            
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
