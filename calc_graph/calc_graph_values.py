import numpy as np
from functools import reduce

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

    def speed_coord(self, move: list, index):
        try:
            speed_list = []
            y_coord = []

            if index != 0:
                shift_list = move[index:] + move[:index]
                temp_list = shift_list[5:] + shift_list + shift_list[:5]

            else:
                temp_list = move[5:] + move + move[:5]

            for i in range(len(move)):
                for j in range(10):
                    speed_list.append(round(abs(abs(temp_list[i + j]) - abs(temp_list[i + j + 1])), 3))

                temp = reduce(lambda x, y: round(x + y, 3), speed_list)
                y_coord.append(temp)
                speed_list = []

            return y_coord

        except Exception as e:
            self.logger.error(e)

    def coord_sinus(self, height, border, count_wave):
        """Расчёт графика синусоиды. height: высота волны, border: до какой точки, count_wave: количество волн"""
        try:
            height = int(height / 2)

            x = np.arange(border)
            y = np.sin(2 * np.pi * count_wave * x / border) * height

            return x, y

        except Exception as e:
            self.logger.error(e)
