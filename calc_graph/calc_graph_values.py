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

    def rounding_coord(self, coord: list, degree: int):
        try:
            w = np.hanning(degree)
            list_approxy = np.convolve(w / w.sum(), coord, mode='same')

            return list(map(lambda x: round(x, 3), list_approxy))

        except Exception as e:
            self.logger.error(e)

    def speed_coord(self, move: list, tag):
        try:
            speed_list = []
            y_coord = []

            temp_list = move[-5:] + move + move[:5]

            if tag == 'boost_one':
                for i in range(len(move)):
                    for j in range(10):
                        speed_list.append(round(abs(abs(temp_list[i + j + 1]) - abs(temp_list[i + j])), 3))

                    mid_val = round(sum(speed_list) / 10, 3)
                    y_coord.append(mid_val)
                    speed_list = []

            elif tag == 'boost_two':
                for i in range(len(move)):
                    for j in range(10):
                        speed_list.append(round(temp_list[i + j + 1] - temp_list[i + j], 3))

                    mid_val = round(sum(speed_list) / 10, 3)
                    y_coord.append(mid_val)
                    speed_list = []

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

    def _offset_move_by_zero(self, move: list):
        try:
            koef = min(move)
            return [round(x + abs(koef), 3) for x in move]

        except Exception as e:
            self.logger.error(e)

    def _unfolding_move(self, move: list):
        try:
            offset_list = self._offset_move_by_zero(move)
            way = []
            max_val = max(offset_list)
            max_index = offset_list.index(max_val)
            for i in range(len(offset_list)):
                point = offset_list[i]
                if i < max_index:
                    point = round(max_val - abs(offset_list[i]) + max_val, 1)

                way.append(point)

            return way

        except Exception as e:
            self.logger.error(e)

    def convert_move_to_deg(self, move: list):
        try:
            unfold_move = self._unfolding_move(move)
            min_limit = 0
            max_limit = 360
            first_point = unfold_move[0]
            last_point = unfold_move[-1]

            k = round((max_limit - min_limit) / (last_point - first_point), 4)
            b = round(max_limit - k * last_point, 4)

            change_list = [round(k * x + b, 2) for x in unfold_move]

            return change_list

        except Exception as e:
            self.logger.error(e)

    def calc_index_zero_point_piston(self, angle: list):
        try:
            for point in angle:
                if 90 - 2 < point < 90 + 2:
                    return angle.index(point)

        except Exception as e:
            self.logger.error(e)

    def offset_force_coord(self, force, index):
        try:
            force = [x * (-1) for x in force]
            force_list = force[index:] + force[:index]

            return force_list

        except Exception as e:
            self.logger.error(e)

    def calc_speed_coord(self, hod: int, speed: float, angle: list, index: int):
        try:
            x_rad = np.radians(angle)
            radius = round((hod / 1000) / 2, 3)
            piston_rod = 0.4  # длина шатуна
            lam = round(radius / piston_rod, 3)

            first_order = radius * speed * np.sin(x_rad)
            second_order = ((lam * radius * speed) / 2) * np.sin(2 * x_rad)

            speed_order = list((first_order + second_order) * 10000)

            speed_list = speed_order[index:] + speed_order[:index]

            return speed_list

        except Exception as e:
            self.logger.error(e)
