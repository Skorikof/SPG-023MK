from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QObject, pyqtSignal, QSignalMapper, pyqtSlot
from settings_ui import Ui_SettingsWindow
from graph_win import GraphUi
import time


class WinSignals(QObject):
    closed = pyqtSignal()
    log_err = pyqtSignal(str)


class SetWindow(QMainWindow):
    signals = WinSignals()

    def __init__(self, model):
        super(SetWindow, self).__init__()
        try:
            self.response = {}
            self.model = model
            self.ui = Ui_SettingsWindow()
            self.ui.setupUi(self)
            self.hide()
            self.graph_ui = GraphUi(self.model)
            self.flag_graph = None

        except Exception as e:
            self.signals.log_err.emit(f'ERROR in settings_window/__init__ - {e}')

    def smap_line_edit(self):
        smap = QSignalMapper(self)

        self.ui.lineEdit_F_alarm.clicked.connect(smap.map)
        smap.setMapping(self.ui.lineEdit_F_alarm, 1)

        smap.mapped.connect(self.on_click_lineedit)

    @pyqtSlot(int)
    def on_click_lineedit(self, index):
        if index == 1:
            self.model.reader_stop()

    def closeEvent(self, event):
        self.signals.closed.emit()

    def start_param_win_set(self):
        self._create_statusbar_set()
        self.init_buttons()
        self.smap_line_edit()

    def _create_statusbar_set(self):
        self.statusbar = self.statusBar()
        self.statusbar.showMessage('Окно управления стенда в ручную')

    def statusbar_set_ui(self, txt_bar):
        try:
            self.statusbar.showMessage(txt_bar)
            self.signals.log_err.emit(txt_bar)

        except Exception as e:
            self.signals.log_err.emit(f'ERROR in settings_window/statusbar_set_ui - {e}')

    def init_buttons(self):
        self.ui.btn_exit.clicked.connect(self.close)
        self.ui.btn_test.clicked.connect(self.btn_test_clicked)
        self.ui.btn_hod.clicked.connect(self.write_hod)
        self.ui.btn_speed_main.clicked.connect(self.write_frequency_set)
        self.ui.btn_freq_trverse.clicked.connect(self.write_frequency_set)

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

        self.ui.btn_connect.setVisible(False)
        self.ui.btn_read.setVisible(False)

    def update_data_win_set(self, response):
        try:
            self.response = {**self.response, **response}

            self.update_win()

        except Exception as e:
            self.statusbar_set_ui(f'ERROR in settings_window/update_data - {e}')

    def do_connect(self):
        try:
            if self.model.client:
                self.connect_ui()
            else:
                self.disconnect_ui()

        except Exception as e:
            self.statusbar_set_ui(f'ERROR in settings_window/do_connect - {e}')

    def connect_ui(self):
        self.ui.btn_connect.setText('ОТКЛЮЧИТЬСЯ')
        self.ui.btn_read.setEnabled(True)
        self.ui.btn_motor_main_start.setEnabled(True)
        self.ui.btn_motor_main_stop.setEnabled(True)
        self.ui.btn_motor_up.setEnabled(True)
        self.ui.btn_motor_down.setEnabled(True)
        self.ui.btn_motor_traverse_stop.setEnabled(True)
        self.ui.btn_hod.setEnabled(True)
        self.ui.btn_speed_main.setEnabled(True)
        self.ui.btn_freq_trverse.setEnabled(True)
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
        self.ui.btn_hod.setEnabled(False)
        self.ui.btn_speed_main.setEnabled(False)
        self.ui.btn_freq_trverse.setEnabled(False)
        self.ui.btn_cycle_F.setEnabled(False)
        self.ui.btn_no_control.setEnabled(False)
        self.ui.btn_max_F.setEnabled(False)
        self.ui.btn_green_light.setEnabled(False)
        self.ui.btn_red_light.setEnabled(False)
        txt_log = 'Контроллер отключен'
        self.statusbar.showMessage(txt_log)

    def write_hod(self):
        try:
            temp = int(self.ui.lineEdit_hod.text())
            if not temp:
                pass
            else:
                self.model.set_regs['hod'] = temp

        except Exception as e:
            self.statusbar_set_ui(f'ERROR in settings_window/write_hod - {e}')

    def write_frequency_set(self):
        try:
            btn = self.sender()
            if btn.objectName() == 'btn_speed_main':
                value = self.ui.lineEdit_speed_main.text()
                if not value:
                    pass
                else:
                    value = value.replace(',', '.')
                    speed = self.model.calculate_freq(float(value))
                    self.model.write_frequency(1, speed)

            elif btn.objectName() == 'btn_freq_trverse':
                value = int(self.ui.lineEdit_freq_traverse.text())
                if not value:
                    pass
                else:
                    self.model.write_frequency(2, value * 100)

        except Exception as e:
            self.statusbar_set_ui(f'ERROR in settings_window/write_frequency - {e}')

    def click_btn_motor_up(self):
        self.model.motor_up(2)

    def click_btn_motor_down(self):
        self.model.motor_down(2)

    def click_btn_motor_start(self):
        self.model.motor_up(1)

    def click_btn_motor_main_stop(self):
        self.model.motor_stop(1)

    def click_btn_motor_traverse_stop(self):
        self.model.motor_stop(2)

    def write_alarm_force(self):
        try:
            value = float(self.ui.lineEdit_F_alarm.text())

            self.model.write_emergency_force(value)
            time.sleep(0.02)
            self.model.reader_start()

        except Exception as e:
            self.statusbar_set_ui(f'ERROR in settings_window/write_alarm_force - {e}')

    def btn_set_doclick(self):
        try:
            btn = self.sender()
            temp_list = [x for x in self.response.get('list_state')]

            if btn.objectName() == 'btn_cycle_F':
                if temp_list[0] == 0:
                    value = 1

                else:
                    value = 0
                self.model.write_bit_force_cycle(value)

            elif btn.objectName() == 'btn_red_light':
                if temp_list[1] == 0:
                    value = 1
                else:
                    value = 0
                self.model.write_bit_red_light(value)

            elif btn.objectName() == 'btn_green_light':
                if temp_list[2] == 0:
                    value = 1
                else:
                    value = 0
                self.model.write_bit_green_light(value)

            elif btn.objectName() == 'btn_no_control':
                self.model.write_bit_unblock_control()

            elif btn.objectName() == 'btn_max_F':
                self.model.write_bit_emergency_force()

        except Exception as e:
            self.statusbar_set_ui(f'ERROR in settings_window/btn_set_doclick - {e}')

    def update_win(self):
        self.ui.lcdTime.display(self.response.get('counter_time'))
        self.ui.lcdF.display(self.response.get('force'))
        self.ui.lcdH.display(self.response.get('move'))
        self.ui.lcdH_T.display(self.response.get('traverse_move'))
        self.ui.lcdTemp.display(self.response.get('temperature'))
        self.ui.lineEdit_F_alarm.setText(str(int(self.response.get('force_alarm'))))

        self.update_color_switch()

    def update_color_switch(self):
        try:
            self.ui.fram_cycle_F.setStyleSheet(self.set_color_fram(self.response.get('cycle_force')))
            self.ui.fram_no_control.setStyleSheet(self.set_color_fram(self.response.get('lost_control')))
            self.ui.fram_max_F.setStyleSheet(self.set_color_fram(self.response.get('excess_force')))
            self.ui.fram_safety_fence.setStyleSheet(self.set_color_fram(self.response.get('safety_fence')))
            self.ui.fram_condition_FC.setStyleSheet(self.set_color_fram(self.response.get('state_freq')))
            self.ui.fram_sensor_F.setStyleSheet(self.set_color_fram(self.response.get('state_force')))
            self.ui.fram_block_traverse_1.setStyleSheet(self.set_color_fram(
                self.response.get('traverse_block_1'), True))
            self.ui.fram_block_traverse_2.setStyleSheet(self.set_color_fram(
                self.response.get('traverse_block_2'), True))
            self.ui.fram_down_point.setStyleSheet(self.set_color_fram(self.response.get('lowest_position')))
            self.ui.fram_down__alarm_point.setStyleSheet(self.set_color_fram(
                self.response.get('alarm_lowest_position'), True))
            self.ui.fram_up_point.setStyleSheet(self.set_color_fram(self.response.get('highest_position')))
            self.ui.fram_up_alarm_point.setStyleSheet(self.set_color_fram(
                self.response.get('alarm_highest_position'), True))
            self.ui.fram_green_light.setStyleSheet(self.set_color_fram(self.response.get('green_light')))
            self.ui.fram_red_light.setStyleSheet(self.set_color_fram(self.response.get('red_light')))
            self.ui.fram_yellow_btn.setStyleSheet(self.set_color_fram(self.response.get('yellow_btn'), True))

        except Exception as e:
            self.statusbar_set_ui(f'ERROR in settings_window/update_color_switch - {e}')

    def set_color_fram(self, bit, rev=False):
        try:
            if rev:
                if bit == 0:
                    bit = 1
                else:
                    bit = 0
            color_gray = "background-color: rgb(93, 93, 93);\n"
            color_green = "background-color: rgb(0, 255, 0);\n"
            if bit == 0:
                return color_gray + "border-color: rgb(0, 0, 0);"
            elif bit == 1:
                return color_green + "border-color: rgb(0, 0, 0);"

        except Exception as e:
            self.statusbar_set_ui(f'ERROR in settings_window/set_color_fram - {e}')

    def btn_test_clicked(self):
        if self.ui.btn_test.isChecked():
            self.start_test()

        else:
            self.stop_test()
            
    def start_test(self):
        try:
            self.model.set_regs['start_pos'] = False
            self.model.set_regs['start_direction'] = False
            self.model.set_regs['current_direction'] = ''
            self.model.set_regs['min_pos'] = False
            self.model.set_regs['max_pos'] = False
            self.model.write_bit_force_cycle(1)
            time.sleep(0.2)
            self.model.reader_start_test()
            # self.graph_ui.show()

        except Exception as e:
            print(str(e))

    def stop_test(self):
        try:
            self.model.reader_stop_test()
            time.sleep(0.2)
            self.model.write_bit_force_cycle(0)
            time.sleep(0.1)

        except Exception as e:
            print(str(e))

    def update_graph_data(self):
        try:
            coord_x = self.response.get('move_graph')
            coord_y = self.response.get('force_graph')

            self.graph_ui.data_line_test.setData(coord_x, coord_y)

        except Exception as e:
            self.statusbar_set_ui(f'ERROR in settings_window/update_graph_data - {e}')
