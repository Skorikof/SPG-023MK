# -*- coding: utf-8 -*-
import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from scripts.logger import my_logger
from scripts.data_calculation import CalcData
from scripts.calc_graph.abstract_graph import AbstractGraph
from scripts.calc_graph.calc_graph_values import CalcGraphValue


class TripleGraph(AbstractGraph):
    """
    Диаграмма хода, скорости и силы сопротивления по углу поворота кривошипа.
    Все три кривые - измеренные данные цикла (запись буфера раз в 1 мс, кривошип
    вращается равномерно, поэтому точки цикла равномерно ложатся на 0..360°).
    У каждой величины своя шкала: смещение - левая ось (мм), усилие - правая (кгс),
    скорость - вторая правая (м/с); иначе скорость в мм/с визуально забивала усилие.
    0° - середина хода на подъёме (сохранённый цикл начинается в НМТ, сдвиг на 90°).
    """
    AXES_CONFIG = {
        'title': 'Диаграмма хода, скорости, силы сопротивления',
        'left': ('left', 'Смещение', 'мм'),
        'bottom': ('bottom', 'ω * t', '°'),
        'right': ('right', 'Усилие', 'кгс')
    }

    def __init__(self, widget):
        self.logger = my_logger.get_logger(__name__)
        self.widget = widget

        self.gui_graph(**self.AXES_CONFIG)
        self._initialize_axes()
        self._setup_extra_scales()

    def _initialize_axes(self):
        """Initialize graph axes from configuration."""
        for axis_key in ('left', 'bottom', 'right'):
            self.gui_axis(axis_key)
            # без автоприставок СИ: иначе 1000 кгс -> «k кгс», 0.4 м/с -> «m м/с»
            self.widget.getAxis(axis_key).enableAutoSIPrefix(False)

    def _setup_extra_scales(self):
        """
        Отдельные шкалы для усилия и скорости (свои ViewBox, общий X).
        Окно архива создаёт TripleGraph заново на каждый выбор, а виджет тот же -
        шкалы создаются один раз и хранятся на виджете, иначе накапливались бы
        """
        plot = self.widget.getPlotItem()
        extra = getattr(self.widget, '_triple_scales', None)
        if extra is None:
            vb_force = pg.ViewBox()
            plot.showAxis('right')
            plot.scene().addItem(vb_force)
            plot.getAxis('right').linkToView(vb_force)
            vb_force.setXLink(plot)

            vb_speed = pg.ViewBox()
            axis_speed = pg.AxisItem('right')
            plot.layout.addItem(axis_speed, 2, 3)
            plot.scene().addItem(vb_speed)
            axis_speed.linkToView(vb_speed)
            vb_speed.setXLink(plot)

            def update_views():
                for vb in (vb_force, vb_speed):
                    vb.setGeometry(plot.vb.sceneBoundingRect())
                    vb.linkedViewChanged(plot.vb, vb.XAxis)

            plot.vb.sigResized.connect(update_views)
            update_views()
            extra = self.widget._triple_scales = (vb_force, vb_speed, axis_speed)

        self.vb_force, self.vb_speed, axis_speed = extra
        self.vb_force.clear()
        self.vb_speed.clear()
        if plot.legend is not None:
            plot.legend.clear()

        font = QFont()
        font.setPointSize(12)
        pen = pg.mkPen(color='k', width=1.5)
        axis_speed.setPen(pen)
        axis_speed.setTextPen(pen)
        axis_speed.setTickFont(font)
        axis_speed.enableAutoSIPrefix(False)
        axis_speed.setLabel('Скорость', units='м/с', color='k', **{'font-size': '14pt'})

    # --- расчёт ---------------------------------------------------------------------

    @staticmethod
    def _rotate(values):
        """Сдвиг цикла на 90°: 0° графика - середина хода на подъёме (цикл начинается в НМТ)"""
        values = np.asarray(values, dtype=float)
        x_coord = np.linspace(0, 360, num=len(values), endpoint=False)
        index_zero = len(values) // 4
        return x_coord, np.concatenate((values[index_zero:], values[:index_zero]))

    def calc_move_graph(self, data):
        """Измеренное смещение штока от середины хода, мм"""
        try:
            move = np.asarray(data.move_list, dtype=float)
            return self._rotate(move - (move.max() + move.min()) / 2)

        except Exception as e:
            self.logger.error(e)

    def calc_force_graph(self, data):
        try:
            return self._rotate(data.force_list)

        except Exception as e:
            self.logger.error(e)

    def calc_speed_graph(self, data):
        """Измеренная скорость штока, м/с (как в «Усилие/Скорость №2»: приращение за 10 мс, сглаживание)"""
        try:
            move = np.asarray(data.move_list, dtype=float)
            speed = CalcGraphValue().rounding_coord(CalcGraphValue().speed_coord(move, 'two'), 50)
            return self._rotate(speed)

        except Exception as e:
            self.logger.error(e)

    def data_graph(self, data):
        try:
            recoil, comp = CalcData().middle_min_and_max_force(data.force_list)

            return {'speed': data.speed,
                    'recoil': recoil,
                    'comp': comp,
                    'push_force': 0,
                    }

        except Exception as e:
            self.logger.error(e)

    # --- отрисовка ------------------------------------------------------------------

    def _add(self, viewbox, x_coord, y_coord, pen, name):
        item = pg.PlotDataItem(x_coord, y_coord, pen=pen, name=name)
        viewbox.addItem(item)
        legend = self.widget.getPlotItem().legend
        if legend is not None:
            legend.addItem(item, name)
        viewbox.enableAutoRange(axis=pg.ViewBox.YAxis)

    def fill_piston_graph(self, data, pen=None, name='Смещение'):
        try:
            if pen is None:
                pen = pg.mkPen(color='black', width=3, style=Qt.DashDotLine)
            x_coord, y_coord = self.calc_move_graph(data)
            self.widget.plot(x_coord, y_coord, pen=pen, name=name)

        except Exception as e:
            self.logger.error(e)

    def fill_force_graph(self, x_coord, y_coord, pen=None, name='Усилие'):
        try:
            if pen is None:
                pen = pg.mkPen(color='blue', width=3)
            self._add(self.vb_force, x_coord, y_coord, pen, name)

        except Exception as e:
            self.logger.error(e)

    def fill_speed_graph(self, x_coord, y_coord, pen=None, name='Скорость'):
        try:
            if pen is None:
                pen = pg.mkPen(color='red', width=3)
            self._add(self.vb_speed, x_coord, y_coord, pen, name)

        except Exception as e:
            self.logger.error(e)
