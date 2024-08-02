# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtCore import pyqtSignal


class MyLineEdit(QLineEdit):
    clicked = pyqtSignal()

    def __init__(self, *args):
        QLineEdit.__init__(self, *args)

    def mousePressEvent(self, QMouseEvent):
        self.clicked.emit()
        QLineEdit.mousePressEvent(self, QMouseEvent)
