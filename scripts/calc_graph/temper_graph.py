import pyqtgraph as pg

from scripts.logger import my_logger
from scripts.calc_graph.abstract_graph import AbstractGraph
from scripts.calc_graph.calc_graph_values import CalcGraphValue


class TemperGraph(AbstractGraph):
    def __init__(self, widget):
        self.logger = my_logger.get_logger(__name__)
        self.widget = widget
        kwargs = {'title': 'График зависимости усилия от температуры',
                      'left': ('left', 'Усилие', 'кгс'),
                      'bottom': ('bottom', 'Температура', '℃')
                      }
            
        self.gui_graph(**kwargs)
        self.gui_axis('left')
        self.gui_axis('bottom')
            
    def calc_graph(self, data):
        try:
            push_force = CalcGraphValue().select_push_force(data)
            
            recoil = [x + push_force for x in data.recoil_list]
            comp = [x + push_force for x in data.comp_list]
            
            return {'y_rec': recoil,
                    'y_comp': comp,
                    'x_temp': data.temper_list,
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
