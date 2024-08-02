# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QMainWindow
from ui_py.graph_ui import Ui_MainWindow
import pyqtgraph as pg


class GraphUi(QMainWindow, Ui_MainWindow):
    def __init__(self, model):
        super(GraphUi, self).__init__()
        try:
            self.model = model
            self.setupUi(self)
            self.pen_test = None
            self.data_line_test = None
            self.x = []
            self.y = []

            self._init_graph()

        except Exception as e:
            print(str(e))

    def _init_graph(self):
        self.graph_widget.showGrid(True, True)
        self.graph_widget.setBackground('w')

        self.pen_test = pg.mkPen(color='black', width=3)
        self.data_line_test = self.graph_widget.plot([], [], pen=self.pen_test)

    def clear_graph(self):
        self.x = []
        self.y = []
        self.data_line_test.setData(self.x, self.y)
