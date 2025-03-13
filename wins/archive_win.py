# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QIcon
from PIL import ImageGrab
import pyqtgraph as pg
import os

from logger import my_logger
from ui_py.archive_ui import Ui_WindowArch
from archive import ReadArchive
from calc_data.data_calculation import CalcData
from calc_graph.move_graph import MoveGraph
from calc_graph.cascad_graph import CascadeGraph
from calc_graph.triple_graph import TripleGraph
from calc_graph.boost_graph_one import BoostGraphOne
from calc_graph.boost_graph_two import BoostGraphTwo
from calc_graph.temper_graph import TemperGraph


class WinSignals(QObject):
    closed = pyqtSignal()


class ArchiveWin(QMainWindow, Ui_WindowArch):
    signals = WinSignals()

    def __init__(self):
        super(ArchiveWin, self).__init__()
        try:
            self.logger = my_logger.get_logger(__name__)
            self.setupUi(self)
            self.setWindowIcon(QIcon('icon/archive.png'))
            self.hide()

            self.calc_data = CalcData()
            self.move_graph = MoveGraph(self.graphwidget)
            self.cascade_graph = CascadeGraph(self.graphwidget)
            self.triple_graph = TripleGraph(self.graphwidget)
            self.boost_one_graph = BoostGraphOne(self.graphwidget)
            self.boost_two_graph = BoostGraphTwo(self.graphwidget)
            self.temper_graph = TemperGraph(self.graphwidget)
            self.archive = ReadArchive()

            self.compare_data = []
            self.type_graph = 'move'
            self.ind_type_test = 0
            self.index_date = ''
            self.index_test = 0
            self.index_test_cascade = 0
            self.index_test_temper = 0
            self.color_pen = ['black',
                              'blue',
                              'green',
                              'orange',
                              'purple',
                              'brown',
                              'olive',
                              'cyan',
                              'yellow',
                              'pink',
                              'grey',
                              'red']

            self._create_statusbar_set()
            self._init_buttons()

        except Exception as e:
            self.logger.error(e)

    def closeEvent(self, event):
        self.signals.closed.emit()

    def _create_statusbar_set(self):
        self.statusbar = self.statusBar()
        self.statusbar.showMessage('Окно чтения архива испытаний')

    def _statusbar_set_ui(self, txt_bar):
        try:
            self.statusbar.showMessage(txt_bar)

        except Exception as e:
            self.logger.error(e)

    def _init_buttons(self):
        self.btn_exit.clicked.connect(self.close)
        self.btn_print.setVisible(False)
        self.btn_save.clicked.connect(self._archive_save_form)
        self.btn_compare.clicked.connect(self._add_compare_data)
        self.btn_clier.clicked.connect(self._clear_compare_data)
        self.btn_show.clicked.connect(self._show_compare_data)

        self.combo_dates.activated[str].connect(self._change_index_date)
        self.combo_test.activated[int].connect(self._change_index_test)
        self.combo_type.activated[int].connect(self._change_type_graph)

    def read_path_archive(self):
        try:
            self.compare_data = []
            self.type_graph = 'move'
            self.ind_type_test = 0
            self.index_date = ''
            self.index_test = 0
            self.index_test_cascade = 0
            self.index_test_temper = 0

            self.combo_dates.clear()
            self.combo_test.clear()
            self.archive.init_arch()

            if len(self.archive.files_arr) == 0:
                self._archive_ui_clear()

            else:
                self.combo_dates.addItems(self.archive.files_name_sort)
                self.combo_dates.setCurrentIndex(0)
                self.index_date = self.archive.files_name_sort[0]
                self._archive_selected()

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/read_path_archive - {e}')

    def _archive_ui_clear(self):
        try:
            self.graphwidget.clear()
            self.name_le.setText('')
            self.operator_le.setText('')
            self.speed_set_1_le.setText('')
            self.limit_recoil_1_le.setText('')
            self.limit_comp_1_le.setText('')
            self.speed_set_2_le.setText('')
            self.limit_recoil_2_le.setText('')
            self.limit_comp_2_le.setText('')
            self.recoil_le.setText('')
            self.comp_le.setText('')
            self.serial_le.setText('')
            self.date_le.setText('')
            self.speed_le.setText('')
            self.max_temp_le.setText('')
            self.hod_le.setText('')
            self.power_le.setText('')
            self.push_force_le.setText('')

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_archive_ui_clear - {e}')

    def _change_index_date(self, date):
        try:
            if self.index_date != date:
                self.index_date = date
                self._archive_selected()

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_change_index_date - {e}')

    def _change_index_test(self, index):
        try:
            if self.type_graph == 'speed':
                if self.index_test_cascade != index:
                    self.index_test_cascade = index
                    self._archive_test_select()
                    self._archive_graph()

            elif self.type_graph == 'temper':
                if self.index_test_temper != index:
                    self.index_test_temper = index
                    self._archive_test_select()
                    self._archive_graph()

            else:
                if self.index_test != index:
                    self.index_test = index
                    self._archive_test_select()
                    self._archive_graph()

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_change_index_test - {e}')

    def _change_type_graph(self, index):
        try:
            if self.ind_type_test != index:
                self.ind_type_test = index
                if index == 0:
                    self.type_graph = 'move'

                elif index == 1:
                    self.type_graph = 'speed'

                elif index == 2:
                    self.type_graph = 'triple'

                elif index == 3:
                    self.type_graph = 'boost_1'

                elif index == 4:
                    self.type_graph = 'boost_2'

                elif index == 5:
                    self.type_graph = 'temper'

                self._archive_selected()

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_select_type_graph - {e}')

    def _archive_selected(self):
        try:
            date = self.index_date
            self.combo_test.clear()
            temp_arr = []
            self.archive.select_file(date)

            if self.type_graph == 'speed':
                index = 1
                for key, value in self.archive.struct.cascade.items():
                    temp = (f'{index}) '
                            f'{value[0].time_test} - '
                            f'{value[0].amort.name} - '
                            f'{value[0].serial_number} - '
                            f'{value[0].speed}~{value[-1].speed}')
                    temp_arr.append(temp)
                    index += 1

            elif self.type_graph == 'temper':
                for i in range(len(self.archive.struct.temper)):
                    begin_temp = self.archive.struct.temper[i].temper_graph[0]
                    finish_temp = self.archive.struct.temper[i].temper_graph[-1]
                    temp = (f'{i + 1}) '
                            f'{self.archive.struct.temper[i].time_test} - '
                            f'{self.archive.struct.temper[i].amort.name} - '
                            f'{self.archive.struct.temper[i].serial_number} - '
                            f'{begin_temp}~{finish_temp} °С')
                    temp_arr.append(temp)

            else:
                for i in range(len(self.archive.struct.tests)):
                    temp = (f'{i + 1}) '
                            f'{self.archive.struct.tests[i].time_test} - '
                            f'{self.archive.struct.tests[i].amort.name} - '
                            f'{self.archive.struct.tests[i].serial_number} - '
                            f'{self.archive.struct.tests[i].speed}')
                    temp_arr.append(temp)

            self.index_test = 0
            if temp_arr:
                self.combo_test.addItems(temp_arr)
                self._archive_test_select()
                self._archive_graph()
            else:
                self._archive_ui_clear()

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_archive_selected - {e}')

    def _gui_power_freq_visible(self, state):
        try:
            self.power_le.setVisible(state)
            self.power_lbl.setVisible(state)
            self.power_lbl_2.setVisible(state)
            self.freq_le.setVisible(state)

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_gui_power_freq_visible - {e}')

    # FIXME
    def _archive_test_select(self):
        try:
            self.btn_compare.setVisible(True)
            if self.type_graph == 'speed':
                self._pars_lab_cascade_data()

            elif self.type_graph == 'triple':
                self._pars_triple_data()

            elif self.type_graph == 'temper':
                self._pars_temper_data()

            else:
                self._pars_lab_data()

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_archive_test_select - {e}')

    def _pars_lab_data(self):
        try:
            index = self.index_test

            if self.archive.struct.tests[index]:

                self._fill_archive_data_gui(self.archive.struct.tests[index])

                self.speed_le.setText(f'{self.archive.struct.tests[index].speed}')

                self._fill_flag_push_force(self.archive.struct.tests[index].flag_push_force)

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_pars_lab_data - {e}')

    def _pars_lab_cascade_data(self):
        try:
            index = self.index_test_cascade
            if not self.archive.struct.cascade.get(index + 1) is None:
                data = self.archive.struct.cascade.get(index + 1)
                self._fill_archive_data_gui(data[0])

                self._fill_flag_push_force(data[0].flag_push_force)

                speed_list = []
                for obj in data:
                    speed_list.append(obj.speed)

                self.speed_le.setText(f'{speed_list[0]}~{speed_list[-1]}')

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_pars_lab_cascade_data - {e}')

    def _pars_triple_data(self):
        try:
            index = self.index_test
            if self.archive.struct.tests[index]:

                self._fill_archive_data_gui(self.archive.struct.tests[index])

                self.speed_le.setText(f'{self.archive.struct.tests[index].speed}')

                self._fill_flag_push_force('2')

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_pars_triple_data - {e}')

    def _pars_temper_data(self):
        try:
            index = self.index_test_temper
            if self.archive.struct.temper[index]:
                self._fill_archive_data_gui(self.archive.struct.temper[index])

                self.speed_le.setText(f'{self.archive.struct.temper[index].speed}')
                self._fill_flag_push_force(self.archive.struct.temper[index].flag_push_force)

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_pars_temper_data - {e}')

    def _fill_archive_data_gui(self, obj):
        try:
            user_name = obj.operator_name
            user_rank = obj.operator_rank

            select_archive = self.archive.files_name_arr[self.archive.index_archive]
            time_test = obj.time_test

            min_comp = obj.amort.min_comp
            min_comp_2 = obj.amort.min_comp_2
            max_comp = obj.amort.max_comp
            max_comp_2 = obj.amort.max_comp_2
            min_recoil = obj.amort.min_recoil
            min_recoil_2 = obj.amort.min_recoil_2
            max_recoil = obj.amort.max_recoil
            max_recoil_2 = obj.amort.max_recoil_2

            self.name_le.setText(f'{obj.amort.name}')
            self.operator_le.setText(f'{user_rank} {user_name}')
            self.speed_set_1_le.setText(f'{obj.amort.speed_one}')
            self.speed_set_2_le.setText(f'{obj.amort.speed_two}')
            self.limit_recoil_1_le.setText(f'{min_recoil} - {max_recoil}')
            self.limit_recoil_2_le.setText(f'{min_recoil_2} - {max_recoil_2}')
            self.limit_comp_1_le.setText(f'{min_comp} - {max_comp}')
            self.limit_comp_2_le.setText(f'{min_comp_2} - {max_comp_2}')
            self.serial_le.setText(f'{obj.serial_number}')
            self.date_le.setText(f'{select_archive} - {time_test}')
            self.max_temp_le.setText(f'{obj.amort.max_temper}')
            self.hod_le.setText(f'{obj.amort.hod}')

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_fill_archive_data_gui - {e}')

    def _fill_flag_push_force(self, index: str):
        txt = ''
        self.push_force_le.setVisible(True)
        if index == '1':
            txt = f'Динамическая выталкивающая сила'

        elif index == '0':
            txt = f'Статическая выталкивающая сила'

        elif index == '2':
            txt = f'Выталкивающая сила не учитывается'
            self.push_force_le.setVisible(False)

        self.lbl_push_force.setText(txt)

    def _visible_compare_btn(self, state):
        try:
            self.btn_compare.setVisible(state)
            self.btn_clier.setVisible(state)
            self.btn_show.setVisible(state)

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_visible_compare_btn - {e}')

    def _archive_graph(self):
        try:
            if self.type_graph == 'move':
                self._gui_power_freq_visible(True)
                self.move_graph.gui_graph()
                self._fill_lab_graph()
                self._visible_compare_btn(True)

            elif self.type_graph == 'speed':
                self._gui_power_freq_visible(False)
                self.cascade_graph.gui_graph()
                self._fill_lab_cascade_graph()
                self._visible_compare_btn(True)

            elif self.type_graph == 'triple':
                self._gui_power_freq_visible(False)
                self.triple_graph.gui_graph()
                self._fill_triple_graph()
                self._visible_compare_btn(False)

            elif self.type_graph == 'boost_1':
                self._gui_power_freq_visible(False)
                self.boost_one_graph.gui_graph()
                self._fill_boost_one_graph()
                self._visible_compare_btn(False)

            elif self.type_graph == 'boost_2':
                self._gui_power_freq_visible(False)
                self.boost_two_graph.gui_graph()
                self._fill_boost_two_graph()
                self._visible_compare_btn(False)

            elif self.type_graph == 'temper':
                self._gui_power_freq_visible(False)
                self.temper_graph.gui_graph()
                self._fill_temper_graph()
                self._visible_compare_btn(False)

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_archive_graph - {e}')

    def _fill_lab_graph(self):
        try:
            index = self.index_test

            response = self.move_graph.fill_graph(self.archive.struct.tests[index])

            self.recoil_le.setText(f'{response.get("recoil", 0)}')
            self.comp_le.setText(f'{response.get("comp", 0)}')
            self.push_force_le.setText(f'{response.get("push_force", 0)}')
            self.power_le.setText(f'{response.get("power", 0)}')
            self.freq_le.setText(f'{response.get("freq", 0)}')

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_fill_lab_graph - {e}')

    def _fill_lab_cascade_graph(self):
        try:
            index = self.index_test_cascade + 1
            response = self.cascade_graph.fill_graph(self.archive.struct.cascade.get(index))

            self.recoil_le.setText(f'{response.get("recoil", 0)}')
            self.comp_le.setText(f'{response.get("comp", 0)}')

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_fill_lab_cascade_graph - {e}')

    def _fill_triple_graph(self):
        try:
            index = self.index_test
            response = self.triple_graph.fill_graph(self.archive.struct.tests[index])

            self.recoil_le.setText(f'{response.get("recoil", 0)}')
            self.comp_le.setText(f'{response.get("comp", 0)}')
            self.push_force_le.setText(f'{response.get("push_force", 0)}')

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_fill_triple_graph - {e}')

    def _fill_boost_one_graph(self):
        try:
            index = self.index_test

            response = self.boost_one_graph.fill_graph(self.archive.struct.tests[index])

            self.recoil_le.setText(f'{response.get("recoil", 0)}')
            self.comp_le.setText(f'{response.get("comp", 0)}')
            self.push_force_le.setText(f'{response.get("push_force", 0)}')

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_fill_boost_graph - {e}')

    def _fill_boost_two_graph(self):
        try:
            index = self.index_test

            response = self.boost_two_graph.fill_graph(self.archive.struct.tests[index])

            self.recoil_le.setText(f'{response.get("recoil", 0)}')
            self.comp_le.setText(f'{response.get("comp", 0)}')
            self.push_force_le.setText(f'{response.get("push_force", 0)}')

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_fill_boost_graph - {e}')

    def _fill_temper_graph(self):
        try:
            index = self.index_test_temper

            response = self.temper_graph.fill_graph(self.archive.struct.temper[index])

            self.recoil_le.setText(f'{response.get("recoil", 0)}')
            self.comp_le.setText(f'{response.get("comp", 0)}')
            self.push_force_le.setText(f'{response.get("push_force", 0)}')

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_fill_temper_graph - {e}')

    def _archive_save_form(self):
        try:
            rect = self.frameGeometry()
            pos = rect.getRect()
            x = pos[0] + 1
            y = pos[1] + 80
            height = 820
            width = 1024

            image = ImageGrab.grab((x, y, x + width, y + height))
            main_dir = ''
            date_dir = self.index_date
            name = '1'
            if self.type_graph == 'move':
                index = self.index_test
                name = self._name_screen_for_save(self.archive.struct.tests[index])
                main_dir = '1_Усилие_Перемещение'

            elif self.type_graph == 'speed':
                index = self.index_test_cascade
                name = self._name_screen_for_save_speed(self.archive.struct.cascade[index + 1])
                main_dir = '2_Усилие_Скорость'

            elif self.type_graph == 'triple':
                index = self.index_test
                name = self._name_screen_for_save(self.archive.struct.tests[index])
                main_dir = '3_Ход_Скорость_Сопротивление'

            elif self.type_graph == 'boost_1' or self.type_graph == 'boost_2':
                index = self.index_test
                name = self._name_screen_for_save(self.archive.struct.tests[index])
                main_dir = '4_Скорость_Сопротивление'

            elif self.type_graph == 'temper':
                index = self.index_test_temper
                name = self._name_screen_for_save_temper(self.archive.struct.temper[index])
                main_dir = '5_Температура_Сопротвление'

            self._create_dir_for_save(main_dir)
            file_dir = f"screens/{main_dir}/{date_dir}/{name}.bmp"
            image.save(file_dir, "BMP")

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_archive_save_form - {e}')

    def _create_dir_for_save(self, main_dir):
        try:
            date_dir = self.index_date
            directory = f'screens/{main_dir}/{date_dir}'
            os.makedirs(directory, exist_ok=True)

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_create_dir_for_save - {e}')

    def _name_screen_for_save(self, obj):
        try:
            time = obj.time_test.replace(':', '.')
            name = (f'{time}_'
                    f'{obj.amort.name}_'
                    f'{obj.serial_number}_'
                    f'{obj.speed}')

            return name

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_name_screen_for_save - {e}')

    def _name_screen_for_save_speed(self, obj):
        try:
            time = obj[0].time_test.replace(':', '.')
            name = (f'{time}_'
                    f'{obj[0].amort.name}_'
                    f'{obj[0].serial_number}_'
                    f'{obj[0].speed}~{obj[-1].speed}')

            return name

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_name_screen_for_save_speed - {e}')

    def _name_screen_for_save_temper(self, obj):
        try:
            time = obj.time_test.replace(':', '.')
            begin_temp = obj.temper_graph[0]
            finish_temp = obj.temper_graph[-1]
            name = (f'{time}_'
                    f'{obj.amort.name}_'
                    f'{obj.serial_number}_'
                    f'{begin_temp}~{finish_temp} °С')

            return name

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_name_screen_for_save_temper - {e}')

    def _clear_compare_data(self):
        try:
            if len(self.compare_data) > 0:
                self.compare_data.clear()
                self.read_path_archive()

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_clear_compare_data - {e}')

    def _add_compare_data(self):
        try:
            if self.type_graph == 'speed':
                index = self.index_test_cascade
                if not self.archive.struct.cascade[index + 1] in self.compare_data:
                    self.compare_data.append(self.archive.struct.cascade[index + 1])

            elif self.type_graph == 'temper':
                index = self.index_test_temper

            else:
                index = self.index_test
                if not self.archive.struct.tests[index] in self.compare_data:
                    self.compare_data.append(self.archive.struct.tests[index])
            self.btn_compare.setVisible(False)

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_add_compare_data - {e}')

    def _show_compare_data(self):
        try:
            if 0 < len(self.compare_data) < 13:
                self._show_graph(self.compare_data)

            elif len(self.compare_data) == 0:
                pass

            else:
                msg = QMessageBox.information(self,
                                              'Внимание',
                                              f'<b style="color: #f00;">'
                                              f'Число выбранных графиков для сравнения превышает допустимое число'
                                              f'Выбрано - {len(self.compare_data)}, допустимо - 12</b>'
                                              )

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_show_compare_data - {e}')

    def _show_graph(self, obj):
        try:
            self.graphwidget.plot(clear=True)
            if self.type_graph == 'move':
                for graph in obj:
                    x_list = graph.move_list
                    y_list = graph.force_list
                    pen = pg.mkPen(color=self.color_pen[obj.index(graph)], width=3)

                    name = (f'{graph.time_test} - '
                            f'{graph.amort.name} - '
                            f'{graph.serial_number} - '
                            f'{graph.speed}')

                    self.graphwidget.plot(x_list, y_list, pen=pen, name=name)

            elif self.type_graph == 'speed':
                for arch_obj in obj:
                    speed_list = [0]
                    comp_list = [0]
                    recoil_list = [0]
                    push_force = 0
                    for graph in arch_obj:
                        speed_list.append(float(graph.speed))
                        flag_push_force = graph.flag_push_force
                        if flag_push_force == '1':
                            push_force = float(graph.dynamic_push_force)

                        elif flag_push_force == '0':
                            push_force = float(graph.static_push_force)

                        recoil, comp = self.calc_data.middle_min_and_max_force(graph.force_list)

                        recoil_list.append(round(recoil + push_force, 2))
                        comp_list.append(round(comp * (-1) + push_force, 2))

                    x_list = [*speed_list[::-1], *speed_list]
                    y_list = [*comp_list[::-1], *recoil_list]

                    pen = pg.mkPen(color=self.color_pen[obj.index(arch_obj)], width=3)

                    name = (f'{arch_obj[0].time_test} - '
                            f'{arch_obj[0].amort.name} - '
                            f'{arch_obj[0].serial_number} - '
                            f'{arch_obj[0].speed}~{arch_obj[-1].speed}')

                    self.graphwidget.plot(x_list, y_list, pen=pen, name=name)

                self.cascade_graph.limit_line_graph(obj[0][0])

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_show_graph - {e}')
