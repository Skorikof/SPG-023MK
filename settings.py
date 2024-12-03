# -*- coding: utf-8 -*-
from configparser import ConfigParser


class PrgSettings:
    def __init__(self):
        try:
            self.settings = {}
            self.state = {}
            config = ConfigParser()
            config.read('settings.ini')
            temp_val = config['ComPort']['PortSettings']
            temp_val = str.split(temp_val, ',')

            con_set = {'COM': 'COM' + config['ComPort']['NumberPort'],
                       'baudrate': int(temp_val[0]),
                       'parity': temp_val[1],
                       'bytesize': int(temp_val[2]),
                       'stopbits': int(temp_val[3]),
                       }

            force_koef = self._force_koef(config['Settings']['ForceKoef'].replace(',', '.'))
            finish_temper = float(config['Settings']['FinishTemper'].replace(',', '.'))

            self.settings = {'con_set': con_set,
                             }

            self.state = {'operator': {'name': '', 'rank': ''},
                          'amort': None,
                          'query_write': False,
                          'list_write': [],
                          'repeat_command': False,
                          'fc_ready': False,
                          'flag_bit_force': False,
                          'stage': 'wait',
                          'type_test': '',
                          'test_launch': False,
                          'test_flag': False,
                          'fill_graph': False,
                          'alarm_flag': False,
                          'alarm_tag': '',
                          'traverse_stock': 756,
                          'start_direction': False,
                          'current_direction': None,
                          'min_pos': False,
                          'min_point': 0,
                          'max_pos': False,
                          'max_point': 0,
                          'force_refresh': 0,
                          'force_koef': force_koef,
                          'force': 0,
                          'force_list': [],
                          'force_accum_list': [],
                          'force_graph': [],
                          'move': 0.0,
                          'move_list': [],
                          'move_accum_list': [],
                          'move_graph': [],
                          'max_comp': 0,
                          'max_recoil': 0,
                          'temperature': 0,
                          'temper_first': 0,
                          'temper_second': 0,
                          'temp_list': [],
                          'max_temperature': 0,
                          'finish_temper': finish_temper,
                          'traverse_referent': False,
                          'gear_referent': False,
                          'traverse_freq': 10,
                          }

        except Exception as e:
            print(str(e))

    def _force_koef(self, value):
        try:
            return float(value)

        except ValueError:
            return 1


class SpeedLimit:
    def calculate_speed_limit(self, hod):
        if 40 <= hod < 50:
            return 0.41
        elif 50 <= hod < 60:
            return 0.51
        elif 60 <= hod < 70:
            return 0.62
        elif 70 <= hod < 80:
            return 0.72
        elif 80 <= hod < 90:
            return 0.82
        elif 90 <= hod < 100:
            return 0.92
        elif 100 <= hod < 110:
            return 1.03
        elif 110 <= hod < 120:
            return 1.13
        elif hod == 120:
            return 1.23
        else:
            return 0.41
