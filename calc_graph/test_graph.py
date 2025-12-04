import pyqtgraph as pg
from PySide6.QtCore import Qt

from logger import my_logger
from calc_graph.abstract_graph import AbstractGraph


class TestGraph(AbstractGraph):
    def __init__(self, widget, tag):
        self.logger = my_logger.get_logger(__name__)
        self.widget = widget
        
        if tag == 'move':
            kwargs = {'title': 'График зависимости усилия от перемещения',
                    'left': ('left', 'Усилие', 'кгс'),
                    'bottom': ('bottom', 'Перемещение', 'мм')
                    }
        else:
            kwargs = {'title': 'График зависимости усилия от температуры',
                      'left': ('left', 'Усилие', 'кгс'),
                      'bottom': ('bottom', 'Температура', '℃')
                    }
        self.gui_graph(**kwargs)
        self.gui_axis('left')
        self.gui_axis('bottom')

    def fill_graph(self, x_coord, y_coord, pen=None, name='Сопротивление'):
        try:
            if pen == None:
                pen = pg.mkPen(color='black', width=3)
            self.widget.plot(x_coord, y_coord, pen=pen, name=name)

        except Exception as e:
            self.logger.error(e)
            
    def _select_color_line(self, ind):
        try:
            color_pen = ('black',
                         'blue',
                         'green',
                         'orange',
                         'purple',
                         'brown',
                         'olive',
                         'cyan',
                         'pink',
                         'red')
            
            if ind < 10:
                ind = ind
            elif 10 <= ind < 20:
                ind = ind - 10
            else:
                ind = ind - 20
                
            return color_pen[ind]
        
        except Exception as e:
            self.logger(e)
            
    def _select_line_style(self, ind):
        try:
            if ind < 10:
                return Qt.SolidLine
            elif 9 < ind < 20:
                return Qt.DashLine
            else:
                return Qt.DashDotDotLine
            
        except Exception as e:
            self.logger.error(e)

    def fill_compare_graph(self, compare_list):
        try:
            for ind, graph in enumerate(compare_list):
                name = f'{graph["speed"]} м/с'
                
                pen = pg.mkPen(color=self._select_color_line(ind),
                               width=3,
                               style=self._select_line_style(ind))

                self.widget.plot(graph['move'], graph['force'], pen=pen, name=name)
            
        except Exception as e:
            self.logger.error(e)
