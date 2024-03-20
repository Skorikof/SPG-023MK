from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QObject, pyqtSignal
from settings_ui import Ui_SettingsWindow
from graph_win import GraphUi


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

            self._create_statusbar_set()

            self.init_buttons()

        except Exception as e:
            print(str(e))

    def closeEvent(self, event):
        self.close_window()

    def close_window(self):
        self.signals.closed.emit()

    def _create_statusbar_set(self):
        self.statusbar = self.statusBar()
        self.statusbar.showMessage('Чтение регистров контроллера запущено автоматически')

    def statusbar_set_ui(self, txt_bar):
        try:
            self.statusbar.showMessage(txt_bar)

        except Exception as e:
            txt_log = 'ERROR in settings_window/statusbar_set_ui - {}'.format(e)
            self.model.status_bar_msg(txt_log)
            self.model.save_log('error', str(e))

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
                self.model.set_regs['frequency'] = int(value)
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

    def click_btn_motor_stop(self):
        self.model.motor_stop()

    def btn_set_doclick(self):
        try:
            btn = self.sender()
            index = 0
            flag = False
            temp_list = [x for x in self.model.set_regs.get('list_state')]

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
                value = temp_list[index]
                if value == 0:
                    bool_val = 1
                    btn.setChecked(True)
                    if index == 0:
                        self.open_graph_win()
                else:
                    bool_val = 0
                    btn.setChecked(False)
                self.model.change_list_state(index, bool_val)

            else:
                bool_val = 0
                btn.setChecked(False)
                self.model.change_list_state(index, bool_val)

        except Exception as e:
            txt_log = 'ERROR in settings_window/btn_set_doclick - {}'.format(e)
            self.statusbar.showMessage(txt_log)
            self.model.save_log('error', str(e))

    def update_win(self):
        self.ui.lcdF.display(self.model.set_regs.get('force_now'))
        self.ui.lcdH.display(self.model.set_regs.get('amort_move'))
        self.ui.lcdH_T.display(self.model.set_regs.get('traverse_move'))
        self.ui.lcdTemp.display(self.model.set_regs.get('temperature'))
        self.update_color_switch(self.model.set_regs)
        if self.flag_graph:
            self.update_graph()

    def update_color_switch(self, state):
        try:
            self.ui.fram_cycle_F.setStyleSheet(self.set_color_fram(state.get('cycle_force')))
            self.ui.fram_no_control.setStyleSheet(self.set_color_fram(state.get('lost_control')))
            self.ui.fram_max_F.setStyleSheet(self.set_color_fram(state.get('excess_force')))
            self.ui.fram_safety_fence.setStyleSheet(self.set_color_fram(state.get('safety_fence')))
            self.ui.fram_condition_FC.setStyleSheet(self.set_color_fram(state.get('state_freq')))
            self.ui.fram_sensor_F.setStyleSheet(self.set_color_fram(state.get('state_force')))
            self.ui.fram_block_traverse_1.setStyleSheet(self.set_color_fram(state.get('traverse_block_1')))
            self.ui.fram_block_traverse_2.setStyleSheet(self.set_color_fram(state.get('traverse_block_2')))
            self.ui.fram_down_point.setStyleSheet(self.set_color_fram(state.get('lowest_position')))
            self.ui.fram_down__alarm_point.setStyleSheet(self.set_color_fram(state.get('alarm_lowest_position'), True))
            self.ui.fram_up_point.setStyleSheet(self.set_color_fram(state.get('highest_position')))
            self.ui.fram_up_alarm_point.setStyleSheet(self.set_color_fram(state.get('alarm_highest_position'), True))

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

    def open_graph_win(self):
        self.graph_ui.show()
        self.flag_graph = True

    def update_graph(self):
        x = self.model.set_regs.get('amort_move_list')
        y = self.model.set_regs.get('force_list')
        self.graph_ui.data_line_test.setData(x, y)
