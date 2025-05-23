# -*- coding: utf-8 -*-
import numpy as np
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem
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
        self.archive_fill = ArchiveWinFill(self)
        
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

    def _read_path_archive(self):
        try:
            self.combo_dates.clear()
            self.combo_test.clear()
            self.combo_type.clear()
            self.archive.init_arch()

            if len(self.archive.files_arr) == 0:
                self.archive_fill.ui_clear()

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
                self._fill_combo_type_graph(index)
                if index == 0:
                    self.type_test = 'lab'
                    self.data_stWd.setCurrentIndex(0)
                elif index == 1:
                    self.type_test = 'casc'
                    self.data_stWd.setCurrentIndex(2)
                elif index == 2:
                    self.type_test = 'conv'
                    self.data_stWd.setCurrentIndex(0)
                elif index == 3:
                    self.type_test = 'temper'
                    self.data_stWd.setCurrentIndex(1)
                self._archive_selected()

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_change_index_type_test - {e}')

    def _change_index_test(self, index):
        try:
            if self.index_test != index:
                self.index_test = index
                self._archive_graph()

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_change_index_test - {e}')

    def _fill_combo_type_graph(self, index):
        self.combo_type.clear()
        self.type_graph_list.clear()
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
        self.combo_type.setCurrentIndex(0)
        self.index_type_graph = 0
            
    def _change_type_graph(self, index):
        try:
            if self.index_type_graph != index:
                self.index_type_graph = index
                self.type_graph = self.type_graph_list[index]
                self._archive_graph()

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_select_type_graph - {e}')

    def _archive_selected(self):
        try:
            self.combo_test.clear()
            self.archive.select_file(self.index_date)
            
            if self.type_test == 'lab':
                self._archive_fill_combo_test(self.archive.lab)
            elif self.type_test == 'casc':
                self._archive_fill_combo_test(self.archive.cascade)
            elif self.type_test == 'conv':
                self._archive_fill_combo_test(self.archive.conv)
            elif self.type_test == 'temper':
                self._archive_fill_combo_test(self.archive.temper)
            
            self.index_test = 0
            self.combo_test.setCurrentIndex(0)
            
            self._archive_graph()
                
        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_archive_selected - {e}')

    def _archive_fill_combo_test(self, arch_list):
        try:
            if len(arch_list) == 0:
                self.archive_fill.ui_clear()
            
            else:
                test_list = []
                type_graph = self.type_graph_list[self.index_type_graph]
                
                for ind, obj in enumerate(arch_list):
                    first = f'{ind + 1}) {obj.time_test} - {obj.amort.name} - {obj.serial_number} - '
                    
                    if type_graph == 'speed':
                        second = f'{obj.speed_list[0]}~{obj.speed_list[-1]}'
                    elif type_graph == 'temper':
                        second = f'{obj.temper_list[0]}~{obj.temper_list[-1]} °С'
                    else:
                        second = f'{obj.speed}'
                    full = first + second
                    test_list.append(full)
                
                self.combo_test.addItems(test_list)
            
        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_archive_fill_combo_test - {e}')

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
            type_graph = self.type_graph_list[self.index_type_graph]
            if type_graph == 'move':
                self.stackedWidget.setCurrentIndex(0)
                self._visible_compare_btn(True)
                self.move_graph.gui_graph()
                self._fill_lab_graph()
                
            elif type_graph == 'boost_1':
                self.stackedWidget.setCurrentIndex(0)
                self._visible_compare_btn(False)
                self.boost_one_graph.gui_graph()
                self._fill_boost_one_graph()

            elif type_graph == 'boost_2':
                self.stackedWidget.setCurrentIndex(0)
                self._visible_compare_btn(False)
                self.boost_two_graph.gui_graph()
                self._fill_boost_two_graph()
                
            elif type_graph == 'triple':
                self.stackedWidget.setCurrentIndex(1)
                self._visible_compare_btn(False)
                self.triple_graph.gui_graph()
                self._fill_triple_graph()

            elif type_graph == 'speed':
                self.stackedWidget.setCurrentIndex(0)
                self._visible_compare_btn(True)
                self.cascade_graph.gui_graph()
                self._fill_lab_cascade_graph()

            elif type_graph == 'temper':
                self.stackedWidget.setCurrentIndex(0)
                self._visible_compare_btn(False)
                self.temper_graph.gui_graph()
                self._fill_temper_graph()

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_archive_graph - {e}')
            
    def _object_test_is_exists(self, obj):
        try:
            if len(obj) == 0:
                return False
            else:
                return True
            
        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_object_is_exists')
            
    def _select_lab_or_conv(self):
        try:
            if self.type_test == 'lab':
                flag = self._object_test_is_exists(self.archive.lab)
                if flag:
                    return self.archive.lab[self.index_test]
                
            elif self.type_test == 'conv':
                flag = self._object_test_is_exists(self.archive.conv)
                if flag:
                    return self.archive.conv[self.index_test]
                
            return None
            
        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_object_is_exists')
            
    def _fill_lab_graph(self):
        try:
            arch_obj = self._select_lab_or_conv()
                
            if arch_obj is None:
                pass
            
            else:
                self.move_graph.fill_graph(arch_obj)
                response = self.move_graph.data_graph(arch_obj)
                self.archive_fill.ui_fill(arch_obj, 'base', self.index_date)
                self.archive_fill.fill_lbl_push_force(arch_obj.flag_push_force, 'base')

                self.recoil_base_le.setText(f'{response.get("recoil", 0)}')
                self.comp_base_le.setText(f'{response.get("comp", 0)}')
                self.speed_base_le.setText(f'{response.get("speed", 0)}')
                self.push_force_base_le.setText(f'{response.get("push_force", 0)}')
                self.power_base_le.setText(f'{response.get("power", 0)}')
                self.freq_base_le.setText(f'{response.get("freq", 0)}')

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_fill_lab_graph - {e}')
            
    def _fill_boost_one_graph(self):
        try:
            arch_obj = self._select_lab_or_conv()
                
            if arch_obj is None:
                pass
            
            else:
                response = self.boost_one_graph.fill_graph(arch_obj)

                self.archive_fill.ui_fill(arch_obj, 'base', self.index_date)
                self.archive_fill.fill_lbl_push_force(arch_obj.flag_push_force, 'base')

                self.speed_base_le.setText(f'{arch_obj.speed}')
                self.recoil_base_le.setText(f'{response.get("recoil", 0)}')
                self.comp_base_le.setText(f'{response.get("comp", 0)}')
                self.push_force_base_le.setText(f'{response.get("push_force", 0)}')

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_fill_boost_one_graph - {e}')
            
    def _fill_boost_two_graph(self):
        try:
            arch_obj = self._select_lab_or_conv()
                
            if arch_obj is None:
                pass
            
            else:
                response = self.boost_two_graph.fill_graph(arch_obj)

                self.archive_fill.ui_fill(arch_obj, 'base', self.index_date)
                self.archive_fill.fill_lbl_push_force(arch_obj.flag_push_force, 'base')

                self.speed_base_le.setText(f'{arch_obj.speed}')
                self.recoil_base_le.setText(f'{response.get("recoil", 0)}')
                self.comp_base_le.setText(f'{response.get("comp", 0)}')
                self.push_force_base_le.setText(f'{response.get("push_force", 0)}')

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_fill_boost_two_graph - {e}')
            
    def _fill_triple_graph(self):
        try:
            arch_obj = self._select_lab_or_conv()
                
            if arch_obj is None:
                pass
            
            else:
                response = self.triple_graph.fill_graph(arch_obj)

                self.archive_fill.ui_fill(arch_obj, 'base', self.index_date)
                self.archive_fill.fill_lbl_push_force('2', 'base')
                
                self.speed_base_le.setText(f'{arch_obj.speed}')
                self.recoil_base_le.setText(f'{response.get("recoil", 0)}')
                self.comp_base_le.setText(f'{response.get("comp", 0)}')
                self.push_force_base_le.setText(f'{response.get("push_force", 0)}')

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_fill_triple_graph - {e}')

