from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QObject, pyqtSignal
from settings_ui import Ui_SettingsWindow


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

            self.init_buttons()

        except Exception as e:
            print(str(e))

    def closeEvent(self, event):
        self.close_window()

    def close_window(self):
        self.signals.closed.emit()

    def init_buttons(self):
        self.ui.btn_ok.clicked.connect(self.close_window)
        self.ui.rbtn_traverse.toggled.connect(self.select_engine)
        self.ui.rbtn_traverse.adr_freq = 2
        self.ui.rbtn_engine.toggled.connect(self.select_engine)
        self.ui.rbtn_engine.adr_freq = 1
        self.ui.btn_save_freq.clicked.connect(self.write_frequency)
        self.ui.btn_motor_main_start.clicked.connect(self.click_btn_motor_start)
        self.ui.btn_motor_main_stop.clicked.connect(self.click_btn_motor_stop)
        self.ui.btn_motor_up.clicked.connect(self.click_btn_motor_up)
        self.ui.btn_motor_down.clicked.connect(self.click_btn_motor_down)
        self.ui.btn_motor_stop.clicked.connect(self.click_btn_motor_stop)
        self.ui.btn_cycle_F.clicked.connect(self.btn_set_doclick)
        self.ui.btn_no_control.clicked.connect(self.btn_set_doclick)
        self.ui.btn_max_F.clicked.connect(self.btn_set_doclick)

    def select_engine(self):
        rbtn = self.sender()
        if rbtn.isChecked():
            self.model.set_regs['adr_freq'] = int(rbtn.adr_freq)

    def write_frequency(self):
        try:
            value = self.ui.lineEdit_freq.text()
            if not value:
                pass
            else:
                self.model.set_state['frequency'] = int(value)
                self.model.write_frequency()

        except Exception as e:
            print(str(e))

    def click_btn_motor_up(self):
        self.model.set_regs['adr_freq'] = 2
        self.model.motor_up()

    def click_btn_motor_down(self):
        self.model.set_regs['adr_freq'] = 2
        self.model.motor_down()

    def click_btn_motor_start(self):
        self.model.set_regs['adr_freq'] = 1
        self.model.motor_up()

    def click_btn_motor_stop(self):
        self.model.motor_stop()

    def btn_set_doclick(self):
        try:
            btn = self.sender()
            index = 0
            flag = False

            if btn.objectName() == 'btn_cycle_F':
                index = 0
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
                value = self.model.set_regs.get('list_state')[index]
                if value == 0:
                    bool_val = 1
                    btn.setChecked(True)
                else:
                    bool_val = 0
                    btn.setChecked(False)
                self.model.change_list_state(index, bool_val)

            else:
                bool_val = 0
                btn.setChecked(False)
                self.model.change_list_state(index, bool_val)

        except Exception as e:
            print(str(e))

    def update_win(self):
        self.ui.lcdF.display(self.model.set_state.get('force'))
        self.ui.lcdH.display(self.model.set_state.get('amort_move'))
        self.ui.lcdH_T.display(self.model.set_state.get('traverse_move'))
        self.ui.lcdTemp.display(self.model.set_state.get('temperature'))
        self.update_color_switch(self.model.set_state)

    def update_color_switch(self, state):
        try:
            self.ui.fram_cycle_F.setStyleSheet(self.set_color_farm(state.get('cycle_force')))
            self.ui.fram_no_control.setStyleSheet(self.set_color_farm(state.get('lost_control')))
            self.ui.fram_max_F.setStyleSheet(self.set_color_farm(state.get('excess_force')))
            self.ui.fram_safety_fence.setStyleSheet(self.set_color_farm(state.get('safety_fence')))
            self.ui.fram_condition_FC.setStyleSheet(self.set_color_farm(state.get('state_freq')))
            self.ui.fram_sensor_F.setStyleSheet(self.set_color_farm(state.get('state_force')))
            self.ui.fram_block_traverse_1.setStyleSheet(self.set_color_farm(state.get('traverse_block_1')))
            self.ui.fram_block_traverse_2.setStyleSheet(self.set_color_farm(state.get('traverse_block_2')))
            self.ui.fram_down_point.setStyleSheet(self.set_color_farm(state.get('lowest_position')))
            self.ui.fram_down__alarm_point.setStyleSheet(self.set_color_farm(state.get('alarm_lowest_position')))
            self.ui.fram_up_point.setStyleSheet(self.set_color_farm(state.get('highest_position')))
            self.ui.fram_up_alarm_point.setStyleSheet(self.set_color_farm(state.get('alarm_highest_position')))

        except Exception as e:
            print(str(e))

    def set_color_farm(self, bit):
        try:
            color_gray = "background-color: rgb(93, 93, 93);\n"
            color_green = "background-color: rgb(0, 255, 0);\n"
            if bit == '0':
                return color_gray + "border-color: rgb(0, 0, 0);"
            elif bit == '1':
                return color_green + "border-color: rgb(0, 0, 0);"

        except Exception as e:
            print(str(e))
