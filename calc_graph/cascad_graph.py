import pyqtgraph as pg

from logger import my_logger
from calc_graph.abstract_graph import AbstractGraph
from calc_graph.calc_graph_values import CalcGraphValue


class CascadeGraph:
    def __init__(self, widget):
        self.logger = my_logger.get_logger(__name__)
        self.widget = widget
        self.graph = AbstractGraph(widget)

    def gui_graph(self):
        try:
            kwargs = {'title': 'График зависимости усилия от скорости',
                      'left': ['left', 'Усилие', 'кгс'],
                      'bottom': ['bottom', 'Скорость', 'м/с']
                      }
            
            self.graph.gui_graph(**kwargs)
            
        except Exception as e:
            self.logger.error(e)
            
    def gui_axis(self):
        self.graph.gui_axis('left')
        self.graph.gui_axis('bottom')

    def limit_line_graph(self, obj):
        try:
            lim_speed_1 = []
            lim_speed_2 = []
            lim_recoil_1 = []
            lim_recoil_2 = []
            lim_comp_1 = []
            lim_comp_2 = []

            lim_speed_1.append(float(obj.speed_one))
            lim_speed_1.append(float(obj.speed_one))
            lim_speed_2.append(float(obj.speed_two))
            lim_speed_2.append(float(obj.speed_two))

            lim_recoil_1.append(float(obj.min_recoil))
            lim_recoil_1.append(float(obj.max_recoil))
            lim_recoil_2.append(float(obj.max_recoil_2))
            lim_recoil_2.append(float(obj.min_recoil_2))

            lim_comp_1.append(float(obj.min_comp) * -1)
            lim_comp_1.append(float(obj.max_comp) * -1)
            lim_comp_2.append(float(obj.max_comp_2) * -1)
            lim_comp_2.append(float(obj.min_comp_2) * -1)

            pen = pg.mkPen(color='red', width=2)

            self.widget.plot(lim_speed_1, lim_recoil_1, pen=pen)
            self.widget.plot(lim_speed_2, lim_recoil_2, pen=pen)
            self.widget.plot(lim_speed_1, lim_comp_1, pen=pen)
            self.widget.plot(lim_speed_2, lim_comp_2, pen=pen)

        except Exception as e:
            self.logger.error(e)
            
    def calc_graph(self, data):
        try:
            push_force = CalcGraphValue().select_push_force(data)
            
            speed = data.speed_list[:]
            recoil = [round(x + push_force, 2) for x in data.recoil_list]
            comp = [round(x + push_force, 2) for x in data.comp_list]
            
            speed.insert(0, 0)
            recoil.insert(0, 0)
            comp.insert(0, 0)
            
            r_x, r_y = CalcGraphValue().interpoly_line_coord(speed, recoil)
            c_x, c_y = CalcGraphValue().interpoly_line_coord(speed, comp)
            
            return r_x, r_y, c_x, c_y
        
        except Exception as e:
            self.logger.error(e)

    def fill_graph(self, r_x, r_y, c_x, c_y, pen_r=None, pen_c=None, name_r='Отбой', name_c='Сжатие'):
        try:
            if pen_r == None:
                pen_r = pg.mkPen(color='black', width=3)
            if pen_c == None:
                pen_c = pg.mkPen(color='blue', width=3)

            self.widget.plot(r_x, r_y, pen=pen_r, name=name_r)
            self.widget.plot(c_x, c_y, pen=pen_c, name=name_c)

        except Exception as e:
            self.logger.error(e)
            
    def data_graph(self, data):
        try:
            push_force = CalcGraphValue().select_push_force(data)
            
            recoil = [round(x + push_force, 2) for x in data.recoil_list]
            comp = [round(x + push_force, 2) for x in data.comp_list]
            
            return {'push_force': push_force,
                    'speed': data.speed_list,
                    'recoil': recoil,
                    'comp': comp}
            
        except Exception as e:
            self.logger.error(e)
