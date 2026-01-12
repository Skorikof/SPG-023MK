# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QLineEdit
from PySide6.QtCore import Signal


class MyLineEdit(QLineEdit):
    clicked = Signal()

    def __init__(self, *args):
        QLineEdit.__init__(self, *args)

    def mousePressEvent(self, QMouseEvent):
        self.clicked.emit()
        QLineEdit.mousePressEvent(self, QMouseEvent)
