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
            self.registers['start_reg_write'] = 0
            self.registers['list_state'] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            self.registers['values_write'] = [0]
            self.registers['start_reg_read'] = 0x2000
            self.registers['count_reg_read'] = 12
            self.registers['state_reg'] = 0x2003

            self.registers['reg_len_freq'] = 0x2060
            self.registers['len_freq_msg'] = 8
            self.registers['start_reg_freq_buffer'] = 0x2061
            self.registers['count_reg_freq_buffer'] = 16
            self.registers['reg_len_force'] = 0x2080
            self.registers['start_reg_force_buffer'] = 0x2081
            self.registers['count_reg_force_buffer'] = 16
            self.registers['start_reg_buffer'] = 0x4000
            self.registers['count_reg_buffer'] = 15000

            self.state['alarm_force'] = 15000
            self.state['cycle_force'] = 0
            self.state['lost_control'] = 0
            self.state['excess_force'] = 0
            self.state['state_freq'] = 0
            self.state['frequency'] = 0
            self.state['state_force'] = 0

            self.state['safety_fence'] = 0
            self.state['traverse_block_1'] = 0
            self.state['traverse_block_2'] = 0
            self.state['test_launch'] = 0
            self.state['alarm_highest_position'] = 0
            self.state['highest_position'] = 0
            self.state['alarm_lowest_position'] = 0
            self.state['lowest_position'] = 0

        except Exception as e:
            print(str(e))
