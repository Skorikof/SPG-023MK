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
            move_list = data.move_list
            force_list = data.force_list
            push_force = self.calc_graph_values.select_push_force(data)

            recoil, comp = self.calc_data.middle_min_and_max_force(force_list)

            max_recoil = round(recoil + push_force, 2)
            max_comp = round(comp - push_force, 2)

            speed_coord = self.calc_graph_values.speed_coord(move_list, 'boost_one')
            x_coord = self.calc_graph_values.rounding_coord(speed_coord, 10)

            pen = pg.mkPen(color='blue', width=5)
            self.widget.plot(x_coord, force_list, pen=pen, name='Скорость')

            return {'recoil': max_recoil,
                    'comp': max_comp,
                    'push_force': push_force}

        except Exception as e:
            self.logger.error(e)