# FIXME tabe data
    def _fill_lab_cascade_graph(self):
        try:
            if len(self.archive.cascade) == 0:
                pass
            else:
                arch_obj = self.archive.cascade[self.index_test]
                response = self.cascade_graph.fill_graph(arch_obj)

                self.archive_fill.ui_fill(arch_obj, 'casc', self.index_date)
                self.archive_fill.fill_lbl_push_force(arch_obj.flag_push_force, 'casc')
                
                self.push_force_casc_le.setText(f'{response.get("push_force", 0)}')
                speed = np.round(response.get('speed'), decimals=2)
                recoil = np.round(response.get('recoil'), decimals=2)
                comp = np.round(response.get('comp'), decimals=2)
                
                for ind, val in enumerate(speed):
                    self.casc_tableWt.setItem(0, ind, QTableWidgetItem(f'{val}'))
                    self.casc_tableWt.setItem(1, ind, QTableWidgetItem(f'{recoil[ind]}'))
                    self.casc_tableWt.setItem(2, ind, QTableWidgetItem(f'{comp[ind]}'))

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in archive_win/_fill_lab_cascade_graph - {e}')

    def _fill_temper_graph(self):
        try:
            if len(self.archive.temper) == 0:
                pass
            else:
                arch_obj = self.archive.temper[self.index_test]

                response = self.temper_graph.fill_graph(arch_obj)

                self.archive_fill.ui_fill(arch_obj, 'temper', self.index_date)
                self.archive_fill.fill_lbl_push_force(arch_obj.flag_push_force, 'temper')

                self.speed_temp_le.setText(f'{arch_obj.speed}')
                self.begin_temp_le.setText(f'{arch_obj.temper_list[0]}')
                self.max_temp_le.setText(f'{arch_obj.temper_list[-1]}')
                
                self.recoil_begin_temp_le.setText(f'{response.get("recoil")[0]}')
                self.recoil_end_temp_le.setText(f'{response.get("recoil")[-1]}')
                self.comp_begin_temp_le.setText(f'{response.get("comp")[0]}')
                self.comp_end_temp_le.setText(f'{response.get("comp")[-1]}')
                self.push_force_temp_le.setText(f'{response.get("push_force")}')

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


