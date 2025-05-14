# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QIcon

from logger import my_logger
from ui_py.archive_ui import Ui_WindowArch
from archive import ReadArchive
from calc_data.data_calculation import CalcData
from calc_graph.conv_graph import ConvGraph
from calc_graph.move_graph import MoveGraph
from calc_graph.cascad_graph import CascadeGraph
from calc_graph.triple_graph import TripleGraph
from calc_graph.boost_graph_one import BoostGraphOne
from calc_graph.boost_graph_two import BoostGraphTwo
from calc_graph.temper_graph import TemperGraph
from calc_graph.compare_graph import CompareGraph
from screenshot.save_screen import ScreenSave


class WinSignals(QObject):
    closed = pyqtSignal()


class ArchiveWin(QMainWindow, Ui_WindowArch):
    signals = WinSignals()

    def __init__(self):
        super(ArchiveWin, self).__init__()
        self.logger = my_logger.get_logger(__name__)

    def init_archive_win(self):
        self.setupUi(self)
        self.setWindowIcon(QIcon('icon/archive.png'))
        
        self.calc_data = CalcData()
        self.move_graph = MoveGraph(self.duble_graphwidget)
        self.conv_graph = ConvGraph(self.duble_graphwidget)
        self.cascade_graph = CascadeGraph(self.duble_graphwidget)
        self.triple_graph = TripleGraph(self.triple_graphwidget)
        self.boost_one_graph = BoostGraphOne(self.duble_graphwidget)
        self.boost_two_graph = BoostGraphTwo(self.duble_graphwidget)
        self.temper_graph = TemperGraph(self.duble_graphwidget)
        self.compare_graph = CompareGraph(self.duble_graphwidget)
        self.screen_save = ScreenSave()
        self.archive = ReadArchive()
        
        self.index_date = ''
        self.index_type_test = 0
        self.type_test = 'lab'
        self.index_test = 0
        self.index_type_graph = 0
        self.type_graph_list = []
        self.type_graph = 'move'

        self.compare_data = []

        self._create_statusbar_set()
        self._init_buttons()
        self._read_path_archive()

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
        self.combo_type_test.activated[int].connect(self._change_index_type_test)
        self.combo_test.activated[int].connect(self._change_index_test)
        self.combo_type.activated[int].connect(self._change_type_graph)

    # FIXME
    def _read_path_archive(self):
        try:
            self.compare_data = []
            self.type_graph = 'move'
            self.ind_type_graph = 0
            self.index_date = ''
            self.index_type_test = 0
            self.type_test = 'lab'
            self.index_test = 0
            self.index_conv = 0
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
                self._fill_combo_type_graph(self.index_type_test)
                self._archive_selected()

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_read_path_archive - {e}')
            
    def _change_index_date(self, date):
        try:
            if self.index_date != date:
                self.index_date = date
                self._archive_selected()

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_change_index_date - {e}')
            
    def _change_index_type_test(self, index):
        try:
            if self.index_type_test != index:
                self.index_type_test = index
                self.index_test = 0
                self.combo_test.setCurrentIndex(0)
                self._fill_combo_type_graph(index)
                if index == 0:
                    self.type_test = 'lab'
                elif index == 1:
                    self.type_test = 'cascade'
                elif index == 2:
                    self.type_test = 'conv'
                elif index == 3:
                    self.type_test = 'temper'
                self._archive_selected()

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_change_index_type_test - {e}')
            
    def _change_index_test(self, index):
        try:
            if self.index_test != index:
                self.index_test = index
                self._archive_selected()

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_change_index_test - {e}')
            
    def _fill_combo_type_graph(self, index):
        self.combo_type.clear()
        if index == 1:
            temp = ['Усилие/Скорость']
            self.type_graph_list = ['speed']
        elif index == 3:
            temp = ['Температура/Усилие']
            self.type_graph_list = ['temper']
        else:
            temp = ['Усилие/Перемещение',
                    'Усилие/Скорость №1',
                    'Усилие/Скорость №2',
                    'Усилие/Скорость/Смещение'
                    ]
            self.type_graph_list = ['move',
                                    'boost_1',
                                    'boost_2',
                                    'triple']
            
        self.combo_type.addItems(temp)
        self.index_type_graph = 0
        self.combo_type.setCurrentIndex(0)
            
    def _change_type_graph(self, index):
        try:
            if self.ind_type_graph != index:
                self.ind_type_graph = index
                self.type_graph = self.type_graph_list[index]
                self._archive_selected()                

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_select_type_graph - {e}')










































    def _archive_ui_clear(self):
        try:
            self.duble_graphwidget.clear()
            self.triple_graphwidget.clear()
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
            self.freq_le.setText('')
            self.push_force_le.setText('')
            self._fill_lbl_push_force('-1')

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_archive_ui_clear - {e}')

    def _archive_selected(self):
        try:
            date = self.index_date
            self.combo_test.clear()
            temp_arr = []
            self.archive.select_file(date)
            
            pass
          
            if self.index_type_test == 0:
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

            elif self.index_type_test == 1:
                for i in range(len(self.archive.struct.conv)):
                    temp = (f'{i + 1}) '
                            f'{self.archive.struct.conv[i].time_test} - '
                            f'{self.archive.struct.conv[i].amort.name} - '
                            f'{self.archive.struct.conv[i].serial_number} - '
                            f'{self.archive.struct.conv[i].speed}')
                    temp_arr.append(temp)
                self.index_conv = 0

            if temp_arr:
                self.combo_test.addItems(temp_arr)
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

    def _fill_lbl_push_force(self, index: str):
        txt = ''
        self.push_force_le.setVisible(True)
        if index == '1':
            txt = f'Динамическая выталкивающая сила'

        elif index == '0':
            txt = f'Статическая выталкивающая сила'

        elif index == '2':
            txt = f'Выталкивающая сила не учитывается'
            self.push_force_le.setVisible(False)
        elif index == '-1':
            txt = ''

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
                self.stackedWidget.setCurrentIndex(0)
                self._gui_power_freq_visible(True)
                self.move_graph.gui_graph()
                self._fill_lab_graph()
                self._visible_compare_btn(True)

            elif self.type_graph == 'conv':
                self.stackedWidget.setCurrentIndex(0)
                self._gui_power_freq_visible(True)
                self.conv_graph.gui_graph()
                self._fill_conv_graph()
                self._visible_compare_btn(True)

            elif self.type_graph == 'speed':
                self.stackedWidget.setCurrentIndex(0)
                self._gui_power_freq_visible(False)
                self.cascade_graph.gui_graph()
                self._fill_lab_cascade_graph()
                self._visible_compare_btn(True)

            elif self.type_graph == 'triple':
                self.stackedWidget.setCurrentIndex(1)
                self._gui_power_freq_visible(False)
                self.triple_graph.gui_graph()
                self._fill_triple_graph()
                self._visible_compare_btn(False)

            elif self.type_graph == 'boost_1':
                self.stackedWidget.setCurrentIndex(0)
                self._gui_power_freq_visible(False)
                self.boost_one_graph.gui_graph()
                self._fill_boost_one_graph()
                self._visible_compare_btn(False)

            elif self.type_graph == 'boost_2':
                self.stackedWidget.setCurrentIndex(0)
                self._gui_power_freq_visible(False)
                self.boost_two_graph.gui_graph()
                self._fill_boost_two_graph()
                self._visible_compare_btn(False)

            elif self.type_graph == 'temper':
                self.stackedWidget.setCurrentIndex(0)
                self._gui_power_freq_visible(False)
                self.temper_graph.gui_graph()
                self._fill_temper_graph()
                self._visible_compare_btn(False)

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_archive_graph - {e}')

    def _fill_conv_graph(self):
        try:
            index = self.index_conv
            obj = self.archive.struct.conv[index]
            self.conv_graph.fill_graph(obj)
            response = self.conv_graph.data_graph(obj)

            self._fill_archive_data_gui(obj)
            self._fill_lbl_push_force(obj.flag_push_force)

            self.recoil_le.setText(f'{response.get("recoil", 0)}')
            self.comp_le.setText(f'{response.get("comp", 0)}')
            self.speed_le.setText(f'{response.get("speed", 0)}')
            self.push_force_le.setText(f'{response.get("push_force", 0)}')
            self.power_le.setText(f'{response.get("power", 0)}')
            self.freq_le.setText(f'{response.get("freq", 0)}')

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_fill_conv_graph - {e}')

    def _fill_lab_graph(self):
        try:
            index = self.index_test
            obj = self.archive.struct.tests[index]

            self.move_graph.fill_graph(obj)
            response = self.move_graph.data_graph(obj)
            self._fill_archive_data_gui(obj)
            self._fill_lbl_push_force(obj.flag_push_force)

            self.recoil_le.setText(f'{response.get("recoil", 0)}')
            self.comp_le.setText(f'{response.get("comp", 0)}')
            self.speed_le.setText(f'{response.get("speed", 0)}')
            self.push_force_le.setText(f'{response.get("push_force", 0)}')
            self.power_le.setText(f'{response.get("power", 0)}')
            self.freq_le.setText(f'{response.get("freq", 0)}')

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_fill_lab_graph - {e}')

    def _fill_lab_cascade_graph(self):
        try:
            index = self.index_test_cascade + 1
            data = self.archive.struct.cascade.get(index)

            response = self.cascade_graph.fill_graph(data)

            self._fill_archive_data_gui(data[0])
            self._fill_lbl_push_force(data[0].flag_push_force)

            speed_list = []
            for obj in data:
                speed_list.append(obj.speed)
            self.speed_le.setText(f'{speed_list[0]}~{speed_list[-1]}')

            self.recoil_le.setText(f'{response.get("recoil", 0)}')
            self.comp_le.setText(f'{response.get("comp", 0)}')

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_fill_lab_cascade_graph - {e}')

    def _fill_triple_graph(self):
        try:
            index = self.index_test
            response = self.triple_graph.fill_graph(self.archive.struct.tests[index])

            self._fill_archive_data_gui(self.archive.struct.tests[index])
            self._fill_lbl_push_force('2')
            self.speed_le.setText(f'{self.archive.struct.tests[index].speed}')

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

            self._fill_archive_data_gui(self.archive.struct.tests[index])
            self.speed_le.setText(f'{self.archive.struct.tests[index].speed}')
            self._fill_lbl_push_force(self.archive.struct.tests[index].flag_push_force)

            self.recoil_le.setText(f'{response.get("recoil", 0)}')
            self.comp_le.setText(f'{response.get("comp", 0)}')
            self.push_force_le.setText(f'{response.get("push_force", 0)}')

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_fill_boost_one_graph - {e}')

    def _fill_boost_two_graph(self):
        try:
            index = self.index_test

            response = self.boost_two_graph.fill_graph(self.archive.struct.tests[index])

            self._fill_archive_data_gui(self.archive.struct.tests[index])
            self.speed_le.setText(f'{self.archive.struct.tests[index].speed}')
            self._fill_lbl_push_force(self.archive.struct.tests[index].flag_push_force)

            self.recoil_le.setText(f'{response.get("recoil", 0)}')
            self.comp_le.setText(f'{response.get("comp", 0)}')
            self.push_force_le.setText(f'{response.get("push_force", 0)}')

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_fill_boost_two_graph - {e}')

    def _fill_temper_graph(self):
        try:
            index = self.index_test_temper

            response = self.temper_graph.fill_graph(self.archive.struct.temper[index])

            self._fill_archive_data_gui(self.archive.struct.temper[index])
            self.speed_le.setText(f'{self.archive.struct.temper[index].speed}')
            self._fill_lbl_push_force(self.archive.struct.temper[index].flag_push_force)

            self.recoil_le.setText(f'{response.get("recoil", 0)}')
            self.comp_le.setText(f'{response.get("comp", 0)}')
            self.push_force_le.setText(f'{response.get("push_force", 0)}')

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_fill_temper_graph - {e}')

    def _archive_save_form(self):
        try:
            main_dir = ''
            date_dir = self.index_date
            name = '1'
            if self.type_graph == 'move':
                index = self.index_test
                name = self.screen_save.name_screen_for_save(self.archive.struct.tests[index])
                main_dir = '1_Усилие_Перемещение'

            elif self.type_graph == 'conv':
                index = self.index_conv
                name = self.screen_save.name_screen_for_save(self.archive.struct.conv[index])
                main_dir = '6_Конвейер'

            elif self.type_graph == 'speed':
                index = self.index_test_cascade
                name = self.screen_save.name_screen_for_save_speed(self.archive.struct.cascade[index + 1])
                main_dir = '2_Усилие_Скорость'

            elif self.type_graph == 'triple':
                index = self.index_test
                name = self.screen_save.name_screen_for_save(self.archive.struct.tests[index])
                main_dir = '3_Ход_Скорость_Сопротивление'

            elif self.type_graph == 'boost_1' or self.type_graph == 'boost_2':
                index = self.index_test
                name = self.screen_save.name_screen_for_save(self.archive.struct.tests[index])
                main_dir = '4_Скорость_Сопротивление'

            elif self.type_graph == 'temper':
                index = self.index_test_temper
                name = self.screen_save.name_screen_for_save_temper(self.archive.struct.temper[index])
                main_dir = '5_Температура_Сопротвление'

            self.screen_save.create_dir_for_save(main_dir, date_dir)

            file_dir = f"screens/{main_dir}/{date_dir}/{name}.bmp"
            image = self.screen_save.create_image_for_save(self.frameGeometry())
            image.save(file_dir, "BMP")

            msg = QMessageBox.information(self,
                                          'Внимание',
                                          f'<b style="color: #f00;">'
                                          f'Скриншот успешно сохранён в директории'
                                          )

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_archive_save_form - {e}')

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

            # elif self.type_graph == 'temper':
            #     index = self.index_test_temper

            elif self.type_graph == 'conv':
                index = self.index_conv
                if not self.archive.struct.conv[index] in self.compare_data:
                    self.compare_data.append(self.archive.struct.conv[index])

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
                self.compare_graph.show_graph(self.type_graph, self.compare_data)

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
