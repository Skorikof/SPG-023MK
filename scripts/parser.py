import struct

from scripts.logger import my_logger


class ParserSPG023MK:
    def __init__(self):
        self.logger = my_logger.get_logger(__name__)
        
    def pars_response_from_regs(self, res):
        try:
            result = {
                'force': self._parse_float(res[0], res[1]),
                'move': self._movement_amount(res[2], 'pos'),
                'state': self._register_state(res[3]),
                'state_list': self._bits16(res[3]),
                'counter': res[4],
                'switch': self._switch_state(res[5]),
                'traverse': self._movement_amount(res[6], 'traverse'),
                'first_t': self._parse_float(res[7], res[8]),
                'force_a': self._parse_float(res[10], res[11]),
                'second_t': self._parse_float(res[12], res[13])
            }

            return result
            
        except Exception as e:
            self.logger.error(e)
            
    def pars_response_from_buffer(self, res):
        try:
            if res.get('count') == []:
                return
            
            result = {
                'count': res.get('count'),
                'force': [self._parse_float(a, b) for a, b in zip(res.get('force_big'), res.get('force_low'))],
                'move': [self._movement_amount(x, 'pos') for x in res.get('move')],
                'state': self._register_state(res.get('state')[-1]),
                'state_list': self._bits16(res.get('state')[-1]),
                'temper': res.get('temper'),
            }
            print(f'count --> {result.get("count")}')
            print(f'force --> {result.get("force")}')
            print(f'move --> {result.get("move")}')
            print(f'state --> {result.get("state")}')
            print(f'temper --> {result.get("temper")}')
            return result
            # return self._discard_left_data(result) # Убрал для отладки, контроллер на столе
            
        except Exception as e:
            self.logger.error(e)
        
    def _discard_left_data(self, request):
        """Filter out invalid force data points (value -100000) from request."""
        try:
            force_data = request.get('force', [])
            
            if not force_data:
                return None
            
            # Filter indices where force is not -100000
            valid_ind_f = [i for i, force in enumerate(force_data) if force != -100000]
            
            if not valid_ind_f:
                return None
            
            # Build response with only valid data points
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
    
    def _parse_float(self, big_reg: int, low_reg: int) -> float | None:
        """Парсер значения типа float из двух регистров"""
        try:
            raw = (big_reg << 16) | low_reg
            return struct.unpack_from('<f', raw.to_bytes(4, 'little'))[0]
        except Exception as e:
            self.logger.error(e)
            return None
        
    def _movement_amount(self, value: int, tag: str) -> float | None:
        """Текущая величина перемещения штока аммортизатора или траверсы"""
        try:
            if value & 0x8000:
                value -= 0x10000
            if tag == 'pos':
                return -0.1 * value
            elif tag == 'traverse':
                return -0.5 * value

        except Exception as e:
            self.logger.error(e)
            return None
        
    def _bits16(self, reg: int) -> list[int]:
        return [(reg >> i) & 1 for i in range(16)]

    def _register_state(self, reg):
        """Регистр состояния 0х2003"""
        try:
            bits = self._bits16(reg)

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

    def _switch_state(self, reg):
        """Регистр состояния входов модуля МВ110-224.16ДН"""
        try:
            bits = self._bits16(reg)
            
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
