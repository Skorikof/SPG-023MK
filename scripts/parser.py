from struct import pack, unpack

from scripts.logger import my_logger


class ParserSPG023MK:
    def __init__(self):
        self.logger = my_logger.get_logger(__name__)

    def discard_left_data(self, request):
        try:
            response = {'count': [],
                        'force': [],
                        'move': [],
                        'state': [],
                        'temper': [],
                        }

            if not request.get('force', []):
                return None

            else:
                for ind, force in enumerate(request.get('force')):
                    if force != -100000:
                        response['count'].append(request.get('count')[ind])
                        response['force'].append(request.get('force')[ind])
                        response['move'].append(request.get('move')[ind])
                        response['state'].append(request.get('state')[ind])
                        response['temper'].append(request.get('temper')[ind])
                        
                if len(response['force']) > 0:
                    return response
                
                else:
                    return None

        except Exception as e:
            self.logger.error(e)

    def magnitude_effort(self, low_reg, big_reg):
        """Текущая величина усилия"""
        try:
            return round(unpack('f', pack('<HH', big_reg, low_reg))[0], 1)

        except Exception as e:
            self.logger.error(e)

    def movement_amount(self, data):
        """Текущая величина перемещения штока аммортизатора или траверсы"""
        try:
            return round(-0.1 * (int.from_bytes(pack('>H', data), 'big', signed=True)), 1)

        except Exception as e:
            self.logger.error(e)

    def register_state(self, reg):
        """Регистр состояния 0х2003"""
        try:
            temp = bin(reg)[2:].zfill(16)
            bits = ''.join(reversed(temp))

            return {'cycle_force': bool(int(bits[0])),
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

        except Exception as e:
            self.logger.error(e)

    def counter_time(self, register):
        """Регистр счётчика времени"""
        try:
            return register

        except Exception as e:
            self.logger.error(e)

    def switch_state(self, reg):
        """Регистр состояния входов модуля МВ110-224.16ДН"""
        try:
            temp = bin(reg)[2:].zfill(16)
            bits = ''.join(reversed(temp))

            return {'traverse_block_left': bool(int(bits[1])),
                    'traverse_block_right': bool(int(bits[2])),
                    'alarm_highest_position': bool(int(bits[8])),
                    'alarm_lowest_position': bool(int(bits[9])),
                    'highest_position': bool(int(bits[12])),
                    'lowest_position': bool(int(bits[13]))}

        except Exception as e:
            self.logger.error(e)

    def temperature_value(self, low_reg, big_reg):
        """Величина температуры с модуля МВ-110-224-2А"""
        try:
            return round(unpack('f', pack('<HH', big_reg, low_reg))[0], 1)

        except Exception as e:
            self.logger.error(e)

    def emergency_force(self, low_reg, big_reg):
        """Аварийное усилие"""
        try:
            return unpack('f', pack('<HH', big_reg, low_reg))[0]

        except Exception as e:
            self.logger.error(e)
