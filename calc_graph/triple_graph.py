import pyqtgraph as pg
import numpy as np

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
            speed = float(data.speed)
            move_list = data.move_list
            force_list = data.force_list

            index_zero_point = self.calc_graph_values.calc_index_zero_point_piston(move_list, hod)

            self._fill_piston_graph(hod)

            x_coord = self.calc_graph_values.convert_move_to_deg(move_list)

            convert_force = self._convert_force_list(force_list, index_zero_point)
            self._fill_force_graph(x_coord, convert_force)

            speed_coord = self._calc_speed_coord(hod, speed, x_coord)
            self._fill_speed_graph(x_coord, speed_coord)

            recoil, comp = self.calc_data.middle_min_and_max_force(force_list)

            return {'recoil': recoil,
                    'comp': comp,
                    'push_force': 0,
                    }

        except Exception as e:
            self.logger.error(e)

    def _convert_force_list(self, force: list, index: int):
        try:
            temp = force[index:] + force[:index]
            temp_list = [x * (-1) for x in temp]

            return temp_list

        except Exception as e:
            self.logger.error(e)

    def _calc_speed_coord(self, hod: int, speed: float, angle: list):
        try:
            x = np.array(angle, 'float')
            radius = round((hod / 1000) / 2, 3)
            piston_rod = 0.4  # длина шатуна
            lam = round(radius / piston_rod, 3)

            first_order = radius * speed * np.sin(x)
            second_order = ((lam * radius * speed) / 2) * np.sin(2 * x)

            speed_order = (first_order + second_order) * 100

            return speed_order

            # pen_1 = pg.mkPen(color='black', width=3)
            # pen_2 = pg.mkPen(color='blue', width=3)
            # self.widget.plot(x, first_order, pen=pen_1, name='V1')
            # self.widget.plot(x, second_order, pen=pen_2, name='V2')
            #
            # pen = pg.mkPen(color='red', width=3)
            # self.widget.plot(x, speed_order, pen=pen, name='V')

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
