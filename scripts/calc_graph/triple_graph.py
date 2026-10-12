# -*- coding: utf-8 -*-
import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Qt

from scripts.logger import my_logger
from scripts.data_calculation import CalcData
from scripts.calc_graph.abstract_graph import AbstractGraph
from scripts.calc_graph.calc_graph_values import CalcGraphValue


class TripleGraph(AbstractGraph):
    """
    Диаграмма хода, скорости и силы сопротивления по углу поворота кривошипа.
    Все три кривые - измеренные данные цикла (запись буфера раз в 1 мс, кривошип
    вращается равномерно, поэтому точки цикла равномерно ложатся на 0..360°).
    Две оси: левая - смещение (мм) и скорость (мм/с), правая - усилие (кгс).
    Обе шкалы симметричны относительно нуля, нули на одной горизонтали.
    0° - середина хода на подъёме (сохранённый цикл начинается в НМТ, сдвиг на 90°).
    """
    AXES_CONFIG = {
        'title': 'Диаграмма хода, скорости, силы сопротивления',
        'left': ('left', 'Смещение (мм), скорость (мм/с)', ''),
        'bottom': ('bottom', 'ω * t', '°'),
        'right': ('right', 'Усилие', 'кгс')
    }
    MARGIN = 1.1    # запас по высоте над максимумом

    def __init__(self, widget):
        self.logger = my_logger.get_logger(__name__)
        self.widget = widget

        self.gui_graph(**self.AXES_CONFIG)
        self._initialize_axes()
        self._setup_force_scale()

    def _initialize_axes(self):
        """Initialize graph axes from configuration."""
        for axis_key in ('left', 'bottom', 'right'):
            self.gui_axis(axis_key)
            # без автоприставок СИ: иначе 1000 кгс -> «k кгс»
            self.widget.getAxis(axis_key).enableAutoSIPrefix(False)

    def _setup_force_scale(self):
        """
        Отдельная шкала усилия справа (свой ViewBox, общий X).
        Окно архива создаёт TripleGraph заново на каждый выбор, а виджет тот же -
        шкала создаётся один раз и хранится на виджете, иначе накапливалась бы
        """
        plot = self.widget.getPlotItem()
        vb_force = getattr(self.widget, '_triple_force_vb', None)
        if vb_force is None:
            vb_force = pg.ViewBox()
            plot.showAxis('right')
            plot.scene().addItem(vb_force)
            plot.getAxis('right').linkToView(vb_force)
            vb_force.setXLink(plot)

            def update_view():
                vb_force.setGeometry(plot.vb.sceneBoundingRect())
                vb_force.linkedViewChanged(plot.vb, vb_force.XAxis)

            widget = self.widget

            axis_left = plot.getAxis('left')
            axis_right = plot.getAxis('right')
            # сетку рисует только левая ось; деления правой ставятся на её же линии
            axis_right.setGrid(False)

            def follow_y(_vb, y_range):
                # шкала усилия повторяет левую пропорционально (_triple_ratio = кгс на единицу
                # левой оси): масштаб и сдвиг по вертикали - сразу у всех кривых, нули совпадают
                ratio = getattr(widget, '_triple_ratio', None)
                if not ratio:
                    axis_right.setTicks(None)
                    return
                vb_force.setYRange(y_range[0] * ratio, y_range[1] * ratio, padding=0)
                # деления справа - на тех же высотах, что слева (ratio «круглый», значения тоже)
                levels = axis_left.tickValues(y_range[0], y_range[1], max(plot.vb.height(), 1))
                ticks = []
                for _spacing, values in levels[:2]:
                    ticks.append([(v * ratio, f'{v * ratio:g}') for v in values])
                axis_right.setTicks(ticks)

            plot.vb.sigResized.connect(update_view)
            plot.vb.sigResized.connect(lambda *_: follow_y(None, plot.vb.viewRange()[1]))
            plot.vb.sigYRangeChanged.connect(follow_y)
            update_view()
            # мышь управляет только левой шкалой (правая повторяет её), иначе колёсико над
            # графиком попадало бы в шкалу усилия и сводило бы шкалы
            vb_force.setMouseEnabled(x=False, y=False)
            self.widget._triple_force_vb = vb_force

        self.vb_force = vb_force
        self.vb_force.clear()
        if plot.legend is not None:
            plot.legend.clear()

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
        """Измеренная скорость штока, мм/с (как в «Усилие/Скорость №2»: приращение за 10 мс, сглаживание)"""
        try:
            move = np.asarray(data.move_list, dtype=float)
            speed = CalcGraphValue().rounding_coord(CalcGraphValue().speed_coord(move, 'two'), 50)
            return self._rotate(np.asarray(speed) * 1000.0)

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

    @staticmethod
    def _nice_ceil(value):
        exp = np.floor(np.log10(value))
        base = 10 ** exp
        for m in (1, 2, 2.5, 5, 10):
            if value <= m * base * (1 + 1e-9):
                return m * base
        return 10 * base

    @staticmethod
    def _max_abs(items):
        values = [np.nanmax(np.abs(y)) for it in items
                  for y in (it.getData()[1],) if y is not None and len(y)]
        return max(values) if values else 0.0

    def _align_scales(self):
        """
        Обе шкалы симметричны относительно нуля - нули левой (мм, мм/с) и правой (кгс)
        осей на одной горизонтали: по вертикали видно, какое усилие при нулевой
        скорости (перекладка) и при максимальной (середина хода). Диапазон - по
        максимуму всех кривых оси (при сравнении испытаний - в правильном соотношении).
        Правая шкала связана с левой коэффициентом (follow_y): масштаб мышью по
        вертикали меняет обе сразу, сведение нулей сохраняется
        """
        plot = self.widget.getPlotItem()
        left = self._max_abs([it for it in plot.listDataItems() if isinstance(it, pg.PlotDataItem)])
        force = self._max_abs([it for it in self.vb_force.addedItems if isinstance(it, pg.PlotDataItem)])
        plot.vb.setMouseEnabled(y=True)
        plot.vb.disableAutoRange(axis=pg.ViewBox.YAxis)
        self.vb_force.disableAutoRange(axis=pg.ViewBox.YAxis)
        if left > 0 and force > 0:
            # округление вверх до 1, 2, 2.5, 5 × 10^n: деления справа на тех же линиях
            # сетки, что и слева, получают круглые значения (не 117.8 кгс)
            self.widget._triple_ratio = self._nice_ceil(force / left)
        else:
            self.widget._triple_ratio = None
            if force > 0:
                self.vb_force.setYRange(-force * self.MARGIN, force * self.MARGIN, padding=0)
        if left > 0:
            # через сигнал диапазона левой шкалы правая выставится в ±force * MARGIN
            plot.vb.setYRange(-left * self.MARGIN, left * self.MARGIN, padding=0)

    def fill_piston_graph(self, data, pen=None, name='Смещение, мм'):
        try:
            if pen is None:
                pen = pg.mkPen(color='black', width=3, style=Qt.DashDotLine)
            x_coord, y_coord = self.calc_move_graph(data)
            self.widget.plot(x_coord, y_coord, pen=pen, name=name)
            self._align_scales()

        except Exception as e:
            self.logger.error(e)

    def fill_force_graph(self, x_coord, y_coord, pen=None, name='Усилие, кгс'):
        try:
            if pen is None:
                pen = pg.mkPen(color='blue', width=3)
            item = pg.PlotDataItem(x_coord, y_coord, pen=pen, name=name)
            self.vb_force.addItem(item)
            legend = self.widget.getPlotItem().legend
            if legend is not None:
                legend.addItem(item, name)
            self._align_scales()

        except Exception as e:
            self.logger.error(e)

    def fill_speed_graph(self, x_coord, y_coord, pen=None, name='Скорость, мм/с'):
        try:
            if pen is None:
                pen = pg.mkPen(color='red', width=3)
            self.widget.plot(x_coord, y_coord, pen=pen, name=name)
            self._align_scales()

        except Exception as e:
            self.logger.error(e)
