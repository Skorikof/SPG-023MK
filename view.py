from mainui import Ui_MainWindow
from settings_window import SetWindow
from executors_win import ExecWin
from PyQt5.QtWidgets import QMainWindow, QFrame, QLabel
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.Qt import QFont


class VLine(QFrame):
    # a simple VLine, like the one you get from designer
    def __init__(self):
        super(VLine, self).__init__()
        self.setFrameShape(self.VLine|self.Sunken)


class AppWindow(QMainWindow):
    def __init__(self, model, controller):
        super(AppWindow, self).__init__()
        self.model = model
        self.controller = controller
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.win_set = SetWindow(self.model)
        self.win_exec = ExecWin(self.model)

        self._create_statusbar_ui()

        self.operators = None

        self.start_param()

    def closeEvent(self, event):
        self.model.reader_exit()
        self.model.disconnect_client()
        self.model.threadpool.waitForDone()
        self.close()

    def _create_statusbar_ui(self):

        self.lbl_info_msg = QLabel("Инф:")
        self.lbl_info_msg.setStyleSheet('border: 0);')
        self.lbl_info_msg.setFont(QFont('Calibri', 14))

        self.lbl_info_F = QLabel("Усилие,(кгс):")
        self.lbl_info_F.setStyleSheet('border: 0);')
        self.lbl_info_F.setFont(QFont('Calibri', 14))

        self.lbl_info_H = QLabel("Перемещение,(мм):")
        self.lbl_info_H.setStyleSheet('border: 0);')
        self.lbl_info_H.setFont(QFont('Calibri', 16))

        self.lbl_info_Traverse = QLabel("Траверса, (мм):")
        self.lbl_info_Traverse.setStyleSheet('border: 0);')
        self.lbl_info_Traverse.setFont(QFont('Calibri', 16))

        self.lbl_info_executor = QLabel("Оператор:")
        self.lbl_info_executor.setStyleSheet('border: 0);')
        self.lbl_info_executor.setFont(QFont('Calibri', 16))

        self.statusBar().reformat()
        self.statusBar().setStyleSheet('border: 0; background-color: #FFF8DC;')
        self.statusBar().setStyleSheet("QStatusBar::item {border: none;}")

        self.statusBar().addPermanentWidget(VLine())  # <---
        self.statusBar().addPermanentWidget(self.lbl_info_msg, stretch=1)
        self.statusBar().addPermanentWidget(VLine())  # <---
        self.statusBar().addPermanentWidget(self.lbl_info_F, stretch=1)
        self.statusBar().addPermanentWidget(VLine())  # <---
        self.statusBar().addPermanentWidget(self.lbl_info_H, stretch=1)
        self.statusBar().addPermanentWidget(VLine())  # <---
        self.statusBar().addPermanentWidget(self.lbl_info_Traverse, stretch=1)
        self.statusBar().addPermanentWidget(VLine())  # <---
        self.statusBar().addPermanentWidget(self.lbl_info_executor, stretch=1)

    def status_bar_ui(self, txt_bar):
        try:
            self.lbl_info_msg.setText(txt_bar)

        except Exception as e:
            self.model.save_log('error', str(e))

    def start_param(self):
        self.init_buttons()
        self.init_signals()
        self.ui.main_stackedWidget.setCurrentIndex(0)
        self.ui.message_btn_frame.setVisible(False)

    def init_signals(self):
        self.model.signals.stbar_msg.connect(self.status_bar_ui)
        self.win_exec.signals.closed.connect(self.close_win_operator)
        self.win_set.signals.closed.connect(self.close_win_settings)

    def init_buttons(self):
        self.ui.main_close_btn.clicked.connect(self.closeEvent)
        self.ui.main_STOP_btn.clicked.connect(self.btn_main_stop_clicked)
        self.ui.main_operator_btn.clicked.connect(self.open_win_operator)
        self.ui.main_test_btn.clicked.connect(self.specif_page)
        self.ui.main_hand_debug_btn.clicked.connect(self.open_win_settings)
        self.ui.main_archive_btn.clicked.connect(self.archive_page)

    def btn_main_stop_clicked(self):
        try:
            client = self.model.set_connect.get('client')
            if client:
                self.model.set_regs['adr_freq'] = 1
                self.model.motor_stop()
                self.model.set_regs['adr_freq'] = 2
                self.model.motor_stop()
                self.model.reader_stop()
                self.ui.main_stackedWidget.setCurrentIndex(0)
                self.ui.stack_start_label.setText('ЖМАКНУТА\nБОЛЬШАЯ\nКРАСНАЯ\nКНОПКА!!!')

        except Exception as e:
            txt_log = 'ERROR in view/btn_main_stop_clicked - {}'.format(e)
            self.status_bar_ui(txt_log)
            self.model.save_log('error', str(e))

    def open_win_operator(self):
        self.ui.main_stackedWidget.setEnabled(False)
        self.ui.main_btn_frame.setEnabled(False)
        self.win_exec.operator_ui()
        self.win_exec.show()

    def close_win_operator(self):
        self.lbl_info_executor.clear()
        self.ui.main_stackedWidget.setEnabled(True)
        self.ui.main_btn_frame.setEnabled(True)
        self.win_exec.hide()

        name = self.model.set_state.get('operator')['name']
        rank = self.model.set_state.get('operator')['rank']
        if len(name) > 0 and len(rank) > 0:
            self.lbl_info_executor.setText('Оператор: {}, {}'.format(name, rank))

    def specif_page(self):
        self.ui.main_stackedWidget.setCurrentIndex(3)

    def test_page(self):
        self.ui.main_stackedWidget.setCurrentIndex(2)

    def archive_page(self):
        self.ui.main_stackedWidget.setCurrentIndex(5)

    def open_win_settings(self):
        self.ui.main_stackedWidget.setEnabled(False)
        self.ui.main_btn_frame.setEnabled(False)
        self.win_set.show()
        self.win_set.start_param()

    def close_win_settings(self):
        self.ui.main_stackedWidget.setEnabled(True)
        self.ui.main_btn_frame.setEnabled(True)
        self.win_set.hide()
