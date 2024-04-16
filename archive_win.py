from PyQt5.QtWidgets import QMainWindow, QDialog
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtGui import QPageLayout, QPixmap, QPainter
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QAbstractPrintDialog
from archive_ui import Ui_WindowArch
from archive import ReadArchive
from datetime import datetime
from PIL import ImageGrab
import pyqtgraph as pg


class WinSignals(QObject):
    closed = pyqtSignal()
    log_msg = pyqtSignal(str)
    log_err = pyqtSignal(str)


class ArchiveWin(QMainWindow):
    signals = WinSignals()

    def __init__(self):
        super(ArchiveWin, self).__init__()
        try:
            self.archive = None
            self.ui = Ui_WindowArch()
            self.ui.setupUi(self)
            self.hide()
            self._create_statusbar_set()
            self.init_buttons()

        except Exception as e:
            txt_log = 'ERROR in archive_win/__init__ - {}'.format(e)
            self.signals.log_err.emit(txt_log)

    def closeEvent(self, event):
        self.signals.closed.emit()

    def _create_statusbar_set(self):
        self.statusbar = self.statusBar()
        self.statusbar.showMessage('Окно чтения архива испытаний')

    def statusbar_set_ui(self, txt_bar):
        try:
            self.statusbar.showMessage(txt_bar)

        except Exception as e:
            txt_log = 'ERROR in archive_win/statusbar_set_ui - {}'.format(e)
            self.signals.log_err.emit(txt_log)

    def init_buttons(self):
        self.ui.btn_exit.clicked.connect(self.close)
        self.ui.btn_print.clicked.connect(self.archive_save_form)

    def archive_init(self):
        try:
            self.archive = ReadArchive()
            self.archive_update()

        except Exception as e:
            txt_log = 'ERROR in archive_win/archive_init - {}'.format(e)
            self.statusbar_set_ui(txt_log)
            self.signals.log_err.emit(txt_log)

    def archive_update(self):
        try:
            self.archive.init_arch()
            self.ui.combo_dates.clear()
            self.ui.combo_test.clear()

            if len(self.archive.files_arr) == 0:
                self.ui.btn_print.setEnabled(False)
                self.archive_ui_clear()

            else:
                self.ui.combo_dates.addItems(self.archive.files_name_sort)
                self.ui.combo_dates.setCurrentIndex(0)
                self.ui.combo_dates.activated[str].connect(self.archive_selected)
                self.archive_selected(self.archive.files_name_sort[0])
                self.ui.btn_print.setEnabled(True)

        except Exception as e:
            txt_log = 'ERROR in archive_win/archive_update - {}'.format(e)
            self.statusbar_set_ui(txt_log)
            self.signals.log_err.emit(txt_log)

    def archive_ui_clear(self):
        try:
            self.ui.name_le.setText('')
            self.ui.max_comp_le.setText('')
            self.ui.max_recoil_le.setText('')
            self.ui.resistance_le.setText('')
            self.ui.date_le.setText('')
            self.ui.operator_le.setText('')
            self.ui.conclusion_le.setText('')
            self.ui.serial_le.setText('')
            self.ui.type_test_le.setText('')
            self.ui.limit_comp_le.setText('')
            self.ui.limit_recoil_le.setText('')
            self.ui.speed_le.setText('')
            self.ui.temper_le.setText('')

        except Exception as e:
            txt_log = 'ERROR in archive_win/archive_ui_clear - {}'.format(e)
            self.statusbar_set_ui(txt_log)
            self.signals.log_err.emit(txt_log)

    def archive_selected(self, data):
        try:
            self.ui.combo_test.clear()
            temp_arr = []
            self.archive.select_file(data)

            for i in range(len(self.archive.struct.tests)):
                temp = self.archive.struct.tests[i].time + ' - ' + self.archive.struct.tests[i].name + \
                       ' - ' + self.archive.struct.tests[i].serial_number
                temp_arr.append(temp)

            self.ui.combo_test.addItems(temp_arr)

            self.archive_test_select(0)
            self.archive_graph(0)
            self.ui.combo_test.activated[int].connect(self.archive_test_select)
            self.ui.combo_test.activated[int].connect(self.archive_graph)

        except Exception as e:
            txt_log = 'ERROR in archive_win/archive_selected - {}'.format(e)
            self.statusbar_set_ui(txt_log)
            self.signals.log_err.emit(txt_log)

    def archive_test_select(self, data):
        try:
            select_archive = self.archive.files_name_arr[self.archive.index_archive]
            date_arr = select_archive + ' - ' + self.archive.struct.tests[data].time
            min_comp = self.archive.struct.tests[data].min_comp
            max_comp = self.archive.struct.tests[data].max_comp
            min_recoil = self.archive.struct.tests[data].min_recoil
            max_recoil = self.archive.struct.tests[data].max_recoil
            limit_comp = min_comp + ' - ' + max_comp
            limit_recoil = min_recoil + ' - ' + max_recoil

            self.ui.name_le.setText(self.archive.struct.tests[data].name)
            self.ui.limit_comp_le.setText(limit_comp)
            self.ui.max_comp_le.setText(max_comp)
            self.ui.limit_recoil_le.setText(limit_recoil)
            self.ui.max_recoil_le.setText(max_recoil)
            self.ui.speed_le.setText(self.archive.struct.tests[data].speed)
            self.ui.temper_le.setText(self.archive.struct.tests[data].temper)
            self.ui.date_le.setText(date_arr)
            self.ui.operator_le.setText(self.archive.struct.tests[data].operator)
            self.ui.conclusion_le.setText(self.archive.struct.tests[data].conclusion)
            self.ui.serial_le.setText(self.archive.struct.tests[data].serial_number)
            self.ui.resistance_le.setText(self.archive.struct.tests[data].resistance)
            self.ui.type_test_le.setText(self.archive.struct.tests[data].type_test)

        except Exception as e:
            txt_log = 'ERROR in archive_win/archive_test_select - {}'.format(e)
            self.statusbar_set_ui(txt_log)
            self.signals.log_err.emit(txt_log)

    def archive_graph(self, data):
        try:
            self.ui.graphwidget.clear()
            self.ui.graphwidget.setLabel('left', 'СЖАТИЕ ---------------------УСИЛИЕ ------------ОТБОЙ',
                                                 units='кгс')
            self.ui.graphwidget.setLabel('bottom', 'Перемещение', units='мм')
            self.ui.graphwidget.setWindowTitle('ГРАФИК ЗАВИСИМОСТИ УСИЛИЯ ОТ ПЕРЕМЕЩЕНИЯ')

            self.title_graph = 'Amort test'
            self.name_x = 'Перемещение, мм'
            self.name_y = 'Усилие, кгс'
            list_x = []
            list_y = []
            self.max_y = ''
            self.min_y = ''

            flag_mirror = False
            temp_val = self.archive.struct.tests[data].date_arch
            dat_curr = datetime.strptime(temp_val, "%d.%m.%Y")
            dat_m = datetime.strptime('20.04.2022', "%d.%m.%Y")
            if dat_curr < dat_m:
                flag_mirror = True

            for i in range(len(self.archive.struct.tests[data].graph)):
                temp_val = self.archive.struct.tests[data].graph[i]
                temp_val = temp_val.replace(',', '.')
                temp_val = temp_val.split(";")
                list_x.append(float(temp_val[0]))
                if flag_mirror:
                    list_y.append(-float(temp_val[1]))
                else:
                    list_y.append(float(temp_val[1]))
                # list_y.append(float(temp_val[1]))

            temp_val = self.archive.struct.tests[data].graph[0]
            temp_val = temp_val.replace(',', '.')
            temp_val = temp_val.split(";")
            list_x.append(float(temp_val[0]))
            if flag_mirror:
                list_y.append(-float(temp_val[1]))
            else:
                list_y.append(float(temp_val[1]))
            # list_y.append(float(temp_val[1]))

            self.max_y = str(max(list_y))
            self.min_y = str(abs(min(list_y)))

            self.ui.graphwidget.showGrid(True, True)

            self.ui.graphwidget.setBackground('w')

            pen = pg.mkPen(color='k', width=3)

            self.ui.graphwidget.plot(list_x, list_y, pen=pen)
            # if flag_mirror:

            # else:
            self.ui.max_comp_le.setText(self.min_y)
            self.ui.max_recoil_le.setText(self.max_y)

        except Exception as e:
            txt_log = 'ERROR in archive_win/archive_graph - {}'.format(e)
            self.statusbar_set_ui(txt_log)
            self.signals.log_err.emit(txt_log)

    def archive_save_form(self):
        try:
            rect = self.frameGeometry()
            pos = rect.getRect()
            x = pos[0] + 1
            y = pos[1] + 100
            height = 810
            width = 1014

            image = ImageGrab.grab((x, y, x + width, y + height))
            image.save("screen.bmp", "BMP")

            self.printer = QPrinter(QPrinter.HighResolution)
            self.printer.setPageOrientation(QPageLayout.Landscape)

            pd = QPrintDialog(self.printer, parent=self)
            pd.setOptions(QAbstractPrintDialog.PrintToFile | QAbstractPrintDialog.PrintSelection)
            if pd.exec() == QDialog.Accepted:
                self._printImage(self.printer)


        except Exception as e:
            txt_log = 'ERROR in archive_win/archive_save_form - {}'.format(e)
            self.statusbar_set_ui(txt_log)
            self.signals.log_err.emit(txt_log)

    def _printImage(self, printer):
        try:
            painter = QPainter()
            painter.begin(printer)
            pixmap = QPixmap("screen.bmp")
            pixmap = pixmap.scaled(printer.width(), printer.height(), aspectRatioMode=Qt.KeepAspectRatio)
            painter.drawPixmap(0, 0, pixmap)

        except Exception as e:
            txt_log = 'ERROR in archive_win/_printImage - {}'.format(e)
            self.statusbar_set_ui(txt_log)
            self.signals.log_err.emit(txt_log)
