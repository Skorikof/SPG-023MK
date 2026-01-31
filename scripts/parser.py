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
        
    # def pars_response_from_buffer(self, res):
    #     try:
    #         count = res[0::6]
    #         force_low = res[1::6]
    #         force_big = res[2::6]
    #         move = res[3::6]
    #         state = res[4::6]
    #         temper = res[5::6]
            
    #         force = tuple(self._magnitude_effort(x, force_big[i]) for i, x in enumerate(force_low))
            
    #         # print(f'count ==> {count}')
    #         # print(f'force ==> {force}')
    #         # print(f'move ==> {move}')
    #         # print(f'state ==> {state}')
    #         # print(f'temper ==> {temper}')
            
    #         return self._discard_left_data(count, force, move, state, temper)
            
    #     except Exception as e:
    #         self.logger.error(e)
            
    # def _discard_left_data(self, count: tuple, force: tuple,
    #                        move: tuple, state: tuple, temper: tuple):
    #     try:
    #         if force is not None:
    #             valid_indices = [i for i, force in enumerate(force) if force != -100000]
                
    #             if not valid_indices:
    #                 return None
                
    #             result = {'count': [count[i] for i in valid_indices],
    #                     'force': [force[i] for i in valid_indices],
    #                     'move': [self.movement_amount(move[i]) for i in valid_indices],
    #                     'state': [self.register_state(state[i]) for i in valid_indices],
    #                     'state_list': self._change_state_list(state[0]),
    #                     'temper': [round(temper[i] * 0.01, 1) for i in valid_indices],
    #                     }

    #             return result
            
    #         else:
    #             return None
            
    #     except Exception as e:
    #         self.logger.error(e)
    #         return None
        
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
            
    def _change_state_list(self, reg):
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
