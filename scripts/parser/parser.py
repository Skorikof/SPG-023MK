from dataclasses import dataclass
import struct

from scripts.logger import my_logger


@dataclass(slots=True, frozen=True)
class RegisterState:
    bits: list[int] = None
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
    
    
@dataclass(slots=True, frozen=True)
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
        
    def parse_float(self, big_reg: int, low_reg: int) -> float | None:
        """Парсер значения типа float из двух регистров"""
        try:
            raw = (big_reg << 16) | low_reg
            return struct.unpack_from('<f', raw.to_bytes(4, 'little'))[0]
        except Exception as e:
            self.logger.error(e)
            return None

    def movement_amount(self, value: int) -> float | None:
        """Текущая величина перемещения штока аммортизатора или траверсы"""
        try:
            if value & 0x8000:
                value -= 0x10000
            return -0.1 * value

        except Exception as e:
            self.logger.error(e)
            return None
            
    def _bits16(self, reg: int) -> list[int]:
        return [(reg >> i) & 1 for i in range(16)]

    def register_state(self, reg: int) -> RegisterState| None:
        """Регистр состояния 0х2003"""
        try:
            bits = self._bits16(reg)
            
            reg_state = RegisterState(
                bits=bits,
                cycle_force=bool(bits[0]),
                red_light=bool(bits[1]),
                green_light=bool(bits[2]),
                lost_control=bool(bits[3]),
                excess_force=bool(bits[4]),
                referent=bool(bits[5]),
                select_temper=bits[6],
                safety_fence=bool(bits[8]),
                traverse_block=bool(bits[9]),
                state_freq=bool(bits[11]),
                state_force=bool(bits[12]),
                yellow_btn=bool(bits[13])
            )
            return reg_state

        except Exception as e:
            self.logger.error(e)
            return None

    def switch_state(self, reg: int) -> SwitchState | None:
        """Регистр состояния входов модуля МВ110-224.16ДН"""
        try:
            bits = self._bits16(reg)
            
            switch_state = SwitchState(
                traverse_block_left=bool(bits[1]),
                traverse_block_right=bool(bits[2]),
                alarm_highest_position=bool(bits[8]),
                alarm_lowest_position=bool(bits[9]),
                highest_position=bool(bits[12]),
                lowest_position=bool(bits[13]),
            )
        
            return switch_state

        except Exception as e:
            self.logger.error(e)
            return None
