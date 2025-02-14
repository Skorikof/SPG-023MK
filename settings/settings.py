# -*- coding: utf-8 -*-
from configparser import ConfigParser

from logger import my_logger


class PrgSettings:
    def __init__(self):
        try:
            self.logger = my_logger.get_logger(__name__)
            self.settings = {}
            self.state = {}
            config = ConfigParser()
            config.read('settings.ini', encoding='utf-8')
            temp_val = config['ComPort']['PortSettings']
            temp_val = str.split(temp_val, ',')

            self.con_set = {'COM': 'COM' + config['ComPort']['NumberPort'],
                            'baudrate': int(temp_val[0]),
                            'parity': temp_val[1],
                            'bytesize': int(temp_val[2]),
                            'stopbits': int(temp_val[3]),
                            }

            force_koef = self._force_koef(config['Settings']['ForceKoef'].replace(',', '.'))
            finish_temper = float(config['Settings']['FinishTemper'].replace(',', '.'))

            self.state = {'operator': {'name': '', 'rank': ''},
                          'amort': None,
                          'force_koef': force_koef,
                          'finish_temper': finish_temper,
                          'buffer_state': ['null', 'null'],
                          }

        except Exception as e:
            self.logger.error(e)

    def _force_koef(self, value):
        try:
            return float(value)

        except ValueError:
            return 1
