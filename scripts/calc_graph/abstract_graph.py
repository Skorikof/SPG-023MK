import pyqtgraph as pg
from PySide6.QtGui import QFont


class AbstractGraph:
    def __init__(self, widget):
        self.widget = widget
        
    def gui_graph(self, **kwargs):
        self.widget.plot(clear=True)
        for k, v in kwargs.items():
            if k == 'title':
                self._graph_title(v)
                
            elif k == 'left' or k == 'right' or k == 'bottom':
                self._line_label(v)
                
            else:
                pass
                
        self.widget.showGrid(True, True)
        self.widget.setBackground('w')
        self.widget.addLegend()
        
    def _graph_title(self, title):
        if not title:
            title = ''
            
        self.widget.setTitle(title, color='k', size='16pt')
        
    def _line_label(self, data: tuple) -> None:
        if not data:
            data = ('left', '', '')
            
        line = data[0]
        name = data[1]
        unit = data[2]
        kwargs = {'font-size':'14pt'}
        self.widget.setLabel(line, name, units=unit, color='k', **kwargs)
    
    def gui_axis(self, line: str) -> None:
        font=QFont()
        font.setPointSize(12)
        pen = pg.mkPen(color='k', width=1.5)
        self.widget.getAxis(line).setPen(pen)
        self.widget.getAxis(line).setTickFont(font)
        self.widget.getAxis(line).setTickPen(pen)
