import pyqtgraph as pg
import numpy as np

from logger import my_logger
from calc_graph.calc_graph_values import CalcGraphValue


class TemperGraph:
    def __init__(self, widget):
        self.logger = my_logger.get_logger(__name__)
        self.widget = widget

    def gui_graph(self):
        try:
            self.widget.plot(clear=True)
            self.widget.setLabel('left', 'Усилие', units='кгс')
            self.widget.setLabel('bottom', 'Температура', units='℃')
            self.widget.setTitle('График зависимости усилия от температуры')
            self.widget.showGrid(True, True)
            self.widget.setBackground('w')
            self.widget.addLegend()

        except Exception as e:
            self.logger.error(e)

    def fill_graph(self, data):
        try:
            push_force = CalcGraphValue().select_push_force(data)
            
            recoil = np.array(data.recoil_list) + push_force
            comp = np.array(data.comp_list) + push_force

            pen_recoil = pg.mkPen(color='black', width=3)
            pen_comp = pg.mkPen(color='blue', width=3)

            self.widget.plot(data.temper_list, recoil, pen=pen_recoil, name='Отбой')
            self.widget.plot(data.temper_list, comp, pen=pen_comp, name='Сжатие')

            return {'recoil': recoil,
                    'comp': comp,
                    'push_force': push_force,
                    }

        except Exception as e:
            self.logger.error(e)
