# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QMainWindow, QDialog
from PySide6.QtGui import QIcon
from PySide6.QtCore import QObject, Signal

from app.ui_py.executors_ui import Ui_ExecutorWindow
from app.ui_py.new_oper import OperatorDialog
from scripts.logger import my_logger
from scripts.operators import Operators


class WinSignals(QObject):
    closed = Signal()
    operator_select = Signal(str, str)


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
            
            names = self.operators.get_names()
            
            if len(names) == 0:
                self.btn_ok_select.setEnabled(False)
                self.btn_del.setEnabled(False)
                self.lbl_name.setText('')
                self.lbl_rank.setText('')
                self.name = ''
                self.rank = ''
                self.signals.operator_select.emit(self.name, self.rank)

            else:
                self.combo_Names.addItems(names)
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
            operator = self.operators.get_operator(ind)
            if operator:
                self.operators.current_index = ind
                self.name = operator.name
                self.rank = operator.rank

                self.lbl_name.setText(self.name)
                self.lbl_rank.setText(self.rank)
            else:
                self.logger.warning(f"Оператор с индексом {ind} не найден")

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in executors_win/_operator_select - {e}')

    def _btn_del_click(self):
        try:
            self.action = 'del'
            ind = self.operators.current_index
            operator = self.operators.get_operator(ind)
            
            if operator:
                self.txt_quest.setText(
                    f'Вы действительно хотите<BR>удалить исполнителя<BR>'
                    f'{operator.name} {operator.rank}<BR>из списка?'
                )
                self._set_frame_question(True)
            else:
                self.logger.warning(f"Оператор с индексом {ind} не найден")

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in executors_win/_btn_del_click - {e}')

    def _operator_delete(self):
        try:
            ind = self.operators.current_index
            operator = self.operators.get_operator(ind)
            
            if operator:
                txt_log = f'Operator is delete - {operator.rank}, {operator.name}'
                self.logger.info(txt_log)

                if operator.name == self.name:
                    self.name = ''
                    self.rank = ''
                    self.signals.operator_select.emit(self.name, self.rank)

                if self.operators.delete_operator(ind):
                    self._operator_update()
                else:
                    self._statusbar_set_ui('Ошибка при удалении оператора')
            else:
                self.logger.warning(f"Оператор с индексом {ind} не найден")

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
                name = win_diag.name_le.text().strip()
                rank = win_diag.rank_le.text().strip()
                
                if name and rank:
                    self.new_operator['name'] = name
                    self.new_operator['rank'] = rank
                    
                    if self._check_concurrence_name():
                        if self.operators.add_operator(name, rank):
                            txt_log = f'Operator is added - {rank}, {name}'
                            self.logger.info(txt_log)
                            self._operator_update()
                        else:
                            self._statusbar_set_ui('Ошибка при добавлении оператора')
                    else:
                        self.txt_warning.setText('Такой оператор<BR>уже имеется в списке')
                        self._set_frame_warning(True)

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in executors_win/_operator_add - {e}')

    def _operator_ok(self):
        try:
            self.signals.operator_select.emit(self.name, self.rank)

            txt_log = f'Operator is select - {self.rank}, {self.name}'
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
            new_name = self.new_operator.get('name', '').upper()
            for name in self.operators.get_names():
                if name.upper() == new_name:
                    return False
            return True

        except Exception as e:
            self.logger.error(e)
            self._statusbar_set_ui(f'ERROR in executors_win/_check_concurrence_name - {e}')
            return False
