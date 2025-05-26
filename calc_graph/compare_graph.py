import numpy as np
import pyqtgraph as pg

from logger import my_logger
from calc_data.data_calculation import CalcData
from calc_graph.calc_graph_values import CalcGraphValue
from calc_graph.move_graph import MoveGraph
from calc_graph.boost_graph_one import BoostGraphOne
from calc_graph.boost_graph_two import BoostGraphTwo
from calc_graph.triple_graph import TripleGraph
from calc_graph.cascad_graph import CascadeGraph
from calc_graph.temper_graph import TemperGraph


class CompareGraph:
    def __init__(self, ui, compare_data):
        self.logger = my_logger.get_logger(__name__)
        self.ui = ui
        self.compare_data = compare_data
        self.type_graph = compare_data[0][1]
        self.type_test = compare_data[0][0]

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
        
        self.break_data_by_type_graph()
            
    def break_data_by_type_graph(self):
        try:
            if self.type_graph == 'move':
                self._compare_move_graph()
            elif self.type_graph == 'boost_1':
                pass
            elif self.type_graph == 'boost_2':
                pass
            elif self.type_graph == 'tripe':
                pass
            elif self.type_graph == 'speed':
                pass
            elif self.type_graph == 'temper':
                pass
            
        except Exception as e:
            self.logger.error(e)
            
    def _compare_move_graph(self):
        try:
            self.ui.stackedWidget.setCurrentIndex(0)
            graph = MoveGraph(self.ui.duble_graphwidget)
            graph.gui_graph()
            for ind, obj in enumerate(self.compare_data):
                arch_obj = obj[2]
                if ind == 0:
                    self._fill_compare_move_data(graph.data_graph(arch_obj))
                self._fill_compare_move_graph(self.color_pen[ind], arch_obj)
                
        except Exception as e:
            self.logger.error(e)
            
    def _fill_compare_move_data(self, data):
        try:
            self.ui.recoil_base_le.setText(f'{data.get("recoil", 0)}')
            self.ui.comp_base_le.setText(f'{data.get("comp", 0)}')
            self.ui.speed_base_le.setText(f'{data.get("speed", 0)}')
            self.ui.push_force_base_le.setText(f'{data.get("push_force", 0)}')
            self.ui.power_base_le.setText(f'{data.get("power", 0)}')
            self.ui.freq_base_le.setText(f'{data.get("freq", 0)}')
            
        except Exception as e:
            self.logger.error(e)
            
    def _fill_compare_move_graph(self, color, data):
        try:
            name = (f'{data.time_test} - '
                    f'{data.amort.name} - '
                    f'{data.serial_number} - '
                    f'{data.speed}')
            
            pen = pg.mkPen(color=color, width=3)
            self.ui.duble_graphwidget.plot(np.array(data.move_list),
                                           np.array(data.force_list),
                                           pen=pen,
                                           name=name)
            
        except Exception as e:
            self.logger.error(e)

    def conv_graph(self, obj):
        try:
            for graph in obj:
                pen = pg.mkPen(color=self.color_pen[obj.index(graph)], width=3)
                name = (f'{graph.time_test} - '
                        f'{graph.amort.name} - '
                        f'{graph.serial_number} - '
                        f'{graph.speed}')

                self.widget.plot(np.array(graph.move_list), np.array(graph.force_list), pen=pen, name=name)

        except Exception as e:
            self.logger.error(e)

    def move_graph(self, obj):
        try:
            for graph in obj:
                pen = pg.mkPen(color=self.color_pen[obj.index(graph)], width=3)
                name = (f'{graph.time_test} - '
                        f'{graph.amort.name} - '
                        f'{graph.serial_number} - '
                        f'{graph.speed}')

                self.widget.plot(np.array(graph.move_list), np.array(graph.force_list), pen=pen, name=name)

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
                    push_force = CalcGraphValue().select_push_force(graph)

                    recoil, comp = CalcData().middle_min_and_max_force(np.array(graph.force_list))

                    recoil_list.append(round(recoil + push_force, 2))
                    comp_list.append(round(comp * (-1) + push_force, 2))

                recoil_x, recoil_interp = CalcGraphValue().interpoly_line_coord(speed_list, recoil_list)
                comp_x, comp_interp = CalcGraphValue().interpoly_line_coord(speed_list, comp_list)

                x_list = [*recoil_x[::-1], *comp_x]
                y_list = [*recoil_interp[::-1], *comp_interp]

                pen = pg.mkPen(color=self.color_pen[obj.index(arch_obj)], width=3)
                name = (f'{arch_obj[0].time_test} - '
                        f'{arch_obj[0].amort.name} - '
                        f'{arch_obj[0].serial_number} - '
                        f'{arch_obj[0].speed}~{arch_obj[-1].speed}')

                self.widget.plot(x_list, y_list, pen=pen, name=name)

            self.limit_line_graph(obj[0][0])

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
