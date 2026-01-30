import pyqtgraph as pg

from scripts.logger import my_logger
from scripts.data_calculation import CalcData
from scripts.calc_graph.abstract_graph import AbstractGraph
from scripts.calc_graph.calc_graph_values import CalcGraphValue


class MoveGraph(AbstractGraph):
    AXES_CONFIG = {
        'title': 'График зависимости усилия от перемещения',
        'left': ('left', 'Усилие', 'кгс'),
        'bottom': ('bottom', 'Перемещение', 'мм')
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
            max_comp = round(comp + push_force, 2)

            power = CalcData().power_amort(data.move_list, data.force_list)

            speed = float(data.speed)
            freq = CalcData().freq_piston_amort(speed, data.hod)

            return {'recoil': max_recoil,
                    'comp': max_comp,
                    'push_force': push_force,
                    'power': power,
                    'speed': speed,
                    'freq': freq}

        except Exception as e:
            self.logger.error(e)
