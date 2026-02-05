from struct import pack, unpack

from scripts.logger import my_logger


class ParserSPG023MK:
    def __init__(self):
        self.logger = my_logger.get_logger(__name__)
        
    def pars_response_from_regs(self, res):
        try:
            result = {
                'force': self.magnitude_effort(res[0], res[1]),
                'move': self.movement_amount(res[2]),
                'state': self.register_state(res[3]),
                'state_list': self._change_state_list(res[3]),
                'counter': self.counter_time(res[4]),
                'switch': self.switch_state(res[5]),
                'traverse': round(0.5 * self.movement_amount(res[6]), 1),
                'first_t': self.temperature_value(res[7], res[8]),
                'force_a': self.emergency_force(res[10], res[11]),
                'second_t': self.temperature_value(res[12], res[13])
            }
            
            return result
            
        except Exception as e:
            self.logger.error(e)
        
    def discard_left_data(self, request):
        """Filter out invalid force data points (value -100000) from request."""
        try:
            force_data = request.get('force', [])
            
            if not force_data:
                return None

            valid_ind_f = [i for i, force in enumerate(force_data) if force != -100000]
            
            if not valid_ind_f:
                return None

            valid_force = {
                'count': [request['count'][i] for i in valid_ind_f],
                'force': [request['force'][i] for i in valid_ind_f],
                'move': [request['move'][i] for i in valid_ind_f],
                'state': [request['state'][i] for i in valid_ind_f],
                'temper': [request['temper'][i] for i in valid_ind_f],
            }
            
            return valid_force
        
        except Exception as e:
            self.logger.error(e)
            
    def discard_left_move(self, move):
        valid_ind = []
        for i, move in enumerate(move):
            if i == 0:
                valid_ind.append(i)
                temp = abs(move)
            else:
                if abs(temp - abs(move)) < 10:
                    valid_ind.append(i)
                    temp = abs(move)
                    
        return valid_ind

    def magnitude_effort(self, low_reg, big_reg):
        """Текущая величина усилия"""
        try:
            return round(unpack('f', pack('<HH', big_reg, low_reg))[0], 1)

        except Exception as e:
            self.logger.error(e)

    def movement_amount(self, value):
        """Текущая величина перемещения штока аммортизатора или траверсы"""
        try:
            return round(-0.1 * (int.from_bytes(pack('>H', value), 'big', signed=True)), 1)

        except Exception as e:
            self.logger.error(e)
            
    def change_state_list(self, reg):
        try:
            bits = ''.join(reversed(bin(reg)[2:].zfill(16)))
            return [int(x) for x in bits]

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
                       'referent': (5, bool),
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
