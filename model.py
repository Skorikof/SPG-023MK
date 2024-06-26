import inspect
import time

import crcmod
import serial
import numpy as np
import modbus_tk.defines as cst
import modbus_tk.modbus_rtu as modbus_rtu
from struct import pack, unpack
from my_threads import LogWriter, Writer, Reader
from settings import PrgSettings
from PyQt5.QtCore import QObject, QThreadPool, pyqtSignal, QTimer


class WinSignals(QObject):
    connect_ctrl = pyqtSignal()
    stbar_msg = pyqtSignal(str)
    read_start = pyqtSignal()
    start_test = pyqtSignal()
    stop_test = pyqtSignal()
    read_stop = pyqtSignal()
    read_exit = pyqtSignal()
    read_finish = pyqtSignal(dict)
    full_cycle = pyqtSignal()
    update_graph_settings = pyqtSignal()
    test_launch = pyqtSignal()


class Model:
    def __init__(self):
        self.signals = WinSignals()

        self.set_connect = PrgSettings().connect
        self.set_regs = PrgSettings().registers
        self.threadpool = QThreadPool()

        self.client = None
        self.log_writer = None
        self.reader = None
        self.writer = None
        self.writer_flag_init = False
        self.flag_write = False
        # self.timer_connect = None
        self.timer_yellow = None
        self.amort = None
        self.count_msg = 0
        self.force_graph = []
        self.move_graph = []
        # self.time_response = time.monotonic()
        self.time_push_yellow = None
        self.yellow_rattle = False

        self.start_param_model()

    def start_param_model(self):
        self.init_connect()
        time.sleep(0.1)
        # self.init_timer_connect()
        self.init_timer_yellow_btn()
        if self.client:
            self.init_reader()
            # self.reader_start()
            # time.sleep(0.1)
            # self.timer_connect.start()

        else:
            self.log_error(f'Нет подключения к контроллеру')

    def save_log(self, mode_s, msg_s):
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

    def log_error(self, txt_log):
        self.status_bar_msg(txt_log)
        self.save_log('error', txt_log)

    def log_info(self, txt_log):
        self.status_bar_msg(txt_log)
        self.save_log('info', txt_log)

    def current_amort_model(self, obj):
        try:
            self.amort = obj

        except Exception as e:
            self.log_error(f'ERROR in model/current_amort - {e}')

    def init_connect(self):
        try:
            self.client = modbus_rtu.RtuMaster(serial.Serial(port=self.set_connect.get('COM', 4),
                                                             baudrate=self.set_connect.get('baudrate', 921600),
                                                             bytesize=self.set_connect.get('bytesize', 8),
                                                             parity=self.set_connect.get('parity', 'N'),
                                                             stopbits=self.set_connect.get('stopbits', 1),
                                                             timeout=0.000001))

            self.client.set_timeout(1.0)
            self.client.set_verbose(True)
            self.client.open()
            self.set_connect['connect'] = True
            self.status_bar_msg(f'Контроллер подключен')

        except Exception as e:
            self.client = None
            self.log_error(f'ERROR in model/init_connect - {e}')

    def disconnect_client(self):
        if self.client:
            self.client.close()
            self.set_connect['connect'] = False
            # self.client = None
            self.status_bar_msg(f'Контроллер отключен')

    # def check_connect_client(self):
    #     try:
    #         check_time = time.monotonic()
    #         if check_time - self.time_response > 5:
    #             print(f'Подключение к контроллеру отсутствует')
    #             self.timer_connect.stop()
    #             print(f'Таймер контроля посылки остановлен')
    #             # self.signals.connect_ctrl.emit()
    #             self.reader_stop()
    #             print(f'Чтение контроллера остановлено')
    #             time.sleep(0.1)
    #             self.disconnect_client()
    #             print(f'Подключение разорвано')
    #             time.sleep(0.5)
    #             self.client.open()
    #             time.sleep(0.1)
    #             self.time_response = time.monotonic()
    #             if self.set_connect['connect']:
    #                 print(f'Подключение восстановлено')
    #                 self.timer_connect.start()
    #                 print(f'Таймер контроля посылки запущен')
    #                 # self.signals.connect_ctrl.emit()
    #                 self.reader_start()
    #                 print(f'Поток чтения запущен')
    #
    #     except Exception as e:
    #         self.log_error(f'ERROR in model/check_connect_client - {e}')

    # def init_timer_connect(self):
    #     try:
    #         self.timer_connect = QTimer()
    #         self.timer_connect.setInterval(3000)
    #         self.timer_connect.timeout.connect(self.check_connect_client)
    #
    #     except Exception as e:
    #         self.log_error(f'ERROR in model/init_timer_connect - {e}')

    def init_reader(self):
        self.reader = Reader(self.client, cst)
        self.reader.signals.thread_log.connect(self.log_info)
        self.reader.signals.thread_err.connect(self.log_error)
        self.reader.signals.read_result.connect(self.reader_result)
        self.signals.read_start.connect(self.reader.start_read)
        self.signals.start_test.connect(self.reader.start_test)
        self.signals.read_stop.connect(self.reader.stop_read)
        self.signals.stop_test.connect(self.reader.stop_test)
        self.signals.read_exit.connect(self.reader.exit_read)
        self.threadpool.start(self.reader)

    def reader_start(self):
        self.count_msg = 0
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

    def delete_left_data(self, force: list, move: list):
        try:
            force_list = []
            move_list = []

            force = np.array(force, int)
            move = np.array(move, float)

            for i in range(len(force)):
                if force[i] != -100000:
                    force_list.append(force[i])
                    move_list.append(move[i])

            return force_list, move_list

        except Exception as e:
            self.log_error(f'ERROR in model/delete_left_data - {e}')

    def reader_result(self, response, tag):
        try:
            if tag == 'buffer':

                force_list, move_list = self.delete_left_data(response.get('force'), response.get('move'))

                # for i in range(len(response['force'])):
                #     if response['force'][i] != -100000:
                #         force_list.append(response.get('force')[i])
                #         move_list.append(response.get('move')[i])
                #         self.count_msg += 1
                #         self.status_bar_msg(f'Получен ответ контроллера - {self.count_msg}')
                #     else:
                #         pass

                if not force_list:
                    print(f'Пришла пустая посылка')

                else:
                    self.count_msg += 1
                    self.status_bar_msg(f'Получен ответ контроллера - {self.count_msg}')

                    self.set_regs['force_list'] = [x for x in force_list]
                    self.set_regs['move_list'] = [x for x in move_list]
                    self.set_regs['temp_list'] = [x for x in response.get('temp') if x != -100.0]

                    self.set_regs['counter_time'] = response.get('count')[-1]
                    self.set_regs['force'] = force_list[-1]
                    self.set_regs['move'] = move_list[-1]

                    self.register_state(response.get('state')[-1])

                    self.check_temperature(self.set_regs['temp_list'])

                    print(f'Счётчик --> {self.set_regs.get("counter_time")}')
                    print(f'Усилие --> {self.set_regs.get("force_list")}')
                    print(f'Перемещение --> {self.set_regs.get("move_list")}')
                    print(f'Состояние --> {self.set_regs.get("state")[-1]:b}')
                    print(f'Температура --> {self.set_regs.get["temp_list"]}')
                    print(f'======================')

                    self.signals.read_finish.emit(self.set_regs)

                    self.pars_response_on_circle(self.set_regs.get('force_list'), self.set_regs.get('move_list'))

            if tag == 'reg':
                force = self.magnitude_effort(response['regs'][0], response['regs'][1])
                move = -1 * self.movement_amount(response['regs'][2])
                self.register_state(response['regs'][3])
                self.set_regs['counter_time'] = self.counter_time(response['regs'][4])
                self.switch_state(response['regs'][5])
                self.set_regs['traverse_move'] = round(-0.5 * self.movement_amount(response['regs'][6]), 1)
                self.set_regs['temperature'] = self.temperature_value(response['regs'][7], response['regs'][8])
                self.set_regs['force_alarm'] = self.emergency_force(response['regs'][10], response['regs'][11])

                if force == -100000.0:
                    pass
                    force, move = None, None

                else:
                    self.set_regs['force'] = force
                    self.set_regs['move'] = move
                    self.count_msg += 1
                    self.status_bar_msg(f'Получен ответ контроллера - {self.count_msg}')

                    self.signals.read_finish.emit(self.set_regs)

            # self.time_response = time.monotonic()

            if self.count_msg == 10000:
                self.count_msg = 0

            if self.set_regs.get('test_launch', False) is True:
                if not self.timer_yellow.isActive():
                    self.timer_yellow.start()
                else:
                    pass

        except Exception as e:
            self.log_error(f'ERROR in model/reader_result - {e}')

    def init_timer_yellow_btn(self):
        try:
            self.timer_yellow = QTimer()
            self.timer_yellow.setInterval(200)
            self.timer_yellow.timeout.connect(self.yellow_btn_click)

        except Exception as e:
            self.log_error(f'ERROR in model/init_timer_yellow_btn - {e}')

    def yellow_btn_click(self):
        try:
            if self.set_regs['yellow_btn'] is False:
                if self.yellow_rattle is False:
                    self.time_push_yellow = time.monotonic()
                    self.signals.test_launch.emit()
                    self.yellow_rattle = True

                else:
                    time_signal = time.monotonic() - self.time_push_yellow
                    if 2 < time_signal:
                        self.time_push_yellow = time.monotonic()
                        self.signals.test_launch.emit()
                        self.yellow_rattle = True

                    else:
                        pass
            else:
                self.timer_yellow.stop()

        except Exception as e:
            self.log_error(f'ERROR in model/yellow_btn_click - {e}')

    def find_start_point(self, move: float):
        try:
            self.set_regs['start_point'] = move
            self.set_regs['start_pos'] = True
            print(f'Find start point --> {move}')

        except Exception as e:
            self.log_error(f'ERROR in model/find_start_point - {e}')

    def find_start_direction(self, move: list):
        try:
            start_point = self.set_regs.get('start_point')
            if start_point < move[-1]:
                self.set_regs['start_direction'] = 'up'
                self.set_regs['current_direction'] = 'up'

            elif start_point > move[-1]:
                self.set_regs['start_direction'] = 'down'
                self.set_regs['current_direction'] = 'down'

            else:
                self.set_regs['start_direction'] = None

            print(f'Start direction --> {self.set_regs["start_direction"]}')

        except Exception as e:
            self.log_error(f'ERROR in model/find_start_direction - {e}')

    def add_data_on_graph(self, force: list, move: list):
        """Добавление координаты в списки усилия и перемещения"""
        try:
            self.force_graph.extend(force)
            self.move_graph.extend(move)

        except Exception as e:
            self.log_error(f'ERROR in model/add_data_on_graph - {e}')

    def pars_response_on_circle(self, force: list, move: list):
        try:
            if not self.set_regs.get('start_pos'):
                self.find_start_point(move[0])

            if not self.set_regs.get('start_direction'):
                self.find_start_direction(move)

            if self.set_regs.get('current_direction') == 'up':
                self.add_data_on_graph(force, move)
                if max(move) > move[-1] + 1:
                    self.set_regs['max_point'] = max(move)
                    self.set_regs['max_pos'] = True

                    print(f'Find max point --> {max(move)}')

                    self.set_regs['current_direction'] = 'down'

            elif self.set_regs.get('current_direction') == 'down':
                self.add_data_on_graph(force, move)
                if min(move) < move[-1] - 1:
                    self.set_regs['min_point'] = min(move)
                    self.set_regs['min_pos'] = True

                    self.set_regs['start_point'] = self.set_regs.get('min_point') + 10

                    print(f'Find min point --> {min(move)}')

                    self.set_regs['current_direction'] = 'up'

            if self.set_regs.get('min_pos') and self.set_regs.get('max_pos') \
                    and (self.set_regs.get('start_point') in move):

                print(f'Full cycle is done!')

                force_list = [x for x in self.force_graph]
                move_list = [x for x in self.move_graph]

                self.force_graph = []
                self.move_graph = []

                self.full_circle_done(force_list, move_list)

        except Exception as e:
            self.log_error(f'ERROR in model/pars_response_on_circle - {e}')

    def approximate_data(self, x: list, y: list):
        try:
            x = np.array(x, float)
            y = np.array(y, int)
            t = np.polyfit(x, y, 4)
            f = np.poly1d(t)
            y = f(x)

            return y

        except Exception as e:
            self.log_error(f'ERROR in model/approximate_data - {e}')

    def full_circle_done(self, force: list, move: list):
        try:
            if self.set_regs.get('gear_referent', False) is False:
                teor_hod = self.amort.hod
                if teor_hod == 120:
                    teor_hod = 118
                fact_hod = abs(self.set_regs['min_point']) + abs(self.set_regs['max_point'])

                if abs(teor_hod - fact_hod) > 2:
                    print(f'Ход несоответствует заданному')

                else:
                    self.set_regs['gear_referent'] = True
                    self.set_regs['start_pos'] = False
                    self.set_regs['start_direction'] = False

            else:
                self.set_regs['max_comp'] = max(force)
                self.set_regs['max_recoil'] = abs(min(force))
                self.set_regs['force_graph'] = [x for x in force]
                # self.set_regs['move_graph'] = [x for x in move]
                self.set_regs['move_graph'] = self.approximate_data(force, move)
                self.signals.full_cycle.emit()
                self.signals.update_graph_settings.emit()

            self.set_regs['min_pos'] = False
            self.set_regs['max_pos'] = False

        except Exception as e:
            self.log_error(f'ERROR in model/full_circle_done - {e}')

    def init_writer(self, tag, values=None, reg_write=None, freq_command=None):
        try:
            self.writer = Writer(client=self.client,
                                 cst=cst,
                                 tag=tag,
                                 values=values,
                                 reg_write=reg_write,
                                 freq_command=freq_command)

            if not self.writer_flag_init:
                self.writer.signals.thread_log.connect(self.log_info)
                self.writer.signals.thread_err.connect(self.log_error)
                self.writer.signals.write_finish.connect(self.writer_result)
                self.writer_flag_init = True
            self.threadpool.start(self.writer)

        except Exception as e:
            self.log_error(f'ERROR in model/init_writer - {e}')

    def writer_result(self, state):
        self.flag_write = state

    def write_reg_state(self, com_list):
        try:
            res = 0
            values = []
            for i in range(16):
                res = res + com_list[i] * 2 ** i

            values.append(res)

            self.init_writer('reg', values, 0x2003)

        except Exception as e:
            self.log_error(f'ERROR in model/write_reg_state - {e}')

    def change_list_state(self, bit, value):
        try:
            com_list = [x for x in self.set_regs.get('list_state')]
            com_list[bit] = value

            self.write_reg_state(com_list)

        except Exception as e:
            self.log_error(f'ERROR in model/change_list_state - {e}')

    def write_bit_force_cycle(self, value):
        try:
            self.change_list_state(0, value)

        except Exception as e:
            self.log_error(f'ERROR in model/write_bit_force_cycle - {e}')

    def write_bit_red_light(self, value):
        try:
            self.change_list_state(1, value)

        except Exception as e:
            self.log_error(f'ERROR in model/write_bit_red_light - {e}')

    def write_bit_green_light(self, value):
        try:
            self.change_list_state(2, value)

        except Exception as e:
            self.log_error(f'ERROR in model/write_bit_green_light - {e}')

    def write_bit_unblock_control(self):
        try:
            self.change_list_state(3, 1)

        except Exception as e:
            self.log_error(f'ERROR in model/write_bit_unblock_control - {e}')

    def write_bit_emergency_force(self):
        try:
            self.change_list_state(4, 1)

        except Exception as e:
            self.log_error(f'ERROR in model/write_bit_emergency_force - {e}')

    def write_emergency_force(self, value):
        try:
            arr = []
            val = pack('>f', value)
            for i in range(0, 4, 2):
                arr.append(int((hex(val[i])[2:] + hex(val[i + 1])[2:]), 16))

            self.init_writer('reg', arr, 0x200a)

        except Exception as e:
            self.log_error(f'ERROR in model/write_emergency_force - {e}')

    def motor_command(self, command):
        try:
            command = command + self.calc_crc(command)
            values = self.calc_values_write(command)

            self.init_writer('FC', freq_command=values)

        except Exception as e:
            self.log_error(f'ERROR in model/motor_command - {e}')

    def write_frequency(self, adr_freq, freq):
        try:
            freq_hex = hex(freq)[2:].zfill(4)
            freq_hex = f'0{adr_freq}06010D{freq_hex}'
            self.motor_command(freq_hex)

        except Exception as e:
            self.log_error(f'ERROR in model/write_frequency - {e}')

    def motor_up(self, adr_freq):
        try:
            com_hex = f'0{adr_freq}0620000002'
            self.motor_command(com_hex)

        except Exception as e:
            self.log_error(f'ERROR in model/motor_up - {e}')

    def motor_down(self, adr_freq):
        try:
            com_hex = f'0{adr_freq}0620000001'
            self.motor_command(com_hex)

        except Exception as e:
            self.log_error(f'ERROR in model/motor_down - {e}')

    def motor_stop(self, adr_freq):
        try:
            com_hex = f'0{adr_freq}0620000003'
            self.motor_command(com_hex)

        except Exception as e:
            self.log_error(f'ERROR in model/motor_stop - {e}')
        
    def calc_crc(self, data):
        try:
            byte_data = bytes.fromhex(data)
            crc16 = crcmod.mkCrcFun(0x18005, initCrc=0xFFFF, rev=True, xorOut=0x0000)
            crc_str = hex(crc16(byte_data))[2:].zfill(4)
            crc_str = crc_str[2:] + crc_str[:2]

            return crc_str

        except Exception as e:
            self.log_error(f'ERROR in model/calc_crc - {e}')

    def calc_values_write(self, data):
        try:
            val_regs = []
            for i in range(0, len(data), 4):
                temp = data[i:i + 4]
                temp_byte = bytearray.fromhex(temp)
                temp_val = int.from_bytes(temp_byte, 'big')
                val_regs.append(temp_val)

            return val_regs

        except Exception as e:
            self.log_error(f'ERROR in model/calc_values_write - {e}')

    def check_temperature(self, temp_list: list):
        try:
            self.set_regs['temperature'] = temp_list[-1]

            if max(temp_list) > self.set_regs['max_temperature']:
                self.set_regs['max_temperature'] = max(temp_list)

        except Exception as e:
            self.log_error(f'ERROR in model/find_max_temperature - {e}')

    def magnitude_effort(self, low_reg, big_reg):
        """Текущая величина усилия"""
        try:
            val_temp = round(unpack('f', pack('<HH', big_reg, low_reg))[0], 0)

            return val_temp

        except Exception as e:
            self.log_error(f'ERROR in model/magnitude_effort - {e}')

    def movement_amount(self, data) -> float:
        """Текущая величина перемещения штока аммортизатора или траверсы"""
        try:
            result = round(0.1 * (int.from_bytes(pack('>H', data), 'big', signed=True)), 1)

            return result

        except Exception as e:
            self.log_error(f'ERROR in model/movement_amount - {e}')

    def register_state(self, register):
        """Регистр состояния 0х2003"""
        try:
            temp = bin(register)[2:].zfill(16)
            bits = ''.join(reversed(temp))

            self.set_regs['list_state'] = [int(x) for x in bits]

            self.set_regs['cycle_force'] = bool(self.set_regs.get('list_state')[0])
            self.set_regs['red_light'] = bool(self.set_regs.get('list_state')[1])
            self.set_regs['green_light'] = bool(self.set_regs.get('list_state')[2])
            self.set_regs['lost_control'] = bool(self.set_regs.get('list_state')[3])
            self.set_regs['excess_force'] = bool(self.set_regs.get('list_state')[4])
            self.set_regs['safety_fence'] = bool(self.set_regs.get('list_state')[8])
            self.set_regs['state_freq'] = bool(self.set_regs.get('list_state')[11])
            self.set_regs['state_force'] = bool(self.set_regs.get('list_state')[12])
            self.set_regs['yellow_btn'] = bool(self.set_regs.get('list_state')[13])

        except Exception as e:
            self.log_error(f'ERROR in model/register_state - {e}')

    def counter_time(self, register):
        """Регистр счётчика времени"""
        try:
            return register

        except Exception as e:
            self.log_error(f'ERROR in model/counter_time - {e}')

    def switch_state(self, register):
        """Регистр состояния входов модуля МВ110-224.16ДН"""
        try:
            temp = bin(register)[2:].zfill(16)
            bits = ''.join(reversed(temp))

            # self.set_regs['safety_fence'] = int(bits[0])
            self.set_regs['traverse_block_1'] = bool(int(bits[1]))
            self.set_regs['traverse_block_2'] = bool(int(bits[2]))
            # self.set_regs['yellow_btn'] = int(bits[3])
            self.set_regs['alarm_highest_position'] = bool(int(bits[8]))
            self.set_regs['alarm_lowest_position'] = bool(int(bits[9]))
            self.set_regs['highest_position'] = bool(int(bits[12]))
            self.set_regs['lowest_position'] = bool(int(bits[13]))

        except Exception as e:
            self.log_error(f'ERROR in model/switch_state - {e}')

    def temperature_value(self, low_reg, big_reg):
        """Величина температуры с модуля МВ-110-224-2А"""
        try:
            val_temp = round(unpack('f', pack('<HH', big_reg, low_reg))[0], 1)

            return val_temp

        except Exception as e:
            self.log_error(f'ERROR in model/temperature_value - {e}')

    def emergency_force(self, low_reg, big_reg):
        """Аварийное усилие"""
        try:
            val_temp = unpack('f', pack('<HH', big_reg, low_reg))[0]

            return val_temp

        except Exception as e:
            self.log_error(f'ERROR in model/emergency_force - {e}')

    def calculate_freq(self, speed):
        """Пересчёт скорости в частоту для записи в частотник"""
        try:
            koef = (3 * 7) / (2 * 3.1415 * 0.98)
            hod = self.set_regs.get('hod') / 1000
            radius = hod / 2
            freq = int(100 * (koef * speed) / radius)

            return freq

        except Exception as e:
            self.log_error(f'ERROR in model/calculate_freq - {e}')
