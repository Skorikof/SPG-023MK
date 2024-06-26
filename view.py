from mainui import Ui_MainWindow
from executors_win import ExecWin
from amorts_win import AmortWin
from archive_win import ArchiveWin
import pyqtgraph as pg
from PyQt5.QtWidgets import QMainWindow, QFrame
from PyQt5.QtCore import QRect
from PyQt5.QtGui import QIcon
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
        self.amort = None
        self.pen_test_lab = None
        self.data_line_test_lab = None
        self.pen_test_conv = None
        self.data_line_test_conv = None

        self.model = model
        self.controller = controller
        self.win_set = win_set

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.win_exec = ExecWin()
        self.win_exec.setWindowIcon(QIcon('icon/user.png'))
        self.win_amort = AmortWin()
        self.win_amort.setWindowIcon(QIcon('icon/shock-absorber.png'))
        self.win_archive = ArchiveWin()
        self.win_archive.setWindowIcon(QIcon('icon/archive.png'))

        self._create_statusbar_ui()

        self.start_param_view()

    def closeEvent(self, event):
        self.model.reader_exit()
        self.model.disconnect_client()
        self.model.threadpool.waitForDone()
        self.close()

    def _create_statusbar_ui(self):
        self.statusbar = self.statusBar()
        #
        # self.lbl_info_msg = QLabel("Инф:")
        # self.lbl_info_msg.setStyleSheet('border: 0);')
        # self.lbl_info_msg.setFont(QFont('Calibri', 14))
        #
        # self.statusBar().reformat()
        # self.statusBar().setStyleSheet('border: 0; background-color: #FFF8DC;')
        # self.statusBar().setStyleSheet("QStatusBar::item {border: none;}")
        #
        # self.statusBar().addPermanentWidget(VLine())  # <---
        # self.statusBar().addPermanentWidget(self.lbl_info_msg, stretch=1)

    def status_bar_ui(self, txt_bar):
        try:
            self.ui.statusbar.showMessage(txt_bar)
            # self.lbl_info_msg.setText(txt_bar)

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/status_bar_ui - {e}')

    def update_data_on_left_bar(self):
        try:
            self.ui.force_le.setText(f'{self.response.get("force")}')
            self.ui.move_motor_le.setText(f'{self.response.get("move")}')
            self.ui.move_traverse_le.setText(f'{self.response.get("traverse_move")}')
            self.ui.temperature_le.setText(f'{self.response.get("temperature")}')

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/update_data_on_left_bar - {e}')

    def start_param_view(self):
        self.init_buttons()
        self.init_signals()
        self.start_page()
        self.init_lab_graph()
        self.init_conv_graph()

    def init_signals(self):
        self.model.signals.connect_ctrl.connect(self.start_page)
        self.model.signals.stbar_msg.connect(self.status_bar_ui)
        self.model.signals.read_finish.connect(self.update_data_view)
        self.model.signals.update_graph_settings.connect(self.update_data_graph)

        self.controller.signals.control_msg.connect(self.controller_msg_slot)
        self.controller.signals.traverse_referent.connect(self.msg_traverse_referent)
        self.controller.signals.traverse_position.connect(self.msg_traverse_position)
        self.controller.signals.wait_yellow_btn.connect(self.msg_yellow_btn)
        self.controller.signals.conv_win_test.connect(self.conv_test_win)
        self.controller.signals.conv_lamp.connect(self.conv_test_lamp)
        self.controller.signals.lab_win_test.connect(self.lab_test_win)
        self.controller.signals.cancel_test.connect(self.cancel_test_slot)

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
        self.ui.main_STOP_btn.clicked.connect(self.btn_main_stop_clicked)
        self.ui.ok_message_btn.clicked.connect(self.btn_ok_message_clicked)
        self.ui.main_operator_btn.clicked.connect(self.open_win_operator)
        self.ui.main_test_btn.clicked.connect(self.specif_page)
        self.ui.main_hand_debug_btn.clicked.connect(self.open_win_settings)
        self.ui.main_archive_btn.clicked.connect(self.open_win_archive)
        self.ui.main_amorts_btn.clicked.connect(self.open_win_amort)

        self.ui.specif_continue_btn.clicked.connect(self.specif_continue_btn_click)
        self.ui.test_cancel_btn.clicked.connect(self.cancel_test_clicked)
        self.ui.test_conv_cancel_btn.clicked.connect(self.cancel_test_clicked)
        self.ui.test_repeat_btn.clicked.connect(self.test_lab)
        self.ui.btn_speed_change.clicked.connect(self.change_speed_test)

    def update_data_view(self, response):
        try:
            self.response = {**self.response, **response}

            self.update_data_on_left_bar()

            temp = self.response.get('type_test')

            if temp == 'lab' or temp == 'conv':
                self.controller.update_data_ctrl(response)

            elif temp == 'hand':
                self.win_set.update_data_win_set(response)

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
                txt = 'ПОТЕРЯНО\nУПРАВЛЕНИЕ'

            elif msg == 'excess_force':
                txt = 'ПРЕВЫШЕНИЕ\nУСИЛИЯ'

            elif msg == 'excess_temperature':
                txt = 'ПРЕВЫШЕНА\nМАКСИМАЛЬНО\nДОПУСТИМАЯ\nТЕМПЕРАТУРА'

            elif msg == 'safety_fence':
                txt = 'ОТКРЫТО\nЗАЩИТНОЕ\nОГРАЖДЕНИЕ'

            elif msg == 'alarm_traverse_up':
                txt = 'ТРАВЕРСА\nВ ВЕРХНЕМ\nПОЛОЖЕНИИ'

            elif msg == 'alarm_traverse_down':
                txt = 'ТРАВЕРСА\nВ НИЖНЕМ\nПОЛОЖЕНИИ'
            else:
                print(msg)

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
            txt = 'НАЖМИТЕ\nЖЁЛТУЮ\nКНОПКУ\nДЛЯ ЗАПУСКА\nИСПЫТАНИЯ'
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
                self.main_btn_disable()
            self.ui.main_stackedWidget.setCurrentIndex(0)
            self.ui.stack_start_label.setText(txt)
            self.ui.stack_start_label.setStyleSheet("background-color: " + backcolor + ";\n" +
                                                    "color: " + color + ";")

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/main_ui_msg - {e}')

    def btn_main_stop_clicked(self):
        try:
            txt = 'РАБОТА ПРЕРВАНА\nПО КОМАНДЕ\nОПЕРАТОРА'
            tag = 'warning'
            self.main_ui_msg(txt, tag)
            self.controller.work_interrupted_operator()
            self.log_msg_info_slot(f'PUSH BIG RED BUTTON')

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/btn_main_stop_clicked - {e}')

    def btn_ok_message_clicked(self):
        try:
            self.controller.lamp_all_switch_off()
            self.main_btn_enable()
            self.start_page()

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/btn_ok_message_clicked - {e}')

    def main_ui_enable(self):
        self.ui.main_stackedWidget.setEnabled(True)
        self.ui.main_btn_frame.setEnabled(True)

    def main_ui_disable(self):
        self.ui.main_stackedWidget.setEnabled(False)
        self.ui.main_btn_frame.setEnabled(False)

    def main_btn_enable(self):
        self.ui.main_operator_btn.setEnabled(True)
        self.ui.main_test_btn.setEnabled(True)
        self.ui.main_archive_btn.setEnabled(True)
        self.ui.main_amorts_btn.setEnabled(True)
        self.ui.main_hand_debug_btn.setEnabled(True)

    def main_btn_disable(self):
        self.ui.main_operator_btn.setEnabled(False)
        self.ui.main_test_btn.setEnabled(False)
        self.ui.main_archive_btn.setEnabled(False)
        self.ui.main_amorts_btn.setEnabled(False)
        self.ui.main_hand_debug_btn.setEnabled(False)

    def main_stop_enable(self):
        self.ui.main_STOP_btn.setEnabled(True)

    def main_stop_disable(self):
        self.ui.main_STOP_btn.setEnabled(False)

    def start_page(self):
        try:
            self.main_stop_disable()
            if self.model.client:
                txt = "Здравствуйте.\nДобро пожаловать\nв\nпрограмму.\nВыберите необходимый\nпункт меню."
                tag = 'info'
                self.main_ui_msg(txt, tag)
                self.main_ui_enable()

            else:
                txt = "ОТСУТСТВУЕТ\nПОДКЛЮЧЕНИЕ\nК\nКОНТРОЛЛЕРУ."
                tag = 'attention'
                self.main_ui_msg(txt, tag)
                self.main_ui_disable()
                self.model.start_param_model()

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/start_page - {e}')

    def open_win_operator(self):
        self.main_ui_disable()
        self.win_exec.show()

    def operator_select(self, name, rank):
        self.model.set_regs['operator']['name'] = name
        self.model.set_regs['operator']['rank'] = rank

        self.ui.operator_name_le.setText(f'{name}')
        self.ui.operator_rank_le.setText(f'{rank}')

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
            self.ui.specif_choice_comboBox.setCurrentIndex(0)
            self.ui.specif_choice_comboBox.activated[int].connect(self.select_amort)
            self.select_amort(0)

        self.ui.specif_type_test_comboBox.setCurrentIndex(0)
        self.ui.specif_type_test_comboBox.activated[int].connect(self.select_type_test)
        self.select_type_test(0)

    def update_data_graph(self):
        try:
            temp = self.response.get('type_test')
            if temp == 'lab':
                self.update_lab_graph()

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
            self.amort = self.win_amort.amorts.struct.amorts[ind]

            self.model.current_amort_model(self.win_amort.amorts.struct.amorts[ind])
            self.controller.current_amort_ctrl(self.win_amort.amorts.struct.amorts[ind])

            self.specif_ui_fill(self.win_amort.amorts.struct.amorts[ind])

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/select_amort - {e}')

    def specif_ui_fill(self, obj):
        try:
            self.ui.specif_name_lineEdit.setText(str(obj.name))
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
            self.ui.specif_choice_comboBox.clear()
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
            self.main_stop_enable()
            self.main_btn_disable()
            self.ui.test_save_btn.setVisible(False)
            self.ui.test_repeat_btn.setVisible(False)
            self.ui.test_cancel_btn.setText('СТОП')

            temp = float(self.ui.specif_speed_one_lineEdit.text())
            if temp != self.amort.speed_one:
                self.amort.speed_one = temp

            name = self.amort.name
            dimensions = f'{self.amort.min_length} - {self.amort.max_length}'
            hod = f'{self.amort.hod}'
            speed = f'{self.amort.speed_one}'
            limit_comp = f'{self.amort.min_comp} - {self.amort.max_comp}'
            limit_recoil = f'{self.amort.min_recoil} - {self.amort.max_recoil}'
            temper = f'{self.amort.max_temper}'

            txt_log = f'Start laboratory test --> name = {name}, dimensions = {dimensions}, hod = {hod}, ' \
                      f'speed = {speed}, limit_comp = {limit_comp}, ' \
                      f'limit_recoil = {limit_recoil}, max_temper = {temper}'

            self.log_msg_info_slot(txt_log)

            self.controller.start_test_clicked()

            self.ui.test_data_name_lineEdit.setText(name)

            self.ui.test_data_limit_comp_lineEdit.setText(limit_comp)
            self.ui.test_data_limit_recoil_lineEdit.setText(limit_recoil)
            self.ui.test_data_speed_lineEdit.setText(str(speed))

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/test_page - {e}')

    def lab_test_win(self):
        try:
            self.ui.main_stackedWidget.setCurrentIndex(2)

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/lab_test_win - {e}')

    def init_lab_graph(self):
        try:
            self.ui.lab_GraphWidget.showGrid(True, True)
            self.ui.lab_GraphWidget.setBackground('w')

            self.pen_test_lab = pg.mkPen(color='black', width=3)
            self.data_line_test_lab = self.ui.lab_GraphWidget.plot([], [], pen=self.pen_test_conv)

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/init_lab_graph - {e}')

    def update_lab_graph(self):
        try:
            coord_x = self.response.get('move_graph')
            coord_y = self.response.get('force_graph')

            self.data_line_test_lab.setData(coord_x, coord_y)

            self.update_lab_data()

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/update_lab_graph - {e}')

    def update_lab_data(self):
        try:
            max_comp = self.response.get('max_comp')
            max_recoil = self.response.get('max_recoil')
            temper = self.response.get('temperature')
            max_temper = self.response.get('max_temper')

            self.ui.test_data_max_comp_lineEdit.setText(str(max_comp))
            self.ui.test_data_max_recoil_lineEdit.setText(str(max_recoil))
            self.ui.test_data_now_temp_lineEdit.setText(str(temper))
            self.ui.test_data_max_temp_lineEdit.setText(str(max_temper))

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/update_lab_data - {e}')

    def change_speed_test(self):
        try:
            value = self.ui.test_data_speed_lineEdit.text()
            value = float(value.replace(',', '.'))
            speed = self.amort.speed_one

            if value == speed:
                pass
            else:
                speed = self.model.calculate_freq(float(value))
                self.model.write_frequency(1, speed)

                txt_log = f'Change speed in lab test on --> {speed}'

                self.log_msg_info_slot(txt_log)

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/change_speed_test - {e}')

    def test_conveyor(self):
        try:
            self.main_btn_disable()
            self.main_stop_enable()

            name = self.amort.name
            dimensions = f'{self.amort.min_length} - {self.amort.max_length}'
            hod = f'{self.amort.hod}'
            speed = f'one = {self.amort.speed_one} and two = {self.amort.speed_two}'
            limit_comp = f'{self.amort.min_comp} - {self.amort.max_comp}'
            limit_recoil = f'{self.amort.min_recoil} - {self.amort.max_recoil}'
            temper = f'{self.amort.max_temper}'

            txt_log = f'Start conveyor test --> name = {name}, dimensions = {dimensions}, hod = {hod}, ' \
                      f'speed = {speed}, limit_comp = {limit_comp}, ' \
                      f'limit_recoil = {limit_recoil}, max_temper = {temper}'

            self.log_msg_info_slot(txt_log)

            self.controller.start_test_clicked()

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/test_conveyor - {e}')

    def conv_test_win(self):
        try:
            self.ui.main_stackedWidget.setCurrentIndex(3)

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/conv_test_win - {e}')

    def conv_test_lamp(self, command):
        try:
            border = "border-color: rgb(0, 0, 0);"
            if command == 'all_on':
                self.ui.red_signal.setStyleSheet("background-color: rgb(255, 0, 0);\n" + border)
                self.ui.green_signal.setStyleSheet("background-color: rgb(0, 255, 0);\n" + border)

            elif command == 'all_off':
                self.ui.red_signal.setStyleSheet("background-color: rgb(255, 255, 255);\n" + border)
                self.ui.green_signal.setStyleSheet("background-color: rgb(255, 255, 255);\n" + border)

            elif command == 'red_on':
                self.ui.red_signal.setStyleSheet("background-color: rgb(255, 0, 0);\n" + border)
                self.ui.green_signal.setStyleSheet("background-color: rgb(255, 255, 255);\n" + border)

            elif command == 'green_on':
                self.ui.red_signal.setStyleSheet("background-color: rgb(255, 255, 255);\n" + border)
                self.ui.green_signal.setStyleSheet("background-color: rgb(0, 255, 0);\n" + border)

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/conv_test_lamp - {e}')

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

    def color_led_lamp(self):
        try:
            if self.model.set_regs.get('red_light') is True:
                self.ui.red_signal.setStyleSheet('background-color: rgb(255, 0, 0);')
            else:
                self.ui.red_signal.setStyleSheet('background-color: rgb(255, 255, 255);')

            if self.model.set_regs.get('green_light') is True:
                self.ui.green_signal.setStyleSheet('background-color: rgb(0, 255, 0);')
            else:
                self.ui.green_signal.setStyleSheet('background-color: rgb(255, 255, 255);')

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/color_led_lamp - {e}')

    def cancel_test_clicked(self):
        try:
            self.controller.stop_test_clicked()

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/cancel_test_clicked - {e}')

    def cancel_test_slot(self):
        try:
            self.main_stop_disable()
            self.main_btn_enable()
            type_test = self.response.get('type_test')
            if type_test == 'conv':

                self.specif_page()

            elif type_test == 'lab':
                # temp = self.ui.test_cancel_btn.text()
                # if temp == 'СТОП':
                self.ui.test_save_btn.setVisible(True)
                self.ui.test_repeat_btn.setVisible(True)
                # self.ui.test_cancel_btn.setText('НАЗАД')

                # elif temp == 'НАЗАД':
                #     self.specif_page()

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/cancel_test_slot - {e}')

    def open_win_archive(self):
        self.main_ui_disable()
        self.win_archive.show()
        self.win_archive.archive_update()

    def close_win_archive(self):
        self.main_ui_enable()
        self.win_archive.hide()

    def open_win_settings(self):
        self.main_ui_disable()
        self.model.set_regs['type_test'] = 'hand'
        self.win_set.show()
        self.win_set.start_param_win_set()

    def close_win_settings(self):
        self.model.set_regs['type_test'] = None
        self.main_ui_enable()
        self.win_set.hide()

    def save_btn_clicked(self):
        try:
            ser = self.ui.test_data_serial_lineEdit.text()
            if ser == '':
                pass

            else:
                self.save_data_in_archive()

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/save_btn_clicked - {e}')

    def save_data_in_archive(self):
        try:
            print(f'Save data in archive')

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/save_data_in_archive - {e}')
