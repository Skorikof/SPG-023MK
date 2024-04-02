from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QObject, pyqtSignal, QSignalMapper, pyqtSlot
from settings_ui import Ui_SettingsWindow
from graph_win import GraphUi
import time


class WinSignals(QObject):
    closed = pyqtSignal()


class SetWindow(QMainWindow):
    signals = WinSignals()

    def __init__(self, model):
        super(SetWindow, self).__init__()
        try:
            self.model = model
            self.ui = Ui_SettingsWindow()
            self.ui.setupUi(self)
            self.hide()
            self.graph_ui = GraphUi(self.model)
            self.flag_graph = None

        except Exception as e:
            txt_log = 'ERROR in settings_window/__init__ - {}'.format(e)
            self.model.status_bar_msg(txt_log)
            self.model.save_log('error', str(e))

    def smap_line_edit(self):
        smap = QSignalMapper(self)

        self.ui.lineEdit_F_alarm.clicked.connect(smap.map)
        smap.setMapping(self.ui.lineEdit_F_alarm, 1)

        smap.mapped.connect(self.on_click_lineedit)

    @pyqtSlot(int)
    def on_click_lineedit(self, index):
        print(index)
        if index == 1:
            self.model.reader_stop()

    def closeEvent(self, event):
        self.model.reader_stop()
        self.read_stop_ui()
        self.model.disconnect_client()
        self.signals.closed.emit()

    def start_param(self):
        self._create_statusbar_set()
        self.init_buttons()
        self.init_signals()
        self.smap_line_edit()
        self.disconnect_ui()

    def _create_statusbar_set(self):
        self.statusbar = self.statusBar()
        self.statusbar.showMessage('Окно управления стенда в ручную')

    def statusbar_set_ui(self, txt_bar):
        try:
            self.statusbar.showMessage(txt_bar)

        except Exception as e:
            txt_log = 'ERROR in settings_window/statusbar_set_ui - {}'.format(e)
            self.model.status_bar_msg(txt_log)
            self.model.save_log('error', str(e))

    def init_buttons(self):
        self.ui.btn_exit.clicked.connect(self.close)
        self.ui.btn_connect.clicked.connect(self.do_connect)
        self.ui.btn_read.clicked.connect(self.read_controller)
        self.ui.rbtn_traverse.toggled.connect(self.select_engine)
        self.ui.rbtn_traverse.adr_freq = 2
        self.ui.rbtn_engine.toggled.connect(self.select_engine)
        self.ui.rbtn_engine.adr_freq = 1
        self.ui.btn_save_freq.clicked.connect(self.write_frequency_set)
        self.ui.btn_motor_main_start.clicked.connect(self.click_btn_motor_start)
        self.ui.btn_motor_main_stop.clicked.connect(self.click_btn_motor_main_stop)
        self.ui.btn_motor_up.clicked.connect(self.click_btn_motor_up)
        self.ui.btn_motor_down.clicked.connect(self.click_btn_motor_down)
        self.ui.btn_motor_traverse_stop.clicked.connect(self.click_btn_motor_traverse_stop)
        self.ui.btn_cycle_F.clicked.connect(self.btn_set_doclick)
        self.ui.btn_no_control.clicked.connect(self.btn_set_doclick)
        self.ui.btn_max_F.clicked.connect(self.btn_set_doclick)
        self.ui.btn_green_light.clicked.connect(self.btn_set_doclick)
        self.ui.btn_red_light.clicked.connect(self.btn_set_doclick)

        self.ui.lineEdit_F_alarm.returnPressed.connect(self.write_alarm_force)

    def init_signals(self):
        self.model.signals.read_finish.connect(self.update_win)

    def do_connect(self):
        try:
            temp = self.ui.btn_connect.text()
            if temp == 'ПОДКЛЮЧИТЬСЯ':
                self.model.init_connect()
                con = self.model.set_connect.get('connect')
                if con:
                    self.model.init_reader()
                    self.connect_ui()
            elif temp == 'ОТКЛЮЧИТЬСЯ':
                self.model.disconnect_client()
                self.disconnect_ui()
        except Exception as e:
            txt_log = 'ERROR in settings_window/do_connect - {}'.format(e)
            self.statusbar.showMessage(txt_log)
            self.model.save_log('error', str(e))

    def connect_ui(self):
        self.ui.btn_connect.setText('ОТКЛЮЧИТЬСЯ')
        self.ui.btn_read.setEnabled(True)
        self.ui.btn_motor_main_start.setEnabled(True)
        self.ui.btn_motor_main_stop.setEnabled(True)
        self.ui.btn_motor_up.setEnabled(True)
        self.ui.btn_motor_down.setEnabled(True)
        self.ui.btn_motor_traverse_stop.setEnabled(True)
        self.ui.btn_save_freq.setEnabled(True)
        self.ui.btn_cycle_F.setEnabled(True)
        self.ui.btn_no_control.setEnabled(True)
        self.ui.btn_max_F.setEnabled(True)
        self.ui.btn_green_light.setEnabled(True)
        self.ui.btn_red_light.setEnabled(True)
        txt_log = 'Контроллер подключен'
        self.statusbar.showMessage(txt_log)

    def disconnect_ui(self):
        self.ui.btn_connect.setText('ПОДКЛЮЧИТЬСЯ')
        self.ui.btn_read.setEnabled(False)
        self.ui.btn_motor_main_start.setEnabled(False)
        self.ui.btn_motor_main_stop.setEnabled(False)
        self.ui.btn_motor_up.setEnabled(False)
        self.ui.btn_motor_down.setEnabled(False)
        self.ui.btn_motor_traverse_stop.setEnabled(False)
        self.ui.btn_save_freq.setEnabled(False)
        self.ui.btn_cycle_F.setEnabled(False)
        self.ui.btn_no_control.setEnabled(False)
        self.ui.btn_max_F.setEnabled(False)
        self.ui.btn_green_light.setEnabled(False)
        self.ui.btn_red_light.setEnabled(False)
        txt_log = 'Контроллер отключен'
        self.statusbar.showMessage(txt_log)

    def read_controller(self):
        try:
            temp = self.ui.btn_read.text()
            if temp == 'ЧИТАТЬ':
                self.model.reader_start()
                self.read_start_ui()
            elif temp == 'ОСТАНОВИТЬ':
                self.model.reader_stop()
                self.read_stop_ui()

        except Exception as e:
            txt_log = 'ERROR in settings_window/reda_controller - {}'.format(e)
            self.statusbar.showMessage(txt_log)
            self.model.save_log('error', str(e))

    def read_start_ui(self):
        self.ui.btn_read.setText('ОСТАНОВИТЬ')
        self.ui.btn_connect.setEnabled(False)

    def read_stop_ui(self):
        self.ui.btn_read.setText('ЧИТАТЬ')
        self.ui.btn_connect.setEnabled(True)

    def select_engine(self):
        rbtn = self.sender()
        if rbtn.isChecked():
            self.model.set_regs['adr_freq'] = int(rbtn.adr_freq)

    def write_frequency_set(self):
        try:
            value = self.ui.lineEdit_freq.text()
            if not value:
                pass
            else:
                self.model.set_regs['frequency'] = int(value) * 100
                self.model.write_frequency()

        except Exception as e:
            txt_log = 'ERROR in settings_window/write_frequency - {}'.format(e)
            self.statusbar.showMessage(txt_log)
            self.model.save_log('error', str(e))

    def click_btn_motor_up(self):
        self.model.set_regs['adr_freq'] = 2
        self.model.motor_up()

    def click_btn_motor_down(self):
        self.model.set_regs['adr_freq'] = 2
        self.model.motor_down()

    def click_btn_motor_start(self):
        self.model.set_regs['adr_freq'] = 1
        self.model.motor_up()

    def click_btn_motor_main_stop(self):
        self.model.set_regs['adr_freq'] = 1
        self.model.motor_stop()

    def click_btn_motor_traverse_stop(self):
        self.model.set_regs['adr_freq'] = 2
        self.model.motor_stop()

    def write_alarm_force(self):
        try:
            self.model.reader_stop()
            value = float(self.ui.lineEdit_F_alarm.text())
            self.model.set_regs['force_alarm'] = value

            self.model.write_emergency_force()
            time.sleep(0.02)
            self.model.reader_start()

        except Exception as e:
            txt_log = 'ERROR in settings_window/write_alarm_force - {}'.format(e)
            self.statusbar.showMessage(txt_log)
            self.model.save_log('error', str(e))

    def btn_set_doclick(self):
        try:
            btn = self.sender()
            index = 0
            flag = False
            temp_list = [x for x in self.model.set_regs.get('list_state')]

            if btn.objectName() == 'btn_cycle_F':
                index = 0
                flag = True
            elif btn.objectName() == 'btn_red_light':
                index = 1
                flag = True
            elif btn.objectName() == 'btn_green_light':
                index = 2
                flag = True
            elif btn.objectName() == 'btn_no_control':
                index = 3
                flag = False
            elif btn.objectName() == 'btn_max_F':
                index = 4
                flag = False
            else:
                pass

            if flag:
                value = temp_list[index]
                if value == 0:
                    bool_val = 1
                    btn.setChecked(True)

                else:
                    bool_val = 0
                    btn.setChecked(False)
                self.model.change_list_state(index, bool_val)

            else:
                bool_val = 1
                btn.setChecked(False)
                self.model.change_list_state(index, bool_val)

        except Exception as e:
            txt_log = 'ERROR in settings_window/btn_set_doclick - {}'.format(e)
            self.statusbar.showMessage(txt_log)
            self.model.save_log('error', str(e))

    def update_win(self):
        self.ui.lcdTime.display(self.model.set_regs.get('counter_time'))
        self.ui.lcdF.display(self.model.set_regs.get('force_now'))
        self.ui.lcdH.display(self.model.set_regs.get('amort_move'))
        self.ui.lcdH_T.display(self.model.set_regs.get('traverse_move'))
        self.ui.lcdTemp.display(self.model.set_regs.get('temperature'))
        self.ui.lineEdit_F_alarm.setText(str(self.model.set_regs.get('force_alarm')))
        self.update_color_switch(self.model.set_regs)

    def update_color_switch(self, state):
        try:
            self.ui.fram_cycle_F.setStyleSheet(self.set_color_fram(state.get('cycle_force')))
            self.ui.fram_no_control.setStyleSheet(self.set_color_fram(state.get('lost_control')))
            self.ui.fram_max_F.setStyleSheet(self.set_color_fram(state.get('excess_force')))
            self.ui.fram_safety_fence.setStyleSheet(self.set_color_fram(state.get('safety_fence'), True))
            self.ui.fram_condition_FC.setStyleSheet(self.set_color_fram(state.get('state_freq')))
            self.ui.fram_sensor_F.setStyleSheet(self.set_color_fram(state.get('state_force')))
            self.ui.fram_block_traverse_1.setStyleSheet(self.set_color_fram(state.get('traverse_block_1'), True))
            self.ui.fram_block_traverse_2.setStyleSheet(self.set_color_fram(state.get('traverse_block_2'), True))
            self.ui.fram_down_point.setStyleSheet(self.set_color_fram(state.get('lowest_position')))
            self.ui.fram_down__alarm_point.setStyleSheet(self.set_color_fram(state.get('alarm_lowest_position'), True))
            self.ui.fram_up_point.setStyleSheet(self.set_color_fram(state.get('highest_position')))
            self.ui.fram_up_alarm_point.setStyleSheet(self.set_color_fram(state.get('alarm_highest_position'), True))
            self.ui.fram_green_light.setStyleSheet(self.set_color_fram(state.get('green_light')))
            self.ui.fram_red_light.setStyleSheet(self.set_color_fram(state.get('red_light')))

        except Exception as e:
            txt_log = 'ERROR in settings_window/update_color_switch - {}'.format(e)
            self.statusbar.showMessage(txt_log)
            self.model.save_log('error', str(e))

    def set_color_fram(self, bit, rev=False):
        try:
            if rev:
                if bit == '0':
                    bit = '1'
                else:
                    bit = '0'
            color_gray = "background-color: rgb(93, 93, 93);\n"
            color_green = "background-color: rgb(0, 255, 0);\n"
            if bit == '0':
                return color_gray + "border-color: rgb(0, 0, 0);"
            elif bit == '1':
                return color_green + "border-color: rgb(0, 0, 0);"

        except Exception as e:
            txt_log = 'ERROR in settings_window/set_color_fram - {}'.format(e)
            self.statusbar.showMessage(txt_log)
            self.model.save_log('error', str(e))
