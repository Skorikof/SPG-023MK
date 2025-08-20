import statistics
import crcmod
from struct import pack

from logger import my_logger


class CalcData:
    def __init__(self):
        self.logger = my_logger.get_logger(__name__)

    def calc_crc(self, data):
        try:
            byte_data = bytes.fromhex(data)
            crc16 = crcmod.mkCrcFun(0x18005, initCrc=0xFFFF, rev=True, xorOut=0x0000)
            crc_str = hex(crc16(byte_data))[2:].zfill(4)
            crc_str = crc_str[2:] + crc_str[:2]

            return crc_str

        except Exception as e:
            self.logger.error(e)

    def values_freq_command(self, data):
        try:
            val_regs = []
            for i in range(0, len(data), 4):
                temp = data[i:i + 4]
                temp_byte = bytearray.fromhex(temp)
                temp_val = int.from_bytes(temp_byte, 'big')
                val_regs.append(temp_val)

            return val_regs

        except Exception as e:
            self.logger.error(e)

    def max_speed(self, hod, freq=119):
        try:
            koef = round((2 * 17.99) / (2 * 3.1415 * 0.98), 5)
            radius = round((hod / 1000) / 2, 3)
            return round((freq * radius) / koef, 3)

        except Exception as e:
            self.logger.error(e)

    def freq_from_speed(self, speed: float, hod: int):
        """Пересчёт скорости в частоту для записи в частотник"""
        try:
            koef = round((2 * 17.99) / (2 * 3.1415 * 0.98), 5)
            hod = hod / 1000
            radius = hod / 2
            freq = int(100 * (koef * speed) / radius)

            return freq

        except Exception as e:
            self.logger.error(e)

    def emergency_force(self, value):
        try:
            arr = []
            val = pack('>f', value)
            for i in range(0, 4, 2):
                arr.append(int((hex(val[i])[2:] + hex(val[i + 1])[2:]), 16))

            return arr

        except Exception as e:
            self.logger.error(e)

    def check_temperature(self, temp_list: list, max_temper: float):
        try:
            if max(temp_list) > max_temper:
                return max(temp_list)
            else:
                return max_temper

        except Exception as e:
            self.logger.error(e)

    def middle_min_and_max_force(self, data):
        try:
            rec_ind = data.index(max(data))
            max_rec = round(statistics.fmean(data[rec_ind - 5:rec_ind + 5]), 1)

            comp_ind = data.index(min(data))
            max_comp = round(statistics.fmean(data[comp_ind - 5:comp_ind + 5]), 1)

        except Exception as e:
            max_rec = 0
            max_comp = 0
            self.logger.error(e)
            
        finally:
            return max_rec, max_comp

    def offset_move_by_hod(self, amort, min_p):
        try:
            return round((float(amort.max_length) - float(amort.min_length) - float(amort.hod)) / 2 + min_p, 1)

        except Exception as e:
            self.logger.error(e)

    def power_amort(self, move, force):
        """Расчёт мощности"""
        try:
            temp = 0
            for i in range(1, len(move)):
                step = abs(abs(move[i]) - abs(move[i - 1]))
                
                if step > 0:
                    temp = round(temp + step * abs(force[i - 1]), 1)

            return round((temp * 0.009807) / 1000, 3)

        except Exception as e:
            self.logger.error(e)

    def freq_piston_amort(self, speed, hod):
        try:
            return round(speed / (int(hod) * 0.002 * 3.14), 3)

        except Exception as e:
            self.logger.error(e)

    def excess_force(self, amort):
        try:
            force = int(max(amort.max_comp, amort.max_recoil) * 5)
            if force >= 1900:
                return 1900
            else:
                return 1500

        except Exception as e:
            self.logger.error(e)
