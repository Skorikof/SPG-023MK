# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ExecutorsUilVcntl.ui'
##
## Created by: Qt User Interface Compiler version 6.4.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject, QRect, QSize, Qt)
from PySide6.QtGui import (QFont)
from PySide6.QtWidgets import (QComboBox, QFrame, QHBoxLayout,
                               QLabel, QPushButton, QStatusBar,
                               QTextEdit, QVBoxLayout, QWidget)

class Ui_ExecutorWindow(object):
    def setupUi(self, ExecutorWindow):
        if not ExecutorWindow.objectName():
            ExecutorWindow.setObjectName(u"ExecutorWindow")
        ExecutorWindow.resize(470, 370)
        ExecutorWindow.setMinimumSize(QSize(470, 370))
        ExecutorWindow.setMaximumSize(QSize(1410, 370))
        self.centralwidget = QWidget(ExecutorWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setMinimumSize(QSize(470, 350))
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.frame_quest = QFrame(self.centralwidget)
        self.frame_quest.setObjectName(u"frame_quest")
        self.frame_quest.setMinimumSize(QSize(470, 350))
        self.frame_quest.setMaximumSize(QSize(470, 350))
        self.frame_quest.setStyleSheet(u"background-color: rgb(85, 170, 127);")
        self.frame_quest.setFrameShape(QFrame.Box)
        self.frame_quest.setFrameShadow(QFrame.Raised)
        self.frame_quest.setLineWidth(2)
        self.txt_quest = QTextEdit(self.frame_quest)
        self.txt_quest.setObjectName(u"txt_quest")
        self.txt_quest.setGeometry(QRect(10, 10, 450, 240))
        font = QFont()
        font.setFamilies([u"Calibri"])
        font.setPointSize(20)
        font.setBold(True)
        self.txt_quest.setFont(font)
        self.txt_quest.setStyleSheet(u"")
        self.txt_quest.setFrameShape(QFrame.Box)
        self.txt_quest.setFrameShadow(QFrame.Plain)
        self.txt_quest.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.txt_quest.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.txt_quest.setReadOnly(True)
        self.btn_ok_quest = QPushButton(self.frame_quest)
        self.btn_ok_quest.setObjectName(u"btn_ok_quest")
        self.btn_ok_quest.setGeometry(QRect(60, 270, 70, 60))
        self.btn_ok_quest.setMinimumSize(QSize(70, 60))
        self.btn_ok_quest.setMaximumSize(QSize(70, 60))
        self.btn_ok_quest.setFont(font)
        self.btn_ok_quest.setStyleSheet(u"QPushButton \n"
"{\n"
"	color: rgb(0, 0, 0);\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(240, 240, 240, 255), stop:1 rgba(207, 207, 207, 255));\n"
"\n"
"	border: 1px rgb(0, 0, 0);\n"
"	border-radius: 10px;\n"
"\n"
"	border-style: outset;\n"
"\n"
"	padding: 5px;\n"
"}\n"
"\n"
"QPushButton:hover\n"
"{\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(234, 246, 253, 255), stop:1 rgba(169, 219, 246, 255));\n"
"	\n"
"}\n"
"	\n"
"\n"
"QPushButton:checked\n"
"{\n"
"	\n"
"	background-color: rgb(0, 0, 255);\n"
"	\n"
"}\n"
"\n"
"QPushButton:enabled\n"
"{	\n"
"	color: rgb(0,0, 0);\n"
"}\n"
"QPushButton:disabled\n"
"{	\n"
"	color: rgb(175, 175, 175);\n"
"}")
        self.btn_cancel_quest = QPushButton(self.frame_quest)
        self.btn_cancel_quest.setObjectName(u"btn_cancel_quest")
        self.btn_cancel_quest.setGeometry(QRect(270, 270, 150, 60))
        self.btn_cancel_quest.setMinimumSize(QSize(150, 60))
        self.btn_cancel_quest.setMaximumSize(QSize(150, 60))
        self.btn_cancel_quest.setFont(font)
        self.btn_cancel_quest.setStyleSheet(u"QPushButton \n"
"{\n"
"	color: rgb(0, 0, 0);\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(240, 240, 240, 255), stop:1 rgba(207, 207, 207, 255));\n"
"\n"
"	border: 1px rgb(0, 0, 0);\n"
"	border-radius: 10px;\n"
"\n"
"	border-style: outset;\n"
"\n"
"	padding: 5px;\n"
"}\n"
"\n"
"QPushButton:hover\n"
"{\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(234, 246, 253, 255), stop:1 rgba(169, 219, 246, 255));\n"
"	\n"
"}\n"
"	\n"
"\n"
"QPushButton:checked\n"
"{\n"
"	\n"
"	background-color: rgb(0, 0, 255);\n"
"	\n"
"}\n"
"\n"
"QPushButton:enabled\n"
"{	\n"
"	color: rgb(0,0, 0);\n"
"}\n"
"QPushButton:disabled\n"
"{	\n"
"	color: rgb(175, 175, 175);\n"
"}")

        self.horizontalLayout.addWidget(self.frame_quest)

        self.frame_main = QFrame(self.centralwidget)
        self.frame_main.setObjectName(u"frame_main")
        self.frame_main.setMinimumSize(QSize(470, 350))
        self.frame_main.setMaximumSize(QSize(470, 350))
        self.frame_main.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"")
        self.frame_main.setFrameShape(QFrame.Box)
        self.frame_main.setFrameShadow(QFrame.Raised)
        self.frame_main.setLineWidth(2)
        self.verticalLayout = QVBoxLayout(self.frame_main)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.frame = QFrame(self.frame_main)
        self.frame.setObjectName(u"frame")
        self.frame.setMaximumSize(QSize(16777215, 16777215))
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.combo_Names = QComboBox(self.frame)
        self.combo_Names.setObjectName(u"combo_Names")
        self.combo_Names.setGeometry(QRect(10, 10, 450, 60))
        self.combo_Names.setMinimumSize(QSize(0, 60))
        self.combo_Names.setMaximumSize(QSize(16777215, 60))
        font1 = QFont()
        font1.setFamilies([u"Calibri"])
        font1.setPointSize(18)
        font1.setBold(True)
        self.combo_Names.setFont(font1)
        self.combo_Names.setStyleSheet(u"background-color: rgb(255, 255, 127);")
        self.combo_Names.setEditable(False)
        self.lbl_name = QLabel(self.frame)
        self.lbl_name.setObjectName(u"lbl_name")
        self.lbl_name.setGeometry(QRect(120, 90, 330, 40))
        self.lbl_name.setFont(font1)
        self.lbl_name.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_name.setFrameShape(QFrame.Box)
        self.lbl_name.setFrameShadow(QFrame.Raised)
        self.lbl_name.setAlignment(Qt.AlignCenter)
        self.lbl_rank = QLabel(self.frame)
        self.lbl_rank.setObjectName(u"lbl_rank")
        self.lbl_rank.setGeometry(QRect(170, 140, 245, 40))
        self.lbl_rank.setFont(font1)
        self.lbl_rank.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_rank.setFrameShape(QFrame.Box)
        self.lbl_rank.setFrameShadow(QFrame.Raised)
        self.lbl_rank.setAlignment(Qt.AlignCenter)
        self.lbl_txt1 = QLabel(self.frame)
        self.lbl_txt1.setObjectName(u"lbl_txt1")
        self.lbl_txt1.setGeometry(QRect(0, 90, 100, 37))
        self.lbl_txt1.setFont(font1)
        self.lbl_txt1.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_txt1.setFrameShape(QFrame.NoFrame)
        self.lbl_txt1.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lbl_txt2 = QLabel(self.frame)
        self.lbl_txt2.setObjectName(u"lbl_txt2")
        self.lbl_txt2.setGeometry(QRect(20, 140, 125, 37))
        self.lbl_txt2.setFont(font1)
        self.lbl_txt2.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_txt2.setFrameShape(QFrame.NoFrame)
        self.lbl_txt2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.verticalLayout.addWidget(self.frame)

        self.frame_2 = QFrame(self.frame_main)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setMaximumSize(QSize(16777215, 150))
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.btn_add = QPushButton(self.frame_2)
        self.btn_add.setObjectName(u"btn_add")
        self.btn_add.setGeometry(QRect(10, 10, 160, 60))
        self.btn_add.setMinimumSize(QSize(160, 60))
        self.btn_add.setMaximumSize(QSize(160, 60))
        self.btn_add.setFont(font)
        self.btn_add.setStyleSheet(u"QPushButton \n"
"{\n"
"	color: rgb(0, 0, 0);\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(240, 240, 240, 255), stop:1 rgba(207, 207, 207, 255));\n"
"\n"
"	border: 1px rgb(0, 0, 0);\n"
"	border-radius: 10px;\n"
"\n"
"	border-style: outset;\n"
"\n"
"	padding: 5px;\n"
"}\n"
"\n"
"QPushButton:hover\n"
"{\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(234, 246, 253, 255), stop:1 rgba(169, 219, 246, 255));\n"
"	\n"
"}\n"
"	\n"
"\n"
"QPushButton:checked\n"
"{\n"
"	\n"
"	background-color: rgb(0, 0, 255);\n"
"	\n"
"}\n"
"\n"
"QPushButton:enabled\n"
"{	\n"
"	color: rgb(0,0, 0);\n"
"}\n"
"QPushButton:disabled\n"
"{	\n"
"	color: rgb(175, 175, 175);\n"
"}")
        self.btn_ok_select = QPushButton(self.frame_2)
        self.btn_ok_select.setObjectName(u"btn_ok_select")
        self.btn_ok_select.setGeometry(QRect(380, 10, 70, 60))
        self.btn_ok_select.setMinimumSize(QSize(70, 60))
        self.btn_ok_select.setMaximumSize(QSize(70, 60))
        self.btn_ok_select.setFont(font)
        self.btn_ok_select.setStyleSheet(u"QPushButton \n"
"{\n"
"	color: rgb(0, 0, 0);\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(240, 240, 240, 255), stop:1 rgba(207, 207, 207, 255));\n"
"\n"
"	border: 1px rgb(0, 0, 0);\n"
"	border-radius: 10px;\n"
"\n"
"	border-style: outset;\n"
"\n"
"	padding: 5px;\n"
"}\n"
"\n"
"QPushButton:hover\n"
"{\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(234, 246, 253, 255), stop:1 rgba(169, 219, 246, 255));\n"
"	\n"
"}\n"
"	\n"
"\n"
"QPushButton:checked\n"
"{\n"
"	\n"
"	background-color: rgb(0, 0, 255);\n"
"	\n"
"}\n"
"\n"
"QPushButton:enabled\n"
"{	\n"
"	color: rgb(0,0, 0);\n"
"}\n"
"QPushButton:disabled\n"
"{	\n"
"	color: rgb(175, 175, 175);\n"
"}")
        self.btn_del = QPushButton(self.frame_2)
        self.btn_del.setObjectName(u"btn_del")
        self.btn_del.setGeometry(QRect(190, 10, 160, 60))
        self.btn_del.setMinimumSize(QSize(160, 60))
        self.btn_del.setMaximumSize(QSize(160, 60))
        self.btn_del.setFont(font)
        self.btn_del.setStyleSheet(u"QPushButton \n"
"{\n"
"	color: rgb(0, 0, 0);\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(240, 240, 240, 255), stop:1 rgba(207, 207, 207, 255));\n"
"\n"
"	border: 1px rgb(0, 0, 0);\n"
"	border-radius: 10px;\n"
"\n"
"	border-style: outset;\n"
"\n"
"	padding: 5px;\n"
"}\n"
"\n"
"QPushButton:hover\n"
"{\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(234, 246, 253, 255), stop:1 rgba(169, 219, 246, 255));\n"
"	\n"
"}\n"
"	\n"
"\n"
"QPushButton:checked\n"
"{\n"
"	\n"
"	background-color: rgb(0, 0, 255);\n"
"	\n"
"}\n"
"\n"
"QPushButton:enabled\n"
"{	\n"
"	color: rgb(0,0, 0);\n"
"}\n"
"QPushButton:disabled\n"
"{	\n"
"	color: rgb(175, 175, 175);\n"
"}")
        self.btn_cancel_select = QPushButton(self.frame_2)
        self.btn_cancel_select.setObjectName(u"btn_cancel_select")
        self.btn_cancel_select.setGeometry(QRect(60, 80, 160, 60))
        self.btn_cancel_select.setMinimumSize(QSize(160, 60))
        self.btn_cancel_select.setMaximumSize(QSize(160, 60))
        self.btn_cancel_select.setFont(font)
        self.btn_cancel_select.setStyleSheet(u"QPushButton \n"
"{\n"
"	color: rgb(0, 0, 0);\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(240, 240, 240, 255), stop:1 rgba(207, 207, 207, 255));\n"
"\n"
"	border: 1px rgb(0, 0, 0);\n"
"	border-radius: 10px;\n"
"\n"
"	border-style: outset;\n"
"\n"
"	padding: 5px;\n"
"}\n"
"\n"
"QPushButton:hover\n"
"{\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(234, 246, 253, 255), stop:1 rgba(169, 219, 246, 255));\n"
"	\n"
"}\n"
"	\n"
"\n"
"QPushButton:checked\n"
"{\n"
"	\n"
"	background-color: rgb(0, 0, 255);\n"
"	\n"
"}\n"
"\n"
"QPushButton:enabled\n"
"{	\n"
"	color: rgb(0,0, 0);\n"
"}\n"
"QPushButton:disabled\n"
"{	\n"
"	color: rgb(175, 175, 175);\n"
"}")
        self.btn_exit = QPushButton(self.frame_2)
        self.btn_exit.setObjectName(u"btn_exit")
        self.btn_exit.setGeometry(QRect(280, 80, 160, 60))
        self.btn_exit.setMinimumSize(QSize(160, 60))
        self.btn_exit.setMaximumSize(QSize(160, 60))
        self.btn_exit.setFont(font)
        self.btn_exit.setStyleSheet(u"QPushButton \n"
"{\n"
"	color: rgb(0, 0, 0);\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(240, 240, 240, 255), stop:1 rgba(207, 207, 207, 255));\n"
"\n"
"	border: 1px rgb(0, 0, 0);\n"
"	border-radius: 10px;\n"
"\n"
"	border-style: outset;\n"
"\n"
"	padding: 5px;\n"
"}\n"
"\n"
"QPushButton:hover\n"
"{\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(234, 246, 253, 255), stop:1 rgba(169, 219, 246, 255));\n"
"	\n"
"}\n"
"	\n"
"\n"
"QPushButton:checked\n"
"{\n"
"	\n"
"	background-color: rgb(0, 0, 255);\n"
"	\n"
"}\n"
"\n"
"QPushButton:enabled\n"
"{	\n"
"	color: rgb(0,0, 0);\n"
"}\n"
"QPushButton:disabled\n"
"{	\n"
"	color: rgb(175, 175, 175);\n"
"}")

        self.verticalLayout.addWidget(self.frame_2)


        self.horizontalLayout.addWidget(self.frame_main)

        self.frame_warning = QFrame(self.centralwidget)
        self.frame_warning.setObjectName(u"frame_warning")
        self.frame_warning.setMinimumSize(QSize(470, 350))
        self.frame_warning.setMaximumSize(QSize(470, 350))
        self.frame_warning.setStyleSheet(u"background-color: rgb(255, 170, 0);")
        self.frame_warning.setFrameShape(QFrame.Box)
        self.frame_warning.setFrameShadow(QFrame.Raised)
        self.frame_warning.setLineWidth(2)
        self.txt_warning = QTextEdit(self.frame_warning)
        self.txt_warning.setObjectName(u"txt_warning")
        self.txt_warning.setGeometry(QRect(10, 10, 450, 240))
        self.txt_warning.setFont(font)
        self.txt_warning.setStyleSheet(u"")
        self.txt_warning.setFrameShape(QFrame.Box)
        self.txt_warning.setFrameShadow(QFrame.Plain)
        self.txt_warning.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.txt_warning.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.txt_warning.setReadOnly(True)
        self.btn_ok_warning = QPushButton(self.frame_warning)
        self.btn_ok_warning.setObjectName(u"btn_ok_warning")
        self.btn_ok_warning.setGeometry(QRect(200, 270, 70, 60))
        self.btn_ok_warning.setMinimumSize(QSize(70, 60))
        self.btn_ok_warning.setMaximumSize(QSize(70, 60))
        self.btn_ok_warning.setFont(font)
        self.btn_ok_warning.setStyleSheet(u"QPushButton \n"
"{\n"
"	color: rgb(0, 0, 0);\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(240, 240, 240, 255), stop:1 rgba(207, 207, 207, 255));\n"
"\n"
"	border: 1px rgb(0, 0, 0);\n"
"	border-radius: 10px;\n"
"\n"
"	border-style: outset;\n"
"\n"
"	padding: 5px;\n"
"}\n"
"\n"
"QPushButton:hover\n"
"{\n"
"	background-color: qlineargradient(spread:pad, x1:0.489, y1:0.0227273, x2:0.489, y2:1, stop:0 rgba(234, 246, 253, 255), stop:1 rgba(169, 219, 246, 255));\n"
"	\n"
"}\n"
"	\n"
"\n"
"QPushButton:checked\n"
"{\n"
"	\n"
"	background-color: rgb(0, 0, 255);\n"
"	\n"
"}\n"
"\n"
"QPushButton:enabled\n"
"{	\n"
"	color: rgb(0,0, 0);\n"
"}\n"
"QPushButton:disabled\n"
"{	\n"
"	color: rgb(175, 175, 175);\n"
"}")

        self.horizontalLayout.addWidget(self.frame_warning)

        ExecutorWindow.setCentralWidget(self.centralwidget)
        self.frame_main.raise_()
        self.frame_warning.raise_()
        self.frame_quest.raise_()
        self.statusbar = QStatusBar(ExecutorWindow)
        self.statusbar.setObjectName(u"statusbar")
        ExecutorWindow.setStatusBar(self.statusbar)

        self.retranslateUi(ExecutorWindow)

        QMetaObject.connectSlotsByName(ExecutorWindow)
    # setupUi

    def retranslateUi(self, ExecutorWindow):
        ExecutorWindow.setWindowTitle(QCoreApplication.translate("ExecutorWindow", u"SPG-023MK", None))
        self.txt_quest.setMarkdown(QCoreApplication.translate("ExecutorWindow", u"**\u0418\u041d\u0424\u041e\u0420\u041c\u0410\u0426\u0418\u042f**\n"
"\n"
"", None))
        self.txt_quest.setHtml(QCoreApplication.translate("ExecutorWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Calibri'; font-size:20pt; font-weight:700; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:13px; margin-bottom:13px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">\u0418\u041d\u0424\u041e\u0420\u041c\u0410\u0426\u0418\u042f</span></p></body></html>", None))
        self.btn_ok_quest.setText(QCoreApplication.translate("ExecutorWindow", u"Ok", None))
        self.btn_cancel_quest.setText(QCoreApplication.translate("ExecutorWindow", u"\u041e\u0442\u043c\u0435\u043d\u0430", None))
        self.lbl_name.setText(QCoreApplication.translate("ExecutorWindow", u"\u041f\u0443\u043f\u043a\u0438\u043d \u041f. \u041f. ", None))
        self.lbl_rank.setText(QCoreApplication.translate("ExecutorWindow", u"\u0441\u043b\u0435\u0441\u0430\u0440\u044c", None))
        self.lbl_txt1.setText(QCoreApplication.translate("ExecutorWindow", u"\u0424. \u0418. \u041e.", None))
        self.lbl_txt2.setText(QCoreApplication.translate("ExecutorWindow", u"\u0414\u043e\u043b\u0436\u043d\u043e\u0441\u0442\u044c", None))
        self.btn_add.setText(QCoreApplication.translate("ExecutorWindow", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c", None))
        self.btn_ok_select.setText(QCoreApplication.translate("ExecutorWindow", u"Ok", None))
        self.btn_del.setText(QCoreApplication.translate("ExecutorWindow", u"\u0423\u0434\u0430\u043b\u0438\u0442\u044c", None))
        self.btn_cancel_select.setText(QCoreApplication.translate("ExecutorWindow", u"\u041e\u0442\u043c\u0435\u043d\u0430", None))
        self.btn_exit.setText(QCoreApplication.translate("ExecutorWindow", u"\u0412\u044b\u0445\u043e\u0434", None))
        self.txt_warning.setMarkdown(QCoreApplication.translate("ExecutorWindow", u"**\u041f\u0420\u0415\u0414\u0423\u041f\u0420\u0415\u0416\u0414\u0415\u041d\u0418\u0415**\n"
"\n"
"", None))
        self.txt_warning.setHtml(QCoreApplication.translate("ExecutorWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Calibri'; font-size:20pt; font-weight:700; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:13px; margin-bottom:13px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">\u041f\u0420\u0415\u0414\u0423\u041f\u0420\u0415\u0416\u0414\u0415\u041d\u0418\u0415</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:13px; margin-bottom:13px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-weight:600;\"><br /></p></body></html>", None))
        self.btn_ok_warning.setText(QCoreApplication.translate("ExecutorWindow", u"Ok", None))
    # retranslateUi

