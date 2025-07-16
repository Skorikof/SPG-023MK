# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QLineEdit
from PySide6.QtCore import Signal


class LineEdit(QLineEdit):
    signal = Signal()

    def __init__(self, parent=None):
        super(LineEdit, self).__init__(parent)

    def focusInEvent(self, event):
        self.setInputMask('')

    def focusOutEvent(self, event):
        self.signal.emit()
