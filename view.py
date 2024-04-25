from mainui import Ui_MainWindow
from executors_win import ExecWin
from amorts_win import AmortWin
from archive_win import ArchiveWin
from datetime import datetime
import pyqtgraph as pg
from PyQt5.QtWidgets import QMainWindow, QFrame, QLabel
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.Qt import QFont
import glob_var


class VLine(QFrame):
    # a simple VLine, like the one you get from designer
    def __init__(self):
        super(VLine, self).__init__()
        self.setFrameShape(self.VLine | self.Sunken)


class AppWindow(QMainWindow):
    def __init__(self, model, controller, win_set):
        super(AppWindow, self).__init__()
        self.model = model
        self.controller = controller
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.win_set = win_set
        self.win_exec = ExecWin()
        self.win_amort = AmortWin()
        self.win_archive = ArchiveWin()

        self._create_statusbar_ui()

        self.operators = None
        self.amort = None
        self.current_amort = None

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
        self.lbl_info_H.setFont(QFont('Calibri', 14))

        self.lbl_info_Traverse = QLabel("Траверса, (мм):")
        self.lbl_info_Traverse.setStyleSheet('border: 0);')
        self.lbl_info_Traverse.setFont(QFont('Calibri', 14))

        self.lbl_info_executor = QLabel("Оператор:")
        self.lbl_info_executor.setStyleSheet('border: 0);')
        self.lbl_info_executor.setFont(QFont('Calibri', 14))

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
            txt_log = 'ERROR in view/status_bar_ui - {}'.format(e)
            self.log_msg_err_slot(txt_log)

    def update_statusbar_data(self, result):
        try:
            txt = 'Усилие, кгс: {}'.format(result.get('force_now'))
            self.lbl_info_F.setText(txt)
            txt = 'Перемещение, мм: {}'.format(result.get('amort_move'))
            self.lbl_info_H.setText(txt)
            txt = 'Траверса, мм: {}'.format(result.get('traverse_move'))
            self.lbl_info_Traverse.setText(txt)

        except Exception as e:
            txt_log = 'ERROR in view/update_statusbar_data - {}'.format(e)
            self.status_bar_ui(txt_log)
            self.log_msg_err_slot(txt_log)

    def start_param(self):
        self.init_buttons()
        self.init_signals()
        self.start_page()

    def init_signals(self):
        self.model.signals.stbar_msg.connect(self.status_bar_ui)
        self.model.signals.read_finish.connect(self.update_statusbar_data)

        self.controller.signals.control_msg.connect(self.controller_msg_slot)

        self.win_exec.signals.closed.connect(self.close_win_operator)
        self.win_exec.signals.log_msg.connect(self.log_msg_info_slot)
        self.win_exec.signals.log_err.connect(self.log_msg_err_slot)
        self.win_exec.signals.operator_select.connect(self.operator_select)

        self.win_amort.signals.closed.connect(self.close_win_amort)
        self.win_amort.signals.log_msg.connect(self.log_msg_info_slot)
        self.win_amort.signals.log_err.connect(self.log_msg_err_slot)

        self.win_set.signals.closed.connect(self.close_win_settings)
        self.win_set.signals.log_err.connect(self.log_msg_err_slot)

        self.win_archive.signals.closed.connect(self.close_win_archive)
        self.win_archive.signals.log_msg.connect(self.log_msg_info_slot)
        self.win_archive.signals.log_err.connect(self.log_msg_err_slot)

    def init_buttons(self):
        self.ui.main_close_btn.clicked.connect(self.closeEvent)
        self.ui.main_STOP_btn.clicked.connect(self.btn_main_stop_clicked)
        self.ui.ok_message_btn.clicked.connect(self.btn_ok_message_clicked)
        self.ui.main_operator_btn.clicked.connect(self.open_win_operator)
        self.ui.main_test_btn.clicked.connect(self.specif_page)
        self.ui.main_hand_debug_btn.clicked.connect(self.open_win_settings)
        self.ui.main_archive_btn.clicked.connect(self.open_win_archive)
        self.ui.main_amorts_btn.clicked.connect(self.open_win_amort)

        self.ui.specif_continue_btn.clicked.connect(self.specif_continue_btn_click)
        self.ui.test_cancel_btn.clicked.connect(self.test_cancel_click)

    def log_msg_info_slot(self, txt_log):
        self.model.save_log('info', txt_log)

    def log_msg_err_slot(self, txt_log):
        self.model.save_log('error', txt_log)

    def controller_msg_slot(self, msg):
        try:
            txt = ''
            tag = 'warning'
            if msg == 'pos_traverse':
                txt = 'ПОЗИЦИОНИРОВАНИЕ\nТРАВЕРСЫ'
                tag = 'attention'

            elif msg == 'move_detection':
                txt = 'ВНИМАНИЕ!\nБудет произведено\nопределение хода'
                tag = 'attention'

            elif msg == 'lost_control':
                self.log_msg_err_slot(msg)
                txt = 'ПОТЕРЯНО\nУПРАВЛЕНИЕ'

            elif msg == 'excess_force':
                self.log_msg_err_slot(msg)
                txt = 'ПРЕВЫШЕНИЕ\nУСИЛИЯ'

            elif msg == 'safety_fence':
                self.log_msg_err_slot(msg)
                txt = 'ОТКРЫТО\nЗАЩИТНОЕ\nОГРАЖДЕНИЕ'

            elif msg == 'alarm_traverce_up':
                self.log_msg_err_slot(msg)
                txt = 'ТРАВЕРСА\nВ ВЕРХНЕМ\nПОЛОЖЕНИИ'

            elif msg == 'alarm_traverce_down':
                self.log_msg_err_slot(msg)
                txt = 'ТРАВЕРСА\nВ НИЖНЕМ\nПОЛОЖЕНИИ'

            self.main_ui_msg(txt, tag)

        except Exception as e:
            txt_log = 'ERROR in view/slot_controller_msg - {}'.format(e)
            self.status_bar_ui(txt_log)
            self.log_msg_err_slot(txt_log)

    def main_ui_msg(self, txt, tag):
        try:
            backcolor = ''
            color = glob_var.COLOR_BLACK

            if tag == 'info':
                self.ui.message_btn_frame.setVisible(False)

            elif tag == 'attention':
                backcolor = glob_var.COLOR_ORANGE
                self.ui.message_btn_frame.setVisible(False)

            elif tag == 'warning':
                backcolor = glob_var.COLOR_RED
                color = glob_var.COLOR_LYELLOW
                self.ui.message_btn_frame.setVisible(True)
                self.ui.ok_message_btn.setVisible(True)
                self.ui.cancel_message_btn.setVisible(False)
                self.ui.main_btn_frame.setEnabled(False)
            self.ui.main_stackedWidget.setCurrentIndex(0)
            self.ui.stack_start_label.setText(txt)
            self.ui.stack_start_label.setStyleSheet("background-color: " + backcolor + ";\n" +
                                                    "color: " + color + ";")

        except Exception as e:
            txt_log = 'ERROR in view/main_ui_msg - {}'.format(e)
            self.status_bar_ui(txt_log)
            self.log_msg_err_slot(txt_log)

    def btn_main_stop_clicked(self):
        try:
            txt = 'РАБОТА ПРЕРВАНА\nПО КОМАНДЕ\nОПЕРАТОРА'
            tag = 'warning'
            self.main_ui_msg(txt, tag)
            self.controller.work_interrupted_operator()
            txt_log = 'Work stopped interrupted operator'
            self.log_msg_info_slot(txt_log)

        except Exception as e:
            txt_log = 'ERROR in view/btn_main_stop_clicked - {}'.format(e)
            self.status_bar_ui(txt_log)
            self.log_msg_err_slot(txt_log)

    def btn_ok_message_clicked(self):
        try:
            self.start_page()

        except Exception as e:
            txt_log = 'ERROR in view/btn_ok_message_clicked - {}'.format(e)
            self.status_bar_ui(txt_log)
            self.log_msg_err_slot(txt_log)

    def main_ui_enable(self):
        self.ui.main_stackedWidget.setEnabled(True)
        self.ui.main_btn_frame.setEnabled(True)

    def main_ui_disable(self):
        self.ui.main_stackedWidget.setEnabled(False)
        self.ui.main_btn_frame.setEnabled(False)

    def start_page(self):
        try:
            txt = "Здравствуйте.\nДобро пожаловать\nв\nпрограмму.\nВыберите необходимый\nпункт меню."
            tag = 'info'
            self.main_ui_msg(txt, tag)
            self.ui.main_btn_frame.setEnabled(True)

        except Exception as e:
            txt_log = 'ERROR in view/start_page - {}'.format(e)
            self.status_bar_ui(txt_log)
            self.log_msg_err_slot(txt_log)

    def open_win_operator(self):
        self.main_ui_disable()
        self.win_exec.show()

    def operator_select(self, name, rank):
        self.model.set_state['operator']['name'] = name
        self.model.set_state['operator']['rank'] = rank

        self.lbl_info_executor.setText('Оператор: {}, {}'.format(name, rank))

    def close_win_operator(self):
        self.main_ui_enable()
        self.win_exec.hide()

    def open_win_amort(self):
        self.main_ui_disable()
        self.win_amort.show()

    def close_win_amort(self):
        self.main_ui_enable()
        self.win_amort.hide()

    def specif_page(self):
        self.specif_ui_clear()
        self.ui.main_stackedWidget.setCurrentIndex(3)
        self.ui.specif_add_btn.setVisible(False)
        self.ui.specif_del_btn.setVisible(False)
        self.ui.specif_choice_comboBox.addItems(self.win_amort.amorts.names)
        if len(self.win_amort.amorts.names) < 1:
            self.ui.specif_continue_btn.setEnabled(False)
        else:
            self.ui.specif_continue_btn.setEnabled(True)
            self.ui.specif_choice_comboBox.activated[int].connect(self.select_amort)
            self.select_amort(0)

        self.ui.specif_type_test_comboBox.activated[int].connect(self.select_type_test)
        self.select_type_test(0)

    def select_type_test(self, ind):
        try:
            if ind == 0:
                self.model.set_state['type_test'] = 'lab'

            elif ind == 1:
                self.model.set_state['type_test'] = 'conv'

        except Exception as e:
            txt_log = 'ERROR in view/select_type_test - {}'.format(e)
            self.status_bar_ui(txt_log)
            self.log_msg_err_slot(txt_log)

    def select_amort(self, ind):
        try:
            self.current_amort = self.win_amort.amorts.struct.amorts[ind]

            self.specif_ui_fill(self.current_amort)

        except Exception as e:
            txt_log = 'ERROR in view/select_amort - {}'.format(e)
            self.status_bar_ui(txt_log)
            self.log_msg_err_slot(txt_log)

    def specif_ui_fill(self, obj):
        try:
            self.ui.specif_name_lineEdit.setText(str(obj.name_a))
            self.ui.specif_min_length_lineEdit.setText(str(obj.min_length))
            self.ui.specif_max_length_lineEdit.setText(str(obj.max_length))
            self.ui.specif_speed_lineEdit.setText(str(obj.speed))
            self.ui.specif_min_comp_lineEdit.setText(str(obj.min_comp))
            self.ui.specif_max_comp_lineEdit.setText(str(obj.max_comp))
            self.ui.specif_min_recoil_lineEdit.setText(str(obj.min_recoil))
            self.ui.specif_max_recoil_lineEdit.setText(str(obj.max_recoil))
            self.ui.specif_max_temp_lineEdit.setText(str(obj.max_temper))

        except Exception as e:
            txt_log = 'ERROR in view/specif_ui_fill - {}'.format(e)
            self.status_bar_ui(txt_log)
            self.log_msg_err_slot(txt_log)

    def specif_ui_clear(self):
        try:
            self.ui.specif_name_lineEdit.clear()
            self.ui.specif_min_length_lineEdit.clear()
            self.ui.specif_max_length_lineEdit.clear()
            self.ui.specif_speed_lineEdit.clear()
            self.ui.specif_min_comp_lineEdit.clear()
            self.ui.specif_max_comp_lineEdit.clear()
            self.ui.specif_min_recoil_lineEdit.clear()
            self.ui.specif_max_recoil_lineEdit.clear()
            self.ui.specif_max_temp_lineEdit.clear()
            
        except Exception as e:
            txt_log = 'ERROR in view/specif_ui_clear - {}'.format(e)
            self.status_bar_ui(txt_log)
            self.log_msg_err_slot(txt_log)

    def specif_continue_btn_click(self):
        try:
            name = self.model.set_state.get('operator')['name']
            rank = self.model.set_state.get('operator')['rank']
            if len(name) > 1 and len(rank) > 1:
                self.test_page()

            else:
                self.open_win_operator()

        except Exception as e:
            txt_log = 'ERROR in view/specif_continue_btn_click - {}'.format(e)
            self.status_bar_ui(txt_log)
            self.log_msg_err_slot(txt_log)

    def test_page(self):
        try:
            name = self.current_amort.name_a
            type_test = self.model.set_state.get('type_test')
            limit_comp = str(self.current_amort.min_comp) + ' - ' + str(self.current_amort.max_comp)
            limit_recoil = str(self.current_amort.min_recoil) + ' - ' + str(self.current_amort.max_recoil)
            speed = str(self.current_amort.speed)
            txt_log = 'Start test amort -> {}, type_test - {}, limit_comp - {},' \
                      'limit_recoil - {}, speed - {}'.format(name,
                                                             type_test,
                                                             limit_comp,
                                                             limit_recoil,
                                                             speed)

            self.log_msg_info_slot(txt_log)

            self.ui.main_stackedWidget.setCurrentIndex(2)
            self.ui.test_save_btn.setVisible(False)
            self.ui.test_repeat_btn.setVisible(False)

            self.ui.test_data_name_lineEdit.setText(name)

            self.ui.test_data_limit_comp_lineEdit.setText(limit_comp)
            self.ui.test_data_limit_recoil_lineEdit.setText(limit_recoil)
            self.ui.test_data_speed_lineEdit.setText(speed)

        except Exception as e:
            txt_log = 'ERROR in view/test_page - {}'.format(e)
            self.status_bar_ui(txt_log)
            self.log_msg_err_slot(txt_log)

    def test_cancel_click(self):
        try:
            self.btn_main_stop_clicked()

        except Exception as e:
            txt_log = 'ERROR in view/test_cancel_click - {}'.format(e)
            self.status_bar_ui(txt_log)
            self.log_msg_err_slot(txt_log)

    # def save_test_archive(self):
    #     self.win_archive.archive_save_test()

    def open_win_archive(self):
        self.main_ui_disable()
        self.win_archive.show()
        self.win_archive.archive_update()

    def close_win_archive(self):
        self.main_ui_enable()
        self.win_archive.hide()

    def open_win_settings(self):
        self.main_ui_disable()
        self.win_set.show()
        self.win_set.start_param()

    def close_win_settings(self):
        self.main_ui_enable()
        self.win_set.hide()
