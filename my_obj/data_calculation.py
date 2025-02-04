import numpy as np
from struct import pack

from logger import my_logger


class SpeedLimitForHod:
    def speed_limit(self, hod):
        if 40 <= hod < 50:
            return 0.41
        elif 50 <= hod < 60:
            return 0.51
        elif 60 <= hod < 70:
            return 0.62
        elif 70 <= hod < 80:
            return 0.72
        elif 80 <= hod < 90:
            return 0.82
        elif 90 <= hod < 100:
            return 0.92
        elif 100 <= hod < 110:
            return 1.03
        elif 110 <= hod < 120:
            return 1.13
        elif hod == 120:
            return 1.23
        else:
            return 0.41


class CalcData:
    def __init__(self):
        self.logger = my_logger.get_logger(__name__)

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

    def middle_min_and_max_force(self, data: list):
        try:
            comp_index = data.index(min(data))
            comp_list = [abs(x) for x in data[comp_index - 10:comp_index + 10]]
            max_comp = round((sum(comp_list) / len(comp_list)), 1)

            recoil_index = data.index(max(data))
            recoil_list = [abs(x) for x in data[recoil_index - 10:recoil_index + 10]]
            max_recoil = round((sum(recoil_list) / len(recoil_list)), 1)

            return max_recoil, max_comp

        except Exception as e:
            self.logger.error(e)

    def offset_move_by_hod(self, amort, min_p):
        try:
            return round((float(amort.max_length) - float(amort.min_length) - float(amort.hod)) / 2 + min_p, 2)

        except Exception as e:
            self.logger.error(e)

    def power_amort(self, move: list, force: list):
        try:
            temp = 0
            for i in range(1, len(move)):
                temp = round(temp + abs(move[i] - abs(move[i - 1])) * abs(force[i - 1]), 1)

            temp = round((temp * 0.009807) / 1000, 3)

            return temp

        except Exception as e:
            self.logger.error(e)

    def freq_piston_amort(self, speed, amort):
        try:
            return round(speed / (int(amort.hod) * 0.002 * 3.14), 3)

        except Exception as e:
            self.logger.error(e)

    def calc_coord_sinus(self, height, border, count_wave):
        """Расчёт графика синусоиды. height: высота волны, border: до какой точки, count_wave: количество волн"""
        try:
            height = int(height / 2)

            x = np.arange(border)
            y = np.sin(2 * np.pi * count_wave * x / border) * height

            return x, y

        except Exception as e:
            self.logger.error(e)
