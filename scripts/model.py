# -*- coding: utf-8 -*-
import time
import statistics
from dataclasses import dataclass
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


@dataclass
class ForceData:
    """Управление данными о силе и коэффициентах."""
    force_clear: float = 0
    force_correct: float = 0
    force_offset: float = 0
    force_koef: float = 0
    force_koef_offset: float = 0
    koef_force_list: list = None
    timer_add_koef: QTimer = None
    timer_calc_koef: QTimer = None
    
    def __post_init__(self):
        if self.koef_force_list is None:
            self.koef_force_list = []


@dataclass
class MovementData:
    """Управление данными о движении и направлении."""
    move_now: float = 0
    move_traverse: float = 0
    hod_measure: float = 0
    min_point: float = 0
    max_point: float = 0
    start_direction: str = 'none'
    current_direction: str = 'none'
    min_pos: bool = False
    max_pos: bool = False


@dataclass
class GraphData:
    """Управление данными графиков."""
    force_list: list = None
    move_list: list = None
    force: list = None
    move: list = None
    temper_graph: list = None
    temper_recoil_graph: list = None
    temper_comp_graph: list = None
    
    def __post_init__(self):
        if self.force_list is None:
            self.force_list = []
        if self.move_list is None:
            self.move_list = []
        if self.force is None:
            self.force = []
        if self.move is None:
            self.move = []
        if self.temper_graph is None:
            self.temper_graph = []
        if self.temper_recoil_graph is None:
            self.temper_recoil_graph = []
        if self.temper_comp_graph is None:
            self.temper_comp_graph = []


class ForceManager:
    """Управление коэффициентами и вычислениями силы."""
    
    def __init__(self, force_data: ForceData, signals: ModelSignals, logger, write_bit_func):
        self.data = force_data
        self.signals = signals
        self.logger = logger
        self.write_bit_force_cycle = write_bit_func
    
    def init_koef_timer(self, add_func, calc_func):
        """Инициализация таймеров для расчёта коэффициента."""
        self.write_bit_force_cycle(1)
        
        self.data.timer_add_koef = QTimer()
        self.data.timer_add_koef.setInterval(50)
        self.data.timer_add_koef.timeout.connect(add_func)
        self.data.timer_add_koef.start()

        self.data.timer_calc_koef = QTimer()
        self.data.timer_calc_koef.setInterval(1000)
        self.data.timer_calc_koef.timeout.connect(calc_func)
        self.data.timer_calc_koef.start()
    
    def add_koef_to_list(self, force_clear, force_correct):
        """Добавление значения коэффициента в список."""
        if force_clear != -100000.0:
            self.data.koef_force_list.append(force_correct)
    
    def calc_and_save_koef(self):
        """Расчёт и сохранение среднего значения коэффициента."""
        try:
            self.write_bit_force_cycle(0)
            self.data.timer_add_koef.stop()
            self.data.timer_calc_koef.stop()

            if self.data.koef_force_list:
                self.data.force_koef_offset = round(statistics.fmean(self.data.koef_force_list), 1)
                self.data.koef_force_list.clear()
                self.signals.save_koef_force.emit('done')
            else:
                self.signals.save_koef_force.emit('bad')

        except Exception as e:
            self.logger.error(e)
            self.signals.stbar_msg.emit(f'ERROR in ForceManager/calc_and_save_koef - {e}')
    
    def cancel_koef(self):
        """Отмена расчёта коэффициента."""
        try:
            self.data.force_koef_offset = 0
        except Exception as e:
            self.logger.error(e)
            self.signals.stbar_msg.emit(f'ERROR in ForceManager/cancel_koef - {e}')


