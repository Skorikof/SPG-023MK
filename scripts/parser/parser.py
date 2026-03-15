# -*- coding: utf-8 -*-
import struct

from scripts.logger import my_logger


class ParserSPG023MK:
    def __init__(self):
        self.logger = my_logger.get_logger(__name__)
        self.INVALID_FORCE = -100000

    def _replace_invalid_force(self, values: list[float | None]) -> list[float] | None:
        """Replace invalid force samples (-100000/None) with nearest valid values.

        Strategy: forward-fill with previous valid value; for leading invalid samples,
        use the first valid value in the series. If there are no valid samples,
        returns None.
        """
        try:
            if not values:
                return None

            valid_first = None
            for v in values:
                if v is not None and v != self.INVALID_FORCE:
                    valid_first = float(v)
                    break

            if valid_first is None:
                return None

            out: list[float] = []
            prev = valid_first
            for v in values:
                if v is None or v == self.INVALID_FORCE:
                    out.append(prev)
                else:
                    prev = float(v)
                    out.append(prev)
            return out

        except Exception as e:
            self.logger.error(e)
            return None
        
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
            count_list = res.get('count') or []
            force_big = res.get('force_big') or []
            force_low = res.get('force_low') or []
            move_list = res.get('move') or []
            state_list = res.get('state') or []
            temper_list = res.get('temper') or []

            if not count_list or not force_big or not force_low or not move_list:
                return None

            parse_float = self._parse_float
            movement_amount = self._movement_amount

            count_out: list[int] = []
            force_out: list[float | None] = []
            move_out: list[float | None] = []
            state_out: list[int] = []
            temper_out: list[int] = []

            for c, fb, fl, mv, st, tp in zip(
                count_list, force_big, force_low, move_list, state_list, temper_list
            ):
                count_out.append(c)
                force_out.append(parse_float(fb, fl))
                move_out.append(movement_amount(mv, 'pos'))
                state_out.append(st)
                temper_out.append(tp)

            force_sanitized = self._replace_invalid_force(force_out)
            if force_sanitized is None:
                return None

            last_state_reg = state_out[-1]
            last_temp = temper_out[-1]

            return {
                'count': count_out,
                'force': force_sanitized,
                'move': move_out,
                'state': self._register_state(last_state_reg),
                'state_list': self._bits16(last_state_reg),
                'temper': round(last_temp * 0.01, 1),
            }

        except Exception as e:
            self.logger.error(e)
            return None
        
    def _discard_left_data(self, request):
        """Filter out invalid force data points (value -100000) from request."""
        try:
            force_data = request.get('force') or []
            move_data = request.get('move') or []
            
            if not force_data:
                return None
            
            # Filter indices where force is valid and move exists
            valid_ind_f = [
                i
                for i, force in enumerate(force_data)
                if force is not None
                and force != self.INVALID_FORCE
                and i < len(move_data)
                and move_data[i] is not None
            ]
            
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
                return -0.05 * value

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
