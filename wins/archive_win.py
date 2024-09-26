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
            self.ind_type_test = 0
            self.index_date = ''
            self.index_test = 0
            self.index_test_cascade = 0
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

        self.combo_dates.activated[str].connect(self._change_index_date)
        self.combo_test.activated[int].connect(self._change_index_test)
        self.combo_type.activated[int].connect(self._change_type_graph)

    def read_path_archive(self):
        try:
            self.combo_dates.clear()
            self.combo_test.clear()
            self.archive.init_arch()

            if len(self.archive.files_arr) == 0:
                self._archive_ui_clear()

            else:
                self.combo_dates.addItems(self.archive.files_name_sort)
                self.combo_dates.setCurrentIndex(0)
                self.index_date = self.archive.files_name_sort[0]
                self._archive_update()

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/read_path_archive - {e}')

    def _archive_update(self):
        try:
            self._archive_selected()
            self._archive_graph()

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_archive_update - {e}')

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

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_archive_ui_clear - {e}')

    def _change_index_date(self, date):
        try:
            if self.index_date != date:
                self.index_date = date
                self._archive_update()

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_change_index_date - {e}')

    def _change_index_test(self, index):
        try:
            if self.type_graph == 'move':
                if self.index_test != index:
                    self.index_test = index
                    self._archive_test_select()
                    self._archive_graph()

            elif self.type_graph == 'speed':
                if self.index_test_cascade != index:
                    self.index_test_cascade = index
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

                self._archive_update()

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_select_type_graph - {e}')

    def _archive_selected(self):
        try:
            date = self.index_date
            self.combo_test.clear()
            temp_arr = []
            self.archive.select_file(date)

            if self.type_graph == 'move':
                for i in range(len(self.archive.struct.tests)):
                    temp = (f'{self.archive.struct.tests[i].time_test} - '
                            f'{self.archive.struct.tests[i].amort.name} - '
                            f'{self.archive.struct.tests[i].serial_number}')
                    temp_arr.append(temp)

            elif self.type_graph == 'speed':
                for key, value in self.archive.struct_cascade.cascade.items():
                    temp = (f'{value[0].time_test} - '
                            f'{value[0].amort.name} - '
                            f'{value[0].serial_number}')
                    temp_arr.append(temp)

            if temp_arr:
                self.combo_test.addItems(temp_arr)
                self._archive_test_select()
                self._archive_graph()
            else:
                pass

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_archive_selected - {e}')

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

    def _archive_test_select(self):
        try:
            if self.type_graph == 'move':
                self._pars_lab_data()

            if self.type_graph == 'speed':
                self._pars_lab_cascade_data()

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_archive_test_select - {e}')

    def _pars_lab_data(self):
        try:
            index = self.index_test

            if self.archive.struct.tests[index]:

                self._fill_archive_data_gui(self.archive.struct.tests[index])

                self.speed_le.setText(f'{self.archive.struct.tests[index].speed}')

                self._fill_flag_push_force(self.archive.struct.tests[index].flag_push_force)

            else:
                pass

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_pars_lab_data - {e}')

    def _pars_lab_cascade_data(self):
        try:
            index = self.index_test_cascade
            if not self.archive.struct_cascade.cascade.get(index + 1) is None:
                data = self.archive.struct_cascade.cascade.get(index + 1)
                self._fill_archive_data_gui(data[0])

                self._fill_flag_push_force(data[0].flag_push_force)

                speed_list = []
                for obj in data:
                    speed_list.append(obj.speed)

                self.speed_le.setText(f'{speed_list[0]} - {speed_list[-1]}')

            else:
                pass

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_pars_lab_cascade_data - {e}')

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
        if index == '1':
            txt = f'Динамическая\nвыталкивающая\nсила'
        elif index == '0':
            txt = f'Статическая\nвыталкивающая\nсила'

        self.lbl_push_force.setText(txt)

    def _archive_graph(self):
        try:
            self.graphwidget.clear()
            if self.type_graph == 'move':
                self._gui_move_graph()
                self._fill_lab_graph()

            elif self.type_graph == 'speed':
                self._gui_speed_graph()
                self._fill_lab_cascade_graph()

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_archive_graph - {e}')

    def _fill_lab_graph(self):
        try:
            index = self.index_test
            move_list = self.archive.struct.tests[index].move_list
            force_list = self.archive.struct.tests[index].force_list

            max_recoil = round(max(force_list) + float(self.archive.struct.tests[index].push_force), 2)
            max_comp = round(abs(min(force_list)) - float(self.archive.struct.tests[index].push_force), 2)

            pen = pg.mkPen(color='black', width=3)

            self.graphwidget.plot(move_list, force_list, pen=pen)

            self.comp_le.setText(f'{max_comp}')
            self.recoil_le.setText(f'{max_recoil}')

            power = self._calc_power(move_list, force_list)
            print(f'{power=}')

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_fill_lab_graph - {e}')

    def _fill_lab_cascade_graph(self):
        try:
            index = self.index_test_cascade
            speed_list = [0]
            comp_list = [0]
            recoil_list = [0]
            data = self.archive.struct_cascade.cascade.get(index + 1)

            for obj in data:
                speed_list.append(float(obj.speed))
                recoil_list.append(round(max(obj.force_list) + float(obj.push_force), 2))
                comp_list.append(round(min(obj.force_list) + float(obj.push_force), 2))

            pen = pg.mkPen(color='black', width=3)

            self.graphwidget.plot(speed_list, recoil_list, pen=pen)
            self.graphwidget.plot(speed_list, comp_list, pen=pen)

            self.recoil_le.setText(f'{max(recoil_list)}')
            self.comp_le.setText(f'{abs(min(comp_list))}')

            self._fill_limit_lab_cascade_graph(data[0])

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_fill_lab_cascade_graph - {e}')

    def _fill_limit_lab_cascade_graph(self, obj):
        try:
            speed_1 = []
            speed_2 = []
            limit_recoil_1 = []
            limit_recoil_2 = []
            limit_comp_1 = []
            limit_comp_2 = []

            speed_1.append(float(obj.amort.speed_one))
            speed_1.append(float(obj.amort.speed_one))

            speed_2.append(float(obj.amort.speed_two))
            speed_2.append(float(obj.amort.speed_two))

            limit_recoil_1.append(float(obj.amort.min_recoil))
            limit_recoil_1.append(float(obj.amort.max_recoil))

            limit_recoil_2.append(float(obj.amort.min_recoil_2))
            limit_recoil_2.append(float(obj.amort.max_recoil_2))

            limit_comp_1.append(float(obj.amort.min_comp) * -1)
            limit_comp_1.append(float(obj.amort.max_comp) * -1)

            limit_comp_2.append(float(obj.amort.min_comp_2) * -1)
            limit_comp_2.append(float(obj.amort.max_comp_2) * -1)

            pen = pg.mkPen(color='red', width=3)

            self.graphwidget.plot(speed_1, limit_recoil_1, pen=pen)
            self.graphwidget.plot(speed_1, limit_comp_1, pen=pen)
            self.graphwidget.plot(speed_2, limit_recoil_2, pen=pen)
            self.graphwidget.plot(speed_2, limit_comp_2, pen=pen)


        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_fill_limit_lab_cascade_graph - {e}')

    def _calc_power(self, move: list, force: list):
        try:
            temp = 0
            for i in range(1, len(move)):
                temp = round(temp + abs(move[i] - abs(move[i - 1])) * abs(force[i - 1]), 1)

            temp = round(temp * 0.009807, 1)

            return temp

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in archive_win/_calc_power - {e}')

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
