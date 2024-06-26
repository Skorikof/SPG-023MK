from configparser import ConfigParser


class PrgSettings:
    def __init__(self):
        try:
            self.connect = {}
            self.registers = {}
            config = ConfigParser()
            config.read('settings.ini')
            self.connect['COM'] = 'COM' + config['ComPort']['NumberPort']
            temp_val = config['ComPort']['PortSettings']
            temp_val = str.split(temp_val, ',')
            self.connect['baudrate'] = int(temp_val[0])
            self.connect['parity'] = temp_val[1]
            self.connect['bytesize'] = int(temp_val[2])
            self.connect['stopbits'] = int(temp_val[3])

            self.registers['force'] = 0
            self.registers['force_list'] = []
            self.registers['force_graph'] = []
            self.registers['move'] = 0
            self.registers['move_list'] = []
            self.registers['move_graph'] = []

            # self.registers['list_state'] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            # self.registers['cycle_force'] = 0
            # self.registers['lost_control'] = 0
            # self.registers['excess_force'] = 0
            # self.registers['state_freq'] = 0
            # self.registers['state_force'] = 0
            # self.registers['counter_time'] = 0
            # self.registers['temp_list'] = []

            # self.registers['safety_fence'] = 0
            # self.registers['traverse_block_1'] = 0
            # self.registers['traverse_block_2'] = 0
            # self.registers['test_launch'] = False
            # self.registers['yellow_btn'] = 0
            # self.registers['test_flag'] = False
            # self.registers['alarm_highest_position'] = 0
            # self.registers['highest_position'] = 0
            # self.registers['alarm_lowest_position'] = 0
            # self.registers['lowest_position'] = 0
            # self.registers['green_light'] = 0
            # self.registers['red_light'] = 0
            self.registers['traverse_stock'] = 755
            self.registers['traverse_referent'] = False
            # self.registers['traverse_position'] = False
            # self.registers['traverse_point'] = 0
            # self.registers['gear_referent'] = False
            self.registers['stage'] = ''
            self.registers['alarm_stage'] = False

            self.registers['operator'] = {'name': '', 'rank': ''}
            self.registers['type_test'] = ''
            self.registers['hod'] = 120
            self.registers['start_direction'] = None
            self.registers['current_direction'] = None
            # self.registers['full_cycle'] = False
            self.registers['start_pos'] = False
            self.registers['start_point'] = 0
            self.registers['min_pos'] = False
            self.registers['min_point'] = 0
            self.registers['max_pos'] = False
            self.registers['max_point'] = 0
            self.registers['max_comp'] = 0
            self.registers['max_recoil'] = 0
            self.registers['temperature'] = 0
            self.registers['max_temperature'] = 0

        except Exception as e:
            print(str(e))
