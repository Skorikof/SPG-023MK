# -*- coding: utf-8 -*-
import time

from ui_py.mainui import Ui_MainWindow
from wins.executors_win import ExecWin
from wins.amorts_win import AmortWin
from wins.archive_win import ArchiveWin
import pyqtgraph as pg
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem
import glob_var
from archive import ReadArchive


class AppWindow(QMainWindow):
    def __init__(self, model, controller, win_set):
        super(AppWindow, self).__init__()

        self.response = {}
        self.dict_lab_cascade = {}

        self.index_amort = 0
        self.index_type_test = 0

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.model = model
        self.controller = controller
        self.win_set = win_set

        self.win_exec = ExecWin()
        self.win_amort = AmortWin()
        self.win_archive = ArchiveWin()

        self._start_param_view()

    def closeEvent(self, event):
        self.model.write_bit_force_cycle(0)
        self.controller.timer_process.stop()
        self.model.reader_exit()
        self.model.threadpool.waitForDone()
        self.model.disconnect_client()
        self.close()

    def _create_statusbar_ui(self):
        self.statusbar = self.statusBar()

    def status_bar_ui(self, txt_bar):
        try:
            self.ui.statusbar.showMessage(txt_bar)

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/status_bar_ui - {e}')

    def _start_param_view(self):
        self._create_statusbar_ui()
        self._init_buttons()
        self._init_signals()

        self.ui.main_hand_debug_btn.setVisible(False)  # Окно ручной отладки

        self._init_lab_graph()
        self._init_conv_graph()
        self._start_page()

    def _init_signals(self):
        self.model.signals.connect_ctrl.connect(self._start_page)
        self.model.signals.stbar_msg.connect(self.status_bar_ui)
        self.model.signals.read_finish.connect(self.update_data_view)
        self.model.signals.update_data_graph.connect(self.update_graph_view)

        self.controller.signals.control_msg.connect(self.controller_msg_slot)
        self.controller.signals.traverse_referent.connect(self.msg_traverse_referent)
        self.controller.signals.traverse_position.connect(self.msg_traverse_position)
        self.controller.signals.wait_yellow_btn.connect(self.msg_yellow_btn)
        self.controller.signals.conv_win_test.connect(self.conv_test_win)
        self.controller.signals.conv_lamp.connect(self.conv_test_lamp)
        self.controller.signals.lab_win_test.connect(self.lab_test_win)
        self.controller.signals.cancel_test.connect(self.cancel_test_slot)
        self.controller.signals.end_test.connect(self.slot_write_end_test)
        self.controller.signals.lab_test_stop.connect(self.slot_lab_test_stop)
        self.controller.signals.lab_save_result.connect(self.slot_save_lab_result)
        self.controller.signals.search_hod.connect(self.slot_search_hod)
        self.controller.signals.reset_ui.connect(self.slot_start_page)

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

    def _init_buttons(self):
        self.ui.main_STOP_btn.clicked.connect(self.btn_main_stop_clicked)
        self.ui.ok_message_btn.clicked.connect(self.btn_ok_message_clicked)
        self.ui.cancel_message_btn.clicked.connect(self.btn_cancel_message_clicked)
        self.ui.main_operator_btn.clicked.connect(self.open_win_operator)
        self.ui.main_test_btn.clicked.connect(self.specif_page)
        self.ui.main_hand_debug_btn.clicked.connect(self.open_win_settings)
        self.ui.main_archive_btn.clicked.connect(self.open_win_archive)
        self.ui.main_amorts_btn.clicked.connect(self.open_win_amort)
        self.ui.main_set_gear_hod_btn.clicked.connect(self.btn_gear_set_pos)
        self.ui.main_search_hod_btn.clicked.connect(self.btn_search_hod_clicked)
        self.ui.main_correct_force_btn.clicked.connect(self.btn_correct_force_clicked)
        self.ui.main_cancel_correct_force_btn.clicked.connect(self.btn_cancel_correct_force_clicked)

        self.ui.specif_continue_btn.clicked.connect(self.specif_continue_btn_click)
        self.ui.btn_add_speed.clicked.connect(self.specif_add_lab_cascade_table)
        self.ui.btn_reduce_speed.clicked.connect(self.specif_reduce_lab_cascade_table)
        self.ui.test_cancel_btn.clicked.connect(self.cancel_test_clicked)
        self.ui.test_conv_cancel_btn.clicked.connect(self.cancel_test_conv_clicked)
        self.ui.test_repeat_btn.clicked.connect(self.repeat_test_clicked)
        self.ui.test_change_speed_btn.clicked.connect(self.change_speed_lab_test)

    def update_data_view(self, response):
        try:
            self.response = {**self.response, **response}

            self.controller.update_data_ctrl(self.response)

            if self.response.get('type_test') == 'hand':
                self.win_set.update_data_win_set(self.response)

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/update_data_view - {e}')

    def log_msg_info_slot(self, txt_log):
        self.model.log_info(txt_log)

    def log_msg_err_slot(self, txt_log):
        self.model.log_error(txt_log)

    def controller_msg_slot(self, msg):
        try:
            self.ui.ok_message_btn.setText('OK')
            txt = ''
            tag = 'warning'
            if msg == 'pos_traverse':
                txt = 'ПОЗИЦИОНИРОВАНИЕ\nТРАВЕРСЫ'
                tag = 'attention'

            elif msg == 'move_detection':
                txt = 'ВНИМАНИЕ!\nБудет произведено\nопределение хода'
                tag = 'attention'

            elif msg == 'gear_set_pos':
                txt = 'ВНИМАНИЕ!\nПРОВОРОТ ПРИВОДА\nВ ПОЛОЖЕНИЕ\nДЛЯ РЕГУЛИРОВКИ ХОДА'
                tag = 'attention'

            elif msg == 'pumping':
                txt = 'ПРОКАЧКА\nАМОРТИЗАТОРА'
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
                txt = 'ТРАВЕРСА\nВ ВЕРХНЕМ\nПОЛОЖЕНИИ!\nНАЖМИТЕ\nКНОПКУ РАЗБЛОКИРОВКИ\nИ УДЕРЖИВАЯ ЕЁ\nНАЖМИТЕ КНОПКУ\nНА ЭКРАНЕ'
                self.ui.ok_message_btn.setText('ОПУСТИТЬ')

            elif msg == 'alarm_traverse_down':
                txt = 'ТРАВЕРСА\nВ НИЖНЕМ\nПОЛОЖЕНИИ!\nНАЖМИТЕ\nКНОПКУ РАЗБЛОКИРОВКИ\nИ УДЕРЖИВАЯ ЕЁ\nНАЖМИТЕ КНОПКУ\nНА ЭКРАНЕ'
                self.ui.ok_message_btn.setText('ПОДНЯТЬ')

            elif msg == 'traverse_block':
                txt = 'ТРАВЕРСА\nНЕ РАЗБЛОКИРОВАНА'

            elif msg == 'traverse_unblock':
                txt = 'ТРАВЕРСА\nНЕ ЗАБЛОКИРОВАНА'

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
            self.ui.ok_message_btn.setText('ЗАПУСК')
            txt = 'НАЖМИТЕ\nЖЁЛТУЮ\nКНОПКУ\nДЛЯ ЗАПУСКА\nИСПЫТАНИЯ'
            self.main_ui_msg(txt, 'question')

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

            if tag == 'question':
                backcolor = glob_var.COLOR_ORANGE
                self.ui.message_btn_frame.setVisible(True)
                self.ui.ok_message_btn.setVisible(True)
                self.ui.cancel_message_btn.setVisible(True)

            elif tag == 'attention':
                backcolor = glob_var.COLOR_ORANGE
                self.ui.message_btn_frame.setVisible(False)

            elif tag == 'warning':
                backcolor = glob_var.COLOR_RED
                color = glob_var.COLOR_LYELLOW
                self.ui.message_btn_frame.setVisible(True)
                self.ui.ok_message_btn.setVisible(True)
                self.ui.cancel_message_btn.setVisible(False)
                self.main_btn_state(False)
            self.ui.main_stackedWidget.setCurrentIndex(0)
            self.ui.stack_start_label.setText(txt)
            self.ui.stack_start_label.setStyleSheet("background-color: " + backcolor + ";\n" +
                                                    "color: " + color + ";")

            self.response['tag_msg'] = tag

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
            tag = self.response.get('tag_msg')
            alarm_tag = self.response.get('alarm_tag')
            if tag == 'warning':
                if alarm_tag == 'alarm_traverse_up':
                    self.controller.move_traverse_out_alarm('up')

                elif alarm_tag == 'alarm_traverse_down':
                    self.controller.move_traverse_out_alarm('down')

                else:
                    self.controller.lamp_all_switch_off()
                    time.sleep(0.1)
                    self._start_page()

            elif tag == 'question':
                self.controller.lamp_all_switch_off()
                time.sleep(0.1)
                self.main_btn_state(False)
                self.main_stop_state(True)
                self.model.signals.test_launch.emit(True)

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/btn_ok_message_clicked - {e}')

    def btn_cancel_message_clicked(self):
        try:
            command = {'stage': 'wait',
                       'test_launch': False,
                       }
            self.model.update_main_dict(command)

            self.controller.lamp_all_switch_off()
            time.sleep(0.1)
            self._start_page()

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/btn_cancel_message_clicked - {e}')

    def main_ui_state(self, state):
        self.ui.main_stackedWidget.setEnabled(state)

    def main_btn_state(self, state):
        self.ui.main_operator_btn.setEnabled(state)
        self.ui.main_test_btn.setEnabled(state)
        self.ui.main_archive_btn.setEnabled(state)
        self.ui.main_amorts_btn.setEnabled(state)
        self.ui.main_hand_debug_btn.setEnabled(state)
        self.ui.main_set_gear_hod_btn.setEnabled(state)
        self.ui.main_search_hod_btn.setEnabled(state)
        self.ui.main_correct_force_btn.setEnabled(state)
        self.ui.main_cancel_correct_force_btn.setEnabled(state)

    def main_stop_state(self, state):
        self.ui.main_STOP_btn.setEnabled(state)

    def slot_start_page(self):
        try:
            self._start_page()

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/slot_start_page - {e}')

    def _start_page(self):
        try:
            self.main_stop_state(False)
            if self.model.client:
                txt = "Здравствуйте.\nДобро пожаловать\nв\nпрограмму.\nВыберите необходимый\nпункт меню."
                tag = 'info'
                self.main_ui_msg(txt, tag)
                self.main_btn_state(True)
                self.main_ui_state(True)

            else:
                txt = "ОТСУТСТВУЕТ\nПОДКЛЮЧЕНИЕ\nК\nКОНТРОЛЛЕРУ."
                tag = 'attention'
                self.main_ui_msg(txt, tag)
                self.main_ui_state(False)

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/_start_page - {e}')

    def open_win_operator(self):
        self.main_ui_state(False)
        self.win_exec.show()

    def operator_select(self, name, rank):
        command = {'operator': {'name': name, 'rank': rank}}

        self.model.update_main_dict(command)

        self.ui.operator_name_le.setText(f'{name}')
        self.ui.operator_rank_le.setText(f'{rank}')

    def close_win_operator(self):
        self.main_ui_state(True)
        self.win_exec.hide()

    def open_win_amort(self):
        self.main_ui_state(False)
        self.win_amort.show()

    def close_win_amort(self):
        self.main_ui_state(True)
        self.win_amort.hide()

    def btn_search_hod_clicked(self):
        try:
            self.main_btn_state(False)
            self.main_stop_state(True)
            self.controller.search_hod_gear()

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/btn_search_hod_clicked - {e}')

    def slot_search_hod(self):
        try:
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          f'<b style="color: #f00;">Ход шатуна равен {self.response.get("hod_measure", 0)}</b>'
                                          )
            self.main_ui_state(True)
            self.main_btn_state(True)
            self.main_stop_state(False)
            self._start_page()

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/slot_search_hod - {e}')

    def btn_gear_set_pos(self):
        try:
            self.main_btn_state(False)
            self.main_stop_state(True)
            self.controller.move_gear_set_pos()

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/btn_gear_set_pos - {e}')

    def btn_correct_force_clicked(self):
        try:
            self.model.save_koef_force()
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          f'<b style="color: #f00;">Датчик усилия откорректирован к нулю</b>'
                                          )

        except Exception as e:
            self.log_msg_err_slot(f'btn_correct_force_clicked - {e}')

    def btn_cancel_correct_force_clicked(self):
        try:
            self.model.cancel_koef_force()
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          f'<b style="color: #f00;">Корректировка датчика усилия сброшена</b>'
                                          )

        except Exception as e:
            self.log_msg_err_slot(f'btn_cancel_correct_force_clicked - {e}')

    def specif_page(self):
        self.specif_ui_clear()
        self.ui.main_stackedWidget.setCurrentIndex(1)
        self.ui.specif_choice_comboBox.addItems(self.win_amort.amorts.names)
        if len(self.win_amort.amorts.names) < 1:
            self.ui.specif_continue_btn.setEnabled(False)
        else:
            self.ui.specif_continue_btn.setEnabled(True)
            self.ui.specif_choice_comboBox.setCurrentIndex(0)
            self.ui.specif_choice_comboBox.activated[int].connect(self.change_index_select_amort)
            self.change_index_select_amort(0)

        self.ui.specif_type_test_comboBox.setCurrentIndex(0)
        self.ui.specif_type_test_comboBox.activated[int].connect(self.change_index_type_test)
        self.change_index_type_test(0)

    def change_index_select_amort(self, index):
        self.index_amort = index
        self.select_amort()

    def change_index_type_test(self, index):
        self.index_type_test = index
        self.select_type_test()

    def update_graph_view(self):
        try:
            temp = self.response.get('type_test', 'hand')
            if temp == 'conv':
                self._update_conv_graph()

            elif temp == 'hand':
                self.win_set.update_graph_hand_set()

            else:
                self._update_lab_graph()

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/update_graph - {e}')

    def select_type_test(self):
        try:
            ind = self.index_type_test
            if ind == 0:
                self.model.set_regs['type_test'] = 'lab'
                self.specif_lab_gui()

            elif ind == 1:
                self.model.set_regs['type_test'] = 'lab_hand'
                self.specif_lab_hand_gui()

            elif ind == 2:
                self.model.set_regs['type_test'] = 'lab_cascade'
                self.specif_lab_cascade_gui()

            elif ind == 3:
                self.model.set_regs['type_test'] = 'conv'
                self.specif_lab_gui()

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/select_type_test - {e}')

    def specif_lab_gui(self):
        self.ui.specif_speed_one_lineEdit.setReadOnly(True)

        self.ui.specif_speed_two_lineEdit.setVisible(True)
        self.ui.specif_min_recoil_lineEdit_2.setVisible(True)
        self.ui.specif_max_recoil_lineEdit_2.setVisible(True)
        self.ui.specif_min_comp_lineEdit_2.setVisible(True)
        self.ui.specif_max_comp_lineEdit_2.setVisible(True)

        self.ui.btn_add_speed.setVisible(False)
        self.ui.btn_reduce_speed.setVisible(False)
        self.ui.specif_lab_cascade_speed_table.setVisible(False)

    def specif_lab_hand_gui(self):
        self.ui.specif_speed_one_lineEdit.setReadOnly(False)

        self.ui.specif_speed_two_lineEdit.setVisible(False)
        self.ui.specif_min_recoil_lineEdit_2.setVisible(False)
        self.ui.specif_max_recoil_lineEdit_2.setVisible(False)
        self.ui.specif_min_comp_lineEdit_2.setVisible(False)
        self.ui.specif_max_comp_lineEdit_2.setVisible(False)

        self.ui.btn_add_speed.setVisible(False)
        self.ui.btn_reduce_speed.setVisible(False)
        self.ui.specif_lab_cascade_speed_table.setVisible(False)

    def specif_lab_cascade_gui(self):
        self.ui.specif_speed_one_lineEdit.setReadOnly(False)

        self.ui.specif_speed_two_lineEdit.setVisible(False)
        self.ui.specif_min_recoil_lineEdit_2.setVisible(False)
        self.ui.specif_max_recoil_lineEdit_2.setVisible(False)
        self.ui.specif_min_comp_lineEdit_2.setVisible(False)
        self.ui.specif_max_comp_lineEdit_2.setVisible(False)

        self.ui.btn_add_speed.setVisible(True)
        self.ui.btn_reduce_speed.setVisible(True)
        self.ui.specif_lab_cascade_speed_table.setVisible(True)

    def select_amort(self):
        try:
            ind = self.index_amort
            amort = self.win_amort.amorts.struct.amorts[ind]

            command = {'amort': amort,
                       'hod': amort.hod}

            self.model.update_main_dict(command)

            self.specif_ui_fill(amort)

            adjust_x = int((amort.max_length - amort.min_length - amort.adapter_len) / 2)
            self.model.change_adjust_x(adjust_x)

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/select_amort - {e}')

    def specif_ui_fill(self, obj):
        try:
            self.ui.specif_min_length_lineEdit.setText(str(obj.min_length))
            self.ui.specif_max_length_lineEdit.setText(str(obj.max_length))
            self.ui.specif_hod_lineEdit.setText(str(obj.hod))
            self.ui.specif_speed_one_lineEdit.setText(str(obj.speed_one))
            self.ui.specif_speed_two_lineEdit.setText(str(obj.speed_two))
            self.ui.specif_min_comp_lineEdit.setText(str(obj.min_comp))
            self.ui.specif_min_comp_lineEdit_2.setText(str(obj.min_comp_2))
            self.ui.specif_max_comp_lineEdit.setText(str(obj.max_comp))
            self.ui.specif_max_comp_lineEdit_2.setText(str(obj.max_comp_2))
            self.ui.specif_min_recoil_lineEdit.setText(str(obj.min_recoil))
            self.ui.specif_min_recoil_lineEdit_2.setText(str(obj.min_recoil_2))
            self.ui.specif_max_recoil_lineEdit.setText(str(obj.max_recoil))
            self.ui.specif_max_recoil_lineEdit_2.setText(str(obj.max_recoil_2))
            self.ui.specif_max_temp_lineEdit.setText(str(obj.max_temper))

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/specif_ui_fill - {e}')

    def specif_ui_clear(self):
        try:
            self.ui.specif_choice_comboBox.clear()
            self.ui.specif_serial_lineEdit.clear()
            self.ui.specif_min_length_lineEdit.clear()
            self.ui.specif_max_length_lineEdit.clear()
            self.ui.specif_hod_lineEdit.clear()
            self.ui.specif_speed_one_lineEdit.clear()
            self.ui.specif_speed_two_lineEdit.clear()
            self.ui.specif_min_comp_lineEdit.clear()
            self.ui.specif_min_comp_lineEdit_2.clear()
            self.ui.specif_max_comp_lineEdit.clear()
            self.ui.specif_max_comp_lineEdit_2.clear()
            self.ui.specif_min_recoil_lineEdit.clear()
            self.ui.specif_min_recoil_lineEdit_2.clear()
            self.ui.specif_max_recoil_lineEdit.clear()
            self.ui.specif_max_recoil_lineEdit_2.clear()
            self.ui.specif_max_temp_lineEdit.clear()
            self.ui.specif_static_push_force_lineEdit.clear()

            self.ui.specif_lab_cascade_speed_table.setRowCount(0)

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/specif_ui_clear - {e}')

    def calculate_speed_limit(self):
        hod = int(self.response.get('hod', 40))
        if 40 <= hod < 50:
            return 0.34
        elif 50 <= hod < 60:
            return 0.42
        elif 60 <= hod < 70:
            return 0.51
        elif 70 <= hod < 80:
            return 0.59
        elif 80 <= hod < 90:
            return 0.68
        elif 90 <= hod < 100:
            return 0.77
        elif 100 <= hod < 110:
            return 0.85
        elif 110 <= hod < 120:
            return 0.94
        elif hod == 120:
            return 1.02
        else:
            return 0.34

    def specif_lab_input_speed(self, obj):
        try:
            text = obj.text()
            if not text:
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              'Заполните поле скорости испытания'
                                              )

            speed = float(text.replace(',', '.'))
            max_speed = self.calculate_speed_limit()
            if 0.02 <= speed <= max_speed:
                return speed

            else:
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              f'Данная скорость (<b style="color: #f00;">{speed}</b>)'
                                              f'не попадает в диапазон от 0.02 до {max_speed}'
                                              )

        except ValueError:
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          f'<b style="color: #f00;">Введено некорректное значение в поле -->\n'
                                          f'Скорость испытания</b>'
                                          )

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/specif_lab_input_speed - {e}')

    def specif_add_lab_cascade_table(self):
        try:
            self.ui.specif_lab_cascade_speed_table.setColumnCount(1)
            speed = self.specif_lab_input_speed(self.ui.specif_speed_one_lineEdit)
            if speed:
                count_rows = self.ui.specif_lab_cascade_speed_table.rowCount()

                self.ui.specif_lab_cascade_speed_table.setRowCount(count_rows + 1)

                self.ui.specif_lab_cascade_speed_table.setItem(count_rows, 0, QTableWidgetItem(f'{speed}'))

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/specif_add_lab_cascade_table - {e}')

    def specif_reduce_lab_cascade_table(self):
        try:
            count_rows = self.ui.specif_lab_cascade_speed_table.rowCount()
            if count_rows > 0:
                self.ui.specif_lab_cascade_speed_table.removeRow(count_rows - 1)

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/specif_reduce_lab_cascade_table - {e}')

    def specif_read_lab_cascade_table(self):
        try:
            list_speed = []
            count_rows = self.ui.specif_lab_cascade_speed_table.rowCount()
            if count_rows == 0:
                return False

            else:
                for i in range(count_rows):
                    list_speed.append(float(self.ui.specif_lab_cascade_speed_table.item(i, 0).text()))

                self.model.set_regs['speed_cascade'] = list_speed[:]
                return True

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/specif_read_lab_cascade_table - {e}')

    def specif_msg_none_cascade_speed(self):
        msg = QMessageBox.information(self,
                                      'Внимание',
                                      f'<b style="color: #f00;">Не введено ни одной скорости для испытания</b>'
                                      )

    def specif_continue_btn_click(self):
        try:
            name = self.response.get('operator')['name']
            rank = self.response.get('operator')['rank']

            if name != '' and rank != '':
                self.flag_push_force_set()

                type_test = self.response.get('type_test')

                if type_test == 'conv':
                    self.begin_test()

                else:
                    self.ui.test_change_speed_btn.setVisible(False)
                    self.ui.lab_speed_le.setReadOnly(True)
                    flag = self.serial_editing_finished()
                    if flag:
                        serial_number = self.ui.specif_serial_lineEdit.text()
                        if serial_number != '':
                            self.model.set_regs['serial_number'] = serial_number
                            flag = self.static_push_force_editing()
                            if flag:
                                if type_test == 'lab_cascade':
                                    flag = self.specif_read_lab_cascade_table()
                                    if flag:
                                        self.begin_test()
                                    else:
                                        self.specif_msg_none_cascade_speed()

                                elif type_test == 'lab_hand':
                                    speed = self.specif_lab_input_speed(self.ui.specif_speed_one_lineEdit)
                                    if speed:
                                        self.model.set_regs['speed'] = speed
                                        self.begin_test()

                                else:
                                    self.begin_test()

            else:
                self.open_win_operator()

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/specif_continue_btn_click - {e}')

    def serial_editing_finished(self):
        text = self.ui.specif_serial_lineEdit.text()
        if not text:
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          'Заполните поле серийного номера'
                                          )
            return False

        else:
            return True

    def static_push_force_editing(self):
        try:
            text = self.ui.specif_static_push_force_lineEdit.text()
            if not text:
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              'Заполните поле статической выталкивающей силы'
                                              )
                return False

            push_force = float(text.replace(',', '.'))
            self.model.set_regs['static_push_force'] = push_force

            return True

        except ValueError:
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          f'<b style="color: #f00;">Введено некорректное значение в поле -->\n'
                                          f'Статическая выталкивающая сила</b>'
                                          )

    def flag_push_force_set(self):
        try:
            if self.ui.push_force_chb.isChecked():
                self.model.set_regs['flag_push_force'] = True
                self.model.set_regs['lbl_push_force'] = f'Динамическая\nвыталкивающая\nсила'

            else:
                self.model.set_regs['flag_push_force'] = False
                self.model.set_regs['lbl_push_force'] = f'Статическая\nвыталкивающая\nсила'

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/flag_push_force_set - {e}')

    def save_log_begin_test(self):
        try:
            amort = self.response.get('amort')
            type_test = self.response.get('type_test')
            if type_test == 'lab_hand':
                speed = self.response.get('speed')
            elif type_test == 'lab_cascade':
                speed = self.model.set_regs.get('speed_cascade')
            else:
                speed = amort.speed_one

            name = amort.name
            dimensions = f'{amort.min_length} - {amort.max_length}'
            hod = f'{amort.hod}'
            speed_one = f'{amort.speed_one}'
            speed_two = f'{amort.speed_two}'
            limit_comp_one = f'{amort.min_comp} - {amort.max_comp}'
            limit_comp_two = f'{amort.min_comp_2} - {amort.max_comp_2}'
            limit_recoil_one = f'{amort.min_recoil} - {amort.max_recoil}'
            limit_recoil_two = f'{amort.min_recoil_2} - {amort.max_recoil_2}'
            temper = f'{amort.max_temper}'

            txt_log = (f'Start {type_test} test --> name = {name}, speed = {speed}, dimensions = {dimensions}, '
                       f'hod = {hod}, speed_one = {speed_one}, speed_two = {speed_two}, '
                       f'limit_comp_one = {limit_comp_one}, limit_comp_two = {limit_comp_two}, '
                       f'limit_recoil_one = {limit_recoil_one}, limit_comp_two = {limit_comp_two}, '
                       f'limit_recoil_two = {limit_recoil_two}, max_temper = {temper}')

            self.log_msg_info_slot(txt_log)

            self.model.set_regs['hod'] = amort.hod

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/save_log_begin_test - {e}')

    def fill_gui_lab_test(self):
        try:
            amort = self.response.get('amort')
            name = amort.name
            hod = f'{amort.hod}'
            speed_one = f'{amort.speed_one}'
            speed_two = f'{amort.speed_two}'
            limit_comp_one = f'{amort.min_comp} - {amort.max_comp}'
            limit_comp_two = f'{amort.min_comp_2} - {amort.max_comp_2}'
            limit_recoil_one = f'{amort.min_recoil} - {amort.max_recoil}'
            limit_recoil_two = f'{amort.min_recoil_2} - {amort.max_recoil_2}'

            self.ui.lab_name_le.setText(name)
            self.ui.lab_speed_set_1_le.setText(speed_one)
            self.ui.lab_limit_comp_1_le.setText(limit_comp_one)
            self.ui.lab_limit_recoil_1_le.setText(limit_recoil_one)
            self.ui.lab_speed_set_2_le.setText(speed_two)
            self.ui.lab_limit_comp_2_le.setText(limit_comp_two)
            self.ui.lab_limit_recoil_2_le.setText(limit_recoil_two)
            self.ui.lab_hod_le.setText(hod)

            self.ui.lbl_push_force_lab.setText(self.model.set_regs.get('lbl_push_force', ''))

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/fill_gui_lab_test - {e}')

    def begin_test(self):
        try:
            self.main_stop_state(True)
            self.main_btn_state(False)

            self.save_log_begin_test()

            type_test = self.response.get('type_test')

            if type_test == 'conv':
                self._conv_win_clear()
                self.ui.lbl_push_force_conv.setText(self.model.set_regs.get('lbl_push_force', ''))

            else:
                self._lab_win_clear()
                self.ui.test_repeat_btn.setVisible(False)
                self.ui.test_cancel_btn.setText('ПРЕРВАТЬ ИСПЫТАНИЕ')
                self.fill_gui_lab_test()

            self.controller.start_test_clicked()

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/begin_test - {e}')

    def _lab_win_clear(self):
        try:
            self.ui.lab_GraphWidget.clear()
            self.ui.lab_recoil_le.clear()
            self.ui.lab_comp_le.clear()
            self.ui.lab_speed_le.clear()
            self.ui.lab_now_temp_le.clear()
            self.ui.lab_max_temp_le.clear()
            self.ui.lab_serial_le.clear()

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/_lab_win_clear - {e}')

    def lab_test_win(self):
        try:
            self.ui.main_stackedWidget.setCurrentIndex(2)

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/lab_test_win - {e}')

    def change_speed_test(self):
        try:
            value = self.ui.lab_speed_le.text()
            value = float(value.replace(',', '.'))

            speed = self.model.calculate_freq(value)
            self.model.write_frequency(1, speed)

            txt_log = f'Change speed in lab test on --> {value} m/s'

            self.log_msg_info_slot(txt_log)

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/change_speed_test - {e}')

    def _conv_win_clear(self):
        try:
            self.ui.conv_comp_le.clear()
            self.ui.conv_recoil_le.clear()
            self.ui.conv_speed_le.clear()
            self.ui.conv_comp_limit_le.clear()
            self.ui.conv_recoil_limit_le.clear()
            self.ui.conv_temperture_le.clear()
            
        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/_conv_win_clear - {e}')

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

    def _init_lab_graph(self):
        try:
            self.ui.lab_GraphWidget.showGrid(True, True)
            self.ui.lab_GraphWidget.setBackground('w')

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/_init_lab_graph - {e}')

    def _update_lab_graph(self):
        try:
            self.ui.lab_GraphWidget.clear()
            pen = pg.mkPen(color='black', width=3)
            self.ui.lab_GraphWidget.plot(self.response.get('move_graph'), self.response.get('force_graph'), pen=pen)

            self._update_lab_data()

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/_update_lab_graph - {e}')

    def _update_lab_data(self):
        try:
            self.ui.lab_comp_le.setText(f'{self.response.get("max_comp", 0)}')
            self.ui.lab_recoil_le.setText(f'{self.response.get("max_recoil", 0)}')
            self.ui.lab_now_temp_le.setText(f'{self.response.get("temperature", 0)}')
            self.ui.lab_max_temp_le.setText(f'{self.response.get("max_temperature", 0)}')
            self.ui.lab_speed_le.setText(f'{self.response.get("speed", 0)}')
            self.ui.lab_serial_le.setText(f'{self.response.get("serial_number", 0)}')

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/_update_lab_data - {e}')

    def _update_lab_cascade_graph(self):
        try:
            self.ui.lab_GraphWidget.clear()
            pen = pg.mkPen(color='black', width=3)

            if self.dict_lab_cascade:
                for key, value in self.dict_lab_cascade.items():
                    self.ui.lab_GraphWidget.plot(value.move, value.force, pen=pen)

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/_update_lab_cascade_graph - {e}')

    def _init_conv_graph(self):
        try:
            self.ui.conv_GraphWidget.showGrid(True, True)
            self.ui.conv_GraphWidget.setBackground('w')

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/_init_conv_graph - {e}')

    def _update_conv_graph(self):
        try:
            self.ui.conv_GraphWidget.clear()
            pen = pg.mkPen(color='black', width=3)
            self.ui.conv_GraphWidget.plot(self.response.get('move_graph'), self.response.get('force_graph'), pen=pen)
            
            self._update_conv_data()

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/_update_conv_graph - {e}')
            
    def _update_conv_data(self):
        try:
            amort = self.model.set_regs.get('amort')
            self.ui.conv_comp_le.setText(f'{self.response.get("max_comp", 0)}')
            self.ui.conv_recoil_le.setText(f'{self.response.get("max_recoil", 0)}')
            self.ui.conv_temperture_le.setText(f'{self.response.get("temperature", 0)}')

            if self.response.get('stage') == 'test_speed_one':
                self.ui.conv_speed_le.setText(f'{amort.speed_one}')
                self.ui.conv_comp_limit_le.setText(f'{amort.min_comp} - {amort.max_comp}')
                self.ui.conv_recoil_limit_le.setText(f'{amort.min_recoil} - {amort.max_recoil}')
            
            elif self.response.get('stage') == 'test_speed_two':
                self.ui.conv_speed_le.setText(f'{amort.speed_two}')
                self.ui.conv_comp_limit_le.setText(f'{amort.min_comp_2} - {amort.max_comp_2}')
                self.ui.conv_recoil_limit_le.setText(f'{amort.min_recoil_2} - {amort.max_recoil_2}')

            else:
                pass
            
        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/_update_conv_data - {e}')

    def repeat_test_clicked(self):
        self.model.set_regs['repeat_test'] = True
        self.specif_continue_btn_click()

    def cancel_test_clicked(self):
        try:
            temp = self.ui.test_cancel_btn.text()
            if temp == 'ПРЕРВАТЬ ИСПЫТАНИЕ':
                self.ui.test_cancel_btn.setText('ОСТАНОВКА')
                self.controller.stop_test_clicked()

            elif temp == 'НАЗАД':
                self.model.set_regs['test_launch'] = False
                self.controller.traverse_install_point('stop_test')
                self.ui.test_cancel_btn.setText('ПРЕРВАТЬ ИСПЫТАНИЕ')

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/cancel_test_clicked - {e}')

    def change_speed_lab_test(self):
        try:
            speed = self.specif_lab_input_speed(self.ui.lab_speed_le)
            if speed:
                self.model.set_regs['speed'] = speed

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/change_speed_lab_test - {e}')

    def slot_lab_test_stop(self):
        self.ui.test_cancel_btn.setText('НАЗАД')
        self.ui.test_repeat_btn.setVisible(True)

        if self.response.get('type_test') == 'lab_hand':
            self.ui.lab_speed_le.setReadOnly(False)
            self.ui.test_change_speed_btn.setVisible(True)

    def cancel_test_conv_clicked(self):
        try:
            self.controller.stop_test_clicked()

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/cancel_test_conv_clicked - {e}')

    def cancel_test_slot(self):
        try:
            self.main_stop_state(False)
            self.main_btn_state(True)
            self.specif_page()

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/cancel_test_slot - {e}')

    def open_win_archive(self):
        self.main_ui_state(False)
        self.win_archive.show()
        self.win_archive.read_path_archive()

    def close_win_archive(self):
        self.main_ui_state(True)
        self.win_archive.hide()

    def open_win_settings(self):
        self.main_ui_state(False)
        self.model.set_regs['type_test'] = 'hand'
        self.win_set.show()
        self.win_set.start_param_win_set()

    def close_win_settings(self):
        self.model.set_regs['type_test'] = None
        self.main_ui_state(True)
        self.win_set.hide()

    def slot_save_lab_result(self):
        try:
            self.save_data_in_archive()

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/slot_save_lab_result - {e}')

    def save_data_in_archive(self):
        try:
            data_dict = {'move_graph': self.response.get('move_graph')[:],
                         'force_graph': self.response.get('force_graph')[:],
                         'type_test': self.response.get('type_test'),
                         'speed': self.response.get('speed'),
                         'operator': self.response.get('operator').copy(),
                         'serial': self.response.get('serial_number'),
                         'amort': self.response.get('amort'),
                         'flag_push_force': int(self.response.get('flag_push_force')),
                         'static_push_force': self.response.get('static_push_force'),
                         'dynamic_push_force': self.response.get('dynamic_push_force'),
                         'max_temperature': self.response.get('max_temperature')}

            ReadArchive().save_test_in_archive(data_dict)

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/save_data_in_archive - {e}')

    def slot_write_end_test(self):
        try:
            ReadArchive().write_end_test_in_archive()

        except Exception as e:
            self.log_msg_err_slot(f'ERROR in view/slot_write_end_test - {e}')
