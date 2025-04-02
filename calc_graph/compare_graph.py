import pyqtgraph as pg

from logger import my_logger
from calc_data.data_calculation import CalcData
from calc_graph.calc_graph_values import CalcGraphValue
from calc_graph.cascad_graph import CascadeGraph


class CompareGraph:
    def __init__(self, widget):
        self.logger = my_logger.get_logger(__name__)
        self.widget = widget
        self.calc_data = CalcData()
        self.calc_graph_values = CalcGraphValue()
        self.cascade_graph = CascadeGraph(widget)

        self.color_pen = ['black',
                          'blue',
                          'green',
                          'orange',
                          'purple',
                          'brown',
                          'olive',
                          'cyan',
                          'yellow',
                          'pink',
                          'grey',
                          'red']

    def show_graph(self, type_graph, obj):
        try:
            self.widget.plot(clear=True)
            if type_graph == 'move':
                self.move_graph(obj)

            elif type_graph == 'conv':
                self.conv_graph(obj)

            elif type_graph == 'speed':
                self.speed_graph(obj)

        except Exception as e:
            self.logger.error(e)

    def conv_graph(self, obj):
        try:
            for graph in obj:
                x_list = graph.move_list
                y_list = graph.force_list
                pen = pg.mkPen(color=self.color_pen[obj.index(graph)], width=3)
                name = (f'{graph.time_test} - '
                        f'{graph.amort.name} - '
                        f'{graph.serial_number} - '
                        f'{graph.speed}')

                self.widget.plot(x_list, y_list, pen=pen, name=name)

        except Exception as e:
            self.logger.error(e)

    def move_graph(self, obj):
        try:
            for graph in obj:
                x_list = graph.move_list
                y_list = graph.force_list
                pen = pg.mkPen(color=self.color_pen[obj.index(graph)], width=3)
                name = (f'{graph.time_test} - '
                        f'{graph.amort.name} - '
                        f'{graph.serial_number} - '
                        f'{graph.speed}')

                self.widget.plot(x_list, y_list, pen=pen, name=name)

        except Exception as e:
            self.logger.error(e)

    def speed_graph(self, obj):
        try:
            for arch_obj in obj:
                speed_list = [0]
                comp_list = [0]
                recoil_list = [0]
                for graph in arch_obj:
                    speed_list.append(float(graph.speed))
                    push_force = self.calc_graph_values.select_push_force(graph)

                    recoil, comp = self.calc_data.middle_min_and_max_force(graph.force_list)

                    recoil_list.append(round(recoil + push_force, 2))
                    comp_list.append(round(comp * (-1) + push_force, 2))

                recoil_x, recoil_interp = self.calc_graph_values.interpoly_line_coord(speed_list, recoil_list)
                comp_x, comp_interp = self.calc_graph_values.interpoly_line_coord(speed_list, comp_list)

                x_list = [*recoil_x[::-1], *comp_x]
                y_list = [*recoil_interp[::-1], *comp_interp]

                pen = pg.mkPen(color=self.color_pen[obj.index(arch_obj)], width=3)
                name = (f'{arch_obj[0].time_test} - '
                        f'{arch_obj[0].amort.name} - '
                        f'{arch_obj[0].serial_number} - '
                        f'{arch_obj[0].speed}~{arch_obj[-1].speed}')

                self.widget.plot(x_list, y_list, pen=pen, name=name)

            self.cascade_graph.limit_line_graph(obj[0][0])

        except Exception as e:
            self.logger.error(e)