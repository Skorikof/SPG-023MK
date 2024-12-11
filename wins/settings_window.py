# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QObject, pyqtSignal, QSignalMapper, pyqtSlot
import time

from ui_py.settings_ui import Ui_SettingsWindow
from wins.graph_win import GraphUi


class WinSignals(QObject):
    closed = pyqtSignal()
    log_err = pyqtSignal(str)


class SetWindow(QMainWindow, Ui_SettingsWindow):
    signals = WinSignals()

    def __init__(self, model):
        super(SetWindow, self).__init__()
        try:
            self.response = {}
            self.model = model
            self.setupUi(self)
            self.hide()
            self.graph_ui = GraphUi(self.model)

        except Exception as e:
            self.signals.log_err.emit(f'ERROR in settings_window/__init__ - {e}')

    def _smap_line_edit(self):
        smap = QSignalMapper(self)

        self.lineEdit_F_alarm.clicked.connect(smap.map)
        smap.setMapping(self.lineEdit_F_alarm, 1)

        smap.mapped.connect(self._on_click_lineedit)

    @pyqtSlot(int)
    def _on_click_lineedit(self, index):
        if index == 1:
            self.model.reader_stop()

    def closeEvent(self, event):
        self.signals.closed.emit()

    def start_param_win_set(self):
        self._create_statusbar_set()
        self._init_buttons()
        self._smap_line_edit()
        self._fill_lbl_temp_sens()

        self._check_operator()

    def _check_operator(self):
        try:
            name = self.model.set_regs.get('operator')['name']
            if name == 'Скориков И.А.':
                self.freq_frame.setVisible(True)

            else:
                self.freq_frame.setVisible(False)

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in settings_window/_check_operator - {e}')

    def _fill_lbl_temp_sens(self):
        channel = self.response.get('select_temper', 0)
        txt = ''
        if channel == 0:
            txt = 'Бесконтактный датчик температуры'
        elif channel == 1:
            txt = 'Контактный датчик темературы'
        self.lbl_temp_sens.setText(txt)

    def _create_statusbar_set(self):
        self.statusbar = self.statusBar()
        self.statusbar.showMessage('Окно управления стенда в ручную')

    def _statusbar_set_ui(self, txt_bar):
        try:
            self.statusbar.showMessage(txt_bar)
            self.signals.log_err.emit(txt_bar)

        except Exception as e:
            self.signals.log_err.emit(f'ERROR in settings_window/_statusbar_set_ui - {e}')

    def _init_buttons(self):
        self.btn_exit.clicked.connect(self.close)
        self.btn_hod.clicked.connect(self._write_hod)
        self.btn_speed_main.clicked.connect(self._write_speed_set)
        self.btn_freq_trverse.clicked.connect(self._write_frequency_set)

        self.btn_motor_main_start.clicked.connect(self._click_btn_motor_start)
        self.btn_motor_main_stop.clicked.connect(self._click_btn_motor_main_stop)
        self.btn_motor_up.clicked.connect(self._click_btn_motor_up)
        self.btn_motor_down.clicked.connect(self._click_btn_motor_down)
        self.btn_motor_traverse_stop.clicked.connect(self._click_btn_motor_traverse_stop)
        self.btn_cycle_F.clicked.connect(self._btn_set_doclick)
        self.btn_no_control.clicked.connect(self._btn_set_doclick)
        self.btn_max_F.clicked.connect(self._btn_set_doclick)
        self.btn_green_light.clicked.connect(self._btn_set_doclick)
        self.btn_red_light.clicked.connect(self._btn_set_doclick)
        self.btn_temper_channel.clicked.connect(self._btn_set_doclick)

        self.btn_test.clicked.connect(self._btn_test_clicked)

        self.lineEdit_F_alarm.returnPressed.connect(self._write_alarm_force)

        self.btn_connect.setVisible(False)
        self.btn_read.setVisible(False)

    def update_data_win_set(self, response):
        try:
            self.response = {**self.response, **response}
            self._update_win()

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in settings_window/update_data - {e}')

    def _write_hod(self):
        try:
            temp = int(self.lineEdit_hod.text())
            if not temp:
                pass
            else:
                self.model.update_main_dict({'hod': temp})

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in settings_window/_write_hod - {e}')

    def _write_speed_set(self):
        try:
            value = self.lineEdit_speed_main.text()
            value = float(value.replace(',', '.'))
            speed = self.model.calculate_freq(value)
            self.model.write_frequency(1, speed)

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in settings_window/_write_speed_set - {e}')

    def _write_frequency_set(self):
        try:
            value = int(self.lineEdit_freq_traverse.text())

            self.model.write_frequency(2, value * 100)

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in settings_window/_write_frequency_set - {e}')

    def _click_btn_motor_up(self):
        self.model.motor_up(2)

    def _click_btn_motor_down(self):
        self.model.motor_down(2)

    def _click_btn_motor_start(self):
        self.model.motor_up(1)

    def _click_btn_motor_main_stop(self):
        self.model.motor_stop(1)

    def _click_btn_motor_traverse_stop(self):
        self.model.motor_stop(2)

    def _write_alarm_force(self):
        try:
            value = float(self.lineEdit_F_alarm.text())
            if value == float(self.response.get('force_alarm')):
                pass
            else:
                self.model.write_emergency_force(value)
                time.sleep(0.02)

            self.model.reader_start()
            time.sleep(0.02)

            self.model.write_bit_unblock_control()

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in settings_window/_write_alarm_force - {e}')

    def _btn_set_doclick(self):
        try:
            btn = self.sender().objectName()
            temp_list = [x for x in self.response.get('list_state')]

            if btn == 'btn_cycle_F':
                if temp_list[0] == 0:
                    value = 1
                else:
                    value = 0
                self.model.write_bit_force_cycle(value)

            elif btn == 'btn_red_light':
                if temp_list[1] == 0:
                    value = 1
                else:
                    value = 0
                self.model.write_bit_red_light(value)

            elif btn == 'btn_green_light':
                if temp_list[2] == 0:
                    value = 1
                else:
                    value = 0
                self.model.write_bit_green_light(value)

            elif btn == 'btn_temper_channel':
                if temp_list[6] == 0:
                    value = 1
                else:
                    value = 0
                self._change_lbl_temper_channel(value)
                self.model.write_bit_select_temper(value)

            elif btn == 'btn_no_control':
                self.model.write_bit_unblock_control()

            elif btn == 'btn_max_F':
                self.model.write_bit_emergency_force()

            else:
                pass

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in settings_window/_btn_set_doclick - {e}')

    def _change_lbl_temper_channel(self, value):
        if value == 1:
            txt = 'Контактный датчик температуры'
        else:
            txt = 'Бесконтактный датчик температуры'

        self.lbl_temp_sens.setText(txt)

    def _update_win(self):
        self.lcdTime.display(self.response.get('count'))
        self.lcdF.display(self.response.get('force'))
        self.lcdH.display(self.response.get('move'))
        self.lcdH_T.display(self.response.get('traverse_move'))
        self.lcdTemp_1.display(self.response.get('temper_first', 0))
        self.lcdTemp_2.display(self.response.get('temper_second', 0))
        self.lineEdit_F_alarm.setText(f'{self.response.get("force_alarm")}')

        self._update_color_switch()

    def _update_color_switch(self):
        try:
            self.fram_cycle_F.setStyleSheet(self._set_color_fram(self.response.get('cycle_force', False)))
            self.fram_no_control.setStyleSheet(self._set_color_fram(self.response.get('lost_control', False)))
            self.fram_max_F.setStyleSheet(self._set_color_fram(self.response.get('excess_force', False)))
            self.fram_safety_fence.setStyleSheet(self._set_color_fram(self.response.get('safety_fence', False)))
            self.fram_condition_FC.setStyleSheet(self._set_color_fram(self.response.get('state_freq', False)))
            self.fram_sensor_F.setStyleSheet(self._set_color_fram(self.response.get('state_force', False)))
            self.fram_block_traverse_1.setStyleSheet(self._set_color_fram(
                self.response.get('traverse_block_left', True), True))
            self.fram_block_traverse_2.setStyleSheet(self._set_color_fram(
                self.response.get('traverse_block_right', True), True))
            self.fram_down_point.setStyleSheet(self._set_color_fram(self.response.get('lowest_position', False)))
            self.fram_down__alarm_point.setStyleSheet(self._set_color_fram(
                self.response.get('alarm_lowest_position', True), True))
            self.fram_up_point.setStyleSheet(self._set_color_fram(self.response.get('highest_position', False)))
            self.fram_up_alarm_point.setStyleSheet(self._set_color_fram(
                self.response.get('alarm_highest_position', True), True))
            self.fram_green_light.setStyleSheet(self._set_color_fram(self.response.get('green_light', False)))
            self.fram_red_light.setStyleSheet(self._set_color_fram(self.response.get('red_light', False)))
            self.fram_yellow_btn.setStyleSheet(self._set_color_fram(self.response.get('yellow_btn', True), True))

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in settings_window/update_color_switch - {e}')

    def _set_color_fram(self, state, rev=False):
        try:
            if rev:
                if state is False:
                    state = True
                else:
                    state = False
            color_gray = "background-color: rgb(93, 93, 93);\n"
            color_green = "background-color: rgb(0, 255, 0);\n"
            if state is False:
                return color_gray + "border-color: rgb(0, 0, 0);"
            elif state is True:
                return color_green + "border-color: rgb(0, 0, 0);"

        except Exception as e:
            self._statusbar_set_ui(f'ERROR in settings_window/_set_color_fram - {e}')

    def _btn_test_clicked(self):
        if self.btn_test.isChecked():
            command = {'start_direction': False,
                       'current_direction': '',
                       'min_pos': False,
                       'max_pos': False,
                       }

            self.model.update_main_dict(command)

            self.model.reader_start_test()

            # self.graph_ui.show()

        else:
            self.model.reader_stop_test()

    # def update_graph_hand_set(self):
    #     try:
    #         self.graph_ui.data_line_test.setData(self.response.get('move_graph'), self.response.get('force_graph'))
    #
    #     except Exception as e:
    #         self._statusbar_set_ui(f'ERROR in settings_window/update_graph_hand_set - {e}')
