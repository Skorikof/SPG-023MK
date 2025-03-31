import pyqtgraph as pg

from logger import my_logger
from calc_data.data_calculation import CalcData
from calc_graph.calc_graph_values import CalcGraphValue


class CascadeGraph:
    def __init__(self, widget):
        self.logger = my_logger.get_logger(__name__)
        self.calc_data = CalcData()
        self.calc_graph_values = CalcGraphValue()
        self.widget = widget

    def gui_graph(self):
        try:
            self.widget.plot(clear=True)
            self.widget.setLabel('left', 'Усилие', units='кгс')
            self.widget.setLabel('bottom', 'Скорость', units='м/с')
            self.widget.setLabel('right', 'Усилие', units='кгс')
            self.widget.setTitle('График зависимости усилия от скорости')
            self.widget.showGrid(True, True)
            self.widget.setBackground('w')
            self.widget.addLegend()

        except Exception as e:
            self.logger.error(e)

    def limit_line_graph(self, obj):
        try:
            lim_speed_1 = []
            lim_speed_2 = []
            lim_recoil_1 = []
            lim_recoil_2 = []
            lim_comp_1 = []
            lim_comp_2 = []

            lim_speed_1.append(float(obj.amort.speed_one))
            lim_speed_1.append(float(obj.amort.speed_one))
            lim_speed_2.append(float(obj.amort.speed_two))
            lim_speed_2.append(float(obj.amort.speed_two))

            lim_recoil_1.append(float(obj.amort.min_recoil))
            lim_recoil_1.append(float(obj.amort.max_recoil))
            lim_recoil_2.append(float(obj.amort.max_recoil_2))
            lim_recoil_2.append(float(obj.amort.min_recoil_2))

            lim_comp_1.append(float(obj.amort.min_comp) * -1)
            lim_comp_1.append(float(obj.amort.max_comp) * -1)
            lim_comp_2.append(float(obj.amort.max_comp_2) * -1)
            lim_comp_2.append(float(obj.amort.min_comp_2) * -1)

            pen = pg.mkPen(color='red', width=2)

            self.widget.plot(lim_speed_1, lim_recoil_1, pen=pen)
            self.widget.plot(lim_speed_2, lim_recoil_2, pen=pen)
            self.widget.plot(lim_speed_1, lim_comp_1, pen=pen)
            self.widget.plot(lim_speed_2, lim_comp_2, pen=pen)

        except Exception as e:
            self.logger.error(e)

    def fill_graph(self, data):
        try:
            speed_list = [0]
            comp_list = [0]
            recoil_list = [0]

            for obj in data:
                speed_list.append(float(obj.speed))
                push_force = self.calc_graph_values.select_push_force(obj)

                recoil, comp = self.calc_data.middle_min_and_max_force(obj.force_list)

                recoil_list.append(round(recoil + push_force, 2))
                comp_list.append(round(comp * (-1) + push_force, 2))

            pen_recoil = pg.mkPen(color='black', width=3)
            pen_comp = pg.mkPen(color='blue', width=3)

            recoil_x, recoil_interp = self.calc_graph_values.interpoly_line_coord(speed_list, recoil_list)
            comp_x, comp_interp = self.calc_graph_values.interpoly_line_coord(speed_list, comp_list)

            self.widget.plot(recoil_x, recoil_interp, pen=pen_recoil, name='Отбой')
            self.widget.plot(comp_x, comp_interp, pen=pen_comp, name='Сжатие')

            self.limit_line_graph(data[0])

            return {'recoil': max(recoil_list),
                    'comp': abs(min(comp_list))}

        except Exception as e:
            self.logger.error(e)
