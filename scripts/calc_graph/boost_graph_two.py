import numpy as np
import pyqtgraph as pg

from scripts.logger import my_logger
from scripts.data_calculation import CalcData
from scripts.calc_graph.abstract_graph import AbstractGraph
from scripts.calc_graph.calc_graph_values import CalcGraphValue


class BoostGraphTwo(AbstractGraph):
    def __init__(self, widget):
        self.logger = my_logger.get_logger(__name__)
        self.widget = widget
        
        kwargs = {'title': 'График зависимости усилия от скорости',
                  'left': ('left', 'Усилие', 'кгс'),
                  'bottom': ('bottom', 'Скорость', 'м/с')
                  }
        self.gui_graph(**kwargs)
        self.gui_axis('left')
        self.gui_axis('bottom')
            
    def calc_graph(self, data):
        try:
            push_force = CalcGraphValue().select_push_force(data)
            recoil, comp = CalcData().middle_min_and_max_force(data.force_list)
            max_recoil = round(recoil + push_force, 2)
            max_comp = round(comp + push_force, 2)
            
            move_array = np.array(data.move_list)
            force_array = np.array(data.force_list)
            speed_coord = CalcGraphValue().speed_coord(move_array, 'two')
            round_coord = CalcGraphValue().rounding_coord(speed_coord, 50)
            reverse_x = round_coord * (-1)
            x_coord = np.concatenate((reverse_x, reverse_x[:1]))
            y_coord = np.concatenate((force_array, force_array[:1]))
            
            return {'x_coord': x_coord,
                    'y_coord': y_coord,
                    'recoil': max_recoil,
                    'comp': max_comp,
                    'push_force': push_force}
            
        except Exception as e:
            self.logger.error(e)

    def fill_graph(self, x_coord, y_coord, pen=None, name='Скорость'):
        try:
            if pen == None:
                pen = pg.mkPen(color='blue', width=5)

            self.widget.plot(x_coord, y_coord, pen=pen, name=name)

        except Exception as e:
            self.logger.error(e)
