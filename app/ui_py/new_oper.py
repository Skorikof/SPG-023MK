# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'new_operaFZNxZ.ui'
##
## Created by: Qt User Interface Compiler version 6.4.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject, QSize, Qt)
from PySide6.QtGui import (QFont)
from PySide6.QtWidgets import (QDialogButtonBox, QGridLayout, QLabel)

from app.modified_ui_obj.exam_lineedit import LineEdit


class OperatorDialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(380, 180)
        self.gridLayout = QGridLayout(Dialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(10)
        self.gridLayout.setVerticalSpacing(5)
        self.gridLayout.setContentsMargins(10, 10, 10, 10)
        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 2)

        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(100, 0))
        self.label.setMaximumSize(QSize(100, 16777215))
        font = QFont()
        font.setFamilies([u"Calibri"])
        font.setPointSize(14)
        self.label.setFont(font)

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.rank_le = LineEdit(Dialog)
        self.rank_le.setObjectName(u"rank_le")
        self.rank_le.setMinimumSize(QSize(250, 30))
        self.rank_le.setMaximumSize(QSize(250, 16777215))
        self.rank_le.setFont(font)

        self.gridLayout.addWidget(self.rank_le, 1, 1, 1, 1)

        self.name_le = LineEdit(Dialog)
        self.name_le.setObjectName(u"name_le")
        self.name_le.setMinimumSize(QSize(250, 30))
        self.name_le.setMaximumSize(QSize(250, 16777215))
        self.name_le.setFont(font)

        self.gridLayout.addWidget(self.name_le, 0, 1, 1, 1)

        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMinimumSize(QSize(100, 0))
        self.label_2.setMaximumSize(QSize(100, 16777215))
        self.label_2.setFont(font)

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)


        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"\u0414\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u043e\u043f\u0435\u0440\u0430\u0442\u043e\u0440\u0430", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"<html><head/><body><p align=\"right\">\u0424. \u0418. \u041e.:</p></body></html>", None))
        self.rank_le.setText("")
        self.name_le.setText("")
        self.label_2.setText(QCoreApplication.translate("Dialog", u"<html><head/><body><p align=\"right\">\u0434\u043e\u043b\u0436\u043d\u043e\u0441\u0442\u044c:</p></body></html>", None))
    # retranslateUi

