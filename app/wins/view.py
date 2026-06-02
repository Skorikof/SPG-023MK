# -*- coding: utf-8 -*-
import time
import pyqtgraph as pg
from PySide6.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem
from PySide6.QtCore import Slot

from app import glob_var
from app.ui_py.mainui import Ui_MainWindow
from app.wins.executors_win import ExecWin
from app.wins.amorts_win import AmortWin
from app.wins.archive_win import ArchiveWin
from app.wins.settings_window import SetWindow
from app.wins.txt_msg import TextMsg
from scripts.data_calculation import CalcData
from scripts.calc_graph.test_graph import TestGraph
from scripts.controller.controller import Controller
from scripts.controller.stages import Stage, TypeTest, ColorLampConv
from scripts.logger import my_logger
from scripts.model import Model


class AppWindow(QMainWindow):
    def __init__(self, model: Model, controller: Controller):
        super(AppWindow, self).__init__()
        self.logger = my_logger.get_logger(__name__)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.model = model
        self.controller = controller
        self.win_set = SetWindow(model)
        self.calc_data = CalcData()
        self.win_exec = ExecWin()
        self.win_amort = AmortWin()
        self.win_archive = ArchiveWin()

        self._start_param_view()

    def closeEvent(self, event):
        if self.model.get_state_cycle_force():
            self.model.write_bit_force_cycle(0)
            
        if self.controller.timer_process is not None:
            self.controller.timer_process.stop()

        self.model.save_arch.timer_writer_arch_stop()
        self.model.writer.threadpool.waitForDone()
        self.model.writer.timer_writer_stop()
        self.model.reader_exit()
        self.model.reader.threadpool.waitForDone()
        self.model.client.disconnect_client()
        event.accept()

    def _start_param_view(self):
        self._init_variables()
        self._init_buttons()
        self._init_signals()
        self._init_start_view()

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
        self.model.signals.save_koef_force.connect(self.btn_correct_force_slot)
        self.model.signals.update_lab_graph.connect(self.update_graph_view_lab)
        self.model.signals.update_conv_graph.connect(self.update_graph_view_conv)
        self.model.signals.update_temper_graph.connect(self.update_graph_view_temper)
        self.model.signals.conv_result_lamp.connect(self.conv_test_lamp_slot)

        self.controller.signals.control_msg.connect(self.controller_msg_slot)
        self.controller.signals.conv_win_test.connect(self.conv_test_win)
        self.controller.signals.lab_win_test.connect(self.lab_test_win)
        self.controller.signals.cancel_test.connect(self.cancel_test_slot)
        self.controller.signals.lab_test_stop.connect(self.slot_lab_test_stop)
        self.controller.signals.conv_test_stop.connect(self.slot_conv_test_stop)
        self.controller.signals.search_hod_msg.connect(self.slot_search_hod)
        self.controller.signals.reset_ui.connect(self._start_page)

        self.win_exec.signals.closed.connect(self.close_win_operator)
        self.win_exec.signals.operator_select.connect(self.operator_select)

        self.win_amort.signals.closed.connect(self.close_win_amort)
        self.win_set.signals.closed.connect(self.close_win_settings)
        self.win_archive.signals.closed.connect(self.close_win_archive)
        
    def log_exceptions(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                args[0].logger.error(
                    f'ERROR in {func.__name__}: {e}'
                )
        return wrapper

    def _init_lab_graph(self):
        self.graph = TestGraph(self.ui.lab_GraphWidget, 'move')

    def _init_conv_graph(self):
        self.graph = TestGraph(self.ui.conv_GraphWidget, 'move')

    def _init_temp_graph(self):
        self.graph = TestGraph(self.ui.lab_GraphWidget, 'temper')

    @log_exceptions
    def status_bar_ui(self, txt_bar):
        self.ui.statusbar.showMessage(txt_bar)

    @log_exceptions
    def controller_msg_slot(self, msg):
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

    @log_exceptions
    def main_ui_msg(self, tag, txt):
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

    @log_exceptions
    def btn_main_stop_clicked(self):
        self.main_ui_msg(*TextMsg.msg_from_controller('red_btn'))
        self.model.work_interrupted_operator()
        self.logger.info(f'PUSH BIG RED BUTTON')

    @log_exceptions
    def btn_ok_message_clicked(self):
        if self.tag_msg == 'warning':
            if self.model.alarm_tag == 'alarm_traverse_up':
                self.controller.trav_serv.traverse_move_out_alarm('up')

            elif self.model.alarm_tag == 'alarm_traverse_down':
                self.controller.trav_serv.traverse_move_out_alarm('down')

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

    @log_exceptions
    def btn_cancel_message_clicked(self):
        self.controller.set_stage(Stage.WAIT)
        self.model.flag_test_launch = False

        self.model.lamp_all_switch_off()
        time.sleep(0.1)
        self._start_page()

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

    @log_exceptions
    def _start_page(self):
        self.main_stop_state(False)
        if self.model.client.flag_connect:
            self.main_ui_msg(*TextMsg.msg_from_controller('welcome'))
            self.main_btn_state(True)
            self.main_ui_state(True)

        else:
            self.main_ui_msg(*TextMsg.msg_from_controller('connect_lost'))
            self.main_ui_state(False)

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

    @log_exceptions
    def btn_search_hod_clicked(self):
        self.main_ui_state(False)
        self.main_btn_state(False)
        self.main_stop_state(True)
        self.model.search_hod()

    @log_exceptions
    def slot_search_hod(self):
        msg = QMessageBox.information(self,
                                        'Внимание',
                                        f'<b style="color: #f00;">Ход шатуна равен '
                                        f'{self.model.stroke}</b>'
                                        )
        self.main_ui_state(True)
        self.main_btn_state(True)
        self.main_stop_state(False)
        self._start_page()

    @log_exceptions
    def btn_gear_set_pos(self):
        self.main_ui_state(False)
        self.main_btn_state(False)
        self.main_stop_state(True)
        self.model.move_gear_set_pos()

    def btn_correct_force_clicked(self):
        self.main_ui_state(False)
        self.main_btn_state(False)
        self.model.init_timer_koef_force()

    def btn_correct_force_slot(self, tag):
        txt_msg = 'Неудачная попытка откорректировать датчик, повторите пожалуйста'
        if tag == 'done':
            txt_msg = 'Показания с датчика усилия обнулены'

        if self.model.get_type_test() == TypeTest.SETTINGS:
            self.win_set.setEnabled(True)

        else:
            msg = QMessageBox.information(self,
                                          'Внимание',
                                          f'<b style="color: #f00;">{txt_msg}</b>')

            self.main_ui_state(True)
            self.main_btn_state(True)

    def btn_cancel_correct_force_clicked(self):
        self.model.cancel_koef_force()
        msg = QMessageBox.information(self,
                                        'Внимание',
                                        f'<b style="color: #f00;">Корректировка датчика усилия сброшена</b>'
                                        )

        self.main_ui_state(True)
        self.main_btn_state(True)

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
    
    @Slot(object)
    def update_graph_view_lab(self, data):
        self._update_lab_graph(data)
        self._update_lab_data()

    @Slot(object)
    def update_graph_view_conv(self, data):
        self._update_conv_graph(data)
        self._update_conv_data()

    @Slot(object)
    def update_graph_view_temper(self, data):
        self._update_temper_graph(data)
        self._update_temper_data()

    @log_exceptions
    def select_type_test(self):
        ind = self.index_type_test
        if ind == 0:
            self.model.set_type_test(TypeTest.LAB)
            self.specif_enable_gui(True, True, False, True)

        elif ind == 1:
            self.model.set_type_test(TypeTest.LAB_HAND)
            self.specif_enable_gui(False, False, False, True)

        elif ind == 2:
            self.model.set_type_test(TypeTest.LAB_CASCADE)
            self.specif_enable_gui(False, False, True, True)

        elif ind == 3:
            self.model.set_type_test(TypeTest.TEMPER)
            self.specif_enable_gui(False, False, False, False)

        elif ind == 4:
            self.model.set_type_test(TypeTest.CONV)
            self.specif_enable_gui(True, True, False, True)

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

    @log_exceptions
    def select_amort(self):
        amort = self.win_amort.amorts.struct.amorts[self.index_amort]
        self.model.set_amort(amort)
        self.specif_ui_fill(amort)

    @log_exceptions
    def specif_ui_fill(self, obj):
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
        if self.model.get_type_test() == TypeTest.TEMPER:
            max_temper = self.model.data_test.finish_temperature
        else:
            max_temper = obj.max_temper
        self.ui.specif_max_temp_lineEdit.setText(str(max_temper))

    def specif_ui_clear(self):
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

    @log_exceptions
    def specif_add_lab_cascade_table(self):
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

    @log_exceptions
    def specif_reduce_lab_cascade_table(self):
            count_rows = self.ui.specif_lab_cascade_speed_table.rowCount()
            if count_rows > 0:
                self.ui.specif_lab_cascade_speed_table.removeRow(count_rows - 1)

    @log_exceptions
    def specif_read_lab_cascade_table(self):
        list_speed = []
        count_rows = self.ui.specif_lab_cascade_speed_table.rowCount()
        if count_rows == 0:
            return False

        else:
            for i in range(count_rows):
                list_speed.append(float(self.ui.specif_lab_cascade_speed_table.item(i, 0).text()))

            self.model.data_test.speed_list = list_speed[:]
            return True

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

    @log_exceptions
    def change_temper_sensor_btn(self):
        if self.model.state_list[6] == 0:
            self.ui.select_temp_sensor_btn.setText('Бесконтактный датчик температуры')
        else:
            self.ui.select_temp_sensor_btn.setText('Контактный датчик температуры')

    @log_exceptions
    def select_temper_sensor(self):
        btn = self.ui.select_temp_sensor_btn.text()
        if 'Бесконтактный' in btn:
            self.model.write_bit_select_temper(1)
            self.ui.select_temp_sensor_btn.setText('Контактный датчик температуры')

        else:
            self.model.write_bit_select_temper(0)
            self.ui.select_temp_sensor_btn.setText('Бесконтактный датчик температуры')

    @log_exceptions
    def specif_continue_btn_click(self):
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
                    type_test = self.model.get_type_test()
                    if type_test == TypeTest.CONV:
                        self._init_conv_graph()
                        self._conv_win_clear()
                        self.conv_test_fill_template()
                        self.begin_test()

                    else:
                        self._lab_win_clear()
                        self.fill_gui_lab_test()
                        if type_test == TypeTest.LAB_CASCADE:
                            flag = self.specif_read_lab_cascade_table()
                            if flag:
                                self._init_lab_graph()
                                self.begin_test()
                            else:
                                self.specif_msg_none_cascade_speed()

                        elif type_test == TypeTest.LAB_HAND:
                            speed = self.specif_lab_input_speed(self.ui.specif_speed_one_lineEdit)
                            if speed:
                                self.model.set_speed_test(speed)
                                self._init_lab_graph()
                                self.begin_test()
                        elif type_test == TypeTest.TEMPER:
                            speed = self.specif_lab_input_speed(self.ui.specif_speed_one_lineEdit)
                            if speed:
                                self.model.set_speed_test(speed)
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

    @log_exceptions
    def flag_push_force_set(self):
        if self.ui.push_force_chb.isChecked():
            self.model.data_test.flag_push_force = True
            self.model.lbl_push_force = 'Динамическая выталкивающая сила'

        else:
            self.model.data_test.flag_push_force = False
            self.model.lbl_push_force = 'Статическая выталкивающая сила'

    @log_exceptions
    def save_log_begin_test(self):
        type_test = self.model.get_type_test()
        amort = self.model.data_test.amort
        if type_test in (TypeTest.LAB_HAND, TypeTest.TEMPER):
            speed = self.model.get_speed_test()
        elif type_test == TypeTest.LAB_CASCADE:
            speed = self.model.data_test.speed_list
        else:
            speed = amort.speed_one

        dimensions = f'{amort.min_length}~{amort.max_length}'
        limit_comp_one = f'{amort.min_comp}~{amort.max_comp}'
        limit_comp_two = f'{amort.min_comp_2}~{amort.max_comp_2}'
        limit_recoil_one = f'{amort.min_recoil}~{amort.max_recoil}'
        limit_recoil_two = f'{amort.min_recoil_2}~{amort.max_recoil_2}'

        txt_log = (f'Start {type_test.name.lower()} --> n={amort.name}, s={speed}, '
                    f'dim={dimensions}, h={amort.hod}, '
                    f's_o={amort.speed_one}, s_t={amort.speed_two}, '
                    f'l_c_o={limit_comp_one}, l_c_t={limit_comp_two}, '
                    f'l_r_o={limit_recoil_one}, l_r_t={limit_recoil_two}, '
                    f'm_t={amort.max_temper}')

        self.logger.info(txt_log)

    @log_exceptions
    def fill_gui_lab_test(self):
        amort = self.model.data_test.amort
        limit_comp_one = f'{amort.min_comp}~{amort.max_comp}'
        limit_comp_two = f'{amort.min_comp_2}~{amort.max_comp_2}'
        limit_recoil_one = f'{amort.min_recoil}~{amort.max_recoil}'
        limit_recoil_two = f'{amort.min_recoil_2}~{amort.max_recoil_2}'

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

    def begin_test(self):
        self.main_stop_state(True)
        self.main_btn_state(False)
        
        type_test = self.model.get_type_test()

        if type_test != TypeTest.CONV:
            if type_test == TypeTest.TEMPER:
                self.model.data_test.reset_temper_test()
                
            self.model.list_lab_result = []
            self.ui.test_repeat_btn.setVisible(False)
            self.ui.lab_speed_le.setReadOnly(True)
            self.ui.test_change_speed_btn.setVisible(False)
            self.ui.test_cancel_btn.setText('ПРЕРВАТЬ ИСПЫТАНИЕ')
            self.ui.test_cancel_btn.setEnabled(True)

        else:
            self.model.list_conv_result = []
            self.ui.test_conv_cancel_btn.setText('ПРЕРВАТЬ ИСПЫТАНИЕ')
            self.ui.test_conv_cancel_btn.setEnabled(True)

        self.save_log_begin_test()

        self.controller.start_test_clicked()

    @log_exceptions
    def _lab_win_clear(self):
        self.ui.lab_GraphWidget.clear()
        self.ui.lab_recoil_le.clear()
        self.ui.lab_recoil_le_2.clear()
        self.ui.lab_comp_le.clear()
        self.ui.lab_comp_le_2.clear()
        self.ui.lab_speed_le.clear()
        self.ui.lab_power_le.clear()
        self.ui.lab_freq_le.clear()
        self.ui.lab_now_temp_le.clear()
        self.ui.lab_max_temp_le.clear()
        self.ui.lab_serial_le.clear()

    def lab_test_win(self):
        self.ui.main_stackedWidget.setCurrentIndex(2)

    def _conv_win_clear(self):
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
        self.conv_test_lamp_slot('one', ColorLampConv.WHITE)
        self.conv_test_lamp_slot('two', ColorLampConv.WHITE)

    def conv_test_win(self):
        self.ui.main_stackedWidget.setCurrentIndex(3)

    @log_exceptions
    def conv_test_fill_template(self):
        amort = self.model.data_test.amort
        self.ui.conv_comp_limit_le.setText(f'{amort.min_comp}~{amort.max_comp}')
        self.ui.conv_recoil_limit_le.setText(f'{amort.min_recoil}~{amort.max_recoil}')
        self.ui.conv_comp_limit_le_2.setText(f'{amort.min_comp_2}~{amort.max_comp_2}')
        self.ui.conv_recoil_limit_le_2.setText(f'{amort.min_recoil_2}~{amort.max_recoil_2}')

        self.ui.lbl_push_force_conv.setText(self.model.lbl_push_force)

    @log_exceptions
    def conv_test_lamp_slot(self, step, color: ColorLampConv):
        border = "border-color: rgb(0, 0, 0);"
        res = f"background-color: {color.value};\n{border}"
        if step == 'one':
            self.ui.first_signal.setStyleSheet(res)
        elif step == 'two':
            self.ui.second_signal.setStyleSheet(res)

    @log_exceptions
    def _update_conv_graph(self, data):
        self.ui.conv_GraphWidget.clear()
        self.graph.fill_graph(data[0], data[1],
                                name=f'{self.model.get_speed_test()} м/с')

    @log_exceptions
    def _update_conv_data(self):
        self.ui.conv_temperture_le.setText(f'{self.model.data_test.temperature}')
        self.ui.conv_push_force_le.setText(f'{self._fill_push_force()}')

        if self.controller.stage == Stage.TEST_SPEED_ONE:
            self.ui.conv_speed_one_le.setText(f'{self.model.get_speed_test()}')
            self.ui.conv_comp_le.setText(f'{self.model.data_test.max_comp}')
            self.ui.conv_recoil_le.setText(f'{self.model.data_test.max_recoil}')

        elif self.controller.stage == Stage.TEST_SPEED_TWO:
            self.ui.conv_speed_two_le.setText(f'{self.model.get_speed_test()}')
            self.ui.conv_comp_le_2.setText(f'{self.model.data_test.max_comp}')
            self.ui.conv_recoil_le_2.setText(f'{self.model.data_test.max_recoil}')

        else:
            pass

    @log_exceptions
    def _update_lab_graph(self, data):
        self.ui.lab_GraphWidget.clear()
        self.graph.fill_graph(data[0], data[1],
                                name=f'{self.model.get_speed_test()} м/с')

    @log_exceptions
    def _update_temper_graph(self, data: tuple):
        self.ui.lab_GraphWidget.clear()
        recoil = data[0]
        comp = data[1]
        temper = data[2]
        
        pen_recoil = pg.mkPen(color='black', width=3)
        pen_comp = pg.mkPen(color='blue', width=3)

        self.graph.fill_graph(temper, recoil,
                                pen=pen_recoil, name='Отбой')
        self.graph.fill_graph(temper, comp,
                                pen=pen_comp, name='Сжатие')

    @log_exceptions
    def _update_lab_data(self):
        if self.model.get_type_test() == TypeTest.LAB:
            if self.controller.stage == Stage.TEST_SPEED_ONE:
                self.ui.lab_comp_le.setText(f'{self.model.data_test.max_comp}')
                self.ui.lab_recoil_le.setText(f'{self.model.data_test.max_recoil}')

            elif self.controller.stage == Stage.TEST_SPEED_TWO:
                self.ui.lab_comp_le_2.setText(f'{self.model.data_test.max_comp}')
                self.ui.lab_recoil_le_2.setText(f'{self.model.data_test.max_recoil}')
        else:
            self.ui.lab_comp_le.setText(f'{self.model.data_test.max_comp}')
            self.ui.lab_recoil_le.setText(f'{self.model.data_test.max_recoil}')
        self.ui.lab_now_temp_le.setText(f'{self.model.data_test.temperature}')
        self.ui.lab_max_temp_le.setText(f'{self.model.data_test.max_temperature}')
        self.ui.lab_speed_le.setText(f'{self.model.get_speed_test()}')
        self.ui.lab_power_le.setText(f'{self.model.data_test.power_amort}')
        self.ui.lab_freq_le.setText(f'{self.model.data_test.freq_piston}')
        self.ui.lab_push_force_le.setText(f'{self._fill_push_force()}')

    @log_exceptions
    def _update_temper_data(self):
        self.ui.lab_comp_le.setText(f'{self.model.data_test.max_comp}')
        self.ui.lab_recoil_le.setText(f'{self.model.data_test.max_recoil}')
        
        self.ui.lab_now_temp_le.setText(f'{self.model.data_test.temperature}')
        self.ui.lab_max_temp_le.setText(f'{self.model.data_test.max_temperature}')
        self.ui.lab_speed_le.setText(f'{self.model.get_speed_test()}')
        self.ui.lab_power_le.setText(f'{self.model.data_test.power_amort}')
        self.ui.lab_freq_le.setText(f'{self.model.data_test.freq_piston}')
        self.ui.lab_push_force_le.setText(f'{self._fill_push_force()}')

    @log_exceptions
    def _fill_push_force(self):
        if self.model.data_test.flag_push_force:
            return self.model.data_test.dynamic_push_force

        else:
            return self.model.data_test.static_push_force

    def repeat_test_clicked_slot(self):
        self.model.flag_repeat = True
        self.begin_test()

    @log_exceptions
    def cancel_test_clicked(self):
        temp = self.ui.test_cancel_btn.text()
        if temp == 'ПРЕРВАТЬ ИСПЫТАНИЕ':
            self.ui.test_cancel_btn.setEnabled(False)
            self.controller.stop_test_clicked()

        elif temp == 'НАЗАД':
            self.model.flag_reset_stop_test()
            self.controller.trav_serv.traverse_install_point('stop_test')
            self.ui.test_cancel_btn.setText('ПРЕРВАТЬ ИСПЫТАНИЕ')

    @log_exceptions
    def change_speed_lab_test(self):
        speed = self.specif_lab_input_speed(self.ui.lab_speed_le)
        if speed:
            self.model.set_speed_test(speed)

    @Slot()
    def slot_lab_test_stop(self):
        self.ui.test_cancel_btn.setEnabled(True)
        self.ui.test_cancel_btn.setText('НАЗАД')
        self.ui.test_repeat_btn.setVisible(True)
        type_test = self.model.get_type_test()
        if type_test == TypeTest.LAB_HAND:
            self.ui.lab_speed_le.setReadOnly(False)
            self.ui.test_change_speed_btn.setVisible(True)
            
        elif type_test in (TypeTest.LAB, TypeTest.LAB_CASCADE):
            self.ui.lab_GraphWidget.clear()
            self.graph.fill_compare_graph(self.model.list_lab_result)

    @Slot()
    def slot_conv_test_stop(self):
        self.ui.test_conv_cancel_btn.setEnabled(True)
        self.ui.test_conv_cancel_btn.setText('НАЗАД')
        self.ui.conv_GraphWidget.clear()
        self.graph.fill_compare_graph(self.model.list_conv_result)

    @log_exceptions
    def cancel_test_conv_clicked(self):
        temp = self.ui.test_conv_cancel_btn.text()
        if temp == 'ПРЕРВАТЬ ИСПЫТАНИЕ':
            self.ui.test_conv_cancel_btn.setEnabled(False)
            self.controller.stop_test_clicked()

        elif temp == 'НАЗАД':
            self.model.flag_reset_stop_test()
            self.model.data_test.serial = str(int(self.model.data_test.serial) + 1)
            self.controller.trav_serv.traverse_install_point('stop_test')
            self.ui.test_conv_cancel_btn.setText('ПРЕРВАТЬ ИСПЫТАНИЕ')

    def cancel_test_slot(self):
        self.main_stop_state(False)
        self.main_btn_state(True)
        self.specif_page()

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
        self.model.set_type_test(TypeTest.SETTINGS)
        self.win_set.start_param_win_set()
        self.win_set.show()

    def close_win_settings(self):
        self.main_btn_state(True)
        self.main_ui_state(True)
        self.win_set.close()
        self.select_type_test()
