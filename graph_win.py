from PyQt5.QtWidgets import QMainWindow
from graph_ui import Ui_MainWindow
import pyqtgraph as pg


class GraphUi(QMainWindow):
    def __init__(self, model):
        super(GraphUi, self).__init__()
        try:
            self.model = model
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            self.pen_test = None
            self.data_line_test = None

            self.init_graph()

        except Exception as e:
            print(str(e))

    def init_graph(self):
        self.ui.graph_widget.showGrid(True, True)
        self.ui.graph_widget.setBackground('w')

        self.pen_test = pg.mkPen(color='black', width=3)
        self.data_line_test = self.ui.graph_widget.plot([], [], pen=self.pen_test)

    def clear_graph(self):
        self.x = []
        self.y = []
        self.data_line_test.setData(self.x, self.y)
