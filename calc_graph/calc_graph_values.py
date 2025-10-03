import numpy as np
from scipy import interpolate

from logger import my_logger


class CalcGraphValue:
    def __init__(self):
        self.logger = my_logger.get_logger(__name__)

    def select_push_force(self, data):
        try:
            flag_push_force = data.flag_push_force
            if flag_push_force == '1':
                return float(data.dynamic_push_force)

            elif flag_push_force == '0':
                return float(data.static_push_force)

            else:
                return 0

        except Exception as e:
            self.logger.error(e)

    def rounding_coord(self, coord, degree: int):
        try:
            w = np.hanning(degree)
            return np.round(np.convolve(w / w.sum(), coord, mode='same'), decimals=3)

        except Exception as e:
            self.logger.error(e)

    def speed_coord(self, move, tag):
        try:
            y_coord = []

            move_array = np.concatenate((move[-5:], move, move[:5]))

            if tag == 'one':
                for i in range(len(move)):
                    y_coord.append(round(np.std(move_array[i:i + 10]), 3))

            elif tag == 'two':
                for i in range(len(move)):
                    speed_coord = []
                    for j in range(10):
                        speed_coord.append(move_array[i + j + 1] - move_array[i + j])
                    y_coord.append(round(sum(speed_coord) / 10, 3))

            return y_coord

        except Exception as e:
            self.logger.error(e)

    def coord_sinus(self, height, border, count_wave):
        """Расчёт графика синусоиды. height: высота волны, border: до какой точки, count_wave: количество волн"""
        try:
            height = int(height / 2)

            x = np.arange(border + 1)
            y = np.sin(2 * np.pi * count_wave * x / border) * height

            return x, y

        except Exception as e:
            self.logger.error(e)

    def calc_speed_coord(self, hod: int, speed: float, angle):
        try:
            x_rad = np.radians(angle)
            radius = round((hod / 1000) / 2, 3)
            piston_rod = 0.4  # длина шатуна
            lam = round(radius / piston_rod, 3)

            first_order = radius * speed * np.sin(x_rad)
            second_order = ((lam * radius * speed) / 2) * np.sin(2 * x_rad)

            speed_order = (first_order + second_order) * 10000

            return speed_order

        except Exception as e:
            self.logger.error(e)

    def interpoly_line_coord(self, x, y):
        try:
            f = interpolate.interp1d(x, y, kind='cubic')
            x_new = np.linspace(0, max(x), num=10000)
            y_new = f(x_new)
            return x_new, y_new

        except Exception as e:
            self.logger.error(e)
            return x, y
