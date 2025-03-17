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

            index_mid_hod = self._calc_index_zero_point_piston(move_list, hod)

            self._fill_piston_graph(hod)

            offset_list = self._offset_move_by_zero(move_list)
            unfold_move = self._unfolding_move(offset_list)
            convert_move = self._convert_move_to_deg(unfold_move)
            convert_force = self._convert_force_list(force_list, index_mid_hod)
            self._fill_force_graph(convert_move, convert_force)

            speed_list = self.calc_graph_values.speed_coord(move_list, index_mid_hod)
            round_speed_list = self.calc_graph_values.rounding_coord(speed_list, 5)
            speed_coord = [round(x * 100, 1) for x in round_speed_list]
            self._fill_speed_graph(convert_move, speed_coord)

            recoil, comp = self.calc_data.middle_min_and_max_force(force_list)

            return {'recoil': recoil,
                    'comp': comp,
                    'push_force': 0,
                    }

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
            way = []
            max_val = max(move)
            max_index = move.index(max_val)
            for i in range(len(move)):
                point = move[i]
                if i < max_index:
                    point = round(max_val - abs(move[i]) + max_val, 1)

                way.append(point)

            return way

        except Exception as e:
            self.logger.error(e)

    def _calc_index_zero_point_piston(self, move: list, hod: int):
        try:
            mid_hod = hod // 2
            find_point = move[0] + mid_hod
            for point in move:
                if find_point - 1 < point < find_point + 1:
                    return move.index(point)

        except Exception as e:
            self.logger.error(e)

    def _convert_move_to_deg(self, move: list):
        try:
            min_limit = 0
            max_limit = 360
            first_point = move[0]
            last_point = move[-1]

            k = round((max_limit - min_limit) / (last_point - first_point), 4)
            b = round(max_limit - k * last_point, 4)

            change_list = [round(k * x + b, 2) for x in move]

            return change_list

        except Exception as e:
            self.logger.error(e)

    def _convert_force_list(self, force: list, index: int):
        try:
            temp = force[index:] + force[:index]
            temp_list = [x * (-1) for x in temp]

            return temp_list

            # w = np.hanning(10)
            # force_approxy = np.convolve(w / w.sum(), temp_list, mode='same')
            #
            # return list(force_approxy)

        except Exception as e:
            self.logger.error(e)

    def _fill_piston_graph(self, hod):
        try:
            hod_x, hod_y = self.calc_graph_values.coord_sinus(hod, 360, 1)
            pen = pg.mkPen(color='black', width=3)
            self.widget.plot(hod_x, hod_y, pen=pen, name='Смещение')

        except Exception as e:
            self.logger.error(e)

    def _fill_force_graph(self, move: list, force: list):
        try:
            pen = pg.mkPen(color='blue', width=3)
            self.widget.plot(move, force, pen=pen, name='Усилие')

        except Exception as e:
            self.logger.error(e)

    def _fill_speed_graph(self, move, speed):
        try:
            pen = pg.mkPen(color='red', width=3)
            self.widget.plot(move, speed, pen=pen, name='Скорость')

        except Exception as e:
            self.logger.error(e)