class MovementAnalyzer:
    """Анализ движения и определение направления."""
    
    def __init__(self, movement_data: MovementData, signals: ModelSignals, logger):
        self.data = movement_data
        self.signals = signals
        self.logger = logger
    
    def find_start_direction(self, move):
        """Определение стартового направления движения."""
        try:
            if move[0] < move[-1]:
                direction = 'up'
            elif move[0] > move[-1]:
                direction = 'down'
            else:
                direction = False

            if direction:
                self.data.start_direction = direction
                self.data.current_direction = direction
                self.logger.debug(f'Start direction --> {direction}')

        except Exception as e:
            self.logger.error(e)
            self.signals.stbar_msg.emit(f'ERROR in MovementAnalyzer/find_start_direction - {e}')
    
    def find_direction_and_point(self, move):
        """Поиск экстремумов движения."""
        try:
            if self.data.current_direction == 'up':
                max_point = max(move)
                if max_point > move[-1]:
                    if not -1 < max_point < 1:
                        self.data.max_point = max_point
                        self.data.max_pos = True
                        self.data.current_direction = 'down'
                        self.logger.debug(f'Max point --> {max_point}')

            elif self.data.current_direction == 'down':
                min_point = min(move)
                if min_point < move[-1]:
                    if not -1 < min_point < 1:
                        self.data.min_point = min_point
                        self.data.min_pos = True
                        self.data.current_direction = 'up'
                        self.logger.debug(f'Min point --> {min_point}')

        except Exception as e:
            self.logger.error(e)
            self.signals.stbar_msg.emit(f'ERROR in MovementAnalyzer/find_direction_and_point - {e}')
    
    def reset(self):
        """Сброс состояния движения на новый цикл."""
        try:
            self.data.min_pos = False
            self.data.max_pos = False
            self.data.start_direction = 'none'
            self.data.current_direction = 'none'
        except Exception as e:
            self.logger.error(e)
            self.signals.stbar_msg.emit(f'ERROR in MovementAnalyzer/reset - {e}')


class GraphManager:
    """Управление данными и операциями графиков."""
    
    def __init__(self, graph_data: GraphData, signals: ModelSignals, logger):
        self.data = graph_data
        self.signals = signals
        self.logger = logger
    
    def add_data(self, force, move):
        """Добавление данных в графики."""
        try:
            self.data.force_list.extend(force)
            self.data.move_list.extend(move)
        except Exception as e:
            self.logger.error(e)
            self.signals.stbar_msg.emit(f'ERROR in GraphManager/add_data - {e}')
    
    def add_terminator(self):
        """Добавление маркера конца данных."""
        try:
            self.data.force_list.append('end')
            self.data.move_list.append('end')
        except Exception as e:
            self.logger.error(e)
    
    def clear_raw(self):
        """Очистка сырых данных."""
        self.data.force_list = []
        self.data.move_list = []
    
    def clear_circle(self):
        """Очистка данных текущего цикла."""
        self.data.force = []
        self.data.move = []
    
    def clear_temperature(self):
        """Очистка данных температуры."""
        self.data.temper_graph = []
        self.data.temper_recoil_graph = []
        self.data.temper_comp_graph = []


