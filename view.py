from mainui import Ui_MainWindow
from executors_win import ExecWin
from amorts_win import AmortWin
from archive_win import ArchiveWin
from datetime import datetime
import pyqtgraph as pg
from PyQt5.QtWidgets import QMainWindow, QFrame, QLabel
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QRect
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
        self.response = {}
        self.pen_test_conv = None
        self.data_line_test_conv = None
        self.model = model
        self.controller = controller
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.win_set = win_set
        self.win_exec = ExecWin()
        self.win_amort = AmortWin()
        self.win_archive = ArchiveWin()

        self._create_statusbar_ui()

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
            self.log_msg_err_slot(f'ERROR in view/status_bar_ui - {e}')

    def update_statusbar_data(self, result):
        try:
            txt = 'Усилие, кгс: {}'.format(result.get('force'))
            self.lbl_info_F.setText(txt)
            txt = 'Перемещение, мм: {}'.format(result.get('move'))
            self.lbl_info_H.setText(txt)
            txt = 'Траверса, мм: {}'.format(result.get('traverse_move'))
            self.lbl_info_Traverse.setText(txt)

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/update_statusbar_data - {e}')

    def start_param(self):
        self.init_buttons()
        self.init_signals()
        self.start_page()
        self.ui.main_STOP_btn.setEnabled(False)
        self.init_conv_graph()

    def init_signals(self):
        self.model.signals.stbar_msg.connect(self.status_bar_ui)
        self.model.signals.read_finish.connect(self.update_data)
        self.model.signals.update_graph_settings.connect(self.update_data_graph)

        self.controller.signals.control_msg.connect(self.controller_msg_slot)
        self.controller.signals.traverse_referent.connect(self.msg_traverse_referent)
        self.controller.signals.traverse_position.connect(self.msg_traverse_position)
        self.controller.signals.wait_yellow_btn.connect(self.msg_yellow_btn)
        self.controller.signals.conv_win_test.connect(self.conv_test_win)

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
        self.ui.test_cancel_btn.clicked.connect(self.test_lab_cancel_click)
        self.ui.test_repeat_btn.clicked.connect(self.test_lab)
        self.ui.test_conv_cancel_btn.clicked.connect(self.test_conv_cancel_click)

    def update_data(self, response):
        try:
            self.response = response
            self.update_statusbar_data(self.response)

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/update_data - {e}')

    def log_msg_info_slot(self, txt_log):
        self.model.log_info(txt_log)

    def log_msg_err_slot(self, txt_log):
        self.model.log_error(txt_log)

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
            else:
                print(msg)

            self.log_msg_err_slot(msg)
            self.main_ui_msg(txt, tag)

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/slot_controller_msg - {e}')

    def msg_traverse_referent(self):
        try:
            txt = 'ОПРЕДЕЛЕНИЕ\nРЕФЕРЕНТНОЙ ТОЧКИ\nТРАВЕРСЫ'
            self.main_ui_msg(txt, 'attention')

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/msg_traverse_referent - {e}')

    def msg_traverse_position(self):
        try:
            txt = 'ПОЗИЦИОНИРОВАНИЕ\nТРАВЕРСЫ\nДЛЯ УСТАНОВКИ\nАМОРТИЗАТОРА'
            self.main_ui_msg(txt, 'attention')

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/msg_traverse_position - {e}')

    def msg_yellow_btn(self):
        try:
            temp = self.response.get('type_test')
            if temp == 'conv':
                txt = 'НАЖМИТЕ\nЖЁЛТУЮ\nКНОПКУ\nДЛЯ ЗАПУСКА\nИСПЫТАНИЯ'
                self.main_ui_msg(txt, 'attention')

            elif temp == 'lab':
                txt = 'ЖМАКНИТЕ\nЧТО-НИБУДЬ\nДЛЯ ЗАПУСКА\nИСПЫТАНИЯ'
                self.main_ui_msg(txt, 'attention')

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/msg_yellow_btn - {e}')

    def msg_test_move_cycle(self):
        try:
            txt = 'ПРОВЕРОЧНЫЙ\nХОД'
            self.main_ui_msg(txt, 'attention')

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/msg_test_move_cycle - {e}')

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
            self.log_msg_err_slot(f'ERROR in view/main_ui_msg - {e}')

    def btn_main_stop_clicked(self):
        try:
            self.ui.main_btn_frame.setEnabled(False)
            txt = 'РАБОТА ПРЕРВАНА\nПО КОМАНДЕ\nОПЕРАТОРА'
            tag = 'warning'
            self.main_ui_msg(txt, tag)
            self.controller.work_interrupted_operator()
            self.log_msg_info_slot(f'PUSH BIG RED BUTTON')

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/btn_main_stop_clicked - {e}')

    def btn_ok_message_clicked(self):
        try:
            self.start_page()

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/btn_ok_message_clicked - {e}')

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
            self.log_msg_err_slot(f'ERROR in view/start_page - {e}')

    def open_win_operator(self):
        self.main_ui_disable()
        self.win_exec.show()

    def operator_select(self, name, rank):
        self.model.set_regs['operator']['name'] = name
        self.model.set_regs['operator']['rank'] = rank

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
        self.ui.main_stackedWidget.setCurrentIndex(1)
        self.ui.specif_choice_comboBox.addItems(self.win_amort.amorts.names)
        if len(self.win_amort.amorts.names) < 1:
            self.ui.specif_continue_btn.setEnabled(False)
        else:
            self.ui.specif_continue_btn.setEnabled(True)
            self.ui.specif_choice_comboBox.activated[int].connect(self.select_amort)
            self.select_amort(0)

        self.ui.specif_type_test_comboBox.activated[int].connect(self.select_type_test)
        self.select_type_test(0)

    def update_data_graph(self):
        try:
            temp = self.response.get('type_test')
            if temp == 'lab':
                pass

            elif temp == 'conv':
                self.update_conv_graph()

            elif temp == 'hand':
                self.win_set.update_graph_data()

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/update_data_graph - {e}')

    def select_type_test(self, ind):
        try:
            if ind == 0:
                self.model.set_regs['type_test'] = 'lab'
                self.ui.specif_speed_one_lineEdit.setGeometry(QRect(480, 260, 100, 40))
                self.ui.specif_data_label2_2.setVisible(False)
                self.ui.specif_data_label2_3.setVisible(False)
                self.ui.specif_speed_two_lineEdit.setVisible(False)
                self.ui.specif_speed_one_lineEdit.setReadOnly(False)

            elif ind == 1:
                self.model.set_regs['type_test'] = 'conv'
                self.ui.specif_speed_one_lineEdit.setGeometry(QRect(570, 260, 100, 40))
                self.ui.specif_data_label2_2.setVisible(True)
                self.ui.specif_data_label2_3.setVisible(True)
                self.ui.specif_speed_two_lineEdit.setVisible(True)
                self.ui.specif_speed_one_lineEdit.setReadOnly(True)
                self.ui.specif_speed_two_lineEdit.setReadOnly(True)

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/select_type_test - {e}')

    def select_amort(self, ind):
        try:
            self.model.set_regs['amort'] = self.win_amort.amorts.struct.amorts[ind]

            self.specif_ui_fill()

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/select_amort - {e}')

    def specif_ui_fill(self):
        try:
            obj = self.response.get('amort')
            self.ui.specif_name_lineEdit.setText(str(obj.name_a))
            self.ui.specif_min_length_lineEdit.setText(str(obj.min_length))
            self.ui.specif_max_length_lineEdit.setText(str(obj.max_length))
            self.ui.specif_hod_lineEdit.setText(str(obj.hod))
            self.ui.specif_speed_one_lineEdit.setText(str(obj.speed_one))
            self.ui.specif_speed_two_lineEdit.setText(str(obj.speed_two))
            self.ui.specif_min_comp_lineEdit.setText(str(obj.min_comp))
            self.ui.specif_max_comp_lineEdit.setText(str(obj.max_comp))
            self.ui.specif_min_recoil_lineEdit.setText(str(obj.min_recoil))
            self.ui.specif_max_recoil_lineEdit.setText(str(obj.max_recoil))
            self.ui.specif_max_temp_lineEdit.setText(str(obj.max_temper))

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/specif_ui_fill - {e}')

    def specif_ui_clear(self):
        try:
            self.ui.specif_name_lineEdit.clear()
            self.ui.specif_min_length_lineEdit.clear()
            self.ui.specif_max_length_lineEdit.clear()
            self.ui.specif_hod_lineEdit.clear()
            self.ui.specif_speed_one_lineEdit.clear()
            self.ui.specif_speed_two_lineEdit.clear()
            self.ui.specif_min_comp_lineEdit.clear()
            self.ui.specif_max_comp_lineEdit.clear()
            self.ui.specif_min_recoil_lineEdit.clear()
            self.ui.specif_max_recoil_lineEdit.clear()
            self.ui.specif_max_temp_lineEdit.clear()
            
        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/specif_ui_clear - {e}')

    def specif_continue_btn_click(self):
        try:
            name = self.response.get('operator')['name']
            rank = self.response.get('operator')['rank']
            if len(name) > 1 and len(rank) > 1:
                temp = self.response.get('type_test')
                if temp == 'lab':
                    self.test_lab()
                elif temp == 'conv':
                    self.test_conveyor()

            else:
                self.open_win_operator()

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/specif_continue_btn_click - {e}')

    def test_lab(self):
        try:
            self.ui.main_stackedWidget.setCurrentIndex(2)
            self.ui.main_STOP_btn.setEnabled(True)
            self.ui.main_btn_frame.setEnabled(False)
            self.ui.test_save_btn.setVisible(False)
            self.ui.test_repeat_btn.setVisible(False)
            self.ui.test_cancel_btn.setText('СТОП')

            amort = self.model.set_regs.get('amort')

            temp = float(self.ui.specif_speed_one_lineEdit.text())
            if temp != amort.speed_one:
                amort.speed_one = temp
                self.model.set_regs['amort'].speed_one = temp

            name = amort.name_a
            dimensions = f'{amort.min_length} - {amort.max_length}'
            hod = f'{amort.hod}'
            speed = f'{amort.speed_one}'
            limit_comp = f'{amort.min_comp} - {amort.max_comp}'
            limit_recoil = f'{amort.min_recoil} - {amort.max_recoil}'
            temper = f'{amort.max_temper}'

            txt_log = f'Start laboratory test --> name = {name}, dimensions = {dimensions}, hod = {hod}, ' \
                      f'speed = {speed}, limit_comp = {limit_comp}, ' \
                      f'limit_recoil = {limit_recoil}, max_temper = {temper}'

            self.log_msg_info_slot(txt_log)

            self.model.set_regs['traverse_referent'] = False

            self.controller.current_amort()

            self.controller.start_test_clicked()

            self.ui.test_data_name_lineEdit.setText(name)

            self.ui.test_data_limit_comp_lineEdit.setText(limit_comp)
            self.ui.test_data_limit_recoil_lineEdit.setText(limit_recoil)

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/test_page - {e}')

    def test_lab_cancel_click(self):
        try:
            temp = self.ui.test_cancel_btn.text()
            if temp == 'СТОП':
                self.log_msg_info_slot(f'Laboratory test stopped interrupted operator')
                self.controller.work_interrupted_operator()
                self.ui.test_save_btn.setVisible(True)
                self.ui.test_repeat_btn.setVisible(True)
                self.ui.main_btn_frame.setEnabled(True)
                self.ui.main_STOP_btn.setEnabled(False)
                self.ui.test_cancel_btn.setText('НАЗАД')

            elif temp == 'НАЗАД':
                self.specif_page()

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/test_cancel_click - {e}')

    def test_conveyor(self):
        try:
            self.ui.main_btn_frame.setEnabled(False)
            self.ui.main_STOP_btn.setEnabled(True)
            # self.ui.main_stackedWidget.setCurrentIndex(3)

            amort = self.response.get('amort')
            name = amort.name_a
            dimensions = f'{amort.min_length} - {amort.max_length}'
            hod = f'{amort.hod}'
            speed = f'one = {amort.speed_one} and two = {amort.speed_two}'
            limit_comp = f'{amort.min_comp} - {amort.max_comp}'
            limit_recoil = f'{amort.min_recoil} - {amort.max_recoil}'
            temper = f'{amort.max_temper}'

            txt_log = f'Start conveyor test --> name = {name}, dimensions = {dimensions}, hod = {hod}, ' \
                      f'speed = {speed}, limit_comp = {limit_comp}, ' \
                      f'limit_recoil = {limit_recoil}, max_temper = {temper}'

            self.log_msg_info_slot(txt_log)

            self.model.set_regs['traverse_referent'] = False

            self.controller.current_amort()
            self.controller.start_test_clicked()

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/test_conveyor - {e}')

    def conv_test_win(self):
        try:
            self.ui.main_stackedWidget.setCurrentIndex(3)

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/conv_test_win - {e}')

    def init_conv_graph(self):
        try:
            self.ui.conv_GraphWidget.showGrid(True, True)
            self.ui.conv_GraphWidget.setBackground('w')

            self.pen_test_conv = pg.mkPen(color='black', width=3)
            self.data_line_test_conv = self.ui.conv_GraphWidget.plot([], [], pen=self.pen_test_conv)

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/init_conv_graph - {e}')

    def update_conv_graph(self):
        try:
            coord_x = self.response.get('move_graph')
            coord_y = self.response.get('force_graph')

            self.data_line_test_conv.setData(coord_x, coord_y)

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/update_conv_graph - {e}')

    # def color_led_lamp(self):
    #     try:
    #         if self.model.set_regs.get('red_light') == '1':
    #             self.ui.red_signal.setStyleSheet('background-color: rgb(255, 0, 0);')
    #         else:
    #             self.ui.red_signal.setStyleSheet('background-color: rgb(255, 255, 255);')
    #
    #         if self.model.set_regs.get('green_light') == '1':
    #             self.ui.green_signal.setStyleSheet('background-color: rgb(0, 255, 0);')
    #         else:
    #             self.ui.green_signal.setStyleSheet('background-color: rgb(255, 255, 255);')
    #
    #     except Exception as e:
    #         self.log_msg_err_slot(f'ERROR in view/color_led_lamp - {e}')

    def test_conv_cancel_click(self):
        self.log_msg_info_slot(f'Conveyor test stopped interrupted operator')
        self.controller.work_interrupted_operator()
        self.specif_page()
        self.ui.main_btn_frame.setEnabled(True)
        self.ui.main_STOP_btn.setEnabled(False)

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
