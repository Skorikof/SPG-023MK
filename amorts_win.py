from PyQt5.QtWidgets import QMainWindow, QDialog
from PyQt5.QtCore import QObject, pyqtSignal
from amorts_ui import Ui_AmortsWindow
from amorts import Amort
from my_dialog import AmortDialog


class WinSignals(QObject):
    closed = pyqtSignal()
    log_msg = pyqtSignal(str)
    log_err = pyqtSignal(str)


class AmortWin(QMainWindow):
    signals = WinSignals()

    def __init__(self):
        super(AmortWin, self).__init__()
        try:
            self.action = ''
            self.amorts = None
            self.new_amort = {}
            self.win_diag = None
            self.ui = Ui_AmortsWindow()
            self.ui.setupUi(self)
            self.hide()
            self._create_statusbar_set()
            self.init_ui()
            self.init_buttons()

        except Exception as e:
            self.signals.log_err.emit(f'ERROR in amorts_win/__init__ - {e}')

    def init_ui(self):
        try:
            self.ui.frame_quest.setVisible(False)
            self.ui.frame_warning.setVisible(False)
            self.amort_init()

        except Exception as e:
            self.statusbar_set_ui(f'ERROR in amorts_win/init_ui - {e}')

    def closeEvent(self, event):
        self.signals.closed.emit()

    def _create_statusbar_set(self):
        self.statusbar = self.statusBar()
        self.statusbar.showMessage('Окно менеджмента амортизаторов')

    def statusbar_set_ui(self, txt_bar):
        try:
            self.statusbar.showMessage(txt_bar)
            self.signals.log_err.emit(txt_bar)

        except Exception as e:
            self.signals.log_err.emit(f'ERROR in amorts_win/statusbar_set_ui - {e}')

    def init_buttons(self):
        self.ui.btn_exit.clicked.connect(self.close)
        self.ui.btn_del.clicked.connect(self.btn_del_click)
        self.ui.btn_add.clicked.connect(self.amort_add)
        self.ui.btn_ok_quest.clicked.connect(self.ok_question)
        self.ui.btn_cancel_quest.clicked.connect(self.cancel_question)
        self.ui.btn_ok_warning.clicked.connect(self.ok_warning)

    def amort_init(self):
        try:
            self.amorts = Amort()
            self.amorts_update()

        except Exception as e:
            self.statusbar_set_ui(f'ERROR in amorts_win/amort_init - {e}')

    def amorts_update(self):
        try:
            self.amorts.update_amort_list()
            self.ui.combo_Names.clear()
            if len(self.amorts.config.sections()) == 0:
                self.ui.btn_del.setEnabled(False)
                self.amorts_ui_clear()

            else:
                self.ui.combo_Names.addItems(self.amorts.names)
                self.ui.combo_Names.setCurrentIndex(0)
                self.amorts.current_index = 0
                self.ui.combo_Names.activated[int].connect(self.amort_select)
                self.amort_select(0)
                self.ui.btn_del.setEnabled(True)

        except Exception as e:
            self.statusbar_set_ui(f'ERROR in amorts_win/amorts_update - {e}')

    def amorts_ui_clear(self):
        try:
            self.ui.lbl_hod.setText('')
            self.ui.lbl_speed_1.setText('')
            self.ui.lbl_speed_2.setText('')
            self.ui.lbl_length_min.setText('')
            self.ui.lbl_length_max.setText('')
            self.ui.lbl_comp_min.setText('')
            self.ui.lbl_comp_max.setText('')
            self.ui.lbl_recoil_min.setText('')
            self.ui.lbl_recoil_max.setText('')
            self.ui.lbl_temper.setText('')

        except Exception as e:
            self.statusbar_set_ui(f'ERROR in amorts_win/amorts_ui_clear - {e}')

    def amort_select(self, index):
        try:
            self.amorts.current_index = index

            self.ui.lbl_hod.setText(str(self.amorts.struct.amorts[index].hod))
            self.ui.lbl_speed_1.setText(str(self.amorts.struct.amorts[index].speed_one))
            self.ui.lbl_speed_2.setText(str(self.amorts.struct.amorts[index].speed_two))
            self.ui.lbl_length_min.setText(str(self.amorts.struct.amorts[index].min_length))
            self.ui.lbl_length_max.setText(str(self.amorts.struct.amorts[index].max_length))
            self.ui.lbl_comp_min.setText(str(self.amorts.struct.amorts[index].min_comp))
            self.ui.lbl_comp_max.setText(str(self.amorts.struct.amorts[index].max_comp))
            self.ui.lbl_recoil_min.setText(str(self.amorts.struct.amorts[index].min_recoil))
            self.ui.lbl_recoil_max.setText(str(self.amorts.struct.amorts[index].max_recoil))
            self.ui.lbl_temper.setText(str(self.amorts.struct.amorts[index].max_temper))

        except Exception as e:
            self.statusbar_set_ui(f'ERROR in amorts_win/amort_select - {e}')

    def btn_del_click(self):
        try:
            self.action = 'del'
            ind = self.amorts.current_index
            self.ui.txt_quest.setText('Вы действительно хотите<BR>удалить амортизатор<BR>' +
                                      self.amorts.names[ind] + '<BR>из списка?')
            self.set_frame_question(True)

        except Exception as e:
            self.statusbar_set_ui(f'ERROR in amorts_win/btn_del_click - {e}')

    def amort_delete(self):
        try:
            ind = self.amorts.current_index
            amort = self.amorts.struct.amorts[ind]

            name = amort.name_a
            dimensions = f'{amort.min_length} - {amort.max_length}'
            hod = f'{amort.hod}'
            speed = f'one: {amort.speed_one} & two: {amort.speed_two}'
            limit_comp = f'{amort.min_comp} - {amort.max_comp}'
            limit_recoil = f'{amort.min_recoil} - {amort.max_recoil}'
            temper = f'{amort.max_temper}'

            txt_log = f'Amort is delete --> name = {name}, dimensions = {dimensions}, hod = {hod}, ' \
                      f'speed = {speed}, limit_comp = {limit_comp}, ' \
                      f'limit_recoil = {limit_recoil}, max_temper = {temper}'

            self.signals.log_msg.emit(txt_log)

            self.amorts.delete_amort(ind)

            self.amorts_update()

        except Exception as e:
            self.statusbar_set_ui(f'ERROR in amorts_win/amort_delete - {e}')

    def amort_add(self):
        try:
            trans_table = str.maketrans(',', '.')
            self.new_amort.clear()
            dialog = QDialog()
            win_diag = AmortDialog()
            win_diag.setupUi(dialog)
            if dialog.exec_():
                self.new_amort['name'] = win_diag.lineEdit_name.text().translate(trans_table)
                self.new_amort['len_min'] = win_diag.le_length_min.text().translate(trans_table)
                self.new_amort['len_max'] = win_diag.le_length_max.text().translate(trans_table)
                self.new_amort['hod'] = win_diag.le_hod.text().translate(trans_table)
                self.new_amort['speed_one'] = win_diag.le_speed_one.text().translate(trans_table)
                self.new_amort['speed_two'] = win_diag.le_speed_two.text().translate(trans_table)
                self.new_amort['comp_min'] = win_diag.le_comp_min.text().translate(trans_table)
                self.new_amort['comp_max'] = win_diag.le_comp_max.text().translate(trans_table)
                self.new_amort['recoil_min'] = win_diag.le_recoil_min.text().translate(trans_table)
                self.new_amort['recoil_max'] = win_diag.le_recoil_max.text().translate(trans_table)
                self.new_amort['max_temper'] = win_diag.le_temper.text().translate(trans_table)

                flag_add = self.check_concurrence_name()
                if flag_add:
                    name = self.new_amort.get('name_a')
                    dimensions = f'{self.new_amort.get("min_length")} - {self.new_amort.get("max_length")}'
                    hod = f'{self.new_amort.get("hod")}'
                    speed = f'one: {self.new_amort.get("speed_one")} & two: {self.new_amort.get("speed_two")}'
                    limit_comp = f'{self.new_amort.get("min_comp")} - {self.new_amort.get("max_comp")}'
                    limit_recoil = f'{self.new_amort.get("min_recoil")} - {self.new_amort.get("max_recoil")}'
                    temper = f'{self.new_amort.get("max_temper")}'

                    txt_log = f'Amort is added --> name = {name}, dimensions = {dimensions}, hod = {hod}, ' \
                              f'speed = {speed}, limit_comp = {limit_comp}, ' \
                              f'limit_recoil = {limit_recoil}, max_temper = {temper}'

                    self.signals.log_msg.emit(txt_log[:-1])
                    self.amorts.add_amort(self.new_amort)
                    self.amorts_update()
                else:
                    self.ui.txt_warning.setText('Такой амортизатор<BR>уже имеется в списке')
                    self.set_frame_warning(True)

            else:
                pass

        except Exception as e:
            self.statusbar_set_ui(f'ERROR in amorts_win/amort_add - {e}')

    def set_frame_question(self, bool_val):
        self.ui.frame_quest.setVisible(bool_val)
        self.ui.frame_quest.move(20, 60)
        self.ui.frame_btn.setEnabled(not bool_val)

    def set_frame_warning(self, bool_val):
        self.ui.frame_warning.setVisible(bool_val)
        self.ui.frame_warning.move(20, 60)
        self.ui.frame_btn.setVisible(not bool_val)

    def ok_warning(self):
        self.set_frame_warning(False)

    def ok_question(self):
        try:
            if self.action == 'del':
                self.amort_delete()
                self.set_frame_question(False)

        except Exception as e:
            self.statusbar_set_ui(f'ERROR in amorts_win/ok_question - {e}')

    def cancel_question(self):
        try:
            self.set_frame_question(False)

        except Exception as e:
            self.statusbar_set_ui(f'ERROR in amorts_win/cancel_question - {e}')

    def check_concurrence_name(self):
        try:
            flag_add = True
            for name in self.amorts.names:
                if name.upper() == self.new_amort.get('name').upper():
                    flag_add = False

            return flag_add

        except Exception as e:
            self.statusbar_set_ui(f'ERROR in amorts_win/check_concurrence_name - {e}')
