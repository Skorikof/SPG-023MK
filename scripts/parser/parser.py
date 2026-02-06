from dataclasses import dataclass
from struct import pack, unpack

from scripts.logger import my_logger


@dataclass(slots=True)
class RegisterState:
    cycle_force: bool = False
    red_light: bool = False
    green_light: bool = False
    lost_control: bool = False
    excess_force: bool = False
    referent: bool = False
    select_temper: int = 0
    safety_fence: bool = False
    traverse_block: bool = False
    state_freq: bool = False
    state_force: bool = False
    yellow_btn: bool = False
    
    
@dataclass(slots=True)
class SwitchState:
    traverse_block_left: bool = False
    traverse_block_right: bool = False
    alarm_highest_position: bool = False
    alarm_lowest_position: bool = False
    highest_position: bool = False
    lowest_position: bool = False
    

class ParserSPG023MK:
    def __init__(self):
        self.logger = my_logger.get_logger(__name__)
        
    def pars_response_from_regs(self, res):
        try:
            result = {
                'force': self.magnitude_effort(res[0], res[1]),
                'move': self.movement_amount(res[2]),
                'state': self.register_state(res[3]),
                'state_list': self.change_state_list(res[3]),
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
            
            reg_state = RegisterState(
                cycle_force=bool(int(bits[0])),
                red_light=bool(int(bits[1])),
                green_light=bool(int(bits[2])),
                lost_control=bool(int(bits[3])),
                excess_force=bool(int(bits[4])),
                referent=bool(int(bits[5])),
                select_temper=int(bits[6]),
                safety_fence=bool(int(bits[8])),
                traverse_block=bool(int(bits[9])),
                state_freq=bool(int(bits[11])),
                state_force=bool(int(bits[12])),
                yellow_btn=bool(int(bits[13]))
            )
        
            return reg_state

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
            
            switch_state = SwitchState(
                traverse_block_left=bool(int(bits[1])),
                traverse_block_right=bool(int(bits[2])),
                alarm_highest_position=bool(int(bits[8])),
                alarm_lowest_position=bool(int(bits[9])),
                highest_position=bool(int(bits[12])),
                lowest_position=bool(int(bits[13])),
            )
        
            return switch_state

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
