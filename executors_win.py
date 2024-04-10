from PyQt5.QtWidgets import QMainWindow, QDialog
from PyQt5.QtCore import QObject, pyqtSignal
from executors_ui import Ui_ExecutorWindow
from operators import Operators
from my_dialog import Ui_Dialog


class WinSignals(QObject):
    closed = pyqtSignal()
    log_msg = pyqtSignal(str)
    log_err = pyqtSignal(str)
    operator_select = pyqtSignal(str, str)


class ExecWin(QMainWindow):
    signals = WinSignals()

    def __init__(self):
        super(ExecWin, self).__init__()
        try:
            self.action = ''
            self.new_operator = {}
            self.operators = None
            self.win_diag = None
            self.ui = Ui_ExecutorWindow()
            self.ui.setupUi(self)
            self.hide()
            self._create_statusbar_set()

            self.init_buttons()

        except Exception as e:
            txt_log = 'ERROR in executors_win/__init__ - {}'.format(e)
            self.signals.log_err.emit(txt_log)

    def closeEvent(self, event):
        self.signals.closed.emit()

    def _create_statusbar_set(self):
        self.statusbar = self.statusBar()
        self.statusbar.showMessage('Окно менеджмента операторов стенда')

    def statusbar_set_ui(self, txt_bar):
        try:
            self.statusbar.showMessage(txt_bar)

        except Exception as e:
            txt_log = 'ERROR in executors_win/statusbar_set_ui - {}'.format(e)
            self.signals.log_err.emit(txt_log)

    def init_buttons(self):
        self.ui.btn_exit.clicked.connect(self.close)
        self.ui.btn_del.clicked.connect(self.btn_del_click)
        self.ui.btn_add.clicked.connect(self.operator_add)
        self.ui.btn_ok_select.clicked.connect(self.operator_ok)
        self.ui.btn_ok_quest.clicked.connect(self.ok_question)
        self.ui.btn_cancel_quest.clicked.connect(self.cancel_question)
        self.ui.btn_ok_warning.clicked.connect(self.ok_warning)

    def operator_ui(self):
        try:
            self.ui.frame_main.setVisible(True)
            self.ui.frame_quest.setVisible(False)
            self.ui.frame_warning.setVisible(False)
            self.ui.btn_cancel_select.setVisible(False)
            self.operator_init()

        except Exception as e:
            txt_log = 'ERROR in executors_win/operator_ui - {}'.format(e)
            self.statusbar_set_ui(txt_log)
            self.signals.log_err.emit(txt_log)

    def operator_init(self):
        try:
            self.operators = Operators()
            self.operator_update()

        except Exception as e:
            txt_log = 'ERROR in executors_win/operator_init - {}'.format(e)
            self.statusbar_set_ui(txt_log)
            self.signals.log_err.emit(txt_log)

    def operator_update(self):
        try:
            self.operators.update_list()
            self.ui.combo_Names.clear()
            if len(self.operators.config.sections()) == 0:
                self.ui.btn_ok_select.setEnabled(False)
                self.ui.btn_del.setEnabled(False)
                self.ui.lbl_name.setText('')
                self.ui.lbl_rank.setText('')
                self.signals.operator_select.emit('', '')

            else:
                self.ui.combo_Names.addItems(self.operators.names)
                self.ui.combo_Names.setCurrentIndex(0)
                self.operators.current_index = 0
                self.ui.combo_Names.activated[int].connect(self.operator_select)
                self.operator_select(self.operators.current_index)
                self.ui.btn_ok_select.setEnabled(True)
                self.ui.btn_del.setEnabled(True)

        except Exception as e:
            txt_log = 'ERROR in executors_win/operator_update - {}'.format(e)
            self.statusbar_set_ui(txt_log)
            self.signals.log_err.emit(txt_log)

    def operator_select(self, ind):
        try:
            self.operators.current_index = ind
            name = self.operators.names[ind]
            rank = self.operators.ranks[ind]

            self.ui.lbl_name.setText(name)
            self.ui.lbl_rank.setText(rank)

        except Exception as e:
            txt_log = 'ERROR in executors_win/operator_select - {}'.format(e)
            self.statusbar_set_ui(txt_log)
            self.signals.log_err.emit(txt_log)

    def btn_del_click(self):
        try:
            self.action = 'del'
            ind = self.operators.current_index
            self.ui.txt_quest.setText('Вы действительно хотите<BR>удалить исполнителя<BR>' +
                                      self.operators.names[ind] + ' ' + self.operators.ranks[ind] +
                                      '<BR>из списка?')
            self.set_frame_question(True)

        except Exception as e:
            txt_log = 'ERROR in executors_win/btn_del_click - {}'.format(e)
            self.statusbar_set_ui(txt_log)
            self.signals.log_err.emit(txt_log)

    def operator_delete(self):
        try:
            ind = self.operators.current_index

            name = self.operators.names[ind]
            rank = self.operators.ranks[ind]
            txt_log = 'Operator is delete - {}, {}'.format(rank, name)
            self.signals.log_msg.emit(txt_log)

            self.operators.delete_operator(ind)

            self.operator_update()

        except Exception as e:
            txt_log = 'ERROR in executors_win/operator_delete - {}'.format(e)
            self.status_bar_ui(txt_log)
            self.signals.log_err.emit(txt_log)

    def operator_add(self):
        try:
            self.new_operator.clear()
            dialog = QDialog()
            win_diag = Ui_Dialog()
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

    def operator_ok(self):
        try:
            name = self.ui.lbl_name.text()
            rank = self.ui.lbl_rank.text()

            self.signals.operator_select.emit(name, rank)

            txt_log = 'Operator is select - {}, {}'.format(rank, name)
            self.signals.log_msg.emit(txt_log)

            self.close()

        except Exception as e:
            txt_log = 'ERROR in executors_win/operator_ok - {}'.format(e)
            self.statusbar_set_ui(txt_log)
            self.signals.log_err.emit(txt_log)

    def set_frame_question(self, bool_val):
        self.ui.frame_quest.setVisible(bool_val)
        self.ui.frame_main.setVisible(not bool_val)

    def set_frame_warning(self, bool_val):
        self.ui.frame_warning.setVisible(bool_val)
        self.ui.frame_main.setVisible(not bool_val)

    def ok_warning(self):
        self.set_frame_warning(False)

    def ok_question(self):
        try:
            if self.action == 'del':
                self.operator_delete()
                self.set_frame_question(False)

        except Exception as e:
            txt_log = 'ERROR in executors_win/ok_question - {}'.format(e)
            self.statusbar_set_ui(txt_log)
            self.signals.log_err.emit(txt_log)

    def cancel_question(self):
        try:
            self.set_frame_question(False)

        except Exception as e:
            txt_log = 'ERROR in executors_win/cancel_question - {}'.format(e)
            self.statusbar_set_ui(txt_log)
            self.signals.log_err.emit(txt_log)

    def check_concurrence_name(self):
        try:
            flag_add = True
            for name in self.operators.names:
                if name.upper() == self.new_operator.get('name').upper():
                    flag_add = False

            return flag_add

        except Exception as e:
            txt_log = 'ERROR in executors_win/check_concurrence_name - {}'.format(e)
            self.statusbar_set_ui(txt_log)
            self.signals.log_err.emit(txt_log)
