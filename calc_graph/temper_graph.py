import pyqtgraph as pg

from logger import my_logger
from calc_data.data_calculation import CalcData
from calc_graph.calc_graph_values import CalcGraphValue


class TemperGraph:
    def __init__(self, widget):
        self.logger = my_logger.get_logger(__name__)
        self.calc_data = CalcData()
        self.calc_graph_values = CalcGraphValue()
        self.widget = widget

    def gui_graph(self):
        try:
            self.widget.plot(clear=True)
            self.widget.setLabel('left', 'Усилие', units='кгс')
            self.widget.setLabel('bottom', 'Температура', units='℃')
            self.widget.setLabel('right', 'Усилие', units='кгс')
            self.widget.setTitle('График зависимости усилия от температуры')
            self.widget.showGrid(True, True)
            self.widget.setBackground('w')
            self.widget.addLegend()

        except Exception as e:
            self.logger.error(e)

    def fill_graph(self, data):
        try:
            recoil_list = []
            comp_list = []
            temper_coord = data.temper_graph

            for value in data.temper_force_graph:
                value = value.strip('\'\"')
                value = value.replace(',', '.')
                value = value.split('|')
                recoil, comp = float(value[0]), float(value[1])
                recoil_list.append(recoil)
                comp_list.append(comp)

            push_force = self.calc_graph_values.select_push_force(data)

            pen_recoil = pg.mkPen(color='black', width=3)
            pen_comp = pg.mkPen(color='blue', width=3)

            self.widget.plot(temper_coord, recoil_list, pen=pen_recoil, name='Отбой')
            self.widget.plot(temper_coord, comp_list, pen=pen_comp, name='Сжатие')

            return {'recoil': recoil_list[-1],
                    'comp': comp_list[-1],
                    'push_force': push_force,
                    }

        except Exception as e:
            self.logger.error(e)
