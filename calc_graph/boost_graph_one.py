import numpy as np
import pyqtgraph as pg

from logger import my_logger
from calc_data.data_calculation import CalcData
from calc_graph.calc_graph_values import CalcGraphValue


class BoostGraphOne:
    def __init__(self, widget):
        self.logger = my_logger.get_logger(__name__)
        self.calc_graph_values = CalcGraphValue()
        self.calc_data = CalcData()
        self.widget = widget

    def gui_graph(self):
        try:
            self.widget.plot(clear=True)
            self.widget.setLabel('left', 'Усилие', units='кгс')
            self.widget.setLabel('bottom', 'Скорость', units='м/с')
            self.widget.setLabel('right', 'Усилие', units='кгс')
            self.widget.setTitle('График зависимости усилия от скорости')
            self.widget.showGrid(True, True)
            self.widget.setBackground('w')
            self.widget.addLegend()

        except Exception as e:
            self.logger.error(e)

    def fill_graph(self, data):
        try:
            move_array = np.array(data.move_list)
            force_array = np.array(data.force_list)
            push_force = self.calc_graph_values.select_push_force(data)

            recoil, comp = self.calc_data.middle_min_and_max_force(force_array)

            max_recoil = round(recoil + push_force, 2)
            max_comp = round(comp - push_force, 2)

            speed_coord = self.calc_graph_values.speed_coord(move_array, 'one')
            round_coord = self.calc_graph_values.rounding_coord(speed_coord, 50)

            # revers_force = [round(x * (-1), 1) for x in force_list]
            x_coord = np.concatenate((round_coord, round_coord[:1]))
            y_coord = np.concatenate((force_array, force_array[:1]))

            pen = pg.mkPen(color='blue', width=5)
            self.widget.plot(x_coord, y_coord, pen=pen, name='Скорость')

            return {'recoil': max_recoil,
                    'comp': max_comp,
                    'push_force': push_force}

        except Exception as e:
            self.logger.error(e)
