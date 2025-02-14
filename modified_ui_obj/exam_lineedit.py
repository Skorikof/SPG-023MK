# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtCore import pyqtSignal


class LineEdit(QLineEdit):
    signal = pyqtSignal()

    def __init__(self, parent=None):
        super(LineEdit, self).__init__(parent)

    def focusInEvent(self, event):
        self.setInputMask('')

    def focusOutEvent(self, event):
        self.signal.emit()
