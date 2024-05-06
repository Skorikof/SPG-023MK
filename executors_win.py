from PyQt5.QtWidgets import QMainWindow, QDialog
from PyQt5.QtCore import QObject, pyqtSignal
from executors_ui import Ui_ExecutorWindow
from operators import Operators
from my_dialog import OperatorDialog


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
            self.name = ''
            self.rank = ''
            self.operators = None
            self.win_diag = None
            self.ui = Ui_ExecutorWindow()
            self.ui.setupUi(self)
            self.hide()
            self.init_ui()
            self._create_statusbar_set()

            self.init_buttons()

        except Exception as e:
            self.signals.log_err.emit(f'ERROR in executors_win/__init__ - {e}')

    def closeEvent(self, event):
        self.signals.closed.emit()

    def init_ui(self):
        try:
            self.ui.frame_main.setVisible(True)
            self.ui.frame_quest.setVisible(False)
            self.ui.frame_warning.setVisible(False)
            self.ui.btn_cancel_select.setVisible(False)
            self.operator_init()

        except Exception as e:
            self.statusbar_set_ui(f'ERROR in executors_win/__init__ - {e}')

    def _create_statusbar_set(self):
        self.statusbar = self.statusBar()
        self.statusbar.showMessage('Окно менеджмента операторов стенда')

    def statusbar_set_ui(self, txt_bar):
        try:
            self.statusbar.showMessage(txt_bar)
            self.signals.log_err.emit(txt_bar)

        except Exception as e:
            self.signals.log_err.emit(f'ERROR in executors_win/statusbar_set_ui - {e}')

    def init_buttons(self):
        self.ui.btn_exit.clicked.connect(self.close)
        self.ui.btn_del.clicked.connect(self.btn_del_click)
        self.ui.btn_add.clicked.connect(self.operator_add)
        self.ui.btn_ok_select.clicked.connect(self.operator_ok)
        self.ui.btn_ok_quest.clicked.connect(self.ok_question)
        self.ui.btn_cancel_quest.clicked.connect(self.cancel_question)
        self.ui.btn_ok_warning.clicked.connect(self.ok_warning)

    def operator_init(self):
        try:
            self.operators = Operators()
            self.operator_update()

        except Exception as e:
            self.statusbar_set_ui(f'ERROR in executors_win/operator_init - {e}')

    def operator_update(self):
        try:
            self.operators.update_list()
            self.ui.combo_Names.clear()
            if len(self.operators.config.sections()) == 0:
                self.ui.btn_ok_select.setEnabled(False)
                self.ui.btn_del.setEnabled(False)
                self.ui.lbl_name.setText('')
                self.ui.lbl_rank.setText('')
                self.name = ''
                self.rank = ''

                self.signals.operator_select(self.name, self.rank)

            else:
                self.ui.combo_Names.addItems(self.operators.names)
                self.ui.combo_Names.setCurrentIndex(0)
                self.operators.current_index = 0
                self.ui.combo_Names.activated[int].connect(self.operator_select)
                self.operator_select(self.operators.current_index)
                self.ui.btn_ok_select.setEnabled(True)
                self.ui.btn_del.setEnabled(True)

        except Exception as e:
            self.statusbar_set_ui(f'ERROR in executors_win/operator_update - {e}')

    def operator_select(self, ind):
        try:
            self.operators.current_index = ind
            self.name = self.operators.names[ind]
            self.rank = self.operators.ranks[ind]

            self.ui.lbl_name.setText(self.name)
            self.ui.lbl_rank.setText(self.rank)

        except Exception as e:
            self.statusbar_set_ui(f'ERROR in executors_win/operator_select - {e}')

    def btn_del_click(self):
        try:
            self.action = 'del'
            ind = self.operators.current_index
            self.ui.txt_quest.setText('Вы действительно хотите<BR>удалить исполнителя<BR>' +
                                      self.operators.names[ind] + ' ' + self.operators.ranks[ind] +
                                      '<BR>из списка?')
            self.set_frame_question(True)

        except Exception as e:
            self.statusbar_set_ui(f'ERROR in executors_win/btn_del_click - {e}')

    def operator_delete(self):
        try:
            ind = self.operators.current_index

            name = self.operators.names[ind]
            rank = self.operators.ranks[ind]
            txt_log = 'Operator is delete - {}, {}'.format(rank, name)
            self.signals.log_msg.emit(txt_log)

            if name == self.name:
                self.name = ''
                self.rank = ''
                self.signals.operator_select.emit(self.name, self.rank)

            self.operators.delete_operator(ind)

            self.operator_update()

        except Exception as e:
            self.status_bar_ui(f'ERROR in executors_win/operator_delete - {e}')

    def operator_add(self):
        try:
            self.new_operator.clear()
            dialog = QDialog()
            win_diag = OperatorDialog()
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
            self.statusbar_set_ui(f'ERROR in executors_win/operator_add - {e}')

    def operator_ok(self):
        try:
            self.name = self.ui.lbl_name.text()
            self.rank = self.ui.lbl_rank.text()

            self.signals.operator_select.emit(self.name, self.rank)

            txt_log = 'Operator is select - {}, {}'.format(self.rank, self.name)
            self.signals.log_msg.emit(txt_log)

            self.close()

        except Exception as e:
            self.statusbar_set_ui(f'ERROR in executors_win/operator_ok - {e}')

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
            self.statusbar_set_ui(f'ERROR in executors_win/ok_question - {e}')

    def cancel_question(self):
        try:
            self.set_frame_question(False)

        except Exception as e:
            self.statusbar_set_ui(f'ERROR in executors_win/cancel_question - {e}')

    def check_concurrence_name(self):
        try:
            flag_add = True
            for name in self.operators.names:
                if name.upper() == self.new_operator.get('name').upper():
                    flag_add = False

            return flag_add

        except Exception as e:
            self.statusbar_set_ui(f'ERROR in executors_win/check_concurrence_name - {e}')
