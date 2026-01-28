from struct import pack, unpack

from scripts.logger import my_logger


class ParserSPG023MK:
    def __init__(self):
        self.logger = my_logger.get_logger(__name__)
            
    def discard_left_data(self, request):
        """Filter out invalid force data points (value -100000) from request."""
        try:
            force_data = request.get('force', [])
            
            if not force_data:
                return None
            
            # Filter indices where force is not -100000
            valid_indices = [i for i, force in enumerate(force_data) if force != -100000]
            
            if not valid_indices:
                return None
            
            # Build response with only valid data points
            response = {
                'count': [request['count'][i] for i in valid_indices],
                'force': [request['force'][i] for i in valid_indices],
                'move': [request['move'][i] for i in valid_indices],
                'state': [request['state'][i] for i in valid_indices],
                'temper': [request['temper'][i] for i in valid_indices],
            }
            
            # print(f'count ==> {response["count"]}')
            # print(f'force ==> {response["force"]}')
            # print(f'move ==> {response["move"]}')
            # print(f'state ==> {response["state"]}')
            # print(f'temper ==> {response["temper"]}')

            return response
            
        except Exception as e:
            self.logger.error(e)
            return None

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
            bits = ''.join(reversed(bin(reg)[2:].zfill(16)))

            BIT_MAP = {'cycle_force': (0, bool),
                       'red_light': (1, bool),
                       'green_light': (2, bool),
                       'lost_control': (3, bool),
                       'excess_force': (4, bool),
                       'select_temper': (6, int),
                       'safety_fence': (8, bool),
                       'traverse_block': (9, bool),
                       'state_freq': (11, bool),
                       'state_force': (12, bool),
                       'yellow_btn': (13, bool),
                       }
        
            return {key: converter(int(bits[bit_pos])) 
                    for key, (bit_pos, converter) in BIT_MAP.items()}

        except Exception as e:
            self.logger.error(e)
            return None

    def counter_time(self, register):
        """Регистр счётчика времени"""
        try:
            return register

        except Exception as e:
            self.logger.error(e)

    def switch_state(self, reg):
        """Регистр состояния входов модуля МВ110-224.16ДН"""
        try:
            bits = ''.join(reversed(bin(reg)[2:].zfill(16)))
            
            BIT_MAP = {'traverse_block_left': (1, bool),
                       'traverse_block_right': (2, bool),
                       'alarm_highest_position': (8, bool),
                       'alarm_lowest_position': (9, bool),
                       'highest_position': (12, bool),
                       'lowest_position': (13, bool),
                       }
        
            return {key: converter(int(bits[bit_pos])) 
                    for key, (bit_pos, converter) in BIT_MAP.items()}

        except Exception as e:
            self.logger.error(e)
            return None

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
