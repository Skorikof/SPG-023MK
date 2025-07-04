import pyqtgraph as pg
import numpy as np

from logger import my_logger
from calc_graph.abstract_graph import AbstractGraph
from calc_graph.calc_graph_values import CalcGraphValue


class TemperGraph:
    def __init__(self, widget):
        self.logger = my_logger.get_logger(__name__)
        self.widget = widget
        self.graph = AbstractGraph(widget)

    def gui_graph(self):
        try:
            kwargs = {'title': 'График зависимости усилия от температуры',
                      'left': ['left', 'Усилие', 'кгс'],
                      'bottom': ['bottom', 'Температура', '℃']
                      }
            
            self.graph.gui_graph(**kwargs)
            self.graph.gui_axis('left')
            self.graph.gui_axis('bottom')
            
        except Exception as e:
            self.logger.error(e)
            
    def calc_graph(self, data):
        try:
            push_force = CalcGraphValue().select_push_force(data)
            
            y_coord_recoil = np.array(data.recoil_list) + push_force
            y_coord_comp = np.array(data.comp_list) + push_force
                        
            return data.temper_list, y_coord_recoil, y_coord_comp
            
        except Exception as e:
            self.logger.error(e)

    def fill_graph(self, x_coord, y_r, y_c, pen_r=None, pen_c=None, name_r='Отбой', name_c='Сжатие'):
        try:
            if pen_r == None:
                pen_r = pg.mkPen(color='black', width=3)
            if pen_c == None:
                pen_c = pg.mkPen(color='blue', width=3)

            self.widget.plot(x_coord, y_r, pen=pen_r, name=name_r)
            self.widget.plot(x_coord, y_c, pen=pen_c, name=name_c)

        except Exception as e:
            self.logger.error(e)
            
    def data_graph(self, data):
        try:
            push_force = CalcGraphValue().select_push_force(data)
            
            recoil = np.array(data.recoil_list) + push_force
            comp = np.array(data.comp_list) + push_force
            
            
            return {'start_recoil': recoil[0],
                    'end_recoil': recoil[-1],
                    'start_comp': comp[0],
                    'end_comp': comp[-1],
                    'start_temper': data.temper_list[0],
                    'end_temper': data.temper_list[-1],
                    'push_force': push_force,
                    'speed': data.speed,
                    }

        except Exception as e:
            self.logger.error(e)
