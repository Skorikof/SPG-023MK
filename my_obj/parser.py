import logging
import traceback
from struct import pack, unpack


class ParserSPG:
    def __init__(self):
        self.error_log = logging.getLogger('error')

    def magnitude_effort(self, low_reg, big_reg):
        """Текущая величина усилия"""
        try:
            val_temp = round(unpack('f', pack('<HH', big_reg, low_reg))[0], 1)

            return val_temp

        except:
            self.error_log.error(traceback.format_exc())

    def movement_amount(self, data) -> float:
        """Текущая величина перемещения штока аммортизатора или траверсы"""
        try:
            result = round(-0.1 * (int.from_bytes(pack('>H', data), 'big', signed=True)), 1)

            return result

        except Exception as e:
            self.log_error(f'ERROR in model/_movement_amount - {e}')

    def _register_state(self, reg):
        """Регистр состояния 0х2003"""
        try:
            if self.reg_state != reg:
                self.reg_state = reg
                temp = bin(reg)[2:].zfill(16)
                bits = ''.join(reversed(temp))

                command = {'list_state': [int(x) for x in bits],
                           'cycle_force': bool(int(bits[0])),
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

                self.update_main_dict(command)

        except Exception as e:
            self.log_error(f'ERROR in model/_register_state - {e}')

    def _counter_time(self, register):
        """Регистр счётчика времени"""
        try:
            return register

        except Exception as e:
            self.log_error(f'ERROR in model/_counter_time - {e}')

    def _switch_state(self, reg):
        """Регистр состояния входов модуля МВ110-224.16ДН"""
        try:
            if self.reg_switch != reg:
                self.reg_switch = reg
                temp = bin(reg)[2:].zfill(16)
                bits = ''.join(reversed(temp))

                command = {'traverse_block_left': bool(int(bits[1])),
                           'traverse_block_right': bool(int(bits[2])),
                           'alarm_highest_position': bool(int(bits[8])),
                           'alarm_lowest_position': bool(int(bits[9])),
                           'highest_position': bool(int(bits[12])),
                           'lowest_position': bool(int(bits[13]))}

                self.update_main_dict(command)

        except Exception as e:
            self.log_error(f'ERROR in model/_switch_state - {e}')

    def _temperature_value(self, low_reg, big_reg):
        """Величина температуры с модуля МВ-110-224-2А"""
        try:
            val_temp = round(unpack('f', pack('<HH', big_reg, low_reg))[0], 1)

            return val_temp

        except Exception as e:
            self.log_error(f'ERROR in model/_temperature_value - {e}')

    def _emergency_force(self, low_reg, big_reg):
        """Аварийное усилие"""
        try:
            val_temp = unpack('f', pack('<HH', big_reg, low_reg))[0]

            return val_temp

        except Exception as e:
            self.log_error(f'ERROR in model/_emergency_force - {e}')