class HardwareController:
    """Управление регистрами и оборудованием (лампочки, буфер, аварийные сигналы)."""
    
    def __init__(self, logger, signals: ModelSignals, writer):
        self.logger = logger
        self.signals = signals
        self.writer = writer
        self.state_dict = {}
        self.switch_dict = {}
        self.state_list = [0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.buffer_state = ['null', 'null']
    
    def update_switch_dict(self, data):
        """Обновление словаря переключателей."""
        try:
            if data is not None:
                self.switch_dict = {**self.switch_dict, **data}
                
        except Exception as e:
            self.logger.error(e)
            self.signals.stbar_msg.emit(f'ERROR in HardwareController/update_switch_dict - {e}')
    
    def update_state_dict(self, data):
        """Обновление словаря состояния."""
        try:
            if data is not None:
                self.state_dict = {**self.state_dict, **data}
                
        except Exception as e:
            self.logger.error(e)
            self.signals.stbar_msg.emit(f'ERROR in HardwareController/update_state_dict - {e}')
    
    def change_state_list(self, reg, parser):
        """Обновление списка состояния из регистра."""
        try:
            bits = ''.join(reversed(bin(reg)[2:].zfill(16)))
            self.state_list = [int(x) for x in bits]
            self.update_state_dict(parser.register_state(reg))
            
        except Exception as e:
            self.logger.error(e)
            self.signals.stbar_msg.emit(f'ERROR in HardwareController/change_state_list - {e}')
    
    def check_buffer_state(self, res, state):
        """Обновление состояния буфера."""
        self.buffer_state = [res, state]
    
    def write_reg_state(self, bit, value, command=None):
        """Запись одного бита в регистр."""
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
            self.signals.stbar_msg.emit(f'ERROR in HardwareController/write_reg_state - {e}')
    
    def write_bit_if_changed(self, state_key: str, bit_pos: int, value: int, command: str = None):
        """Запись бита только при изменении значения."""
        try:
            current_value = self.state_dict.get(state_key, 0)
            if int(current_value) != value:
                self.write_reg_state(bit_pos, value, command=command or state_key)
        except Exception as e:
            self.logger.error(e)
            self.signals.stbar_msg.emit(f'ERROR in HardwareController/write_bit_if_changed - {e}')
    
    def write_bit_force_cycle(self, value):
        """Управление буфером записи силы."""
        try:
            self.buffer_state = ['null', 'null']
            command = 'buffer_on' if value == 1 else 'buffer_off'
            self.write_reg_state(0, value, command)
        except Exception as e:
            self.logger.error(e)
            self.signals.stbar_msg.emit(f'ERROR in HardwareController/write_bit_force_cycle - {e}')
    
    def write_bit_red_light(self, value):
        """Управление красным индикатором."""
        self.write_bit_if_changed('red_light', 1, value)
    
    def write_bit_green_light(self, value):
        """Управление зелёным индикатором."""
        self.write_bit_if_changed('green_light', 2, value)
    
    def write_bit_unblock_control(self):
        """Разблокировка управления."""
        try:
            self.write_reg_state(3, 1, command='unblock_control')
        except Exception as e:
            self.logger.error(e)
            self.signals.stbar_msg.emit(f'ERROR in HardwareController/write_bit_unblock_control - {e}')
    
    def write_bit_emergency_force(self):
        """Сброс аварийного усилия."""
        try:
            self.write_reg_state(4, 1, command='reset_emergency_force')
        except Exception as e:
            self.logger.error(e)
            self.signals.stbar_msg.emit(f'ERROR in HardwareController/write_bit_emergency_force - {e}')
    
    def write_bit_select_temper(self, value):
        """Выбор источника температуры."""
        self.write_bit_if_changed('select_temper', 6, value)
    
    def lamp_all_switch_on(self):
        """Включение всех индикаторов."""
        try:
            self.write_bit_green_light(1)
            self.write_bit_red_light(1)
        except Exception as e:
            self.logger.error(e)
            self.signals.stbar_msg.emit(f'ERROR in HardwareController/lamp_all_switch_on - {e}')
    
    def lamp_all_switch_off(self):
        """Выключение всех индикаторов."""
        try:
            self.write_bit_green_light(0)
            self.write_bit_red_light(0)
        except Exception as e:
            self.logger.error(e)
            self.signals.stbar_msg.emit(f'ERROR in HardwareController/lamp_all_switch_off - {e}')
    
    def lamp_green_switch_on(self):
        """Включение зелёного индикатора."""
        try:
            self.write_bit_green_light(1)
            self.write_bit_red_light(0)
        except Exception as e:
            self.logger.error(e)
            self.signals.stbar_msg.emit(f'ERROR in HardwareController/lamp_green_switch_on - {e}')
    
    def lamp_red_switch_on(self):
        """Включение красного индикатора."""
        try:
            self.write_bit_green_light(0)
            self.write_bit_red_light(1)
        except Exception as e:
            self.logger.error(e)
            self.signals.stbar_msg.emit(f'ERROR in HardwareController/lamp_red_switch_on - {e}')


class CircleAnalyzer:
    """Анализ цикла испытания и расчёт результатов."""
    
    def __init__(self, graph_data: GraphData, movement_data: MovementData, 
                 signals: ModelSignals, logger, calc_data: CalcData, data_test: DataTest = None):
        self.graph = graph_data
        self.movement = movement_data
        self.signals = signals
        self.logger = logger
        self.calc_data = calc_data
        self.data_test = data_test
        
        self.dynamic_push_force = 0
        self.max_recoil = 0
        self.max_comp = 0
        self.power_amort = 0
        self.freq_piston = 0
        
        self.gear_referent = False
    
    def check_full_circle(self, clear_graph_func):
        """Проверка полноты цикла."""
        try:
            if not self.gear_referent:
                clear_graph_func()
                self.movement.reset()
                self.gear_referent = True
                self.logger.debug('Gear referent is True')
            else:
                self._full_circle_done(clear_graph_func)
        except Exception as e:
            self.logger.error(e)
            self.signals.stbar_msg.emit(f'ERROR in CircleAnalyzer/check_full_circle - {e}')
    
    def _full_circle_done(self, clear_graph_func):
        """Завершение обработки полного цикла."""
        try:
            self.logger.debug('Full circle is done')
            
            amort = self.data_test.amort if self.data_test else None
            offset_p = self.calc_data.offset_move_by_hod(amort, self.movement.min_point)
            
            self.graph.force = [round(x * (-1), 2) for x in self.graph.force_list]
            self.graph.move = [round(x + offset_p, 2) for x in self.graph.move_list]

            clear_graph_func()

            max_recoil, max_comp = self.calc_data.middle_min_and_max_force(self.graph.force)
            self.logger.debug(f'Clear recoil --> {max_recoil}, clear comp --> {max_comp}')
            
            # Note: push_force calculation requires data_test context, handled in Model
            self.max_recoil = max_recoil
            self.max_comp = max_comp
            
            self.logger.debug('Full circle response parsing is done')
            self.signals.update_data_graph.emit()
            self.signals.full_cycle_count.emit('+1')

            self.movement.min_pos = False
            self.movement.max_pos = False

        except Exception as e:
            clear_graph_func()
            self.movement.min_pos = False
            self.movement.max_pos = False
            self.logger.error(e)
            self.signals.stbar_msg.emit(f'ERROR in CircleAnalyzer/_full_circle_done - {e}')
    
    def calc_dynamic_push_force(self, static_push_force):
        """Расчёт динамического усилия прижима."""
        try:
            force_min = self.graph.force[self.graph.move.index(min(self.graph.move))]
            force_max = self.graph.force[self.graph.move.index(max(self.graph.move))]
            force_mid = (force_min + force_max) / 2
            self.dynamic_push_force = round((force_mid - static_push_force) / 2 + static_push_force, 2)
            return self.dynamic_push_force
        except Exception as e:
            self.logger.error(e)
            self.signals.stbar_msg.emit(f'ERROR in CircleAnalyzer/calc_dynamic_push_force - {e}')
            return 0
    
    def pars_response_on_circle(self, force, move, flag_fill_graph, flag_search_hod):
        """Обработка данных ответа на цикл."""
        try:
            if self.movement.start_direction == 'none':
                self.movement.find_start_direction(move)
            else:
                if flag_fill_graph:
                    self.graph.add_data(force, move)

                if (self.movement.min_pos and self.movement.max_pos and 
                    min(move) <= self.movement.min_point <= max(move)):
                    hod = round(abs(self.movement.min_point) + abs(self.movement.max_point), 1)
                    if not flag_search_hod:
                        if hod > 30:
                            self.check_full_circle(self.graph.clear_raw)
                        else:
                            self.movement.min_pos = False
                            self.movement.max_pos = False
                    else:
                        self.check_full_circle(self.graph.clear_raw)
                else:
                    self.movement.find_direction_and_point(move)

        except Exception as e:
            self.logger.error(e)
            self.signals.stbar_msg.emit(f'ERROR in CircleAnalyzer/pars_response_on_circle - {e}')


class DataStorage:
    """Управление сохранением и архивированием данных."""
    
    def __init__(self, signals: ModelSignals, logger, calc_data: CalcData, writer: Writer):
        self.signals = signals
        self.logger = logger
        self.calc_data = calc_data
        self.writer = writer
        self.list_lab_result = []
    
    def save_result_cycle(self, move, force, data_test):
        """Сохранение результатов цикла."""
        try:
            if not move or not force:
                return
            
            if data_test.type_test in ('lab', 'lab_cascade', 'conv'):
                data_dict = {'speed': data_test.speed_test,
                             'move': move[:],
                             'force': force[:]}
                self.list_lab_result.append(data_dict)
                        
            self.save_data_in_archive(move, force, data_test)
                    
        except Exception as e:
            self.logger.error(e)
            self.signals.stbar_msg.emit(f'ERROR in DataStorage/save_result_cycle - {e}')
    
    def write_data_in_archive(self, tag, data=None):
        """Запись данных в архив."""
        try:
            save_arch = WriterArch()
            save_arch.timer_writer_arch_start()
            save_arch.write_arch_out(tag, data)
        except Exception as e:
            self.logger.error(e)
            self.signals.stbar_msg.emit(f'ERROR in DataStorage/write_data_in_archive - {e}')
    
    def save_data_in_archive(self, move, force, data_test, temper_data=None):
        """Сохранение полных данных в архив."""
        try:
            if temper_data is None:
                temper_data = {'temper_graph': [], 'temper_recoil_graph': [], 'temper_comp_graph': []}
            
            data_dict = {'move_graph': move[:],
                         'force_graph': force[:],
                         'temper_graph': temper_data.get('temper_graph', []),
                         'temper_recoil_graph': temper_data.get('temper_recoil_graph', []),
                         'temper_comp_graph': temper_data.get('temper_comp_graph', []),
                         'type_test': data_test.type_test,
                         'speed': data_test.speed_test,
                         'operator_name': data_test.operator.name,
                         'operator_rank': data_test.operator.rank,
                         'serial': data_test.serial,
                         'amort': data_test.amort,
                         'flag_push_force': int(data_test.flag_push_force),
                         'static_push_force': data_test.static_push_force,
                         'dynamic_push_force': 0,  # Set by caller
                         'max_temperature': data_test.max_temperature}
            
            self.write_data_in_archive('data', data_dict)
        except Exception as e:
            self.logger.error(e)
            self.signals.stbar_msg.emit(f'ERROR in DataStorage/save_data_in_archive - {e}')
    
    def write_end_test_in_archive(self):
        """Запись маркера конца теста в архив."""
        try:
            self.write_data_in_archive('end_test')
        except Exception as e:
            self.logger.error(e)
            self.signals.stbar_msg.emit(f'ERROR in DataStorage/write_end_test_in_archive - {e}')


class Model:
    def __init__(self):
        self.logger = my_logger.get_logger(__name__)
        self.signals = ModelSignals()
        self.client = Client()
        self.writer = None
        self.reader = Reader()
        self.fc = FreqControl()
        self.parser = ParserSPG023MK()
        self.calc_data = CalcData()
        self.data_test = DataTest()

        # Initialize component data
        self.force_data = ForceData(force_koef=PrgSettings().force_koef)
        self.movement_data = MovementData()
        self.graph_data = GraphData()
        
        # Initialize component managers
        self.hardware = HardwareController(self.logger, self.signals, None)  # writer set later
        self.force_mgr = ForceManager(self.force_data, self.signals, self.logger, 
                                      self.hardware.write_bit_force_cycle)
        self.movement = MovementAnalyzer(self.movement_data, self.signals, self.logger)
        self.graph_mgr = GraphManager(self.graph_data, self.signals, self.logger)
        self.circle = CircleAnalyzer(self.graph_data, self.movement_data, 
                                    self.signals, self.logger, self.calc_data, self.data_test)
        self.storage = DataStorage(self.signals, self.logger, self.calc_data, None)  # writer set later
        
        # Additional state
        self.counter = 0
        self.timer_yellow = None
        self.time_push_yellow = None
        
        self.flag_fill_graph = False
        self.flag_test = False
        self.flag_test_lunch = False
        self.yellow_rattle = False
        self.flag_repeat = False
        self.flag_search_hod = False
        self.traverse_referent = False
        
        self.alarm_tag = ''
        self.flag_alarm = False
        self.lbl_push_force = ''

        self._start_param_model()

    def _init_signals(self):
        self.reader.signals.result.connect(self._reader_result)
        self.reader.signals.error.connect(self.log_error_thread)
        self.writer.signals.check_buffer.connect(self.check_buffer_state)

    def _start_param_model(self):
        self.client.connect_client()

        if self.client.flag_connect:
            self.writer = Writer(self.client.client)
            self.hardware.writer = self.writer  # Set writer after creation
            self.storage.writer = self.writer
            self.writer.timer_writer_start()

            self._init_signals()
            self.reader.init_reader(self.client.client)
            self.reader_start()
            
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

    def check_buffer_state(self, res, state):
        self.hardware.check_buffer_state(res, state)

    def reader_start(self):
        self.reader.reader_start()
        self.status_bar_msg(f'Чтение контроллера запущено')

    def reader_start_test(self):
        self.reader.reader_start_test()
        self.status_bar_msg(f'Чтение буффура контроллера запущено')

    def reader_stop(self):
        self.reader.reader_stop()
        self.status_bar_msg(f'Чтение контроллера остановлено')

    def reader_stop_test(self):
        self.reader.reader_stop_test()
        self.status_bar_msg(f'Чтение буффера контроллера остановлено')

    def reader_exit(self):
        self.reader.reader_exit()
    
    def _update_switch_dict(self, data):
        """Обновление словаря переключателей."""
        try:
            self.hardware.update_switch_dict(data)
        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_update_switch_dict - {e}')
    
    def get_switch_dict(self):
        """Получение словаря переключателей."""
        return getattr(self.hardware, 'switch_dict', {})

    def init_timer_koef_force(self):
        """Инициализация таймеров расчёта коэффициента."""
        self.force_mgr.init_koef_timer(
            self._add_koef_force_in_list,
            self._calc_and_save_force_koef
        )

    def _add_koef_force_in_list(self):
        """Добавление коэффициента в список."""
        self.force_mgr.add_koef_to_list(self.force_clear, self.force_correct)

    def _calc_and_save_force_koef(self):
        """Расчёт и сохранение коэффициента."""
        self.force_mgr.calc_and_save_koef()

    def cancel_koef_force(self):
        """Отмена расчёта коэффициента."""
        self.force_mgr.cancel_koef()

    def _reader_result(self, response, tag):
        try:
            if tag == 'buffer':
                self._pars_buffer_result(response)
            if tag == 'reg':
                self._pars_regs_result(response.get('regs'))
        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_reader_result - {e}')

    def _pars_regs_result(self, res):
        try:
            if not res:
                return
            
            self.force_clear = self.parser.magnitude_effort(res[0], res[1])
            self.force_correct = round(self.force_clear * self.force_data.force_koef, 1)
            self.force_offset = round(self.force_correct - self.force_data.force_koef_offset, 1)

            self.move_now = self.parser.movement_amount(res[2])
            self.move_traverse = round(0.5 * self.parser.movement_amount(res[6]), 1)

            self.counter = self.parser.counter_time(res[4])
            self.data_test.force_alarm = self.parser.emergency_force(res[10], res[11])

            self.data_test.first_temperature = self.parser.temperature_value(res[7], res[8])
            self.data_test.second_temperature = self.parser.temperature_value(res[12], res[13])
            temp = max(self.data_test.first_temperature, self.data_test.second_temperature)
            if temp > self.data_test.max_temperature:
                self.data_test.max_temperature = temp

            self._update_switch_dict(self.parser.switch_state(res[5]))
            self.hardware.change_state_list(res[3], self.parser)

            if self.data_test.type_test == 'hand':
                self.signals.win_set_update.emit()

        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/_pars_regs_result - {e}')

    def _pars_buffer_result(self, response):
        try:
            data = self.parser.discard_left_data(response)

            if data is None:
                self.logger.debug('Response from buffer controller is None')
                return

            self.force_clear = data.get('force')[-1]
            self.force_correct = round(self.force_clear * self.force_data.force_koef, 1)
            self.force_offset = round(self.force_correct - self.force_data.force_koef_offset, 1)
            force_buf = [x * self.force_data.force_koef - self.force_data.force_koef_offset for x in data.get('force')]

            self.move_now = data.get('move')[-1]
            move_buf = data.get('move')

            self.counter = data.get('count')[-1]

            self.data_test.max_temperature = self.calc_data.check_temperature(
                data.get('temper'), self.data_test.max_temperature
            )
            self.data_test.temperature = data.get('temper')[-1]

            self.hardware.change_state_list(data.get('state')[-1], self.parser)

            if self.data_test.type_test == 'hand':
                self.signals.win_set_update.emit()
            else:
                self._pars_response_on_circle(force_buf, move_buf)

        except Exception as e:
            if str(e) != 'list index out of range':
                self.logger.error(e)
                self.status_bar_msg(f'ERROR in model/_pars_buffer_result - {e}')

    def _pars_response_on_circle(self, force, move):
        """Обработка данных цикла через CircleAnalyzer."""
        self.circle.pars_response_on_circle(force, move, self.flag_fill_graph, self.flag_search_hod)

    def write_emergency_force(self, value):
        try:
            arr = self.calc_data.emergency_force(value)
            self.writer.write_out('reg', values=arr, reg_write=0x200a)
        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/write_emergency_force - {e}')

    def fc_control(self, tag: str, adr: int, speed: float = None, freq: int = None, hod: int = None):
        try:
            if self.hardware.state_dict.get('lost_control'):
                self.hardware.write_bit_unblock_control()

            if self.hardware.state_dict.get('excess_force'):
                self.hardware.write_bit_emergency_force()
                
            if hod is None:
                hod = 120 if self.data_test.amort is None else self.data_test.amort.hod
                
            values, comm = self.fc.freq_command(tag, adr, speed, freq, hod)
            self.writer.write_out('FC', freq_command=values, command=comm)
            
        except Exception as e:
            self.logger.error(e)
            self.status_bar_msg(f'ERROR in model/fc_control - {e}')

    # Proxy methods to hardware controller for backward compatibility
    def write_bit_red_light(self, value):
        self.hardware.write_bit_red_light(value)

    def write_bit_green_light(self, value):
        self.hardware.write_bit_green_light(value)

    def write_bit_force_cycle(self, value):
        self.hardware.write_bit_force_cycle(value)

    def write_bit_unblock_control(self):
        self.hardware.write_bit_unblock_control()

    def write_bit_emergency_force(self):
        self.hardware.write_bit_emergency_force()

    def write_bit_select_temper(self, value):
        self.hardware.write_bit_select_temper(value)

    def lamp_all_switch_on(self):
        self.hardware.lamp_all_switch_on()

    def lamp_all_switch_off(self):
        self.hardware.lamp_all_switch_off()

    def lamp_green_switch_on(self):
        self.hardware.lamp_green_switch_on()

    def lamp_red_switch_on(self):
        self.hardware.lamp_red_switch_on()

    # Proxy methods to graph manager
    def clear_data_in_graph(self):
        self.graph_mgr.clear_raw()

    def clear_data_in_circle_graph(self):
        self.graph_mgr.clear_circle()

    def clear_data_in_temper_graph(self):
        self.graph_mgr.clear_temperature()

    # Proxy methods to storage
    def save_result_cycle(self):
        self.storage.save_result_cycle(
            self.graph_data.move, 
            self.graph_data.force, 
            self.data_test
        )

    def save_data_in_archive(self):
        temper_data = {
            'temper_graph': self.graph_data.temper_graph,
            'temper_recoil_graph': self.graph_data.temper_recoil_graph,
            'temper_comp_graph': self.graph_data.temper_comp_graph,
        }
        self.storage.save_data_in_archive(
            self.graph_data.move,
            self.graph_data.force,
            self.data_test,
            temper_data
        )
        self.clear_data_in_circle_graph()

    def write_end_test_in_archive(self):
        self.storage.write_end_test_in_archive()

    def write_data_in_archive(self, tag, data=None):
        self.storage.write_data_in_archive(tag, data)

    def reset_current_circle(self):
        """Сброс состояния текущего цикла."""
        self.movement.reset()

    # Properties for direct access (backward compatibility)
    @property
    def state_dict(self):
        return self.hardware.state_dict

    @property
    def state_list(self):
        return self.hardware.state_list

    @property
    def switch_dict(self):
        return self.hardware.switch_dict

    @property
    def buffer_state(self):
        return self.hardware.buffer_state

    @property
    def force_clear(self):
        return self.force_data.force_clear
    
    @force_clear.setter
    def force_clear(self, value):
        self.force_data.force_clear = value

    @property
    def force_correct(self):
        return self.force_data.force_correct
    
    @force_correct.setter
    def force_correct(self, value):
        self.force_data.force_correct = value

    @property
    def force_offset(self):
        return self.force_data.force_offset
    
    @force_offset.setter
    def force_offset(self, value):
        self.force_data.force_offset = value

    @property
    def force_koef_offset(self):
        return self.force_data.force_koef_offset

    @property
    def move_now(self):
        return self.movement_data.move_now
    
    @move_now.setter
    def move_now(self, value):
        self.movement_data.move_now = value

    @property
    def move_traverse(self):
        return self.movement_data.move_traverse
    
    @move_traverse.setter
    def move_traverse(self, value):
        self.movement_data.move_traverse = value

    @property
    def min_point(self):
        return self.movement_data.min_point
    
    @min_point.setter
    def min_point(self, value):
        self.movement_data.min_point = value

    @property
    def max_point(self):
        return self.movement_data.max_point
    
    @max_point.setter
    def max_point(self, value):
        self.movement_data.max_point = value

    @property
    def min_pos(self):
        return self.movement_data.min_pos
    
    @min_pos.setter
    def min_pos(self, value):
        self.movement_data.min_pos = value

    @property
    def max_pos(self):
        return self.movement_data.max_pos
    
    @max_pos.setter
    def max_pos(self, value):
        self.movement_data.max_pos = value

    @property
    def force_list(self):
        return self.graph_data.force_list

    @property
    def move_list(self):
        return self.graph_data.move_list

    @property
    def force(self):
        return self.graph_data.force

    @property
    def move(self):
        return self.graph_data.move

    @property
    def temper_graph(self):
        return self.graph_data.temper_graph

    @property
    def temper_recoil_graph(self):
        return self.graph_data.temper_recoil_graph

    @property
    def temper_comp_graph(self):
        return self.graph_data.temper_comp_graph

    @property
    def dynamic_push_force(self):
        return self.circle.dynamic_push_force

    @property
    def max_recoil(self):
        return self.circle.max_recoil

    @property
    def max_comp(self):
        return self.circle.max_comp

    @property
    def power_amort(self):
        return self.circle.power_amort

    @property
    def freq_piston(self):
        return self.circle.freq_piston

    @property
    def gear_referent(self):
        return self.circle.gear_referent

    @property
    def start_direction(self):
        return self.movement_data.start_direction

    @property
    def current_direction(self):
        return self.movement_data.current_direction

    @property
    def list_lab_result(self):
        return self.storage.list_lab_result

    @property
    def koef_force_list(self):
        return self.force_data.koef_force_list

    @property
    def hod_measure(self):
        return self.movement_data.hod_measure
    
    @hod_measure.setter
    def hod_measure(self, value):
        self.movement_data.hod_measure = value
