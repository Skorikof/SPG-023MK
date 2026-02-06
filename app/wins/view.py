# -*- coding: utf-8 -*-
import time
import pyqtgraph as pg
from PySide6.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem

from app import glob_var
from app.ui_py.mainui import Ui_MainWindow
from app.wins.executors_win import ExecWin
from app.wins.amorts_win import AmortWin
from app.wins.archive_win import ArchiveWin
from app.wins.settings_window import SetWindow
from app.wins.txt_msg import TextMsg
from scripts.data_calculation import CalcData
from scripts.calc_graph.test_graph import TestGraph
from scripts.logger import my_logger


class AppWindow(QMainWindow):
    def __init__(self, model, controller):
        super(AppWindow, self).__init__()
        self.logger = my_logger.get_logger(__name__)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.model = model
        self.controller = controller
        self.calc_data = CalcData()
        self.win_set = SetWindow(model)
        self.win_exec = ExecWin()
        self.win_amort = AmortWin()
        self.win_archive = ArchiveWin()

        self._start_param_view()

    def closeEvent(self, event):
        # if self.model.buffer_state[1] == 'buffer_on':
        #     self.model.write_bit_force_cycle(0)
            
        # if self.controller.timer_process is not None:
        #     self.controller.timer_process.stop()

        # self.model.save_arch.timer_writer_arch_stop()
        self.model.stopConnectCtrl()
        # self.model.client.disconnect_client()
        event.accept()

    def _start_param_view(self):
        self._init_start_view()

        self._init_variables()
        self._init_buttons()
        self._init_signals()

        self._start_page()

    def _init_start_view(self):
        self.tag_msg = 'info'
        self.statusbar = self.statusBar()

    def _init_variables(self):
        self.index_amort = 0
        self.index_type_test = 0

    def _init_buttons(self):
        self.ui.test_save_btn.setVisible(False)
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
        self.ui.select_temp_sensor_btn.clicked.connect(self.select_temper_sensor)
        self.ui.btn_add_speed.clicked.connect(self.specif_add_lab_cascade_table)
        self.ui.btn_reduce_speed.clicked.connect(self.specif_reduce_lab_cascade_table)
        self.ui.test_cancel_btn.clicked.connect(self.cancel_test_clicked)
        self.ui.test_conv_cancel_btn.clicked.connect(self.cancel_test_conv_clicked)
        self.ui.test_repeat_btn.clicked.connect(self.repeat_test_clicked_slot)
        self.ui.test_change_speed_btn.clicked.connect(self.change_speed_lab_test)

        self.ui.specif_type_test_comboBox.activated[int].connect(self.change_index_type_test)
        self.ui.specif_choice_comboBox.activated[int].connect(self.change_index_select_amort)

    def _init_signals(self):
        self.model.signals.connect_ctrl.connect(self._start_page)
        self.model.signals.stbar_msg.connect(self.status_bar_ui)
        self.model.signals.update_data_graph.connect(self.update_graph_view)
        self.model.signals.save_koef_force.connect(self.btn_correct_force_slot)

        self.controller.signals.control_msg.connect(self.controller_msg_slot)
        self.controller.signals.conv_win_test.connect(self.conv_test_win)
        self.controller.signals.lab_win_test.connect(self.lab_test_win)
        self.controller.signals.cancel_test.connect(self.cancel_test_slot)
        self.controller.signals.lab_test_stop.connect(self.slot_lab_test_stop)
        self.controller.signals.conv_test_stop.connect(self.slot_conv_test_stop)
        self.controller.signals.search_hod_msg.connect(self.slot_search_hod)
        self.controller.signals.reset_ui.connect(self._start_page)
        self.controller.steps.signals.conv_result_lamp.connect(self.conv_test_lamp_slot)

        self.win_exec.signals.closed.connect(self.close_win_operator)
        self.win_exec.signals.operator_select.connect(self.operator_select)

        self.win_amort.signals.closed.connect(self.close_win_amort)
        self.win_set.signals.closed.connect(self.close_win_settings)
        self.win_archive.signals.closed.connect(self.close_win_archive)

    def _init_lab_graph(self):
        try:
            self.graph = TestGraph(self.ui.lab_GraphWidget, 'move')

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/_init_lab_graph - {e}')

    def _init_conv_graph(self):
        try:
            self.graph = TestGraph(self.ui.conv_GraphWidget, 'move')

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/_init_conv_graph - {e}')
            
    def _init_temp_graph(self):
        try:
            self.graph = TestGraph(self.ui.lab_GraphWidget, 'temper')
            
        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/_init_temp_graph - {e}')
            
    def status_bar_ui(self, txt_bar):
        try:
            self.ui.statusbar.showMessage(txt_bar)

        except Exception as e:
            self.logger.error(e)

    def controller_msg_slot(self, msg):
        try:
            txt_btn = ''
            if msg == 'yellow_btn':
                txt_btn = 'ЗАПУСК'
            elif msg == 'alarm_traverse_up':
                txt_btn = 'ОПУСТИТЬ'
            elif msg == 'alarm_traverse_down':
                txt_btn = 'ПОДНЯТЬ'
            else:
                txt_btn = 'OK'
            self.ui.ok_message_btn.setText(txt_btn)
            self.main_ui_msg(*TextMsg.msg_from_controller(msg))

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/controller_msg_slot - {e}')

    def main_ui_msg(self, tag, txt):
        try:
            if tag is not None or txt is not None:
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
                    self.main_ui_state(True)
                    self.ui.ok_message_btn.setVisible(True)
                    self.ui.ok_message_btn.setEnabled(True)
                    self.ui.cancel_message_btn.setVisible(False)
                    self.main_btn_state(False)
                self.ui.main_stackedWidget.setCurrentIndex(0)
                self.ui.stack_start_label.setText(txt)
                self.ui.stack_start_label.setStyleSheet("background-color: " + backcolor + ";\n" +
                                                        "color: " + color + ";")

                self.tag_msg = tag
                
            else:
                pass

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/main_ui_msg - {e}')

    def btn_main_stop_clicked(self):
        try:
            self.main_ui_msg(*TextMsg.msg_from_controller('red_btn'))
            self.controller.work_interrupted_operator()
            self.logger.info(f'PUSH BIG RED BUTTON')

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/btn_main_stop_clicked - {e}')

    def btn_ok_message_clicked(self):
        try:
            if self.tag_msg == 'warning':
                if self.model.alarm_tag == 'alarm_traverse_up':
                    self.controller.traverse_move_out_alarm('up')

                elif self.model.alarm_tag == 'alarm_traverse_down':
                    self.controller.traverse_move_out_alarm('down')

                else:
                    self.model.lamp_all_switch_off()
                    time.sleep(0.1)
                    self._start_page()

            elif self.tag_msg == 'question':
                self.model.lamp_all_switch_off()
                time.sleep(0.1)
                self.main_btn_state(False)
                self.main_stop_state(True)
                self.model.signals.test_launch.emit(True)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/btn_ok_message_clicked - {e}')

    def btn_cancel_message_clicked(self):
        try:
            self.controller.change_stage_controller('wait')
            self.model.flag_test_launch = False

            self.model.lamp_all_switch_off()
            time.sleep(0.1)
            self._start_page()

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/btn_cancel_message_clicked - {e}')

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

    def _start_page(self):
        try:
            self.main_stop_state(False)
            if self.model.is_opened_modbus:
                self.main_ui_msg(*TextMsg.msg_from_controller('welcome'))
                self.main_btn_state(True)
                self.main_ui_state(True)

            else:
                self.main_ui_msg(*TextMsg.msg_from_controller('connect_lost'))
                self.main_ui_state(False)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/_start_page - {e}')

    def open_win_operator(self):
        self.main_ui_state(False)
        self.main_btn_state(False)
        self.win_exec.show()

    def operator_select(self, name, rank):
        self.model.data_test.operator.name = name
        self.model.data_test.operator.rank = rank

        self.ui.operator_name_le.setText(f'{name}')
        self.ui.operator_rank_le.setText(f'{rank}')

    def close_win_operator(self):
        self.main_ui_state(True)
        self.main_btn_state(True)
        self.win_exec.hide()

    def open_win_amort(self):
        self.main_ui_state(False)
        self.main_btn_state(False)
        self.win_amort.show()

    def close_win_amort(self):
        self.main_ui_state(True)
        self.main_btn_state(True)
        self.win_amort.hide()
        self.specif_page()

    def btn_search_hod_clicked(self):
        try:
            self.main_ui_state(False)
            self.main_btn_state(False)
            self.main_stop_state(True)
            self.controller.search_hod_gear()

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/btn_search_hod_clicked - {e}')

    def slot_search_hod(self):
        try:
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          f'<b style="color: #f00;">Ход шатуна равен '
                                          f'{self.model.hod_measure}</b>'
                                          )
            self.main_ui_state(True)
            self.main_btn_state(True)
            self.main_stop_state(False)
            self._start_page()

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/slot_search_hod - {e}')

    def btn_gear_set_pos(self):
        try:
            self.main_ui_state(False)
            self.main_btn_state(False)
            self.main_stop_state(True)
            self.controller.move_gear_set_pos()

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/btn_gear_set_pos - {e}')

    def btn_correct_force_clicked(self):
        try:
            self.main_ui_state(False)
            self.main_btn_state(False)
            self.model.init_timer_koef_force()

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'btn_correct_force_clicked - {e}')

    def btn_correct_force_slot(self, tag):
        txt_msg = 'Неудачная попытка откорректировать датчик, повторите пожалуйста'
        if tag == 'done':
            txt_msg = 'Показания с датчика усилия обнулены'

        if self.model.data_test.type_test == 'hand':
            self.win_set.setEnabled(True)

        else:
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          f'<b style="color: #f00;">{txt_msg}</b>')

            self.main_ui_state(True)
            self.main_btn_state(True)

    def btn_cancel_correct_force_clicked(self):
        try:
            self.model.cancel_koef_force()
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          f'<b style="color: #f00;">Корректировка датчика усилия сброшена</b>'
                                          )

            self.main_ui_state(True)
            self.main_btn_state(True)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'btn_cancel_correct_force_clicked - {e}')

    def specif_page(self):
        self.specif_ui_clear()
        self.ui.main_stackedWidget.setCurrentIndex(1)
        self.ui.specif_choice_comboBox.addItems(self.win_amort.amorts.names)
        if len(self.win_amort.amorts.names) < 1:
            self.ui.specif_continue_btn.setEnabled(False)
            self.ui.specif_choice_comboBox.setEnabled(False)
            self.ui.specif_type_test_comboBox.setEnabled(False)
        else:
            self.ui.specif_continue_btn.setEnabled(True)
            self.ui.specif_choice_comboBox.setEnabled(True)
            self.ui.specif_type_test_comboBox.setEnabled(True)
            self.ui.specif_choice_comboBox.setCurrentIndex(self.index_amort)
            self.change_index_select_amort(self.index_amort)

        self.ui.specif_type_test_comboBox.setCurrentIndex(self.index_type_test)
        self.change_index_type_test(self.index_type_test)

        self.change_temper_sensor_btn()

    def change_index_select_amort(self, index):
        self.index_amort = index
        self.select_amort()

    def change_index_type_test(self, index):
        self.index_type_test = index
        self.select_type_test()
        self.select_amort()

    def update_graph_view(self):
        try:
            type_test = self.model.data_test.type_test
            if type_test == 'hand':
                pass

            elif type_test == 'conv':
                self._update_conv_graph()
                self._update_conv_data()

            elif type_test == 'temper':
                self._update_temper_graph()
                self._update_lab_data()

            else:
                self._update_lab_graph()
                self._update_lab_data()

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/update_graph - {e}')

    def select_type_test(self):
        try:
            ind = self.index_type_test
            if ind == 0:
                self.model.data_test.type_test = 'lab'
                self.specif_enable_gui(True, True, False, True)

            elif ind == 1:
                self.model.data_test.type_test = 'lab_hand'
                self.specif_enable_gui(False, False, False, True)

            elif ind == 2:
                self.model.data_test.type_test = 'lab_cascade'
                self.specif_enable_gui(False, False, True, True)

            elif ind == 3:
                self.model.data_test.type_test = 'temper'
                self.specif_enable_gui(False, False, False, False)

            elif ind == 4:
                self.model.data_test.type_test = 'conv'
                self.specif_enable_gui(True, True, False, True)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/select_type_test - {e}')

    def specif_enable_gui(self, flag_change_speed, flag_enable_two_test, flag_cascade, flag_temper):
        self.ui.specif_speed_one_lineEdit.setReadOnly(flag_change_speed)

        self.ui.specif_speed_two_lineEdit.setVisible(flag_enable_two_test)
        self.ui.specif_min_recoil_lineEdit_2.setVisible(flag_enable_two_test)
        self.ui.specif_max_recoil_lineEdit_2.setVisible(flag_enable_two_test)
        self.ui.specif_min_comp_lineEdit_2.setVisible(flag_enable_two_test)
        self.ui.specif_max_comp_lineEdit_2.setVisible(flag_enable_two_test)

        self.ui.specif_max_temp_lineEdit.setReadOnly(flag_temper)

        self.ui.btn_add_speed.setVisible(flag_cascade)
        self.ui.btn_reduce_speed.setVisible(flag_cascade)
        self.ui.specif_lab_cascade_speed_table.setVisible(flag_cascade)

    def select_amort(self):
        try:
            amort = self.win_amort.amorts.struct.amorts[self.index_amort]
            self.model.data_test.amort = amort
            self.specif_ui_fill(amort)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/select_amort - {e}')

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
            if self.model.data_test.type_test == 'temper':
                max_temper = self.model.data_test.finish_temperature
            else:
                max_temper = obj.max_temper
            self.ui.specif_max_temp_lineEdit.setText(str(max_temper))

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/specif_ui_fill - {e}')

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
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/specif_ui_clear - {e}')

    def specif_lab_input_speed(self, obj):
        try:
            text = obj.text()
            if not text:
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              'Заполните поле скорости испытания'
                                              )

            speed = float(text.replace(',', '.'))

            if self.model.data_test.amort is None:
                hod = 120
            else:
                hod = self.model.data_test.amort.hod

            max_speed = self.calc_data.max_speed(hod)
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
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/specif_lab_input_speed - {e}')

    def specif_add_lab_cascade_table(self):
        try:
            count_rows = self.ui.specif_lab_cascade_speed_table.rowCount()
            if count_rows < 30:
                self.ui.specif_lab_cascade_speed_table.setColumnCount(1)
                speed = self.specif_lab_input_speed(self.ui.specif_speed_one_lineEdit)
                if speed:
                    self.ui.specif_lab_cascade_speed_table.setRowCount(count_rows + 1)

                    self.ui.specif_lab_cascade_speed_table.setItem(count_rows, 0, QTableWidgetItem(f'{speed}'))

            else:
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              f'<b style="color: #f00;">Введено максимальное количество скоростей '
                                              f'для испытания</b>'
                                              )

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/specif_add_lab_cascade_table - {e}')


    def specif_reduce_lab_cascade_table(self):
        try:
            count_rows = self.ui.specif_lab_cascade_speed_table.rowCount()
            if count_rows > 0:
                self.ui.specif_lab_cascade_speed_table.removeRow(count_rows - 1)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/specif_reduce_lab_cascade_table - {e}')

    def specif_read_lab_cascade_table(self):
        try:
            list_speed = []
            count_rows = self.ui.specif_lab_cascade_speed_table.rowCount()
            if count_rows == 0:
                return False

            else:
                for i in range(count_rows):
                    list_speed.append(float(self.ui.specif_lab_cascade_speed_table.item(i, 0).text()))

                self.model.data_test.speed_list = list_speed[:]
                return True

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/specif_read_lab_cascade_table - {e}')

    def specif_msg_none_cascade_speed(self):
        msg = QMessageBox.information(self,
                                      'Внимание',
                                      f'<b style="color: #f00;">Не введено ни одной скорости для испытания</b>'
                                      )

    def specif_lab_input_temper(self, obj):
        try:
            text = obj.text()
            if not text:
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              'Заполните поле максимальной температуры испытания'
                                              )

            temper = float(text.replace(',', '.'))
            if 0 <= temper <= 200:
                return temper

            else:
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              f'Данная температура (<b style="color: #f00;">{temper}</b>)'
                                              f'не попадает в диапазон от 0 до 200'
                                              )

        except ValueError:
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          f'<b style="color: #f00;">Введено некорректное значение в поле -->\n'
                                          f'Максимальная температура</b>'
                                          )

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/specif_lab_input_temper - {e}')

    def change_temper_sensor_btn(self):
        try:
            if self.model.reg_data.state.select_temper:
                self.ui.select_temp_sensor_btn.setText('Бесконтактный датчик температуры')
            else:
                self.ui.select_temp_sensor_btn.setText('Контактный датчик температуры')

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/change_temper_sensor_btn - {e}')

    def select_temper_sensor(self):
        try:
            btn = self.ui.select_temp_sensor_btn.text()
            if 'Бесконтактный' in btn:
                self.model.write_bit_select_temper(1)
                self.ui.select_temp_sensor_btn.setText('Контактный датчик температуры')

            else:
                self.model.write_bit_select_temper(0)
                self.ui.select_temp_sensor_btn.setText('Бесконтактный датчик температуры')

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/select_temper_sensor - {e}')

    def specif_continue_btn_click(self):
        try:
            if self.model.data_test.operator.name != '' and self.model.data_test.operator.rank != '':
                self.flag_push_force_set()
                self.ui.test_change_speed_btn.setVisible(False)
                self.ui.lab_speed_le.setReadOnly(True)

                flag = self.static_push_force_editing()
                if flag:
                    flag = self.serial_editing_finished()
                    if flag:
                        self.model.data_test.serial = self.ui.specif_serial_lineEdit.text()
                        self.lab_test_second_force_gui(False)
                        if self.model.data_test.type_test == 'conv':
                            self._init_conv_graph()
                            self._conv_win_clear()
                            self.conv_test_fill_template()
                            self.begin_test()

                        else:
                            self._lab_win_clear()
                            self.fill_gui_lab_test()
                            if self.model.data_test.type_test == 'lab_cascade':
                                flag = self.specif_read_lab_cascade_table()
                                if flag:
                                    self._init_lab_graph()
                                    self.begin_test()
                                else:
                                    self.specif_msg_none_cascade_speed()

                            elif self.model.data_test.type_test == 'lab_hand':
                                speed = self.specif_lab_input_speed(self.ui.specif_speed_one_lineEdit)
                                if speed:
                                    self.model.data_test.speed_test = speed
                                    self._init_lab_graph()
                                    self.begin_test()
                            elif self.model.data_test.type_test == 'temper':
                                speed = self.specif_lab_input_speed(self.ui.specif_speed_one_lineEdit)
                                if speed:
                                    self.model.data_test.speed_test = speed
                                    temper = self.specif_lab_input_temper(self.ui.specif_max_temp_lineEdit)
                                    if temper:
                                        self.model.data_test.finish_temperature = temper
                                        self._init_temp_graph()
                                        self.begin_test()

                            else:
                                self.lab_test_second_force_gui(True)
                                self._init_lab_graph()
                                self.begin_test()

            else:
                self.open_win_operator()

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/specif_continue_btn_click - {e}')

    def lab_test_second_force_gui(self, flag):
        self.ui.lab_recoil_le_2.setVisible(flag)
        self.ui.lab_comp_le_2.setVisible(flag)

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
            self.model.data_test.static_push_force = push_force

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
                self.model.data_test.flag_push_force = True
                self.model.lbl_push_force = 'Динамическая выталкивающая сила'

            else:
                self.model.data_test.flag_push_force = False
                self.model.lbl_push_force = 'Статическая выталкивающая сила'

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/flag_push_force_set - {e}')

    def save_log_begin_test(self):
        try:
            type_test = self.model.data_test.type_test
            amort = self.model.data_test.amort
            if type_test == 'lab_hand' or type_test == 'temper':
                speed = self.model.data_test.speed_test
            elif type_test == 'lab_cascade':
                speed = self.model.data_test.speed_list
            else:
                speed = amort.speed_one

            dimensions = f'{amort.min_length}~{amort.max_length}'
            limit_comp_one = f'{amort.min_comp}~{amort.max_comp}'
            limit_comp_two = f'{amort.min_comp_2}~{amort.max_comp_2}'
            limit_recoil_one = f'{amort.min_recoil}~{amort.max_recoil}'
            limit_recoil_two = f'{amort.min_recoil_2}~{amort.max_recoil_2}'

            txt_log = (f'Start {type_test} --> n={amort.name}, s={speed}, '
                       f'dim={dimensions}, h={amort.hod}, '
                       f's_o={amort.speed_one}, s_t={amort.speed_two}, '
                       f'l_c_o={limit_comp_one}, l_c_t={limit_comp_two}, '
                       f'l_r_o={limit_recoil_one}, l_r_t={limit_recoil_two}, '
                       f'm_t={amort.max_temper}')

            self.logger.info(txt_log)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/save_log_begin_test - {e}')

    def fill_gui_lab_test(self):
        try:
            amort = self.model.data_test.amort
            limit_comp_one = f'{amort.min_comp} - {amort.max_comp}'
            limit_comp_two = f'{amort.min_comp_2} - {amort.max_comp_2}'
            limit_recoil_one = f'{amort.min_recoil} - {amort.max_recoil}'
            limit_recoil_two = f'{amort.min_recoil_2} - {amort.max_recoil_2}'

            self.ui.lab_name_le.setText(amort.name)
            self.ui.lab_speed_set_1_le.setText(f'{amort.speed_one}')
            self.ui.lab_limit_comp_1_le.setText(limit_comp_one)
            self.ui.lab_limit_recoil_1_le.setText(limit_recoil_one)
            self.ui.lab_speed_set_2_le.setText(f'{amort.speed_two}')
            self.ui.lab_limit_comp_2_le.setText(limit_comp_two)
            self.ui.lab_limit_recoil_2_le.setText(limit_recoil_two)
            self.ui.lab_hod_le.setText(f'{amort.hod}')

            self.ui.lbl_push_force_lab.setText(self.model.lbl_push_force)
            self.ui.lab_serial_le.setText(f'{self.model.data_test.serial}')

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/fill_gui_lab_test - {e}')

    def begin_test(self):
        try:
            self.main_stop_state(True)
            self.main_btn_state(False)

            if self.model.data_test.type_test != 'conv':
                self.model.list_lab_result = []
                self.ui.test_repeat_btn.setVisible(False)
                self.ui.lab_speed_le.setReadOnly(True)
                self.ui.test_change_speed_btn.setVisible(False)
                self.ui.test_cancel_btn.setText('ПРЕРВАТЬ ИСПЫТАНИЕ')
                self.ui.test_cancel_btn.setEnabled(True)

            else:
                self.ui.test_conv_cancel_btn.setText('ПРЕРВАТЬ ИСПЫТАНИЕ')
                self.ui.test_conv_cancel_btn.setEnabled(True)

            self.save_log_begin_test()

            self.controller.start_test_clicked()

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/begin_test - {e}')

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
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/_lab_win_clear - {e}')

    def lab_test_win(self):
        try:
            self.ui.main_stackedWidget.setCurrentIndex(2)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/lab_test_win - {e}')

    def _conv_win_clear(self):
        try:
            self.ui.conv_comp_le.clear()
            self.ui.conv_comp_le_2.clear()
            self.ui.conv_recoil_le.clear()
            self.ui.conv_recoil_le_2.clear()
            self.ui.conv_speed_one_le.clear()
            self.ui.conv_speed_two_le.clear()
            self.ui.conv_comp_limit_le.clear()
            self.ui.conv_comp_limit_le_2.clear()
            self.ui.conv_recoil_limit_le.clear()
            self.ui.conv_recoil_limit_le_2.clear()
            self.ui.conv_temperture_le.clear()
            self.ui.conv_push_force_le.clear()
            self.conv_test_lamp_slot('one', 'white')
            self.conv_test_lamp_slot('two', 'white')
            
        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/_conv_win_clear - {e}')

    def conv_test_win(self):
        try:
            self.ui.main_stackedWidget.setCurrentIndex(3)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/conv_test_win - {e}')

    def conv_test_fill_template(self):
        try:
            amort = self.model.data_test.amort
            self.ui.conv_comp_limit_le.setText(f'{amort.min_comp} - {amort.max_comp}')
            self.ui.conv_recoil_limit_le.setText(f'{amort.min_recoil} - {amort.max_recoil}')
            self.ui.conv_comp_limit_le_2.setText(f'{amort.min_comp_2} - {amort.max_comp_2}')
            self.ui.conv_recoil_limit_le_2.setText(f'{amort.min_recoil_2} - {amort.max_recoil_2}')

            self.ui.lbl_push_force_conv.setText(self.model.lbl_push_force)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/conv_test_fill_sample - {e}')

    def conv_color_lamp(self, color):
        try:
            border = "border-color: rgb(0, 0, 0);"
            if color == 'white':
                res = f"background-color: rgb(255, 255, 255);\n{border}"
            elif color == 'red':
                res = f"background-color: rgb(255, 0, 0);\n{border}"
            elif color == 'green':
                res = f"background-color: rgb(0, 255, 0);\n{border}"
            else:
                res = f"background-color: rgb(0, 0, 0);\n{border}"

            return res
        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/conv_color_lamp - {e}')

    def conv_test_lamp_slot(self, step, color):
        try:
            if step == 'one':
                self.ui.first_signal.setStyleSheet(self.conv_color_lamp(color))
            elif step == 'two':
                self.ui.second_signal.setStyleSheet(self.conv_color_lamp(color))

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/conv_test_lamp_slot - {e}')

    def _update_conv_graph(self):
        try:
            self.ui.conv_GraphWidget.clear()
            self.graph.fill_graph(self.model.move,
                                  self.model.force,
                                  name=f'{self.model.data_test.speed_test} м/с')

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/_update_conv_graph - {e}')

    def _update_conv_data(self):
        try:
            self.ui.conv_temperture_le.setText(f'{self.model.data_test.temperature}')
            self.ui.conv_push_force_le.setText(f'{self._fill_push_force()}')

            if self.controller.stage == 'test_speed_one':
                self.ui.conv_speed_one_le.setText(f'{self.model.data_test.speed_test}')
                self.ui.conv_comp_le.setText(f'{self.model.max_comp}')
                self.ui.conv_recoil_le.setText(f'{self.model.max_recoil}')

            if self.controller.stage == 'test_speed_two':
                self.ui.conv_speed_two_le.setText(f'{self.model.data_test.speed_test}')
                self.ui.conv_comp_le_2.setText(f'{self.model.max_comp}')
                self.ui.conv_recoil_le_2.setText(f'{self.model.max_recoil}')

            else:
                pass

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/_update_conv_data - {e}')

    def _update_lab_graph(self):
        try:
            self.ui.lab_GraphWidget.clear()
            self.graph.fill_graph(self.model.move,
                                  self.model.force,
                                  name=f'{self.model.data_test.speed_test} м/с')

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/_update_lab_graph - {e}')

    def _update_temper_graph(self):
        try:
            self.ui.lab_GraphWidget.clear()
            if len(self.model.temper_graph) > 1:
                pen_recoil = pg.mkPen(color='black', width=3)
                pen_comp = pg.mkPen(color='blue', width=3)

                self.graph.fill_graph(self.model.temper_graph, self.model.temper_recoil_graph,
                                      pen=pen_recoil, name='Отбой')
                self.graph.fill_graph(self.model.temper_graph, self.model.temper_comp_graph,
                                      pen=pen_comp, name='Сжатие')

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/_update_temper_graph - {e}')

    def _update_lab_data(self):
        try:
            if self.model.data_test.type_test == 'lab':
                if self.controller.stage == 'test_speed_one':
                    self.ui.lab_comp_le.setText(f'{self.model.max_comp}')
                    self.ui.lab_recoil_le.setText(f'{self.model.max_recoil}')

                elif self.controller.stage == 'test_speed_two':
                    self.ui.lab_comp_le_2.setText(f'{self.model.max_comp}')
                    self.ui.lab_recoil_le_2.setText(f'{self.model.max_recoil}')
            else:
                self.ui.lab_comp_le.setText(f'{self.model.max_comp}')
                self.ui.lab_recoil_le.setText(f'{self.model.max_recoil}')

            self.ui.lab_now_temp_le.setText(f'{self.model.data_test.temperature}')
            self.ui.lab_max_temp_le.setText(f'{self.model.data_test.max_temperature}')
            self.ui.lab_speed_le.setText(f'{self.model.data_test.speed_test}')
            self.ui.lab_power_le.setText(f'{self.model.power_amort}')
            self.ui.lab_freq_le.setText(f'{self.model.freq_piston}')
            self.ui.lab_push_force_le.setText(f'{self._fill_push_force()}')

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/_update_lab_data - {e}')

    def _fill_push_force(self):
        try:
            if self.model.data_test.flag_push_force:
                return self.model.dynamic_push_force

            else:
                return self.model.data_test.static_push_force

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/_fill_push_force - {e}')

    def repeat_test_clicked_slot(self):
        self.model.flag_repeat = True
        self.begin_test()

    def cancel_test_clicked(self):
        try:

            temp = self.ui.test_cancel_btn.text()

            if temp == 'ПРЕРВАТЬ ИСПЫТАНИЕ':
                self.ui.test_cancel_btn.setEnabled(False)
                self.controller.stop_test_clicked()

            elif temp == 'НАЗАД':
                self.controller.steps_tests.step_stop_test()
                self.model.flag_test_launch = False
                self.controller.traverse_install_point('stop_test')
                self.ui.test_cancel_btn.setText('ПРЕРВАТЬ ИСПЫТАНИЕ')

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/cancel_test_clicked - {e}')

    def change_speed_lab_test(self):
        try:
            speed = self.specif_lab_input_speed(self.ui.lab_speed_le)
            if speed:
                self.model.data_test.speed_test = speed

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/change_speed_lab_test - {e}')

    def slot_lab_test_stop(self):
        type_test = self.model.data_test.type_test
        self.ui.test_cancel_btn.setEnabled(True)
        self.ui.test_cancel_btn.setText('НАЗАД')
        self.ui.test_repeat_btn.setVisible(True)

        if type_test == 'lab_hand':
            self.ui.lab_speed_le.setReadOnly(False)
            self.ui.test_change_speed_btn.setVisible(True)

        elif type_test == 'lab' or type_test == 'lab_cascade':
            self.ui.lab_GraphWidget.clear()
            self.graph.fill_compare_graph(self.model.list_lab_result)

    def slot_conv_test_stop(self):
        self.ui.test_conv_cancel_btn.setEnabled(True)
        self.ui.test_conv_cancel_btn.setText('НАЗАД')
        self.ui.conv_GraphWidget.clear()
        self.graph.fill_compare_graph(self.model.list_lab_result)

    def cancel_test_conv_clicked(self):
        try:
            temp = self.ui.test_conv_cancel_btn.text()

            if temp == 'ПРЕРВАТЬ ИСПЫТАНИЕ':
                self.ui.test_conv_cancel_btn.setEnabled(False)
                self.controller.stop_test_clicked()

            elif temp == 'НАЗАД':
                self.controller.steps_tests.step_stop_test()
                self.model.flag_test_launch = False
                self.model.data_test.serial = str(int(self.model.data_test.serial) + 1)
                self.controller.traverse_install_point('stop_test')
                self.ui.test_conv_cancel_btn.setText('ПРЕРВАТЬ ИСПЫТАНИЕ')

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/cancel_test_conv_clicked - {e}')

    def cancel_test_slot(self):
        try:
            self.main_stop_state(False)
            self.main_btn_state(True)
            self.specif_page()

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/cancel_test_slot - {e}')

    def open_win_archive(self):
        self.main_ui_state(False)
        self.main_btn_state(False)
        self.win_archive.init_archive_win()
        self.win_archive.show()

    def close_win_archive(self):
        self.main_ui_state(True)
        self.main_btn_state(True)
        self.win_archive.close()

    def open_win_settings(self):
        self.main_btn_state(False)
        self.main_ui_state(False)
        self.model.data_test.type_test = 'hand'
        self.win_set.show()
        self.win_set.start_param_win_set()

    def close_win_settings(self):
        self.main_btn_state(True)
        self.main_ui_state(True)
        self.win_set.close()
        self.select_type_test()
