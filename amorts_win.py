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
            self.new_amort = dict()
            self.win_diag = None
            self.ui = Ui_AmortsWindow()
            self.ui.setupUi(self)
            self.hide()
            self._create_statusbar_set()
            self.init_ui()
            self.init_buttons()

        except Exception as e:
            txt_log = 'ERROR in amorts_win/__init__ - {}'.format(e)
            self.signals.log_err.emit(txt_log)

    def init_ui(self):
        try:
            self.ui.frame_quest.setVisible(False)
            self.ui.frame_warning.setVisible(False)
            self.amort_init()

        except Exception as e:
            txt_log = 'ERROR in amorts_win/init_ui - {}'.format(e)
            self.statusbar_set_ui(txt_log)
            self.signals.log_err.emit(txt_log)

    def closeEvent(self, event):
        self.signals.closed.emit()

    def _create_statusbar_set(self):
        self.statusbar = self.statusBar()
        self.statusbar.showMessage('Окно менеджмента амортизаторов')

    def statusbar_set_ui(self, txt_bar):
        try:
            self.statusbar.showMessage(txt_bar)

        except Exception as e:
            txt_log = 'ERROR in amorts_win/statusbar_set_ui - {}'.format(e)
            self.signals.log_err.emit(txt_log)

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
            txt_log = 'ERROR in amorts_win/amort_init - {}'.format(e)
            self.statusbar_set_ui(txt_log)
            self.signals.log_err.emit(txt_log)

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
            txt_log = 'ERROR in amorts_win/amorts_update - {}'.format(e)
            self.statusbar_set_ui(txt_log)
            self.signals.log_err.emit(txt_log)

    def amorts_ui_clear(self):
        try:
            self.ui.lbl_length_min.setText('')
            self.ui.lbl_length_max.setText('')
            self.ui.lbl_comp_min.setText('')
            self.ui.lbl_comp_max.setText('')
            self.ui.lbl_recoil_min.setText('')
            self.ui.lbl_recoil_max.setText('')
            self.ui.lbl_temper.setText('')
            self.ui.lbl_speed.setText('')

        except Exception as e:
            txt_log = 'ERROR in amorts_win/amorts_ui_clear - {}'.format(e)
            self.statusbar_set_ui(txt_log)
            self.signals.log_err.emit(txt_log)

    def amort_select(self, index):
        try:
            self.amorts.current_index = index

            self.ui.lbl_length_min.setText(str(self.amorts.struct.amorts[index].min_length))
            self.ui.lbl_length_max.setText(str(self.amorts.struct.amorts[index].max_length))
            self.ui.lbl_comp_min.setText(str(self.amorts.struct.amorts[index].min_comp))
            self.ui.lbl_comp_max.setText(str(self.amorts.struct.amorts[index].max_comp))
            self.ui.lbl_recoil_min.setText(str(self.amorts.struct.amorts[index].min_recoil))
            self.ui.lbl_recoil_max.setText(str(self.amorts.struct.amorts[index].max_recoil))
            self.ui.lbl_temper.setText(str(self.amorts.struct.amorts[index].max_temper))
            self.ui.lbl_speed.setText(str(self.amorts.struct.amorts[index].speed))

        except Exception as e:
            txt_log = 'ERROR in amorts_win/amort_select - {}'.format(e)
            self.statusbar_set_ui(txt_log)
            self.signals.log_err.emit(txt_log)

    def btn_del_click(self):
        try:
            self.action = 'del'
            ind = self.amorts.current_index
            self.ui.txt_quest.setText('Вы действительно хотите<BR>удалить амортизатор<BR>' +
                                      self.amorts.names[ind] + '<BR>из списка?')
            self.set_frame_question(True)

        except Exception as e:
            txt_log = 'ERROR in amorts_win/btn_del_click - {}'.format(e)
            self.statusbar_set_ui(txt_log)
            self.signals.log_err.emit(txt_log)

    def amort_delete(self):
        try:
            ind = self.amorts.current_index
            name = self.amorts.struct.amorts[ind].name_a
            len_min = self.amorts.struct.amorts[ind].min_length
            len_max = self.amorts.struct.amorts[ind].max_length
            comp_min = self.amorts.struct.amorts[ind].min_comp
            comp_max = self.amorts.struct.amorts[ind].max_comp
            recoil_min = self.amorts.struct.amorts[ind].min_recoil
            recoil_max = self.amorts.struct.amorts[ind].max_recoil
            max_temper = self.amorts.struct.amorts[ind].max_temper
            speed = self.amorts.struct.amorts[ind].speed

            txt_log = 'Amort is delete -> name - {}, len_min - {}, len_max - {}, comp_min - {}, comp_max - {},' \
                      'recoil_min - {}, recoil_max - {}, max_temper - {}, speed - {}'.format(name, len_min, len_max,
                                                                                             comp_min, comp_max,
                                                                                             recoil_min, recoil_max,
                                                                                             max_temper, speed)
            self.signals.log_msg.emit(txt_log)

            self.amorts.delete_amort(ind)

            self.amorts_update()

        except Exception as e:
            txt_log = 'ERROR in amorts_win/amort_delete - {}'.format(e)
            self.statusbar_set_ui(txt_log)
            self.signals.log_err.emit(txt_log)

    def amort_add(self):
        try:
            trans_table = str.maketrans(',', '.')
            self.new_amort.clear()
            dialog = QDialog()
            win_diag = AmortDialog()
            win_diag.setupUi(dialog)
            if dialog.exec_():
                self.new_amort['name'] = win_diag.name_le.text().translate(trans_table)
                self.new_amort['len_min'] = win_diag.length_min.text().translate(trans_table)
                self.new_amort['len_max'] = win_diag.length_max.text().translate(trans_table)
                self.new_amort['comp_min'] = win_diag.comp_min.text().translate(trans_table)
                self.new_amort['comp_max'] = win_diag.comp_max.text().translate(trans_table)
                self.new_amort['recoil_min'] = win_diag.recoil_min.text().translate(trans_table)
                self.new_amort['recoil_max'] = win_diag.recoil_max.text().translate(trans_table)
                self.new_amort['max_temper'] = win_diag.max_temper.text().translate(trans_table)
                self.new_amort['speed'] = win_diag.speed.text().translate(trans_table)

                flag_add = self.check_concurrence_name()
                if flag_add:
                    txt_log = 'Amort is added -'
                    for k, v in self.new_amort.items():
                        txt_log = txt_log + ' ' + k + ' - ' + v + ','
                    self.signals.log_msg.emit(txt_log[:-1])
                    self.amorts.add_amort(self.new_amort)
                    self.amorts_update()
                else:
                    self.ui.txt_warning.setText('Такой амортизатор<BR>уже имеется в списке')
                    self.set_frame_warning(True)

            else:
                pass

        except Exception as e:
            txt_log = 'ERROR in amorts_win/amort_add - {}'.format(e)
            self.statusbar_set_ui(txt_log)
            self.signals.log_err.emit(txt_log)

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
            txt_log = 'ERROR in amorts_win/ok_question - {}'.format(e)
            self.statusbar_set_ui(txt_log)
            self.signals.log_err.emit(txt_log)

    def cancel_question(self):
        try:
            self.set_frame_question(False)

        except Exception as e:
            txt_log = 'ERROR in amorts_win/cancel_question - {}'.format(e)
            self.statusbar_set_ui(txt_log)
            self.signals.log_err.emit(txt_log)

    def check_concurrence_name(self):
        try:
            flag_add = True
            for name in self.amorts.names:
                if name.upper() == self.new_amort.get('name').upper():
                    flag_add = False

            return flag_add

        except Exception as e:
            txt_log = 'ERROR in amorts_win/check_concurrence_name - {}'.format(e)
            self.statusbar_set_ui(txt_log)
            self.signals.log_err.emit(txt_log)
