from PyQt5.QtWidgets import QMainWindow, QDialog
from PyQt5.QtCore import QObject, pyqtSignal
from amorts_ui import Ui_AmortsWindow
from amorts import Amort
from my_dialog import AmortDialog


class WinSignals(QObject):
    closed = pyqtSignal()
    log_msg = pyqtSignal(str)
    log_err = pyqtSignal(str)
    amort_select = pyqtSignal(object)


class AmortWin(QMainWindow):
    signals = WinSignals()

    def __init__(self):
        super(AmortWin, self).__init__()
        try:
            self.action = ''
            self.amorts = None
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
        pass

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
                self.ui.btn_ok.setEnabled(False)
                self.ui.btn_del.setEnabled(False)
                self.amorts_ui_clear()

            else:
                self.ui.combo_Names.addItems(self.amorts.names)
                self.ui.combo_Names.setCurrentIndex(0)
                self.amorts.current_index = 0
                self.ui.combo_Names.activated[int].connect(self.amort_select)
                self.amort_select(0)
                self.ui.btn_ok.setEnabled(True)
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

            name = self.amorts.names[ind]
            txt_log = 'Amort is delete - {}'.format(name)
            self.signals.log_msg.emit(txt_log)

            self.amorts.delete_amort(ind)

            self.amorts_update()

        except Exception as e:
            txt_log = 'ERROR in amorts_win/amort_delete - {}'.format(e)
            self.statusbar_set_ui(txt_log)
            self.signals.log_err.emit(txt_log)

    # FIXME
    def amort_add(self):
        try:
            self.new_operator.clear()
            dialog = QDialog()
            win_diag = AmortDialog()
            win_diag.setupUi(dialog)
            if dialog.exec_():
                name = win_diag.name_le.text()
                rank = win_diag.rank_le.text()
                if len(name) > 0 and len(rank) > 0:
                    self.new_operator['name'] = name
                    self.new_operator['rank'] = rank
                    flag_add = self.check_concurrence_name()
                    if flag_add:
                        txt_log = 'Operator is added - {}, {}'.format(rank, name)
                        self.signals.log_msg.emit(txt_log)
                        self.operators.add_operator(name, rank)
                        self.operator_update()
                    else:
                        self.ui.txt_warning.setText('Такой оператор<BR>уже имеется в списке')
                        self.set_frame_warning(True)
                else:
                    pass
            else:
                pass

        except Exception as e:
            txt_log = 'ERROR in executors_win/operator_add - {}'.format(e)
            self.statusbar_set_ui(txt_log)
            self.signals.log_err.emit(txt_log)

    # FIXME
    def amort_ok(self):
        try:
            name = self.ui.combo_Names.text()

            # self.signals.operator_select.emit(name, rank)

            txt_log = 'Amort is select - {}'.format(name)
            self.signals.log_msg.emit(txt_log)

            self.close()

        except Exception as e:
            txt_log = 'ERROR in amorts_win/amort_ok - {}'.format(e)
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
