from PyQt5.QtWidgets import QMainWindow, QDialog
from PyQt5.QtCore import QObject, pyqtSignal
from executors_ui import Ui_ExecutorWindow
from operators import Operators
from my_dialog import Ui_Dialog


class WinSignals(QObject):
    closed = pyqtSignal()


class ExecWin(QMainWindow):
    signals = WinSignals()

    def __init__(self, model):
        super(ExecWin, self).__init__()
        try:
            self.operators = None
            self.win_diag = None
            self.model = model
            self.ui = Ui_ExecutorWindow()
            self.ui.setupUi(self)
            self.hide()
            self._create_statusbar_set()

            self.init_buttons()

        except Exception as e:
            txt_log = 'ERROR in executors_win/__init__ - {}'.format(e)
            self.model.status_bar_msg(txt_log)
            self.model.save_log('error', str(e))

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
            self.model.status_bar_msg(txt_log)
            self.model.save_log('error', str(e))

    def init_buttons(self):
        self.ui.btn_exit.clicked.connect(self.close)
        self.ui.btn_del.clicked.connect(self.operator_delete)
        self.ui.btn_add.clicked.connect(self.operator_add)
        self.ui.btn_ok_select.clicked.connect(self.operator_ok)

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
            self.model.save_log('error', str(e))

    def operator_init(self):
        try:
            self.operators = Operators()
            self.operator_update()

        except Exception as e:
            txt_log = 'ERROR in executors_win/operator_init - {}'.format(e)
            self.statusbar_set_ui(txt_log)
            self.model.save_log('error', str(e))

    def operator_update(self):
        try:
            self.operators.update_list()
            self.ui.combo_Names.clear()
            if len(self.operators.config.sections()) == 0:
                self.ui.btn_ok_select.setEnabled(False)
                self.ui.btn_del.setEnabled(False)
                self.ui.lbl_name.setText('')
                self.ui.lbl_rank.setText('')
                self.model.set_state['operator']['name'] = ''
                self.model.set_state['operator']['rank'] = ''

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
            self.model.statusbar_set_ui(txt_log)
            self.model.save_log('error', str(e))

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
            self.model.save_log('error', str(e))

    def operator_delete(self):
        try:
            ind = self.operators.current_index

            name = self.operators.names[ind]
            rank = self.operators.ranks[ind]
            txt_log = 'Operator is delete - {}, {}'.format(rank, name)
            self.model.save_log('info', txt_log)

            self.operators.delete_operator(ind)

            self.operator_update()

        except Exception as e:
            txt_log = 'ERROR in executors_win/operator_delete - {}'.format(e)
            self.status_bar_ui(txt_log)
            self.model.save_log('error', str(e))

    def operator_add(self, s):
        try:
            dialog = QDialog()
            win_diag = Ui_Dialog()
            win_diag.setupUi(dialog)
            if dialog.exec_():
                name = win_diag.name_le.text()
                rank = win_diag.rank_le.text()
                if len(name) > 0 and len(rank) > 0:
                    txt_log = 'Operator is added - {}, {}'.format(rank, name)
                    self.model.save_log('info', txt_log)
                    self.operators.add_operator(name, rank)
                    self.operator_update()
                else:
                    pass
            else:
                pass

        except Exception as e:
            txt_log = 'ERROR in executors_win/operator_add - {}'.format(e)
            self.statusbar_set_ui(txt_log)
            self.model.save_log('error', str(e))

    def operator_ok(self):
        try:
            name = self.ui.lbl_name.text()
            rank = self.ui.lbl_rank.text()

            self.model.set_state['operator']['name'] = name
            self.model.set_state['operator']['rank'] = rank

            txt_log = 'Operator is select - {}, {}'.format(rank, name)
            self.model.save_log('info', txt_log)

            self.close()

        except Exception as e:
            txt_log = 'ERROR in executors_win/operator_ok - {}'.format(e)
            self.statusbar_set_ui(txt_log)
            self.model.save_log('error', str(e))
