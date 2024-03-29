import configparser


class PrgSettings:
    def __init__(self):
        try:
            self.connect = dict()
            self.registers = dict()
            self.state = dict()
            config = configparser.ConfigParser()
            config.read('settings.ini')
            self.connect['COM'] = 'COM' + config['ComPort']['NumberPort']
            temp_val = config['ComPort']['PortSettings']
            temp_val = str.split(temp_val, ',')
            self.connect['baudrate'] = int(temp_val[0])
            self.connect['parity'] = temp_val[1]
            self.connect['bytesize'] = int(temp_val[2])
            self.connect['stopbits'] = int(temp_val[3])

            self.registers['dev_id'] = 1
            self.registers['adr_freq'] = 1
            self.registers['reg_write'] = 0x2003
            self.registers['write_values'] = [0]
            self.registers['reg_read'] = 0x2000
            self.registers['read_count'] = 12
            self.registers['reg_state'] = 0x2003
            self.registers['list_state'] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

            self.registers['reg_len_freq'] = 0x2060
            self.registers['len_freq_msg'] = 8
            self.registers['reg_freq_buffer'] = 0x2061
            self.registers['freq_buffer_count'] = 16
            self.registers['reg_len_force'] = 0x2080
            self.registers['reg_force_buffer'] = 0x2081
            self.registers['force_buffer_count'] = 16
            self.registers['reg_buffer'] = 0x4000
            self.registers['buffer_count'] = 15000

            self.registers['force_now'] = 0
            self.registers['force_list'] = []
            self.registers['amort_move_list'] = []
            self.registers['alarm_force'] = 15000
            self.registers['cycle_force'] = 0
            self.registers['lost_control'] = 0
            self.registers['excess_force'] = 0
            self.registers['state_freq'] = 0
            self.registers['frequency'] = 0
            self.registers['state_force'] = 0

            self.registers['safety_fence'] = 0
            self.registers['traverse_block_1'] = 0
            self.registers['traverse_block_2'] = 0
            self.registers['test_launch'] = 0
            self.registers['alarm_highest_position'] = 0
            self.registers['highest_position'] = 0
            self.registers['alarm_lowest_position'] = 0
            self.registers['lowest_position'] = 0

        except Exception as e:
            print(str(e))
