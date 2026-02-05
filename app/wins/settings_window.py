# -*- coding: utf-8 -*-
import time
from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import QObject, Signal, QSignalMapper, Slot

from scripts.logger import my_logger
from scripts.data_calculation import CalcData
from app.ui_py.settings_ui import UiSettingsWindow


class WinSignals(QObject):
    closed = Signal()


class SetWindow(QMainWindow, UiSettingsWindow):
    signals = WinSignals()

    def __init__(self, model):
        super(SetWindow, self).__init__()
        try:
            self.logger = my_logger.get_logger(__name__)
            self.model = model
            self.calc_data = CalcData()
            self.setupUi(self)

            self.hod = 50

        except Exception as e:
            self.logger.error(e)

    def _smap_line_edit(self):
        smap = QSignalMapper(self)

        self.lineEdit_F_alarm.clicked.connect(smap.map)
        smap.setMapping(self.lineEdit_F_alarm, 1)

        smap.mappedInt.connect(self._on_click_lineedit)

    @Slot(int)
    def _on_click_lineedit(self, index):
        if index == 1:
            self.model.reader_stop()

    def closeEvent(self, event):
        if self.model.buffer_state[1] == 'buffer_on':
            # self.model.flag_bufer = False
            # self.model.clear_data_in_graph()
            self.model.write_bit_force_cycle(0)
        self.signals.closed.emit()

    def start_param_win_set(self):
        self._init_buttons()
        self._smap_line_edit()
        self._fill_lbl_temp_sens()

        self._check_operator()

    def _check_operator(self):
        try:
            if self.model.data_test.operator.name == 'Скориков И.А.':
                self.freq_frame.setVisible(True)

            else:
                self.freq_frame.setVisible(False)

        except Exception as e:
            self.logger.error(e)

    def _fill_lbl_temp_sens(self):
        channel = self.model.state_dict.get('select_temper', 0)
        txt = ''
        if channel == 0:
            txt = 'Бесконтактный датчик температуры'
        elif channel == 1:
            txt = 'Контактный датчик темературы'
        self.lbl_temp_sens.setText(txt)

    def _init_buttons(self):
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
        self.btn_correct_force.clicked.connect(self._btn_set_doclick)

        self.btn_test.clicked.connect(self._btn_test_clicked)
        self.lineEdit_F_alarm.returnPressed.connect(self._write_alarm_force)

    def update_data_win_set(self):
        try:
            self._update_win()

        except Exception as e:
            self.logger.error(e)

    def _write_hod(self):
        try:
            temp = int(self.lineEdit_hod.text())
            if not temp:
                pass
            else:
                self.hod = temp

        except Exception as e:
            self.logger.error(e)

    def _write_speed_set(self):
        try:
            value = self.lineEdit_speed_main.text()
            value = float(value.replace(',', '.'))

            command = {'tag': 'speed',
                       'adr': 1,
                       'speed': value,
                       'hod': self.hod}
            self.model.fc_control(**command)

        except Exception as e:
            self.logger.error(e)

    def _write_frequency_set(self):
        try:
            value = int(self.lineEdit_freq_traverse.text())
            command = {'tag': 'speed',
                       'adr': 2,
                       'freq': value}
            self.model.fc_control(**command)

        except Exception as e:
            self.logger.error(e)

    def _click_btn_motor_up(self):
        self.model.fc_control(**{'tag': 'up', 'adr': 2})

    def _click_btn_motor_down(self):
        self.model.fc_control(**{'tag': 'down', 'adr': 2})

    def _click_btn_motor_start(self):
        self.model.fc_control(**{'tag': 'up', 'adr': 1})

    def _click_btn_motor_main_stop(self):
        self.model.fc_control(**{'tag': 'stop', 'adr': 1})

    def _click_btn_motor_traverse_stop(self):
        self.model.fc_control(**{'tag': 'stop', 'adr': 2})

    def _write_alarm_force(self):
        try:
            value = float(self.lineEdit_F_alarm.text())
            if value == float(self.model.data_test.force_alarm):
                pass
            else:
                self.model.write_emergency_force(value)
                time.sleep(0.02)

            self.model.reader_start()
            time.sleep(0.02)

            self.model.write_bit_unblock_control()

        except Exception as e:
            self.logger.error(e)

    def _btn_set_doclick(self):
        try:
            btn = self.sender().objectName()
            if btn == 'btn_cycle_F':
                if self.model.state_list[0] == 0:
                    value = 1
                else:
                    value = 0
                self.model.write_bit_force_cycle(value)

            elif btn == 'btn_red_light':
                if self.model.state_list[1] == 0:
                    value = 1
                else:
                    value = 0
                self.model.write_bit_red_light(value)

            elif btn == 'btn_green_light':
                if self.model.state_list[2] == 0:
                    value = 1
                else:
                    value = 0
                self.model.write_bit_green_light(value)

            elif btn == 'btn_temper_channel':
                if self.model.state_list[6] == 0:
                    value = 1
                else:
                    value = 0
                self._change_lbl_temper_channel(value)
                self.model.write_bit_select_temper(value)

            elif btn == 'btn_no_control':
                self.model.write_bit_unblock_control()

            elif btn == 'btn_max_F':
                self.model.write_bit_emergency_force()

            elif btn == 'btn_correct_force':
                self.setEnabled(False)
                self.model.init_timer_koef_force()

            else:
                pass

        except Exception as e:
            self.logger.error(e)

    def _change_lbl_temper_channel(self, value):
        if value == 1:
            txt = 'Контактный датчик температуры'
        else:
            txt = 'Бесконтактный датчик температуры'

        self.lbl_temp_sens.setText(txt)

    def _update_win(self):
        self.lcdTime.display(self.model.counter)
        self.clear_force_lcd.display(self.model.force_clear)
        self.koef_force_lcd.display(self.model.force_correct)
        self.correct_force_lcd.display(self.model.force_offset)
        self.lcdH.display(self.model.move_now)
        self.lcdH_T.display(self.model.move_traverse)
        self.lcdTemp_1.display(self.model.data_test.first_temperature)
        self.lcdTemp_2.display(self.model.data_test.second_temperature)
        self.lineEdit_F_alarm.setText(f'{self.model.data_test.force_alarm}')

        self._update_color_switch()

    def _update_color_switch(self):
        try:
            self.fram_cycle_F.setStyleSheet(self._set_color_fram(self.model.state_dict.get('cycle_force', False)))
            self.fram_no_control.setStyleSheet(self._set_color_fram(self.model.state_dict.get('lost_control', False)))
            self.fram_max_F.setStyleSheet(self._set_color_fram(self.model.state_dict.get('excess_force', False)))
            self.fram_safety_fence.setStyleSheet(self._set_color_fram(self.model.state_dict.get('safety_fence', False)))
            self.fram_condition_FC.setStyleSheet(self._set_color_fram(self.model.state_dict.get('state_freq', False)))
            self.fram_sensor_F.setStyleSheet(self._set_color_fram(self.model.state_dict.get('state_force', False)))
            self.fram_block_traverse_1.setStyleSheet(self._set_color_fram(
                self.model.switch_dict.get('traverse_block_left', True), True))
            self.fram_block_traverse_2.setStyleSheet(self._set_color_fram(
                self.model.switch_dict.get('traverse_block_right', True), True))
            self.fram_down_point.setStyleSheet(self._set_color_fram(self.model.switch_dict.get('lowest_position', False)))
            self.fram_down__alarm_point.setStyleSheet(self._set_color_fram(
                self.model.switch_dict.get('alarm_lowest_position', True), True))
            self.fram_up_point.setStyleSheet(self._set_color_fram(self.model.switch_dict.get('highest_position', False)))
            self.fram_up_alarm_point.setStyleSheet(self._set_color_fram(
                self.model.switch_dict.get('alarm_highest_position', True), True))
            self.fram_green_light.setStyleSheet(self._set_color_fram(self.model.state_dict.get('green_light', False)))
            self.fram_red_light.setStyleSheet(self._set_color_fram(self.model.state_dict.get('red_light', False)))
            self.fram_yellow_btn.setStyleSheet(self._set_color_fram(self.model.state_dict.get('yellow_btn', True)))

        except Exception as e:
            self.logger.error(e)

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
            self.logger.error(e)

    def _btn_test_clicked(self):
        if self.btn_test.isChecked():
            self.btn_test.clicked.connect(self.model.qtCtrl.startBuffer)
            self.btn_test.clicked.disconnect(self.model.qtCtrl.startBuffer)
            # self.model.reset_current_circle()

            # self.model.reader_start_test()
            # self.model.flag_bufer = True

        else:
            self.btn_test.clicked.connect(self.model.qtCtrl.stopBuffer)
            self.btn_test.clicked.disconnect(self.model.qtCtrl.stopBuffer)
            # self.model.reader_stop_test()
            # self.model.flag_bufer = False
            # self.model.clear_data_in_graph()