class ArchiveWinFill:
    def __init__(self, widget):
        self.logger = my_logger.get_logger(__name__)
        self.widget = widget
        
    def ui_clear(self):
        try:
            self.widget.duble_graphwidget.clear()
            self.widget.triple_graphwidget.clear()
            
            self.base_frame_clear()
            self.ui_base_clear()
            self.ui_casc_clear()
            self.ui_temp_clear()
            
        except Exception as e:
            self.logger.error(e)
            
    def base_frame_clear(self):
        try:
            self.widget.name_le.setText('')
            self.widget.operator_le.setText('')
            self.widget.serial_le.setText('')
            self.widget.date_le.setText('')
            
        except Exception as e:
            self.logger.error(e)
            
    def ui_base_clear(self):
        try:
            self.widget.recoil_base_le.setText('')
            self.widget.comp_base_le.setText('')
            self.widget.speed_set_1_base_le.setText('')
            self.widget.limit_recoil_1_base_le.setText('')
            self.widget.limit_comp_1_base_le.setText('')
            self.widget.speed_set_2_base_le.setText('')
            self.widget.limit_recoil_2_base_le.setText('')
            self.widget.limit_comp_2_base_le.setText('')
            self.widget.power_base_le.setText('')
            self.widget.freq_base_le.setText('')
            self.widget.speed_base_le.setText('')
            self.widget.hod_base_le.setText('')
            self.widget.max_temp_base_le.setText('')
            self.widget.push_force_base_le.setText('')
            
            self.fill_lbl_push_force('-1', 'base')
            
        except Exception as e:
            self.logger.error(e)
            
    def ui_casc_clear(self):
        try:
            self.widget.hod_casc_le.setText('')
            self.widget.max_temp_casc_le.setText('')
            self.widget.push_force_casc_le.setText('')
            self.widget.casc_tableWt.clear()
            
            self.fill_lbl_push_force('-1', 'casc')
            
        except Exception as e:
            self.logger.error(e)
            
    def ui_temp_clear(self):
        try:
            self.widget.recoil_begin_temp_le.setText('')
            self.widget.recoil_end_temp_le.setText('')
            self.widget.comp_begin_temp_le.setText('')
            self.widget.comp_end_temp_le.setText('')
            self.widget.speed_temp_le.setText('')
            self.widget.hod_temp_le.setText('')
            self.widget.begin_temp_le.setText('')
            self.widget.max_temp_le.setText('')
            self.widget.push_force_temp_le.setText('')
            
            self.fill_lbl_push_force('-1', 'temper')
            
        except Exception as e:
            self.logger.error(e)
            
    def fill_lbl_push_force(self, index: str, tag: str):
        try:
            txt = ''
            if tag == 'base':
                obj_lbl = self.widget.lbl_base_push_force
                obj_le = self.widget.push_force_base_le
            elif tag == 'casc':
                obj_lbl = self.widget.lbl_casc_push_force
                obj_le = self.widget.push_force_casc_le
            elif tag == 'temper':
                obj_lbl = self.widget.lbl_temp_push_force
                obj_le = self.widget.push_force_temp_le
            obj_le.setVisible(True)
            
            if index == '1':
                txt = f'Динамическая выталкивающая сила'

            elif index == '0':
                txt = f'Статическая выталкивающая сила'

            elif index == '2':
                txt = f'Выталкивающая сила не учитывается'
                obj_le.setVisible(False)
            elif index == '-1':
                txt = ''
                obj_le.setVisible(False)

            obj_lbl.setText(txt)
        
        except Exception as e:
            self.logger.error(e)

    def ui_fill(self, arch_obj, tag, date):
        try:
            self.ui_base_frame_fill(arch_obj, date)
            if tag == 'base':
                self.ui_base_fill(arch_obj)
            elif tag == 'casc':
                self.ui_casc_fill(arch_obj)
            elif tag == 'temper':
                self.ui_temp_fill(arch_obj)
            
        except Exception as e:
            self.logger.error(e)
            
    def ui_base_frame_fill(self, arch_obj, date):
        try:
            self.widget.name_le.setText(f'{arch_obj.amort.name}')
            self.widget.operator_le.setText(f'{arch_obj.operator_rank} {arch_obj.operator_name}')
            self.widget.serial_le.setText(f'{arch_obj.serial_number}')
            self.widget.date_le.setText(f'{date} - {arch_obj.time_test}')
            
        except Exception as e:
            self.logger.error(e)
            
    def ui_base_fill(self, arch_obj):
        try:
            limit_recoil = f'{arch_obj.amort.min_recoil} - {arch_obj.amort.max_recoil}'
            limit_recoil_2 = f'{arch_obj.amort.min_recoil_2} - {arch_obj.amort.max_recoil_2}'
            limit_comp = f'{arch_obj.amort.min_comp} - {arch_obj.amort.max_comp}'
            limit_comp_2 = f'{arch_obj.amort.min_comp_2} - {arch_obj.amort.max_comp_2}'
            
            self.widget.speed_set_1_base_le.setText(f'{arch_obj.amort.speed_one}')
            self.widget.speed_set_2_base_le.setText(f'{arch_obj.amort.speed_two}')
            self.widget.limit_recoil_1_base_le.setText(limit_recoil)
            self.widget.limit_recoil_2_base_le.setText(limit_recoil_2)
            self.widget.limit_comp_1_base_le.setText(limit_comp)
            self.widget.limit_comp_2_base_le.setText(limit_comp_2)
            self.widget.max_temp_base_le.setText(f'{arch_obj.amort.max_temper}')
            self.widget.hod_base_le.setText(f'{arch_obj.amort.hod}')
            
        except Exception as e:
            self.logger.error(e)
            
    def ui_casc_fill(self, arch_obj):
        try:
            self.widget.hod_casc_le.setText(f'{arch_obj.amort.hod}')
            self.widget.max_temp_casc_le.setText(f'{arch_obj.amort.max_temper}')
            
        except Exception as e:
            self.logger.error(e)
            
    def ui_temp_fill(self, arch_obj):
        try:
            self.widget.hod_temp_le.setText(f'{arch_obj.amort.hod}')
            
        except Exception as e:
            self.logger.error(e)
