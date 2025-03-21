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
            y_approxy = np.convolve(w / w.sum(), coord, mode='same')

            return list(map(lambda x: round(x, 1), y_approxy))

        except Exception as e:
            self.logger.error(e)

    def speed_coord(self, move: list, index):
        try:
            speed_list = []
            y_coord = []

            if index != 0:
                shift_list = move[index:] + move[:index]
                temp_list = shift_list[-5:] + shift_list + shift_list[:5]

            else:
                temp_list = move[-5:] + move + move[:5]

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

            x = np.arange(border + 1)
            y = np.sin(2 * np.pi * count_wave * x / border) * height

            return x, y

        except Exception as e:
            self.logger.error(e)

    def calc_index_zero_point_piston(self, move: list, hod: int):
        try:
            mid_hod = hod // 2
            find_point = move[0] + mid_hod
            for point in move:
                if find_point - 1 < point < find_point + 1:
                    return move.index(point)

        except Exception as e:
            self.logger.error(e)

    def _offset_move_by_zero(self, move: list):
        try:
            koef = min(move)
            return [x + abs(koef) for x in move]

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
