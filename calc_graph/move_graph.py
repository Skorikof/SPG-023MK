import pyqtgraph as pg

from logger import my_logger
from calc_data.data_calculation import CalcData
from calc_graph.abstract_graph import AbstractGraph
from calc_graph.calc_graph_values import CalcGraphValue


class MoveGraph:
    def __init__(self, widget):
        self.logger = my_logger.get_logger(__name__)
        self.widget = widget
        self.graph = AbstractGraph(widget)

    def gui_graph(self):
        try:
            kwargs = {'title': 'График зависимости усилия от перемещения',
                      'left': ['left', 'Усилие', 'кгс'],
                      'bottom': ['bottom', 'Перемещение', 'мм']
                      }
            
            self.graph.gui_graph(**kwargs)
                        
        except Exception as e:
            self.logger.error(e)
            
    def gui_axis(self):
        self.graph.gui_axis('left')
        self.graph.gui_axis('bottom')

    def fill_graph(self, x_coord, y_coord, pen=None, name='Сопротивление'):
        try:
            if pen == None:
                pen = pg.mkPen(color='black', width=3)
            self.widget.plot(x_coord, y_coord, pen=pen, name=name)

        except Exception as e:
            self.logger.error(e)

    def data_graph(self, data):
        try:
            recoil, comp = CalcData().middle_min_and_max_force(data.force_list)
            push_force = CalcGraphValue().select_push_force(data)

            max_recoil = round(recoil + push_force, 2)
            max_comp = round(comp - push_force, 2)

            power = CalcData().power_amort(data.move_list, data.force_list)

            speed = float(data.speed)
            freq = CalcData().freq_piston_amort(speed, data.amort.hod)

            return {'recoil': max_recoil,
                    'comp': max_comp,
                    'push_force': push_force,
                    'power': power,
                    'speed': speed,
                    'freq': freq}

        except Exception as e:
            self.logger.error(e)
