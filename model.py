import inspect
import serial
import crcmod
import numpy as np
import modbus_tk.defines as cst
import modbus_tk.modbus_rtu as modbus_rtu
from struct import pack, unpack
from my_threads import LogWriter, Writer, Reader
from settings import PrgSettings
from PyQt5.QtCore import QObject, QThreadPool, pyqtSignal, QTimer


class WinSignals(QObject):
    stbar_msg = pyqtSignal(str)
    # read_buffer_start = pyqtSignal(object, object, int, int, int)
    # read_buffer_stop = pyqtSignal()
    # read_buffer_exit = pyqtSignal()
    read_start = pyqtSignal(object, object, object)
    read_stop = pyqtSignal()
    read_exit = pyqtSignal()
    read_finish = pyqtSignal()


class Model:
    def __init__(self):
        self.data_response = {}
        self.force = []
        self.signals = WinSignals()

        self.set_connect = PrgSettings().connect
        self.set_regs = PrgSettings().registers
        self.set_state = PrgSettings().state
        self.threadpool = QThreadPool()

        self.log_writer = None
        self.reader_buffer = None
        self.reader = None
        self.writer = None
        self.writer_flag_init = False
        self.flag_write = False
        self.timer_process = None
        self.count_msg = 0

    def start_param(self):
        self.set_connect['cst'] = cst
        # self.init_connect()
        # self.write_emergency_force()
        # self.init_reader()
        # self.init_reader_buffer()
        # self.init_timer()

    # def init_timer(self):
    #     try:
    #         self.timer_process = QTimer()
    #         self.timer_process.setInterval(80)
    #         self.timer_process.timeout.connect(self.control_process)
    #         self.timer_process.start()
    #
    #     except Exception as e:
    #         txt_log = 'ERROR in model/init_timer - {}'.format(e)
    #         self.status_bar_msg(txt_log)
    #         self.save_log('error', str(e))

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

    def control_process(self):
        try:
            self.change_list_state(3, 1)

        except Exception as e:
            txt_log = 'ERROR in model/control_process - {}'.format(e)
            self.status_bar_msg(txt_log)
            self.save_log('error', str(e))

    def status_bar_msg(self, txt_bar):
        self.signals.stbar_msg.emit(txt_bar)

    def init_connect(self):
        try:
            client = modbus_rtu.RtuMaster(serial.Serial(port=self.set_connect.get('COM'),
                                                        baudrate=self.set_connect.get('baudrate'),
                                                        bytesize=self.set_connect.get('bytesize'),
                                                        parity=self.set_connect.get('parity'),
                                                        stopbits=self.set_connect.get('stopbits'),
                                                        timeout=0.000001))

            client.set_timeout(1.0)
            client.set_verbose(True)
            client.open()

            self.set_connect['client'] = client
            self.set_connect['connect'] = True
            txt_log = 'Контроллер подключен'
            self.status_bar_msg(txt_log)

        except Exception as e:
            self.set_connect['connect'] = False
            txt_log = 'ERROR in model/init_connect - {}'.format(e)
            self.status_bar_msg(txt_log)
            self.save_log('error', str(e))

    def disconnect_client(self):
        client = self.set_connect.get('client')
        if client:
            client.close()
            self.set_connect['client'] = None
            self.set_connect['connect'] = False
            txt_log = 'Контроллер отключен'
            self.status_bar_msg(txt_log)

    def thread_log_msg(self, txt_log):
        print(txt_log)
        self.status_bar_msg(txt_log)
        self.save_log('info', txt_log)

    def thread_err_log(self, txt_log):
        print(txt_log)
        self.status_bar_msg(txt_log)
        self.save_log('error', txt_log)

    # def init_reader_buffer(self):
    #     self.reader_buffer = Reader(self.set_connect['client'], cst)
    #     self.reader_buffer.signals.thread_log.connect(self.thread_log_msg)
    #     self.reader_buffer.signals.thread_err.connect(self.thread_err_log)
    #     self.reader_buffer.signals.read_result.connect(self.reader_buffer_result)
    #     self.signals.read_buffer_start.connect(self.reader_buffer.start_read)
    #     self.signals.read_buffer_stop.connect(self.reader_buffer.stop_read)
    #     self.signals.read_buffer_exit.connect(self.reader_buffer.exit_read)
    #     self.threadpool.start(self.reader_buffer)
    #
    # def reader_buffer_start(self):
    #     start_reg = self.set_regs.get('start_reg_buffer')
    #     count_reg = self.set_regs.get('count_reg_buffer')
    #     dev_id = self.set_regs.get('dev_id')
    #
    #     self.signals.read_buffer_start.emit(client=self.set_connect['client'],
    #                                         cst=cst,
    #                                         start_reg=start_reg,
    #                                         count_reg=count_reg,
    #                                         dev_id=dev_id)
    #
    # def reader_buffer_stop(self):
    #     self.signals.read_buffer_stop.emit()
    #
    # def reader_buffer_exit(self):
    #     self.signals.read_buffer_exit.emit()
    #
    # def reader_buffer_result(self, registers):
    #     print(registers)

    def init_reader(self):
        self.reader = Reader()
        self.reader.signals.thread_log.connect(self.thread_err_log)
        self.reader.signals.thread_err.connect(self.thread_err_log)
        self.reader.signals.read_result.connect(self.reader_result)
        self.signals.read_start.connect(self.reader.start_read)
        self.signals.read_stop.connect(self.reader.stop_read)
        self.signals.read_exit.connect(self.reader.exit_read)
        self.threadpool.start(self.reader)

    def reader_start(self):
        self.count_msg = 0
        client = self.set_connect.get('client')
        self.signals.read_start.emit(client, cst, self.set_regs)

    def reader_stop(self):
        self.signals.read_stop.emit()

    def reader_exit(self):
        self.signals.read_exit.emit()

    def reader_result(self, rr):
        try:
            txt_log = 'Идёт чтение контроллера'
            self.status_bar_msg(txt_log)
            self.set_regs['force_now'] = self.magnitude_effort(rr[0], rr[1])
            self.set_regs['amort_move'] = self.movement_amount(rr[2])
            self.register_state(rr[3])
            self.set_regs['counter_time'] = self.counter_time(rr[4])
            self.switch_state(rr[5])
            self.set_regs['traverse_move'] = self.movement_amount(rr[6])
            self.set_regs['temperature'] = self.temperature_value(rr[7], rr[8])
            self.set_regs['force_alarm'] = self.emergency_force(rr[10], rr[11])

            self.count_msg += 1
            print(self.count_msg)

            self.signals.read_finish.emit()

        except Exception as e:
            txt_log = 'ERROR in model/reader_result - {}'.format(e)
            self.status_bar_msg(txt_log)
            self.save_log('error', str(e))

    def fill_data_for_graph(self):
        try:
            force = self.set_regs.get('force_now')
            move = self.set_regs.get('amort_move')
            self.set_regs['force_list'].append(force)
            self.set_regs['amort_move_list'].append(move)
            print('data added in graph')

        except Exception as e:
            txt_log = 'ERROR in model/fill_data_for_graph - {}'.format(e)
            self.status_bar_msg(txt_log)
            self.save_log('error', str(e))

    def init_writer(self):
        try:
            self.writer = Writer(client=self.set_connect['client'],
                                 cst=cst,
                                 **self.set_regs)

            if not self.writer_flag_init:
                self.writer.signals.thread_log.connect(self.thread_log_msg)
                self.writer.signals.thread_err.connect(self.thread_err_log)
                self.writer.signals.write_finish.connect(self.writer_result)
                self.writer_flag_init = True
            self.threadpool.start(self.writer)

        except Exception as e:
            txt_log = 'ERROR in model/init_writer - {}'.format(e)
            self.status_bar_msg(txt_log)
            self.save_log('error', str(e))

    def writer_result(self, state):
        self.flag_write = state

    def write_reg_state(self):
        try:
            res = 0
            values = []
            for i in range(16):
                res = res + self.set_regs.get('list_state')[i] * 2 ** i

            values.append(res)

            self.set_regs['reg_write'] = 0x2003
            self.set_regs['write_values'] = values
            self.set_regs['write_tag'] = 'reg'

            self.init_writer()

        except Exception as e:
            txt_log = 'ERROR in model/write_reg_state - {}'.format(e)
            self.status_bar_msg(txt_log)
            self.save_log('error', str(e))

    def change_list_state(self, bit, value):
        try:
            self.set_regs['list_state'][bit] = value

            self.write_reg_state()

        except Exception as e:
            txt_log = 'ERROR in model/change_list_state - {}'.format(e)
            self.status_bar_msg(txt_log)
            self.save_log('error', str(e))

    def write_emergency_force(self):
        try:
            arr = []
            value = self.set_regs.get('force_alarm')
            val = pack('>f', value)
            for i in range(0, 4, 2):
                arr.append(int((hex(val[i])[2:] + hex(val[i + 1])[2:]), 16))

            self.set_regs['write_tag'] = 'reg'
            self.set_regs['reg_write'] = 0x200a
            self.set_regs['write_values'] = arr

            self.init_writer()

        except Exception as e:
            txt_log = 'ERROR in model/write_emergency_force - {}'.format(e)
            self.status_bar_msg(txt_log)
            self.save_log('error', str(e))

    def motor_command(self, command):
        try:
            command = command + self.calc_crc(command)
            values = self.calc_values_write(command)
            self.set_regs['freq_command'] = values
            self.set_regs['write_tag'] = 'FC'

            self.init_writer()

        except Exception as e:
            txt_log = 'ERROR in model/motor_command - {}'.format(e)
            self.status_bar_msg(txt_log)
            self.save_log('error', str(e))

    def write_frequency(self):
        try:
            adr_freq = str(self.set_regs.get('adr_freq'))
            freq = self.set_regs.get('frequency')
            freq_hex = hex(freq)[2:].zfill(4)
            freq_hex = '0' + adr_freq + '06010D' + freq_hex
            self.motor_command(freq_hex)

        except Exception as e:
            txt_log = 'ERROR in model/write_frequency - {}'.format(e)
            self.status_bar_msg(txt_log)
            self.save_log('error', str(e))

    def motor_up(self):
        try:
            adr_freq = str(self.set_regs.get('adr_freq'))
            com_hex = '0' + adr_freq + '0620000002'
            self.motor_command(com_hex)

        except Exception as e:
            txt_log = 'ERROR in model/motor_up - {}'.format(e)
            self.status_bar_msg(txt_log)
            self.save_log('error', str(e))

    def motor_down(self):
        try:
            com_hex = '020620000001'
            self.motor_command(com_hex)

        except Exception as e:
            txt_log = 'ERROR in model/motor_down - {}'.format(e)
            self.status_bar_msg(txt_log)
            self.save_log('error', str(e))

    def motor_stop(self):
        try:
            adr_freq = str(self.set_regs.get('adr_freq'))
            com_hex = '0' + adr_freq + '0620000003'
            self.motor_command(com_hex)

        except Exception as e:
            txt_log = 'ERROR in model/motor_stop - {}'.format(e)
            self.status_bar_msg(txt_log)
            self.save_log('error', str(e))
        
    def calc_crc(self, data):
        try:
            byte_data = bytes.fromhex(data)
            crc16 = crcmod.mkCrcFun(0x18005, initCrc=0xFFFF, rev=True, xorOut=0x0000)
            crc_str = hex(crc16(byte_data))[2:].zfill(4)
            crc_str = crc_str[2:] + crc_str[:2]

            return crc_str

        except Exception as e:
            txt_log = 'ERROR in model/calc_crc - {}'.format(e)
            self.status_bar_msg(txt_log)
            self.save_log('error', str(e))

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
            txt_log = 'ERROR in model/calc_values_write - {}'.format(e)
            self.status_bar_msg(txt_log)
            self.save_log('error', str(e))

    def magnitude_effort(self, low_reg, big_reg):
        """Текущая величина усилия"""
        try:
            val_temp = round(unpack('f', pack('<HH', big_reg, low_reg))[0], 0)

            self.force.append(val_temp)

            return val_temp

        except Exception as e:
            txt_log = 'ERROR in model/magnitude_effort - {}'.format(e)
            self.status_bar_msg(txt_log)
            self.save_log('error', str(e))

    def movement_amount(self, data) -> float:
        """Текущая величина перемещения штока аммортизатора или траверсы"""
        try:
            result = round(0.1 * (int.from_bytes(pack('>H', data), 'big', signed=True)), 1)

            return result

        except Exception as e:
            txt_log = 'ERROR in model/movement_amount - {}'.format(e)
            self.status_bar_msg(txt_log)
            self.save_log('error', str(e))

    def register_state(self, register):
        """Регистр состояния 0х2003"""
        try:
            temp = bin(register)[2:].zfill(16)
            bits = ''.join(reversed(temp))

            self.set_regs['cycle_force'] = bits[0]
            self.set_regs['list_state'][0] = int(bits[0])
            self.set_regs['red_light'] = bits[1]
            self.set_regs['list_state'][1] = int(bits[1])
            self.set_regs['green_light'] = bits[2]
            self.set_regs['list_state'][2] = int(bits[2])
            self.set_regs['lost_control'] = bits[3]
            self.set_regs['list_state'][3] = int(bits[3])
            self.set_regs['excess_force'] = bits[4]
            self.set_regs['list_state'][4] = int(bits[4])
            self.set_regs['safety_fence'] = bits[8]
            self.set_regs['list_state'][8] = int(bits[8])
            self.set_regs['state_freq'] = bits[11]
            self.set_regs['list_state'][11] = int(bits[11])
            self.set_regs['state_force'] = bits[12]
            self.set_regs['list_state'][12] = int(bits[12])

        except Exception as e:
            txt_log = 'ERROR in model/register_state - {}'.format(e)
            self.status_bar_msg(txt_log)
            self.save_log('error', str(e))

    def counter_time(self, register):
        """Регистр счётчика времени"""
        try:
            return register

        except Exception as e:
            txt_log = 'ERROR in model/counter_time - {}'.format(e)
            self.status_bar_msg(txt_log)
            self.save_log('error', str(e))

    def switch_state(self, register):
        """Регистр состояния входов модуля МВ110-224.16ДН"""
        try:
            temp = bin(register)[2:].zfill(16)
            bits = ''.join(reversed(temp))

            self.set_regs['safety_fence'] = bits[0]
            self.set_regs['traverse_block_1'] = bits[1]
            self.set_regs['traverse_block_2'] = bits[2]
            self.set_regs['test_launch'] = bits[3]
            self.set_regs['alarm_highest_position'] = bits[8]
            self.set_regs['alarm_lowest_position'] = bits[9]
            self.set_regs['highest_position'] = bits[12]
            self.set_regs['lowest_position'] = bits[13]

        except Exception as e:
            txt_log = 'ERROR in model/switch_state - {}'.format(e)
            self.status_bar_msg(txt_log)
            self.save_log('error', str(e))

    def temperature_value(self, low_reg, big_reg):
        """Величина температуры с модуля МВ-110-224-2А"""
        try:
            val_temp = round(unpack('f', pack('<HH', big_reg, low_reg))[0], 1)

            return val_temp

        except Exception as e:
            txt_log = 'ERROR in model/temperature_value - {}'.format(e)
            self.status_bar_msg(txt_log)
            self.save_log('error', str(e))

    def emergency_force(self, low_reg, big_reg):
        """Аварийное усилие"""
        try:
            val_temp = unpack('f', pack('<HH', big_reg, low_reg))[0]

            return val_temp

        except Exception as e:
            txt_log = 'ERROR in model/emergency_force - {}'.format(e)
            self.status_bar_msg(txt_log)
            self.save_log('error', str(e))

    # def len_command_freq(self, data):
    #     """Регистр длины команды ПЧ"""
    #     try:
    #         self.set_regs['len_freq_msg'] = data
    #
    #     except Exception as e:
    #         txt_log = 'ERROR in model/len_command_freq - {}'.format(e)
    #         self.status_bar_msg(txt_log)
    #         self.save_log('error', str(e))
    #
    # def buffer_freq(self, registers):
    #     """Буфер ПЧ"""
    #     try:
    #         self.set_regs['buffer_freq'] = registers
    #
    #     except Exception as e:
    #         txt_log = 'ERROR in model/buffer_freq - {}'.format(e)
    #         self.status_bar_msg(txt_log)
    #         self.save_log('error', str(e))
    #
    # def len_command_force(self, data):
    #     """Регистер длины команды датчика силы"""
    #     try:
    #         self.set_regs['len_force_msg'] = data
    #
    #     except Exception as e:
    #         txt_log = 'ERROR in model/len_command_force - {}'.format(e)
    #         self.status_bar_msg(txt_log)
    #         self.save_log('error', str(e))
    #
    # def buffer_force(self, registers):
    #     """Буфер датчика силы"""
    #     try:
    #         self.set_regs['buffer_force'] = registers
    #
    #     except Exception as e:
    #         txt_log = 'ERROR in model/buffer_force - {}'.format(e)
    #         self.status_bar_msg(txt_log)
    #         self.save_log('error', str(e))
    #
    # def buffer_data(self, registers):
    #     """Буфер данных"""
    #     try:
    #         self.set_regs['buffer_data'] = registers
    #
    #     except Exception as e:
    #         txt_log = 'ERROR in model/buffer_data - {}'.format(e)
    #         self.status_bar_msg(txt_log)
    #         self.save_log('error', str(e))
