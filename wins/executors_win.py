# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QMainWindow, QDialog
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QIcon

from logger import my_logger
from ui_py.executors_ui import Ui_ExecutorWindow
from operators import Operators
from ui_py.my_dialog import OperatorDialog


class WinSignals(QObject):
    closed = pyqtSignal()
    operator_select = pyqtSignal(str, str)


class ExecWin(QMainWindow, Ui_ExecutorWindow):
    signals = WinSignals()

    def __init__(self):
        super(ExecWin, self).__init__()
        try:
            self.logger = my_logger.get_logger(__name__)
            self.action = ''
            self.new_operator = {}
            self.name = ''
            self.rank = ''
            self.operators = None
            self.win_diag = None
            self.setupUi(self)
            self.setWindowIcon(QIcon('icon/user.png'))
            self.hide()
            self._init_ui()
            self._create_statusbar_set()
            self._init_buttons()

        except Exception as e:
            self.logger.error(e)

    def closeEvent(self, event):
        self.signals.closed.emit()

    def _init_ui(self):
        try:
            self.frame_main.setVisible(True)
            self.frame_quest.setVisible(False)
            self.frame_warning.setVisible(False)
            self.btn_cancel_select.setVisible(False)
            self._operator_init()

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in executors_win/_init_ui - {e}')

    def _create_statusbar_set(self):
        self.statusbar = self.statusBar()
        self.statusbar.showMessage('Окно менеджмента операторов стенда')

    def _statusbar_set_ui(self, txt_bar):
        try:
            self.statusbar.showMessage(txt_bar)

        except Exception as e:
            self.logger.error(e)

    def _init_buttons(self):
        self.btn_exit.clicked.connect(self.close)
        self.btn_del.clicked.connect(self._btn_del_click)
        self.btn_add.clicked.connect(self._operator_add)
        self.btn_ok_select.clicked.connect(self._operator_ok)
        self.btn_ok_quest.clicked.connect(self._ok_question)
        self.btn_cancel_quest.clicked.connect(self._cancel_question)
        self.btn_ok_warning.clicked.connect(self._ok_warning)

    def _operator_init(self):
        try:
            self.operators = Operators()
            self._operator_update()

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in executors_win/_operator_init - {e}')

    def _operator_update(self):
        try:
            self.operators.update_list()
            self.combo_Names.clear()
            if len(self.operators.config.sections()) == 0:
                self.btn_ok_select.setEnabled(False)
                self.btn_del.setEnabled(False)
                self.lbl_name.setText('')
                self.lbl_rank.setText('')
                self.name = ''
                self.rank = ''

                self.signals.operator_select(self.name, self.rank)

            else:
                self.combo_Names.addItems(self.operators.names)
                self.combo_Names.setCurrentIndex(0)
                self.operators.current_index = 0
                self.combo_Names.activated[int].connect(self._operator_select)
                self._operator_select(self.operators.current_index)
                self.btn_ok_select.setEnabled(True)
                self.btn_del.setEnabled(True)

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in executors_win/_operator_update - {e}')

    def _operator_select(self, ind):
        try:
            self.operators.current_index = ind
            self.name = self.operators.names[ind]
            self.rank = self.operators.ranks[ind]

            self.lbl_name.setText(self.name)
            self.lbl_rank.setText(self.rank)

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in executors_win/_operator_select - {e}')

    def _btn_del_click(self):
        try:
            self.action = 'del'
            ind = self.operators.current_index
            self.txt_quest.setText('Вы действительно хотите<BR>удалить исполнителя<BR>' +
                                      self.operators.names[ind] + ' ' + self.operators.ranks[ind] +
                                      '<BR>из списка?')
            self._set_frame_question(True)

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in executors_win/_btn_del_click - {e}')

    def _operator_delete(self):
        try:
            ind = self.operators.current_index

            name = self.operators.names[ind]
            rank = self.operators.ranks[ind]
            txt_log = 'Operator is delete - {}, {}'.format(rank, name)
            self.logger.info(txt_log)

            if name == self.name:
                self.name = ''
                self.rank = ''
                self.signals.operator_select.emit(self.name, self.rank)

            self.operators.delete_operator(ind)

            self._operator_update()

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in executors_win/_operator_delete - {e}')

    def _operator_add(self):
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
                    flag_add = self._check_concurrence_name()
                    if flag_add:
                        txt_log = 'Operator is added - {}, {}'.format(rank, name)
                        self.logger.info(txt_log)
                        self.operators.add_operator(name, rank)
                        self._operator_update()
                    else:
                        self.txt_warning.setText('Такой оператор<BR>уже имеется в списке')
                        self._set_frame_warning(True)
                else:
                    pass
            else:
                pass

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in executors_win/_operator_add - {e}')

    def _operator_ok(self):
        try:
            self.name = self.lbl_name.text()
            self.rank = self.lbl_rank.text()

            self.signals.operator_select.emit(self.name, self.rank)

            txt_log = 'Operator is select - {}, {}'.format(self.rank, self.name)
            self.logger.info(txt_log)

            self.close()

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in executors_win/_operator_ok - {e}')

    def _set_frame_question(self, bool_val):
        self.frame_quest.setVisible(bool_val)
        self.frame_main.setVisible(not bool_val)

    def _set_frame_warning(self, bool_val):
        self.frame_warning.setVisible(bool_val)
        self.frame_main.setVisible(not bool_val)

    def _ok_warning(self):
        self._set_frame_warning(False)

    def _ok_question(self):
        try:
            if self.action == 'del':
                self._operator_delete()
                self._set_frame_question(False)

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in executors_win/_ok_question - {e}')

    def _cancel_question(self):
        try:
            self._set_frame_question(False)

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in executors_win/_cancel_question - {e}')

    def _check_concurrence_name(self):
        try:
            flag_add = True
            for name in self.operators.names:
                if name.upper() == self.new_operator.get('name').upper():
                    flag_add = False

            return flag_add

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in executors_win/_check_concurrence_name - {e}')
