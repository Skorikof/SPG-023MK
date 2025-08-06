# -*- coding: utf-8 -*-
import time
import pyqtgraph as pg
from PySide6.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem

from settings import glob_var
from logger import my_logger
from calc_data.data_calculation import CalcData
from calc_graph.test_graph import TestGraph
from ui_py.mainui import Ui_MainWindow
from wins.executors_win import ExecWin
from wins.amorts_win import AmortWin
from wins.archive_win import ArchiveWin


class AppWindow(QMainWindow):
    def __init__(self, model, controller, win_set):
        super(AppWindow, self).__init__()
        self.logger = my_logger.get_logger(__name__)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.model = model
        self.controller = controller
        self.win_set = win_set
        self.calc_data = CalcData()
        self.win_exec = ExecWin()
        self.win_amort = AmortWin()
        self.win_archive = ArchiveWin()

        self._start_param_view()

    def closeEvent(self, event):
        self.model.write_bit_force_cycle(0)
        
        self.controller.timer_process.stop()
        self.model.writer.timer_writer_stop()
        self.model.save_arch.timer_writer_arch_stop()
        self.model.reader_exit()
        
        self.model.threadpool.waitForDone()
        self.model.client.disconnect_client()
        event.accept()

    def _create_statusbar_ui(self):
        self.statusbar = self.statusBar()

    def status_bar_ui(self, txt_bar):
        try:
            self.ui.statusbar.showMessage(txt_bar)

        except Exception as e:
            self.logger.error(e)

    def _start_param_view(self):
        self._init_start_view()
        self._create_statusbar_ui()
        self._init_buttons()
        self._init_signals()

        self._start_page()

    def _init_start_view(self):
        self.tag_msg = 'info'
        self.list_lab = []
        self.dict_lab_cascade = {}
        self.index_amort = 0
        self.index_type_test = 0
        self.bit_temper = None

    def _init_signals(self):
        self.model.signals.connect_ctrl.connect(self._start_page)
        self.model.signals.stbar_msg.connect(self.status_bar_ui)
        self.model.signals.win_set_update.connect(self.update_data_win_settings)
        self.model.signals.update_data_graph.connect(self.update_graph_view)
        self.model.signals.save_koef_force.connect(self.btn_correct_force_slot)

        self.controller.signals.control_msg.connect(self.controller_msg_slot)
        self.controller.signals.traverse_referent_msg.connect(self.msg_traverse_referent)
        self.controller.signals.wait_yellow_btn.connect(self.msg_yellow_btn)
        self.controller.signals.conv_win_test.connect(self.conv_test_win)
        self.controller.signals.lab_win_test.connect(self.lab_test_win)
        self.controller.signals.cancel_test.connect(self.cancel_test_slot)
        self.controller.signals.end_test.connect(self.model.write_end_test_in_archive)
        self.controller.signals.lab_test_stop.connect(self.slot_lab_test_stop)
        self.controller.signals.conv_test_stop.connect(self.slot_conv_test_stop)
        self.controller.signals.save_result_test.connect(self.slot_save_lab_result)
        self.controller.signals.search_hod_msg.connect(self.slot_search_hod)
        self.controller.signals.reset_ui.connect(self.slot_start_page)
        self.controller.steps.signals.conv_result_lamp.connect(self.conv_test_lamp_slot)

        self.win_exec.signals.closed.connect(self.close_win_operator)
        self.win_exec.signals.operator_select.connect(self.operator_select)

        self.win_amort.signals.closed.connect(self.close_win_amort)
        self.win_set.signals.closed.connect(self.close_win_settings)
        self.win_archive.signals.closed.connect(self.close_win_archive)

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

    def _init_lab_graph(self):
        try:
            self.graph = TestGraph(self.ui.lab_GraphWidget)
            self.graph.gui_graph('move')
            self.graph.gui_axis()

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/_init_lab_graph - {e}')

    def _init_conv_graph(self):
        try:
            self.graph = TestGraph(self.ui.conv_GraphWidget)
            self.graph.gui_graph('move')
            self.graph.gui_axis()

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/_init_conv_graph - {e}')
            
    def _init_temp_graph(self):
        try:
            self.graph = TestGraph(self.ui.lab_GraphWidget)
            self.graph.gui_graph('temper')
            self.graph.gui_axis()
            
        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/_init_temp_graph - {e}')

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
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/slot_controller_msg - {e}')

    def msg_traverse_referent(self):
        try:
            txt = 'ОПРЕДЕЛЕНИЕ\nРЕФЕРЕНТНОЙ ТОЧКИ\nТРАВЕРСЫ'
            self.main_ui_msg(txt, 'attention')

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/msg_traverse_referent - {e}')

    def msg_yellow_btn(self):
        try:
            self.ui.ok_message_btn.setText('ЗАПУСК')
            txt = 'НАЖМИТЕ\nЖЁЛТУЮ\nКНОПКУ\nДЛЯ ЗАПУСКА\nИСПЫТАНИЯ'
            self.main_ui_msg(txt, 'question')

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/msg_yellow_btn - {e}')

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

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/main_ui_msg - {e}')

    def btn_main_stop_clicked(self):
        try:
            txt = 'РАБОТА ПРЕРВАНА\nПО КОМАНДЕ\nОПЕРАТОРА'
            tag = 'warning'
            self.main_ui_msg(txt, tag)
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

    def slot_start_page(self):
        try:
            self._start_page()

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/slot_start_page - {e}')

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
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/_start_page - {e}')

    def open_win_operator(self):
        self.main_ui_state(False)
        self.main_btn_state(False)
        self.win_exec.show()

    def operator_select(self, name, rank):
        self.model.operator.name = name
        self.model.operator.rank = rank

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

        if self.model.type_test == 'hand':
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
            type_test = self.model.type_test
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
                self.model.type_test = 'lab'
                self.specif_enable_gui(True, True, False, True)

            elif ind == 1:
                self.model.type_test = 'lab_hand'
                self.specif_enable_gui(False, False, False, True)

            elif ind == 2:
                self.model.type_test = 'lab_cascade'
                self.specif_enable_gui(False, False, True, True)

            elif ind == 3:
                self.model.type_test = 'temper'
                self.specif_enable_gui(False, False, False, False)

            elif ind == 4:
                self.model.type_test = 'conv'
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
            ind = self.index_amort
            self.model.amort = self.win_amort.amorts.struct.amorts[ind]

            self.specif_ui_fill(self.win_amort.amorts.struct.amorts[ind])

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
            if self.model.type_test == 'temper':
                max_temper = self.model.finish_temper
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

            if self.model.amort is None:
                hod = 120
            else:
                hod = self.model.amort.hod

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
            if count_rows <= 30:
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

                self.model.speed_cascade = list_speed[:]
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
            if self.model.state_list[6] == 0:
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
            if self.model.operator.name != '' and self.model.operator.rank != '':
                self.flag_push_force_set()
                self.ui.test_change_speed_btn.setVisible(False)
                self.ui.lab_speed_le.setReadOnly(True)

                flag = self.static_push_force_editing()
                if flag:
                    flag = self.serial_editing_finished()
                    if flag:
                        self.model.serial_number = self.ui.specif_serial_lineEdit.text()
                        self.lab_test_second_force_gui(False)
                        if self.model.type_test == 'conv':
                            self._init_conv_graph()
                            self._conv_win_clear()
                            self.conv_test_fill_template()
                            self.begin_test()

                        else:
                            self._lab_win_clear()
                            self.fill_gui_lab_test()
                            if self.model.type_test == 'lab_cascade':
                                flag = self.specif_read_lab_cascade_table()
                                if flag:
                                    self._init_lab_graph()
                                    self.begin_test()
                                else:
                                    self.specif_msg_none_cascade_speed()

                            elif self.model.type_test == 'lab_hand':
                                speed = self.specif_lab_input_speed(self.ui.specif_speed_one_lineEdit)
                                if speed:
                                    self.model.speed_test = speed
                                    self._init_lab_graph()
                                    self.begin_test()
                            elif self.model.type_test == 'temper':
                                speed = self.specif_lab_input_speed(self.ui.specif_speed_one_lineEdit)
                                if speed:
                                    self.model.speed_test = speed
                                    temper = self.specif_lab_input_temper(self.ui.specif_max_temp_lineEdit)
                                    if temper:
                                        self.model.finish_temper = temper
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
            self.model.static_push_force = push_force

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
                self.model.flag_push_force = True
                self.model.lbl_push_force = 'Динамическая выталкивающая сила'

            else:
                self.model.flag_push_force = False
                self.model.lbl_push_force = 'Статическая выталкивающая сила'

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/flag_push_force_set - {e}')

    def save_log_begin_test(self):
        try:
            if self.model.type_test == 'lab_hand' or self.model.type_test == 'temper':
                speed = self.model.speed_test
            elif self.model.type_test == 'lab_cascade':
                speed = self.model.speed_cascade
            else:
                speed = self.model.amort.speed_one

            name = self.model.amort.name
            dimensions = f'{self.model.amort.min_length} - {self.model.amort.max_length}'
            hod = f'{self.model.amort.hod}'
            speed_one = f'{self.model.amort.speed_one}'
            speed_two = f'{self.model.amort.speed_two}'
            limit_comp_one = f'{self.model.amort.min_comp} - {self.model.amort.max_comp}'
            limit_comp_two = f'{self.model.amort.min_comp_2} - {self.model.amort.max_comp_2}'
            limit_recoil_one = f'{self.model.amort.min_recoil} - {self.model.amort.max_recoil}'
            limit_recoil_two = f'{self.model.amort.min_recoil_2} - {self.model.amort.max_recoil_2}'
            temper = f'{self.model.amort.max_temper}'

            txt_log = (f'Start {self.model.type_test} test --> name = {name}, speed = {speed}, dimensions = {dimensions}, '
                       f'hod = {hod}, speed_one = {speed_one}, speed_two = {speed_two}, '
                       f'limit_comp_one = {limit_comp_one}, limit_comp_two = {limit_comp_two}, '
                       f'limit_recoil_one = {limit_recoil_one}, limit_comp_two = {limit_comp_two}, '
                       f'limit_recoil_two = {limit_recoil_two}, max_temper = {temper}')

            self.logger.info(txt_log)

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/save_log_begin_test - {e}')

    def fill_gui_lab_test(self):
        try:
            name = self.model.amort.name
            hod = f'{self.model.amort.hod}'
            speed_one = f'{self.model.amort.speed_one}'
            speed_two = f'{self.model.amort.speed_two}'
            limit_comp_one = f'{self.model.amort.min_comp} - {self.model.amort.max_comp}'
            limit_comp_two = f'{self.model.amort.min_comp_2} - {self.model.amort.max_comp_2}'
            limit_recoil_one = f'{self.model.amort.min_recoil} - {self.model.amort.max_recoil}'
            limit_recoil_two = f'{self.model.amort.min_recoil_2} - {self.model.amort.max_recoil_2}'

            self.ui.lab_name_le.setText(name)
            self.ui.lab_speed_set_1_le.setText(speed_one)
            self.ui.lab_limit_comp_1_le.setText(limit_comp_one)
            self.ui.lab_limit_recoil_1_le.setText(limit_recoil_one)
            self.ui.lab_speed_set_2_le.setText(speed_two)
            self.ui.lab_limit_comp_2_le.setText(limit_comp_two)
            self.ui.lab_limit_recoil_2_le.setText(limit_recoil_two)
            self.ui.lab_hod_le.setText(hod)

            self.ui.lbl_push_force_lab.setText(self.model.lbl_push_force)
            self.ui.lab_serial_le.setText(f'{self.model.serial_number}')

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/fill_gui_lab_test - {e}')

    def begin_test(self):
        try:
            self.main_stop_state(True)
            self.main_btn_state(False)

            if self.model.type_test != 'conv':
                self.list_lab = []
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
            self.ui.conv_comp_limit_le.setText(f'{self.model.amort.min_comp} - {self.model.amort.max_comp}')
            self.ui.conv_recoil_limit_le.setText(f'{self.model.amort.min_recoil} - {self.model.amort.max_recoil}')
            self.ui.conv_comp_limit_le_2.setText(f'{self.model.amort.min_comp_2} - {self.model.amort.max_comp_2}')
            self.ui.conv_recoil_limit_le_2.setText(f'{self.model.amort.min_recoil_2} - {self.model.amort.max_recoil_2}')

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
                                  name=f'{self.model.speed_test} м/с')

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/_update_conv_graph - {e}')

    def _update_conv_data(self):
        try:
            self.ui.conv_temperture_le.setText(f'{self.model.temper_now}')
            self.ui.conv_push_force_le.setText(f'{self._fill_push_force()}')

            if self.controller.stage == 'test_speed_one':
                self.ui.conv_speed_one_le.setText(f'{self.model.speed_test}')
                self.ui.conv_comp_le.setText(f'{self.model.max_comp}')
                self.ui.conv_recoil_le.setText(f'{self.model.max_recoil}')

            if self.controller.stage == 'test_speed_two':
                self.ui.conv_speed_two_le.setText(f'{self.model.speed_test}')
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
                                  name=f'{self.model.speed_test} м/с')

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
            if self.model.type_test == 'lab':
                if self.controller.stage == 'test_speed_one':
                    self.ui.lab_comp_le.setText(f'{self.model.max_comp}')
                    self.ui.lab_recoil_le.setText(f'{self.model.max_recoil}')

                elif self.controller.stage == 'test_speed_two':
                    self.ui.lab_comp_le_2.setText(f'{self.model.max_comp}')
                    self.ui.lab_recoil_le_2.setText(f'{self.model.max_recoil}')
            else:
                self.ui.lab_comp_le.setText(f'{self.model.max_comp}')
                self.ui.lab_recoil_le.setText(f'{self.model.max_recoil}')

            self.ui.lab_now_temp_le.setText(f'{self.model.temper_now}')
            self.ui.lab_max_temp_le.setText(f'{self.model.temper_max}')
            self.ui.lab_speed_le.setText(f'{self.model.speed_test}')
            self.ui.lab_power_le.setText(f'{self.model.power_amort}')
            self.ui.lab_freq_le.setText(f'{self.model.freq_piston}')
            self.ui.lab_push_force_le.setText(f'{self._fill_push_force()}')

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/_update_lab_data - {e}')

    def _fill_push_force(self):
        try:
            if self.model.flag_push_force:
                return self.model.dynamic_push_force

            else:
                return self.model.static_push_force

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
                self.model.speed_test = speed

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/change_speed_lab_test - {e}')

    def slot_lab_test_stop(self):
        self.ui.test_cancel_btn.setEnabled(True)
        self.ui.test_cancel_btn.setText('НАЗАД')
        self.ui.test_repeat_btn.setVisible(True)

        if self.model.type_test == 'lab_hand':
            self.ui.lab_speed_le.setReadOnly(False)
            self.ui.test_change_speed_btn.setVisible(True)

        elif self.model.type_test == 'lab' or self.model.type_test == 'lab_cascade':
            self.ui.lab_GraphWidget.clear()
            self.graph.fill_compare_graph(self.list_lab)

    def slot_conv_test_stop(self):
        self.ui.test_conv_cancel_btn.setEnabled(True)
        self.ui.test_conv_cancel_btn.setText('НАЗАД')
        self.ui.conv_GraphWidget.clear()
        self.graph.fill_compare_graph(self.list_lab)

    def cancel_test_conv_clicked(self):
        try:
            temp = self.ui.test_conv_cancel_btn.text()

            if temp == 'ПРЕРВАТЬ ИСПЫТАНИЕ':
                self.ui.test_conv_cancel_btn.setEnabled(False)
                self.controller.stop_test_clicked()

            elif temp == 'НАЗАД':
                self.controller.steps_tests.step_stop_test()
                self.model.flag_test_launch = False
                self.model.serial_number = str(int(self.model.serial_number) + 1)
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
        self.model.type_test = 'hand'
        self.win_set.start_param_win_set()
        self.win_set.show()

    def update_data_win_settings(self):
        self.win_set.update_data_win_set()

    def close_win_settings(self):
        self.main_btn_state(True)
        self.main_ui_state(True)
        self.win_set.close()
        self.select_type_test()

    def slot_save_lab_result(self, command):
        try:
            if self.model.type_test == 'lab' or self.model.type_test == 'lab_cascade' or self.model.type_test == 'conv':
                data_dict = {'speed': self.model.speed_test,
                             'move': self.model.move[:],
                             'force': self.model.force[:]}

                self.list_lab.append(data_dict)

            self.model.save_data_in_archive()

            if command == 'end':
                self.model.write_end_test_in_rchive()

        except Exception as e:
            self.logger.error(e)
            self.status_bar_ui(f'ERROR in view/slot_save_lab_result - {e}')
