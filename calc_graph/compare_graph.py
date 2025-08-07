import pyqtgraph as pg
from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtCore import Qt

from logger import my_logger
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
        
        self.break_data_by_type_graph()
            
    def break_data_by_type_graph(self):
        try:
            if self.type_graph == 'move':
                self._compare_move_graph()
            elif self.type_graph == 'boost_1':
                self._compare_boost_one_graph()
            elif self.type_graph == 'boost_2':
                self._compare_boost_two_graph()
            elif self.type_graph == 'triple':
                self._compare_triple_data()
            elif self.type_graph == 'speed':
                self._compare_speed_data()
            elif self.type_graph == 'temper':
                self._compare_temper_data()
            
        except Exception as e:
            self.logger.error(e)
            
    def select_line_style(self, ind):
        try:
            if ind < 10:
                return Qt.SolidLine
            elif 9 < ind < 20:
                return Qt.DashLine
            else:
                return Qt.DashDotDotLine
            
        except Exception as e:
            self.logger.error(e)
            
    def select_color_line(self, ind):
        try:
            color_pen = ['black',
                         'blue',
                         'green',
                         'orange',
                         'purple',
                         'brown',
                         'olive',
                         'cyan',
                         'pink',
                         'red']
            
            if ind < 10:
                ind = ind
            elif 10 <= ind < 20:
                ind = ind - 10
            else:
                ind = ind - 20
                
            return color_pen[ind]
        
        except Exception as e:
            self.logger(e)
            
    def _compare_move_graph(self):
        try:
            self.ui.stackedWidget.setCurrentIndex(0)
            graph = MoveGraph(self.ui.duble_graphwidget)
            graph.gui_graph()
            graph.gui_axis()
            for ind, obj in enumerate(self.compare_data):
                arch_obj = obj[2]
                if ind == 0:
                    self._fill_compare_move_data(graph.data_graph(arch_obj))
                    
                x_coord, y_coord = arch_obj.move_list, arch_obj.force_list
                
                name = (f'{arch_obj.time_test} - '
                        f'{arch_obj.amort.name} - '
                        f'{arch_obj.serial_number} - '
                        f'{arch_obj.speed}')
                
                pen = pg.mkPen(color=self.select_color_line(ind),
                               width=3,
                               style=self.select_line_style(ind))
                
                graph.fill_graph(x_coord, y_coord, pen, name)
                
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

    def _compare_boost_one_graph(self):
        try:
            self.ui.stackedWidget.setCurrentIndex(0)
            graph = BoostGraphOne(self.ui.duble_graphwidget)
            graph.gui_graph()
            graph.gui_axis()
            for ind, obj in enumerate(self.compare_data):
                arch_obj = obj[2]
                if ind == 0:
                    self._fill_compare_boost_one_data(graph.data_graph(arch_obj), arch_obj.speed)
                
                x_coord, y_coord = graph.calc_graph(arch_obj)
                
                name = (f'{arch_obj.time_test} - '
                        f'{arch_obj.amort.name} - '
                        f'{arch_obj.serial_number} - '
                        f'{arch_obj.speed}')
            
                pen = pg.mkPen(color=self.select_color_line(ind),
                               width=3,
                               style=self.select_line_style(ind))
                
                graph.fill_graph(x_coord, y_coord, pen, name)
                
            
        except Exception as e:
            self.logger.error(e)
            
    def _fill_compare_boost_one_data(self, data, speed):
        try:
            self.ui.speed_base_le.setText(f'{speed}')
            self.ui.recoil_base_le.setText(f'{data.get("recoil", 0)}')
            self.ui.comp_base_le.setText(f'{data.get("comp", 0)}')
            self.ui.push_force_base_le.setText(f'{data.get("push_force", 0)}')
            
        except Exception as e:
            self.logger.error(e)

    def _compare_boost_two_graph(self):
        try:
            self.ui.stackedWidget.setCurrentIndex(0)
            graph = BoostGraphTwo(self.ui.duble_graphwidget)
            graph.gui_graph()
            graph.gui_axis()
            for ind, obj in enumerate(self.compare_data):
                arch_obj = obj[2]
                if ind == 0:
                    self._fill_compare_boost_one_data(graph.data_graph(arch_obj), arch_obj.speed)
                
                x_coord, y_coord = graph.calc_graph(arch_obj)
                
                name = (f'{arch_obj.time_test} - '
                        f'{arch_obj.amort.name} - '
                        f'{arch_obj.serial_number} - '
                        f'{arch_obj.speed}')
            
                pen = pg.mkPen(color=self.select_color_line(ind),
                               width=3,
                               style=self.select_line_style(ind))
                
                graph.fill_graph(x_coord, y_coord, pen, name)
                
            
        except Exception as e:
            self.logger.error(e)
            
    def _fill_compare_boost_one_data(self, data, speed):
        try:
            self.ui.speed_base_le.setText(f'{speed}')
            self.ui.recoil_base_le.setText(f'{data.get("recoil", 0)}')
            self.ui.comp_base_le.setText(f'{data.get("comp", 0)}')
            self.ui.push_force_base_le.setText(f'{data.get("push_force", 0)}')
            
        except Exception as e:
            self.logger.error(e)
            
    def _compare_triple_data(self):
        try:
            self.ui.stackedWidget.setCurrentIndex(1)
            graph = TripleGraph(self.ui.triple_graphwidget)
            graph.gui_graph()
            graph.gui_axis()
            for ind, obj in enumerate(self.compare_data):
                arch_obj = obj[2]
                if ind == 0:
                    self._fill_compare_triple_data(graph.data_graph(arch_obj))
                    
                    graph.fill_piston_graph(int(arch_obj.amort.hod))
                    
                pen = pg.mkPen(color=self.select_color_line(ind),
                               width=3,
                               style=self.select_line_style(ind))
                
                name_first = (f'{arch_obj.time_test} - '
                              f'{arch_obj.amort.name} - '
                              f'{arch_obj.serial_number} - '
                              f'{arch_obj.speed} - ')
                
                name_force = name_first + f'Усилие'
                    
                x_f, y_f = graph.calc_force_graph(arch_obj)
                graph.fill_force_graph(x_f, y_f, pen, name_force)
                
                name_speed = name_first + 'Скорость'
                
                x_s, y_s = graph.calc_speed_graph(arch_obj)
                graph.fill_speed_graph(x_s, y_s, pen, name_speed)
                
        except Exception as e:
            self.logger.error(e)
            
    def _fill_compare_triple_data(self, data):
        try:
            self.ui.speed_base_le.setText(f'{data.get("speed", 0)}')
            self.ui.recoil_base_le.setText(f'{data.get("recoil", 0)}')
            self.ui.comp_base_le.setText(f'{data.get("comp", 0)}')
            self.ui.push_force_base_le.setText(f'{data.get("push_force")}')
            
        except Exception as e:
            self.logger.error(e)
    
    def _compare_speed_data(self):
        try:
            self.ui.stackedWidget.setCurrentIndex(0)
            graph = CascadeGraph(self.ui.duble_graphwidget)
            graph.gui_graph()
            graph.gui_axis()
            for ind, obj in enumerate(self.compare_data):
                arch_obj = obj[2]
                if ind == 0:
                    self._fill_compare_speed_data(graph.data_graph(arch_obj))
                    
                name = (f'{arch_obj.time_test} - '
                        f'{arch_obj.amort.name} - '
                        f'{arch_obj.serial_number} - '
                        f'{arch_obj.speed_list[0]}~{arch_obj.speed_list[-1]}')
                
                pen = pg.mkPen(color=self.select_color_line(ind),
                               width=3,
                               style=self.select_line_style(ind))
                
                r_x, r_y, c_x, c_y = graph.calc_graph(arch_obj)
                
                graph.fill_graph(r_x, r_y, c_x, c_y, pen, pen, name, None)
                
                graph.limit_line_graph(arch_obj)
            
        except Exception as e:
            self.logger.error(e)
            
    def _fill_compare_speed_data(self, data):
        try:
            self.ui.push_force_casc_le.setText(f'{data.get("push_force", 0)}')
                
            for ind, val in enumerate(data.get('speed')):
                self.ui.casc_tableWt.setItem(0, ind, QTableWidgetItem(f'{val}'))
                self.ui.casc_tableWt.setItem(1, ind, QTableWidgetItem(f'{data.get("recoil")[ind]}'))
                self.ui.casc_tableWt.setItem(2, ind, QTableWidgetItem(f'{data.get("comp")[ind]}'))
            
        except Exception as e:
            self.logger.error(e)
    
    def _compare_temper_data(self):
        try:
            self.ui.stackedWidget.setCurrentIndex(0)
            graph = TemperGraph(self.ui.duble_graphwidget)
            graph.gui_graph()
            graph.gui_axis()
            for ind, obj in enumerate(self.compare_data):
                arch_obj = obj[2]
                if ind == 0:
                    self._fill_compare_temper_data(graph.data_graph(arch_obj))
            
                name = (f'{arch_obj.time_test} - '
                        f'{arch_obj.amort.name} - '
                        f'{arch_obj.serial_number} - '
                        f'{arch_obj.temper_list[0]}~{arch_obj.temper_list[-1]} °С')
                
                pen = pg.mkPen(color=self.select_color_line(ind),
                               width=3,
                               style=self.select_line_style(ind))
                
                x, y1, y2 = graph.calc_graph(arch_obj)
                graph.fill_graph(x, y1, y2, pen, pen, name, name)
            
        except Exception as e:
            self.logger.error(e)
            
    def _fill_compare_temper_data(self, data):
        try:
            self.ui.speed_temp_le.setText(f'{data.get("speed", 0)}')
            self.ui.begin_temp_le.setText(f'{data.get("start_temper", 0)}')
            self.ui.max_temp_le.setText(f'{data.get("end_temper", 0)}')
            self.ui.recoil_begin_temp_le.setText(f'{data.get("start_recoil", 0)}')
            self.ui.recoil_end_temp_le.setText(f'{data.get("end_recoil", 0)}')
            self.ui.comp_begin_temp_le.setText(f'{data.get("start_comp", 0)}')
            self.ui.comp_end_temp_le.setText(f'{data.get("end_comp", 0)}')
            self.ui.push_force_temp_le.setText(f'{data.get("push_force")}')
            
        except Exception as e:
            self.logger.error(e)
