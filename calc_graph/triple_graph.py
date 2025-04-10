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
            self.widget.setTitle('Диаграмма хода, скорости, силы сопротивления')
            self.widget.setLabel('bottom', 'ω * t', units='°', color='k')
            self.widget.setLabel('left', 'Смещение или Скорость', units='мм или мм/с', color='r')
            self.widget.setLabel('right', 'Усилие', units='кгс', color='b')
            self.widget.showGrid(True, True)
            self.widget.setBackground('w')
            self.widget.addLegend()

        except Exception as e:
            self.logger.error(e)

    def fill_graph(self, data):
        try:
            hod = int(data.amort.hod)
            speed = float(data.speed)
            move_array = np.array(data.move_list)
            force_array = np.array(data.force_list)

            self._fill_piston_graph(hod)

            x_coord = np.linspace(0, 360, num=len(move_array))
            index_zero = np.where(x_coord >= 90)[0][0]

            reversed_force = force_array * (-1)
            offset_force = np.concatenate((reversed_force[index_zero:], reversed_force[:index_zero]))
            self._fill_force_graph(x_coord, offset_force)

            speed_coord = self.calc_graph_values.calc_speed_coord(hod, speed, x_coord)
            offset_speed = np.concatenate((speed_coord[index_zero:], speed_coord[:index_zero]))

            self._fill_speed_graph(x_coord, offset_speed)

            recoil, comp = self.calc_data.middle_min_and_max_force(force_array)

            return {'recoil': recoil,
                    'comp': comp,
                    'push_force': 0,
                    }

        except Exception as e:
            self.logger.error(e)

    def _fill_piston_graph(self, hod):
        try:
            hod_x, hod_y = self.calc_graph_values.coord_sinus(hod, 360, 1)
            pen = pg.mkPen(color='black', width=3)
            self.widget.plot(hod_x, hod_y, pen=pen, name='Смещение')

        except Exception as e:
            self.logger.error(e)

    def _fill_force_graph(self, move, force):
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
