# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QMainWindow, QDialog, QMessageBox
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtGui import QPageLayout, QPixmap, QPainter, QIcon
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QAbstractPrintDialog
from PIL import ImageGrab
import pyqtgraph as pg
import numpy as np
from functools import reduce
import os

from ui_py.archive_ui import Ui_WindowArch
from archive import ReadArchive
from my_obj.data_calculation import CalcData


class WinSignals(QObject):
    closed = pyqtSignal()
    log_msg = pyqtSignal(str)
    log_err = pyqtSignal(str)


class ArchiveWin(QMainWindow, Ui_WindowArch):
    signals = WinSignals()

    def __init__(self):
        super(ArchiveWin, self).__init__()
        try:
            self.compare_data = []
            self.type_graph = 'move'
            self.ind_type_test = 0
            self.index_date = ''
            self.index_test = 0
            self.index_test_cascade = 0
            self.index_test_temper = 0
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
            self.archive = ReadArchive()
            self.setupUi(self)
            self.setWindowIcon(QIcon('icon/archive.png'))
            self.hide()
            self._create_statusbar_set()
            self._init_buttons()

        except Exception as e:
            self.signals.log_err.emit(f'ERROR in archive_win/__init__ - {e}')

    def closeEvent(self, event):
        self.signals.closed.emit()

    def _create_statusbar_set(self):
        self.statusbar = self.statusBar()
        self.statusbar.showMessage('Окно чтения архива испытаний')

    def _statusbar_set_ui(self, txt_bar):
        try:
            self.statusbar.showMessage(txt_bar)
            self.signals.log_err.emit(txt_bar)

        except Exception as e:
            self.signals.log_err.emit(f'ERROR in archive_win/_statusbar_set_ui - {e}')

    def _init_buttons(self):
        self.btn_exit.clicked.connect(self.close)
        self.btn_print.setVisible(False)
        self.btn_save.clicked.connect(self._archive_save_form)
        self.btn_compare.clicked.connect(self._add_compare_data)
        self.btn_clier.clicked.connect(self._clear_compare_data)
        self.btn_show.clicked.connect(self._show_compare_data)

        self.combo_dates.activated[str].connect(self._change_index_date)
        self.combo_test.activated[int].connect(self._change_index_test)
        self.combo_type.activated[int].connect(self._change_type_graph)

    def read_path_archive(self):
        try:
            self.compare_data = []
            self.type_graph = 'move'
            self.ind_type_test = 0
            self.index_date = ''
            self.index_test = 0
            self.index_test_cascade = 0
            self.index_test_temper = 0

            self.combo_dates.clear()
            self.combo_test.clear()
            self.archive.init_arch()

            if len(self.archive.files_arr) == 0:
                self._archive_ui_clear()

            else:
                self.combo_dates.addItems(self.archive.files_name_sort)
                self.combo_dates.setCurrentIndex(0)
                self.index_date = self.archive.files_name_sort[0]
                self._archive_selected()

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/read_path_archive - {e}')

    def _archive_ui_clear(self):
        try:
            self.graphwidget.clear()
            self.name_le.setText('')
            self.operator_le.setText('')
            self.speed_set_1_le.setText('')
            self.limit_recoil_1_le.setText('')
            self.limit_comp_1_le.setText('')
            self.speed_set_2_le.setText('')
            self.limit_recoil_2_le.setText('')
            self.limit_comp_2_le.setText('')
            self.recoil_le.setText('')
            self.comp_le.setText('')
            self.serial_le.setText('')
            self.date_le.setText('')
            self.speed_le.setText('')
            self.max_temp_le.setText('')
            self.hod_le.setText('')
            self.power_le.setText('')
            self.push_force_le.setText('')

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_archive_ui_clear - {e}')

    def _change_index_date(self, date):
        try:
            if self.index_date != date:
                self.index_date = date
                self._archive_selected()

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_change_index_date - {e}')

    def _change_index_test(self, index):
        try:
            if self.type_graph == 'speed':
                if self.index_test_cascade != index:
                    self.index_test_cascade = index
                    self._archive_test_select()
                    self._archive_graph()

            elif self.type_graph == 'temper':
                if self.index_test_temper != index:
                    self.index_test_temper = index
                    self._archive_test_select()
                    self._archive_graph()

            else:
                if self.index_test != index:
                    self.index_test = index
                    self._archive_test_select()
                    self._archive_graph()

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_change_index_test - {e}')

    def _change_type_graph(self, index):
        try:
            if self.ind_type_test != index:
                self.ind_type_test = index
                if index == 0:
                    self.type_graph = 'move'

                elif index == 1:
                    self.type_graph = 'speed'

                elif index == 2:
                    self.type_graph = 'triple'

                elif index == 3:
                    self.type_graph = 'boost_1'

                elif index == 4:
                    self.type_graph = 'boost_2'

                elif index == 5:
                    self.type_graph = 'temper'

                self._archive_selected()

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_select_type_graph - {e}')

    def _archive_selected(self):
        try:
            date = self.index_date
            self.combo_test.clear()
            temp_arr = []
            self.archive.select_file(date)

            if self.type_graph == 'speed':
                index = 1
                for key, value in self.archive.struct.cascade.items():
                    temp = (f'{index}) '
                            f'{value[0].time_test} - '
                            f'{value[0].amort.name} - '
                            f'{value[0].serial_number} - '
                            f'{value[0].speed}~{value[-1].speed}')
                    temp_arr.append(temp)
                    index += 1

            elif self.type_graph == 'temper':
                for i in range(len(self.archive.struct.temper)):
                    begin_temp = self.archive.struct.temper[i].temper_graph[0]
                    finish_temp = self.archive.struct.temper[i].temper_graph[-1]
                    temp = (f'{i + 1}) '
                            f'{self.archive.struct.temper[i].time_test} - '
                            f'{self.archive.struct.temper[i].amort.name} - '
                            f'{self.archive.struct.temper[i].serial_number} - '
                            f'{begin_temp}~{finish_temp} °С')
                    temp_arr.append(temp)

            else:
                for i in range(len(self.archive.struct.tests)):
                    temp = (f'{i + 1}) '
                            f'{self.archive.struct.tests[i].time_test} - '
                            f'{self.archive.struct.tests[i].amort.name} - '
                            f'{self.archive.struct.tests[i].serial_number} - '
                            f'{self.archive.struct.tests[i].speed}')
                    temp_arr.append(temp)

            if temp_arr:
                self.combo_test.addItems(temp_arr)
                self._archive_test_select()
                self._archive_graph()
            else:
                self._archive_ui_clear()

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_archive_selected - {e}')

    def _gui_power_freq_visible(self, state):
        try:
            self.power_le.setVisible(state)
            self.power_lbl.setVisible(state)
            self.power_lbl_2.setVisible(state)
            self.freq_le.setVisible(state)

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_gui_power_freq_visible - {e}')

    def _gui_move_graph(self):
        try:
            self.graphwidget.plot(clear=True)
            self.graphwidget.setLabel('left', 'Усилие', units='кгс', color='k')
            self.graphwidget.setLabel('bottom', 'Перемещение', units='мм', color='k')
            self.graphwidget.setLabel('right', 'Усилие', units='кгс', color='k')
            self.graphwidget.setTitle('График зависимости усилия от перемещения', color='k', size='14pt')
            self.graphwidget.showGrid(True, True)
            self.graphwidget.setBackground('w')

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_gui_move_graph - {e}')

    def _gui_speed_graph(self):
        try:
            self.graphwidget.plot(clear=True)
            self.graphwidget.setLabel('left', 'Усилие', units='кгс')
            self.graphwidget.setLabel('bottom', 'Скорость', units='м/с')
            self.graphwidget.setLabel('right', 'Усилие', units='кгс')
            self.graphwidget.setTitle('График зависимости усилия от скорости')
            self.graphwidget.showGrid(True, True)
            self.graphwidget.setBackground('w')

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_gui_speed_graph - {e}')

    def _gui_triple_graph(self):
        try:
            self.graphwidget.plot(clear=True)
            self.graphwidget.setLabel('left', 'Смещение или Скорость', units='мм или мм/с')
            self.graphwidget.setLabel('bottom', 'ω * t', units='°')
            self.graphwidget.setLabel('right', 'Усилие', units='кгс')
            self.graphwidget.setTitle('Диаграмма хода, скорости, силы сопротивления')
            self.graphwidget.showGrid(True, True)
            self.graphwidget.setBackground('w')

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_gui_triple_graph - {e}')

    def _gui_boost_graph(self):
        try:
            self.graphwidget.plot(clear=True)
            self.graphwidget.setLabel('left', 'Усилие', units='кгс')
            self.graphwidget.setLabel('bottom', 'Скорость', units='м/с')
            self.graphwidget.setLabel('right', 'Усилие', units='кгс')
            self.graphwidget.setTitle('График зависимости усилия от скорости')
            self.graphwidget.showGrid(True, True)
            self.graphwidget.setBackground('w')

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_gui_boost_graph - {e}')

    def _gui_temper_graph(self):
        try:
            self.graphwidget.plot(clear=True)
            self.graphwidget.setLabel('left', 'Усилие', units='кгс')
            self.graphwidget.setLabel('bottom', 'Температура', units='℃')
            self.graphwidget.setLabel('right', 'Усилие', units='кгс')
            self.graphwidget.setTitle('График зависимости усилия от температуры')
            self.graphwidget.showGrid(True, True)
            self.graphwidget.setBackground('w')

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_gui_temper_graph - {e}')

    def _archive_test_select(self):
        try:
            self.btn_compare.setVisible(True)
            if self.type_graph == 'speed':
                self._pars_lab_cascade_data()

            elif self.type_graph == 'triple':
                self._pars_triple_data()

            elif self.type_graph == 'temper':
                self._pars_temper_data()

            else:
                self._pars_lab_data()

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_archive_test_select - {e}')

    def _pars_lab_data(self):
        try:
            index = self.index_test

            if self.archive.struct.tests[index]:

                self._fill_archive_data_gui(self.archive.struct.tests[index])

                self.speed_le.setText(f'{self.archive.struct.tests[index].speed}')

                self._fill_flag_push_force(self.archive.struct.tests[index].flag_push_force)

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_pars_lab_data - {e}')

    def _pars_lab_cascade_data(self):
        try:
            index = self.index_test_cascade
            if not self.archive.struct.cascade.get(index + 1) is None:
                data = self.archive.struct.cascade.get(index + 1)
                self._fill_archive_data_gui(data[0])

                self._fill_flag_push_force(data[0].flag_push_force)

                speed_list = []
                for obj in data:
                    speed_list.append(obj.speed)

                self.speed_le.setText(f'{speed_list[0]}~{speed_list[-1]}')

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_pars_lab_cascade_data - {e}')

    def _pars_triple_data(self):
        try:
            index = self.index_test
            if self.archive.struct.tests[index]:

                self._fill_archive_data_gui(self.archive.struct.tests[index])

                self.speed_le.setText(f'{self.archive.struct.tests[index].speed}')

                self._fill_flag_push_force('2')

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_pars_triple_data - {e}')

    def _pars_temper_data(self):
        try:
            index = self.index_test_temper
            if self.archive.struct.temper[index]:
                self._fill_archive_data_gui(self.archive.struct.temper[index])

                self.speed_le.setText(f'{self.archive.struct.temper[index].speed}')
                self._fill_flag_push_force(self.archive.struct.temper[index].flag_push_force)

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_pars_temper_data - {e}')

    def _fill_archive_data_gui(self, obj):
        try:
            user_name = obj.operator_name
            user_rank = obj.operator_rank

            select_archive = self.archive.files_name_arr[self.archive.index_archive]
            time_test = obj.time_test

            min_comp = obj.amort.min_comp
            min_comp_2 = obj.amort.min_comp_2
            max_comp = obj.amort.max_comp
            max_comp_2 = obj.amort.max_comp_2
            min_recoil = obj.amort.min_recoil
            min_recoil_2 = obj.amort.min_recoil_2
            max_recoil = obj.amort.max_recoil
            max_recoil_2 = obj.amort.max_recoil_2

            self.name_le.setText(f'{obj.amort.name}')
            self.operator_le.setText(f'{user_rank} {user_name}')
            self.speed_set_1_le.setText(f'{obj.amort.speed_one}')
            self.speed_set_2_le.setText(f'{obj.amort.speed_two}')
            self.limit_recoil_1_le.setText(f'{min_recoil} - {max_recoil}')
            self.limit_recoil_2_le.setText(f'{min_recoil_2} - {max_recoil_2}')
            self.limit_comp_1_le.setText(f'{min_comp} - {max_comp}')
            self.limit_comp_2_le.setText(f'{min_comp_2} - {max_comp_2}')
            self.serial_le.setText(f'{obj.serial_number}')
            self.date_le.setText(f'{select_archive} - {time_test}')
            self.max_temp_le.setText(f'{obj.amort.max_temper}')
            self.hod_le.setText(f'{obj.amort.hod}')

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_fill_archive_data_gui - {e}')

    def _fill_flag_push_force(self, index: str):
        txt = ''
        self.push_force_le.setVisible(True)
        if index == '1':
            txt = f'Динамическая выталкивающая сила'

        elif index == '0':
            txt = f'Статическая выталкивающая сила'

        elif index == '2':
            txt = f'Выталкивающая сила не учитывается'
            self.push_force_le.setVisible(False)

        self.lbl_push_force.setText(txt)

    def _visible_compare_btn(self, state):
        try:
            self.btn_compare.setVisible(state)
            self.btn_clier.setVisible(state)
            self.btn_show.setVisible(state)

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_visible_compare_btn - {e}')

    def _archive_graph(self):
        try:
            self.graphwidget.plot(clear=True)
            if self.type_graph == 'move':
                self._gui_power_freq_visible(True)
                self._gui_move_graph()
                self._fill_lab_graph()
                self._visible_compare_btn(True)

            elif self.type_graph == 'speed':
                self._gui_power_freq_visible(False)
                self._gui_speed_graph()
                self._fill_lab_cascade_graph()
                self._visible_compare_btn(True)

            elif self.type_graph == 'triple':
                self._gui_power_freq_visible(False)
                self._gui_triple_graph()
                self._fill_triple_graph()
                self._visible_compare_btn(False)

            elif self.type_graph == 'boost_1' or self.type_graph == 'boost_2':
                self._gui_power_freq_visible(False)
                self._gui_boost_graph()
                self._fill_boost_graph()
                self._visible_compare_btn(False)

            elif self.type_graph == 'temper':
                self._gui_power_freq_visible(False)
                self._gui_temper_graph()
                self._fill_temper_graph()
                self._visible_compare_btn(False)

            self.graphwidget.addLegend()

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_archive_graph - {e}')

    def _fill_lab_graph(self):
        try:
            index = self.index_test
            obj = self.archive.struct.tests[index]

            move_list = obj.move_list

            force_list = obj.force_list
            push_force = self._select_push_force(obj)

            recoil, comp = CalcData().middle_min_and_max_force(force_list)
            max_recoil = round(recoil + push_force, 2)
            max_comp = round(comp - push_force, 2)

            power = CalcData().power_amort(move_list, force_list)

            speed = float(obj.speed)
            freq = CalcData().freq_piston_amort(speed, obj.amort)

            self.push_force_le.setText(f'{push_force}')
            self.power_le.setText(f'{power}')
            self.comp_le.setText(f'{max_comp}')
            self.recoil_le.setText(f'{max_recoil}')
            self.freq_le.setText(f'{freq}')

            pen = pg.mkPen(color='black', width=3)

            self.graphwidget.plot(move_list, force_list, pen=pen)

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_fill_lab_graph - {e}')

    def _fill_lab_cascade_graph(self):
        try:
            index = self.index_test_cascade
            speed_list = [0]
            comp_list = [0]
            recoil_list = [0]
            push_force = 0
            data = self.archive.struct.cascade.get(index + 1)

            for obj in data:
                speed_list.append(float(obj.speed))
                flag_push_force = obj.flag_push_force
                if flag_push_force == '1':
                    push_force = float(obj.dynamic_push_force)

                elif flag_push_force == '0':
                    push_force = float(obj.static_push_force)

                recoil, comp = CalcData().middle_min_and_max_force(obj.force_list)

                recoil_list.append(round(recoil + push_force, 2))
                comp_list.append(round(comp * (-1) + push_force, 2))

            pen_recoil = pg.mkPen(color='black', width=3)
            pen_comp = pg.mkPen(color='blue', width=3)

            self.graphwidget.plot(speed_list, recoil_list, pen=pen_recoil, name='Отбой')
            self.graphwidget.plot(speed_list, comp_list, pen=pen_comp, name='Сжатие')

            self.recoil_le.setText(f'{max(recoil_list)}')
            self.comp_le.setText(f'{abs(min(comp_list))}')

            self._fill_limit_lab_cascade_graph(data[0])

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_fill_lab_cascade_graph - {e}')

    def _fill_limit_lab_cascade_graph(self, obj):
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

            self.graphwidget.plot(lim_speed_1, lim_recoil_1, pen=pen)
            self.graphwidget.plot(lim_speed_2, lim_recoil_2, pen=pen)
            self.graphwidget.plot(lim_speed_1, lim_comp_1, pen=pen)
            self.graphwidget.plot(lim_speed_2, lim_comp_2, pen=pen)

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_fill_limit_lab_cascade_graph - {e}')

    def _fill_triple_graph(self):
        try:
            index = self.index_test
            hod = int(self.archive.struct.tests[index].amort.hod)
            move_list = self.archive.struct.tests[index].move_list
            force_list = self.archive.struct.tests[index].force_list
            self.push_force_le.setText(f'{0}')

            recoil, comp = CalcData().middle_min_and_max_force(force_list)

            self.comp_le.setText(f'{recoil}')
            self.recoil_le.setText(f'{comp}')

            self._fill_triple_hod_graph(hod)

            x_coord = self._convert_triple_move_in_degrees_coord(move_list)

            index_mid_hod = self._calc_index_middle_hod_triple(x_coord, hod)

            self._fill_triple_force_graph(x_coord, force_list, index_mid_hod)

            self._fill_triple_speed_graph(move_list, x_coord, index_mid_hod)

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_fill_triple_graph - {e}')

    def _fill_triple_hod_graph(self, hod):
        try:
            hod_x, hod_y = self._calc_hod_triple_coord(hod)
            pen = pg.mkPen(color='black', width=3)
            self.graphwidget.plot(hod_x, hod_y, pen=pen, name='Смещение')

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_fill_triple_hod_graph - {e}')

    def _calc_hod_triple_coord(self, hod):
        try:
            mid_hod = hod / 2
            fs = 360
            f = 1
            x = np.arange(360)
            y = np.sin(2 * np.pi * f * x / fs) * mid_hod

            return x, y

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_calc_hod_triple_list - {e}')

    def _calc_index_middle_hod_triple(self, x_coord: list, hod: int):
        try:
            mid_hod = hod / 2
            for point in x_coord:
                if mid_hod - 1 < point < mid_hod + 1:
                    return x_coord.index(point)

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_calc_start_point_triple - {e}')

    def _fill_triple_force_graph(self, x_coord: list, force: list, index):
        try:
            force_y = self._calc_triple_force_coord(force, index)
            pen = pg.mkPen(color='blue', width=3)
            self.graphwidget.plot(x_coord, force_y, pen=pen, name='Усилие')

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_fill_triple_force_graph - {e}')

    def _calc_triple_force_coord(self, force: list, index):
        try:
            return list(map(lambda x: round(x * (-1), 1), force[index:] + force[:index]))

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_calc_triple_force_coord - {e}')

    def _convert_triple_move_in_degrees_coord(self, move: list):
        try:
            way = []
            start_point = move[0]
            if start_point < 0:
                temp_list = list(map(lambda x: round(x + abs(start_point), 1), move))

            else:
                temp_list = list(map(lambda x: round(x - start_point, 1), move))

            max_point = max(temp_list)
            max_index = temp_list.index(max_point)

            for i in range(len(temp_list)):
                point = temp_list[i]
                if i > max_index:
                    point = round(max_point - abs(temp_list[i]) + max_point, 1)

                way.append(point)

            max_way = max(way)

            return list(map(lambda x: round(360 * x / max_way, 1), way))

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_calc_triple_x_coord - {e}')

    def _fill_triple_speed_graph(self, move: list, x_coord: list, index):
        try:
            speed_list = self._calc_triple_speed_coord(move, index)

            w = np.hanning(200)
            y_approxy = np.convolve(w / w.sum(), speed_list, mode='same')

            speed_y = list(map(lambda x: round(x * 100, 1), y_approxy))

            pen = pg.mkPen(color='red', width=3)
            self.graphwidget.plot(x_coord, speed_y,
                                  pen=pen,
                                  name='Скорость')

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_fill_triple_speed_graph - {e}')

    def _calc_triple_speed_coord(self, move: list, index):
        try:
            speed_list = []
            y_coord = []

            if index != 0:
                shift_list = move[index:] + move[:index]
                temp_list = shift_list[5:] + shift_list + shift_list[:5]

            else:
                temp_list = move[5:] + move + move[:5]

            for i in range(len(move)):
                for j in range(10):
                    speed_list.append(round(abs(abs(temp_list[i + j]) - abs(temp_list[i + j + 1])), 3))

                temp = reduce(lambda x, y: round(x + y, 3), speed_list)
                y_coord.append(temp)
                speed_list = []

            return y_coord

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_calc_triple_speed_coord - {e}')

    def _fill_boost_graph(self):
        try:
            index = self.index_test
            move_list = self.archive.struct.tests[index].move_list
            force_list = self.archive.struct.tests[index].force_list
            push_force = self._select_push_force(self.archive.struct.tests[index])
            self.push_force_le.setText(f'{push_force}')

            recoil, comp = CalcData().middle_min_and_max_force(force_list)

            self.comp_le.setText(f'{comp}')
            self.recoil_le.setText(f'{recoil}')

            if self.type_graph == 'boost_2':
                offset_p = abs(move_list[0] + int(self.archive.struct.tests[index].amort.hod) / 2)
                move_list = [round(x - offset_p) for x in move_list]

            speed_list = self._calc_triple_speed_coord(move_list, 0)

            w = np.hanning(200)
            y_approxy = np.convolve(w / w.sum(), speed_list, mode='same')

            x_coord = list(map(lambda x: round(x, 1), y_approxy))

            min_x = x_coord[0]
            max_x = x_coord[-1]
            if min_x < max_x:
                koef = min_x
            else:
                koef = max_x
            x_coord = [x - koef for x in x_coord]
            pen = pg.mkPen(color='blue', width=5)
            self.graphwidget.plot(x_coord, force_list, pen=pen, name='Скорость')

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_fill_boost_graph - {e}')

    def _fill_temper_graph(self):
        try:
            recoil_list = []
            comp_list = []
            index = self.index_test_temper
            temper_coord = self.archive.struct.temper[index].temper_graph

            for value in self.archive.struct.temper[index].temper_force_graph:
                value = value.strip('\'\"')
                value = value.replace(',', '.')
                value = value.split('|')
                recoil, comp = float(value[0]), float(value[1])
                recoil_list.append(recoil)
                comp_list.append(comp)

            push_force = self._select_push_force(self.archive.struct.temper[index])
            self.push_force_le.setText(f'{push_force}')

            self.comp_le.setText(f'{comp_list[-1]}')
            self.recoil_le.setText(f'{recoil_list[-1]}')

            pen_recoil = pg.mkPen(color=self.color_pen[0], width=3)
            pen_comp = pg.mkPen(color=self.color_pen[1], width=3)

            self.graphwidget.plot(temper_coord, recoil_list, pen=pen_recoil, name='Отбой')
            self.graphwidget.plot(temper_coord, comp_list, pen=pen_comp, name='Сжатие')

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_fill_temper_graph - {e}')

    def _select_push_force(self, obj):
        try:
            flag_push_force = obj.flag_push_force
            if flag_push_force == '1':
                return float(obj.dynamic_push_force)

            elif flag_push_force == '0':
                return float(obj.static_push_force)

            else:
                return 0

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_select_push_force - {e}')

    def _archive_save_form(self):
        try:
            rect = self.frameGeometry()
            pos = rect.getRect()
            x = pos[0] + 1
            y = pos[1] + 80
            height = 820
            width = 1024

            image = ImageGrab.grab((x, y, x + width, y + height))
            main_dir = ''
            date_dir = self.index_date
            name = '1'
            if self.type_graph == 'move':
                index = self.index_test
                name = self._name_screen_for_save(self.archive.struct.tests[index])
                main_dir = '1_Усилие_Перемещение'

            elif self.type_graph == 'speed':
                index = self.index_test_cascade
                name = self._name_screen_for_save_speed(self.archive.struct.cascade[index + 1])
                main_dir = '2_Усилие_Скорость'

            elif self.type_graph == 'triple':
                index = self.index_test
                name = self._name_screen_for_save(self.archive.struct.tests[index])
                main_dir = '3_Ход_Скорость_Сопротивление'

            elif self.type_graph == 'boost_1' or self.type_graph == 'boost_2':
                index = self.index_test
                name = self._name_screen_for_save(self.archive.struct.tests[index])
                main_dir = '4_Скорость_Сопротивление'

            elif self.type_graph == 'temper':
                index = self.index_test_temper
                name = self._name_screen_for_save_temper(self.archive.struct.temper[index])
                main_dir = '5_Температура_Сопротвление'

            self._create_dir_for_save(main_dir)
            file_dir = f"screens/{main_dir}/{date_dir}/{name}.bmp"
            image.save(file_dir, "BMP")

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_archive_save_form - {e}')

    def _create_dir_for_save(self, main_dir):
        try:
            date_dir = self.index_date
            directory = f'screens/{main_dir}/{date_dir}'
            os.makedirs(directory, exist_ok=True)

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_create_dir_for_save - {e}')

    def _name_screen_for_save(self, obj):
        try:
            time = obj.time_test.replace(':', '.')
            name = (f'{time}_'
                    f'{obj.amort.name}_'
                    f'{obj.serial_number}_'
                    f'{obj.speed}')

            return name

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_name_screen_for_save - {e}')

    def _name_screen_for_save_speed(self, obj):
        try:
            time = obj[0].time_test.replace(':', '.')
            name = (f'{time}_'
                    f'{obj[0].amort.name}_'
                    f'{obj[0].serial_number}_'
                    f'{obj[0].speed}~{obj[-1].speed}')

            return name

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_name_screen_for_save_speed - {e}')

    def _name_screen_for_save_temper(self, obj):
        try:
            time = obj.time_test.replace(':', '.')
            begin_temp = obj.temper_graph[0]
            finish_temp = obj.temper_graph[-1]
            name = (f'{time}_'
                    f'{obj.amort.name}_'
                    f'{obj.serial_number}_'
                    f'{begin_temp}~{finish_temp} °С')

            return name

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_name_screen_for_save_temper - {e}')

    def _clear_compare_data(self):
        try:
            if len(self.compare_data) > 0:
                self.compare_data.clear()
                self.read_path_archive()

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_clear_compare_data - {e}')

    def _add_compare_data(self):
        try:
            if self.type_graph == 'speed':
                index = self.index_test_cascade
                if not self.archive.struct.cascade[index + 1] in self.compare_data:
                    self.compare_data.append(self.archive.struct.cascade[index + 1])

            elif self.type_graph == 'temper':
                index = self.index_test_temper

            else:
                index = self.index_test
                if not self.archive.struct.tests[index] in self.compare_data:
                    self.compare_data.append(self.archive.struct.tests[index])
            self.btn_compare.setVisible(False)

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_add_compare_data - {e}')

    def _show_compare_data(self):
        try:
            if 0 < len(self.compare_data) < 13:
                self._show_graph(self.compare_data)

            elif len(self.compare_data) == 0:
                pass

            else:
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              f'<b style="color: #f00;">'
                                              f'Число выбранных графиков для сравнения превышает допустимое число'
                                              f'Выбрано - {len(self.compare_data)}, допустимо - 12</b>'
                                              )

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_show_compare_data - {e}')

    def _show_graph(self, obj):
        try:
            self.graphwidget.plot(clear=True)
            if self.type_graph == 'move':
                for graph in obj:
                    x_list = graph.move_list
                    y_list = graph.force_list
                    pen = pg.mkPen(color=self.color_pen[obj.index(graph)], width=3)

                    name = (f'{graph.time_test} - '
                            f'{graph.amort.name} - '
                            f'{graph.serial_number} - '
                            f'{graph.speed}')

                    self.graphwidget.plot(x_list, y_list, pen=pen, name=name)

                self.graphwidget.addLegend()

            elif self.type_graph == 'speed':
                for arch_obj in obj:
                    speed_list = [0]
                    comp_list = [0]
                    recoil_list = [0]
                    push_force = 0
                    for graph in arch_obj:
                        speed_list.append(float(graph.speed))
                        flag_push_force = graph.flag_push_force
                        if flag_push_force == '1':
                            push_force = float(graph.dynamic_push_force)

                        elif flag_push_force == '0':
                            push_force = float(graph.static_push_force)

                        recoil, comp = CalcData().middle_min_and_max_force(graph.force_list)

                        recoil_list.append(round(recoil + push_force, 2))
                        comp_list.append(round(comp * (-1) + push_force, 2))

                    x_list = [*speed_list[::-1], *speed_list]
                    y_list = [*comp_list[::-1], *recoil_list]

                    pen = pg.mkPen(color=self.color_pen[obj.index(arch_obj)], width=3)

                    name = (f'{arch_obj[0].time_test} - '
                            f'{arch_obj[0].amort.name} - '
                            f'{arch_obj[0].serial_number} - '
                            f'{arch_obj[0].speed}~{arch_obj[-1].speed}')

                    self.graphwidget.plot(x_list, y_list, pen=pen, name=name)

                self._fill_limit_lab_cascade_graph(obj[0][0])

                self.graphwidget.addLegend()

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_show_graph - {e}')
