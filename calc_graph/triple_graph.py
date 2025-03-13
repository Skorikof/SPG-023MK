import numpy as np
import pyqtgraph as pg

from logger import my_logger
from calc_data.data_calculation import CalcData
from calc_graph.calc_graph_values import CalcGraphValue


class TripleGraph:
    def __init__(self, widget):
        self.logger = my_logger.get_logger(__name__)
        self.calc_data = CalcData()
        self.calc_graph_values = CalcGraphValue()
        self.widget = widget

    def gui_graph(self):
        try:
            self.widget.plot(clear=True)
            self.widget.setLabel('left', 'Смещение или Скорость', units='мм или мм/с')
            self.widget.setLabel('bottom', 'ω * t', units='°')
            self.widget.setLabel('right', 'Усилие', units='кгс')
            self.widget.setTitle('Диаграмма хода, скорости, силы сопротивления')
            self.widget.showGrid(True, True)
            self.widget.setBackground('w')
            self.widget.addLegend()

        except Exception as e:
            self.logger.error(e)

    def fill_graph(self, data):
        try:
            hod = int(data.amort.hod)
            move_list = data.move_list
            force_list = data.force_list

            recoil, comp = self.calc_data.middle_min_and_max_force(force_list)

            self._fill_triple_hod_graph(hod)

            # index_mid_hod = self._calc_index_middle_hod_triple(move_list, hod)
            #
            # index_max_force = force_list.index(max(force_list))
            #
            # correct_move = self.calc_data.offset_move_list_by_zero(move_list, index_mid_hod)
            #
            # force_coord = self._force_triple_graph(force_list, index_mid_hod)
            #
            # move_coord = self._convert_triple_move_in_degrees_coord(correct_move, index_max_force)
            #
            # self._fill_triple_force_graph(move_coord, force_coord)

            # x_coord = self._convert_triple_move_in_degrees_coord(correct_move)
            #
            # # index_mid_hod = self._calc_index_middle_hod_triple(x_coord, hod)
            #
            # self._fill_triple_force_graph(x_coord, force_list, index_mid_hod)
            #
            # self._fill_triple_speed_graph(correct_move, x_coord, index_mid_hod)

            return {'recoil': recoil,
                    'comp': comp,
                    'push_force': 0,
                    }

        except Exception as e:
            self.logger.error(e)

    def _fill_triple_hod_graph(self, hod):
        try:
            hod_x, hod_y = self.calc_graph_values.coord_sinus(hod, 360, 1)
            pen = pg.mkPen(color='black', width=3)
            self.widget.plot(hod_x, hod_y, pen=pen, name='Смещение')

        except Exception as e:
            self.logger.error(e)

    def _calc_index_middle_hod_triple(self, move: list, hod: int):
        try:
            mid_hod = hod // 2
            find_point = move[0] + mid_hod
            for point in move:
                if find_point - 1 < point < find_point + 1:
                    return move.index(point)

        except Exception as e:
            self.logger.error(e)

    def _force_triple_graph(self, force: list, index: int):
        try:
            return [x * (-1) for x in force[:index] + force[index:]]

        except Exception as e:
            self.logger.error(e)

    def _fill_triple_force_graph(self, move: list, force: list):
        try:
            # force_y = self._calc_triple_force_coord(force, index)
            pen = pg.mkPen(color='blue', width=3)
            self.widget.plot(move, force, pen=pen, name='Усилие')

        except Exception as e:
            self.logger.error(e)

    def _calc_triple_force_coord(self, force: list, index):
        try:
            return list(map(lambda x: round(x * (-1), 1), force[index:] + force[:index]))

        except Exception as e:
            self.logger.error(e)

    def _convert_triple_move_in_degrees_coord(self, move: list, index: int):
        try:
            way = []
            max_point = move[index]
            for i in range(len(move)):
                point = move[i]
                if i > index:
                    point = round(max_point - abs(move[i]) + max_point, 1)
                way.append(point)

            return way

            # way = []
            #
            # max_point = max(move)
            # max_index = move.index(max_point)
            #
            # for i in range(len(move)):
            #     point = move[i]
            #     if i > max_index:
            #         point = round(max_point - abs(move[i]) + max_point, 1)
            #
            #     way.append(point)
            #
            # max_way = max(way)
            #
            # return list(map(lambda x: round(360 * x / max_way, 1), way))

        except Exception as e:
            self.logger.error(e)

    def _fill_triple_speed_graph(self, move: list, x_coord: list, index):
        try:
            speed_list = self.calc_graph_values.speed_coord(move, index)

            w = np.hanning(200)
            y_approxy = np.convolve(w / w.sum(), speed_list, mode='same')

            speed_y = list(map(lambda x: round(x * 100, 1), y_approxy))

            pen = pg.mkPen(color='red', width=3)
            self.widget.plot(x_coord, speed_y,
                             pen=pen,
                             name='Скорость')

        except Exception as e:
            self.logger.error(e)
