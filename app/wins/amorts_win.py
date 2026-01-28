# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QMainWindow
from PySide6.QtGui import QIcon
from PySide6.QtCore import QObject, Signal

from app.ui_py.amorts_ui import Ui_AmortsWindow
from app.wins.amorts_new import AmortNew
from scripts.amorts import Amort
from scripts.logger import my_logger


class WinSignals(QObject):
    closed = Signal()


class AmortWin(QMainWindow, Ui_AmortsWindow):
    signals = WinSignals()

    def __init__(self):
        super(AmortWin, self).__init__()
        try:
            self.logger = my_logger.get_logger(__name__)
            self.action = ''
            self.amorts = None
            self.new_amort_win = AmortNew()
            self.setupUi(self)
            self.setWindowIcon(QIcon('icon/shock-absorber.png'))
            self.hide()
            self._create_statusbar_set()
            self._init_ui()
            self._init_signals()
            self._init_buttons()

        except Exception as e:
            self.logger.error(e)

    def _init_ui(self):
        try:
            self.frame_quest.setVisible(False)
            self.frame_warning.setVisible(False)
            self._amort_init()

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in amorts_win/_init_ui - {e}')

    def _init_signals(self):
        try:
            self.new_amort_win.signals.closed.connect(self._close_new_amort_win)
            self.new_amort_win.signals.save_amort.connect(self._amort_add)

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in amorts_win/_init_signals - {e}')

    def closeEvent(self, event):
        self.signals.closed.emit()

    def _create_statusbar_set(self):
        self.statusbar = self.statusBar()
        self.statusbar.showMessage('Окно менеджмента амортизаторов')

    def _statusbar_set_ui(self, txt_bar):
        try:
            self.statusbar.showMessage(txt_bar)

        except Exception as e:
            self.logger.error(e)

    def _init_buttons(self):
        self.btn_exit.clicked.connect(self.close)
        self.btn_del.clicked.connect(self._btn_del_click)
        self.btn_add.clicked.connect(self._open_new_amort_win)
        self.btn_change.clicked.connect(self._open_change_amort_win)
        self.btn_ok_quest.clicked.connect(self._ok_question)
        self.btn_cancel_quest.clicked.connect(self._cancel_question)
        self.btn_ok_warning.clicked.connect(self._ok_warning)

    def _amort_init(self):
        try:
            self.amorts = Amort()
            self._amorts_update()

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in amorts_win/_amort_init - {e}')

    def _amorts_update(self):
        try:
            self.amorts.update_amort_list()
            self.combo_Names.clear()
            if len(self.amorts.config.sections()) == 0:
                self.btn_del.setEnabled(False)
                self.btn_change.setEnabled(False)
                self._amorts_ui_clear()

            else:
                self.combo_Names.addItems(self.amorts.names)
                self.combo_Names.setCurrentIndex(0)
                self.amorts.current_index = 0
                self.combo_Names.activated[int].connect(self._amort_select)
                self._amort_select(0)
                self.btn_del.setEnabled(True)
                self.btn_change.setEnabled(True)

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in amorts_win/_amorts_update - {e}')

    def _amorts_ui_clear(self):
        try:
            self.lbl_hod.setText('')
            self.lbl_adapter.setText('')
            self.lbl_speed_1.setText('')
            self.lbl_speed_2.setText('')
            self.lbl_length_min.setText('')
            self.lbl_length_max.setText('')
            self.lbl_comp_min.setText('')
            self.lbl_comp_max.setText('')
            self.lbl_recoil_min.setText('')
            self.lbl_recoil_max.setText('')
            self.lbl_temper.setText('')

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in amorts_win/_amorts_ui_clear - {e}')

    def _amort_select(self, index):
        try:
            self.amorts.current_index = index

            self.lbl_hod.setText(str(self.amorts.struct.amorts[index].hod))
            self.lbl_adapter.setText(str(self.amorts.struct.amorts[index].adapter))
            self.lbl_speed_1.setText(str(self.amorts.struct.amorts[index].speed_one))
            self.lbl_speed_2.setText(str(self.amorts.struct.amorts[index].speed_two))
            self.lbl_length_min.setText(str(self.amorts.struct.amorts[index].min_length))
            self.lbl_length_max.setText(str(self.amorts.struct.amorts[index].max_length))
            self.lbl_comp_min.setText(str(self.amorts.struct.amorts[index].min_comp))
            self.lbl_comp_min_2.setText(str(self.amorts.struct.amorts[index].min_comp_2))
            self.lbl_comp_max.setText(str(self.amorts.struct.amorts[index].max_comp))
            self.lbl_comp_max_2.setText(str(self.amorts.struct.amorts[index].max_comp_2))
            self.lbl_recoil_min.setText(str(self.amorts.struct.amorts[index].min_recoil))
            self.lbl_recoil_min_2.setText(str(self.amorts.struct.amorts[index].min_recoil_2))
            self.lbl_recoil_max.setText(str(self.amorts.struct.amorts[index].max_recoil))
            self.lbl_recoil_max_2.setText(str(self.amorts.struct.amorts[index].max_recoil_2))
            self.lbl_temper.setText(str(self.amorts.struct.amorts[index].max_temper))

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in amorts_win/_amort_select - {e}')

    def _btn_del_click(self):
        try:
            self.action = 'del'
            ind = self.amorts.current_index
            self.txt_quest.setText('Вы действительно хотите<BR>удалить амортизатор<BR>' +
                                      self.amorts.names[ind] + '<BR>из списка?')
            self._set_frame_question(True)

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in amorts_win/_btn_del_click - {e}')

    def _amort_delete(self):
        try:
            ind = self.amorts.current_index
            amort = self.amorts.struct.amorts[ind]

            name = amort.name
            dimensions = f'{amort.min_length} - {amort.max_length}'
            hod = f'{amort.hod}'
            adapter = f'{amort.adapter}'
            speed_one = f'{amort.speed_one}'
            limit_comp_one = f'{amort.min_comp} - {amort.max_comp}'
            limit_recoil_one = f'{amort.min_recoil} - {amort.max_recoil}'
            speed_two = f'{amort.speed_two}'
            limit_comp_two = f'{amort.min_comp_2} - {amort.max_comp_2}'
            limit_recoil_two = f'{amort.min_recoil_2} - {amort.max_recoil_2}'
            temper = f'{amort.max_temper}'

            txt_log = f'Amort is delete --> name = {name}, dimensions = {dimensions}, hod = {hod}, ' \
                      f'adapter = {adapter}, speed_one = {speed_one}, limit_comp_one = {limit_comp_one}, ' \
                      f'limit_recoil_one = {limit_recoil_one}, speed_two = {speed_two}, ' \
                      f'limit_comp_two = {limit_comp_two}, limit_recoil_two = {limit_recoil_two}, ' \
                      f'max_temper = {temper}'

            self.logger.info(txt_log)

            self.amorts.delete_amort(ind)

            self._amorts_update()

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in amorts_win/_amort_delete - {e}')

    def _open_new_amort_win(self):
        try:
            self.setDisabled(True)
            self.new_amort_win.start_param_new_amort('new')
            self.new_amort_win.show()

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in amorts_win/_open_new_amort_win - {e}')

    def _open_change_amort_win(self):
        try:
            amort = self.amorts.struct.amorts[self.amorts.current_index]
            self.setDisabled(True)
            self.new_amort_win.start_param_new_amort('change', amort=amort)
            self.new_amort_win.show()

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in amorts_win/_open_change_amort_win - {e}')

    def _close_new_amort_win(self):
        try:
            self.setEnabled(True)
            self.new_amort_win.hide()

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in amorts_win/close_new_amort_win - {e}')

    def _amort_add(self, obj):
        try:
            self.new_amort_win.hide()
            self.setEnabled(True)

            if obj.get('tag') == 'new':
                flag_add = self._check_concurrence_name(obj.get('name'))
                if flag_add:
                    self.amorts.add_amort(obj)
                    obj['tag'] = 'Amort is added'
                    self._save_amort_in_log(obj)

                else:
                    self.txt_warning.setText('Такой амортизатор<BR>уже имеется в списке')
                    self._set_frame_warning(True)

            elif obj.get('tag') == 'change':
                ind = self.amorts.current_index
                self.amorts.change_amort(ind, obj)
                
                obj['tag'] = 'Amort is changed'
                
                self._save_amort_in_log(obj)

            self._amorts_update()

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in amorts_win/_amort_add - {e}')
            
    def _save_amort_in_log(self, obj):
        try:
            txt_log = f'{obj.get("tag")} --> name = {obj.get("name")}, ' \
                      f'dimensions = {obj.get("min_length")} - {obj.get("max_length")}, '\
                      f'hod = {obj.get("hod")}, '\
                      f'adapter = {obj.get("adapter")}, '\
                      f'speed_one = {obj.get("speed_one")}, '\
                      f'limit_comp_one = {obj.get("min_comp")} - {obj.get("max_comp")}, ' \
                      f'limit_recoil_one = {obj.get("min_recoil")} - {obj.get("max_recoil")}, '\
                      f'speed_two = {obj.get("speed_two")}, ' \
                      f'limit_comp_two = {obj.get("min_comp_2")} - {obj.get("max_comp_2")}, '\
                      f'limit_recoil_two = {obj.get("min_recoil_2")} - {obj.get("max_recoil_2")}, ' \
                      f'max_temper = {obj.get("max_temper")}'

            self.logger.info(txt_log[:-1])
            
        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in amorts_win/_save_amort_in_log - {e}')

    def _set_frame_question(self, bool_val):
        self.frame_quest.setVisible(bool_val)
        self.frame_quest.move(20, 60)
        self.frame_btn.setEnabled(not bool_val)

    def _set_frame_warning(self, bool_val):
        self.frame_warning.setVisible(bool_val)
        self.frame_warning.move(20, 60)
        self.frame_btn.setVisible(not bool_val)

    def _ok_warning(self):
        self._set_frame_warning(False)

    def _ok_question(self):
        try:
            if self.action == 'del':
                self._amort_delete()
                self._set_frame_question(False)

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in amorts_win/_ok_question - {e}')

    def _cancel_question(self):
        try:
            self._set_frame_question(False)

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in amorts_win/_cancel_question - {e}')

    def _check_concurrence_name(self, new_name):
        try:
            flag_add = True
            for name in self.amorts.names:
                if name.upper() == new_name.upper():
                    flag_add = False

            return flag_add

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in amorts_win/_check_concurrence_name - {e}')
