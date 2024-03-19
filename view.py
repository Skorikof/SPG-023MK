from mainui import Ui_MainWindow
from operators import Operators
from settings_window import SetWindow
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt, QObject, pyqtSignal


class AppWindow(QMainWindow):
    def __init__(self, model, controller):
        super(AppWindow, self).__init__()
        self.model = model
        self.controller = controller
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.win_set = SetWindow(self.model)

        self.operators = None

        self.start_param()

    def closeEvent(self, event):
        # self.model.reader_buffer_exit()
        self.model.reader_exit()
        self.model.disconnect_client()
        self.model.threadpool.waitForDone()
        self.close()

    def status_bar_ui(self, txt_bar):
        try:
            self.statusBar().showMessage(txt_bar)

        except Exception as e:
            self.model.save_log('error', str(e))

    def start_param(self):
        self.init_buttons()
        self.init_signals()
        self.ui.main_stackedWidget.setCurrentIndex(0)
        self.ui.message_btn_frame.setVisible(False)

        # self.win_set.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

    def init_signals(self):
        self.model.signals.stbar_msg.connect(self.status_bar_ui)
        self.model.signals.read_finish.connect(self.update_data)
        self.win_set.signals.closed.connect(self.close_win_settings)

    def init_buttons(self):
        self.ui.main_close_btn.clicked.connect(self.closeEvent)
        self.ui.main_STOP_btn.clicked.connect(self.btn_main_stop_clicked)
        self.ui.main_operator_btn.clicked.connect(self.operator_page)
        self.ui.main_test_btn.clicked.connect(self.specif_page)
        self.ui.main_hand_debug_btn.clicked.connect(self.open_hidden_settings)
        self.ui.main_archive_btn.clicked.connect(self.archive_page)

    def btn_main_stop_clicked(self):
        try:
            self.model.reader_stop()
            self.ui.main_stackedWidget.setCurrentIndex(0)
            self.ui.stack_start_label.setText('ЖМАКНУТА\nБОЛЬШАЯ\nКРАСНАЯ\nКНОПКА!!!')

        except Exception as e:
            txt_log = 'ERROR in view/btn_main_stop_clicked - {}'.format(e)
            self.status_bar_ui(txt_log)
            self.model.save_log('error', str(e))

    def update_data(self):
        self.win_set.update_win()

    # def init_operators(self):
    #     try:
    #         self.operators = Operators()
    #         self.update_operators()
    #
    #     except Exception as e:
    #         txt_log = 'ERROR in view/init_operators - {}'.format(e)
    #         self.status_bar_ui(txt_log)
    #         self.model.save_log('error', str(e))

    def update_operators(self):
        try:
            self.operators.update_list()
            self.ui.operator_name_comboBox.clear()
            if len(self.operators.config.sections()) == 0:
                self.ui.operator_ok_btn.setEnabled(False)
                self.ui.operator_del_btn.setEnabled(False)
                self.ui.operator_position_lineEdit.setText('')
            else:
                self.ui.operator_name_comboBox.addItems(self.operators.names)
                self.ui.operator_name_comboBox.setCurrentIndex(0)
                self.operators.current_index = 0
                self.select_operator(self.operators.current_index)
                self.ui.operator_ok_btn.setEnabled(True)
                self.ui.operator_del_btn.setEnabled(True)

        except Exception as e:
            txt_log = 'ERROR in view/update_operators - {}'.format(e)
            self.status_bar_ui(txt_log)
            self.model.save_log('error', str(e))

    def select_operator(self, ind):
        try:
            self.operators.current_index = ind
            self.ui.operator_position_lineEdit.setText(self.operators.ranks[ind])

        except Exception as e:
            txt_log = 'ERROR in view/select_operator - {}'.format(e)
            self.status_bar_ui(txt_log)
            self.model.save_log('error', str(e))

    # def operator_add_btn(self):
    #     try:
    #
    #
    #     except Exception as e:
    #         txt_log = 'ERROR in view/operator_add_btn - {}'.format(e)
    #         self.status_bar_ui(txt_log)
    #         self.model.save_log('error', str(e))

    def operator_page(self):
        self.ui.main_stackedWidget.setCurrentIndex(1)
        self.operators = Operators()
        self.update_operators()

    def specif_page(self):
        self.ui.main_stackedWidget.setCurrentIndex(3)

    def test_page(self):
        self.ui.main_stackedWidget.setCurrentIndex(2)

    def archive_page(self):
        self.ui.main_stackedWidget.setCurrentIndex(5)

    def open_hidden_settings(self):
        self.ui.main_stackedWidget.setEnabled(False)
        self.ui.main_btn_frame.setEnabled(False)
        self.model.reader_start()
        self.win_set.show()

    def close_win_settings(self):
        self.ui.main_stackedWidget.setEnabled(True)
        self.ui.main_btn_frame.setEnabled(True)
        self.model.reader_stop()
        self.win_set.hide()
