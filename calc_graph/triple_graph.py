import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Qt

from logger import my_logger
from calc_data.data_calculation import CalcData
from calc_graph.abstract_graph import AbstractGraph
from calc_graph.calc_graph_values import CalcGraphValue


class TripleGraph:
    def __init__(self, widget):
        self.logger = my_logger.get_logger(__name__)
        self.widget = widget
        self.graph = AbstractGraph(widget)

    def gui_graph(self):
        try:
            kwargs = {'title': 'Диаграмма хода, скорости, силы сопротивления',
                      'left': ['left', 'Смещение или Скорость', 'мм или мм/с'],
                      'bottom': ['bottom', 'ω * t', '°'],
                      'right': ['right', 'Усилие', 'кгс']
                      }
            
            self.graph.gui_graph(**kwargs)
            
        except Exception as e:
            self.logger.error(e)
            
    def gui_axis(self):
        self.graph.gui_axis('left')
        self.graph.gui_axis('bottom')
        self.graph.gui_axis('right')
                
    def calc_force_graph(self, data):
        try:
            move_array = np.array(data.move_list)
            force_array = np.array(data.force_list)
            
            x_coord = np.linspace(0, 360, num=len(move_array))
            index_zero = np.where(x_coord >= 90)[0][0]

            y_coord = np.concatenate((force_array[index_zero:], force_array[:index_zero]))
            
            return x_coord, y_coord
            
        except Exception as e:
            self.logger.error(e)
            
    def calc_speed_graph(self, data):
        try:
            hod = int(data.hod)
            speed = float(data.speed)
            move_array = np.array(data.move_list)
            
            x_coord = np.linspace(0, 360, num=len(move_array))
            index_zero = np.where(x_coord >= 90)[0][0]

            speed_coord = CalcGraphValue().calc_speed_coord(hod, speed, x_coord)
            y_coord = np.concatenate((speed_coord[index_zero:], speed_coord[:index_zero]))
            
            return x_coord, y_coord
            
        except Exception as e:
            self.logger.error(e)
            
    def data_graph(self, data):
        try:
            recoil, comp = CalcData().middle_min_and_max_force(data.force_list)
            
            return {'speed': data.speed,
                    'recoil': recoil,
                    'comp': comp,
                    'push_force': 0,
                    }
            
        except Exception as e:
            self.logger.error(e)

    def fill_piston_graph(self, hod, pen=None, name='Смещение'):
        try:
            if pen == None:
                pen = pg.mkPen(color='black', width=3, style=Qt.DashDotLine)
                
            hod_x, hod_y = CalcGraphValue().coord_sinus(hod, 360, 1)
            
            self.widget.plot(hod_x, hod_y, pen=pen, name=name)

        except Exception as e:
            self.logger.error(e)

    def fill_force_graph(self, x_coord, y_coord, pen=None, name='Усилие'):
        try:
            if pen == None:
                pen = pg.mkPen(color='blue', width=3)
            self.widget.plot(x_coord, y_coord, pen=pen, name=name)

        except Exception as e:
            self.logger.error(e)

    def fill_speed_graph(self, x_coord, y_coord, pen=None, name='Скорость'):
        try:
            if pen == None:
                pen = pg.mkPen(color='red', width=3)
            self.widget.plot(x_coord, y_coord, pen=pen, name=name)

        except Exception as e:
            self.logger.error(e)
