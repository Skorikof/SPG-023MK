import pyqtgraph as pg
from logger import my_logger

from calc_data.data_calculation import CalcData
from calc_graph.calc_graph_values import CalcGraphValue


class MoveGraph:
    def __init__(self, widget):
        self.logger = my_logger.get_logger(__name__)
        self.calc_data = CalcData()
        self.calc_graph_values = CalcGraphValue()
        self.widget = widget

    def gui_graph(self):
        try:
            self.widget.plot(clear=True)
            self.widget.setLabel('left', 'Усилие', units='кгс', color='k')
            self.widget.setLabel('bottom', 'Перемещение', units='мм', color='k')
            self.widget.setLabel('right', 'Усилие', units='кгс', color='k')
            self.widget.setTitle('График зависимости усилия от перемещения', color='k', size='14pt')
            self.widget.showGrid(True, True)
            self.widget.setBackground('w')
            self.widget.addLegend()

        except Exception as e:
            self.logger.error(e)

    def fill_graph(self, data):
        try:
            move_list = data.move_list
            force_list = data.force_list

            recoil, comp = self.calc_data.middle_min_and_max_force(force_list)
            push_force = self.calc_graph_values.select_push_force(data)

            max_recoil = round(recoil + push_force, 2)
            max_comp = round(comp - push_force, 2)

            power = self.calc_data.power_amort(move_list, force_list)

            speed = float(data.speed)
            freq = self.calc_data.freq_piston_amort(speed, data.amort.hod)

            pen = pg.mkPen(color='black', width=3)

            self.widget.plot(move_list, force_list, pen=pen)

            return {'recoil': max_recoil,
                    'comp': max_comp,
                    'push_force': push_force,
                    'power': power,
                    'speed': speed,
                    'freq': freq}

        except Exception as e:
            self.logger.error(e)
