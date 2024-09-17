# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QMainWindow, QDialog
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtGui import QPageLayout, QPixmap, QPainter, QIcon
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QAbstractPrintDialog
from ui_py.archive_ui import Ui_WindowArch
from archive import ReadArchive
from PIL import ImageGrab
import pyqtgraph as pg


class WinSignals(QObject):
    closed = pyqtSignal()
    log_msg = pyqtSignal(str)
    log_err = pyqtSignal(str)


class ArchiveWin(QMainWindow, Ui_WindowArch):
    signals = WinSignals()

    def __init__(self):
        super(ArchiveWin, self).__init__()
        try:
            self.type_graph = 'move'
            self.ind_type_test = -1
            self.index_test = 0
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
        self.btn_print.clicked.connect(self._archive_save_form)

    def archive_update(self):
        try:
            self.archive.init_arch()
            self.combo_dates.clear()
            self.combo_test.clear()

            if len(self.archive.files_arr) == 0:
                self.btn_print.setEnabled(False)
                self._archive_ui_clear()

            else:
                self.btn_print.setEnabled(True)
                self.combo_dates.addItems(self.archive.files_name_sort)
                self.combo_dates.setCurrentIndex(0)
                self._archive_selected(self.archive.files_name_sort[0])
                self.combo_dates.activated[str].connect(self._archive_selected)

                self._archive_test_select(0)
                self._archive_graph(0)
                self.combo_test.activated[int].connect(self._archive_test_select)
                self.combo_test.activated[int].connect(self._archive_graph)

                self._select_type_graph(0)
                self.combo_type.activated[int].connect(self._select_type_graph)

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/archive_update - {e}')

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
            self.push_force_le.setText('')

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_archive_ui_clear - {e}')

    def _select_type_graph(self, index):
        try:
            if self.ind_type_test != index:
                self.ind_type_test = index
                if index == 0:
                    self.type_graph = 'move'
                    self._gui_move_graph()

                elif index == 1:
                    self.type_graph = 'speed'
                    self._gui_speed_graph()
                self._archive_graph(self.index_test)

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_select_type_graph - {e}')

    def _gui_move_graph(self):
        try:
            self.graphwidget.clear()
            self.graphwidget.setLabel('left', 'Усилие', units='кгс')
            self.graphwidget.setLabel('bottom', 'Перемещение', units='мм')
            self.graphwidget.setWindowTitle('ГРАФИК ЗАВИСИМОСТИ УСИЛИЯ ОТ ПЕРЕМЕЩЕНИЯ')
            self.graphwidget.showGrid(True, True)
            self.graphwidget.setBackground('w')

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_gui_move_graph - {e}')

    def _gui_speed_graph(self):
        try:
            self.graphwidget.clear()
            self.graphwidget.setLabel('left', 'Усилие', units='кгс')
            self.graphwidget.setLabel('bottom', 'Скорость', units='м/с')
            self.graphwidget.setWindowTitle('ГРАФИК ЗАВИСИМОСТИ УСИЛИЯ ОТ СКОРОСТИ')
            self.graphwidget.showGrid(True, True)
            self.graphwidget.setBackground('w')

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_gui_speed_graph - {e}')

    def _archive_selected(self, date):
        try:
            self.combo_test.clear()
            temp_arr = []
            self.archive.select_file(date)

            for i in range(len(self.archive.struct.tests)):
                temp = (f'{self.archive.struct.tests[i].time_test} - '
                        f'{self.archive.struct.tests[i].amort.name} - '
                        f'{self.archive.struct.tests[i].serial_number}')
                temp_arr.append(temp)

            self.combo_test.addItems(temp_arr)

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_archive_selected - {e}')

    def _archive_test_select(self, index):
        try:
            user_name = self.archive.struct.tests[index].operator_name
            user_rank = self.archive.struct.tests[index].operator_rank

            select_archive = self.archive.files_name_arr[self.archive.index_archive]
            time_test = self.archive.struct.tests[index].time_test

            min_comp = self.archive.struct.tests[index].amort.min_comp
            min_comp_2 = self.archive.struct.tests[index].amort.min_comp_2
            max_comp = self.archive.struct.tests[index].amort.max_comp
            max_comp_2 = self.archive.struct.tests[index].amort.max_comp_2
            min_recoil = self.archive.struct.tests[index].amort.min_recoil
            min_recoil_2 = self.archive.struct.tests[index].amort.min_recoil_2
            max_recoil = self.archive.struct.tests[index].amort.max_recoil
            max_recoil_2 = self.archive.struct.tests[index].amort.max_recoil_2

            self.name_le.setText(f'{self.archive.struct.tests[index].amort.name}')
            self.operator_le.setText(f'{user_rank} {user_name}')
            self.speed_set_1_le.setText(f'{self.archive.struct.tests[index].amort.speed_one}')
            self.speed_set_2_le.setText(f'{self.archive.struct.tests[index].amort.speed_two}')
            self.limit_recoil_1_le.setText(f'{min_recoil} - {max_recoil}')
            self.limit_recoil_2_le.setText(f'{min_recoil_2} - {max_recoil_2}')
            self.limit_comp_1_le.setText(f'{min_comp} - {max_comp}')
            self.limit_comp_2_le.setText(f'{min_comp_2} - {max_comp_2}')
            self.serial_le.setText(f'{self.archive.struct.tests[index].serial_number}')
            self.date_le.setText(f'{select_archive} - {time_test}')
            self.max_temp_le.setText(f'{self.archive.struct.tests[index].amort.max_temper}')
            self.hod_le.setText(f'{self.archive.struct.tests[index].amort.hod}')

            self.push_force_le.setText(f'{self.archive.struct.tests[index].push_force}')
            self.speed_le.setText(f'{self.archive.struct.tests[index].speed}')

            self._fill_flag_push_force(index)

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_archive_test_select - {e}')

    def _fill_flag_push_force(self, index):
        txt = ''
        flag = self.archive.struct.tests[index].flag_push_force
        if flag == '1':
            txt = f'Динамическая\nвыталкивающая\nсила'
        elif flag == '0':
            txt = f'Статическая\nвыталкивающая\nсила'

        self.lbl_push_force.setText(txt)

    def _archive_graph(self, index):
        try:
            self.index_test = index
            self.graphwidget.clear()

            move_list = self.archive.struct.tests[index].move_list
            force_list = self.archive.struct.tests[index].force_list

            max_recoil = max(force_list)
            max_comp = abs(min(force_list))

            pen = pg.mkPen(color='black', width=3)

            if self.type_graph == 'speed':
                move_list = self._convert_move_in_speed(move_list)

            self.graphwidget.plot(move_list, force_list, pen=pen)

            self.comp_le.setText(f'{max_comp}')
            self.recoil_le.setText(f'{max_recoil}')

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_archive_graph - {e}')

    def _pars_lab_graph(self, index):
        try:
            move_list = self.archive.struct.tests[index].move_list
            force_list = self.archive.struct.tests[index].force_list

            max_recoil = max(force_list)
            max_comp = abs(min(force_list))

            pen = pg.mkPen(color='black', width=3)

            if self.type_graph == 'speed':
                move_list = self._convert_move_in_speed(move_list)

            self.graphwidget.plot(move_list, force_list, pen=pen)

            self.comp_le.setText(f'{max_comp}')
            self.recoil_le.setText(f'{max_recoil}')

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_pars_lab_graph - {e}')

    def _convert_move_in_speed(self, move_list):
        try:
            sum_list = []
            response_list = []
            begin_5_points = move_list[0:5]
            end_5_points = move_list[-5:]
            temp_list = end_5_points + move_list + begin_5_points

            for i in range(len(move_list)):
                for j in range(i, i + 10):
                    sum_list.append(round(abs(abs(temp_list[j]) - abs(temp_list[j + 1])), 2))

                temp_sum = 0
                for k in range(len(sum_list) - 1):
                    temp_sum = temp_sum + abs(sum_list[k] - sum_list[k + 1])

                response_list.append(round(temp_sum, 10))

                sum_list = []

            return response_list

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_convert_move_in_speed - {e}')

    def _archive_save_form(self):
        try:
            rect = self.frameGeometry()
            pos = rect.getRect()
            x = pos[0] + 1
            y = pos[1] + 80
            height = 820
            width = 1024

            image = ImageGrab.grab((x, y, x + width, y + height))
            image.save("screen.bmp", "BMP")

            self.printer = QPrinter(QPrinter.HighResolution)
            self.printer.setPageOrientation(QPageLayout.Landscape)

            pd = QPrintDialog(self.printer, parent=self)
            pd.setOptions(QAbstractPrintDialog.PrintToFile | QAbstractPrintDialog.PrintSelection)
            if pd.exec() == QDialog.Accepted:
                self._print_image(self.printer)

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_archive_save_form - {e}')

    def _print_image(self, printer):
        try:
            painter = QPainter()
            painter.begin(printer)
            pixmap = QPixmap("screen.bmp")
            pixmap = pixmap.scaled(printer.width(), printer.height(), aspectRatioMode=Qt.KeepAspectRatio)
            painter.drawPixmap(0, 0, pixmap)

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_printImage - {e}')
