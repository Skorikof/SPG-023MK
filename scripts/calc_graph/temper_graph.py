# -*- coding: utf-8 -*-
import pyqtgraph as pg

from scripts.logger import my_logger
from scripts.calc_graph.abstract_graph import AbstractGraph
from scripts.calc_graph.calc_graph_values import CalcGraphValue


class TemperGraph(AbstractGraph):
    AXES_CONFIG = {
        'title': 'График зависимости усилия от температуры',
        'left': ('left', 'Усилие', 'кгс'),
        'bottom': ('bottom', 'Температура', '℃')
    }

    def __init__(self, widget):
        self.logger = my_logger.get_logger(__name__)
        self.widget = widget
        
        self.gui_graph(**self.AXES_CONFIG)
        self._initialize_axes()
    
    def _initialize_axes(self):
        """Initialize graph axes from configuration."""
        for axis_key in ('left', 'bottom'):
            self.gui_axis(axis_key)
            
    def calc_graph(self, data):
        try:
            push_force = CalcGraphValue().select_push_force(data)
            
            recoil = [x + push_force for x in data.recoil_list]
            comp = [x + push_force for x in data.comp_list]
            
            x_coord = data.temper_list
            r_x, r_y = CalcGraphValue().interpoly_line_coord(x_coord, recoil, start_point=x_coord[0])
            c_x, c_y = CalcGraphValue().interpoly_line_coord(x_coord, comp, start_point=x_coord[0])
            
            return {'y_rec': r_y,
                    'y_comp': c_y,
                    'x_rec': r_x,
                    'x_comp': c_x,
                    'start_recoil': recoil[0],
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

    def fill_graph(self, x_r, y_r, x_c, y_c, pen_r=None, pen_c=None, name_r='Отбой', name_c='Сжатие'):
        try:
            if pen_r is None:
                pen_r = pg.mkPen(color='black', width=3)
            if pen_c is None:
                pen_c = pg.mkPen(color='blue', width=3)

            self.widget.plot(x_r, y_r, pen=pen_r, name=name_r)
            self.widget.plot(x_c, y_c, pen=pen_c, name=name_c)

        except Exception as e:
            self.logger.error(e)
